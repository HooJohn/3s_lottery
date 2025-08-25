"""
11选5彩票游戏管理后台
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from apps.games.models import Game, Draw, BetType, Bet
from .models import (
    Lottery11x5Game,
    Lottery11x5Bet,
    Lottery11x5Result,
    Lottery11x5Trend,
    Lottery11x5HotCold,
    Lottery11x5UserNumber
)


@admin.register(Lottery11x5Game)
class Lottery11x5GameAdmin(admin.ModelAdmin):
    """
    11选5游戏配置管理
    """
    list_display = [
        'game', 'draw_count_per_day', 'draw_interval_minutes',
        'auto_create_draws', 'auto_draw', 'profit_target',
        'updated_at'
    ]
    list_filter = ['auto_create_draws', 'auto_draw']
    search_fields = ['game__name', 'game__code']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本配置', {
            'fields': ('game', 'draw_count_per_day', 'first_draw_time', 'draw_interval_minutes', 'close_before_minutes')
        }),
        ('自动化设置', {
            'fields': ('auto_create_draws', 'auto_draw', 'profit_target')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Lottery11x5Bet)
class Lottery11x5BetAdmin(admin.ModelAdmin):
    """
    11选5投注详情管理
    """
    list_display = [
        'bet_id', 'user_phone', 'draw_number', 'bet_method',
        'numbers_display', 'amount', 'multiple_count', 'status', 'created_at'
    ]
    list_filter = ['bet_method', 'is_multiple', 'bet__status', 'created_at']
    search_fields = ['bet__user__phone', 'bet__draw__draw_number']
    readonly_fields = ['bet', 'created_at']
    
    def bet_id(self, obj):
        return str(obj.bet.id)[:8]
    bet_id.short_description = '投注ID'
    
    def user_phone(self, obj):
        return obj.bet.user.phone
    user_phone.short_description = '用户手机'
    
    def draw_number(self, obj):
        return obj.bet.draw.draw_number
    draw_number.short_description = '期号'
    
    def numbers_display(self, obj):
        return str(obj.bet.numbers)
    numbers_display.short_description = '投注号码'
    
    def amount(self, obj):
        return f"₦{obj.bet.amount}"
    amount.short_description = '投注金额'
    
    def status(self, obj):
        status_colors = {
            'PENDING': 'orange',
            'WON': 'green',
            'LOST': 'red',
            'CANCELLED': 'gray',
            'REFUNDED': 'blue',
        }
        color = status_colors.get(obj.bet.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.bet.get_status_display()
        )
    status.short_description = '状态'


@admin.register(Lottery11x5Result)
class Lottery11x5ResultAdmin(admin.ModelAdmin):
    """
    11选5开奖结果管理
    """
    list_display = [
        'draw_number', 'draw_time', 'numbers_display', 'sum_value',
        'odd_even_display', 'big_small_display', 'span_value', 'created_at'
    ]
    list_filter = ['draw__draw_time', 'odd_count', 'big_count']
    search_fields = ['draw__draw_number']
    readonly_fields = ['draw', 'created_at']
    
    def draw_number(self, obj):
        return obj.draw.draw_number
    draw_number.short_description = '期号'
    
    def draw_time(self, obj):
        return obj.draw.draw_time.strftime('%Y-%m-%d %H:%M')
    draw_time.short_description = '开奖时间'
    
    def numbers_display(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: red;">{}</span>',
            ' '.join(f'{num:02d}' for num in obj.numbers)
        )
    numbers_display.short_description = '开奖号码'
    
    def odd_even_display(self, obj):
        return f"{obj.odd_count}奇{obj.even_count}偶"
    odd_even_display.short_description = '奇偶'
    
    def big_small_display(self, obj):
        return f"{obj.big_count}大{obj.small_count}小"
    big_small_display.short_description = '大小'


@admin.register(Lottery11x5Trend)
class Lottery11x5TrendAdmin(admin.ModelAdmin):
    """
    11选5走势管理
    """
    list_display = [
        'draw_number', 'numbers_display', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['draw__draw_number']
    readonly_fields = ['created_at']
    
    def draw_number(self, obj):
        return obj.draw.draw_number
    draw_number.short_description = '期号'
    
    def numbers_display(self, obj):
        numbers = [
            obj.position1_number, obj.position2_number, obj.position3_number,
            obj.position4_number, obj.position5_number
        ]
        return format_html(
            '<span style="font-weight: bold;">{}</span>',
            ' '.join(f'{num:02d}' for num in numbers)
        )
    numbers_display.short_description = '位置号码'


@admin.register(Lottery11x5HotCold)
class Lottery11x5HotColdAdmin(admin.ModelAdmin):
    """
    11选5冷热号码管理
    """
    list_display = [
        'game', 'period_type', 'number', 'frequency',
        'last_appearance', 'status_display', 'updated_at'
    ]
    list_filter = ['period_type', 'is_hot', 'is_cold', 'game']
    search_fields = ['number']
    readonly_fields = ['updated_at']
    
    def status_display(self, obj):
        if obj.is_hot:
            return format_html('<span style="color: red; font-weight: bold;">热号</span>')
        elif obj.is_cold:
            return format_html('<span style="color: blue; font-weight: bold;">冷号</span>')
        else:
            return format_html('<span style="color: gray;">普通</span>')
    status_display.short_description = '状态'


@admin.register(Lottery11x5UserNumber)
class Lottery11x5UserNumberAdmin(admin.ModelAdmin):
    """
    11选5用户常用号码管理
    """
    list_display = [
        'user_phone', 'name', 'numbers_display', 'bet_method',
        'usage_count', 'win_count', 'win_rate', 'is_favorite', 'updated_at'
    ]
    list_filter = ['bet_method', 'is_favorite', 'game']
    search_fields = ['user__phone', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    def user_phone(self, obj):
        return obj.user.phone
    user_phone.short_description = '用户手机'
    
    def numbers_display(self, obj):
        return str(obj.numbers)
    numbers_display.short_description = '号码'
    
    def win_rate(self, obj):
        if obj.usage_count == 0:
            return "0%"
        rate = obj.win_count / obj.usage_count * 100
        color = 'green' if rate > 50 else 'orange' if rate > 20 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    win_rate.short_description = '中奖率'





# 自定义管理动作
def manual_draw_lottery(modeladmin, request, queryset):
    """手动开奖动作"""
    from .services import Lottery11x5Service
    
    success_count = 0
    for draw in queryset:
        if draw.status == 'CLOSED':
            result = Lottery11x5Service.draw_lottery(str(draw.id))
            if result['success']:
                success_count += 1
    
    modeladmin.message_user(
        request,
        f'成功开奖 {success_count} 期'
    )

manual_draw_lottery.short_description = "手动开奖选中的期次"


def close_draws(modeladmin, request, queryset):
    """关闭期次动作"""
    count = 0
    for draw in queryset:
        if draw.status == 'OPEN':
            draw.status = 'CLOSED'
            draw.save()
            count += 1
    
    modeladmin.message_user(
        request,
        f'成功关闭 {count} 期'
    )

close_draws.short_description = "关闭选中的期次"


# 扩展原有的Draw管理
class Lottery11x5DrawAdmin(admin.ModelAdmin):
    """
    11选5期次管理（扩展）
    """
    list_display = [
        'draw_number', 'draw_time', 'close_time', 'status',
        'total_bets', 'total_amount', 'total_payout', 'profit_display'
    ]
    list_filter = ['status', 'draw_time', 'game']
    search_fields = ['draw_number']
    actions = [manual_draw_lottery, close_draws]
    
    def profit_display(self, obj):
        if obj.total_amount > 0:
            profit_rate = obj.profit / obj.total_amount * 100
            color = 'green' if obj.profit > 0 else 'red'
            return format_html(
                '<span style="color: {};">₦{} ({:.1f}%)</span>',
                color, obj.profit, profit_rate
            )
        return "₦0"
    profit_display.short_description = '利润'
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(game__game_type='11选5')


# 注册扩展的Draw管理（如果需要单独管理11选5期次）
# admin.site.register(Draw, Lottery11x5DrawAdmin)