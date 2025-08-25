"""
生成系统报表管理命令
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from apps.core.analytics import ReportGenerator, BusinessAnalytics
from apps.core.models import SystemLog
import json


class Command(BaseCommand):
    help = '生成系统报表'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['daily', 'weekly', 'monthly'],
            default='daily',
            help='报表类型 (daily/weekly/monthly)',
        )
        parser.add_argument(
            '--date',
            type=str,
            help='指定日期 (YYYY-MM-DD)',
        )
        parser.add_argument(
            '--month',
            type=str,
            help='指定月份 (YYYY-MM)',
        )
        parser.add_argument(
            '--export',
            action='store_true',
            help='导出报表到文件',
        )
        parser.add_argument(
            '--output',
            type=str,
            help='输出文件名',
        )
    
    def handle(self, *args, **options):
        report_type = options['type']
        
        try:
            if report_type == 'daily':
                report_data = self.generate_daily_report(options)
            elif report_type == 'weekly':
                report_data = self.generate_weekly_report(options)
            elif report_type == 'monthly':
                report_data = self.generate_monthly_report(options)
            
            # 输出报表摘要
            self.display_report_summary(report_data, report_type)
            
            # 导出文件（如果指定）
            if options['export']:
                filepath = ReportGenerator.export_report_to_json(
                    report_data, 
                    options.get('output')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'报表已导出到: {filepath}')
                )
            
            # 记录日志
            SystemLog.info(
                'REPORT',
                f'{report_type}报表生成完成',
                extra_data={
                    'report_type': report_type,
                    'export': options['export']
                }
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'报表生成失败: {str(e)}')
            )
            SystemLog.error(
                'REPORT',
                f'{report_type}报表生成失败: {str(e)}'
            )
    
    def generate_daily_report(self, options):
        """生成日报"""
        if options['date']:
            date = datetime.strptime(options['date'], '%Y-%m-%d').date()
        else:
            date = timezone.now().date()
        
        self.stdout.write(f'生成 {date} 的日报...')
        return ReportGenerator.generate_daily_report(date)
    
    def generate_weekly_report(self, options):
        """生成周报"""
        if options['date']:
            start_date = datetime.strptime(options['date'], '%Y-%m-%d')
            start_date = timezone.make_aware(start_date)
        else:
            # 默认生成上周的报表
            start_date = timezone.now() - timedelta(days=7)
        
        self.stdout.write(f'生成从 {start_date.date()} 开始的周报...')
        return ReportGenerator.generate_weekly_report(start_date)
    
    def generate_monthly_report(self, options):
        """生成月报"""
        if options['month']:
            year, month = map(int, options['month'].split('-'))
        else:
            # 默认生成上个月的报表
            now = timezone.now()
            if now.month == 1:
                year, month = now.year - 1, 12
            else:
                year, month = now.year, now.month - 1
        
        self.stdout.write(f'生成 {year}年{month}月 的月报...')
        return ReportGenerator.generate_monthly_report(year, month)
    
    def display_report_summary(self, report_data, report_type):
        """显示报表摘要"""
        self.stdout.write(self.style.SUCCESS(f'\n=== {report_type.upper()}报表摘要 ==='))
        
        if report_type == 'daily':
            self.display_daily_summary(report_data)
        else:
            self.display_period_summary(report_data)
    
    def display_daily_summary(self, report_data):
        """显示日报摘要"""
        date = report_data['date']
        users = report_data['users']
        finance = report_data['finance']
        games = report_data['games']
        rewards = report_data['rewards']
        system = report_data['system']
        
        self.stdout.write(f"日期: {date}")
        self.stdout.write(f"新用户: {users['new_users']}")
        self.stdout.write(f"活跃用户: {users['active_users']}")
        
        self.stdout.write(f"\n财务数据:")
        self.stdout.write(f"  存款: {finance['deposits']['count']}笔, ₦{finance['deposits']['amount'] or 0:,.2f}")
        self.stdout.write(f"  提款: {finance['withdrawals']['count']}笔, ₦{finance['withdrawals']['amount'] or 0:,.2f}")
        self.stdout.write(f"  净流入: ₦{finance['net_flow']:,.2f}")
        
        self.stdout.write(f"\n游戏数据:")
        self.stdout.write(f"  投注: {games['bets']['count']}笔, ₦{games['bets']['amount'] or 0:,.2f}")
        self.stdout.write(f"  派彩: ₦{games['bets']['payout'] or 0:,.2f}")
        self.stdout.write(f"  利润: ₦{games['profit']:,.2f}")
        
        self.stdout.write(f"\n奖励数据:")
        self.stdout.write(f"  返水: {rewards['rebates']['count']}人, ₦{rewards['rebates']['amount'] or 0:,.2f}")
        
        self.stdout.write(f"\n系统数据:")
        log_summary = {log['level']: log['count'] for log in system['logs']}
        self.stdout.write(f"  系统日志: {log_summary}")
        
        event_summary = {event['severity']: event['count'] for event in system['security_events']}
        if event_summary:
            self.stdout.write(f"  安全事件: {event_summary}")
    
    def display_period_summary(self, report_data):
        """显示周报/月报摘要"""
        period = report_data['period']
        users = report_data['users']
        finance = report_data['finance']
        games = report_data['games']
        rewards = report_data['rewards']
        
        self.stdout.write(f"时间段: {period['start_date']} 至 {period['end_date']}")
        
        self.stdout.write(f"\n用户数据:")
        self.stdout.write(f"  活跃用户: {users['active_users']}")
        self.stdout.write(f"  留存率(7天): {users['retention_rates']['7_days']:.1f}%")
        self.stdout.write(f"  留存率(30天): {users['retention_rates']['30_days']:.1f}%")
        
        self.stdout.write(f"\n财务数据:")
        self.stdout.write(f"  总余额: ₦{finance['balance_stats']['total_main'] or 0:,.2f}")
        self.stdout.write(f"  平均余额: ₦{finance['balance_stats']['avg_balance'] or 0:,.2f}")
        self.stdout.write(f"  提款成功率: {finance['withdrawal_success_rate']:.1f}%")
        
        self.stdout.write(f"\n游戏数据:")
        if games['game_stats']:
            top_game = games['game_stats'][0]
            self.stdout.write(f"  热门游戏: {top_game['draw__game__name']}")
            self.stdout.write(f"  总投注: ₦{top_game['total_amount']:,.2f}")
            self.stdout.write(f"  独立玩家: {top_game['unique_players']}")
        
        self.stdout.write(f"\n奖励数据:")
        self.stdout.write(f"  返水用户: {rewards['rebate_stats']['total_users']}")
        self.stdout.write(f"  返水总额: ₦{rewards['rebate_stats']['total_amount'] or 0:,.2f}")
        self.stdout.write(f"  推荐人数: {rewards['referral_stats']['total_referrers']}")
        self.stdout.write(f"  推荐奖励: ₦{rewards['referral_stats']['total_amount'] or 0:,.2f}")
        
        system = report_data['system']
        self.stdout.write(f"\n系统数据:")
        self.stdout.write(f"  错误率: {system['error_rate']:.2f}%")
        self.stdout.write(f"  总日志: {system['total_logs']}")
        self.stdout.write(f"  错误日志: {system['error_logs']}")


# 使用示例：
# python manage.py generate_report --type daily
# python manage.py generate_report --type weekly --date 2024-01-01
# python manage.py generate_report --type monthly --month 2024-01 --export
# python manage.py generate_report --type daily --export --output daily_report_20240101.json