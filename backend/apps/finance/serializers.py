"""
财务管理序列化器
"""

from rest_framework import serializers
from decimal import Decimal
from .models import UserBalance, Transaction, BalanceLog, BankAccount, PaymentMethod


class UserBalanceSerializer(serializers.ModelSerializer):
    """
    用户余额序列化器
    """
    total_balance = serializers.SerializerMethodField()
    available_balance = serializers.SerializerMethodField()
    
    class Meta:
        model = UserBalance
        fields = [
            'main_balance', 'bonus_balance', 'frozen_balance',
            'total_balance', 'available_balance', 'updated_at'
        ]
        read_only_fields = ['updated_at']
    
    def get_total_balance(self, obj):
        return float(obj.get_total_balance())
    
    def get_available_balance(self, obj):
        return float(obj.get_available_balance())


class TransactionSerializer(serializers.ModelSerializer):
    """
    交易记录序列化器
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'type', 'type_display', 'amount', 'fee', 'actual_amount',
            'status', 'status_display', 'reference_id', 'description',
            'created_at', 'processed_at'
        ]
        read_only_fields = [
            'id', 'actual_amount', 'processed_at', 'created_at'
        ]


class TransactionCreateSerializer(serializers.ModelSerializer):
    """
    创建交易序列化器
    """
    class Meta:
        model = Transaction
        fields = ['type', 'amount', 'description', 'metadata']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("金额必须大于0")
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BalanceLogSerializer(serializers.ModelSerializer):
    """
    余额变动日志序列化器
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = BalanceLog
        fields = [
            'id', 'type', 'type_display', 'amount', 'balance_before',
            'balance_after', 'description', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BankAccountSerializer(serializers.ModelSerializer):
    """
    银行账户序列化器
    """
    bank_display = serializers.CharField(source='get_bank_code_display', read_only=True)
    
    class Meta:
        model = BankAccount
        fields = [
            'id', 'bank_code', 'bank_display', 'account_number',
            'account_name', 'is_verified', 'is_default', 'created_at'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at']
    
    def validate_account_name(self, value):
        """验证账户名是否与注册姓名一致"""
        user = self.context['request'].user
        if value.upper() != user.full_name.upper():
            raise serializers.ValidationError("账户名必须与注册姓名一致")
        return value
    
    def validate(self, attrs):
        """验证银行账户唯一性"""
        user = self.context['request'].user
        bank_code = attrs.get('bank_code')
        account_number = attrs.get('account_number')
        
        # 检查是否已存在相同的银行账户
        existing = BankAccount.objects.filter(
            user=user,
            bank_code=bank_code,
            account_number=account_number
        )
        
        if self.instance:
            existing = existing.exclude(id=self.instance.id)
        
        if existing.exists():
            raise serializers.ValidationError("该银行账户已存在")
        
        return attrs
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PaymentMethodSerializer(serializers.ModelSerializer):
    """
    支付方式序列化器
    """
    method_type_display = serializers.CharField(source='get_method_type_display', read_only=True)
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'name', 'method_type', 'method_type_display',
            'provider', 'provider_display', 'min_amount', 'max_amount',
            'daily_limit', 'fee_type', 'fee_value', 'is_active',
            'is_deposit_enabled', 'is_withdraw_enabled'
        ]
        read_only_fields = ['id']


class BalanceOperationSerializer(serializers.Serializer):
    """
    余额操作序列化器
    """
    OPERATION_CHOICES = [
        ('freeze', '冻结'),
        ('unfreeze', '解冻'),
        ('add', '增加'),
        ('deduct', '扣除'),
    ]
    
    BALANCE_TYPE_CHOICES = [
        ('main', '主余额'),
        ('bonus', '奖金余额'),
        ('available', '可用余额'),
    ]
    
    operation = serializers.ChoiceField(choices=OPERATION_CHOICES)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('0.01'))
    balance_type = serializers.ChoiceField(choices=BALANCE_TYPE_CHOICES, default='available')
    reason = serializers.CharField(max_length=200, required=False, allow_blank=True)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("金额必须大于0")
        return value


