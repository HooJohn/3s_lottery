"""
初始化系统配置管理命令
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.services import ConfigurationService, initialize_system
from apps.core.models import SystemConfig, GameConfig
from apps.rewards.models import VIPLevel, ReferralReward

User = get_user_model()


class Command(BaseCommand):
    help = '初始化系统配置和基础数据'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='重置所有配置（危险操作）',
        )
        parser.add_argument(
            '--admin-user',
            type=str,
            help='创建管理员用户的手机号',
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            help='管理员用户密码',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始初始化系统配置...'))
        
        # 重置配置（如果指定）
        if options['reset']:
            self.stdout.write(self.style.WARNING('重置所有系统配置...'))
            SystemConfig.objects.all().delete()
            GameConfig.objects.all().delete()
        
        # 初始化系统服务
        initialize_system()
        
        # 初始化游戏配置
        self.init_game_configs()
        
        # 初始化VIP等级（如果不存在）
        self.init_vip_levels()
        
        # 初始化推荐奖励配置（如果不存在）
        self.init_referral_rewards()
        
        # 创建管理员用户（如果指定）
        if options['admin_user'] and options['admin_password']:
            self.create_admin_user(options['admin_user'], options['admin_password'])
        
        self.stdout.write(self.style.SUCCESS('系统配置初始化完成！'))
    
    def init_game_configs(self):
        """初始化游戏配置"""
        self.stdout.write('初始化游戏配置...')
        
        game_configs = [
            # 11选5配置
            ('11x5', 'draws_per_day', 7, '每日开奖次数'),
            ('11x5', 'first_draw_time', '09:00', '首次开奖时间'),
            ('11x5', 'draw_interval_minutes', 120, '开奖间隔（分钟）'),
            ('11x5', 'close_before_minutes', 5, '封盘时间（分钟）'),
            ('11x5', 'profit_target', 0.18, '目标利润率'),
            ('11x5', 'max_bet_amount', 10000, '单注最大投注金额'),
            ('11x5', 'min_bet_amount', 2, '单注最小投注金额'),
            
            # 大乐透配置
            ('superlotto', 'draw_days', [3, 6], '开奖日期（周三、周六）'),
            ('superlotto', 'draw_time', '21:30', '开奖时间'),
            ('superlotto', 'sales_stop_minutes', 30, '停售时间（分钟）'),
            ('superlotto', 'profit_target', 0.35, '目标利润率'),
            ('superlotto', 'base_bet_amount', 2, '基础投注金额'),
            ('superlotto', 'max_multiplier', 99, '最大倍数'),
            ('superlotto', 'jackpot_allocation_rate', 0.75, '一等奖奖池分配比例'),
            ('superlotto', 'second_prize_allocation_rate', 0.18, '二等奖奖池分配比例'),
            
            # 666刮刮乐配置
            ('scratch666', 'card_price', 10, '卡片价格'),
            ('scratch666', 'base_amount', 5, '基础奖金'),
            ('scratch666', 'profit_target', 0.30, '目标利润率'),
            ('scratch666', 'scratch_areas', 9, '刮奖区域数量'),
            ('scratch666', 'win_probability_6', 0.15, '"6"中奖概率'),
            ('scratch666', 'win_probability_66', 0.08, '"66"中奖概率'),
            ('scratch666', 'win_probability_666', 0.02, '"666"中奖概率'),
            ('scratch666', 'multiplier_6', 1, '"6"奖金倍数'),
            ('scratch666', 'multiplier_66', 2, '"66"奖金倍数'),
            ('scratch666', 'multiplier_666', 3, '"666"奖金倍数'),
            ('scratch666', 'enable_auto_scratch', True, '启用自动连刮'),
            ('scratch666', 'max_auto_scratch', 100, '最大自动连刮次数'),
            
            # 体育博彩配置
            ('sports', 'profit_target', 0.10, '目标利润率'),
            ('sports', 'min_bet_amount', 10, '最小投注金额'),
            ('sports', 'max_bet_amount', 100000, '最大投注金额'),
            ('sports', 'auto_transfer', True, '自动转账开关'),
        ]
        
        for game_type, config_key, config_value, description in game_configs:
            GameConfig.objects.get_or_create(
                game_type=game_type,
                config_key=config_key,
                defaults={
                    'config_value': config_value,
                    'description': description,
                    'is_active': True
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'游戏配置初始化完成，共 {len(game_configs)} 项'))
    
    def init_vip_levels(self):
        """初始化VIP等级"""
        if VIPLevel.objects.exists():
            self.stdout.write('VIP等级已存在，跳过初始化')
            return
        
        self.stdout.write('初始化VIP等级...')
        
        vip_levels = [
            {
                'level': 0,
                'name': 'VIP0',
                'required_turnover': 0,
                'rebate_rate': 0.0038,  # 0.38%
                'daily_withdraw_limit': 50000,
                'daily_withdraw_times': 3,
                'withdraw_fee_rate': 0.02,  # 2.0%
                'monthly_bonus': 0,
                'birthday_bonus': 0,
            },
            {
                'level': 1,
                'name': 'VIP1',
                'required_turnover': 10000,
                'rebate_rate': 0.004,  # 0.40%
                'daily_withdraw_limit': 100000,
                'daily_withdraw_times': 5,
                'withdraw_fee_rate': 0.015,  # 1.5%
                'monthly_bonus': 100,
                'birthday_bonus': 200,
            },
            {
                'level': 2,
                'name': 'VIP2',
                'required_turnover': 50000,
                'rebate_rate': 0.0045,  # 0.45%
                'daily_withdraw_limit': 200000,
                'daily_withdraw_times': 8,
                'withdraw_fee_rate': 0.01,  # 1.0%
                'monthly_bonus': 300,
                'birthday_bonus': 500,
            },
            {
                'level': 3,
                'name': 'VIP3',
                'required_turnover': 200000,
                'rebate_rate': 0.005,  # 0.50%
                'daily_withdraw_limit': 500000,
                'daily_withdraw_times': 10,
                'withdraw_fee_rate': 0.008,  # 0.8%
                'monthly_bonus': 800,
                'birthday_bonus': 1000,
            },
            {
                'level': 4,
                'name': 'VIP4',
                'required_turnover': 500000,
                'rebate_rate': 0.0055,  # 0.55%
                'daily_withdraw_limit': 1000000,
                'daily_withdraw_times': 15,
                'withdraw_fee_rate': 0.006,  # 0.6%
                'monthly_bonus': 2000,
                'birthday_bonus': 3000,
            },
            {
                'level': 5,
                'name': 'VIP5',
                'required_turnover': 1000000,
                'rebate_rate': 0.006,  # 0.60%
                'daily_withdraw_limit': 2000000,
                'daily_withdraw_times': 20,
                'withdraw_fee_rate': 0.004,  # 0.4%
                'monthly_bonus': 5000,
                'birthday_bonus': 8000,
            },
            {
                'level': 6,
                'name': 'VIP6',
                'required_turnover': 2000000,
                'rebate_rate': 0.007,  # 0.70%
                'daily_withdraw_limit': 5000000,
                'daily_withdraw_times': 30,
                'withdraw_fee_rate': 0.002,  # 0.2%
                'monthly_bonus': 10000,
                'birthday_bonus': 15000,
            },
            {
                'level': 7,
                'name': 'VIP7',
                'required_turnover': 5000000,
                'rebate_rate': 0.008,  # 0.80%
                'daily_withdraw_limit': 10000000,
                'daily_withdraw_times': 50,
                'withdraw_fee_rate': 0.0,  # 0%免费
                'monthly_bonus': 20000,
                'birthday_bonus': 30000,
                'priority_support': True,
                'dedicated_manager': True,
                'exclusive_promotions': True,
                'higher_bonus_rates': True,
            },
        ]
        
        for vip_data in vip_levels:
            VIPLevel.objects.create(**vip_data)
        
        self.stdout.write(self.style.SUCCESS(f'VIP等级初始化完成，共 {len(vip_levels)} 个等级'))
    
    def init_referral_rewards(self):
        """初始化推荐奖励配置"""
        if ReferralReward.objects.exists():
            self.stdout.write('推荐奖励配置已存在，跳过初始化')
            return
        
        self.stdout.write('初始化推荐奖励配置...')
        
        referral_rewards = [
            {'level': 1, 'name': '一级推荐', 'reward_rate': 0.03, 'description': '直接推荐用户，获得其流水的3%奖励'},
            {'level': 2, 'name': '二级推荐', 'reward_rate': 0.02, 'description': '二级推荐用户，获得其流水的2%奖励'},
            {'level': 3, 'name': '三级推荐', 'reward_rate': 0.01, 'description': '三级推荐用户，获得其流水的1%奖励'},
            {'level': 4, 'name': '四级推荐', 'reward_rate': 0.007, 'description': '四级推荐用户，获得其流水的0.7%奖励'},
            {'level': 5, 'name': '五级推荐', 'reward_rate': 0.005, 'description': '五级推荐用户，获得其流水的0.5%奖励'},
            {'level': 6, 'name': '六级推荐', 'reward_rate': 0.003, 'description': '六级推荐用户，获得其流水的0.3%奖励'},
            {'level': 7, 'name': '七级推荐', 'reward_rate': 0.001, 'description': '七级推荐用户，获得其流水的0.1%奖励'},
        ]
        
        for reward_data in referral_rewards:
            ReferralReward.objects.create(**reward_data)
        
        self.stdout.write(self.style.SUCCESS(f'推荐奖励配置初始化完成，共 {len(referral_rewards)} 个等级'))
    
    def create_admin_user(self, phone, password):
        """创建管理员用户"""
        self.stdout.write(f'创建管理员用户: {phone}')
        
        if User.objects.filter(phone=phone).exists():
            self.stdout.write(self.style.WARNING(f'用户 {phone} 已存在'))
            return
        
        admin_user = User.objects.create_user(
            phone=phone,
            username=phone,
            password=password,
            full_name='系统管理员',
            is_staff=True,
            is_superuser=True,
            kyc_status='APPROVED'
        )
        
        self.stdout.write(self.style.SUCCESS(f'管理员用户创建成功: {phone}'))