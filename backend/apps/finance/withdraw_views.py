"""
提款相关视图
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db import models
from datetime import date, timedelta
from decimal import Decimal
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Transaction, BankAccount, UserBalance
from .serializers import WithdrawRequestSerializer, TransactionSerializer
from .services import FinanceService
from apps.core.security import SecurityManager


class WithdrawLimitsView(APIView):
    """
    提款限制查询
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="获取提款限制信息",
        description="获取当前用户的提款限制、手续费和银行账户信息"
    )
    def get(self, request):
        user = request.user
        
        # 检查KYC状态
        if user.kyc_status != 'APPROVED':
            return Response({
                'success': False,
                'message': '请先完成KYC身份验证才能提款',
                'error_code': 'KYC_REQUIRED',
                'data': {
                    'kyc_status': user.kyc_status,
                    'kyc_url': '/api/v1/users/kyc/submit/'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 获取用户VIP信息
        vip_info = user.get_vip_info()
        
        # 获取用户余额
        try:
            balance = user.balance
            available_balance = balance.get_available_balance()
        except UserBalance.DoesNotExist:
            available_balance = Decimal('0.00')
        
        # 获取已验证的银行账户
        bank_accounts = BankAccount.objects.filter(
            user=user,
            is_verified=True
        ).order_by('-is_default', '-created_at')
        
        # 计算今日已提款金额和次数
        today = date.today()
        today_withdrawals = Transaction.objects.filter(
            user=user,
            type='WITHDRAW',
            status__in=['COMPLETED', 'PROCESSING'],
            created_at__date=today
        )
        
        today_withdraw_amount = today_withdrawals.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')
        
        today_withdraw_count = today_withdrawals.count()
        
        # 计算可提款金额
        daily_limit = Decimal(str(vip_info.get('daily_withdraw_limit', 0)))
        remaining_daily_limit = max(Decimal('0'), daily_limit - today_withdraw_amount)
        max_withdraw_amount = min(available_balance, remaining_daily_limit)
        
        # 银行账户信息
        bank_accounts_data = []
        for account in bank_accounts:
            bank_accounts_data.append({
                'id': str(account.id),
                'bank_name': account.get_bank_code_display(),
                'bank_code': account.bank_code,
                'account_number': account.account_number,
                'account_name': account.account_name,
                'is_default': account.is_default,
                'is_verified': account.is_verified,
                'created_at': account.created_at,
            })
        
        # 手续费信息
        withdraw_fee_rate = Decimal(str(vip_info.get('withdraw_fee_rate', 0.02)))
        fee_examples = []
        for amount in [1000, 5000, 10000, 50000]:
            fee = Decimal(str(amount)) * withdraw_fee_rate
            fee_examples.append({
                'amount': amount,
                'fee': float(fee),
                'actual_amount': float(Decimal(str(amount)) - fee)
            })
        
        response_data = {
            'available_balance': float(available_balance),
            'vip_level': user.vip_level,
            'daily_withdraw_limit': float(daily_limit),
            'daily_withdraw_times': vip_info.get('daily_withdraw_times', 3),
            'today_withdrawn': float(today_withdraw_amount),
            'today_withdraw_count': today_withdraw_count,
            'remaining_daily_limit': float(remaining_daily_limit),
            'remaining_daily_times': max(0, vip_info.get('daily_withdraw_times', 3) - today_withdraw_count),
            'max_withdraw_amount': float(max_withdraw_amount),
            'min_withdraw_amount': 100.00,
            'withdraw_fee_rate': float(withdraw_fee_rate),
            'fee_examples': fee_examples,
            'bank_accounts': bank_accounts_data,
            'has_verified_account': len(bank_accounts_data) > 0,
            'estimated_arrival_time': '1-3个工作日',
        }
        
        return Response({
            'success': True,
            'data': response_data
        }, status=status.HTTP_200_OK)


class WithdrawStatusView(APIView):
    """
    提款状态查询
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="查询提款状态",
        description="根据交易ID查询提款状态和处理进度",
        parameters=[
            OpenApiParameter('transaction_id', str, description='交易ID'),
        ]
    )
    def get(self, request):
        transaction_id = request.query_params.get('transaction_id')
        
        if not transaction_id:
            return Response({
                'success': False,
                'message': '请提供交易ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            transaction = Transaction.objects.get(
                id=transaction_id,
                user=request.user,
                type='WITHDRAW'
            )
            
            # 获取银行账户信息
            bank_account_id = transaction.metadata.get('bank_account_id')
            bank_info = {
                'bank_name': transaction.metadata.get('bank_name', '未知银行'),
                'account_number': transaction.metadata.get('account_number', ''),
                'account_name': transaction.metadata.get('account_name', ''),
            }
            
            response_data = {
                'transaction_id': str(transaction.id),
                'reference_id': transaction.reference_id,
                'amount': float(transaction.amount),
                'fee': float(transaction.fee),
                'actual_amount': float(transaction.actual_amount),
                'status': transaction.status,
                'status_display': transaction.get_status_display(),
                'bank_info': bank_info,
                'created_at': transaction.created_at,
                'processed_at': transaction.processed_at,
                'description': transaction.description,
            }
            
            # 根据状态提供不同的信息
            if transaction.status == 'PENDING':
                response_data['message'] = '提款申请已提交，等待审核'
                response_data['next_step'] = '系统正在进行安全审核'
            elif transaction.status == 'PROCESSING':
                response_data['message'] = '提款正在处理中'
                response_data['next_step'] = '资金正在转账到您的银行账户'
                response_data['estimated_arrival'] = '1-3个工作日'
            elif transaction.status == 'COMPLETED':
                response_data['message'] = '提款已成功处理'
                response_data['completion_time'] = transaction.processed_at
            elif transaction.status == 'FAILED':
                response_data['message'] = '提款处理失败'
                response_data['failure_reason'] = transaction.metadata.get('failure_reason', '未知原因')
                response_data['next_step'] = '请联系客服或重新申请提款'
            
            return Response({
                'success': True,
                'data': response_data
            }, status=status.HTTP_200_OK)
            
        except Transaction.DoesNotExist:
            return Response({
                'success': False,
                'message': '提款记录不存在'
            }, status=status.HTTP_404_NOT_FOUND)


class WithdrawHistoryView(APIView):
    """
    提款历史记录
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="获取提款历史",
        description="获取当前用户的提款历史记录",
        parameters=[
            OpenApiParameter('status', str, description='状态筛选'),
            OpenApiParameter('days', int, description='天数范围'),
        ]
    )
    def get(self, request):
        user = request.user
        
        # 获取筛选参数
        status_filter = request.query_params.get('status')
        days = int(request.query_params.get('days', 30))
        
        # 构建查询
        queryset = Transaction.objects.filter(
            user=user,
            type='WITHDRAW',
            created_at__gte=timezone.now() - timedelta(days=days)
        ).order_by('-created_at')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 序列化数据
        transactions = []
        for transaction in queryset[:50]:  # 限制50条记录
            bank_info = {
                'bank_name': transaction.metadata.get('bank_name', '未知银行'),
                'account_number': transaction.metadata.get('account_number', ''),
            }
            
            transactions.append({
                'id': str(transaction.id),
                'reference_id': transaction.reference_id,
                'amount': float(transaction.amount),
                'fee': float(transaction.fee),
                'actual_amount': float(transaction.actual_amount),
                'status': transaction.status,
                'status_display': transaction.get_status_display(),
                'bank_info': bank_info,
                'created_at': transaction.created_at,
                'processed_at': transaction.processed_at,
            })
        
        # 统计信息
        stats = {
            'total_count': queryset.count(),
            'pending_count': queryset.filter(status='PENDING').count(),
            'processing_count': queryset.filter(status='PROCESSING').count(),
            'completed_count': queryset.filter(status='COMPLETED').count(),
            'failed_count': queryset.filter(status='FAILED').count(),
            'total_amount': float(queryset.filter(
                status='COMPLETED'
            ).aggregate(total=models.Sum('actual_amount'))['total'] or Decimal('0')),
        }
        
        return Response({
            'success': True,
            'data': {
                'transactions': transactions,
                'stats': stats,
                'filters': {
                    'status': status_filter,
                    'days': days,
                }
            }
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="取消提款申请",
    description="取消状态为PENDING的提款申请"
)
def cancel_withdraw(request):
    """
    取消提款申请
    """
    transaction_id = request.data.get('transaction_id')
    
    if not transaction_id:
        return Response({
            'success': False,
            'message': '请提供交易ID'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        transaction = Transaction.objects.get(
            id=transaction_id,
            user=request.user,
            type='WITHDRAW'
        )
        
        if transaction.status != 'PENDING':
            return Response({
                'success': False,
                'message': '只能取消待处理的提款申请'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 取消提款，解冻余额
        balance = FinanceService.get_or_create_balance(request.user)
        if balance.unfreeze_balance(transaction.amount):
            transaction.status = 'CANCELLED'
            transaction.processed_at = timezone.now()
            transaction.metadata['cancelled_by'] = 'user'
            transaction.metadata['cancelled_at'] = timezone.now().isoformat()
            transaction.save()
            
            return Response({
                'success': True,
                'message': '提款申请已取消，余额已解冻'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': '取消提款失败，请联系客服'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Transaction.DoesNotExist:
        return Response({
            'success': False,
            'message': '提款记录不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="获取提款指南",
    description="获取提款流程说明和注意事项"
)
def withdraw_guide(request):
    """
    提款指南
    """
    guide_data = {
        'process_steps': [
            {
                'step': 1,
                'title': '完成KYC验证',
                'description': '首次提款需要完成身份验证',
                'status': 'completed' if request.user.kyc_status == 'APPROVED' else 'pending'
            },
            {
                'step': 2,
                'title': '添加银行账户',
                'description': '添加并验证您的银行账户信息',
                'status': 'completed' if BankAccount.objects.filter(
                    user=request.user, is_verified=True
                ).exists() else 'pending'
            },
            {
                'step': 3,
                'title': '申请提款',
                'description': '选择银行账户，输入提款金额和密码',
                'status': 'available'
            },
            {
                'step': 4,
                'title': '等待处理',
                'description': '系统审核后将资金转账到您的银行账户',
                'status': 'available'
            }
        ],
        'important_notes': [
            '提款金额必须大于等于₦100',
            '每日提款次数和金额根据VIP等级而定',
            '提款手续费根据VIP等级计算，VIP7免手续费',
            '银行账户名必须与注册姓名一致',
            '提款通常在1-3个工作日内到账',
            '如遇问题请及时联系客服'
        ],
        'fee_structure': [
            {'vip_level': 'VIP0', 'fee_rate': '2.0%', 'daily_limit': '₦50,000', 'daily_times': 1},
            {'vip_level': 'VIP1', 'fee_rate': '1.5%', 'daily_limit': '₦100,000', 'daily_times': 2},
            {'vip_level': 'VIP2', 'fee_rate': '1.0%', 'daily_limit': '₦200,000', 'daily_times': 2},
            {'vip_level': 'VIP3', 'fee_rate': '0.8%', 'daily_limit': '₦500,000', 'daily_times': 3},
            {'vip_level': 'VIP4', 'fee_rate': '0.6%', 'daily_limit': '₦1,000,000', 'daily_times': 3},
            {'vip_level': 'VIP5', 'fee_rate': '0.4%', 'daily_limit': '₦2,000,000', 'daily_times': 5},
            {'vip_level': 'VIP6', 'fee_rate': '0.2%', 'daily_limit': '₦5,000,000', 'daily_times': 5},
            {'vip_level': 'VIP7', 'fee_rate': '0%免费', 'daily_limit': '₦10,000,000', 'daily_times': 10},
        ],
        'faq': [
            {
                'question': '提款多久能到账？',
                'answer': '通常在1-3个工作日内到账，具体时间取决于银行处理速度。'
            },
            {
                'question': '为什么需要KYC验证？',
                'answer': '为了保障您的资金安全和符合监管要求，首次提款需要完成身份验证。'
            },
            {
                'question': '可以修改提款申请吗？',
                'answer': '只能取消状态为"待处理"的提款申请，已处理的申请无法修改。'
            },
            {
                'question': '提款失败怎么办？',
                'answer': '提款失败的资金会自动退回您的账户，请检查银行账户信息或联系客服。'
            }
        ]
    }
    
    return Response({
        'success': True,
        'data': guide_data
    }, status=status.HTTP_200_OK)