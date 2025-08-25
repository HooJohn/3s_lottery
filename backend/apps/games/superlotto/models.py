"""
大乐透彩票数据模型
"""

import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.games.models import Game

User = get_user_model()


class SuperLottoGame(models.Model):
    """
    大乐透游戏配置
    """
    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name='superlotto_config')
    
    # 基本配置
    base_bet_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('2.00'),
        help_text="单注基础投注金额"
    )
    max_multiplier = models.IntegerField(default=99, help_text="最大倍数")
    
    # 号码配置
    front_zone_min = models.IntegerField(default=1, help_text="前区最小号码")
    front_zone_max = models.IntegerField(default=35, help_text="前区最大号码")
    front_zone_count = models.IntegerField(default=5, help_text="前区选择数量")
    
    back_zone_min = models.IntegerField(default=1, help_text="后区最小号码")
    back_zone_max = models.IntegerField(default=12, help_text="后区最大号码")
    back_zone_count = models.IntegerField(default=2, help_text="后区选择数量")
    
    # 奖池配置
    jackpot_allocation_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.75'),
        help_text="一等奖奖池分配比例"
    )
    second_prize_allocation_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.18'),
        help_text="二等奖奖池分配比例"
    )
    
    # 固定奖金配置（NGN）
    third_prize_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('10000.00'),
        help_text="三等奖固定奖金"
    )
    fourth_prize_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('3000.00'),
        help_text="四等奖固定奖金"
    )
    fifth_prize_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('300.00'),
        help_text="五等奖固定奖金"
    )
    sixth_prize_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('200.00'),
        help_text="六等奖固定奖金"
    )
    seventh_prize_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('100.00'),
        help_text="七等奖固定奖金"
    )
    eighth_prize_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('15.00'),
        help_text="八等奖固定奖金"
    )
    ninth_prize_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('5.00'),
        help_text="九等奖固定奖金"
    )
    
    # 利润目标
    profit_target = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.35'),
        help_text="目标利润率（35%）"
    )
    
    # 开奖配置
    draw_days = models.CharField(
        max_length=20, default='3,6',
        help_text="开奖日期（周几），用逗号分隔，3=周三，6=周六"
    )
    draw_time = models.TimeField(default='21:30:00', help_text="开奖时间")
    sales_stop_minutes = models.IntegerField(default=30, help_text="开奖前停售分钟数")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'superlotto_game'
        verbose_name = '大乐透游戏配置'
        verbose_name_plural = '大乐透游戏配置'
    
    def __str__(self):
        return f"大乐透配置 - {self.game.name}"
    
    def get_draw_days_list(self):
        """获取开奖日期列表"""
        return [int(day.strip()) for day in self.draw_days.split(',') if day.strip()]
    
    def calculate_expected_payout_rate(self):
        """计算期望派彩率"""
        return 1 - self.profit_target


