"""
交易记录相关视图
"""

from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db import models
from django.db.models import Q, Sum, Count
from datetime import date, timedelta
from decimal import Decimal
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Transaction, UserBalance, BalanceLog
from .serializers import (
    TransactionSerializer, 
    TransactionFilterSerializer,
    BalanceLogSerializer
)


class TransactionAnalyticsView(APIView):
    """
    交易分析视图
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="获取交易分析数据",
        description="获取用户的交易统计和分析数据",
        parameters=[
            OpenApiParameter('period', str, description='统计周期：today/week/month/year'),
        ]
    )
    def get(self, request):
        user = request.user
        period = request.query_params.get('period', 'month')
        
        # 确定时间范围
        now = timezone.now()
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        elif period == 'year':
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)
        
        # 获取交易数据
        transactions = Transaction.objects.filter(
            user=user,
            created_at__gte=start_date,
            status='COMPLETED'
        )
        
        # 按类型统计
        type_stats = {}
        for transaction_type, display_name in Transaction.TYPE_CHOICES:
            type_transactions = transactions.filter(type=transaction_type)
            type_stats[transaction_type] = {
                'display_name': display_name,
                'count': type_transactions.count(),
                'total_amount': float(type_transactions.aggregate(
                    total=Sum('amount')
                )['total'] or Decimal('0')),
                'avg_amount': float(type_transactions.aggregate(
                    avg=models.Avg('amount')
                )['avg'] or Decimal('0')),
            }
        
        # 每日统计（最近7天）
        daily_stats = []
        for i in range(7):
            day = (now - timedelta(days=i)).date()
            day_transactions = transactions.filter(created_at__date=day)
            
            daily_stats.append({
                'date': day.isoformat(),
                'deposit_amount': float(day_transactions.filter(
                    type='DEPOSIT'
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')),
                'withdraw_amount': float(day_transactions.filter(
                    type='WITHDRAW'
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')),
                'bet_amount': float(day_transactions.filter(
                    type='BET'
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')),
                'win_amount': float(day_transactions.filter(
                    type='WIN'
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')),
                'transaction_count': day_transactions.count(),
            })
        
        # 总体统计
        total_stats = {
            'total_transactions': transactions.count(),
            'total_deposit': float(transactions.filter(
                type='DEPOSIT'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')),
            'total_withdraw': float(transactions.filter(
                type='WITHDRAW'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')),
            'total_bet': float(transactions.filter(
                type='BET'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')),
            'total_win': float(transactions.filter(
                type='WIN'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')),
            'net_deposit': 0,  # 将在下面计算
            'net_gaming': 0,   # 将在下面计算
        }
        
        # 计算净值
        total_stats['net_deposit'] = total_stats['total_deposit'] - total_stats['total_withdraw']
        total_stats['net_gaming'] = total_stats['total_win'] - total_stats['total_bet']
        
        return Response({
            'success': True,
            'data': {
                'period': period,
                'start_date': start_date.isoformat(),
                'end_date': now.isoformat(),
                'total_stats': total_stats,
                'type_stats': type_stats,
                'daily_stats': daily_stats[::-1],  # 按时间正序
            }
        }, status=status.HTTP_200_OK)


class BettingRecordsView(APIView):
    """
    投注记录视图
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="获取投注记录",
        description="获取用户的投注记录，支持按游戏类型筛选",
        parameters=[
            OpenApiParameter('game_type', str, description='游戏类型：11选5/大乐透/刮刮乐/体育'),
            OpenApiParameter('status', str, description='状态筛选'),
            OpenApiParameter('days', int, description='天数范围'),
            OpenApiParameter('page', int, description='页码'),
            OpenApiParameter('page_size', int, description='每页数量'),
        ]
    )
    def get(self, request):
        user = request.user
        
        # 获取筛选参数
        game_type = request.query_params.get('game_type')
        status_filter = request.query_params.get('status')
        days = int(request.query_params.get('days', 30))
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        
        # 构建查询
        queryset = Transaction.objects.filter(
            user=user,
            type__in=['BET', 'WIN'],
            created_at__gte=timezone.now() - timedelta(days=days)
        ).order_by('-created_at')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 游戏类型筛选（通过metadata字段）
        if game_type:
            queryset = queryset.filter(
                metadata__game_type=game_type
            )
        
        # 分页
        total_count = queryset.count()
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        transactions = queryset[start_index:end_index]
        
        # 序列化数据
        betting_records = []
        for transaction in transactions:
            game_info = transaction.metadata.get('game_info', {})
            
            record = {
                'id': str(transaction.id),
                'reference_id': transaction.reference_id,
                'type': transaction.type,
                'type_display': transaction.get_type_display(),
                'amount': float(transaction.amount),
                'actual_amount': float(transaction.actual_amount),
                'status': transaction.status,
                'status_display': transaction.get_status_display(),
                'game_type': transaction.metadata.get('game_type', '未知'),
                'game_info': game_info,
                'created_at': transaction.created_at,
                'processed_at': transaction.processed_at,
            }
            
            # 添加游戏特定信息
            if transaction.type == 'BET':
                record['bet_details'] = {
                    'bet_numbers': game_info.get('bet_numbers', []),
                    'bet_type': game_info.get('bet_type', ''),
                    'multiplier': game_info.get('multiplier', 1),
                    'draw_number': game_info.get('draw_number', ''),
                }
            elif transaction.type == 'WIN':
                record['win_details'] = {
                    'winning_numbers': game_info.get('winning_numbers', []),
                    'prize_level': game_info.get('prize_level', ''),
                    'odds': game_info.get('odds', 0),
                }
            
            betting_records.append(record)
        
        # 统计信息
        stats = {
            'total_count': total_count,
            'total_bet_amount': float(queryset.filter(
                type='BET'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')),
            'total_win_amount': float(queryset.filter(
                type='WIN'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')),
            'bet_count': queryset.filter(type='BET').count(),
            'win_count': queryset.filter(type='WIN').count(),
        }
        
        # 分页信息
        pagination = {
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size,
            'has_next': end_index < total_count,
            'has_prev': page > 1,
        }
        
        return Response({
            'success': True,
            'data': {
                'records': betting_records,
                'stats': stats,
                'pagination': pagination,
                'filters': {
                    'game_type': game_type,
                    'status': status_filter,
                    'days': days,
                }
            }
        }, status=status.HTTP_200_OK)


class TransactionExportView(APIView):
    """
    交易记录导出
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="导出交易记录",
        description="导出用户的交易记录为CSV格式",
        parameters=[
            OpenApiParameter('start_date', str, description='开始日期'),
            OpenApiParameter('end_date', str, description='结束日期'),
            OpenApiParameter('types', str, description='交易类型，逗号分隔'),
        ]
    )
    def get(self, request):
        user = request.user
        
        # 获取参数
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        types = request.query_params.get('types', '').split(',') if request.query_params.get('types') else []
        
        # 构建查询
        queryset = Transaction.objects.filter(user=user)
        
        if start_date:
            try:
                start_date_obj = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start_date_obj)
            except ValueError:
                return Response({
                    'success': False,
                    'message': '开始日期格式错误，请使用YYYY-MM-DD格式'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if end_date:
            try:
                end_date_obj = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end_date_obj)
            except ValueError:
                return Response({
                    'success': False,
                    'message': '结束日期格式错误，请使用YYYY-MM-DD格式'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if types:
            queryset = queryset.filter(type__in=types)
        
        # 限制导出数量
        queryset = queryset.order_by('-created_at')[:1000]
        
        # 生成CSV数据
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow([
            '交易ID', '参考ID', '交易类型', '金额', '手续费', '实际金额',
            '状态', '描述', '创建时间', '处理时间'
        ])
        
        # 写入数据
        for transaction in queryset:
            writer.writerow([
                str(transaction.id),
                transaction.reference_id,
                transaction.get_type_display(),
                float(transaction.amount),
                float(transaction.fee),
                float(transaction.actual_amount),
                transaction.get_status_display(),
                transaction.description,
                transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                transaction.processed_at.strftime('%Y-%m-%d %H:%M:%S') if transaction.processed_at else '',
            ])
        
        # 返回CSV内容
        csv_content = output.getvalue()
        output.close()
        
        return Response({
            'success': True,
            'data': {
                'csv_content': csv_content,
                'record_count': queryset.count(),
                'export_time': timezone.now().isoformat(),
            }
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="获取交易统计摘要",
    description="获取用户交易的快速统计摘要"
)
def transaction_summary(request):
    """
    交易统计摘要
    """
    user = request.user
    
    # 获取不同时间段的统计
    now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    def get_period_stats(start_date, period_name):
        transactions = Transaction.objects.filter(
            user=user,
            created_at__gte=start_date,
            status='COMPLETED'
        )
        
        return {
            'period': period_name,
            'total_transactions': transactions.count(),
            'deposit_amount': float(transactions.filter(
                type='DEPOSIT'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')),
            'withdraw_amount': float(transactions.filter(
                type='WITHDRAW'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')),
            'bet_amount': float(transactions.filter(
                type='BET'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')),
            'win_amount': float(transactions.filter(
                type='WIN'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')),
        }
    
    # 获取各时间段统计
    today_stats = get_period_stats(today, 'today')
    week_stats = get_period_stats(week_ago, 'week')
    month_stats = get_period_stats(month_ago, 'month')
    
    # 获取最近的交易
    recent_transactions = Transaction.objects.filter(
        user=user
    ).order_by('-created_at')[:5]
    
    recent_list = []
    for transaction in recent_transactions:
        recent_list.append({
            'id': str(transaction.id),
            'type': transaction.type,
            'type_display': transaction.get_type_display(),
            'amount': float(transaction.amount),
            'status': transaction.status,
            'status_display': transaction.get_status_display(),
            'created_at': transaction.created_at,
        })
    
    # 获取当前余额
    try:
        balance = user.balance
        balance_info = {
            'main_balance': float(balance.main_balance),
            'bonus_balance': float(balance.bonus_balance),
            'frozen_balance': float(balance.frozen_balance),
            'total_balance': float(balance.get_total_balance()),
            'available_balance': float(balance.get_available_balance()),
        }
    except UserBalance.DoesNotExist:
        balance_info = {
            'main_balance': 0,
            'bonus_balance': 0,
            'frozen_balance': 0,
            'total_balance': 0,
            'available_balance': 0,
        }
    
    return Response({
        'success': True,
        'data': {
            'balance': balance_info,
            'period_stats': {
                'today': today_stats,
                'week': week_stats,
                'month': month_stats,
            },
            'recent_transactions': recent_list,
            'summary_time': now.isoformat(),
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="获取有效流水统计",
    description="获取用户的有效流水统计，用于VIP等级计算"
)
def turnover_stats(request):
    """
    有效流水统计
    """
    user = request.user
    
    # 获取时间范围参数
    days = int(request.query_params.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # 计算有效流水（通常是投注金额）
    valid_turnover = Transaction.objects.filter(
        user=user,
        type='BET',
        status='COMPLETED',
        created_at__gte=start_date
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # 按游戏类型统计
    game_turnover = {}
    game_types = ['11选5', '大乐透', '刮刮乐', '体育']
    
    for game_type in game_types:
        game_amount = Transaction.objects.filter(
            user=user,
            type='BET',
            status='COMPLETED',
            created_at__gte=start_date,
            metadata__game_type=game_type
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        game_turnover[game_type] = float(game_amount)
    
    # 每日流水统计（最近7天）
    daily_turnover = []
    for i in range(7):
        day = (timezone.now() - timedelta(days=i)).date()
        day_amount = Transaction.objects.filter(
            user=user,
            type='BET',
            status='COMPLETED',
            created_at__date=day
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        daily_turnover.append({
            'date': day.isoformat(),
            'amount': float(day_amount)
        })
    
    # VIP信息
    vip_info = user.get_vip_info()
    
    return Response({
        'success': True,
        'data': {
            'period_days': days,
            'valid_turnover': float(valid_turnover),
            'total_turnover': float(user.total_turnover),
            'game_turnover': game_turnover,
            'daily_turnover': daily_turnover[::-1],  # 按时间正序
            'vip_info': {
                'current_level': vip_info.get('level', 0),
                'current_turnover': vip_info.get('current_turnover', 0),
                'required_turnover': vip_info.get('required_turnover', 0),
                'progress_percentage': vip_info.get('progress_percentage', 0),
            }
        }
    }, status=status.HTTP_200_OK)