"""
666刮刮乐游戏API视图
"""

from decimal import Decimal
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .services import Scratch666Service
from .serializers import (
    ScratchCardSerializer,
    UserScratchPreferenceSerializer,
    ScratchStatisticsSerializer
)


@api_view(['GET'])
def game_info(request):
    """
    获取刮刮乐游戏信息
    """
    try:
        game = Scratch666Service.get_game()
        if not game:
            return Response({
                'success': False,
                'message': '游戏不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        config = Scratch666Service.get_game_config()
        
        return Response({
            'success': True,
            'data': {
                'game': {
                    'id': str(game.id),
                    'name': game.name,
                    'code': game.code,
                    'game_type': game.game_type,
                    'description': game.description,
                    'rules': game.rules,
                    'status': game.status,
                    'icon': game.icon.url if game.icon else None,
                    'banner': game.banner.url if game.banner else None,
                },
                'config': {
                    'card_price': float(config.card_price) if config else 10.0,
                    'base_amount': float(config.base_amount) if config else 2.0,
                    'profit_target': float(config.profit_target) if config else 0.30,
                    'scratch_areas': config.scratch_areas if config else 9,
                    'enable_auto_scratch': config.enable_auto_scratch if config else True,
                    'max_auto_scratch': config.max_auto_scratch if config else 100,
                    'enable_sound': config.enable_sound if config else True,
                    'enable_music': config.enable_music if config else True,
                    'win_probabilities': {
                        '6': float(config.win_probability_6) if config else 0.20,
                        '66': float(config.win_probability_66) if config else 0.05,
                        '666': float(config.win_probability_666) if config else 0.01,
                    },
                    'multipliers': {
                        '6': float(config.multiplier_6) if config else 1.0,
                        '66': float(config.multiplier_66) if config else 2.0,
                        '666': float(config.multiplier_666) if config else 3.0,
                    },
                    'expected_payout_rate': config.calculate_expected_payout_rate() if config else 0.0,
                } if config else None,
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取游戏信息失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def purchase_card(request):
    """
    购买刮刮乐卡片
    """
    try:
        result = Scratch666Service.purchase_card(request.user)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'购买失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def scratch_area(request):
    """
    刮开指定区域
    """
    try:
        card_id = request.data.get('card_id')
        area_index = request.data.get('area_index')
        
        if not card_id:
            return Response({
                'success': False,
                'message': '缺少卡片ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if area_index is None:
            return Response({
                'success': False,
                'message': '缺少区域索引'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = Scratch666Service.scratch_area(request.user, card_id, int(area_index))
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'刮奖失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def scratch_all(request):
    """
    刮开所有区域
    """
    try:
        card_id = request.data.get('card_id')
        
        if not card_id:
            return Response({
                'success': False,
                'message': '缺少卡片ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = Scratch666Service.scratch_all(request.user, card_id)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'刮奖失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auto_scratch(request):
    """
    自动连刮
    """
    try:
        count = int(request.data.get('count', 10))
        stop_on_win = request.data.get('stop_on_win', True)
        
        # 限制连刮数量
        count = min(max(count, 1), 100)
        
        result = Scratch666Service.auto_scratch(request.user, count, stop_on_win)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'自动连刮失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_cards(request):
    """
    获取用户的刮刮乐卡片
    """
    try:
        limit = int(request.GET.get('limit', 20))
        card_status = request.GET.get('status')
        
        cards = Scratch666Service.get_user_cards(request.user, limit, card_status)
        
        return Response({
            'success': True,
            'data': {
                'cards': cards,
                'count': len(cards)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取卡片列表失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_statistics(request):
    """
    获取用户统计信息
    """
    try:
        stats = Scratch666Service.get_user_statistics(request.user)
        
        return Response({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取用户统计失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_preferences(request):
    """
    更新用户偏好设置
    """
    try:
        preferences = request.data
        
        result = Scratch666Service.update_user_preferences(request.user, preferences)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'更新偏好设置失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def game_statistics(request):
    """
    获取游戏统计信息
    """
    try:
        days = int(request.GET.get('days', 7))
        days = min(max(days, 1), 365)  # 限制在1-365天之间
        
        stats = Scratch666Service.get_game_statistics(days)
        
        if 'error' in stats:
            return Response({
                'success': False,
                'message': stats['error']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取游戏统计失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def participation_records(request):
    """
    获取参与记录
    """
    try:
        limit = int(request.GET.get('limit', 50))
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        from .models import ScratchCard
        
        queryset = ScratchCard.objects.filter(user=request.user)
        
        # 日期筛选
        if date_from:
            from datetime import datetime
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            queryset = queryset.filter(purchased_at__date__gte=date_from)
        
        if date_to:
            from datetime import datetime
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            queryset = queryset.filter(purchased_at__date__lte=date_to)
        
        cards = queryset.order_by('-purchased_at')[:limit]
        
        records = []
        for card in cards:
            records.append({
                'id': str(card.id),
                'purchase_time': card.purchased_at,
                'transaction_id': str(card.purchase_transaction_id) if card.purchase_transaction_id else None,
                'card_price': float(card.price),
                'total_winnings': float(card.total_winnings),
                'profit': float(card.total_winnings - card.price),
                'is_winner': card.is_winner,
                'status': card.status,
                'win_details': card.win_details,
                'scratched_at': card.scratched_at,
            })
        
        return Response({
            'success': True,
            'data': {
                'records': records,
                'count': len(records),
                'summary': {
                    'total_cards': len(records),
                    'total_spent': sum(record['card_price'] for record in records),
                    'total_won': sum(record['total_winnings'] for record in records),
                    'net_result': sum(record['profit'] for record in records),
                    'win_count': sum(1 for record in records if record['is_winner']),
                    'win_rate': round(sum(1 for record in records if record['is_winner']) / len(records) * 100, 2) if records else 0,
                }
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取参与记录失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def product_info(request):
    """
    获取产品说明信息
    """
    try:
        config = Scratch666Service.get_game_config()
        
        product_info = {
            'basic_rules': {
                'title': '基本规则',
                'content': [
                    '每张刮刮乐卡片包含9个刮奖区域',
                    '刮开区域显示"6"、"66"、"666"即可中奖',
                    '多个区域中奖时奖金累加',
                    '刮开后立即派发奖金到账户余额'
                ]
            },
            'winning_mechanism': {
                'title': '中奖机制',
                'content': [
                    f'"6" - 中奖 ₦{float(config.base_amount * config.multiplier_6) if config else 2.0}',
                    f'"66" - 中奖 ₦{float(config.base_amount * config.multiplier_66) if config else 4.0}',
                    f'"666" - 中奖 ₦{float(config.base_amount * config.multiplier_666) if config else 6.0}',
                    '其他符号不中奖'
                ]
            },
            'illustrations': {
                'title': '图例说明',
                'content': [
                    '🎯 "6" = 基础奖金',
                    '🎯🎯 "66" = 双倍奖金',
                    '🎯🎯🎯 "666" = 三倍奖金',
                    '❌ 其他符号 = 不中奖'
                ]
            },
            'operation_guide': {
                'title': '操作教程',
                'content': [
                    '1. 点击"购买"按钮购买刮刮乐卡片',
                    '2. 点击卡片上的区域进行刮奖',
                    '3. 或点击"全部刮开"一次性刮开所有区域',
                    '4. 使用"自动连刮"功能可连续购买并刮开多张卡片',
                    '5. 中奖金额会立即添加到您的账户余额'
                ]
            },
            'features': {
                'title': '特色功能',
                'content': [
                    '🎵 支持音乐和音效开关',
                    '🔄 自动连刮功能，支持中奖停止',
                    '📊 详细的参与记录和统计信息',
                    '⚙️ 个性化偏好设置',
                    '💰 即时奖金派发'
                ]
            },
            'version_info': {
                'title': '版本信息',
                'version': '1.0.0',
                'last_updated': '2025-01-19',
                'features': [
                    '666刮刮乐核心功能',
                    '自动连刮系统',
                    '用户偏好设置',
                    '统计分析功能'
                ]
            }
        }
        
        return Response({
            'success': True,
            'data': product_info
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取产品信息失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 管理员接口
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_statistics(request):
    """
    管理员统计信息
    """
    if not request.user.is_staff:
        return Response({
            'success': False,
            'message': '权限不足'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        days = int(request.GET.get('days', 30))
        stats = Scratch666Service.get_game_statistics(days)
        
        if 'error' in stats:
            return Response({
                'success': False,
                'message': stats['error']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 添加管理员专用统计
        from .models import ScratchCard, UserScratchPreference
        from datetime import timedelta
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # 用户行为分析
        active_users = ScratchCard.objects.filter(
            purchased_at__date__range=[start_date, end_date]
        ).values('user').distinct().count()
        
        # 高价值用户（购买超过100张的用户）
        high_value_users = UserScratchPreference.objects.filter(
            total_cards_purchased__gte=100
        ).count()
        
        # 平均每用户购买量
        total_cards = ScratchCard.objects.filter(
            purchased_at__date__range=[start_date, end_date]
        ).count()
        
        avg_cards_per_user = total_cards / active_users if active_users > 0 else 0
        
        stats['admin_analytics'] = {
            'active_users': active_users,
            'high_value_users': high_value_users,
            'avg_cards_per_user': round(avg_cards_per_user, 2),
            'user_retention': {
                'description': '用户留存分析',
                'note': '需要更多历史数据进行分析'
            }
        }
        
        return Response({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取管理员统计失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_update_config(request):
    """
    管理员更新游戏配置
    """
    if not request.user.is_staff:
        return Response({
            'success': False,
            'message': '权限不足'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        config = Scratch666Service.get_game_config()
        if not config:
            return Response({
                'success': False,
                'message': '游戏配置不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 更新配置
        data = request.data
        
        if 'card_price' in data:
            config.card_price = Decimal(str(data['card_price']))
        if 'base_amount' in data:
            config.base_amount = Decimal(str(data['base_amount']))
        if 'win_probability_6' in data:
            config.win_probability_6 = Decimal(str(data['win_probability_6']))
        if 'win_probability_66' in data:
            config.win_probability_66 = Decimal(str(data['win_probability_66']))
        if 'win_probability_666' in data:
            config.win_probability_666 = Decimal(str(data['win_probability_666']))
        if 'enable_auto_scratch' in data:
            config.enable_auto_scratch = data['enable_auto_scratch']
        if 'max_auto_scratch' in data:
            config.max_auto_scratch = int(data['max_auto_scratch'])
        if 'enable_sound' in data:
            config.enable_sound = data['enable_sound']
        if 'enable_music' in data:
            config.enable_music = data['enable_music']
        
        config.save()
        
        return Response({
            'success': True,
            'message': '配置更新成功',
            'data': {
                'card_price': float(config.card_price),
                'base_amount': float(config.base_amount),
                'expected_payout_rate': config.calculate_expected_payout_rate(),
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'更新配置失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)