"""
财务管理模型
"""

import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction

User = get_user_model()


class UserBalance(models.Model):
    """
    用户余额模型
    支持三种余额类型：主余额、奖金余额、冻结余额
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='balance')
    main_balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="主余额"
    )
    bonus_balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="奖金余额"
    )
    frozen_balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="冻结余额"
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_balances'
    
    def get_total_balance(self):
        """获取总余额（主余额 + 奖金余额）"""
        cache_key = f'user_total_balance_{self.user_id}'
        total = cache.get(cache_key)
        if total is None:
            total = self.main_balance + self.bonus_balance
            cache.set(cache_key, total, 300)  # 缓存5分钟
        return total
    
    def get_available_balance(self):
        """获取可用余额（总余额 - 冻结余额）"""
        return self.get_total_balance() - self.frozen_balance
    
    def freeze_balance(self, amount: Decimal, reason: str = '') -> bool:
        """冻结余额"""
        if amount <= 0:
            return False
        
        available = self.get_available_balance()
        if available < amount:
            return False
        
        with transaction.atomic():
            # 优先从主余额冻结
            if self.main_balance >= amount:
                self.main_balance -= amount
            else:
                # 主余额不足，从奖金余额冻结
                remaining = amount - self.main_balance
                self.main_balance = Decimal('0.00')
                self.bonus_balance -= remaining
            
            self.frozen_balance += amount
            self.save()
            
            # 记录冻结操作
            BalanceLog.objects.create(
                user=self.user,
                type='FREEZE',
                amount=amount,
                balance_after=self.get_total_balance(),
                description=reason or '余额冻结'
            )
            
            self.clear_cache()
            return True
    
    def unfreeze_balance(self, amount: Decimal, to_main: bool = True) -> bool:
        """解冻余额"""
        if amount <= 0 or self.frozen_balance < amount:
            return False
        
        with transaction.atomic():
            self.frozen_balance -= amount
            
            if to_main:
                self.main_balance += amount
            else:
                self.bonus_balance += amount
            
            self.save()
            
            # 记录解冻操作
            BalanceLog.objects.create(
                user=self.user,
                type='UNFREEZE',
                amount=amount,
                balance_after=self.get_total_balance(),
                description='余额解冻'
            )
            
            self.clear_cache()
            return True
    
    def add_balance(self, amount: Decimal, balance_type: str = 'main', 
                   description: str = '') -> bool:
        """增加余额"""
        if amount <= 0:
            return False
        
        with transaction.atomic():
            if balance_type == 'main':
                self.main_balance += amount
            elif balance_type == 'bonus':
                self.bonus_balance += amount
            else:
                return False
            
            self.save()
            
            # 记录余额变动
            BalanceLog.objects.create(
                user=self.user,
                type='ADD',
                amount=amount,
                balance_after=self.get_total_balance(),
                description=description or f'{balance_type}余额增加'
            )
            
            self.clear_cache()
            return True
    
    def deduct_balance(self, amount: Decimal, balance_type: str = 'available', 
                      description: str = '') -> bool:
        """扣除余额"""
        if amount <= 0:
            return False
        
        with transaction.atomic():
            if balance_type == 'main':
                if self.main_balance < amount:
                    return False
                self.main_balance -= amount
            elif balance_type == 'bonus':
                if self.bonus_balance < amount:
                    return False
                self.bonus_balance -= amount
            elif balance_type == 'available':
                # 从可用余额扣除，优先扣除主余额
                available = self.get_available_balance()
                if available < amount:
                    return False
                
                if self.main_balance >= amount:
                    self.main_balance -= amount
                else:
                    remaining = amount - self.main_balance
                    self.main_balance = Decimal('0.00')
                    self.bonus_balance -= remaining
            else:
                return False
            
            self.save()
            
            # 记录余额变动
            BalanceLog.objects.create(
                user=self.user,
                type='DEDUCT',
                amount=amount,
                balance_after=self.get_total_balance(),
                description=description or f'{balance_type}余额扣除'
            )
            
            self.clear_cache()
            return True
    
    def clear_cache(self):
        """清除余额缓存"""
        cache_keys = [
            f'user_total_balance_{self.user_id}',
            f'user_balance_{self.user_id}',
        ]
        cache.delete_many(cache_keys)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.clear_cache()
    
    def __str__(self):
        return f"{self.user.phone} - 总余额: ₦{self.get_total_balance()}"


class Transaction(models.Model):
    """
    交易记录模型
    支持按月分表存储优化查询性能
    """
    TYPE_CHOICES = [
        ('DEPOSIT', '存款'),
        ('WITHDRAW', '提款'),
        ('BET', '投注'),
        ('WIN', '中奖'),
        ('REWARD', '奖励'),
        ('REFUND', '退款'),
        ('ADJUSTMENT', '调整'),
        ('TRANSFER_IN', '转入'),
        ('TRANSFER_OUT', '转出'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', '待处理'),
        ('PROCESSING', '处理中'),
        ('COMPLETED', '已完成'),
        ('FAILED', '失败'),
        ('CANCELLED', '已取消'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions', db_index=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    fee = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    actual_amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="实际到账金额")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    
    # 关联信息
    reference_id = models.CharField(max_length=100, blank=True, help_text="外部参考ID")
    related_transaction = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    
    # 详细信息
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # 处理信息
    processed_at = models.DateTimeField(null=True, blank=True)
    processor = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='processed_transactions'
    )
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 管理器将在模型定义后设置
    
    class Meta:
        db_table = 'transactions'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['type', 'status']),
            models.Index(fields=['reference_id']),
            models.Index(fields=['created_at', 'status']),
        ]
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # 计算实际到账金额
        if not self.actual_amount:
            self.actual_amount = self.amount - self.fee
        
        super().save(*args, **kwargs)
    
    def mark_completed(self, processor=None):
        """标记交易完成"""
        self.status = 'COMPLETED'
        self.processed_at = timezone.now()
        if processor:
            self.processor = processor
        self.save()
    
    def mark_failed(self, reason=''):
        """标记交易失败"""
        self.status = 'FAILED'
        self.processed_at = timezone.now()
        if reason:
            self.metadata['failure_reason'] = reason
        self.save()
    
    def __str__(self):
        return f"{self.user.phone} - {self.get_type_display()} - ₦{self.amount}"


class BalanceLog(models.Model):
    """
    余额变动日志
    """
    TYPE_CHOICES = [
        ('ADD', '增加'),
        ('DEDUCT', '扣除'),
        ('FREEZE', '冻结'),
        ('UNFREEZE', '解冻'),
        ('TRANSFER', '转账'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='balance_logs')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    balance_before = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    transaction = models.ForeignKey(Transaction, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'balance_logs'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['type', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.phone} - {self.get_type_display()} - ₦{self.amount}"


class BankAccount(models.Model):
    """
    用户银行账户
    """
    BANK_CHOICES = [
        ('ACCESS', 'Access Bank'),
        ('GTB', 'Guaranty Trust Bank'),
        ('ZENITH', 'Zenith Bank'),
        ('UBA', 'United Bank for Africa'),
        ('FIRST', 'First Bank of Nigeria'),
        ('FIDELITY', 'Fidelity Bank'),
        ('UNION', 'Union Bank'),
        ('STERLING', 'Sterling Bank'),
        ('STANBIC', 'Stanbic IBTC Bank'),
        ('FCMB', 'First City Monument Bank'),
        ('ECOBANK', 'Ecobank Nigeria'),
        ('DIAMOND', 'Diamond Bank'),
        ('HERITAGE', 'Heritage Bank'),
        ('KEYSTONE', 'Keystone Bank'),
        ('POLARIS', 'Polaris Bank'),
        ('PROVIDUS', 'Providus Bank'),
        ('SUNTRUST', 'SunTrust Bank'),
        ('TITAN', 'Titan Trust Bank'),
        ('UNITY', 'Unity Bank'),
        ('WEMA', 'Wema Bank'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_accounts')
    bank_code = models.CharField(max_length=20, choices=BANK_CHOICES)
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=100, help_text="账户名，必须与注册姓名一致")
    is_verified = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    
    # 验证信息
    verification_data = models.JSONField(default=dict, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bank_accounts'
        unique_together = ['user', 'bank_code', 'account_number']
        indexes = [
            models.Index(fields=['user', 'is_default']),
            models.Index(fields=['account_number', 'bank_code']),
        ]
    
    def save(self, *args, **kwargs):
        # 自动填充账户名为用户注册姓名
        if not self.account_name:
            self.account_name = self.user.full_name
        
        # 如果设置为默认账户，取消其他默认账户
        if self.is_default:
            BankAccount.objects.filter(user=self.user, is_default=True).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.phone} - {self.get_bank_code_display()} - {self.account_number}"


class PaymentMethod(models.Model):
    """
    支付方式配置
    """
    METHOD_TYPES = [
        ('BANK_TRANSFER', '银行转账'),
        ('MOBILE_MONEY', '移动货币'),
        ('PAYMENT_GATEWAY', '支付网关'),
        ('CRYPTO', '加密货币'),
    ]
    
    PROVIDERS = [
        ('PAYSTACK', 'Paystack'),
        ('FLUTTERWAVE', 'Flutterwave'),
        ('OPAY', 'OPay'),
        ('PALMPAY', 'PalmPay'),
        ('MONIEPOINT', 'Moniepoint'),
        ('MANUAL', '手动处理'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    provider = models.CharField(max_length=20, choices=PROVIDERS)
    
    # 配置信息
    config = models.JSONField(default=dict)
    
    # 限制设置
    min_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('100.00'))
    max_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('1000000.00'))
    daily_limit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('5000000.00'))
    
    # 手续费设置
    fee_type = models.CharField(
        max_length=10,
        choices=[('FIXED', '固定'), ('PERCENTAGE', '百分比')],
        default='PERCENTAGE'
    )
    fee_value = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.00'))
    
    # 状态
    is_active = models.BooleanField(default=True)
    is_deposit_enabled = models.BooleanField(default=True)
    is_withdraw_enabled = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_methods'
    
    def calculate_fee(self, amount: Decimal) -> Decimal:
        """计算手续费"""
        if self.fee_type == 'FIXED':
            return self.fee_value
        else:
            return amount * self.fee_value / 100
    
    def __str__(self):
        return f"{self.name} ({self.get_provider_display()})"


# 设置自定义管理器
from .managers import TransactionManager, BalanceLogManager, BankAccountManager, PaymentMethodManager

Transaction.add_to_class('objects', TransactionManager())
BalanceLog.add_to_class('objects', BalanceLogManager())
BankAccount.add_to_class('objects', BankAccountManager())
PaymentMethod.add_to_class('objects', PaymentMethodManager())