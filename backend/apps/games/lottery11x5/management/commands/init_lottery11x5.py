"""
初始化11选5彩票游戏数据
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from apps.games.models import Game, BetType, LotteryNumber
from apps.games.lottery11x5.models import Lottery11x5Game


class Command(BaseCommand):
    help = '初始化11选5彩票游戏数据'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新创建数据（会删除现有数据）',
        )
    
    def handle(self, *args, **options):
        force = options['force']
        
        try:
            # 创建或获取11选5游戏
            game, created = Game.objects.get_or_create(
                code='11x5',
                game_type='11选5',
                defaults={
                    'name': '11选5',
                    'description': '11选5是一种简单易懂的数字彩票游戏，从01-11中选择5个号码进行投注。',
                    'rules': '''
11选5游戏规则：
1. 每期从01-11共11个号码中开出5个号码
2. 支持定位胆、任选等多种玩法
3. 每日7期，开奖时间：10:00-22:00，间隔2小时
4. 开奖前5分钟停止投注
5. 开奖后立即派发奖金
                    '''.strip(),
                    'min_bet': Decimal('1.00'),
                    'max_bet': Decimal('10000.00'),
                    'status': 'ACTIVE',
                    'sort_order': 1,
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'创建11选5游戏: {game.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'11选5游戏已存在: {game.name}')
                )
            
            # 创建游戏配置
            config, config_created = Lottery11x5Game.objects.get_or_create(
                game=game,
                defaults={
                    'draw_count_per_day': 7,
                    'first_draw_time': timezone.datetime.strptime('10:00', '%H:%M').time(),
                    'draw_interval_minutes': 120,  # 2小时间隔
                    'close_before_minutes': 5,
                    'auto_create_draws': True,
                    'auto_draw_results': True,
                    'profit_target': Decimal('0.18'),  # 18%毛利率
                    'enable_position_bets': True,
                    'enable_any_bets': True,
                    'enable_group_bets': True,
                    'position_odds': Decimal('9.90'),
                    'any_1_odds': Decimal('2.20'),
                    'any_2_odds': Decimal('5.50'),
                    'any_3_odds': Decimal('16.50'),
                    'any_4_odds': Decimal('66.00'),
                    'any_5_odds': Decimal('330.00'),
                }
            )
            
            if config_created:
                self.stdout.write(
                    self.style.SUCCESS('创建11选5游戏配置')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('11选5游戏配置已存在')
                )
            
            # 创建投注类型
            bet_types_data = [
                {
                    'name': '定位胆',
                    'code': 'POSITION',
                    'description': '选择特定位置的号码进行投注',
                    'odds': Decimal('9.90'),
                    'min_bet': Decimal('1.00'),
                    'max_bet': Decimal('1000.00'),
                    'max_payout': Decimal('9900.00'),
                    'sort_order': 1,
                    'rules': {
                        'positions': [1, 2, 3, 4, 5],
                        'numbers_per_position': 1,
                        'min_positions': 1,
                        'max_positions': 5,
                    }
                },
                {
                    'name': '任选一',
                    'code': 'ANY_1',
                    'description': '任选1个号码，开奖号码中包含即中奖',
                    'odds': Decimal('2.20'),
                    'min_bet': Decimal('1.00'),
                    'max_bet': Decimal('1000.00'),
                    'max_payout': Decimal('2200.00'),
                    'sort_order': 2,
                    'rules': {
                        'selected_count': 1,
                        'min_numbers': 1,
                        'max_numbers': 11,
                    }
                },
                {
                    'name': '任选二',
                    'code': 'ANY_2',
                    'description': '任选2个号码，开奖号码中包含2个即中奖',
                    'odds': Decimal('5.50'),
                    'min_bet': Decimal('1.00'),
                    'max_bet': Decimal('1000.00'),
                    'max_payout': Decimal('5500.00'),
                    'sort_order': 3,
                    'rules': {
                        'selected_count': 2,
                        'min_numbers': 2,
                        'max_numbers': 11,
                    }
                },
                {
                    'name': '任选三',
                    'code': 'ANY_3',
                    'description': '任选3个号码，开奖号码中包含3个即中奖',
                    'odds': Decimal('16.50'),
                    'min_bet': Decimal('1.00'),
                    'max_bet': Decimal('500.00'),
                    'max_payout': Decimal('8250.00'),
                    'sort_order': 4,
                    'rules': {
                        'selected_count': 3,
                        'min_numbers': 3,
                        'max_numbers': 11,
                    }
                },
                {
                    'name': '任选四',
                    'code': 'ANY_4',
                    'description': '任选4个号码，开奖号码中包含4个即中奖',
                    'odds': Decimal('66.00'),
                    'min_bet': Decimal('1.00'),
                    'max_bet': Decimal('100.00'),
                    'max_payout': Decimal('6600.00'),
                    'sort_order': 5,
                    'rules': {
                        'selected_count': 4,
                        'min_numbers': 4,
                        'max_numbers': 11,
                    }
                },
                {
                    'name': '任选五',
                    'code': 'ANY_5',
                    'description': '任选5个号码，开奖号码中包含5个即中奖',
                    'odds': Decimal('330.00'),
                    'min_bet': Decimal('1.00'),
                    'max_bet': Decimal('20.00'),
                    'max_payout': Decimal('6600.00'),
                    'sort_order': 6,
                    'rules': {
                        'selected_count': 5,
                        'min_numbers': 5,
                        'max_numbers': 11,
                    }
                },
            ]
            
            bet_types_created = 0
            for bet_type_data in bet_types_data:
                bet_type, bt_created = BetType.objects.get_or_create(
                    game=game,
                    code=bet_type_data['code'],
                    defaults=bet_type_data
                )
                
                if bt_created:
                    bet_types_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'创建投注类型: {bet_type.name}')
                    )
            
            if bet_types_created == 0:
                self.stdout.write(
                    self.style.WARNING('所有投注类型已存在')
                )
            
            # 创建彩票号码
            numbers_created = 0
            for number in range(1, 12):
                lottery_number, ln_created = LotteryNumber.objects.get_or_create(
                    game=game,
                    number=number,
                    defaults={
                        'display_name': f'{number:02d}',
                        'is_active': True,
                    }
                )
                
                if ln_created:
                    numbers_created += 1
            
            if numbers_created > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'创建彩票号码: {numbers_created}个')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('彩票号码已存在')
                )
            
            # 创建今日期次
            from apps.games.lottery11x5.services import Lottery11x5Service
            today_draws = Lottery11x5Service.create_draws_for_today()
            
            if today_draws:
                self.stdout.write(
                    self.style.SUCCESS(f'创建今日期次: {len(today_draws)}期')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('今日期次已存在或创建失败')
                )
            
            self.stdout.write(
                self.style.SUCCESS('11选5彩票游戏初始化完成！')
            )
            
            # 显示游戏信息
            self.stdout.write('\n=== 游戏信息 ===')
            self.stdout.write(f'游戏名称: {game.name}')
            self.stdout.write(f'游戏代码: {game.code}')
            self.stdout.write(f'游戏类型: {game.game_type}')
            self.stdout.write(f'投注范围: ₦{game.min_bet} - ₦{game.max_bet}')
            self.stdout.write(f'每日期数: {config.draw_count_per_day}期')
            self.stdout.write(f'开奖间隔: {config.draw_interval_minutes}分钟')
            self.stdout.write(f'目标毛利: {config.profit_target * 100}%')
            
            self.stdout.write('\n=== 投注类型 ===')
            for bt in BetType.objects.filter(game=game).order_by('sort_order'):
                self.stdout.write(f'{bt.name}: 赔率{bt.odds}倍, 投注范围₦{bt.min_bet}-₦{bt.max_bet}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'初始化失败: {str(e)}')
            )
            raise e