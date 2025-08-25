"""
统一返水奖励系统数据模型
"""

import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class VIPLevel(models.Model):
    """
    VIP等级配置
    """
    level = models.IntegerField(unique=True, help_text="VIP等级 (0-7)")
    name = models.CharField(max_length=50, help_text="等级名称")
    
    # 升级要求
    required_turnover = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="升级所需累计有效流水"
    )
    
    # 返水配置
    rebate_rate = models.DecimalField(
        max_digits=5, decimal_places=4, 
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="统一返水比例 (0.0038-0.0080)"
    )
    
    # 提现权益
    daily_withdraw_limit = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('50000.00'),
        help_text="每日提现限额"
    )
    daily_withdraw_times = models.IntegerField(default=1, help_text="每日提现次数")
    withdraw_fee_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.02'),
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="提现手续费率 (0.02-0.00)"
    )
    
    # 其他权益
    monthly_bonus = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        help_text="月度奖金"
    )
    birthday_bonus = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        help_text="生日奖金"
    )
    
    # 客服权益
    priority_support = models.BooleanField(default=False, help_text="优先客服")
    dedicated_manager = models.BooleanField(default=False, help_text="专属客服经理")
    
    # 活动权益
    exclusive_promotions = models.BooleanField(default=False, help_text="专属活动")
    higher_bonus_rates = models.BooleanField(default=False, help_text="更高奖金倍率")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vip_level'
        verbose_name = 'VIP等级'
        verbose_name_plural = 'VIP等级'
        ordering = ['level']
    
    def __str__(self):
        return f"VIP{self.level} - {self.name}"
    
    def get_rebate_percentage(self):
        """获取返水百分比"""
        return float(self.rebate_rate * 100)
    
    def get_withdraw_fee_percentage(self):
        """获取提现手续费百分比"""
        return float(self.withdraw_fee_rate * 100)


