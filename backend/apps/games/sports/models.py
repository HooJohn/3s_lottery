"""
体育博彩第三方平台集成数据模型
"""

import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.games.models import Game

User = get_user_model()


class SportsProvider(models.Model):
    """
    体育博彩第三方平台提供商
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 基本信息
    name = models.CharField(max_length=100, help_text="平台名称")
    code = models.CharField(max_length=50, unique=True, help_text="平台代码")
    logo = models.ImageField(upload_to='sports/logos/', null=True, blank=True, help_text="平台Logo")
    banner = models.ImageField(upload_to='sports/banners/', null=True, blank=True, help_text="平台横幅")
    
    # 平台描述
    description = models.TextField(help_text="平台简介")
    features = models.JSONField(default=list, help_text="特色功能列表")
    supported_sports = models.JSONField(default=list, help_text="支持的体育项目")
    
    # 技术配置
    api_endpoint = models.URLField(help_text="API接入点")
    api_key = models.CharField(max_length=255, help_text="API密钥")
    api_secret = models.CharField(max_length=255, help_text="API密钥")
    webhook_url = models.URLField(null=True, blank=True, help_text="回调地址")
    
    # 集成配置
    INTEGRATION_TYPES = [
        ('IFRAME', 'iframe嵌入'),
        ('REDIRECT', '跳转集成'),
        ('API', 'API集成'),
    ]
    integration_type = models.CharField(max_length=20, choices=INTEGRATION_TYPES, default='REDIRECT')
    launch_url = models.URLField(help_text="启动URL")
    
    # 钱包配置
    WALLET_MODES = [
        ('SINGLE', '单钱包模式'),
        ('TRANSFER', '转账模式'),
    ]
    wallet_mode = models.CharField(max_length=20, choices=WALLET_MODES, default='TRANSFER')
    
    # 财务配置
    profit_share_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.10'),
        help_text="利润分成比例（10%）"
    )
    min_bet_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('1.00'),
        help_text="最小投注金额"
    )
    max_bet_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('100000.00'),
        help_text="最大投注金额"
    )
    
    # 状态控制
    is_active = models.BooleanField(default=True, help_text="是否启用")
    is_maintenance = models.BooleanField(default=False, help_text="是否维护中")
    is_recommended = models.BooleanField(default=False, help_text="是否推荐")
    is_hot = models.BooleanField(default=False, help_text="是否热门")
    
    # 显示配置
    sort_order = models.IntegerField(default=0, help_text="排序权重")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sports_provider'
        verbose_name = '体育博彩平台'
        verbose_name_plural = '体育博彩平台'
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['is_active', 'sort_order']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_status_display(self):
        """获取状态显示"""
        if not self.is_active:
            return "已停用"
        elif self.is_maintenance:
            return "维护中"
        else:
            return "正常"
    
    def get_tags(self):
        """获取标签列表"""
        tags = []
        if self.is_recommended:
            tags.append("推荐")
        if self.is_hot:
            tags.append("热门")
        return tags


class UserSportsWallet(models.Model):
    """
    用户体育平台钱包
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sports_wallets')
    provider = models.ForeignKey(SportsProvider, on_delete=models.CASCADE, related_name='user_wallets')
    
    # 平台账户信息
    platform_user_id = models.CharField(max_length=100, help_text="平台用户ID")
    platform_username = models.CharField(max_length=100, help_text="平台用户名")
    
    # 钱包余额
    balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="平台钱包余额"
    )
    
    # 状态
    is_active = models.BooleanField(default=True)
    last_sync_at = models.DateTimeField(null=True, blank=True, help_text="最后同步时间")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_sports_wallet'
        verbose_name = '用户体育钱包'
        verbose_name_plural = '用户体育钱包'
        unique_together = ['user', 'provider']
        indexes = [
            models.Index(fields=['user', 'provider']),
            models.Index(fields=['platform_user_id']),
        ]
    
    def __str__(self):
        return f"{self.user.phone} - {self.provider.name}"


