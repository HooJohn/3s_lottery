"""
大乐透彩票管理后台
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from .models import SuperLottoGame, SuperLottoDraw, SuperLottoBet, SuperLottoStatistics


@admin.register(SuperLottoGame)
class SuperLottoGameAdmin(admin.ModelAdmin):
    """
    大乐透游戏配置管理
    """
    list_display = [
        'game', 'base_bet_amount', 'profit_target', 'expected_payout_rate',
        'draw_time', 'updated_at'
    ]
    list_filter = ['created_at']
    search_fields = ['game__name']
    readonly_fields = ['created_at', 'updated_at', 'expected_payout_rate']
    
    fieldsets = (
        ('基本配置', {
            'fields': ('game', 'base_bet_amount', 'max_multiplier', 'profit_target')
        }),
        ('号码配置', {
            'fields': (
                ('front_zone_min', 'front_zone_max', 'front_zone_count'),
                ('back_zone_min', 'back_zone_max', 'back_zone_count')
            )
        }),
        ('奖池配置', {
            'fields': ('jackpot_allocation_rate', 'second_prize_allocation_rate')
        }),
        ('固定奖金配置', {
            'fields': (
                ('third_prize_amount', 'fourth_prize_amount', 'fifth_prize_amount'),
                ('sixth_prize_amount', 'seventh_prize_amount'),
                ('eighth_prize_amount', 'ninth_prize_amount')
            )
        }),
        ('开奖配置', {
            'fields': ('draw_days', 'draw_time', 'sales_stop_minutes')
        }),
        ('统计信息', {
            'fields': ('expected_payout_rate', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def expected_payout_rate(self, obj):
        """显示期望派彩率"""
        payout_rate = obj.calculate_expected_payout_rate() * 100
        profit_rate = 100 - payout_rate
        
        color = 'green' if abs(profit_rate - float(obj.profit_target) * 100) < 2 else 'red'
        
        return format_html(
            '<span style="color: {};">派彩率: {:.1f}% (利润率: {:.1f}%)</span>',
            color, payout_rate, profit_rate
        )
    expected_payout_rate.short_description = '期望派彩率'


@admin.register(SuperLottoDraw)
class SuperLottoDrawAdmin(admin.ModelAdmin):
    """
    大乐透开奖期次管理
    """
    list_display = [
        'draw_number', 'draw_time', 'status', 'jackpot_amount',
        'total_sales', 'total_winners_display', 'first_prize_display'
    ]
    list_filter = ['status', 'draw_time', 'game']
    search_fields = ['draw_number']
    readonly_fields = ['created_at', 'updated_at', 'winning_numbers_display', 'total_winners_display']
    
    fieldsets = (
        ('期次信息', {
            'fields': ('game', 'draw_number', 'draw_time', 'sales_end_time', 'status')
        }),
        ('开奖号码', {
            'fields': ('front_numbers', 'back_numbers', 'winning_numbers_display')
        }),
        ('奖池信息', {
            'fields': ('jackpot_amount', 'total_sales')
        }),
        ('一二等奖', {
            'fields': (
                ('first_prize_winners', 'first_prize_amount'),
                ('second_prize_winners', 'second_prize_amount')
            )
        }),
        ('三至九等奖', {
            'fields': (
                ('third_prize_winners', 'fourth_prize_winners', 'fifth_prize_winners'),
                ('sixth_prize_winners', 'seventh_prize_winners'),
                ('eighth_prize_winners', 'ninth_prize_winners')
            )
        }),
        ('统计信息', {
            'fields': ('total_winners_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def winning_numbers_display(self, obj):
        """显示开奖号码"""
        return obj.get_winning_numbers_display()
    winning_numbers_display.short_description = '开奖号码'
    
    def total_winners_display(self, obj):
        """显示总中奖人数"""
        total = obj.calculate_total_winners()
        return format_html('<span style="font-weight: bold; color: red;">{}</span>', total)
    total_winners_display.short_description = '总中奖人数'
    
    def first_prize_display(self, obj):
        """显示一等奖信息"""
        if obj.first_prize_winners > 0:
            return format_html(
                '<span style="color: red;">{} 注 / ₦{:,.2f}</span>',
                obj.first_prize_winners, obj.first_prize_amount
            )
        return '0 注'
    first_prize_display.short_description = '一等奖'


@admin.register(SuperLottoBet)
class SuperLottoBetAdmin(admin.ModelAdmin):
    """
    大乐透投注记录管理
    """
    list_display = [
        'id_short', 'user_phone', 'draw_number', 'bet_type',
        'bet_count', 'total_amount', 'status', 'winning_display', 'created_at'
    ]
    list_filter = ['bet_type', 'status', 'is_winner', 'created_at']
    search_fields = ['user__phone', 'draw__draw_number', 'id']
    readonly_fields = ['created_at', 'updated_at', 'numbers_display']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('id', 'user', 'draw', 'bet_type', 'status')
        }),
        ('投注号码', {
            'fields': ('numbers_display', 'front_numbers', 'back_numbers')
        }),
        ('胆拖号码', {
            'fields': (
                ('front_dan_numbers', 'front_tuo_numbers'),
                ('back_dan_numbers', 'back_tuo_numbers')
            ),
            'classes': ('collapse',)
        }),
        ('投注信息', {
            'fields': ('multiplier', 'bet_count', 'single_amount', 'total_amount')
        }),
        ('中奖信息', {
            'fields': ('is_winner', 'winning_level', 'winning_amount', 'winning_details')
        }),
        ('交易信息', {
            'fields': ('bet_transaction_id', 'win_transaction_id')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def user_phone(self, obj):
        return obj.user.phone
    user_phone.short_description = '用户手机'
    
    def draw_number(self, obj):
        return obj.draw.draw_number
    draw_number.short_description = '期次'
    
    def numbers_display(self, obj):
        """显示投注号码"""
        return obj.get_numbers_display()
    numbers_display.short_description = '投注号码'
    
    def winning_display(self, obj):
        """显示中奖信息"""
        if obj.is_winner:
            return format_html(
                '<span style="color: red; font-weight: bold;">{}等奖 ₦{:,.2f}</span>',
                obj.winning_level, obj.winning_amount
            )
        return '未中奖'
    winning_display.short_description = '中奖情况'


@admin.register(SuperLottoStatistics)
class SuperLottoStatisticsAdmin(admin.ModelAdmin):
    """
    大乐透统计管理
    """
    list_display = [
        'draw_number', 'total_bets', 'total_sales_amount',
        'total_winners', 'total_winning_amount', 'profit_display', 'payout_rate_display'
    ]
    list_filter = ['game', 'draw__draw_time']
    search_fields = ['draw__draw_number']
    readonly_fields = ['created_at', 'updated_at', 'payout_rate_display']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('game', 'draw')
        }),
        ('销售统计', {
            'fields': ('total_bets', 'total_bet_count', 'total_sales_amount')
        }),
        ('中奖统计', {
            'fields': ('total_winners', 'total_winning_amount', 'payout_rate_display')
        }),
        ('各等奖统计', {
            'fields': (
                ('first_prize_bets', 'first_prize_amount'),
                ('second_prize_bets', 'second_prize_amount'),
                ('third_prize_bets', 'third_prize_amount'),
                ('fourth_prize_bets', 'fourth_prize_amount'),
                ('fifth_prize_bets', 'fifth_prize_amount'),
                ('sixth_prize_bets', 'sixth_prize_amount'),
                ('seventh_prize_bets', 'seventh_prize_amount'),
                ('eighth_prize_bets', 'eighth_prize_amount'),
                ('ninth_prize_bets', 'ninth_prize_amount')
            )
        }),
        ('利润统计', {
            'fields': ('profit', 'profit_rate')
        }),
        ('用户统计', {
            'fields': ('unique_players', 'avg_bet_amount')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def draw_number(self, obj):
        return obj.draw.draw_number
    draw_number.short_description = '期次'
    
    def profit_display(self, obj):
        """显示利润"""
        color = 'green' if obj.profit_rate >= 30 else 'orange' if obj.profit_rate >= 25 else 'red'
        return format_html(
            '<span style="color: {};">₦{:,.2f} ({:.1f}%)</span>',
            color, obj.profit, obj.profit_rate
        )
    profit_display.short_description = '利润'
    
    def payout_rate_display(self, obj):
        """显示派彩率"""
        payout_rate = obj.calculate_payout_rate()
        color = 'green' if payout_rate <= 70 else 'orange' if payout_rate <= 75 else 'red'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, payout_rate)
    payout_rate_display.short_description = '派彩率'