class SuperLottoDraw(models.Model):
    """
    大乐透开奖期次
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='superlotto_draws')
    
    # 期次信息
    draw_number = models.CharField(max_length=20, unique=True, help_text="期次号码，如25008")
    draw_time = models.DateTimeField(help_text="开奖时间")
    sales_end_time = models.DateTimeField(help_text="停售时间")
    
    # 开奖号码
    front_numbers = models.JSONField(null=True, blank=True, help_text="前区开奖号码")
    back_numbers = models.JSONField(null=True, blank=True, help_text="后区开奖号码")
    
    # 奖池信息
    jackpot_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="奖池金额"
    )
    total_sales = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="总销售额"
    )
    
    # 各等奖信息
    first_prize_winners = models.IntegerField(default=0)
    first_prize_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    second_prize_winners = models.IntegerField(default=0)
    second_prize_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    third_prize_winners = models.IntegerField(default=0)
    fourth_prize_winners = models.IntegerField(default=0)
    fifth_prize_winners = models.IntegerField(default=0)
    sixth_prize_winners = models.IntegerField(default=0)
    seventh_prize_winners = models.IntegerField(default=0)
    eighth_prize_winners = models.IntegerField(default=0)
    ninth_prize_winners = models.IntegerField(default=0)
    
    # 状态
    STATUS_CHOICES = [
        ('OPEN', '销售中'),
        ('CLOSED', '已停售'),
        ('DRAWN', '已开奖'),
        ('SETTLED', '已派奖'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'superlotto_draw'
        verbose_name = '大乐透开奖期次'
        verbose_name_plural = '大乐透开奖期次'
        ordering = ['-draw_number']
        indexes = [
            models.Index(fields=['draw_number']),
            models.Index(fields=['status', 'draw_time']),
            models.Index(fields=['game', 'status']),
        ]
    
    def __str__(self):
        return f"大乐透 {self.draw_number}期"
    
    def is_sales_open(self):
        """检查是否在销售期内"""
        now = timezone.now()
        return self.status == 'OPEN' and now < self.sales_end_time
    
    def get_winning_numbers_display(self):
        """获取开奖号码显示格式"""
        if not self.front_numbers or not self.back_numbers:
            return "未开奖"
        
        front_str = ' '.join([f"{num:02d}" for num in sorted(self.front_numbers)])
        back_str = ' '.join([f"{num:02d}" for num in sorted(self.back_numbers)])
        return f"前区: {front_str} | 后区: {back_str}"
    
    def calculate_total_winners(self):
        """计算总中奖人数"""
        return (
            self.first_prize_winners + self.second_prize_winners + 
            self.third_prize_winners + self.fourth_prize_winners +
            self.fifth_prize_winners + self.sixth_prize_winners +
            self.seventh_prize_winners + self.eighth_prize_winners +
            self.ninth_prize_winners
        )


class SuperLottoBet(models.Model):
    """
    大乐透投注记录
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='superlotto_bets')
    draw = models.ForeignKey(SuperLottoDraw, on_delete=models.CASCADE, related_name='bets')
    
    # 投注信息
    BET_TYPE_CHOICES = [
        ('SINGLE', '单式'),
        ('MULTIPLE', '复式'),
        ('SYSTEM', '胆拖'),
    ]
    bet_type = models.CharField(max_length=20, choices=BET_TYPE_CHOICES)
    
    # 号码信息
    front_numbers = models.JSONField(help_text="前区选择号码")
    back_numbers = models.JSONField(help_text="后区选择号码")
    
    # 胆拖专用字段
    front_dan_numbers = models.JSONField(null=True, blank=True, help_text="前区胆码")
    front_tuo_numbers = models.JSONField(null=True, blank=True, help_text="前区拖码")
    back_dan_numbers = models.JSONField(null=True, blank=True, help_text="后区胆码")
    back_tuo_numbers = models.JSONField(null=True, blank=True, help_text="后区拖码")
    
    # 投注参数
    multiplier = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(99)])
    bet_count = models.IntegerField(default=1, help_text="注数")
    single_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="单注金额")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="总投注金额")
    
    # 中奖信息
    is_winner = models.BooleanField(default=False)
    winning_level = models.IntegerField(null=True, blank=True, help_text="中奖等级")
    winning_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="中奖金额"
    )
    winning_details = models.JSONField(null=True, blank=True, help_text="中奖详情")
    
    # 交易信息
    bet_transaction_id = models.UUIDField(null=True, blank=True, help_text="投注交易ID")
    win_transaction_id = models.UUIDField(null=True, blank=True, help_text="中奖交易ID")
    
    # 状态
    STATUS_CHOICES = [
        ('PENDING', '待开奖'),
        ('WINNING', '已中奖'),
        ('LOSING', '未中奖'),
        ('SETTLED', '已派奖'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'superlotto_bet'
        verbose_name = '大乐透投注记录'
        verbose_name_plural = '大乐透投注记录'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['draw', 'status']),
            models.Index(fields=['status', 'is_winner']),
        ]
    
    def __str__(self):
        return f"{self.user.phone} - {self.draw.draw_number}期 - {self.get_bet_type_display()}"
    
    def get_numbers_display(self):
        """获取号码显示格式"""
        if self.bet_type == 'SYSTEM':
            # 胆拖显示
            front_dan = ' '.join([f"{num:02d}" for num in sorted(self.front_dan_numbers or [])])
            front_tuo = ' '.join([f"{num:02d}" for num in sorted(self.front_tuo_numbers or [])])
            back_dan = ' '.join([f"{num:02d}" for num in sorted(self.back_dan_numbers or [])])
            back_tuo = ' '.join([f"{num:02d}" for num in sorted(self.back_tuo_numbers or [])])
            
            result = f"前区胆码: {front_dan} 拖码: {front_tuo}"
            if back_dan or back_tuo:
                result += f" | 后区胆码: {back_dan} 拖码: {back_tuo}"
            return result
        else:
            # 单式/复式显示
            front_str = ' '.join([f"{num:02d}" for num in sorted(self.front_numbers)])
            back_str = ' '.join([f"{num:02d}" for num in sorted(self.back_numbers)])
            return f"前区: {front_str} | 后区: {back_str}"
    
    def calculate_bet_count(self):
        """计算注数"""
        from math import comb
        
        if self.bet_type == 'SINGLE':
            return 1
        elif self.bet_type == 'MULTIPLE':
            # 复式注数计算
            front_count = len(self.front_numbers)
            back_count = len(self.back_numbers)
            
            front_combinations = comb(front_count, 5) if front_count >= 5 else 0
            back_combinations = comb(back_count, 2) if back_count >= 2 else 0
            
            return front_combinations * back_combinations
        elif self.bet_type == 'SYSTEM':
            # 胆拖注数计算
            front_dan_count = len(self.front_dan_numbers or [])
            front_tuo_count = len(self.front_tuo_numbers or [])
            back_dan_count = len(self.back_dan_numbers or [])
            back_tuo_count = len(self.back_tuo_numbers or [])
            
            # 前区组合数
            if front_dan_count + front_tuo_count >= 5:
                front_need = 5 - front_dan_count
                front_combinations = comb(front_tuo_count, front_need) if front_tuo_count >= front_need else 0
            else:
                front_combinations = 0
            
            # 后区组合数
            if back_dan_count + back_tuo_count >= 2:
                back_need = 2 - back_dan_count
                back_combinations = comb(back_tuo_count, back_need) if back_tuo_count >= back_need else 0
            else:
                back_combinations = 0
            
            return front_combinations * back_combinations
        
        return 0


