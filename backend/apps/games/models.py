from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class Game(models.Model):
    """游戏基础模型"""
    GAME_TYPES = [
        ('lottery11x5', '11选5'),
        ('superlotto', '超级大乐透'),
        ('sports', '体育博彩'),
        ('scratch666', '刮刮乐666'),
    ]
    
    name = models.CharField('游戏名称', max_length=100)
    game_type = models.CharField('游戏类型', max_length=20, choices=GAME_TYPES)
    is_active = models.BooleanField('是否启用', default=True)
    min_bet = models.DecimalField('最小投注金额', max_digits=10, decimal_places=2, default=Decimal('1.00'))
    max_bet = models.DecimalField('最大投注金额', max_digits=10, decimal_places=2, default=Decimal('10000.00'))
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '游戏'
        verbose_name_plural = '游戏'
        
    def __str__(self):
        return self.name


class Draw(models.Model):
    """开奖基础模型"""
    STATUS_CHOICES = [
        ('pending', '待开奖'),
        ('drawing', '开奖中'),
        ('completed', '已开奖'),
        ('cancelled', '已取消'),
    ]
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name='游戏')
    draw_number = models.CharField('期号', max_length=50)
    draw_time = models.DateTimeField('开奖时间')
    result = models.JSONField('开奖结果', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '开奖'
        verbose_name_plural = '开奖'
        unique_together = ['game', 'draw_number']
        
    def __str__(self):
        return f"{self.game.name} - {self.draw_number}"


class BetType(models.Model):
    """投注类型模型"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name='游戏')
    name = models.CharField('投注类型名称', max_length=100)
    code = models.CharField('投注类型代码', max_length=50)
    odds = models.DecimalField('赔率', max_digits=10, decimal_places=2)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '投注类型'
        verbose_name_plural = '投注类型'
        unique_together = ['game', 'code']
        
    def __str__(self):
        return f"{self.game.name} - {self.name}"


class Bet(models.Model):
    """投注基础模型"""
    STATUS_CHOICES = [
        ('pending', '待开奖'),
        ('won', '中奖'),
        ('lost', '未中奖'),
        ('cancelled', '已取消'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name='游戏')
    draw = models.ForeignKey(Draw, on_delete=models.CASCADE, verbose_name='期次')
    bet_content = models.JSONField('投注内容')
    bet_amount = models.DecimalField('投注金额', max_digits=10, decimal_places=2)
    potential_win = models.DecimalField('可能赢取金额', max_digits=10, decimal_places=2)
    actual_win = models.DecimalField('实际赢取金额', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '投注'
        verbose_name_plural = '投注'
        
    def __str__(self):
        return f"{self.user.username} - {self.game.name} - {self.bet_amount}"