class UserVIPStatus(models.Model):
    """
    用户VIP状态
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vip_status')
    current_level = models.ForeignKey(VIPLevel, on_delete=models.CASCADE, related_name='users')
    
    # 流水统计
    total_turnover = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="累计有效流水"
    )
    monthly_turnover = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="本月有效流水"
    )
    
    # 升级信息
    upgrade_time = models.DateTimeField(null=True, blank=True, help_text="最后升级时间")
    next_level_turnover = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text="下一级所需流水"
    )
    
    # 返水统计
    total_rebate_received = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="累计返水金额"
    )
    monthly_rebate_received = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="本月返水金额"
    )
    
    # 提现统计
    daily_withdraw_used = models.IntegerField(default=0, help_text="今日已用提现次数")
    daily_withdraw_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="今日已提现金额"
    )
    last_withdraw_date = models.DateField(null=True, blank=True, help_text="最后提现日期")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_vip_status'
        verbose_name = '用户VIP状态'
        verbose_name_plural = '用户VIP状态'
    
    def __str__(self):
        return f"{self.user.phone} - VIP{self.current_level.level}"
    
    def get_upgrade_progress(self):
        """获取升级进度百分比"""
        if not self.next_level_turnover or self.next_level_turnover <= 0:
            return 100.0  # 已达到最高等级
        
        progress = (self.total_turnover / self.next_level_turnover) * 100
        return min(float(progress), 100.0)
    
    def get_remaining_turnover_for_upgrade(self):
        """获取升级还需的流水"""
        if not self.next_level_turnover:
            return Decimal('0.00')
        
        remaining = self.next_level_turnover - self.total_turnover
        return max(remaining, Decimal('0.00'))
    
    def can_withdraw_today(self, amount: Decimal):
        """检查今日是否还能提现"""
        today = timezone.now().date()
        
        # 重置每日统计
        if self.last_withdraw_date != today:
            self.daily_withdraw_used = 0
            self.daily_withdraw_amount = Decimal('0.00')
            self.last_withdraw_date = today
            self.save()
        
        # 检查次数限制
        if self.daily_withdraw_used >= self.current_level.daily_withdraw_times:
            return False, "今日提现次数已用完"
        
        # 检查金额限制
        if self.daily_withdraw_amount + amount > self.current_level.daily_withdraw_limit:
            return False, f"超过每日提现限额 ₦{self.current_level.daily_withdraw_limit}"
        
        return True, "可以提现"


class RebateRecord(models.Model):
    """
    返水记录
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rebate_records')
    
    # 返水信息
    period_date = models.DateField(help_text="返水周期日期")
    vip_level = models.IntegerField(help_text="返水时的VIP等级")
    rebate_rate = models.DecimalField(max_digits=5, decimal_places=4, help_text="返水比例")
    
    # 流水信息
    total_turnover = models.DecimalField(max_digits=15, decimal_places=2, help_text="有效流水")
    game_turnover_breakdown = models.JSONField(default=dict, help_text="各游戏流水明细")
    
    # 返水金额
    rebate_amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="返水金额")
    
    # 状态
    STATUS_CHOICES = [
        ('PENDING', '待发放'),
        ('PAID', '已发放'),
        ('CANCELLED', '已取消'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # 发放信息
    paid_at = models.DateTimeField(null=True, blank=True, help_text="发放时间")
    transaction_id = models.UUIDField(null=True, blank=True, help_text="交易ID")
    
    # 备注
    remark = models.TextField(null=True, blank=True, help_text="备注")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rebate_record'
        verbose_name = '返水记录'
        verbose_name_plural = '返水记录'
        ordering = ['-period_date', '-created_at']
        unique_together = ['user', 'period_date']
        indexes = [
            models.Index(fields=['user', 'period_date']),
            models.Index(fields=['status', 'period_date']),
        ]
    
    def __str__(self):
        return f"{self.user.phone} - {self.period_date} - ₦{self.rebate_amount}"


class ReferralRelation(models.Model):
    """
    推荐关系
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_relation')
    
    # 推荐层级 (1-7)
    level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)])
    
    # 推荐码
    referral_code = models.CharField(max_length=20, help_text="使用的推荐码")
    
    # 状态
    is_active = models.BooleanField(default=True, help_text="关系是否有效")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'referral_relation'
        verbose_name = '推荐关系'
        verbose_name_plural = '推荐关系'
        unique_together = ['referrer', 'referee']
        indexes = [
            models.Index(fields=['referrer', 'level']),
            models.Index(fields=['referee']),
            models.Index(fields=['referral_code']),
        ]
    
    def __str__(self):
        return f"{self.referrer.phone} -> {self.referee.phone} (L{self.level})"


class ReferralReward(models.Model):
    """
    推荐奖励配置
    """
    level = models.IntegerField(unique=True, validators=[MinValueValidator(1), MaxValueValidator(7)])
    reward_rate = models.DecimalField(
        max_digits=5, decimal_places=4,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="奖励比例"
    )
    name = models.CharField(max_length=50, help_text="等级名称")
    description = models.TextField(help_text="等级描述")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'referral_reward'
        verbose_name = '推荐奖励配置'
        verbose_name_plural = '推荐奖励配置'
        ordering = ['level']
    
    def __str__(self):
        return f"L{self.level} - {self.name} ({self.get_reward_percentage()}%)"
    
    def get_reward_percentage(self):
        """获取奖励百分比"""
        return float(self.reward_rate * 100)


class ReferralRewardRecord(models.Model):
    """
    推荐奖励记录
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_rewards')
    referee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_rewards')
    
    # 奖励信息
    period_date = models.DateField(help_text="奖励周期日期")
    referral_level = models.IntegerField(help_text="推荐层级")
    reward_rate = models.DecimalField(max_digits=5, decimal_places=4, help_text="奖励比例")
    
    # 流水信息
    referee_turnover = models.DecimalField(max_digits=15, decimal_places=2, help_text="下级有效流水")
    reward_amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="奖励金额")
    
    # 状态
    STATUS_CHOICES = [
        ('PENDING', '待发放'),
        ('PAID', '已发放'),
        ('CANCELLED', '已取消'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # 发放信息
    paid_at = models.DateTimeField(null=True, blank=True, help_text="发放时间")
    transaction_id = models.UUIDField(null=True, blank=True, help_text="交易ID")
    
    # 备注
    remark = models.TextField(null=True, blank=True, help_text="备注")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'referral_reward_record'
        verbose_name = '推荐奖励记录'
        verbose_name_plural = '推荐奖励记录'
        ordering = ['-period_date', '-created_at']
        indexes = [
            models.Index(fields=['referrer', 'period_date']),
            models.Index(fields=['referee', 'period_date']),
            models.Index(fields=['status', 'period_date']),
        ]
    
    def __str__(self):
        return f"{self.referrer.phone} <- {self.referee.phone} (L{self.referral_level}) - ₦{self.reward_amount}"


class UserReferralStats(models.Model):
    """
    用户推荐统计
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='referral_stats')
    
    # 推荐统计
    total_referrals = models.IntegerField(default=0, help_text="总推荐人数")
    active_referrals = models.IntegerField(default=0, help_text="活跃推荐人数")
    
    # 各级推荐人数
    level1_count = models.IntegerField(default=0, help_text="一级推荐人数")
    level2_count = models.IntegerField(default=0, help_text="二级推荐人数")
    level3_count = models.IntegerField(default=0, help_text="三级推荐人数")
    level4_count = models.IntegerField(default=0, help_text="四级推荐人数")
    level5_count = models.IntegerField(default=0, help_text="五级推荐人数")
    level6_count = models.IntegerField(default=0, help_text="六级推荐人数")
    level7_count = models.IntegerField(default=0, help_text="七级推荐人数")
    
    # 奖励统计
    total_reward_earned = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="累计推荐奖励"
    )
    monthly_reward_earned = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="本月推荐奖励"
    )
    
    # 团队贡献
    team_total_turnover = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="团队总流水"
    )
    team_monthly_turnover = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="团队本月流水"
    )
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_referral_stats'
        verbose_name = '用户推荐统计'
        verbose_name_plural = '用户推荐统计'
    
    def __str__(self):
        return f"{self.user.phone} - 推荐{self.total_referrals}人 - ₦{self.total_reward_earned}"
    
    def get_level_counts(self):
        """获取各级推荐人数"""
        return {
            1: self.level1_count,
            2: self.level2_count,
            3: self.level3_count,
            4: self.level4_count,
            5: self.level5_count,
            6: self.level6_count,
            7: self.level7_count,
        }


class RewardCalculation(models.Model):
    """
    奖励计算记录 - 记录个人返水金额、推荐奖励金额和总奖励
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reward_calculations')
    
    # 计算周期
    period_date = models.DateField(help_text="计算周期日期")
    period_type = models.CharField(
        max_length=20, 
        choices=[('DAILY', '每日'), ('WEEKLY', '每周'), ('MONTHLY', '每月')],
        default='DAILY',
        help_text="计算周期类型"
    )
    
    # 用户信息
    vip_level = models.IntegerField(help_text="计算时的VIP等级")
    total_turnover = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="周期内总有效流水"
    )
    
    # 返水奖励
    rebate_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.00'),
        help_text="返水比例"
    )
    rebate_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="个人返水金额"
    )
    
    # 推荐奖励
    referral_reward_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="推荐奖励金额"
    )
    referral_reward_breakdown = models.JSONField(
        default=dict, 
        help_text="推荐奖励明细 {level: amount}"
    )
    
    # 其他奖励
    bonus_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="其他奖金(生日奖金、月度奖金等)"
    )
    
    # 总奖励
    total_reward_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="总奖励金额"
    )
    
    # 发放状态
    STATUS_CHOICES = [
        ('CALCULATED', '已计算'),
        ('PAID', '已发放'),
        ('CANCELLED', '已取消'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CALCULATED')
    
    # 发放信息
    paid_at = models.DateTimeField(null=True, blank=True, help_text="发放时间")
    transaction_ids = models.JSONField(default=list, help_text="相关交易ID列表")
    
    # 备注
    remark = models.TextField(null=True, blank=True, help_text="备注")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reward_calculation'
        verbose_name = '奖励计算记录'
        verbose_name_plural = '奖励计算记录'
        ordering = ['-period_date', '-created_at']
        unique_together = ['user', 'period_date', 'period_type']
        indexes = [
            models.Index(fields=['user', 'period_date']),
            models.Index(fields=['status', 'period_date']),
            models.Index(fields=['period_type', 'period_date']),
        ]
    
    def __str__(self):
        return f"{self.user.phone} - {self.period_date} - ₦{self.total_reward_amount}"
    
    def save(self, *args, **kwargs):
        """保存时自动计算总奖励金额"""
        self.total_reward_amount = self.rebate_amount + self.referral_reward_amount + self.bonus_amount
        super().save(*args, **kwargs)
    
    def get_reward_breakdown(self):
        """获取奖励明细"""
        return {
            'rebate': {
                'amount': float(self.rebate_amount),
                'rate': float(self.rebate_rate),
                'percentage': float(self.rebate_rate * 100),
            },
            'referral': {
                'amount': float(self.referral_reward_amount),
                'breakdown': self.referral_reward_breakdown,
            },
            'bonus': {
                'amount': float(self.bonus_amount),
            },
            'total': {
                'amount': float(self.total_reward_amount),
            }
        }


class RewardStatistics(models.Model):
    """
    奖励系统统计
    """
    date = models.DateField(unique=True, help_text="统计日期")
    
    # 返水统计
    total_rebate_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="总返水金额"
    )
    total_rebate_users = models.IntegerField(default=0, help_text="返水用户数")
    
    # 推荐奖励统计
    total_referral_reward = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="总推荐奖励"
    )
    total_referral_users = models.IntegerField(default=0, help_text="获得推荐奖励用户数")
    
    # VIP统计
    vip_distribution = models.JSONField(default=dict, help_text="VIP等级分布")
    
    # 总计
    total_reward_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="总奖励金额"
    )
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reward_statistics'
        verbose_name = '奖励统计'
        verbose_name_plural = '奖励统计'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date} - 总奖励₦{self.total_reward_amount}"