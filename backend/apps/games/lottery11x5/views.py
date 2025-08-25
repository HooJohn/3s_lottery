"""
11选5彩票游戏API视图
"""

from decimal import Decimal
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.core.cache import cache

from apps.games.models import Game, Draw, BetType
from .services import Lottery11x5Service, Lottery11x5DrawService
from .serializers import (
    Lottery11x5BetSerializer,
    Lottery11x5DrawSerializer,
    Lottery11x5ResultSerializer,
    Lottery11x5TrendSerializer
)


@api_view(['GET'])
def game_info(request):
    """
    获取11选5游戏信息
    """
    try:
        game = Lottery11x5Service.get_game()
        if not game:
            return Response({
                'success': False,
                'message': '游戏不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        config = Lottery11x5Service.get_game_config()
        bet_types = Lottery11x5Service.get_bet_types()
        
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
                    'min_bet': float(game.min_bet),
                    'max_bet': float(game.max_bet),
                    'status': game.status,
                    'icon': game.icon.url if game.icon else None,
                    'banner': game.banner.url if game.banner else None,
                },
                'config': {
                    'draw_count_per_day': config.draw_count_per_day if config else 7,
                    'draw_interval_minutes': config.draw_interval_minutes if config else 120,
                    'close_before_minutes': config.close_before_minutes if config else 5,
                    'profit_target': float(config.profit_target) if config else 0.18,
                } if config else None,
                'bet_types': [
                    {
                        'id': str(bt.id),
                        'name': bt.name,
                        'code': bt.code,
                        'description': bt.description,
                        'odds': float(bt.odds),
                        'min_bet': float(bt.min_bet),
                        'max_bet': float(bt.max_bet),
                        'max_payout': float(bt.max_payout),
                        'rules': bt.rules,
                    }
                    for bt in bet_types
                ]
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取游戏信息失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def current_draw(request):
    """
    获取当前期数信息
    """
    try:
        draw = Lottery11x5Service.get_current_draw()
        if not draw:
            return Response({
                'success': False,
                'message': '当前没有可投注的期数'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 获取倒计时信息
        countdown = Lottery11x5DrawService.get_draw_countdown(str(draw.id))
        
        return Response({
            'success': True,
            'data': {
                'draw': {
                    'id': str(draw.id),
                    'draw_number': draw.draw_number,
                    'draw_time': draw.draw_time,
                    'close_time': draw.close_time,
                    'status': draw.status,
                    'total_bets': draw.total_bets,
                    'total_amount': float(draw.total_amount),
                },
                'countdown': countdown
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取当前期数失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def recent_results(request):
    """
    获取最近开奖结果
    """
    try:
        limit = int(request.GET.get('limit', 10))
        results = Lottery11x5Service.get_recent_results(limit)
        
        return Response({
            'success': True,
            'data': {
                'results': results,
                'count': len(results)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取开奖结果失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def hot_cold_numbers(request):
    """
    获取冷热号码统计
    """
    try:
        period_type = int(request.GET.get('period', 50))
        if period_type not in [10, 30, 50, 100]:
            period_type = 50
        
        hot_cold = Lottery11x5Service.get_hot_cold_numbers(period_type)
        
        return Response({
            'success': True,
            'data': hot_cold
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取冷热号码失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_bet(request):
    """
    立即投注
    """
    try:
        data = request.data
        
        # 验证必需参数
        required_fields = ['draw_id', 'bet_type_id', 'numbers', 'amount', 'bet_method']
        for field in required_fields:
            if field not in data:
                return Response({
                    'success': False,
                    'message': f'缺少必需参数: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 参数处理
        draw_id = data['draw_id']
        bet_type_id = data['bet_type_id']
        numbers = data['numbers']
        amount = Decimal(str(data['amount']))
        bet_method = data['bet_method']
        positions = data.get('positions', [])
        selected_count = int(data.get('selected_count', 0))
        multiplier = int(data.get('multiplier', 1))
        mode = data.get('mode', '元')  # 元/角/分
        
        # 根据模式调整金额
        if mode == '角':
            amount = amount / 10
        elif mode == '分':
            amount = amount / 100
        
        # 应用倍数
        if multiplier > 1:
            amount = amount * multiplier
        
        # 调用投注服务
        result = Lottery11x5Service.place_bet(
            user=request.user,
            draw_id=draw_id,
            bet_type_id=bet_type_id,
            numbers=numbers,
            amount=amount,
            bet_method=bet_method,
            positions=positions,
            selected_count=selected_count
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'投注失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """
    添加到购彩篮
    """
    try:
        from .cart import Lottery11x5Cart
        
        cart = Lottery11x5Cart(str(request.user.id))
        result = cart.add_bet(request.data)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'添加到购彩篮失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    """
    获取购彩篮
    """
    try:
        from .cart import Lottery11x5Cart
        
        cart = Lottery11x5Cart(str(request.user.id))
        cart_summary = cart.get_cart_summary()
        
        return Response({
            'success': True,
            'data': cart_summary
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取购彩篮失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, item_id):
    """
    更新购彩篮项目
    """
    try:
        from .cart import Lottery11x5Cart
        
        cart = Lottery11x5Cart(str(request.user.id))
        result = cart.update_bet(item_id, request.data)
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'更新购彩篮项目失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_cart_item(request, item_id):
    """
    移除购彩篮项目
    """
    try:
        from .cart import Lottery11x5Cart
        
        cart = Lottery11x5Cart(str(request.user.id))
        result = cart.remove_bet(item_id)
        
        return Response(result)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'移除购彩篮项目失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    """
    清空购彩篮
    """
    try:
        from .cart import Lottery11x5Cart
        
        cart = Lottery11x5Cart(str(request.user.id))
        result = cart.clear_cart()
        
        return Response(result)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'清空购彩篮失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_cart_bets(request):
    """
    提交购彩篮中的所有投注
    """
    try:
        from .cart import Lottery11x5Cart
        
        cart = Lottery11x5Cart(str(request.user.id))
        result = cart.place_all_bets(request.user)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'提交投注失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def quick_pick_options(request):
    """
    获取快捷选号选项
    """
    try:
        from .cart import Lottery11x5QuickPick
        
        options = Lottery11x5QuickPick.get_quick_pick_options()
        
        return Response({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取快捷选号选项失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def quick_pick_numbers(request):
    """
    快捷选号
    """
    try:
        from .cart import Lottery11x5QuickPick
        
        pick_type = request.data.get('type', 'random')
        count = int(request.data.get('count', 5))
        
        if pick_type == 'all':
            numbers = Lottery11x5QuickPick.get_all_numbers()
        elif pick_type == 'big':
            numbers = Lottery11x5QuickPick.get_big_numbers()
        elif pick_type == 'small':
            numbers = Lottery11x5QuickPick.get_small_numbers()
        elif pick_type == 'odd':
            numbers = Lottery11x5QuickPick.get_odd_numbers()
        elif pick_type == 'even':
            numbers = Lottery11x5QuickPick.get_even_numbers()
        elif pick_type == 'hot':
            period = int(request.data.get('period', 50))
            numbers = Lottery11x5QuickPick.get_hot_numbers(period)
        elif pick_type == 'cold':
            period = int(request.data.get('period', 50))
            numbers = Lottery11x5QuickPick.get_cold_numbers(period)
        else:  # random
            numbers = Lottery11x5QuickPick.get_random_numbers(count)
        
        return Response({
            'success': True,
            'data': {
                'type': pick_type,
                'numbers': numbers,
                'count': len(numbers)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'快捷选号失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def calculate_bet(request):
    """
    计算投注详情（预览）
    """
    try:
        from .bet_calculator import Lottery11x5BetCalculator, Lottery11x5BetValidator
        
        # 验证投注数据
        validation_result = Lottery11x5BetValidator.validate_bet_request(request.data)
        if not validation_result['valid']:
            return Response({
                'success': False,
                'message': '; '.join(validation_result['errors'])
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 计算投注详情
        bet_details = Lottery11x5BetCalculator.calculate_bet_details(request.data)
        
        # 获取优化建议
        suggestions = Lottery11x5BetCalculator.suggest_bet_optimization(bet_details)
        
        return Response({
            'success': True,
            'data': {
                'bet_details': bet_details,
                'suggestions': suggestions,
                'validation': validation_result
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'计算投注详情失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_favorite_numbers(request):
    """
    获取用户常用号码
    """
    try:
        from .models import Lottery11x5UserNumber
        
        game = Lottery11x5Service.get_game()
        if not game:
            return Response({
                'success': False,
                'message': '游戏不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        user_numbers = Lottery11x5UserNumber.objects.filter(
            user=request.user,
            game=game
        ).order_by('-is_favorite', '-usage_count')
        
        numbers_data = []
        for user_number in user_numbers:
            numbers_data.append({
                'id': str(user_number.id),
                'name': user_number.name,
                'numbers': user_number.numbers,
                'bet_method': user_number.bet_method,
                'bet_method_display': user_number.get_bet_method_display(),
                'positions': user_number.positions,
                'selected_count': user_number.selected_count,
                'is_favorite': user_number.is_favorite,
                'usage_count': user_number.usage_count,
                'win_count': user_number.win_count,
                'win_rate': (user_number.win_count / user_number.usage_count * 100) if user_number.usage_count > 0 else 0,
                'created_at': user_number.created_at,
                'updated_at': user_number.updated_at,
            })
        
        return Response({
            'success': True,
            'data': {
                'user_numbers': numbers_data,
                'count': len(numbers_data)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取用户常用号码失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_favorite_numbers(request):
    """
    保存常用号码
    """
    try:
        from .models import Lottery11x5UserNumber
        
        game = Lottery11x5Service.get_game()
        if not game:
            return Response({
                'success': False,
                'message': '游戏不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        required_fields = ['name', 'numbers', 'bet_method']
        
        for field in required_fields:
            if field not in data:
                return Response({
                    'success': False,
                    'message': f'缺少必需字段: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建或更新常用号码
        user_number, created = Lottery11x5UserNumber.objects.update_or_create(
            user=request.user,
            game=game,
            name=data['name'],
            defaults={
                'numbers': data['numbers'],
                'bet_method': data['bet_method'],
                'positions': data.get('positions', []),
                'selected_count': data.get('selected_count', 0),
                'is_favorite': data.get('is_favorite', False),
            }
        )
        
        return Response({
            'success': True,
            'message': '保存成功' if created else '更新成功',
            'data': {
                'id': str(user_number.id),
                'name': user_number.name,
                'numbers': user_number.numbers,
                'created': created
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'保存常用号码失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bet_history(request):
    """
    获取用户投注历史
    """
    try:
        limit = int(request.GET.get('limit', 20))
        bet_status = request.GET.get('status')
        
        history = Lottery11x5Service.get_user_bet_history(
            user=request.user,
            limit=limit,
            status=bet_status
        )
        
        return Response({
            'success': True,
            'data': {
                'bets': history,
                'count': len(history)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取投注历史失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def generate_random_numbers(request):
    """
    生成随机号码
    """
    try:
        count = int(request.data.get('count', 5))
        if count < 1 or count > 11:
            count = 5
        
        numbers = Lottery11x5Service.generate_random_numbers(count)
        
        return Response({
            'success': True,
            'data': {
                'numbers': numbers,
                'count': len(numbers)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'生成随机号码失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def trend_analysis(request):
    """
    获取走势分析数据
    """
    try:
        from .trend_analyzer import Lottery11x5TrendAnalyzer
        
        game = Lottery11x5Service.get_game()
        if not game:
            return Response({
                'success': False,
                'message': '游戏不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        analyzer = Lottery11x5TrendAnalyzer(game)
        
        # 获取参数
        limit = int(request.GET.get('limit', 30))
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        # 转换日期参数
        if date_from:
            from datetime import datetime
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        if date_to:
            from datetime import datetime
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        # 获取走势数据
        trend_data = analyzer.get_trend_data(limit, date_from, date_to)
        
        return Response({
            'success': True,
            'data': trend_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取走势分析失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def position_trend(request, position):
    """
    获取位置走势
    """
    try:
        from .trend_analyzer import Lottery11x5TrendAnalyzer
        
        game = Lottery11x5Service.get_game()
        if not game:
            return Response({
                'success': False,
                'message': '游戏不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        analyzer = Lottery11x5TrendAnalyzer(game)
        limit = int(request.GET.get('limit', 50))
        
        position_data = analyzer.get_position_trend(int(position), limit)
        
        return Response({
            'success': True,
            'data': position_data
        })
        
    except ValueError as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取位置走势失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def missing_analysis(request):
    """
    获取遗漏分析
    """
    try:
        from .trend_analyzer import Lottery11x5TrendAnalyzer
        
        game = Lottery11x5Service.get_game()
        if not game:
            return Response({
                'success': False,
                'message': '游戏不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        analyzer = Lottery11x5TrendAnalyzer(game)
        limit = int(request.GET.get('limit', 100))
        
        missing_data = analyzer.get_missing_analysis(limit)
        
        return Response({
            'success': True,
            'data': missing_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取遗漏分析失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def complete_trend_chart(request):
    """
    获取完整走势图
    """
    try:
        from .trend_analyzer import Lottery11x5TrendAnalyzer
        
        game = Lottery11x5Service.get_game()
        if not game:
            return Response({
                'success': False,
                'message': '游戏不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        analyzer = Lottery11x5TrendAnalyzer(game)
        limit = int(request.GET.get('limit', 30))
        
        chart_data = analyzer.get_complete_trend_chart(limit)
        
        return Response({
            'success': True,
            'data': chart_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取完整走势图失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def prediction_analysis(request):
    """
    获取预测分析
    """
    try:
        from .trend_analyzer import Lottery11x5TrendAnalyzer
        
        game = Lottery11x5Service.get_game()
        if not game:
            return Response({
                'success': False,
                'message': '游戏不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        analyzer = Lottery11x5TrendAnalyzer(game)
        limit = int(request.GET.get('limit', 50))
        
        prediction_data = analyzer.get_prediction_analysis(limit)
        
        return Response({
            'success': True,
            'data': prediction_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取预测分析失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def number_statistics(request):
    """
    获取号码统计信息
    """
    try:
        from .models import Lottery11x5Result
        
        game = Lottery11x5Service.get_game()
        if not game:
            return Response({
                'success': False,
                'message': '游戏不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 获取最近的开奖结果
        limit = int(request.GET.get('limit', 100))
        recent_results = Lottery11x5Result.objects.filter(
            draw__game=game,
            draw__status='COMPLETED'
        ).order_by('-draw__draw_time')[:limit]
        
        # 统计每个号码的出现次数
        number_counts = {i: 0 for i in range(1, 12)}
        position_counts = {i: {j: 0 for j in range(1, 12)} for i in range(1, 6)}
        
        for result in recent_results:
            for number in result.numbers:
                number_counts[number] += 1
            
            # 统计位置号码
            for i, number in enumerate(result.numbers):
                if i < 5:  # 确保不超过5个位置
                    position_counts[i + 1][number] += 1
        
        # 计算遗漏值
        missing_counts = {}
        for number in range(1, 12):
            missing_count = 0
            for result in recent_results:
                if number not in result.numbers:
                    missing_count += 1
                else:
                    break
            missing_counts[number] = missing_count
        
        return Response({
            'success': True,
            'data': {
                'period_count': len(recent_results),
                'number_frequency': number_counts,
                'position_frequency': position_counts,
                'missing_counts': missing_counts,
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取号码统计失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 管理员接口
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_draw_lottery(request):
    """
    管理员手动开奖
    """
    if not request.user.is_staff:
        return Response({
            'success': False,
            'message': '权限不足'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        draw_id = request.data.get('draw_id')
        if not draw_id:
            return Response({
                'success': False,
                'message': '缺少期数ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = Lottery11x5Service.draw_lottery(draw_id)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'开奖失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_create_draws(request):
    """
    管理员创建期次
    """
    if not request.user.is_staff:
        return Response({
            'success': False,
            'message': '权限不足'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        success = Lottery11x5DrawService.create_daily_draws()
        
        return Response({
            'success': success,
            'message': '期次创建成功' if success else '期次创建失败或已存在'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'创建期次失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_close_draws(request):
    """
    管理员关闭过期期次
    """
    if not request.user.is_staff:
        return Response({
            'success': False,
            'message': '权限不足'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        count = Lottery11x5DrawService.close_expired_draws()
        
        return Response({
            'success': True,
            'message': f'已关闭 {count} 个过期期次'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'关闭期次失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def verify_draw_result(request, draw_id):
    """
    验证开奖结果
    """
    try:
        from .draw_engine import Lottery11x5DrawEngine
        from apps.games.models import Draw
        
        draw = Draw.objects.get(id=draw_id)
        
        if draw.status != 'COMPLETED':
            return Response({
                'success': False,
                'message': '该期次尚未开奖'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取开奖号码
        winning_numbers = draw.lottery11x5_result.numbers
        
        # 验证开奖结果
        draw_engine = Lottery11x5DrawEngine()
        verification_result = draw_engine.verify_draw_result(
            draw_id=str(draw.id),
            draw_time=draw.draw_time,
            claimed_numbers=winning_numbers
        )
        
        return Response({
            'success': True,
            'data': {
                'draw_number': draw.draw_number,
                'draw_time': draw.draw_time,
                'winning_numbers': winning_numbers,
                'verification': verification_result,
                'proof': draw.result.get('proof', {}),
            }
        })
        
    except Draw.DoesNotExist:
        return Response({
            'success': False,
            'message': '期次不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'验证失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def draw_settlement_details(request, draw_id):
    """
    获取期次结算详情
    """
    try:
        from apps.games.models import Draw
        
        draw = Draw.objects.get(id=draw_id)
        
        if draw.status != 'COMPLETED':
            return Response({
                'success': False,
                'message': '该期次尚未开奖结算'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取结算详情
        settlement_details = draw.result.get('profit_analysis', {})
        
        # 获取中奖用户信息（仅管理员可见详细信息）
        if request.user.is_staff:
            from apps.games.models import Bet
            winning_bets = Bet.objects.filter(
                draw=draw,
                status='WON'
            ).select_related('user', 'bet_type')
            
            winners_info = []
            for bet in winning_bets:
                lottery_bet = bet.lottery11x5_detail
                winners_info.append({
                    'user_phone': bet.user.phone,
                    'bet_type': bet.bet_type.name,
                    'bet_method': lottery_bet.get_bet_method_display(),
                    'numbers': bet.numbers,
                    'bet_amount': float(bet.amount * lottery_bet.multiple_count),
                    'win_amount': float(bet.payout),
                    'odds': float(bet.odds),
                    'bet_time': bet.bet_time,
                })
        else:
            winners_info = None
        
        return Response({
            'success': True,
            'data': {
                'draw_number': draw.draw_number,
                'draw_time': draw.draw_time,
                'winning_numbers': draw.lottery11x5_result.numbers,
                'total_bets': draw.total_bets,
                'total_amount': float(draw.total_amount),
                'total_payout': float(draw.total_payout),
                'profit': float(draw.profit),
                'profit_rate': float((draw.profit / draw.total_amount * 100) if draw.total_amount > 0 else 0),
                'settlement_details': settlement_details,
                'winners_info': winners_info,
            }
        })
        
    except Draw.DoesNotExist:
        return Response({
            'success': False,
            'message': '期次不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取结算详情失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_force_draw(request):
    """
    管理员强制开奖（指定号码）
    """
    if not request.user.is_staff:
        return Response({
            'success': False,
            'message': '权限不足'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        draw_id = request.data.get('draw_id')
        force_numbers = request.data.get('force_numbers')
        
        if not draw_id:
            return Response({
                'success': False,
                'message': '缺少期数ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not force_numbers or len(force_numbers) != 5:
            return Response({
                'success': False,
                'message': '必须指定5个开奖号码'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证号码
        if not all(isinstance(num, int) and 1 <= num <= 11 for num in force_numbers):
            return Response({
                'success': False,
                'message': '号码必须是1-11之间的整数'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(set(force_numbers)) != 5:
            return Response({
                'success': False,
                'message': '号码不能重复'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 排序号码
        force_numbers.sort()
        
        # 执行开奖
        result = Lottery11x5Service.draw_lottery(draw_id, force_numbers=force_numbers)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'强制开奖失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profit_analysis(request):
    """
    获取利润分析报告
    """
    if not request.user.is_staff:
        return Response({
            'success': False,
            'message': '权限不足'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from apps.games.models import Draw, GameStatistics
        from .draw_engine import Lottery11x5ProfitController
        from datetime import timedelta
        
        # 获取查询参数
        days = int(request.GET.get('days', 7))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        game = Lottery11x5Service.get_game()
        if not game:
            return Response({
                'success': False,
                'message': '游戏不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 获取期间内的开奖数据
        draws = Draw.objects.filter(
            game=game,
            status='COMPLETED',
            draw_time__date__range=[start_date, end_date]
        ).order_by('-draw_time')
        
        # 计算总体统计
        total_draws = draws.count()
        total_bets = sum(draw.total_bets for draw in draws)
        total_amount = sum(draw.total_amount for draw in draws)
        total_payout = sum(draw.total_payout for draw in draws)
        total_profit = total_amount - total_payout
        avg_profit_rate = (total_profit / total_amount * 100) if total_amount > 0 else 0
        
        # 每日统计
        daily_stats = []
        for draw in draws:
            daily_stats.append({
                'draw_number': draw.draw_number,
                'draw_time': draw.draw_time,
                'total_bets': draw.total_bets,
                'total_amount': float(draw.total_amount),
                'total_payout': float(draw.total_payout),
                'profit': float(draw.profit),
                'profit_rate': float((draw.profit / draw.total_amount * 100) if draw.total_amount > 0 else 0),
            })
        
        # 利润率分析
        profit_rates = [float((draw.profit / draw.total_amount * 100) if draw.total_amount > 0 else 0) for draw in draws]
        
        profit_controller = Lottery11x5ProfitController()
        adjustment_analysis = profit_controller.should_adjust_odds(
            [Decimal(str(rate/100)) for rate in profit_rates]
        )
        
        return Response({
            'success': True,
            'data': {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'days': days
                },
                'summary': {
                    'total_draws': total_draws,
                    'total_bets': total_bets,
                    'total_amount': float(total_amount),
                    'total_payout': float(total_payout),
                    'total_profit': float(total_profit),
                    'avg_profit_rate': float(avg_profit_rate),
                    'target_profit_rate': 18.0,
                },
                'daily_stats': daily_stats,
                'adjustment_analysis': {
                    'should_adjust': adjustment_analysis['should_adjust'],
                    'current_avg_rate': float(adjustment_analysis['current_avg_rate'] * 100),
                    'target_rate': float(adjustment_analysis['target_rate'] * 100),
                    'deviation_count': adjustment_analysis['deviation_count'],
                    'adjustment_direction': adjustment_analysis['adjustment_direction'],
                    'suggested_adjustment': float(adjustment_analysis['suggested_adjustment'] * 100),
                }
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取利润分析失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)