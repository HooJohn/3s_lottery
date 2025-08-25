"""
业务分析和报表服务
"""

from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

from apps.users.models import User, KYCDocument, LoginLog
from apps.finance.models import Transaction, UserBalance
from apps.games.models import Game, Draw, Bet
from apps.rewards.models import VIPLevel, RebateRecord, ReferralRewardRecord
from .models import SystemLog, SecurityEvent, PerformanceMetric


class BusinessAnalytics:
    """
    业务分析服务
    """
    
    @staticmethod
    def get_user_analytics(start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        获取用户分析数据
        """
        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()
        
        # 用户注册趋势
        registration_trend = User.objects.filter(
            date_joined__range=[start_date, end_date]
        ).extra(
            select={'day': 'date(date_joined)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        # 用户活跃度
        active_users = User.objects.filter(
            last_login__range=[start_date, end_date]
        ).count()
        
        # VIP用户分布
        vip_distribution = User.objects.values('vip_level').annotate(
            count=Count('id'),
            avg_turnover=Avg('total_turnover'),
            total_turnover=Sum('total_turnover')
        ).order_by('vip_level')
        
        # 地区分布
        country_distribution = User.objects.values('country').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # KYC状态分布
        kyc_distribution = User.objects.values('kyc_status').annotate(
            count=Count('id')
        )
        
        # 用户留存率（7天、30天）
        retention_7d = BusinessAnalytics._calculate_retention_rate(7)
        retention_30d = BusinessAnalytics._calculate_retention_rate(30)
        
        return {
            'registration_trend': list(registration_trend),
            'active_users': active_users,
            'vip_distribution': list(vip_distribution),
            'country_distribution': list(country_distribution),
            'kyc_distribution': list(kyc_distribution),
            'retention_rates': {
                '7_days': retention_7d,
                '30_days': retention_30d
            }
        }
    
    @staticmethod
    def get_financial_analytics(start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        获取财务分析数据
        """
        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()
        
        # 交易统计
        transactions = Transaction.objects.filter(
            created_at__range=[start_date, end_date]
        )
        
        # 按类型统计交易
        transaction_by_type = transactions.values('type').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('type')
        
        # 每日交易趋势
        daily_transactions = transactions.extra(
            select={'day': 'date(created_at)'}
        ).values('day', 'type').annotate(
            count=Count('id'),
            amount=Sum('amount')
        ).order_by('day', 'type')
        
        # 用户余额分布
        balance_stats = UserBalance.objects.aggregate(
            total_main=Sum('main_balance'),
            total_bonus=Sum('bonus_balance'),
            total_frozen=Sum('frozen_balance'),
            avg_balance=Avg(F('main_balance') + F('bonus_balance'))
        )
        
        # 大额交易统计
        large_transactions = transactions.filter(
            amount__gte=50000
        ).values('type').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        
        # 提款成功率
        withdrawal_stats = transactions.filter(type='WITHDRAW').aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='COMPLETED')),
            failed=Count('id', filter=Q(status='FAILED')),
            pending=Count('id', filter=Q(status='PENDING'))
        )
        
        withdrawal_success_rate = 0
        if withdrawal_stats['total'] > 0:
            withdrawal_success_rate = withdrawal_stats['completed'] / withdrawal_stats['total'] * 100
        
        return {
            'transaction_by_type': list(transaction_by_type),
            'daily_transactions': list(daily_transactions),
            'balance_stats': balance_stats,
            'large_transactions': list(large_transactions),
            'withdrawal_stats': withdrawal_stats,
            'withdrawal_success_rate': withdrawal_success_rate
        }
    
    @staticmethod
    def get_game_analytics(start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        获取游戏分析数据
        """
        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()
        
        # 游戏参与度统计
        bets = Bet.objects.filter(
            created_at__range=[start_date, end_date]
        )
        
        # 按游戏统计
        game_stats = bets.values('draw__game__name').annotate(
            bet_count=Count('id'),
            total_amount=Sum('amount'),
            total_payout=Sum('actual_win'),
            unique_players=Count('user', distinct=True),
            avg_bet=Avg('amount')
        ).order_by('-total_amount')
        
        # 每日游戏活动
        daily_game_activity = bets.extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            bet_count=Count('id'),
            total_amount=Sum('amount'),
            unique_players=Count('user', distinct=True)
        ).order_by('day')
        
        # 游戏利润率
        game_profit_rates = []
        for stat in game_stats:
            if stat['total_amount'] and stat['total_amount'] > 0:
                profit = stat['total_amount'] - (stat['total_payout'] or 0)
                profit_rate = profit / stat['total_amount'] * 100
                game_profit_rates.append({
                    'game': stat['draw__game__name'],
                    'profit': profit,
                    'profit_rate': profit_rate
                })
        
        # 热门投注时段
        hourly_activity = bets.extra(
            select={'hour': 'extract(hour from created_at)'}
        ).values('hour').annotate(
            bet_count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('hour')
        
        return {
            'game_stats': list(game_stats),
            'daily_game_activity': list(daily_game_activity),
            'game_profit_rates': game_profit_rates,
            'hourly_activity': list(hourly_activity)
        }
    
    @staticmethod
    def get_reward_analytics(start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        获取奖励系统分析数据
        """
        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()
        
        # 返水统计
        rebate_stats = RebateRecord.objects.filter(
            period_date__range=[start_date.date(), end_date.date()]
        ).aggregate(
            total_users=Count('user', distinct=True),
            total_amount=Sum('rebate_amount'),
            avg_amount=Avg('rebate_amount')
        )
        
        # 按VIP等级统计返水
        rebate_by_vip = RebateRecord.objects.filter(
            period_date__range=[start_date.date(), end_date.date()]
        ).values('vip_level').annotate(
            user_count=Count('user', distinct=True),
            total_amount=Sum('rebate_amount'),
            avg_amount=Avg('rebate_amount')
        ).order_by('vip_level')
        
        # 推荐奖励统计
        referral_stats = ReferralRewardRecord.objects.filter(
            period_date__range=[start_date.date(), end_date.date()]
        ).aggregate(
            total_referrers=Count('referrer', distinct=True),
            total_amount=Sum('reward_amount'),
            avg_amount=Avg('reward_amount')
        )
        
        # 按推荐级别统计
        referral_by_level = ReferralRewardRecord.objects.filter(
            period_date__range=[start_date.date(), end_date.date()]
        ).values('referral_level').annotate(
            referrer_count=Count('referrer', distinct=True),
            total_amount=Sum('reward_amount'),
            avg_amount=Avg('reward_amount')
        ).order_by('referral_level')
        
        # VIP升级统计
        vip_upgrades = User.objects.filter(
            updated_at__range=[start_date, end_date],
            vip_level__gt=0
        ).values('vip_level').annotate(
            count=Count('id')
        ).order_by('vip_level')
        
        return {
            'rebate_stats': rebate_stats,
            'rebate_by_vip': list(rebate_by_vip),
            'referral_stats': referral_stats,
            'referral_by_level': list(referral_by_level),
            'vip_upgrades': list(vip_upgrades)
        }
    
    @staticmethod
    def get_system_analytics(start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        获取系统分析数据
        """
        if not start_date:
            start_date = timezone.now() - timedelta(days=7)
        if not end_date:
            end_date = timezone.now()
        
        # 系统日志统计
        log_stats = SystemLog.objects.filter(
            created_at__range=[start_date, end_date]
        ).values('level').annotate(
            count=Count('id')
        ).order_by('level')
        
        # 安全事件统计
        security_stats = SecurityEvent.objects.filter(
            created_at__range=[start_date, end_date]
        ).values('event_type', 'severity').annotate(
            count=Count('id')
        ).order_by('event_type', 'severity')
        
        # 性能指标统计
        performance_stats = PerformanceMetric.objects.filter(
            created_at__range=[start_date, end_date]
        ).values('metric_name').annotate(
            avg_value=Avg('value'),
            max_value=Count('value'),
            min_value=Count('value'),
            count=Count('id')
        ).order_by('metric_name')
        
        # 错误率统计
        error_logs = SystemLog.objects.filter(
            created_at__range=[start_date, end_date],
            level__in=['ERROR', 'CRITICAL']
        ).count()
        
        total_logs = SystemLog.objects.filter(
            created_at__range=[start_date, end_date]
        ).count()
        
        error_rate = 0
        if total_logs > 0:
            error_rate = error_logs / total_logs * 100
        
        return {
            'log_stats': list(log_stats),
            'security_stats': list(security_stats),
            'performance_stats': list(performance_stats),
            'error_rate': error_rate,
            'total_logs': total_logs,
            'error_logs': error_logs
        }
    
    @staticmethod
    def _calculate_retention_rate(days: int) -> float:
        """
        计算用户留存率
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # 在指定天数前注册的用户
        old_users = User.objects.filter(date_joined__lt=cutoff_date)
        old_users_count = old_users.count()
        
        if old_users_count == 0:
            return 0.0
        
        # 在指定天数内有活动的老用户
        active_old_users = old_users.filter(
            last_login__gte=cutoff_date
        ).count()
        
        return active_old_users / old_users_count * 100


class ReportGenerator:
    """
    报表生成器
    """
    
    @staticmethod
    def generate_daily_report(date: datetime = None) -> Dict[str, Any]:
        """
        生成每日报表
        """
        if not date:
            date = timezone.now().date()
        
        start_datetime = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        end_datetime = start_datetime + timedelta(days=1)
        
        # 用户数据
        new_users = User.objects.filter(
            date_joined__range=[start_datetime, end_datetime]
        ).count()
        
        active_users = User.objects.filter(
            last_login__range=[start_datetime, end_datetime]
        ).count()
        
        # 财务数据
        deposits = Transaction.objects.filter(
            type='DEPOSIT',
            created_at__range=[start_datetime, end_datetime],
            status='COMPLETED'
        ).aggregate(
            count=Count('id'),
            amount=Sum('amount')
        )
        
        withdrawals = Transaction.objects.filter(
            type='WITHDRAW',
            created_at__range=[start_datetime, end_datetime],
            status='COMPLETED'
        ).aggregate(
            count=Count('id'),
            amount=Sum('amount')
        )
        
        # 游戏数据
        bets = Bet.objects.filter(
            created_at__range=[start_datetime, end_datetime]
        ).aggregate(
            count=Count('id'),
            amount=Sum('amount'),
            payout=Sum('actual_win')
        )
        
        # 奖励数据
        rebates = RebateRecord.objects.filter(
            period_date=date,
            status='PAID'
        ).aggregate(
            count=Count('id'),
            amount=Sum('rebate_amount')
        )
        
        # 系统数据
        system_logs = SystemLog.objects.filter(
            created_at__range=[start_datetime, end_datetime]
        ).values('level').annotate(
            count=Count('id')
        )
        
        security_events = SecurityEvent.objects.filter(
            created_at__range=[start_datetime, end_datetime]
        ).values('severity').annotate(
            count=Count('id')
        )
        
        return {
            'date': date.isoformat(),
            'users': {
                'new_users': new_users,
                'active_users': active_users
            },
            'finance': {
                'deposits': deposits,
                'withdrawals': withdrawals,
                'net_flow': (deposits.get('amount') or 0) - (withdrawals.get('amount') or 0)
            },
            'games': {
                'bets': bets,
                'profit': (bets.get('amount') or 0) - (bets.get('payout') or 0)
            },
            'rewards': {
                'rebates': rebates
            },
            'system': {
                'logs': list(system_logs),
                'security_events': list(security_events)
            }
        }
    
    @staticmethod
    def generate_weekly_report(start_date: datetime = None) -> Dict[str, Any]:
        """
        生成周报
        """
        if not start_date:
            start_date = timezone.now() - timedelta(days=7)
        
        end_date = start_date + timedelta(days=7)
        
        # 获取各类分析数据
        user_analytics = BusinessAnalytics.get_user_analytics(start_date, end_date)
        financial_analytics = BusinessAnalytics.get_financial_analytics(start_date, end_date)
        game_analytics = BusinessAnalytics.get_game_analytics(start_date, end_date)
        reward_analytics = BusinessAnalytics.get_reward_analytics(start_date, end_date)
        system_analytics = BusinessAnalytics.get_system_analytics(start_date, end_date)
        
        return {
            'period': {
                'start_date': start_date.date().isoformat(),
                'end_date': end_date.date().isoformat(),
                'type': 'weekly'
            },
            'users': user_analytics,
            'finance': financial_analytics,
            'games': game_analytics,
            'rewards': reward_analytics,
            'system': system_analytics
        }
    
    @staticmethod
    def generate_monthly_report(year: int = None, month: int = None) -> Dict[str, Any]:
        """
        生成月报
        """
        if not year or not month:
            now = timezone.now()
            year = now.year
            month = now.month
        
        start_date = timezone.make_aware(datetime(year, month, 1))
        if month == 12:
            end_date = timezone.make_aware(datetime(year + 1, 1, 1))
        else:
            end_date = timezone.make_aware(datetime(year, month + 1, 1))
        
        # 获取各类分析数据
        user_analytics = BusinessAnalytics.get_user_analytics(start_date, end_date)
        financial_analytics = BusinessAnalytics.get_financial_analytics(start_date, end_date)
        game_analytics = BusinessAnalytics.get_game_analytics(start_date, end_date)
        reward_analytics = BusinessAnalytics.get_reward_analytics(start_date, end_date)
        system_analytics = BusinessAnalytics.get_system_analytics(start_date, end_date)
        
        return {
            'period': {
                'year': year,
                'month': month,
                'start_date': start_date.date().isoformat(),
                'end_date': end_date.date().isoformat(),
                'type': 'monthly'
            },
            'users': user_analytics,
            'finance': financial_analytics,
            'games': game_analytics,
            'rewards': reward_analytics,
            'system': system_analytics
        }
    
    @staticmethod
    def export_report_to_json(report_data: Dict[str, Any], filename: str = None) -> str:
        """
        导出报表为JSON文件
        """
        if not filename:
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f'report_{timestamp}.json'
        
        import os
        from django.conf import settings
        
        # 确保报表目录存在
        reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        filepath = os.path.join(reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
        
        return filepath