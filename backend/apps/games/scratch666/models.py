"""
666刮刮乐游戏模型
"""

import uuid
import random
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator

from apps.games.models import Game

User = get_user_model()


class Scratch666Game(models.Model):
    """
    666刮刮乐游戏配置模型
    """
    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name='scratch666_config')
    card_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'))  # 固定价格
    base_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('2.00'))  # 基础金额
    profit_target = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.30'))  # 目标毛利率30%
    
    # 中奖概率配置
    win_probability_6 = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.2000'))  # 单个6的概率20%
    win_probability_66 = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0500'))  # 双6的概率5%
    win_probability_666 = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0100'))  # 三6的概率1%
    
    # 奖金倍数
    multiplier_6 = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.00'))    # 单6 = 基础金额
    multiplier_66 = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('2.00'))   # 双6 = 2倍基础金额
    multiplier_666 = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('3.00'))  # 三6 = 3倍基础金额
    
    # 刮奖区域配置
    scratch_areas = models.IntegerField(default=9)  # 9个刮奖区域
    
    # 自动连刮配置
    enable_auto_scratch = models.BooleanField(default=True)
    max_auto_scratch = models.IntegerField(default=100)  # 最大连刮次数
    
    # 音效配置
    enable_sound = models.BooleanField(default=True)
    enable_music = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scratch666_games'
    
    def __str__(self):
        return f"666刮刮乐配置 - {self.game.name}"
    
    def calculate_expected_payout_rate(self):
        """
        计算期望派彩率
        """
        # 单个区域的期望派彩
        single_area_payout = (
            float(self.win_probability_6) * float(self.multiplier_6) * float(self.base_amount) +
            float(self.win_probability_66) * float(self.multiplier_66) * float(self.base_amount) +
            float(self.win_probability_666) * float(self.multiplier_666) * float(self.base_amount)
        )
        
        # 9个区域的总期望派彩
        total_expected_payout = single_area_payout * self.scratch_areas
        
        # 派彩率 = 期望派彩 / 卡片价格
        payout_rate = total_expected_payout / float(self.card_price)
        
        return round(payout_rate, 4)


