"""
财务管理视图
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db import transaction, models
from django.core.cache import cache
from datetime import timedelta, date
from decimal import Decimal
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import UserBalance, Transaction, BalanceLog, BankAccount, PaymentMethod
from .serializers import (
    UserBalanceSerializer,
    TransactionSerializer,
    TransactionCreateSerializer,
    BalanceLogSerializer,
    BankAccountSerializer,
    PaymentMethodSerializer,
    BalanceOperationSerializer,
    TransactionFilterSerializer,
    DepositRequestSerializer,
    WithdrawRequestSerializer,
)
from .services import FinanceService
from apps.core.security import SecurityManager


class UserBalanceView(APIView):
    """
    用户余额查询
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="获取用户余额",
        description="获取当前用户的详细余额信息",
        responses={200: UserBalanceSerializer}
    )
    def get(self, request):
        user = request.user
        
        # 获取或创建用户余额
        balance, created = UserBalance.objects.get_or_create(user=user)
        
        serializer = UserBalanceSerializer(balance)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class BalanceOperationView(APIView):
    """
    余额操作（管理员功能）
    """
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    @extend_schema(
        summary="余额操作",
        description="管理员执行余额冻结、解冻、增加、扣除操作",
        request=BalanceOperationSerializer
    )
    def post(self, request):
        serializer = BalanceOperationSerializer(data=request.data)
        if serializer.is_valid():
            operation = serializer.validated_data['operation']
            amount = serializer.validated_data['amount']
            balance_type = serializer.validated_data['balance_type']
            reason = serializer.validated_data.get('reason', '')
            
            # 获取目标用户（这里简化为当前用户，实际应该从参数获取）
            target_user = request.user
            balance, created = UserBalance.objects.get_or_create(user=target_user)
            
            success = False
            message = ''
            
            try:
                if operation == 'freeze':
                    success = balance.freeze_balance(amount, reason)
                    message = '余额冻结成功' if success else '余额冻结失败'
                elif operation == 'unfreeze':
                    success = balance.unfreeze_balance(amount)
                    message = '余额解冻成功' if success else '余额解冻失败'
                elif operation == 'add':
                    success = balance.add_balance(amount, balance_type, reason)
                    message = '余额增加成功' if success else '余额增加失败'
                elif operation == 'deduct':
                    success = balance.deduct_balance(amount, balance_type, reason)
                    message = '余额扣除成功' if success else '余额扣除失败'
                
                if success:
                    return Response({
                        'success': True,
                        'message': message,
                        'data': UserBalanceSerializer(balance).data
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'success': False,
                        'message': message
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'操作失败: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': False,
            'message': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class TransactionListView(generics.ListAPIView):
    """
    交易记录列表
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Transaction.objects.filter(user=user)
        
        # 应用筛选条件
        filter_serializer = TransactionFilterSerializer(data=self.request.query_params)
        if filter_serializer.is_valid():
            filters = filter_serializer.validated_data
            
            # 交易类型筛选
            if 'type' in filters:
                queryset = queryset.filter(type=filters['type'])
            
            # 时间范围筛选
            time_range = filters.get('time_range', 'month')
            if time_range == 'today':
                queryset = queryset.filter(created_at__date=date.today())
            elif time_range == '3days':
                queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=3))
            elif time_range == 'week':
                queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=7))
            elif time_range == 'month':
                queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=30))
            elif time_range == 'custom':
                start_date = filters.get('start_date')
                end_date = filters.get('end_date')
                if start_date:
                    queryset = queryset.filter(created_at__date__gte=start_date)
                if end_date:
                    queryset = queryset.filter(created_at__date__lte=end_date)
            
            # 金额范围筛选
            if 'min_amount' in filters:
                queryset = queryset.filter(amount__gte=filters['min_amount'])
            if 'max_amount' in filters:
                queryset = queryset.filter(amount__lte=filters['max_amount'])
        
        return queryset.select_related('user')
    
    @extend_schema(
        summary="获取交易记录",
        description="获取当前用户的交易记录，支持筛选",
        parameters=[
            OpenApiParameter('type', str, description='交易类型'),
            OpenApiParameter('time_range', str, description='时间范围'),
            OpenApiParameter('start_date', str, description='开始日期'),
            OpenApiParameter('end_date', str, description='结束日期'),
            OpenApiParameter('min_amount', float, description='最小金额'),
            OpenApiParameter('max_amount', float, description='最大金额'),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TransactionDetailView(generics.RetrieveAPIView):
    """
    交易记录详情
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="获取交易详情",
        description="获取指定交易的详细信息"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class BalanceLogListView(generics.ListAPIView):
    """
    余额变动日志
    """
    serializer_class = BalanceLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return BalanceLog.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="获取余额变动日志",
        description="获取当前用户的余额变动历史记录"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class BankAccountListCreateView(generics.ListCreateAPIView):
    """
    银行账户管理
    """
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="获取银行账户列表",
        description="获取当前用户的银行账户列表"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="添加银行账户",
        description="为当前用户添加新的银行账户"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class BankAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    银行账户详情
    """
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="获取银行账户详情",
        description="获取指定银行账户的详细信息"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="更新银行账户",
        description="更新指定银行账户的信息"
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="删除银行账户",
        description="删除指定的银行账户"
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class PaymentMethodListView(generics.ListAPIView):
    """
    支付方式列表
    """
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(is_active=True)
    
    @extend_schema(
        summary="获取支付方式列表",
        description="获取可用的支付方式列表"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DepositRequestView(APIView):
    """
    存款申请
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="申请存款",
        description="创建存款订单，支持多种支付方式",
        request=DepositRequestSerializer
    )
    def post(self, request):
        serializer = DepositRequestSerializer(data=request.data)
        if serializer.is_valid():
            payment_method = serializer.payment_method
            amount = serializer.validated_data['amount']
            
            # 安全检查
            security_result = SecurityManager.perform_security_check(
                request.user, 'DEPOSIT', {'amount': float(amount)}
            )
            
            if not security_result['allowed']:
                return Response({
                    'success': False,
                    'message': '存款请求被拒绝，请联系客服',
                    'error_code': 'SECURITY_BLOCKED'
                }, status=status.HTTP_403_FORBIDDEN)
            
            try:
                # 创建存款订单
                deposit_result = FinanceService.create_deposit_order(
                    user=request.user,
                    payment_method=payment_method,
                    amount=amount
                )
                
                if deposit_result['success']:
                    return Response({
                        'success': True,
                        'message': '存款订单创建成功',
                        'data': deposit_result['data']
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'success': False,
                        'message': deposit_result['message']
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'存款申请失败: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': False,
            'message': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class WithdrawRequestView(APIView):
    """
    提款申请
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="申请提款",
        description="创建提款订单，需要验证取款密码和KYC状态",
        request=WithdrawRequestSerializer
    )
    def post(self, request):
        # 检查KYC状态
        if request.user.kyc_status != 'APPROVED':
            return Response({
                'success': False,
                'message': '请先完成KYC身份验证',
                'error_code': 'KYC_REQUIRED'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = WithdrawRequestSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            bank_account = serializer.bank_account
            amount = serializer.validated_data['amount']
            
            # 安全检查
            security_result = SecurityManager.perform_security_check(
                request.user, 'WITHDRAW', {'amount': float(amount)}
            )
            
            if not security_result['allowed']:
                return Response({
                    'success': False,
                    'message': '提款请求被拒绝，请联系客服',
                    'error_code': 'SECURITY_BLOCKED'
                }, status=status.HTTP_403_FORBIDDEN)
            
            try:
                # 创建提款订单
                withdraw_result = FinanceService.create_withdraw_order(
                    user=request.user,
                    bank_account=bank_account,
                    amount=amount
                )
                
                if withdraw_result['success']:
                    return Response({
                        'success': True,
                        'message': '提款申请提交成功',
                        'data': withdraw_result['data']
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'success': False,
                        'message': withdraw_result['message']
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'提款申请失败: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': False,
            'message': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class DepositStatusView(APIView):
    """
    存款状态查询
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="查询存款状态",
        description="根据交易ID或参考ID查询存款状态",
        parameters=[
            OpenApiParameter('transaction_id', str, description='交易ID'),
            OpenApiParameter('reference_id', str, description='参考ID'),
        ]
    )
    def get(self, request):
        transaction_id = request.query_params.get('transaction_id')
        reference_id = request.query_params.get('reference_id')
        
        if not transaction_id and not reference_id:
            return Response({
                'success': False,
                'message': '请提供交易ID或参考ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if transaction_id:
                transaction = Transaction.objects.get(
                    id=transaction_id,
                    user=request.user,
                    type='DEPOSIT'
                )
            else:
                transaction = Transaction.objects.get(
                    reference_id=reference_id,
                    user=request.user,
                    type='DEPOSIT'
                )
            
            # 获取支付方式信息
            payment_method_id = transaction.metadata.get('payment_method_id')
            payment_method_name = transaction.metadata.get('payment_method_name', '未知')
            
            response_data = {
                'transaction_id': str(transaction.id),
                'reference_id': transaction.reference_id,
                'amount': float(transaction.amount),
                'fee': float(transaction.fee),
                'actual_amount': float(transaction.actual_amount),
                'status': transaction.status,
                'status_display': transaction.get_status_display(),
                'payment_method': payment_method_name,
                'created_at': transaction.created_at,
                'processed_at': transaction.processed_at,
                'description': transaction.description,
            }
            
            # 根据状态提供不同的信息
            if transaction.status == 'PENDING':
                response_data['message'] = '存款正在处理中，请耐心等待'
                response_data['estimated_time'] = '通常在5-30分钟内完成'
            elif transaction.status == 'COMPLETED':
                response_data['message'] = '存款已成功到账'
            elif transaction.status == 'FAILED':
                response_data['message'] = '存款失败，如有疑问请联系客服'
                response_data['failure_reason'] = transaction.metadata.get('failure_reason', '未知原因')
            
            return Response({
                'success': True,
                'data': response_data
            }, status=status.HTTP_200_OK)
            
        except Transaction.DoesNotExist:
            return Response({
                'success': False,
                'message': '交易记录不存在'
            }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def deposit_limits(request):
    """
    获取存款限制信息
    """
    user = request.user
    
    # 获取用户VIP信息
    vip_info = user.get_vip_info()
    
    # 获取可用的支付方式
    payment_methods = PaymentMethod.objects.filter(
        is_active=True,
        is_deposit_enabled=True
    )
    
    # 计算今日已存款金额
    from datetime import date
    today_deposits = Transaction.objects.filter(
        user=user,
        type='DEPOSIT',
        status='COMPLETED',
        created_at__date=date.today()
    ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
    
    # 基础限制信息
    limits_info = {
        'kyc_required': user.kyc_status != 'APPROVED',
        'kyc_status': user.kyc_status,
        'vip_level': user.vip_level,
        'today_deposited': float(today_deposits),
        'payment_methods': []
    }
    
    # 添加KYC提醒
    if user.kyc_status != 'APPROVED':
        limits_info['kyc_reminder'] = {
            'title': '完成身份验证，享受更高额度',
            'message': '完成KYC身份验证后，您可以享受更高的存款和提款额度。',
            'action_text': '立即验证',
            'action_url': '/api/v1/users/kyc/submit/'
        }
    
    # 添加支付方式信息
    for method in payment_methods:
        method_info = {
            'id': str(method.id),
            'name': method.name,
            'provider': method.get_provider_display(),
            'method_type': method.get_method_type_display(),
            'min_amount': float(method.min_amount),
            'max_amount': float(method.max_amount),
            'daily_limit': float(method.daily_limit),
            'fee_type': method.fee_type,
            'fee_value': float(method.fee_value),
            'is_recommended': method.provider in ['PAYSTACK', 'FLUTTERWAVE'],
        }
        
        # 计算手续费示例
        example_amount = Decimal('10000')  # 1万奈拉示例
        example_fee = method.calculate_fee(example_amount)
        method_info['fee_example'] = {
            'amount': float(example_amount),
            'fee': float(example_fee),
            'actual_amount': float(example_amount - example_fee)
        }
        
        limits_info['payment_methods'].append(method_info)
    
    return Response({
        'success': True,
        'data': limits_info
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def financial_summary(request):
    """
    财务概览
    """
    user = request.user
    
    # 获取用户余额
    try:
        balance = user.balance
        balance_data = UserBalanceSerializer(balance).data
    except UserBalance.DoesNotExist:
        balance_data = {
            'main_balance': 0,
            'bonus_balance': 0,
            'frozen_balance': 0,
            'total_balance': 0,
            'available_balance': 0
        }
    
    # 获取今日交易统计
    today = date.today()
    today_transactions = Transaction.objects.filter(
        user=user,
        created_at__date=today
    )
    
    today_stats = {
        'deposit_count': today_transactions.filter(type='DEPOSIT').count(),
        'deposit_amount': sum(
            t.amount for t in today_transactions.filter(type='DEPOSIT', status='COMPLETED')
        ),
        'withdraw_count': today_transactions.filter(type='WITHDRAW').count(),
        'withdraw_amount': sum(
            t.amount for t in today_transactions.filter(type='WITHDRAW', status='COMPLETED')
        ),
        'bet_count': today_transactions.filter(type='BET').count(),
        'bet_amount': sum(
            t.amount for t in today_transactions.filter(type='BET', status='COMPLETED')
        ),
        'win_amount': sum(
            t.amount for t in today_transactions.filter(type='WIN', status='COMPLETED')
        ),
    }
    
    # 获取本月交易统计
    month_start = date.today().replace(day=1)
    month_transactions = Transaction.objects.filter(
        user=user,
        created_at__date__gte=month_start
    )
    
    month_stats = {
        'total_deposit': sum(
            t.amount for t in month_transactions.filter(type='DEPOSIT', status='COMPLETED')
        ),
        'total_withdraw': sum(
            t.amount for t in month_transactions.filter(type='WITHDRAW', status='COMPLETED')
        ),
        'total_bet': sum(
            t.amount for t in month_transactions.filter(type='BET', status='COMPLETED')
        ),
        'total_win': sum(
            t.amount for t in month_transactions.filter(type='WIN', status='COMPLETED')
        ),
    }
    
    # VIP信息
    vip_info = user.get_vip_info()
    
    return Response({
        'success': True,
        'data': {
            'balance': balance_data,
            'today_stats': today_stats,
            'month_stats': month_stats,
            'vip_info': vip_info,
            'kyc_status': user.kyc_status,
            'two_factor_enabled': user.two_factor_enabled,
        }
    }, status=status.HTTP_200_OK)