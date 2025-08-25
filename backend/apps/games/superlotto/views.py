"""
大乐透彩票API视图
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache

from .services import SuperLottoService


@api_view(['GET'])
def game_info(request):
    """
    获取大乐透游戏信息
    """
    try:
        game = SuperLottoService.get_game()
        if not game:
            return Response({
                'success': False,
                'message': '游戏不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        config = SuperLottoService.get_game_config()
        
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
                    'base_bet_amount': float(config.base_bet_amount),
                    'max_multiplier': config.max_multiplier,
                    'front_zone_range': [config.front_zone_min, config.front_zone_max],
                    'front_zone_count': config.front_zone_count,
                    'back_zone_range': [config.back_zone_min, config.back_zone_max],
                    'back_zone_count': config.back_zone_count,
                    'draw_days': config.get_draw_days_list(),
                    'draw_time': config.draw_time.strftime('%H:%M'),
                    'sales_stop_minutes': config.sales_stop_minutes,
                    'prize_amounts': {
                        'third_prize': float(config.third_prize_amount),
                        'fourth_prize': float(config.fourth_prize_amount),
                        'fifth_prize': float(config.fifth_prize_amount),
                        'sixth_prize': float(config.sixth_prize_amount),
                        'seventh_prize': float(config.seventh_prize_amount),
                        'eighth_prize': float(config.eighth_prize_amount),
                        'ninth_prize': float(config.ninth_prize_amount),
                    }
                } if config else None,
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
    获取当前期次信息
    """
    try:
        result = SuperLottoService.get_draw_info()
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取期次信息失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def draw_info(request, draw_number):
    """
    获取指定期次信息
    """
    try:
        result = SuperLottoService.get_draw_info(draw_number)
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取期次信息失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def latest_draws(request):
    """
    获取最近开奖记录
    """
    try:
        limit = int(request.GET.get('limit', 10))
        draws = SuperLottoService.get_latest_draws(limit)
        
        return Response({
            'success': True,
            'data': {
                'draws': draws,
                'count': len(draws)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取开奖记录失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def calculate_bet(request):
    """
    计算投注金额和注数
    """
    try:
        bet_type = request.data.get('bet_type')
        front_numbers = request.data.get('front_numbers', [])
        back_numbers = request.data.get('back_numbers', [])
        multiplier = int(request.data.get('multiplier', 1))
        
        # 胆拖相关参数
        front_dan = request.data.get('front_dan_numbers', [])
        front_tuo = request.data.get('front_tuo_numbers', [])
        back_dan = request.data.get('back_dan_numbers', [])
        back_tuo = request.data.get('back_tuo_numbers', [])
        
        if not bet_type:
            return Response({
                'success': False,
                'message': '请选择投注类型'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = SuperLottoService.calculate_bet_amount(
            bet_type, front_numbers, back_numbers,
            front_dan, front_tuo, back_dan, back_tuo, multiplier
        )
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'计算失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_bet(request):
    """
    投注下单
    """
    try:
        result = SuperLottoService.place_bet(request.user, request.data)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'投注失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_bets(request):
    """
    获取用户投注记录
    """
    try:
        draw_number = request.GET.get('draw_number')
        limit = int(request.GET.get('limit', 20))
        
        bets = SuperLottoService.get_user_bets(
            user=request.user,
            draw_number=draw_number,
            limit=limit
        )
        
        return Response({
            'success': True,
            'data': {
                'bets': bets,
                'count': len(bets)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取投注记录失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def random_numbers(request):
    """
    生成随机号码（机选）
    """
    try:
        result = SuperLottoService.generate_random_numbers()
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'生成随机号码失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def validate_numbers(request):
    """
    验证号码有效性
    """
    try:
        front_numbers = request.data.get('front_numbers', [])
        back_numbers = request.data.get('back_numbers', [])
        
        result = SuperLottoService.validate_numbers(front_numbers, back_numbers)
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'验证失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 管理员开奖接口
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_draw_numbers(request):
    """
    生成开奖号码（管理员功能）
    """
    try:
        # 这里可以添加管理员权限检查
        if not request.user.is_staff:
            return Response({
                'success': False,
                'message': '权限不足'
            }, status=status.HTTP_403_FORBIDDEN)
        
        result = SuperLottoService.generate_draw_numbers()
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'生成开奖号码失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def conduct_draw(request):
    """
    执行开奖（管理员功能）
    """
    try:
        # 检查管理员权限
        if not request.user.is_staff:
            return Response({
                'success': False,
                'message': '权限不足'
            }, status=status.HTTP_403_FORBIDDEN)
        
        draw_id = request.data.get('draw_id')
        front_numbers = request.data.get('front_numbers')
        back_numbers = request.data.get('back_numbers')
        
        if not draw_id:
            return Response({
                'success': False,
                'message': '缺少期次ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = SuperLottoService.conduct_draw(draw_id, front_numbers, back_numbers)
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'开奖失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_next_draw(request):
    """
    创建下一期次（管理员功能）
    """
    try:
        # 检查管理员权限
        if not request.user.is_staff:
            return Response({
                'success': False,
                'message': '权限不足'
            }, status=status.HTTP_403_FORBIDDEN)
        
        result = SuperLottoService.create_next_draw()
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'创建期次失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_draw_sales(request):
    """
    停止期次销售（管理员功能）
    """
    try:
        # 检查管理员权限
        if not request.user.is_staff:
            return Response({
                'success': False,
                'message': '权限不足'
            }, status=status.HTTP_403_FORBIDDEN)
        
        draw_id = request.data.get('draw_id')
        
        if not draw_id:
            return Response({
                'success': False,
                'message': '缺少期次ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = SuperLottoService.close_draw_sales(draw_id)
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'停售失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)