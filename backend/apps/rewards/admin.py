"""
统一返水奖励系统管理后台
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from .models import (
    VIPLevel, UserVIPStatus, RebateRecord, ReferralRelation,
    ReferralReward, ReferralRewardRecord, UserReferralStats, RewardStatistics,
    RewardCalculation
)


@admin.register(VIPLevel)
class VIPLevelAdmin(admin.ModelAdmin):
    """
    VIP等级管理
    """
    list_display = [
        'level', 'name', 'required_turnover', 'rebate_percentage',
        'withdraw_fee_percentage', 'daily_withdraw_limit', 'monthly_bonus'
    ]
    list_filter = ['priority_support', 'dedicated_manager', 'exclusive_promotions']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('level', 'name', 'required_turnover')
        }),
        ('返水配置', {
            'fields': ('rebate_rate',)
        }),
        ('提现权益', {
            'fields': ('daily_withdraw_limit', 'daily_withdraw_times', 'withdraw_fee_rate')
        }),
        ('奖金权益', {
            'fields': ('monthly_bonus', 'birthday_bonus')
        }),
        ('服务权益', {
            'fields': ('priority_support', 'dedicated_manager')
        }),
        ('活动权益', {
            'fields': ('exclusive_promotions', 'higher_bonus_rates')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rebate_percentage(self, obj):
        """显示返水百分比"""
        return format_html('<span style="color: green;">{:.2f}%</span>', obj.get_rebate_percentage())
    rebate_percentage.short_description = '返水比例'
    
    def withdraw_fee_percentage(self, obj):
        """显示提现手续费百分比"""
        return format_html('<span style="color: blue;">{:.1f}%</span>', obj.get_withdraw_fee_percentage())
    withdraw_fee_percentage.short_description = '提现手续费'


@admin.register(UserVIPStatus)
class UserVIPStatusAdmin(admin.ModelAdmin):
    """
    用户VIP状态管理
    """
    list_display = [
        'user_phone', 'current_vip', 'total_turnover', 'monthly_turnover',
        'upgrade_progress', 'total_rebate_received', 'upgrade_time'
    ]
    list_filter = ['current_level', 'upgrade_time']
    search_fields = ['user__phone', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'upgrade_progress_display']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'current_level', 'upgrade_time')
        }),
        ('流水统计', {
            'fields': ('total_turnover', 'monthly_turnover', 'next_level_turnover', 'upgrade_progress_display')
        }),
        ('返水统计', {
            'fields': ('total_rebate_received', 'monthly_rebate_received')
        }),
        ('提现统计', {
            'fields': ('daily_withdraw_used', 'daily_withdraw_amount', 'last_withdraw_date')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_phone(self, obj):
        return obj.user.phone
    user_phone.short_description = '用户手机'
    
    def current_vip(self, obj):
        """显示当前VIP等级"""
        return format_html(
            '<span style="color: #FF6600; font-weight: bold;">VIP{}</span>',
            obj.current_level.level
        )
    current_vip.short_description = 'VIP等级'
    
    def upgrade_progress(self, obj):
        """显示升级进度"""
        progress = obj.get_upgrade_progress()
        if progress >= 100:
            return format_html(
                '<span style="color: green;">已达最高等级</span>'
            )
        else:
            return format_html(
                '<div style="width:100px; background-color:#f1f1f1; border-radius:3px;">' 
                '<div style="width:{}px; background-color:#4CAF50; height:10px; border-radius:3px;"></div>'
                '</div> {:.1f}%',
                int(progress), progress
            )
    upgrade_progress.short_description = '升级进度'
    
    def upgrade_progress_display(self, obj):
        """详细显示升级进度"""
        progress = obj.get_upgrade_progress()
        remaining = obj.get_remaining_turnover_for_upgrade()
        
        if progress >= 100:
            return format_html('<span style="color: green; font-size: 16px;">已达最高等级</span>')
        else:
            return format_html(
                '<div style="margin-bottom:10px;">' 
                '<div style="width:300px; background-color:#f1f1f1; border-radius:5px;">'
                '<div style="width:{}px; background-color:#4CAF50; height:20px; border-radius:5px;"></div>'
                '</div>'
                '</div>'
                '<div>进度: <b>{:.1f}%</b></div>'
                '<div>当前流水: <b>₦{:,.2f}</b></div>'
                '<div>下级要求: <b>₦{:,.2f}</b></div>'
                '<div>还需流水: <b>₦{:,.2f}</b></div>',
                int(progress * 3), progress, obj.total_turnover, obj.next_level_turnover or 0, remaining
            )
    upgrade_progress_display.short_description = '升级进度详情'


@admin.register(RebateRecord)
class RebateRecordAdmin(admin.ModelAdmin):
    """
    返水记录管理
    """
    list_display = [
        'id_short', 'user_phone', 'period_date', 'vip_level_display',
        'total_turnover', 'rebate_percentage', 'rebate_amount', 'status', 'paid_at'
    ]
    list_filter = ['status', 'period_date', 'vip_level']
    search_fields = ['user__phone', 'id']
    readonly_fields = ['created_at', 'updated_at', 'game_breakdown_display']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'period_date', 'vip_level', 'rebate_rate')
        }),
        ('流水信息', {
            'fields': ('total_turnover', 'game_breakdown_display')
        }),
        ('返水信息', {
            'fields': ('rebate_amount', 'status', 'paid_at', 'transaction_id')
        }),
        ('备注', {
            'fields': ('remark',)
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
    
    def vip_level_display(self, obj):
        """显示VIP等级"""
        return format_html(
            '<span style="color: #FF6600; font-weight: bold;">VIP{}</span>',
            obj.vip_level
        )
    vip_level_display.short_description = 'VIP等级'
    
    def rebate_percentage(self, obj):
        """显示返水百分比"""
        return format_html('<span style="color: green;">{:.2f}%</span>', float(obj.rebate_rate * 100))
    rebate_percentage.short_description = '返水比例'
    
    def game_breakdown_display(self, obj):
        """显示游戏流水明细"""
        if not obj.game_turnover_breakdown:
            return '无明细数据'
        
        html = '<table style="width:100%; border-collapse: collapse;">' \
               '<tr><th style="border:1px solid #ddd; padding:8px;">游戏</th>' \
               '<th style="border:1px solid #ddd; padding:8px;">流水金额</th></tr>'
        
        for game_code, amount in obj.game_turnover_breakdown.items():
            html += f'<tr><td style="border:1px solid #ddd; padding:8px;">{game_code}</td>' \
                   f'<td style="border:1px solid #ddd; padding:8px;">₦{amount:,.2f}</td></tr>'
        
        html += f'<tr><td style="border:1px solid #ddd; padding:8px; font-weight:bold;">总计</td>' \
               f'<td style="border:1px solid #ddd; padding:8px; font-weight:bold;">₦{obj.total_turnover:,.2f}</td></tr>'
        
        html += '</table>'
        return format_html(html)
    game_breakdown_display.short_description = '游戏流水明细'


@admin.register(ReferralRelation)
class ReferralRelationAdmin(admin.ModelAdmin):
    """
    推荐关系管理
    """
    list_display = [
        'referrer_phone', 'referee_phone', 'level', 'referral_code',
        'is_active', 'created_at'
    ]
    list_filter = ['level', 'is_active', 'created_at']
    search_fields = ['referrer__phone', 'referee__phone', 'referral_code']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('推荐关系', {
            'fields': ('referrer', 'referee', 'level')
        }),
        ('推荐信息', {
            'fields': ('referral_code', 'is_active')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def referrer_phone(self, obj):
        return obj.referrer.phone
    referrer_phone.short_description = '推荐人手机'
    
    def referee_phone(self, obj):
        return obj.referee.phone
    referee_phone.short_description = '被推荐人手机'


@admin.register(ReferralReward)
class ReferralRewardAdmin(admin.ModelAdmin):
    """
    推荐奖励配置管理
    """
    list_display = [
        'level', 'name', 'reward_percentage', 'description', 'updated_at'
    ]
    list_filter = ['level']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('level', 'name', 'reward_rate')
        }),
        ('描述', {
            'fields': ('description',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def reward_percentage(self, obj):
        """显示奖励百分比"""
        return format_html('<span style="color: green;">{:.1f}%</span>', obj.get_reward_percentage())
    reward_percentage.short_description = '奖励比例'


@admin.register(ReferralRewardRecord)
class ReferralRewardRecordAdmin(admin.ModelAdmin):
    """
    推荐奖励记录管理
    """
    list_display = [
        'id_short', 'referrer_phone', 'referee_phone', 'period_date',
        'referral_level', 'reward_percentage', 'reward_amount', 'status', 'paid_at'
    ]
    list_filter = ['status', 'period_date', 'referral_level']
    search_fields = ['referrer__phone', 'referee__phone', 'id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('referrer', 'referee', 'period_date', 'referral_level', 'reward_rate')
        }),
        ('流水信息', {
            'fields': ('referee_turnover',)
        }),
        ('奖励信息', {
            'fields': ('reward_amount', 'status', 'paid_at', 'transaction_id')
        }),
        ('备注', {
            'fields': ('remark',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def referrer_phone(self, obj):
        return obj.referrer.phone
    referrer_phone.short_description = '推荐人手机'
    
    def referee_phone(self, obj):
        return obj.referee.phone
    referee_phone.short_description = '被推荐人手机'
    
    def reward_percentage(self, obj):
        """显示奖励百分比"""
        return format_html('<span style="color: green;">{:.1f}%</span>', float(obj.reward_rate * 100))
    reward_percentage.short_description = '奖励比例'


@admin.register(UserReferralStats)
class UserReferralStatsAdmin(admin.ModelAdmin):
    """
    用户推荐统计管理
    """
    list_display = [
        'user_phone', 'total_referrals', 'active_referrals', 'total_reward_earned',
        'monthly_reward_earned', 'team_total_turnover', 'updated_at'
    ]
    list_filter = ['updated_at']
    search_fields = ['user__phone', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'level_breakdown_display']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user',)
        }),
        ('推荐统计', {
            'fields': ('total_referrals', 'active_referrals', 'level_breakdown_display')
        }),
        ('奖励统计', {
            'fields': ('total_reward_earned', 'monthly_reward_earned')
        }),
        ('团队贡献', {
            'fields': ('team_total_turnover', 'team_monthly_turnover')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_phone(self, obj):
        return obj.user.phone
    user_phone.short_description = '用户手机'
    
    def level_breakdown_display(self, obj):
        """显示各级推荐人数明细"""
        level_counts = obj.get_level_counts()
        
        html = '<table style="width:100%; border-collapse: collapse;">' \
               '<tr><th style="border:1px solid #ddd; padding:8px;">级别</th>' \
               '<th style="border:1px solid #ddd; padding:8px;">人数</th></tr>'
        
        for level, count in level_counts.items():
            if count > 0:
                html += f'<tr><td style="border:1px solid #ddd; padding:8px;">L{level}</td>' \
                       f'<td style="border:1px solid #ddd; padding:8px;">{count}人</td></tr>'
        
        html += f'<tr><td style="border:1px solid #ddd; padding:8px; font-weight:bold;">总计</td>' \
               f'<td style="border:1px solid #ddd; padding:8px; font-weight:bold;">{obj.total_referrals}人</td></tr>'
        
        html += '</table>'
        return format_html(html)
    level_breakdown_display.short_description = '各级推荐明细'


@admin.register(RewardStatistics)
class RewardStatisticsAdmin(admin.ModelAdmin):
    """
    奖励统计管理
    """
    list_display = [
        'date', 'total_reward_amount', 'total_rebate_amount', 'total_referral_reward',
        'total_rebate_users', 'total_referral_users', 'updated_at'
    ]
    list_filter = ['date']
    readonly_fields = ['created_at', 'updated_at', 'vip_distribution_display']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('date',)
        }),
        ('返水统计', {
            'fields': ('total_rebate_amount', 'total_rebate_users')
        }),
        ('推荐奖励统计', {
            'fields': ('total_referral_reward', 'total_referral_users')
        }),
        ('总计', {
            'fields': ('total_reward_amount',)
        }),
        ('VIP分布', {
            'fields': ('vip_distribution_display',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def vip_distribution_display(self, obj):
        """显示VIP等级分布"""
        if not obj.vip_distribution:
            return '无数据'
        
        html = '<table style="width:100%; border-collapse: collapse;">' \
               '<tr><th style="border:1px solid #ddd; padding:8px;">VIP等级</th>' \
               '<th style="border:1px solid #ddd; padding:8px;">用户数</th></tr>'
        
        for vip_level, count in obj.vip_distribution.items():
            html += f'<tr><td style="border:1px solid #ddd; padding:8px;">{vip_level}</td>' \
                   f'<td style="border:1px solid #ddd; padding:8px;">{count}人</td></tr>'
        
        html += '</table>'
        return format_html(html)
    vip_distribution_display.short_description = 'VIP等级分布'


@admin.register(RewardCalculation)
class RewardCalculationAdmin(admin.ModelAdmin):
    """
    奖励计算记录管理
    """
    list_display = [
        'id_short', 'user_phone', 'period_date', 'period_type', 'vip_level_display',
        'total_turnover', 'rebate_amount', 'referral_reward_amount', 'total_reward_amount', 'status'
    ]
    list_filter = ['status', 'period_date', 'period_type', 'vip_level']
    search_fields = ['user__phone', 'id']
    readonly_fields = ['created_at', 'updated_at', 'reward_breakdown_display', 'total_reward_amount']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'period_date', 'period_type', 'vip_level')
        }),
        ('流水信息', {
            'fields': ('total_turnover',)
        }),
        ('奖励明细', {
            'fields': ('rebate_rate', 'rebate_amount', 'referral_reward_amount', 'bonus_amount', 'total_reward_amount')
        }),
        ('奖励详情', {
            'fields': ('reward_breakdown_display',)
        }),
        ('发放信息', {
            'fields': ('status', 'paid_at', 'transaction_ids')
        }),
        ('备注', {
            'fields': ('remark',)
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
    
    def vip_level_display(self, obj):
        """显示VIP等级"""
        return format_html(
            '<span style="color: #FF6600; font-weight: bold;">VIP{}</span>',
            obj.vip_level
        )
    vip_level_display.short_description = 'VIP等级'
    
    def reward_breakdown_display(self, obj):
        """显示奖励明细"""
        breakdown = obj.get_reward_breakdown()
        
        html = '<table style="width:100%; border-collapse: collapse;">' \
               '<tr><th style="border:1px solid #ddd; padding:8px;">奖励类型</th>' \
               '<th style="border:1px solid #ddd; padding:8px;">金额</th>' \
               '<th style="border:1px solid #ddd; padding:8px;">比例/明细</th></tr>'
        
        # 返水奖励
        if breakdown['rebate']['amount'] > 0:
            html += f'<tr><td style="border:1px solid #ddd; padding:8px;">返水奖励</td>' \
                   f'<td style="border:1px solid #ddd; padding:8px;">₦{breakdown["rebate"]["amount"]:,.2f}</td>' \
                   f'<td style="border:1px solid #ddd; padding:8px;">{breakdown["rebate"]["percentage"]:.2f}%</td></tr>'
        
        # 推荐奖励
        if breakdown['referral']['amount'] > 0:
            referral_detail = ', '.join([f'{k}: ₦{v:.2f}' for k, v in breakdown['referral']['breakdown'].items()])
            html += f'<tr><td style="border:1px solid #ddd; padding:8px;">推荐奖励</td>' \
                   f'<td style="border:1px solid #ddd; padding:8px;">₦{breakdown["referral"]["amount"]:,.2f}</td>' \
                   f'<td style="border:1px solid #ddd; padding:8px;">{referral_detail}</td></tr>'
        
        # 其他奖金
        if breakdown['bonus']['amount'] > 0:
            html += f'<tr><td style="border:1px solid #ddd; padding:8px;">其他奖金</td>' \
                   f'<td style="border:1px solid #ddd; padding:8px;">₦{breakdown["bonus"]["amount"]:,.2f}</td>' \
                   f'<td style="border:1px solid #ddd; padding:8px;">生日/月度奖金</td></tr>'
        
        # 总计
        html += f'<tr style="background-color:#f9f9f9;"><td style="border:1px solid #ddd; padding:8px; font-weight:bold;">总计</td>' \
               f'<td style="border:1px solid #ddd; padding:8px; font-weight:bold;">₦{breakdown["total"]["amount"]:,.2f}</td>' \
               f'<td style="border:1px solid #ddd; padding:8px; font-weight:bold;">-</td></tr>'
        
        html += '</table>'
        return format_html(html)
    reward_breakdown_display.short_description = '奖励明细'