class ScratchCard(models.Model):
    """
    刮刮乐卡片模型
    """
    STATUS_CHOICES = [
        ('ACTIVE', '未刮开'),
        ('SCRATCHED', '已刮开'),
        ('EXPIRED', '已过期'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scratch_cards')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='scratch_cards')
    card_type = models.CharField(max_length=20, default='666')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # 刮奖区域数据
    areas = models.JSONField()  # 存储9个区域的内容和状态
    
    # 中奖信息
    total_winnings = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    is_winner = models.BooleanField(default=False)
    win_details = models.JSONField(default=dict, blank=True)
    
    # 状态信息
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    purchased_at = models.DateTimeField(auto_now_add=True)
    scratched_at = models.DateTimeField(null=True, blank=True)
    
    # 交易信息
    purchase_transaction_id = models.UUIDField(null=True, blank=True)
    win_transaction_id = models.UUIDField(null=True, blank=True)
    
    class Meta:
        db_table = 'scratch_cards'
        ordering = ['-purchased_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['game', 'purchased_at']),
            models.Index(fields=['is_winner', 'total_winnings']),
        ]
    
    def __str__(self):
        return f"刮刮乐 {self.card_type} - {self.user.phone} - ₦{self.total_winnings}"
    
    def scratch_area(self, area_index: int):
        """
        刮开指定区域
        """
        if self.status != 'ACTIVE':
            raise ValueError("卡片已刮开或已过期")
        
        if area_index < 0 or area_index >= len(self.areas):
            raise ValueError("无效的区域索引")
        
        # 标记区域为已刮开
        self.areas[area_index]['scratched'] = True
        
        # 检查是否所有区域都已刮开
        if all(area['scratched'] for area in self.areas):
            self.status = 'SCRATCHED'
            self.scratched_at = timezone.now()
            
            # 计算总中奖金额
            self._calculate_winnings()
        
        self.save()
    
    def scratch_all(self):
        """
        刮开所有区域
        """
        if self.status != 'ACTIVE':
            raise ValueError("卡片已刮开或已过期")
        
        # 标记所有区域为已刮开
        for area in self.areas:
            area['scratched'] = True
        
        self.status = 'SCRATCHED'
        self.scratched_at = timezone.now()
        
        # 计算总中奖金额
        self._calculate_winnings()
        
        self.save()
    
    def _calculate_winnings(self):
        """
        计算中奖金额
        """
        from .services import Scratch666Service
        
        total_winnings = Decimal('0.00')
        win_details = []
        
        # 获取游戏配置
        config = self.game.scratch666_config
        
        for i, area in enumerate(self.areas):
            if area['content'] == '6':
                # 单个6
                win_amount = config.base_amount * config.multiplier_6
                total_winnings += win_amount
                win_details.append({
                    'area': i + 1,
                    'content': '6',
                    'amount': float(win_amount)
                })
            elif area['content'] == '66':
                # 双6
                win_amount = config.base_amount * config.multiplier_66
                total_winnings += win_amount
                win_details.append({
                    'area': i + 1,
                    'content': '66',
                    'amount': float(win_amount)
                })
            elif area['content'] == '666':
                # 三6
                win_amount = config.base_amount * config.multiplier_666
                total_winnings += win_amount
                win_details.append({
                    'area': i + 1,
                    'content': '666',
                    'amount': float(win_amount)
                })
        
        self.total_winnings = total_winnings
        self.is_winner = total_winnings > 0
        self.win_details = {
            'areas': win_details,
            'total': float(total_winnings),
            'win_count': len(win_details)
        }
    
    def get_scratch_progress(self):
        """
        获取刮奖进度
        """
        total_areas = len(self.areas)
        scratched_areas = sum(1 for area in self.areas if area['scratched'])
        
        return {
            'total_areas': total_areas,
            'scratched_areas': scratched_areas,
            'progress_percent': round(scratched_areas / total_areas * 100, 1),
            'is_complete': scratched_areas == total_areas
        }


class ScratchCardTemplate(models.Model):
    """
    刮刮乐卡片模板模型
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='scratch_templates')
    name = models.CharField(max_length=100)
    card_type = models.CharField(max_length=20, default='666')
    
    # 模板配置
    areas_config = models.JSONField()  # 区域配置模板
    win_probability_config = models.JSONField()  # 中奖概率配置
    
    # 外观配置
    background_image = models.ImageField(upload_to='scratch/backgrounds/', null=True, blank=True)
    scratch_overlay = models.ImageField(upload_to='scratch/overlays/', null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scratch_card_templates'
    
    def __str__(self):
        return f"刮刮乐模板 - {self.name}"


class ScratchStatistics(models.Model):
    """
    刮刮乐统计模型
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='scratch_statistics')
    date = models.DateField()
    
    # 销售统计
    total_cards_sold = models.IntegerField(default=0)
    total_sales_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # 中奖统计
    total_winners = models.IntegerField(default=0)
    total_winnings = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # 按奖项统计
    winners_6 = models.IntegerField(default=0)      # 单6中奖数
    winnings_6 = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    winners_66 = models.IntegerField(default=0)     # 双6中奖数
    winnings_66 = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    winners_666 = models.IntegerField(default=0)    # 三6中奖数
    winnings_666 = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # 利润统计
    profit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    profit_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # 用户统计
    unique_players = models.IntegerField(default=0)
    avg_cards_per_player = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scratch_statistics'
        unique_together = ['game', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"刮刮乐统计 - {self.date} - 利润₦{self.profit}"
    
    def calculate_payout_rate(self):
        """
        计算派彩率
        """
        if self.total_sales_amount > 0:
            return float(self.total_winnings / self.total_sales_amount * 100)
        return 0.0


class UserScratchPreference(models.Model):
    """
    用户刮刮乐偏好模型
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='scratch_preference')
    
    # 音效偏好
    sound_enabled = models.BooleanField(default=True)
    music_enabled = models.BooleanField(default=True)
    
    # 自动连刮偏好
    auto_scratch_enabled = models.BooleanField(default=False)
    auto_scratch_count = models.IntegerField(default=10)
    auto_scratch_stop_on_win = models.BooleanField(default=True)
    
    # 统计信息
    total_cards_purchased = models.IntegerField(default=0)
    total_amount_spent = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_winnings = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    biggest_win = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_scratch_preferences'
    
    def __str__(self):
        return f"刮刮乐偏好 - {self.user.phone}"
    
    def get_win_rate(self):
        """
        获取中奖率
        """
        if self.total_cards_purchased > 0:
            win_cards = ScratchCard.objects.filter(
                user=self.user,
                is_winner=True
            ).count()
            return round(win_cards / self.total_cards_purchased * 100, 2)
        return 0.0
    
    def get_roi(self):
        """
        获取投资回报率
        """
        if self.total_amount_spent > 0:
            return round(float(self.total_winnings / self.total_amount_spent * 100), 2)
        return 0.0