class TransactionFilterSerializer(serializers.Serializer):
    """
    交易记录筛选序列化器
    """
    TYPE_CHOICES = [
        ('DEPOSIT', '存款'),
        ('WITHDRAW', '提款'),
        ('BET', '投注'),
        ('WIN', '中奖'),
        ('REWARD', '奖励'),
        ('REFUND', '退款'),
        ('ADJUSTMENT', '调整'),
    ]
    
    TIME_RANGE_CHOICES = [
        ('today', '今天'),
        ('3days', '三天内'),
        ('week', '一周内'),
        ('month', '一月内'),
        ('custom', '自定义'),
    ]
    
    type = serializers.ChoiceField(choices=TYPE_CHOICES, required=False)
    time_range = serializers.ChoiceField(choices=TIME_RANGE_CHOICES, default='month')
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    min_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    max_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    
    def validate(self, attrs):
        time_range = attrs.get('time_range')
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if time_range == 'custom':
            if not start_date or not end_date:
                raise serializers.ValidationError("自定义时间范围需要提供开始和结束日期")
            
            if start_date > end_date:
                raise serializers.ValidationError("开始日期不能晚于结束日期")
        
        min_amount = attrs.get('min_amount')
        max_amount = attrs.get('max_amount')
        
        if min_amount and max_amount and min_amount > max_amount:
            raise serializers.ValidationError("最小金额不能大于最大金额")
        
        return attrs


class DepositRequestSerializer(serializers.Serializer):
    """
    存款请求序列化器
    """
    payment_method_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('100.00'))
    
    def validate_payment_method_id(self, value):
        try:
            payment_method = PaymentMethod.objects.get(
                id=value,
                is_active=True,
                is_deposit_enabled=True
            )
            self.payment_method = payment_method
            return value
        except PaymentMethod.DoesNotExist:
            raise serializers.ValidationError("支付方式不存在或不可用")
    
    def validate_amount(self, value):
        if hasattr(self, 'payment_method'):
            if value < self.payment_method.min_amount:
                raise serializers.ValidationError(f"最小存款金额为 ₦{self.payment_method.min_amount}")
            
            if value > self.payment_method.max_amount:
                raise serializers.ValidationError(f"最大存款金额为 ₦{self.payment_method.max_amount}")
        
        return value


class WithdrawRequestSerializer(serializers.Serializer):
    """
    提款请求序列化器
    """
    bank_account_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('100.00'))
    withdraw_password = serializers.CharField(max_length=100, write_only=True)
    
    def validate_bank_account_id(self, value):
        user = self.context['request'].user
        try:
            bank_account = BankAccount.objects.get(
                id=value,
                user=user,
                is_verified=True
            )
            self.bank_account = bank_account
            return value
        except BankAccount.DoesNotExist:
            raise serializers.ValidationError("银行账户不存在或未验证")
    
    def validate_withdraw_password(self, value):
        user = self.context['request'].user
        # 这里可以实现取款密码验证逻辑
        # 暂时使用登录密码验证
        if not user.check_password(value):
            raise serializers.ValidationError("取款密码错误")
        return value
    
    def validate_amount(self, value):
        user = self.context['request'].user
        
        # 检查用户余额
        try:
            balance = user.balance
            if balance.get_available_balance() < value:
                raise serializers.ValidationError("余额不足")
        except UserBalance.DoesNotExist:
            raise serializers.ValidationError("用户余额信息不存在")
        
        # 检查VIP等级提款限制
        vip_info = user.get_vip_info()
        if value > vip_info.get('daily_withdraw_limit', 0):
            raise serializers.ValidationError(f"超过每日提款限额 ₦{vip_info['daily_withdraw_limit']}")
        
        return value