"""
支付回调处理视图
"""

import json
import hashlib
import hmac
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema

from .models import Transaction
from .tasks import process_deposit_callback
from apps.core.utils import get_client_ip


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
@extend_schema(
    summary="Paystack支付回调",
    description="处理Paystack支付成功/失败回调"
)
def paystack_callback(request):
    """
    Paystack支付回调处理
    """
    try:
        # 验证签名
        signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
        if not signature:
            return HttpResponse('Missing signature', status=400)
        
        # 计算期望的签名
        body = request.body
        expected_signature = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode(),
            body,
            hashlib.sha512
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return HttpResponse('Invalid signature', status=400)
        
        # 解析回调数据
        data = json.loads(body.decode('utf-8'))
        event = data.get('event')
        
        if event == 'charge.success':
            # 支付成功
            charge_data = data.get('data', {})
            reference = charge_data.get('reference')
            amount = charge_data.get('amount', 0) / 100  # 从kobo转换为naira
            status_code = charge_data.get('status')
            
            # 查找对应的交易记录
            try:
                transaction = Transaction.objects.get(
                    reference_id=reference,
                    type='DEPOSIT'
                )
                
                # 验证金额
                if abs(float(transaction.amount) - amount) > 0.01:
                    return HttpResponse('Amount mismatch', status=400)
                
                # 异步处理存款回调
                process_deposit_callback.delay(
                    str(transaction.id),
                    'success' if status_code == 'success' else 'failed',
                    charge_data.get('id', ''),
                    {
                        'gateway': 'paystack',
                        'gateway_response': charge_data.get('gateway_response'),
                        'paid_at': charge_data.get('paid_at'),
                        'channel': charge_data.get('channel'),
                        'ip_address': get_client_ip(request),
                    }
                )
                
                return HttpResponse('OK', status=200)
                
            except Transaction.DoesNotExist:
                return HttpResponse('Transaction not found', status=404)
        
        return HttpResponse('Event not handled', status=200)
        
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
@extend_schema(
    summary="Flutterwave支付回调",
    description="处理Flutterwave支付成功/失败回调"
)
def flutterwave_callback(request):
    """
    Flutterwave支付回调处理
    """
    try:
        # 验证签名
        signature = request.META.get('HTTP_VERIF_HASH')
        if not signature:
            return HttpResponse('Missing signature', status=400)
        
        expected_signature = settings.FLUTTERWAVE_SECRET_HASH
        if signature != expected_signature:
            return HttpResponse('Invalid signature', status=400)
        
        # 解析回调数据
        data = json.loads(request.body.decode('utf-8'))
        
        tx_ref = data.get('txRef')
        status_code = data.get('status')
        amount = data.get('amount', 0)
        
        # 查找对应的交易记录
        try:
            transaction = Transaction.objects.get(
                reference_id=tx_ref,
                type='DEPOSIT'
            )
            
            # 验证金额
            if abs(float(transaction.amount) - amount) > 0.01:
                return HttpResponse('Amount mismatch', status=400)
            
            # 异步处理存款回调
            process_deposit_callback.delay(
                str(transaction.id),
                'success' if status_code == 'successful' else 'failed',
                data.get('flwRef', ''),
                {
                    'gateway': 'flutterwave',
                    'processor_response': data.get('processorResponse'),
                    'charged_amount': data.get('chargedAmount'),
                    'app_fee': data.get('appfee'),
                    'merchant_fee': data.get('merchantfee'),
                    'ip_address': get_client_ip(request),
                }
            )
            
            return HttpResponse('OK', status=200)
            
        except Transaction.DoesNotExist:
            return HttpResponse('Transaction not found', status=404)
        
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
@extend_schema(
    summary="支付成功页面",
    description="支付成功后的跳转页面"
)
def payment_success(request):
    """
    支付成功页面
    """
    reference = request.GET.get('reference')
    
    try:
        transaction = Transaction.objects.get(
            reference_id=reference,
            type='DEPOSIT'
        )
        
        return Response({
            'success': True,
            'message': '支付成功',
            'data': {
                'transaction_id': str(transaction.id),
                'reference': transaction.reference_id,
                'amount': float(transaction.amount),
                'status': transaction.status,
            }
        }, status=status.HTTP_200_OK)
        
    except Transaction.DoesNotExist:
        return Response({
            'success': False,
            'message': '交易不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
@extend_schema(
    summary="支付失败页面",
    description="支付失败后的跳转页面"
)
def payment_failed(request):
    """
    支付失败页面
    """
    reference = request.GET.get('reference')
    
    try:
        transaction = Transaction.objects.get(
            reference_id=reference,
            type='DEPOSIT'
        )
        
        # 标记交易失败
        if transaction.status == 'PENDING':
            transaction.mark_failed('用户取消支付')
        
        return Response({
            'success': False,
            'message': '支付失败',
            'data': {
                'transaction_id': str(transaction.id),
                'reference': transaction.reference_id,
                'amount': float(transaction.amount),
                'status': transaction.status,
            }
        }, status=status.HTTP_200_OK)
        
    except Transaction.DoesNotExist:
        return Response({
            'success': False,
            'message': '交易不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
@extend_schema(
    summary="移动货币回调",
    description="处理移动货币支付回调（OPay/PalmPay/Moniepoint）"
)
def mobile_money_callback(request):
    """
    移动货币支付回调处理
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        
        provider = data.get('provider')  # opay, palmpay, moniepoint
        reference = data.get('reference')
        status_code = data.get('status')
        amount = data.get('amount', 0)
        
        # 查找对应的交易记录
        try:
            transaction = Transaction.objects.get(
                reference_id=reference,
                type='DEPOSIT'
            )
            
            # 验证金额
            if abs(float(transaction.amount) - amount) > 0.01:
                return HttpResponse('Amount mismatch', status=400)
            
            # 异步处理存款回调
            process_deposit_callback.delay(
                str(transaction.id),
                'success' if status_code in ['success', 'successful', 'completed'] else 'failed',
                data.get('transaction_id', ''),
                {
                    'gateway': f'mobile_money_{provider}',
                    'provider': provider,
                    'phone_number': data.get('phone_number'),
                    'network': data.get('network'),
                    'ip_address': get_client_ip(request),
                }
            )
            
            return HttpResponse('OK', status=200)
            
        except Transaction.DoesNotExist:
            return HttpResponse('Transaction not found', status=404)
        
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)