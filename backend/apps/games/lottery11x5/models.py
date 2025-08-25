"""
11选5彩票游戏数据模型
"""

import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.games.models import Game, Draw, Bet

User = get_user_model()


class Lottery11x5Game(models.Model):
    """
    11选5游戏配置
    """
    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name='lottery11x5_config')
    
    # 基本配置
    base_bet_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('2.00'),
        help_text="单注基础投注金额"
    )
    
    # 期次配置
    draw_count_per_day = models.IntegerField(default=7, help_text="每日期数")
    draw_interval_minutes = models.IntegerField(default=120, help_text="开奖间隔(分钟)")
    close_before_minutes = models.IntegerField(default=5, help_text="封盘时间(分钟)")
    
    # 开奖时间配置
    first_draw_time = models.TimeField(default='09:00:00', help_text="首期开奖时间")
    last_draw_time = models.TimeField(default='21:00:00', help_text="末期开奖时间")
    
    # 利润目标
    profit_target = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.18'),
        help_text="目标利润率（18%）"
    )
    
    # 自动化配置
    auto_create_draws = models.BooleanField(default=True, help_text="自动创建期次")
    auto_draw = models.BooleanField(default=True, help_text="自动开奖")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lottery11x5_game'
        verbose_name = '11选5游戏配置'
        verbose_name_plural = '11选5游戏配置'
    
    def __str__(self):
        return f"11选5配置 - {self.game.name}"
    
    def get_current_draw(self):
        """获取当前可投注期次"""
        now = timezone.now()
        return Draw.objects.filter(
            game=self.game,
            status='OPEN',
            close_time__gt=now
        ).first()
    
    def get_next_draw_time(self):
        """获取下一期开奖时间"""
        current_draw = self.get_current_draw()
        if current_draw:
            return current_draw.draw_time
        return None
    
    def create_draws_for_date(self, date):
        """为指定日期创建期次"""
        from datetime import datetime, timedelta
        
        draws = []
        current_time = datetime.combine(date, self.first_draw_time)
        end_time = datetime.combine(date, self.last_draw_time)
        
        draw_count = 1
        while current_time <= end_time and draw_count <= self.draw_count_per_day:
            draw_number = f"{date.strftime('%Y%m%d')}-{draw_count:03d}"
            
            # 检查期次是否已存在
            if not Draw.objects.filter(game=self.game, draw_number=draw_number).exists():
                draw = Draw.objects.create(
                    game=self.game,
                    draw_number=draw_number,
                    draw_time=current_time,
                    close_time=current_time - timedelta(minutes=self.close_before_minutes),
                    status='OPEN'
                )
                draws.append(draw)
            
            current_time += timedelta(minutes=self.draw_interval_minutes)
            draw_count += 1
        
        return draws


class Lottery11x5Bet(models.Model):
    """
    11选5投注详情
    """
    bet = models.OneToOneField(Bet, on_delete=models.CASCADE, related_name='lottery11x5_detail')
    
    # 投注方式
    BET_METHOD_CHOICES = [
        ('POSITION', '定位胆'),
        ('ANY', '任选'),
        ('GROUP', '组选'),
    ]
    bet_method = models.CharField(max_length=20, choices=BET_METHOD_CHOICES)
    
    # 位置信息（定位胆专用）
    positions = models.JSONField(default=list, help_text="投注位置 [1,2,3,4,5]")
    
    # 任选信息
    selected_count = models.IntegerField(default=0, help_text="任选数量")
    
    # 复式信息
    is_multiple = models.BooleanField(default=False, help_text="是否复式")
    multiple_count = models.IntegerField(default=1, help_text="复式注数")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lottery11x5_bet'
        verbose_name = '11选5投注详情'
        verbose_name_plural = '11选5投注详情'
    
    def __str__(self):
        return f"{self.bet.user.phone} - {self.get_bet_method_display()}"


