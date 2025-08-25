"""
666刮刮乐游戏管理后台
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    Scratch666Game,
    ScratchCard,
    ScratchStatistics,
    UserScratchPreference,
    ScratchCardTemplate
)


@admin.register(Scratch666Game)
class Scratch666GameAdmin(admin.ModelAdmin):
    """
    666刮刮乐游戏配置管理
    """
    list_display = [
        'game', 'card_price', 'base_amount', 'profit_target',
        'expected_payout_rate_display', 'enable_auto_scratch', 'updated_at'
    ]
    list_filter = ['enable_auto_scratch', 'enable_sound', 'enable_music']
    search_fields = ['game__name', 'game__code']
    readonly_fields = ['created_at', 'updated_at', 'expected_payout_rate_display']
    
    fieldsets = (
        ('基本配置', {
            'fields': ('game', 'card_price', 'base_amount', 'profit_target', 'scratch_areas')
        }),
        ('中奖概率配置', {
            'fields': ('win_probability_6', 'win_probability_66', 'win_probability_666')
        }),
        ('奖金倍数配置', {
            'fields': ('multiplier_6', 'multiplier_66', 'multiplier_666')
        }),
        ('功能配置', {
            'fields': ('enable_auto_scratch', 'max_auto_scratch', 'enable_sound', 'enable_music')
        }),
        ('统计信息', {
            'fields': ('expected_payout_rate_display',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def expected_payout_rate_display(self, obj):
        rate = obj.calculate_expected_payout_rate()
        color = 'green' if 0.6 <= rate <= 0.8 else 'orange' if 0.5 <= rate < 0.6 or 0.8 < rate <= 0.9 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2%}</span>',
            color, rate
        )
    expected_payout_rate_display.short_description = '期望派彩率'


@admin.register(ScratchCard)
class ScratchCardAdmin(admin.ModelAdmin):
    """
    刮刮乐卡片管理
    """
    list_display = [
        'card_id_short', 'user_phone', 'card_type', 'price',
        'status_display', 'winnings_display', 'purchased_at'
    ]
    list_filter = ['status', 'is_winner', 'card_type', 'purchased_at']
    search_fields = ['user__phone', 'id']
    readonly_fields = ['id', 'areas', 'win_details', 'purchased_at', 'scratched_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('id', 'user', 'game', 'card_type', 'price', 'status')
        }),
        ('刮奖信息', {
            'fields': ('areas', 'total_winnings', 'is_winner', 'win_details')
        }),
        ('时间信息', {
            'fields': ('purchased_at', 'scratched_at'),
            'classes': ('collapse',)
        }),
        ('交易信息', {
            'fields': ('purchase_transaction_id', 'win_transaction_id'),
            'classes': ('collapse',)
        }),
    )
    
    def card_id_short(self, obj):
        return str(obj.id)[:8]
    card_id_short.short_description = '卡片ID'
    
    def user_phone(self, obj):
        return obj.user.phone
    user_phone.short_description = '用户手机'
    
    def status_display(self, obj):
        status_colors = {
            'ACTIVE': 'orange',
            'SCRATCHED': 'green',
            'EXPIRED': 'gray',
        }
        color = status_colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = '状态'
    
    def winnings_display(self, obj):
        if obj.is_winner:
            return format_html(
                '<span style="color: green; font-weight: bold;">₦{}</span>',
                obj.total_winnings
            )
        else:
            return format_html('<span style="color: gray;">未中奖</span>')
    winnings_display.short_description = '中奖金额'


@admin.register(ScratchStatistics)
class ScratchStatisticsAdmin(admin.ModelAdmin):
    """
    刮刮乐统计管理
    """
    list_display = [
        'date', 'game', 'total_cards_sold', 'total_sales_amount',
        'total_winners', 'win_rate_display', 'profit_display', 'profit_rate'
    ]
    list_filter = ['date', 'game']
    search_fields = ['date']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('game', 'date')
        }),
        ('销售统计', {
            'fields': ('total_cards_sold', 'total_sales_amount', 'unique_players', 'avg_cards_per_player')
        }),
        ('中奖统计', {
            'fields': ('total_winners', 'total_winnings', 'winners_6', 'winnings_6', 
                      'winners_66', 'winnings_66', 'winners_666', 'winnings_666')
        }),
        ('利润统计', {
            'fields': ('profit', 'profit_rate')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def win_rate_display(self, obj):
        if obj.total_cards_sold > 0:
            rate = obj.total_winners / obj.total_cards_sold * 100
            color = 'green' if 10 <= rate <= 30 else 'orange' if 5 <= rate < 10 or 30 < rate <= 40 else 'red'
            return format_html(
                '<span style="color: {};">{:.1f}%</span>',
                color, rate
            )
        return '0%'
    win_rate_display.short_description = '中奖率'
    
    def profit_display(self, obj):
        color = 'green' if obj.profit > 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">₦{}</span>',
            color, obj.profit
        )
    profit_display.short_description = '利润'


@admin.register(UserScratchPreference)
class UserScratchPreferenceAdmin(admin.ModelAdmin):
    """
    用户刮刮乐偏好管理
    """
    list_display = [
        'user_phone', 'total_cards_purchased', 'total_amount_spent',
        'total_winnings', 'win_rate_display', 'roi_display', 'updated_at'
    ]
    list_filter = ['sound_enabled', 'music_enabled', 'auto_scratch_enabled']
    search_fields = ['user__phone']
    readonly_fields = ['created_at', 'updated_at', 'win_rate_display', 'roi_display']
    
    fieldsets = (
        ('用户信息', {
            'fields': ('user',)
        }),
        ('偏好设置', {
            'fields': ('sound_enabled', 'music_enabled', 'auto_scratch_enabled', 
                      'auto_scratch_count', 'auto_scratch_stop_on_win')
        }),
        ('统计信息', {
            'fields': ('total_cards_purchased', 'total_amount_spent', 'total_winnings', 
                      'biggest_win', 'win_rate_display', 'roi_display')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_phone(self, obj):
        return obj.user.phone
    user_phone.short_description = '用户手机'
    
    def win_rate_display(self, obj):
        rate = obj.get_win_rate()
        color = 'green' if rate > 20 else 'orange' if rate > 10 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    win_rate_display.short_description = '中奖率'
    
    def roi_display(self, obj):
        roi = obj.get_roi()
        color = 'green' if roi > 80 else 'orange' if roi > 50 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, roi
        )
    roi_display.short_description = '投资回报率'


@admin.register(ScratchCardTemplate)
class ScratchCardTemplateAdmin(admin.ModelAdmin):
    """
    刮刮乐卡片模板管理
    """
    list_display = ['name', 'game', 'card_type', 'is_active', 'updated_at']
    list_filter = ['is_active', 'card_type', 'game']
    search_fields = ['name', 'card_type']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('game', 'name', 'card_type', 'is_active')
        }),
        ('配置信息', {
            'fields': ('areas_config', 'win_probability_config')
        }),
        ('外观配置', {
            'fields': ('background_image', 'scratch_overlay')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# 自定义管理动作
def update_daily_statistics(modeladmin, request, queryset):
    """更新每日统计动作"""
    from .services import Scratch666Service
    
    success = Scratch666Service.update_daily_statistics()
    
    if success:
        modeladmin.message_user(request, '每日统计更新成功')
    else:
        modeladmin.message_user(request, '每日统计更新失败', level='ERROR')

update_daily_statistics.short_description = "更新每日统计数据"


# 将动作添加到统计管理
ScratchStatisticsAdmin.actions = [update_daily_statistics]