"""
系统核心管理后台配置
"""

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import SystemConfig, SystemLog, SecurityEvent, PerformanceMetric
from apps.users.models import User, KYCDocument
from apps.finance.models import Transaction, UserBalance
from apps.rewards.models import VIPLevel, RebateRecord, ReferralRewardRecord
from apps.games.models import Game, Draw, Bet


class LotteryPlatformAdminSite(AdminSite):
    """
    自定义管理后台站点
    """
    site_header = '非洲彩票博彩平台管理后台'
    site_title = '彩票平台管理'
    index_title = '系统管理控制台'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
            path('system-status/', self.admin_view(self.system_status_view), name='system_status'),
            path('user-analytics/', self.admin_view(self.user_analytics_view), name='user_analytics'),
            path('financial-report/', self.admin_view(self.financial_report_view), name='financial_report'),
            path('game-statistics/', self.admin_view(self.game_statistics_view), name='game_statistics'),
            path('risk-control/', self.admin_view(self.risk_control_view), name='risk_control'),
        ]
        return custom_urls + urls
    
    @method_decorator(never_cache)
    def dashboard_view(self, request):
        """
        系统仪表板视图
        """
        # 获取系统概览数据
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        
        # 用户统计
        total_users = User.objects.count()
        new_users_today = User.objects.filter(date_joined__date=today).count()
        active_users_week = User.objects.filter(last_login__date__gte=week_ago).count()
        kyc_pending = KYCDocument.objects.filter(status='PENDING').count()
        
        # 财务统计
        total_balance = UserBalance.objects.aggregate(
            total=Sum('main_balance')
        )['total'] or 0
        
        transactions_today = Transaction.objects.filter(created_at__date=today)
        deposits_today = transactions_today.filter(type='DEPOSIT').aggregate(
            count=Count('id'), amount=Sum('amount')
        )
        withdrawals_today = transactions_today.filter(type='WITHDRAW').aggregate(
            count=Count('id'), amount=Sum('amount')
        )
        
        # 游戏统计
        games_active = Game.objects.filter(is_active=True).count()
        draws_today = Draw.objects.filter(draw_time__date=today).count()
        bets_today = Bet.objects.filter(created_at__date=today).aggregate(
            count=Count('id'), amount=Sum('amount')
        )
        
        # VIP用户分布
        vip_distribution = User.objects.values('vip_level').annotate(
            count=Count('id')
        ).order_by('vip_level')
        
        # 返水统计
        rebate_today = RebateRecord.objects.filter(
            period_date=today, status='PAID'
        ).aggregate(
            count=Count('id'), amount=Sum('rebate_amount')
        )
        
        context = {
            'title': '系统仪表板',
            'user_stats': {
                'total_users': total_users,
                'new_users_today': new_users_today,
                'active_users_week': active_users_week,
                'kyc_pending': kyc_pending,
            },
            'financial_stats': {
                'total_balance': total_balance,
                'deposits_today': deposits_today,
                'withdrawals_today': withdrawals_today,
            },
            'game_stats': {
                'games_active': games_active,
                'draws_today': draws_today,
                'bets_today': bets_today,
            },
            'vip_distribution': list(vip_distribution),
            'rebate_stats': rebate_today,
        }
        
        return render(request, 'admin/dashboard.html', context)
    
    def system_status_view(self, request):
        """
        系统状态监控视图
        """
        # 获取系统性能指标
        latest_metrics = PerformanceMetric.objects.order_by('-created_at')[:10]
        
        # 获取最近的系统日志
        recent_logs = SystemLog.objects.order_by('-created_at')[:50]
        
        # 获取安全事件
        security_events = SecurityEvent.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).order_by('-created_at')
        
        context = {
            'title': '系统状态监控',
            'performance_metrics': latest_metrics,
            'recent_logs': recent_logs,
            'security_events': security_events,
        }
        
        return render(request, 'admin/system_status.html', context)
    
    def user_analytics_view(self, request):
        """
        用户分析视图
        """
        # 用户注册趋势（最近30天）
        thirty_days_ago = timezone.now() - timedelta(days=30)
        registration_trend = User.objects.filter(
            date_joined__gte=thirty_days_ago
        ).extra(
            select={'day': 'date(date_joined)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        # VIP等级分布
        vip_stats = User.objects.values('vip_level').annotate(
            count=Count('id'),
            avg_turnover=Avg('total_turnover')
        ).order_by('vip_level')
        
        # 地区分布
        country_stats = User.objects.values('country').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # KYC状态分布
        kyc_stats = User.objects.values('kyc_status').annotate(
            count=Count('id')
        )
        
        context = {
            'title': '用户分析',
            'registration_trend': list(registration_trend),
            'vip_stats': list(vip_stats),
            'country_stats': list(country_stats),
            'kyc_stats': list(kyc_stats),
        }
        
        return render(request, 'admin/user_analytics.html', context)
    
    def financial_report_view(self, request):
        """
        财务报表视图
        """
        # 获取日期范围
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        # 每日交易统计
        daily_transactions = Transaction.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day', 'type').annotate(
            count=Count('id'),
            amount=Sum('amount')
        ).order_by('day', 'type')
        
        # 用户余额分布
        balance_distribution = UserBalance.objects.aggregate(
            total_main=Sum('main_balance'),
            total_bonus=Sum('bonus_balance'),
            total_frozen=Sum('frozen_balance')
        )
        
        # VIP等级收入贡献
        vip_revenue = User.objects.values('vip_level').annotate(
            user_count=Count('id'),
            total_turnover=Sum('total_turnover')
        ).order_by('vip_level')
        
        context = {
            'title': '财务报表',
            'daily_transactions': list(daily_transactions),
            'balance_distribution': balance_distribution,
            'vip_revenue': list(vip_revenue),
        }
        
        return render(request, 'admin/financial_report.html', context)
    
    def game_statistics_view(self, request):
        """
        游戏统计视图
        """
        # 游戏参与度统计
        game_stats = Game.objects.annotate(
            total_bets=Count('draw__bet'),
            total_amount=Sum('draw__bet__amount'),
            total_players=Count('draw__bet__user', distinct=True)
        ).order_by('-total_amount')
        
        # 最近开奖统计
        recent_draws = Draw.objects.select_related('game').annotate(
            bet_count=Count('bet'),
            total_amount=Sum('bet__amount'),
            total_payout=Sum('bet__actual_win')
        ).order_by('-draw_time')[:20]
        
        context = {
            'title': '游戏统计',
            'game_stats': game_stats,
            'recent_draws': recent_draws,
        }
        
        return render(request, 'admin/game_statistics.html', context)
    
    def risk_control_view(self, request):
        """
        风控管理视图
        """
        # 高风险用户
        high_risk_users = User.objects.filter(
            total_turnover__gt=1000000  # 流水超过100万的用户
        ).order_by('-total_turnover')[:20]
        
        # 异常交易
        large_transactions = Transaction.objects.filter(
            amount__gt=50000,  # 金额超过5万的交易
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-amount')
        
        # 待审核KYC
        pending_kyc = KYCDocument.objects.filter(
            status='PENDING'
        ).select_related('user').order_by('-created_at')
        
        # 安全事件
        security_events = SecurityEvent.objects.filter(
            severity__in=['HIGH', 'CRITICAL'],
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-created_at')
        
        context = {
            'title': '风控管理',
            'high_risk_users': high_risk_users,
            'large_transactions': large_transactions,
            'pending_kyc': pending_kyc,
            'security_events': security_events,
        }
        
        return render(request, 'admin/risk_control.html', context)


# 创建自定义管理站点实例
admin_site = LotteryPlatformAdminSite(name='lottery_admin')


@admin.register(SystemConfig, site=admin_site)
class SystemConfigAdmin(admin.ModelAdmin):
    """
    系统配置管理
    """
    list_display = ['key', 'value_display', 'description', 'is_active', 'updated_at']
    list_filter = ['is_active', 'config_type', 'updated_at']
    search_fields = ['key', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('key', 'value', 'config_type', 'description')
        }),
        ('状态', {
            'fields': ('is_active',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def value_display(self, obj):
        """显示配置值"""
        if len(str(obj.value)) > 50:
            return f"{str(obj.value)[:50]}..."
        return str(obj.value)
    value_display.short_description = '配置值'
    
    actions = ['activate_configs', 'deactivate_configs']
    
    def activate_configs(self, request, queryset):
        """激活配置"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {updated} 个配置项')
    activate_configs.short_description = '激活选中的配置'
    
    def deactivate_configs(self, request, queryset):
        """停用配置"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功停用 {updated} 个配置项')
    deactivate_configs.short_description = '停用选中的配置'


@admin.register(SystemLog, site=admin_site)
class SystemLogAdmin(admin.ModelAdmin):
    """
    系统日志管理
    """
    list_display = ['level_display', 'module', 'message_short', 'user', 'ip_address', 'created_at']
    list_filter = ['level', 'module', 'created_at']
    search_fields = ['message', 'user__username', 'ip_address']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('日志信息', {
            'fields': ('level', 'module', 'message')
        }),
        ('用户信息', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('额外数据', {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at',)
        }),
    )
    
    def level_display(self, obj):
        """显示日志级别"""
        colors = {
            'DEBUG': 'gray',
            'INFO': 'blue',
            'WARNING': 'orange',
            'ERROR': 'red',
            'CRITICAL': 'darkred',
        }
        color = colors.get(obj.level, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.level
        )
    level_display.short_description = '级别'
    
    def message_short(self, obj):
        """显示简短消息"""
        if len(obj.message) > 100:
            return f"{obj.message[:100]}..."
        return obj.message
    message_short.short_description = '消息'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SecurityEvent, site=admin_site)
class SecurityEventAdmin(admin.ModelAdmin):
    """
    安全事件管理
    """
    list_display = [
        'event_type', 'severity_display', 'user', 'ip_address',
        'description_short', 'status', 'created_at'
    ]
    list_filter = ['event_type', 'severity', 'status', 'created_at']
    search_fields = ['user__username', 'ip_address', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('事件信息', {
            'fields': ('event_type', 'severity', 'description')
        }),
        ('用户信息', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('处理信息', {
            'fields': ('status', 'handled_by', 'handled_at', 'resolution')
        }),
        ('额外数据', {
            'fields': ('event_data',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def severity_display(self, obj):
        """显示严重程度"""
        colors = {
            'LOW': 'green',
            'MEDIUM': 'orange',
            'HIGH': 'red',
            'CRITICAL': 'darkred',
        }
        color = colors.get(obj.severity, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_display.short_description = '严重程度'
    
    def description_short(self, obj):
        """显示简短描述"""
        if len(obj.description) > 80:
            return f"{obj.description[:80]}..."
        return obj.description
    description_short.short_description = '描述'
    
    actions = ['mark_resolved', 'mark_investigating']
    
    def mark_resolved(self, request, queryset):
        """标记为已解决"""
        updated = queryset.update(
            status='RESOLVED',
            handled_by=request.user,
            handled_at=timezone.now()
        )
        self.message_user(request, f'成功标记 {updated} 个事件为已解决')
    mark_resolved.short_description = '标记为已解决'
    
    def mark_investigating(self, request, queryset):
        """标记为调查中"""
        updated = queryset.update(
            status='INVESTIGATING',
            handled_by=request.user,
            handled_at=timezone.now()
        )
        self.message_user(request, f'成功标记 {updated} 个事件为调查中')
    mark_investigating.short_description = '标记为调查中'


@admin.register(PerformanceMetric, site=admin_site)
class PerformanceMetricAdmin(admin.ModelAdmin):
    """
    性能指标管理
    """
    list_display = [
        'metric_name', 'value_display', 'unit', 'threshold_status',
        'server_name', 'created_at'
    ]
    list_filter = ['metric_name', 'server_name', 'created_at']
    search_fields = ['metric_name', 'server_name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('指标信息', {
            'fields': ('metric_name', 'value', 'unit', 'server_name')
        }),
        ('阈值信息', {
            'fields': ('warning_threshold', 'critical_threshold')
        }),
        ('额外数据', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at',)
        }),
    )
    
    def value_display(self, obj):
        """显示指标值"""
        return f"{obj.value:.2f}"
    value_display.short_description = '值'
    
    def threshold_status(self, obj):
        """显示阈值状态"""
        if obj.critical_threshold and obj.value >= obj.critical_threshold:
            return format_html('<span style="color: red; font-weight: bold;">严重</span>')
        elif obj.warning_threshold and obj.value >= obj.warning_threshold:
            return format_html('<span style="color: orange; font-weight: bold;">警告</span>')
        else:
            return format_html('<span style="color: green;">正常</span>')
    threshold_status.short_description = '状态'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# 注册所有应用的模型到自定义管理站点
from apps.users.admin import *
from apps.finance.admin import *
from apps.rewards.admin import *
from apps.games.lottery11x5.admin import *
from apps.games.superlotto.admin import *
from apps.games.scratch666.admin import *

# 将现有的admin注册到自定义站点
admin_site.register(User, UserAdmin)
admin_site.register(UserProfile, UserProfileAdmin)
admin_site.register(KYCDocument, KYCDocumentAdmin)
admin_site.register(LoginLog, LoginLogAdmin)

admin_site.register(UserBalance, UserBalanceAdmin)
admin_site.register(Transaction, TransactionAdmin)
admin_site.register(BalanceLog, BalanceLogAdmin)
admin_site.register(BankAccount, BankAccountAdmin)
admin_site.register(PaymentMethod, PaymentMethodAdmin)

admin_site.register(VIPLevel, VIPLevelAdmin)
admin_site.register(UserVIPStatus, UserVIPStatusAdmin)
admin_site.register(RebateRecord, RebateRecordAdmin)
admin_site.register(ReferralRelation, ReferralRelationAdmin)
admin_site.register(ReferralReward, ReferralRewardAdmin)
admin_site.register(ReferralRewardRecord, ReferralRewardRecordAdmin)
admin_site.register(UserReferralStats, UserReferralStatsAdmin)
admin_site.register(RewardStatistics, RewardStatisticsAdmin)
admin_site.register(RewardCalculation, RewardCalculationAdmin)

# 游戏相关模型注册
from apps.games.models import Game, Draw, BetType, Bet

@admin.register(Game, site=admin_site)
class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'game_type', 'is_active', 'created_at']
    list_filter = ['game_type', 'is_active']
    search_fields = ['name']

@admin.register(Draw, site=admin_site)
class DrawAdmin(admin.ModelAdmin):
    list_display = ['draw_number', 'game', 'draw_time', 'status']
    list_filter = ['game', 'status', 'draw_time']
    search_fields = ['draw_number']

@admin.register(BetType, site=admin_site)
class BetTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'game', 'odds', 'is_active']
    list_filter = ['game', 'is_active']
    search_fields = ['name']

@admin.register(Bet, site=admin_site)
class BetAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'game', 'draw', 'bet_amount', 'status', 'created_at']
    list_filter = ['game', 'status', 'created_at']
    search_fields = ['user__username', 'draw__draw_number']