"""
初始化大乐透游戏管理命令
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal

from apps.games.models import Game
from apps.games.superlotto.models import SuperLottoGame
from apps.games.superlotto.services import SuperLottoService


class Command(BaseCommand):
    help = '初始化大乐透游戏配置和首期'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-game',
            action='store_true',
            help='创建大乐透游戏记录',
        )
        parser.add_argument(
            '--create-config',
            action='store_true',
            help='创建游戏配置',
        )
        parser.add_argument(
            '--create-first-draw',
            action='store_true',
            help='创建首期',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='执行所有初始化操作',
        )
    
    def handle(self, *args, **options):
        if options['all']:
            options['create_game'] = True
            options['create_config'] = True
            options['create_first_draw'] = True
        
        if options['create_game']:
            self.create_game()
        
        if options['create_config']:
            self.create_config()
        
        if options['create_first_draw']:
            self.create_first_draw()
    
    def create_game(self):
        """创建大乐透游戏记录"""
        try:
            game, created = Game.objects.get_or_create(
                code='superlotto',
                defaults={
                    'name': '大乐透',
                    'game_type': '彩票',
                    'description': '大乐透是一种数字型彩票游戏，前区35选5，后区12选2，设置9个奖级。',
                    'rules': {
                        'front_zone': '从01-35中选择5个号码',
                        'back_zone': '从01-12中选择2个号码',
                        'bet_types': ['单式', '复式', '胆拖'],
                        'draw_schedule': '每周三、六21:30开奖',
                        'prize_levels': 9,
                        'min_bet_amount': 2.00
                    },
                    'status': 'ACTIVE',
                    'sort_order': 2
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'成功创建大乐透游戏: {game.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'大乐透游戏已存在: {game.name}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'创建大乐透游戏失败: {str(e)}')
            )
    
    def create_config(self):
        """创建游戏配置"""
        try:
            game = Game.objects.get(code='superlotto')
            
            config, created = SuperLottoGame.objects.get_or_create(
                game=game,
                defaults={
                    'base_bet_amount': Decimal('2.00'),
                    'max_multiplier': 99,
                    'front_zone_min': 1,
                    'front_zone_max': 35,
                    'front_zone_count': 5,
                    'back_zone_min': 1,
                    'back_zone_max': 12,
                    'back_zone_count': 2,
                    'jackpot_allocation_rate': Decimal('0.75'),
                    'second_prize_allocation_rate': Decimal('0.18'),
                    'third_prize_amount': Decimal('10000.00'),
                    'fourth_prize_amount': Decimal('3000.00'),
                    'fifth_prize_amount': Decimal('300.00'),
                    'sixth_prize_amount': Decimal('200.00'),
                    'seventh_prize_amount': Decimal('100.00'),
                    'eighth_prize_amount': Decimal('15.00'),
                    'ninth_prize_amount': Decimal('5.00'),
                    'profit_target': Decimal('0.35'),
                    'draw_days': '3,6',  # 周三、周六
                    'draw_time': '21:30:00',
                    'sales_stop_minutes': 30
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS('成功创建大乐透游戏配置')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('大乐透游戏配置已存在')
                )
                
        except Game.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('大乐透游戏不存在，请先创建游戏')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'创建游戏配置失败: {str(e)}')
            )
    
    def create_first_draw(self):
        """创建首期"""
        try:
            result = SuperLottoService.create_next_draw()
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'成功创建首期: {result["data"]["draw_number"]}期'
                    )
                )
                self.stdout.write(
                    f'开奖时间: {result["data"]["draw_time"]}'
                )
                self.stdout.write(
                    f'停售时间: {result["data"]["sales_end_time"]}'
                )
                self.stdout.write(
                    f'奖池金额: ₦{result["data"]["jackpot_amount"]}'
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'创建首期失败: {result["message"]}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'创建首期失败: {str(e)}')
            )