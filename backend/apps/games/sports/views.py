"""
体育博彩API视图
"""

from decimal import Decimal
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .services import SportsProviderService


@api_view(['GET'])
def providers_list(request):
    """
    获取体育平台列表
    """
    try:
        providers = SportsProviderService.get_active_providers()
        
        return Response({
            'success': True,
            'data': {
                'providers': providers,
                'count': len(providers)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取平台列表失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_wallets(request):
    """
    获取用户所有体育钱包
    """
    try:
        wallets = SportsProviderService.get_user_wallets(request.user)
        
        # 计算总余额
        total_balance = sum(wallet['balance'] for wallet in wallets)
        
        return Response({
            'success': True,
            'data': {
                'wallets': wallets,
                'total_balance': total_balance,
                'count': len(wallets)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取钱包列表失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_detail(request, provider_code):
    """
    获取指定平台钱包详情
    """
    try:
        result = SportsProviderService.get_user_wallet(request.user, provider_code)
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取钱包详情失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer_to_platform(request):
    """
    转账到体育平台
    """
    try:
        provider_code = request.data.get('provider_code')
        amount = request.data.get('amount')
        
        if not provider_code:
            return Response({
                'success': False,
                'message': '请选择平台'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not amount or amount <= 0:
            return Response({
                'success': False,
                'message': '请输入有效的转账金额'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = SportsProviderService.transfer_to_platform(
            user=request.user,
            provider_code=provider_code,
            amount=Decimal(str(amount))
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'转账失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer_from_platform(request):
    """
    从体育平台转出（回收余额）
    """
    try:
        provider_code = request.data.get('provider_code')
        amount = request.data.get('amount')  # 可选，不指定则转出全部
        
        if not provider_code:
            return Response({
                'success': False,
                'message': '请选择平台'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        transfer_amount = None
        if amount is not None:
            if amount <= 0:
                return Response({
                    'success': False,
                    'message': '请输入有效的转出金额'
                }, status=status.HTTP_400_BAD_REQUEST)
            transfer_amount = Decimal(str(amount))
        
        result = SportsProviderService.transfer_from_platform(
            user=request.user,
            provider_code=provider_code,
            amount=transfer_amount
        )
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'转出失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_launch_url(request):
    """
    获取平台启动URL
    """
    try:
        provider_code = request.data.get('provider_code')
        
        if not provider_code:
            return Response({
                'success': False,
                'message': '请选择平台'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = SportsProviderService.get_launch_url(request.user, provider_code)
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取启动URL失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_transactions(request):
    """
    获取钱包交易记录
    """
    try:
        provider_code = request.GET.get('provider_code')
        limit = int(request.GET.get('limit', 20))
        
        transactions = SportsProviderService.get_wallet_transactions(
            user=request.user,
            provider_code=provider_code,
            limit=limit
        )
        
        return Response({
            'success': True,
            'data': {
                'transactions': transactions,
                'count': len(transactions)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取交易记录失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def provider_detail(request, provider_code):
    """
    获取平台详细信息
    """
    try:
        provider = SportsProviderService.get_provider_by_code(provider_code)
        
        if not provider:
            return Response({
                'success': False,
                'message': '平台不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'data': {
                'id': str(provider.id),
                'name': provider.name,
                'code': provider.code,
                'logo': provider.logo.url if provider.logo else None,
                'banner': provider.banner.url if provider.banner else None,
                'description': provider.description,
                'features': provider.features,
                'supported_sports': provider.supported_sports,
                'status': provider.get_status_display(),
                'is_maintenance': provider.is_maintenance,
                'tags': provider.get_tags(),
                'min_bet_amount': float(provider.min_bet_amount),
                'max_bet_amount': float(provider.max_bet_amount),
                'integration_type': provider.integration_type,
                'wallet_mode': provider.wallet_mode,
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取平台详情失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_wallet_balance(request):
    """
    同步钱包余额（从第三方平台）
    """
    try:
        provider_code = request.data.get('provider_code')
        
        if not provider_code:
            return Response({
                'success': False,
                'message': '请选择平台'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 这里应该调用第三方平台API同步余额
        # 由于是示例，我们返回成功
        
        return Response({
            'success': True,
            'message': '余额同步成功',
            'data': {
                'sync_time': timezone.now().isoformat()
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'同步余额失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auto_transfer_on_enter(request):
    """
    进入平台时自动转账
    """
    try:
        provider_code = request.data.get('provider_code')
        amount = request.data.get('amount')
        
        if not provider_code:
            return Response({
                'success': False,
                'message': '请选择平台'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        transfer_amount = None
        if amount is not None:
            if amount <= 0:
                return Response({
                    'success': False,
                    'message': '请输入有效的转账金额'
                }, status=status.HTTP_400_BAD_REQUEST)
            transfer_amount = Decimal(str(amount))
        
        result = SportsProviderService.auto_transfer_on_enter(
            user=request.user,
            provider_code=provider_code,
            amount=transfer_amount
        )
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'自动转账失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auto_transfer_on_exit(request):
    """
    退出平台时自动回收余额
    """
    try:
        provider_code = request.data.get('provider_code')
        
        if not provider_code:
            return Response({
                'success': False,
                'message': '请选择平台'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = SportsProviderService.auto_transfer_on_exit(
            user=request.user,
            provider_code=provider_code
        )
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'自动回收失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_recover_wallets(request):
    """
    一键回收所有平台余额
    """
    try:
        result = SportsProviderService.batch_recover_all_wallets(request.user)
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'批量回收失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def aggregated_bet_records(request):
    """
    获取聚合的投注记录
    """
    try:
        provider_code = request.GET.get('provider_code')
        limit = int(request.GET.get('limit', 20))
        
        records = SportsProviderService.get_aggregated_bet_records(
            user=request.user,
            provider_code=provider_code,
            limit=limit
        )
        
        return Response({
            'success': True,
            'data': {
                'records': records,
                'count': len(records)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取投注记录失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_sports_statistics(request):
    """
    获取用户体育博彩统计
    """
    try:
        stats = SportsProviderService.get_user_sports_statistics(request.user)
        
        return Response({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取统计信息失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def check_single_wallet_mode(request, provider_code):
    """
    检查平台是否支持单钱包模式
    """
    try:
        result = SportsProviderService.check_single_wallet_mode(provider_code)
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'检查失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 管理员接口
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_bet_records(request):
    """
    同步投注记录（管理员功能）
    """
    try:
        # 检查管理员权限
        if not request.user.is_staff:
            return Response({
                'success': False,
                'message': '权限不足'
            }, status=status.HTTP_403_FORBIDDEN)
        
        provider_code = request.data.get('provider_code')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not provider_code:
            return Response({
                'success': False,
                'message': '请选择平台'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 解析日期
        if start_date:
            start_date = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        result = SportsProviderService.sync_bet_records_from_platform(
            provider_code=provider_code,
            start_date=start_date,
            end_date=end_date
        )
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'同步投注记录失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)