class SportsWalletTransaction(models.Model):
    """
    体育钱包转账记录
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sports_transactions')
    provider = models.ForeignKey(SportsProvider, on_delete=models.CASCADE, related_name='transactions')
    wallet = models.ForeignKey(UserSportsWallet, on_delete=models.CASCADE, related_name='transactions')
    
    # 交易信息
    TRANSACTION_TYPES = [
        ('TRANSFER_IN', '转入'),
        ('TRANSFER_OUT', '转出'),
        ('BET', '投注'),
        ('WIN', '中奖'),
        ('REFUND', '退款'),
        ('ADJUSTMENT', '调整'),
    ]
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # 余额信息
    balance_before = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    
    # 平台信息
    platform_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    platform_order_id = models.CharField(max_length=100, null=True, blank=True)
    
    # 状态
    STATUS_CHOICES = [
        ('PENDING', '处理中'),
        ('COMPLETED', '已完成'),
        ('FAILED', '失败'),
        ('CANCELLED', '已取消'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # 描述和备注
    description = models.CharField(max_length=255)
    remark = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, help_text="额外数据")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sports_wallet_transaction'
        verbose_name = '体育钱包交易'
        verbose_name_plural = '体育钱包交易'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['provider', 'transaction_type']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['platform_transaction_id']),
        ]
    
    def __str__(self):
        return f"{self.user.phone} - {self.get_transaction_type_display()} - ₦{self.amount}"


class SportsBetRecord(models.Model):
    """
    体育投注记录
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sports_bets')
    provider = models.ForeignKey(SportsProvider, on_delete=models.CASCADE, related_name='bet_records')
    
    # 平台信息
    platform_bet_id = models.CharField(max_length=100, unique=True)
    platform_user_id = models.CharField(max_length=100)
    
    # 投注信息
    sport_type = models.CharField(max_length=50, help_text="体育项目")
    league = models.CharField(max_length=100, help_text="联赛")
    match_info = models.JSONField(help_text="比赛信息")
    bet_type = models.CharField(max_length=50, help_text="投注类型")
    bet_details = models.JSONField(help_text="投注详情")
    
    # 金额信息
    bet_amount = models.DecimalField(max_digits=15, decimal_places=2)
    potential_win = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    actual_win = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # 赔率信息
    odds = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('1.0000'))
    
    # 状态
    STATUS_CHOICES = [
        ('PENDING', '待结算'),
        ('WON', '已中奖'),
        ('LOST', '未中奖'),
        ('CANCELLED', '已取消'),
        ('REFUNDED', '已退款'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # 时间信息
    bet_time = models.DateTimeField(help_text="投注时间")
    settle_time = models.DateTimeField(null=True, blank=True, help_text="结算时间")
    match_time = models.DateTimeField(null=True, blank=True, help_text="比赛时间")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sports_bet_record'
        verbose_name = '体育投注记录'
        verbose_name_plural = '体育投注记录'
        ordering = ['-bet_time']
        indexes = [
            models.Index(fields=['user', 'bet_time']),
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['platform_bet_id']),
            models.Index(fields=['sport_type', 'bet_time']),
        ]
    
    def __str__(self):
        return f"{self.user.phone} - {self.sport_type} - ₦{self.bet_amount}"
    
    def get_profit_loss(self):
        """计算盈亏"""
        return self.actual_win - self.bet_amount


class SportsStatistics(models.Model):
    """
    体育博彩统计数据
    """
    provider = models.ForeignKey(SportsProvider, on_delete=models.CASCADE, related_name='statistics')
    date = models.DateField(help_text="统计日期")
    
    # 用户统计
    active_users = models.IntegerField(default=0, help_text="活跃用户数")
    new_users = models.IntegerField(default=0, help_text="新用户数")
    
    # 投注统计
    total_bets = models.IntegerField(default=0, help_text="总投注笔数")
    total_bet_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_win_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # 钱包统计
    total_transfer_in = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_transfer_out = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # 利润统计
    gross_profit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    net_profit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    profit_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sports_statistics'
        verbose_name = '体育博彩统计'
        verbose_name_plural = '体育博彩统计'
        unique_together = ['provider', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['provider', 'date']),
        ]
    
    def __str__(self):
        return f"{self.provider.name} - {self.date}"
    
    def calculate_payout_rate(self):
        """计算派彩率"""
        if self.total_bet_amount > 0:
            return float(self.total_win_amount / self.total_bet_amount * 100)
        return 0.0


class SportsProviderConfig(models.Model):
    """
    体育平台配置
    """
    provider = models.OneToOneField(SportsProvider, on_delete=models.CASCADE, related_name='config')
    
    # API配置
    api_timeout = models.IntegerField(default=30, help_text="API超时时间(秒)")
    max_retry_times = models.IntegerField(default=3, help_text="最大重试次数")
    
    # 钱包配置
    auto_transfer = models.BooleanField(default=False, help_text="是否自动转账")
    min_transfer_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('10.00'),
        help_text="最小转账金额"
    )
    max_transfer_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('50000.00'),
        help_text="最大转账金额"
    )
    
    # 同步配置
    sync_interval = models.IntegerField(default=300, help_text="数据同步间隔(秒)")
    last_sync_time = models.DateTimeField(null=True, blank=True)
    
    # 风控配置
    daily_bet_limit = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('100000.00'),
        help_text="每日投注限额"
    )
    single_bet_limit = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('10000.00'),
        help_text="单笔投注限额"
    )
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sports_provider_config'
        verbose_name = '体育平台配置'
        verbose_name_plural = '体育平台配置'
    
    def __str__(self):
        return f"{self.provider.name} 配置"