class SuperLottoStatistics(models.Model):
    """
    大乐透统计数据
    """
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='superlotto_statistics')
    draw = models.ForeignKey(SuperLottoDraw, on_delete=models.CASCADE, related_name='statistics')
    
    # 销售统计
    total_bets = models.IntegerField(default=0, help_text="总投注笔数")
    total_bet_count = models.IntegerField(default=0, help_text="总注数")
    total_sales_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # 中奖统计
    total_winners = models.IntegerField(default=0)
    total_winning_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # 各等奖统计
    first_prize_bets = models.IntegerField(default=0)
    first_prize_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    second_prize_bets = models.IntegerField(default=0)
    second_prize_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    third_prize_bets = models.IntegerField(default=0)
    third_prize_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    fourth_prize_bets = models.IntegerField(default=0)
    fourth_prize_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    fifth_prize_bets = models.IntegerField(default=0)
    fifth_prize_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    sixth_prize_bets = models.IntegerField(default=0)
    sixth_prize_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    seventh_prize_bets = models.IntegerField(default=0)
    seventh_prize_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    eighth_prize_bets = models.IntegerField(default=0)
    eighth_prize_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    ninth_prize_bets = models.IntegerField(default=0)
    ninth_prize_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # 利润统计
    profit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    profit_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # 用户统计
    unique_players = models.IntegerField(default=0)
    avg_bet_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'superlotto_statistics'
        verbose_name = '大乐透统计数据'
        verbose_name_plural = '大乐透统计数据'
        unique_together = ['game', 'draw']
        indexes = [
            models.Index(fields=['game', 'draw']),
        ]
    
    def __str__(self):
        return f"大乐透统计 - {self.draw.draw_number}期"
    
    def calculate_payout_rate(self):
        """计算派彩率"""
        if self.total_sales_amount > 0:
            return float(self.total_winning_amount / self.total_sales_amount * 100)
        return 0.0