class Lottery11x5Result(models.Model):
    """
    11选5开奖结果
    """
    draw = models.OneToOneField(Draw, on_delete=models.CASCADE, related_name='lottery11x5_result')
    
    # 开奖号码
    numbers = models.JSONField(help_text="开奖号码 [1,2,3,4,5]")
    
    # 统计信息
    sum_value = models.IntegerField(help_text="号码总和")
    odd_count = models.IntegerField(help_text="奇数个数")
    even_count = models.IntegerField(help_text="偶数个数")
    big_count = models.IntegerField(help_text="大数个数(>5)")
    small_count = models.IntegerField(help_text="小数个数(<=5)")
    span_value = models.IntegerField(help_text="跨度值")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'lottery11x5_result'
        verbose_name = '11选5开奖结果'
        verbose_name_plural = '11选5开奖结果'
    
    def __str__(self):
        return f"{self.draw.draw_number} - {self.numbers}"


class Lottery11x5Trend(models.Model):
    """
    11选5走势数据
    """
    draw = models.OneToOneField(Draw, on_delete=models.CASCADE, related_name='lottery11x5_trend')
    
    # 位置走势
    position1_number = models.IntegerField(help_text="万位号码")
    position2_number = models.IntegerField(help_text="千位号码")
    position3_number = models.IntegerField(help_text="百位号码")
    position4_number = models.IntegerField(help_text="十位号码")
    position5_number = models.IntegerField(help_text="个位号码")
    
    # 遗漏值
    missing_values = models.JSONField(default=dict, help_text="各号码遗漏值")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'lottery11x5_trend'
        verbose_name = '11选5走势数据'
        verbose_name_plural = '11选5走势数据'
    
    def __str__(self):
        return f"{self.draw.draw_number} 走势"


class Lottery11x5HotCold(models.Model):
    """
    11选5冷热号码统计
    """
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='lottery11x5_hotcold')
    period_type = models.IntegerField(help_text="统计周期 (10/30/50/100)")
    number = models.IntegerField(help_text="号码 (1-11)")
    
    # 统计数据
    frequency = models.IntegerField(default=0, help_text="出现次数")
    last_appearance = models.IntegerField(default=0, help_text="最后出现期数")
    
    # 冷热标识
    is_hot = models.BooleanField(default=False, help_text="是否热号")
    is_cold = models.BooleanField(default=False, help_text="是否冷号")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lottery11x5_hotcold'
        verbose_name = '11选5冷热号码'
        verbose_name_plural = '11选5冷热号码'
        unique_together = ['game', 'period_type', 'number']
        indexes = [
            models.Index(fields=['game', 'period_type']),
            models.Index(fields=['number', 'is_hot']),
            models.Index(fields=['number', 'is_cold']),
        ]
    
    def __str__(self):
        return f"号码{self.number} - {self.period_type}期 - {'热' if self.is_hot else '冷' if self.is_cold else '普通'}"


class Lottery11x5UserNumber(models.Model):
    """
    用户常用号码
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lottery11x5_numbers')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='user_numbers')
    
    # 号码信息
    name = models.CharField(max_length=100, help_text="号码组合名称")
    numbers = models.JSONField(help_text="号码组合")
    bet_method = models.CharField(max_length=20, help_text="投注方式")
    positions = models.JSONField(default=list, help_text="位置信息")
    selected_count = models.IntegerField(default=0, help_text="任选数量")
    
    # 使用统计
    is_favorite = models.BooleanField(default=False, help_text="是否收藏")
    usage_count = models.IntegerField(default=0, help_text="使用次数")
    win_count = models.IntegerField(default=0, help_text="中奖次数")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lottery11x5_user_number'
        verbose_name = '用户常用号码'
        verbose_name_plural = '用户常用号码'
        indexes = [
            models.Index(fields=['user', 'game']),
            models.Index(fields=['is_favorite', 'usage_count']),
        ]
    
    def __str__(self):
        return f"{self.user.phone} - {self.name}"
    
    def get_bet_method_display(self):
        """获取投注方式显示"""
        method_map = {
            'POSITION': '定位胆',
            'ANY': '任选',
            'GROUP': '组选',
        }
        return method_map.get(self.bet_method, self.bet_method)