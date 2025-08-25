"""
体育博彩管理后台
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from .models import (
    SportsProvider, UserSportsWallet, SportsWalletTransaction,
    SportsBetRecord, SportsStatistics, SportsProviderConfig
)


@admin.register(SportsProvider)
class SportsProviderAdmin(admin.ModelAdmin):
    """
    体育博彩平台管理
    """
    list_display = [
        'name', 'code', 'status_display', 'integration_type', 'wallet_mode',
        'tags_display', 'profit_share_rate', 'sort_order', 'updated_at'
    ]
    list_filter = ['is_active', 'is_maintenance', 'is_recommended', 'is_hot', 'integration_type', 'wallet_mode']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code', 'logo', 'banner', 'description')
        }),
        ('功能配置', {
            'fields': ('features', 'supported_sports')
        }),
        ('技术配置', {
            'fields': ('api_endpoint', 'api_key', 'api_secret', 'webhook_url')
        }),
        ('集成配置', {
            'fields': ('integration_type', 'launch_url', 'wallet_mode')
        }),
        ('财务配置', {
            'fields': ('profit_share_rate', 'min_bet_amount', 'max_bet_amount')
        }),
        ('状态控制', {
            'fields': ('is_active', 'is_maintenance', 'is_recommended', 'is_hot', 'sort_order')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_display(self, obj):
        """显示状态"""
        status = obj.get_status_display()
        if status == "正常":
            color = 'green'
        elif status == "维护中":
            color = 'orange'
        else:
            color = 'red'
        
        return format_html('<span style="color: {};">{}</span>', color, status)
    status_display.short_description = '状态'
    
    def tags_display(self, obj):
        """显示标签"""
        tags = obj.get_tags()
        if not tags:
            return '-'
        
        html = ''
        for tag in tags:
            color = 'red' if tag == '推荐' else 'orange'
            html += f'<span style="background-color: {color}; color: white; padding: 2px 6px; border-radius: 3px; margin-right: 4px;">{tag}</span>'
        
        return format_html(html)
    tags_display.short_description = '标签'


@admin.register(UserSportsWallet)
class UserSportsWalletAdmin(admin.ModelAdmin):
    """
    用户体育钱包管理
    """
    list_display = [
        'user_phone', 'provider_name', 'balance', 'platform_user_id',
        'is_active', 'last_sync_at', 'created_at'
    ]
    list_filter = ['provider', 'is_active', 'created_at']
    search_fields = ['user__phone', 'platform_user_id', 'platform_username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'provider', 'is_active')
        }),
        ('平台信息', {
            'fields': ('platform_user_id', 'platform_username')
        }),
        ('余额信息', {
            'fields': ('balance', 'last_sync_at')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_phone(self, obj):
        return obj.user.phone
    user_phone.short_description = '用户手机'
    
    def provider_name(self, obj):
        return obj.provider.name
    provider_name.short_description = '平台名称'


@admin.register(SportsWalletTransaction)
class SportsWalletTransactionAdmin(admin.ModelAdmin):
    """
    体育钱包交易管理
    """
    list_display = [
        'id_short', 'user_phone', 'provider_name', 'transaction_type',
        'amount', 'status', 'created_at'
    ]
    list_filter = ['transaction_type', 'status', 'provider', 'created_at']
    search_fields = ['user__phone', 'platform_transaction_id', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'provider', 'wallet', 'transaction_type', 'status')
        }),
        ('金额信息', {
            'fields': ('amount', 'balance_before', 'balance_after')
        }),
        ('平台信息', {
            'fields': ('platform_transaction_id', 'platform_order_id')
        }),
        ('描述信息', {
            'fields': ('description', 'remark', 'metadata')
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
    
    def provider_name(self, obj):
        return obj.provider.name
    provider_name.short_description = '平台名称'


@admin.register(SportsBetRecord)
class SportsBetRecordAdmin(admin.ModelAdmin):
    """
    体育投注记录管理
    """
    list_display = [
        'id_short', 'user_phone', 'provider_name', 'sport_type',
        'bet_amount', 'actual_win', 'status', 'bet_time'
    ]
    list_filter = ['sport_type', 'status', 'provider', 'bet_time']
    search_fields = ['user__phone', 'platform_bet_id', 'league']
    readonly_fields = ['created_at', 'updated_at', 'profit_loss_display']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'provider', 'platform_bet_id', 'platform_user_id', 'status')
        }),
        ('投注信息', {
            'fields': ('sport_type', 'league', 'match_info', 'bet_type', 'bet_details')
        }),
        ('金额信息', {
            'fields': ('bet_amount', 'potential_win', 'actual_win', 'odds', 'profit_loss_display')
        }),
        ('时间信息', {
            'fields': ('bet_time', 'settle_time', 'match_time')
        }),
        ('系统信息', {
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
    
    def provider_name(self, obj):
        return obj.provider.name
    provider_name.short_description = '平台名称'
    
    def profit_loss_display(self, obj):
        """显示盈亏"""
        profit_loss = obj.get_profit_loss()
        if profit_loss > 0:
            return format_html('<span style="color: green;">+₦{:.2f}</span>', profit_loss)
        elif profit_loss < 0:
            return format_html('<span style="color: red;">₦{:.2f}</span>', profit_loss)
        else:
            return '₦0.00'
    profit_loss_display.short_description = '盈亏'


@admin.register(SportsStatistics)
class SportsStatisticsAdmin(admin.ModelAdmin):
    """
    体育博彩统计管理
    """
    list_display = [
        'provider_name', 'date', 'active_users', 'total_bets',
        'total_bet_amount', 'total_win_amount', 'profit_display', 'payout_rate_display'
    ]
    list_filter = ['provider', 'date']
    search_fields = ['provider__name']
    readonly_fields = ['created_at', 'updated_at', 'payout_rate_display']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('provider', 'date')
        }),
        ('用户统计', {
            'fields': ('active_users', 'new_users')
        }),
        ('投注统计', {
            'fields': ('total_bets', 'total_bet_amount', 'total_win_amount', 'payout_rate_display')
        }),
        ('钱包统计', {
            'fields': ('total_transfer_in', 'total_transfer_out')
        }),
        ('利润统计', {
            'fields': ('gross_profit', 'net_profit', 'profit_rate')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def provider_name(self, obj):
        return obj.provider.name
    provider_name.short_description = '平台名称'
    
    def profit_display(self, obj):
        """显示利润"""
        color = 'green' if obj.profit_rate >= 8 else 'orange' if obj.profit_rate >= 5 else 'red'
        return format_html(
            '<span style="color: {};">₦{:,.2f} ({:.1f}%)</span>',
            color, obj.net_profit, obj.profit_rate
        )
    profit_display.short_description = '净利润'
    
    def payout_rate_display(self, obj):
        """显示派彩率"""
        payout_rate = obj.calculate_payout_rate()
        color = 'green' if payout_rate <= 90 else 'orange' if payout_rate <= 95 else 'red'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, payout_rate)
    payout_rate_display.short_description = '派彩率'


@admin.register(SportsProviderConfig)
class SportsProviderConfigAdmin(admin.ModelAdmin):
    """
    体育平台配置管理
    """
    list_display = [
        'provider_name', 'auto_transfer', 'min_transfer_amount',
        'max_transfer_amount', 'sync_interval', 'last_sync_time'
    ]
    list_filter = ['auto_transfer', 'provider']
    search_fields = ['provider__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('provider',)
        }),
        ('API配置', {
            'fields': ('api_timeout', 'max_retry_times')
        }),
        ('钱包配置', {
            'fields': ('auto_transfer', 'min_transfer_amount', 'max_transfer_amount')
        }),
        ('同步配置', {
            'fields': ('sync_interval', 'last_sync_time')
        }),
        ('风控配置', {
            'fields': ('daily_bet_limit', 'single_bet_limit')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def provider_name(self, obj):
        return obj.provider.name
    provider_name.short_description = '平台名称'