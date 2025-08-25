"""
大乐透彩票服务
"""

import uuid
import random
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from math import comb
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
import logging

from apps.games.models import Game
from apps.finance.models import Transaction, UserBalance
from .models import SuperLottoGame, SuperLottoDraw, SuperLottoBet, SuperLottoStatistics

logger = logging.getLogger(__name__)


class SuperLottoService:
    """
    大乐透彩票服务
    """
    
    @staticmethod
    def get_game():
        """
        获取大乐透游戏
        """
        try:
            game = Game.objects.get(code='superlotto', game_type='彩票')
            return game
        except Game.DoesNotExist:
            return None
    
    @staticmethod
    def get_game_config():
        """
        获取大乐透游戏配置
        """
        game = SuperLottoService.get_game()
        if not game:
            return None
        
        try:
            config = SuperLottoGame.objects.get(game=game)
            return config
        except SuperLottoGame.DoesNotExist:
            return None
    
    @staticmethod
    def get_current_draw():
        """
        获取当前销售期次
        """
        game = SuperLottoService.get_game()
        if not game:
            return None
        
        try:
            current_draw = SuperLottoDraw.objects.filter(
                game=game,
                status='OPEN'
            ).order_by('draw_time').first()
            
            return current_draw
        except SuperLottoDraw.DoesNotExist:
            return None
    
    @staticmethod
    def get_latest_draws(limit: int = 10):
        """
        获取最近的开奖期次
        """
        game = SuperLottoService.get_game()
        if not game:
            return []
        
        draws = SuperLottoDraw.objects.filter(
            game=game,
            status__in=['DRAWN', 'SETTLED']
        ).order_by('-draw_number')[:limit]
        
        result = []
        for draw in draws:
            result.append({
                'draw_number': draw.draw_number,
                'draw_time': draw.draw_time.isoformat(),
                'front_numbers': draw.front_numbers,
                'back_numbers': draw.back_numbers,
                'jackpot_amount': float(draw.jackpot_amount),
                'total_sales': float(draw.total_sales),
                'total_winners': draw.calculate_total_winners(),
                'first_prize_winners': draw.first_prize_winners,
                'first_prize_amount': float(draw.first_prize_amount),
                'status': draw.status
            })
        
        return result
    
    @staticmethod
    def calculate_bet_amount(bet_type: str, front_numbers: List[int], back_numbers: List[int],
                           front_dan: List[int] = None, front_tuo: List[int] = None,
                           back_dan: List[int] = None, back_tuo: List[int] = None,
                           multiplier: int = 1) -> Dict[str, Any]:
        """
        计算投注金额和注数
        """
        try:
            config = SuperLottoService.get_game_config()
            if not config:
                return {'success': False, 'message': '游戏配置不存在'}
            
            bet_count = 0
            
            if bet_type == 'SINGLE':
                # 单式投注
                if len(front_numbers) != 5 or len(back_numbers) != 2:
                    return {'success': False, 'message': '单式投注需要选择5个前区号码和2个后区号码'}
                bet_count = 1
                
            elif bet_type == 'MULTIPLE':
                # 复式投注
                if len(front_numbers) < 5 or len(back_numbers) < 2:
                    return {'success': False, 'message': '复式投注前区至少选择5个号码，后区至少选择2个号码'}
                
                front_combinations = comb(len(front_numbers), 5)
                back_combinations = comb(len(back_numbers), 2)
                bet_count = front_combinations * back_combinations
                
            elif bet_type == 'SYSTEM':
                # 胆拖投注
                front_dan = front_dan or []
                front_tuo = front_tuo or []
                back_dan = back_dan or []
                back_tuo = back_tuo or []
                
                # 验证胆拖号码
                if len(front_dan) + len(front_tuo) < 5:
                    return {'success': False, 'message': '前区胆码+拖码总数至少5个'}
                if len(back_dan) + len(back_tuo) < 2:
                    return {'success': False, 'message': '后区胆码+拖码总数至少2个'}
                if len(front_dan) >= 5:
                    return {'success': False, 'message': '前区胆码不能超过4个'}
                if len(back_dan) >= 2:
                    return {'success': False, 'message': '后区胆码不能超过1个'}
                
                # 计算组合数
                front_need = 5 - len(front_dan)
                back_need = 2 - len(back_dan)
                
                if len(front_tuo) < front_need:
                    return {'success': False, 'message': f'前区拖码至少需要{front_need}个'}
                if len(back_tuo) < back_need:
                    return {'success': False, 'message': f'后区拖码至少需要{back_need}个'}
                
                front_combinations = comb(len(front_tuo), front_need)
                back_combinations = comb(len(back_tuo), back_need)
                bet_count = front_combinations * back_combinations
            
            else:
                return {'success': False, 'message': '无效的投注类型'}
            
            # 计算金额
            single_amount = config.base_bet_amount
            total_amount = single_amount * bet_count * multiplier
            
            return {
                'success': True,
                'bet_count': bet_count,
                'single_amount': float(single_amount),
                'total_amount': float(total_amount),
                'multiplier': multiplier
            }
            
        except Exception as e:
            logger.error(f"计算投注金额失败: {str(e)}")
            return {'success': False, 'message': f'计算失败: {str(e)}'}
    
    @staticmethod
    def place_bet(user, bet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        投注下单
        """
        try:
            # 获取当前期次
            current_draw = SuperLottoService.get_current_draw()
            if not current_draw:
                return {'success': False, 'message': '当前没有可投注的期次'}
            
            if not current_draw.is_sales_open():
                return {'success': False, 'message': '当前期次已停售'}
            
            # 验证投注数据
            bet_type = bet_data.get('bet_type')
            front_numbers = bet_data.get('front_numbers', [])
            back_numbers = bet_data.get('back_numbers', [])
            multiplier = bet_data.get('multiplier', 1)
            
            # 胆拖相关
            front_dan = bet_data.get('front_dan_numbers', [])
            front_tuo = bet_data.get('front_tuo_numbers', [])
            back_dan = bet_data.get('back_dan_numbers', [])
            back_tuo = bet_data.get('back_tuo_numbers', [])
            
            # 计算投注金额
            calc_result = SuperLottoService.calculate_bet_amount(
                bet_type, front_numbers, back_numbers,
                front_dan, front_tuo, back_dan, back_tuo, multiplier
            )
            
            if not calc_result['success']:
                return calc_result
            
            # 检查用户余额
            try:
                balance = user.balance
                total_amount = Decimal(str(calc_result['total_amount']))
                
                if balance.get_available_balance() < total_amount:
                    return {
                        'success': False,
                        'message': f'余额不足，需要 ₦{total_amount}，当前可用余额 ₦{balance.get_available_balance()}'
                    }
            except UserBalance.DoesNotExist:
                return {'success': False, 'message': '用户余额信息不存在'}
            
            with transaction.atomic():
                # 扣除余额
                balance.deduct_balance(total_amount, 'available', f'大乐透投注 {current_draw.draw_number}期')
                
                # 创建投注交易记录
                bet_transaction = Transaction.objects.create(
                    user=user,
                    type='BET',
                    amount=total_amount,
                    fee=Decimal('0.00'),
                    actual_amount=total_amount,
                    status='COMPLETED',
                    reference_id=str(uuid.uuid4()),
                    description=f'大乐透投注 {current_draw.draw_number}期',
                    metadata={
                        'game_type': '彩票',
                        'game_name': '大乐透',
                        'draw_number': current_draw.draw_number,
                        'bet_type': bet_type,
                        'bet_count': calc_result['bet_count'],
                        'multiplier': multiplier,
                    }
                )
                
                # 创建投注记录
                bet = SuperLottoBet.objects.create(
                    user=user,
                    draw=current_draw,
                    bet_type=bet_type,
                    front_numbers=front_numbers,
                    back_numbers=back_numbers,
                    front_dan_numbers=front_dan if bet_type == 'SYSTEM' else None,
                    front_tuo_numbers=front_tuo if bet_type == 'SYSTEM' else None,
                    back_dan_numbers=back_dan if bet_type == 'SYSTEM' else None,
                    back_tuo_numbers=back_tuo if bet_type == 'SYSTEM' else None,
                    multiplier=multiplier,
                    bet_count=calc_result['bet_count'],
                    single_amount=Decimal(str(calc_result['single_amount'])),
                    total_amount=total_amount,
                    bet_transaction_id=bet_transaction.id,
                    status='PENDING'
                )
                
                return {
                    'success': True,
                    'message': '投注成功',
                    'data': {
                        'bet_id': str(bet.id),
                        'draw_number': current_draw.draw_number,
                        'bet_type': bet_type,
                        'bet_count': calc_result['bet_count'],
                        'total_amount': float(total_amount),
                        'multiplier': multiplier,
                        'numbers_display': bet.get_numbers_display(),
                        'balance_after': float(balance.get_available_balance()),
                    }
                }
                
        except Exception as e:
            logger.error(f"大乐透投注失败: {str(e)}")
            return {'success': False, 'message': f'投注失败: {str(e)}'}
    
    @staticmethod
    def get_user_bets(user, draw_number: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取用户投注记录
        """
        try:
            queryset = SuperLottoBet.objects.filter(user=user).select_related('draw')
            
            if draw_number:
                queryset = queryset.filter(draw__draw_number=draw_number)
            
            bets = queryset.order_by('-created_at')[:limit]
            
            result = []
            for bet in bets:
                result.append({
                    'bet_id': str(bet.id),
                    'draw_number': bet.draw.draw_number,
                    'draw_time': bet.draw.draw_time.isoformat(),
                    'bet_type': bet.bet_type,
                    'bet_type_display': bet.get_bet_type_display(),
                    'numbers_display': bet.get_numbers_display(),
                    'bet_count': bet.bet_count,
                    'multiplier': bet.multiplier,
                    'total_amount': float(bet.total_amount),
                    'status': bet.status,
                    'is_winner': bet.is_winner,
                    'winning_level': bet.winning_level,
                    'winning_amount': float(bet.winning_amount),
                    'created_at': bet.created_at.isoformat(),
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取用户投注记录失败: {str(e)}")
            return []
    
    @staticmethod
    def generate_random_numbers() -> Dict[str, List[int]]:
        """
        生成随机号码（机选功能）
        """
        try:
            config = SuperLottoService.get_game_config()
            if not config:
                return {'success': False, 'message': '游戏配置不存在'}
            
            # 生成前区号码
            front_numbers = random.sample(
                range(config.front_zone_min, config.front_zone_max + 1),
                config.front_zone_count
            )
            
            # 生成后区号码
            back_numbers = random.sample(
                range(config.back_zone_min, config.back_zone_max + 1),
                config.back_zone_count
            )
            
            return {
                'success': True,
                'front_numbers': sorted(front_numbers),
                'back_numbers': sorted(back_numbers)
            }
            
        except Exception as e:
            logger.error(f"生成随机号码失败: {str(e)}")
            return {'success': False, 'message': f'生成失败: {str(e)}'}
    
    @staticmethod
    def get_draw_info(draw_number: str = None) -> Dict[str, Any]:
        """
        获取期次信息
        """
        try:
            if draw_number:
                draw = SuperLottoDraw.objects.get(draw_number=draw_number)
            else:
                draw = SuperLottoService.get_current_draw()
                
            if not draw:
                return {'success': False, 'message': '期次不存在'}
            
            # 计算倒计时
            now = timezone.now()
            if draw.status == 'OPEN' and now < draw.sales_end_time:
                time_left = draw.sales_end_time - now
                countdown = {
                    'days': time_left.days,
                    'hours': time_left.seconds // 3600,
                    'minutes': (time_left.seconds % 3600) // 60,
                    'seconds': time_left.seconds % 60,
                    'total_seconds': int(time_left.total_seconds())
                }
            else:
                countdown = None
            
            return {
                'success': True,
                'data': {
                    'draw_number': draw.draw_number,
                    'draw_time': draw.draw_time.isoformat(),
                    'sales_end_time': draw.sales_end_time.isoformat(),
                    'status': draw.status,
                    'is_sales_open': draw.is_sales_open(),
                    'countdown': countdown,
                    'jackpot_amount': float(draw.jackpot_amount),
                    'total_sales': float(draw.total_sales),
                    'front_numbers': draw.front_numbers,
                    'back_numbers': draw.back_numbers,
                    'winning_numbers_display': draw.get_winning_numbers_display(),
                    'total_winners': draw.calculate_total_winners(),
                    'prize_info': {
                        'first_prize': {
                            'winners': draw.first_prize_winners,
                            'amount': float(draw.first_prize_amount)
                        },
                        'second_prize': {
                            'winners': draw.second_prize_winners,
                            'amount': float(draw.second_prize_amount)
                        },
                        'third_prize': {'winners': draw.third_prize_winners},
                        'fourth_prize': {'winners': draw.fourth_prize_winners},
                        'fifth_prize': {'winners': draw.fifth_prize_winners},
                        'sixth_prize': {'winners': draw.sixth_prize_winners},
                        'seventh_prize': {'winners': draw.seventh_prize_winners},
                        'eighth_prize': {'winners': draw.eighth_prize_winners},
                        'ninth_prize': {'winners': draw.ninth_prize_winners},
                    }
                }
            }
            
        except SuperLottoDraw.DoesNotExist:
            return {'success': False, 'message': '期次不存在'}
        except Exception as e:
            logger.error(f"获取期次信息失败: {str(e)}")
            return {'success': False, 'message': f'获取失败: {str(e)}'}
    
    @staticmethod
    def validate_numbers(front_numbers: List[int], back_numbers: List[int]) -> Dict[str, Any]:
        """
        验证号码有效性
        """
        try:
            config = SuperLottoService.get_game_config()
            if not config:
                return {'success': False, 'message': '游戏配置不存在'}
            
            # 验证前区号码
            if not front_numbers:
                return {'success': False, 'message': '请选择前区号码'}
            
            for num in front_numbers:
                if not (config.front_zone_min <= num <= config.front_zone_max):
                    return {
                        'success': False,
                        'message': f'前区号码必须在{config.front_zone_min}-{config.front_zone_max}之间'
                    }
            
            if len(set(front_numbers)) != len(front_numbers):
                return {'success': False, 'message': '前区号码不能重复'}
            
            # 验证后区号码
            if not back_numbers:
                return {'success': False, 'message': '请选择后区号码'}
            
            for num in back_numbers:
                if not (config.back_zone_min <= num <= config.back_zone_max):
                    return {
                        'success': False,
                        'message': f'后区号码必须在{config.back_zone_min}-{config.back_zone_max}之间'
                    }
            
            if len(set(back_numbers)) != len(back_numbers):
                return {'success': False, 'message': '后区号码不能重复'}
            
            return {'success': True, 'message': '号码验证通过'}
            
        except Exception as e:
            logger.error(f"验证号码失败: {str(e)}")
            return {'success': False, 'message': f'验证失败: {str(e)}'}
    
    @staticmethod
    def generate_draw_numbers() -> Dict[str, Any]:
        """
        生成开奖号码
        """
        try:
            config = SuperLottoService.get_game_config()
            if not config:
                return {'success': False, 'message': '游戏配置不存在'}
            
            # 生成前区5个号码（1-35）
            front_numbers = random.sample(
                range(config.front_zone_min, config.front_zone_max + 1),
                config.front_zone_count
            )
            
            # 生成后区2个号码（1-12）
            back_numbers = random.sample(
                range(config.back_zone_min, config.back_zone_max + 1),
                config.back_zone_count
            )
            
            return {
                'success': True,
                'front_numbers': sorted(front_numbers),
                'back_numbers': sorted(back_numbers)
            }
            
        except Exception as e:
            logger.error(f"生成开奖号码失败: {str(e)}")
            return {'success': False, 'message': f'生成失败: {str(e)}'}
    
    @staticmethod
    def conduct_draw(draw_id: str, front_numbers: List[int] = None, back_numbers: List[int] = None) -> Dict[str, Any]:
        """
        执行开奖
        """
        try:
            draw = SuperLottoDraw.objects.get(id=draw_id)
            
            if draw.status != 'CLOSED':
                return {'success': False, 'message': '期次状态不正确，无法开奖'}
            
            # 如果没有提供开奖号码，则自动生成
            if not front_numbers or not back_numbers:
                numbers_result = SuperLottoService.generate_draw_numbers()
                if not numbers_result['success']:
                    return numbers_result
                front_numbers = numbers_result['front_numbers']
                back_numbers = numbers_result['back_numbers']
            
            # 验证开奖号码
            validation_result = SuperLottoService.validate_numbers(front_numbers, back_numbers)
            if not validation_result['success']:
                return validation_result
            
            with transaction.atomic():
                # 更新开奖号码
                draw.front_numbers = front_numbers
                draw.back_numbers = back_numbers
                draw.status = 'DRAWN'
                draw.save()
                
                # 计算中奖情况
                settlement_result = SuperLottoService._settle_draw(draw)
                
                if settlement_result['success']:
                    draw.status = 'SETTLED'
                    draw.save()
                    
                    return {
                        'success': True,
                        'message': '开奖完成',
                        'data': {
                            'draw_number': draw.draw_number,
                            'front_numbers': front_numbers,
                            'back_numbers': back_numbers,
                            'settlement_result': settlement_result['data']
                        }
                    }
                else:
                    return settlement_result
                
        except SuperLottoDraw.DoesNotExist:
            return {'success': False, 'message': '期次不存在'}
        except Exception as e:
            logger.error(f"开奖失败: {str(e)}")
            return {'success': False, 'message': f'开奖失败: {str(e)}'}
    
    @staticmethod
    def _settle_draw(draw: SuperLottoDraw) -> Dict[str, Any]:
        """
        结算期次中奖情况
        """
        try:
            config = SuperLottoService.get_game_config()
            if not config:
                return {'success': False, 'message': '游戏配置不存在'}
            
            # 获取所有投注记录
            bets = SuperLottoBet.objects.filter(draw=draw, status='PENDING')
            
            # 统计各等奖中奖情况
            prize_stats = {
                1: {'count': 0, 'total_amount': Decimal('0.00')},
                2: {'count': 0, 'total_amount': Decimal('0.00')},
                3: {'count': 0, 'total_amount': Decimal('0.00')},
                4: {'count': 0, 'total_amount': Decimal('0.00')},
                5: {'count': 0, 'total_amount': Decimal('0.00')},
                6: {'count': 0, 'total_amount': Decimal('0.00')},
                7: {'count': 0, 'total_amount': Decimal('0.00')},
                8: {'count': 0, 'total_amount': Decimal('0.00')},
                9: {'count': 0, 'total_amount': Decimal('0.00')},
            }
            
            total_winning_amount = Decimal('0.00')
            
            # 逐个检查投注记录
            for bet in bets:
                winning_result = SuperLottoService._check_bet_winning(bet, draw.front_numbers, draw.back_numbers)
                
                if winning_result['is_winner']:
                    level = winning_result['level']
                    amount = SuperLottoService._calculate_prize_amount(level, config, draw, bet.multiplier)
                    
                    # 更新投注记录
                    bet.is_winner = True
                    bet.winning_level = level
                    bet.winning_amount = amount
                    bet.winning_details = winning_result['details']
                    bet.status = 'WINNING'
                    
                    # 统计中奖情况
                    prize_stats[level]['count'] += 1
                    prize_stats[level]['total_amount'] += amount
                    total_winning_amount += amount
                    
                    # 派发奖金
                    SuperLottoService._award_prize(bet, amount)
                else:
                    bet.status = 'LOSING'
                
                bet.save()
            
            # 更新期次中奖统计
            draw.first_prize_winners = prize_stats[1]['count']
            draw.first_prize_amount = prize_stats[1]['total_amount']
            draw.second_prize_winners = prize_stats[2]['count']
            draw.second_prize_amount = prize_stats[2]['total_amount']
            draw.third_prize_winners = prize_stats[3]['count']
            draw.fourth_prize_winners = prize_stats[4]['count']
            draw.fifth_prize_winners = prize_stats[5]['count']
            draw.sixth_prize_winners = prize_stats[6]['count']
            draw.seventh_prize_winners = prize_stats[7]['count']
            draw.eighth_prize_winners = prize_stats[8]['count']
            draw.ninth_prize_winners = prize_stats[9]['count']
            draw.save()
            
            # 更新统计数据
            SuperLottoService._update_draw_statistics(draw, prize_stats, total_winning_amount)
            
            return {
                'success': True,
                'message': '结算完成',
                'data': {
                    'total_bets': bets.count(),
                    'total_winners': sum(stats['count'] for stats in prize_stats.values()),
                    'total_winning_amount': float(total_winning_amount),
                    'prize_breakdown': {
                        f'level_{level}': {
                            'winners': stats['count'],
                            'total_amount': float(stats['total_amount'])
                        }
                        for level, stats in prize_stats.items()
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"结算期次失败: {str(e)}")
            return {'success': False, 'message': f'结算失败: {str(e)}'}
    
    @staticmethod
    def _check_bet_winning(bet: SuperLottoBet, winning_front: List[int], winning_back: List[int]) -> Dict[str, Any]:
        """
        检查投注是否中奖
        """
        try:
            if bet.bet_type == 'SINGLE':
                # 单式投注
                return SuperLottoService._check_single_winning(
                    bet.front_numbers, bet.back_numbers, winning_front, winning_back
                )
            elif bet.bet_type == 'MULTIPLE':
                # 复式投注 - 检查所有可能的组合
                return SuperLottoService._check_multiple_winning(
                    bet.front_numbers, bet.back_numbers, winning_front, winning_back
                )
            elif bet.bet_type == 'SYSTEM':
                # 胆拖投注 - 检查胆拖组合
                return SuperLottoService._check_system_winning(
                    bet.front_dan_numbers, bet.front_tuo_numbers,
                    bet.back_dan_numbers, bet.back_tuo_numbers,
                    winning_front, winning_back
                )
            
            return {'is_winner': False, 'level': None, 'details': {}}
            
        except Exception as e:
            logger.error(f"检查中奖失败: {str(e)}")
            return {'is_winner': False, 'level': None, 'details': {}}
    
    @staticmethod
    def _check_single_winning(front_nums: List[int], back_nums: List[int], 
                            winning_front: List[int], winning_back: List[int]) -> Dict[str, Any]:
        """
        检查单式投注中奖
        """
        front_match = len(set(front_nums) & set(winning_front))
        back_match = len(set(back_nums) & set(winning_back))
        
        # 根据中奖规则判断等级
        level = SuperLottoService._get_prize_level(front_match, back_match)
        
        return {
            'is_winner': level is not None,
            'level': level,
            'details': {
                'front_match': front_match,
                'back_match': back_match,
                'front_numbers': front_nums,
                'back_numbers': back_nums
            }
        }
    
    @staticmethod
    def _check_multiple_winning(front_nums: List[int], back_nums: List[int],
                              winning_front: List[int], winning_back: List[int]) -> Dict[str, Any]:
        """
        检查复式投注中奖（取最高奖级）
        """
        from itertools import combinations
        
        best_level = None
        best_details = {}
        
        # 遍历所有前区组合
        for front_combo in combinations(front_nums, 5):
            # 遍历所有后区组合
            for back_combo in combinations(back_nums, 2):
                result = SuperLottoService._check_single_winning(
                    list(front_combo), list(back_combo), winning_front, winning_back
                )
                
                if result['is_winner']:
                    if best_level is None or result['level'] < best_level:
                        best_level = result['level']
                        best_details = result['details']
        
        return {
            'is_winner': best_level is not None,
            'level': best_level,
            'details': best_details
        }
    
    @staticmethod
    def _check_system_winning(front_dan: List[int], front_tuo: List[int],
                            back_dan: List[int], back_tuo: List[int],
                            winning_front: List[int], winning_back: List[int]) -> Dict[str, Any]:
        """
        检查胆拖投注中奖（取最高奖级）
        """
        from itertools import combinations
        
        best_level = None
        best_details = {}
        
        # 前区需要从拖码中选择的数量
        front_need = 5 - len(front_dan or [])
        back_need = 2 - len(back_dan or [])
        
        # 遍历前区拖码组合
        for front_tuo_combo in combinations(front_tuo or [], front_need):
            front_combo = (front_dan or []) + list(front_tuo_combo)
            
            # 遍历后区拖码组合
            for back_tuo_combo in combinations(back_tuo or [], back_need):
                back_combo = (back_dan or []) + list(back_tuo_combo)
                
                result = SuperLottoService._check_single_winning(
                    front_combo, back_combo, winning_front, winning_back
                )
                
                if result['is_winner']:
                    if best_level is None or result['level'] < best_level:
                        best_level = result['level']
                        best_details = result['details']
        
        return {
            'is_winner': best_level is not None,
            'level': best_level,
            'details': best_details
        }
    
    @staticmethod
    def _get_prize_level(front_match: int, back_match: int) -> Optional[int]:
        """
        根据中奖号码数量获取奖级
        """
        # 大乐透9个奖级规则
        if front_match == 5 and back_match == 2:
            return 1  # 一等奖：5+2
        elif front_match == 5 and back_match == 1:
            return 2  # 二等奖：5+1
        elif front_match == 5 and back_match == 0:
            return 3  # 三等奖：5+0
        elif front_match == 4 and back_match == 2:
            return 4  # 四等奖：4+2
        elif front_match == 4 and back_match == 1:
            return 5  # 五等奖：4+1
        elif front_match == 3 and back_match == 2:
            return 6  # 六等奖：3+2
        elif front_match == 4 and back_match == 0:
            return 7  # 七等奖：4+0
        elif (front_match == 3 and back_match == 1) or (front_match == 2 and back_match == 2):
            return 8  # 八等奖：3+1 或 2+2
        elif (front_match == 3 and back_match == 0) or (front_match == 1 and back_match == 2) or \
             (front_match == 2 and back_match == 1) or (front_match == 0 and back_match == 2):
            return 9  # 九等奖：3+0 或 1+2 或 2+1 或 0+2
        
        return None  # 未中奖
    
    @staticmethod
    def _calculate_prize_amount(level: int, config: SuperLottoGame, draw: SuperLottoDraw, multiplier: int = 1) -> Decimal:
        """
        计算奖金金额
        """
        try:
            if level == 1:
                # 一等奖：奖池75%
                base_amount = draw.jackpot_amount * config.jackpot_allocation_rate
            elif level == 2:
                # 二等奖：奖池18%
                base_amount = draw.jackpot_amount * config.second_prize_allocation_rate
            elif level == 3:
                base_amount = config.third_prize_amount
            elif level == 4:
                base_amount = config.fourth_prize_amount
            elif level == 5:
                base_amount = config.fifth_prize_amount
            elif level == 6:
                base_amount = config.sixth_prize_amount
            elif level == 7:
                base_amount = config.seventh_prize_amount
            elif level == 8:
                base_amount = config.eighth_prize_amount
            elif level == 9:
                base_amount = config.ninth_prize_amount
            else:
                base_amount = Decimal('0.00')
            
            return base_amount * multiplier
            
        except Exception as e:
            logger.error(f"计算奖金失败: {str(e)}")
            return Decimal('0.00')
    
    @staticmethod
    def _award_prize(bet: SuperLottoBet, amount: Decimal):
        """
        派发奖金
        """
        try:
            with transaction.atomic():
                # 添加奖金到用户余额
                user_balance = bet.user.balance
                user_balance.add_balance(amount, 'available', f'大乐透中奖 {bet.draw.draw_number}期')
                
                # 创建中奖交易记录
                win_transaction = Transaction.objects.create(
                    user=bet.user,
                    type='WIN',
                    amount=amount,
                    fee=Decimal('0.00'),
                    actual_amount=amount,
                    status='COMPLETED',
                    reference_id=str(uuid.uuid4()),
                    description=f'大乐透中奖 {bet.draw.draw_number}期 {bet.winning_level}等奖',
                    metadata={
                        'game_type': '彩票',
                        'game_name': '大乐透',
                        'draw_number': bet.draw.draw_number,
                        'bet_id': str(bet.id),
                        'winning_level': bet.winning_level,
                        'winning_amount': float(amount),
                    }
                )
                
                bet.win_transaction_id = win_transaction.id
                bet.status = 'SETTLED'
                bet.save()
                
        except Exception as e:
            logger.error(f"派发奖金失败: {str(e)}")
    
    @staticmethod
    def _update_draw_statistics(draw: SuperLottoDraw, prize_stats: Dict, total_winning_amount: Decimal):
        """
        更新期次统计数据
        """
        try:
            # 计算销售统计
            bets = SuperLottoBet.objects.filter(draw=draw)
            total_bets = bets.count()
            total_bet_count = sum(bet.bet_count for bet in bets)
            total_sales = sum(bet.total_amount for bet in bets)
            
            # 计算利润
            profit = total_sales - total_winning_amount
            profit_rate = (profit / total_sales * 100) if total_sales > 0 else Decimal('0.00')
            
            # 用户统计
            unique_players = bets.values('user').distinct().count()
            avg_bet_amount = (total_sales / total_bets) if total_bets > 0 else Decimal('0.00')
            
            # 创建或更新统计记录
            stats, created = SuperLottoStatistics.objects.update_or_create(
                game=draw.game,
                draw=draw,
                defaults={
                    'total_bets': total_bets,
                    'total_bet_count': total_bet_count,
                    'total_sales_amount': total_sales,
                    'total_winners': sum(stats['count'] for stats in prize_stats.values()),
                    'total_winning_amount': total_winning_amount,
                    'first_prize_bets': prize_stats[1]['count'],
                    'first_prize_amount': prize_stats[1]['total_amount'],
                    'second_prize_bets': prize_stats[2]['count'],
                    'second_prize_amount': prize_stats[2]['total_amount'],
                    'third_prize_bets': prize_stats[3]['count'],
                    'third_prize_amount': prize_stats[3]['total_amount'],
                    'fourth_prize_bets': prize_stats[4]['count'],
                    'fourth_prize_amount': prize_stats[4]['total_amount'],
                    'fifth_prize_bets': prize_stats[5]['count'],
                    'fifth_prize_amount': prize_stats[5]['total_amount'],
                    'sixth_prize_bets': prize_stats[6]['count'],
                    'sixth_prize_amount': prize_stats[6]['total_amount'],
                    'seventh_prize_bets': prize_stats[7]['count'],
                    'seventh_prize_amount': prize_stats[7]['total_amount'],
                    'eighth_prize_bets': prize_stats[8]['count'],
                    'eighth_prize_amount': prize_stats[8]['total_amount'],
                    'ninth_prize_bets': prize_stats[9]['count'],
                    'ninth_prize_amount': prize_stats[9]['total_amount'],
                    'profit': profit,
                    'profit_rate': profit_rate,
                    'unique_players': unique_players,
                    'avg_bet_amount': avg_bet_amount,
                }
            )
            
            # 更新期次销售总额
            draw.total_sales = total_sales
            draw.save()
            
            logger.info(f"大乐透期次统计更新成功: {draw.draw_number}, 创建新记录: {created}")
            
        except Exception as e:
            logger.error(f"更新期次统计失败: {str(e)}")
    
    @staticmethod
    def create_next_draw() -> Dict[str, Any]:
        """
        创建下一期次
        """
        try:
            game = SuperLottoService.get_game()
            config = SuperLottoService.get_game_config()
            
            if not game or not config:
                return {'success': False, 'message': '游戏或配置不存在'}
            
            # 获取最新期次
            latest_draw = SuperLottoDraw.objects.filter(game=game).order_by('-draw_number').first()
            
            # 计算下一期次号码
            if latest_draw:
                current_number = int(latest_draw.draw_number)
                next_number = str(current_number + 1).zfill(5)
            else:
                # 第一期，使用当前年份+期次
                from datetime import date
                year = date.today().year
                next_number = f"{year}001"
            
            # 计算下一次开奖时间
            next_draw_time = SuperLottoService._calculate_next_draw_time(config)
            sales_end_time = next_draw_time - timedelta(minutes=config.sales_stop_minutes)
            
            # 计算奖池金额（累积未中出的奖池）
            jackpot_amount = Decimal('1000000.00')  # 基础奖池100万奈拉
            if latest_draw and latest_draw.first_prize_winners == 0:
                # 如果上期一等奖未中出，累积奖池
                jackpot_amount += latest_draw.jackpot_amount
            
            # 创建新期次
            new_draw = SuperLottoDraw.objects.create(
                game=game,
                draw_number=next_number,
                draw_time=next_draw_time,
                sales_end_time=sales_end_time,
                jackpot_amount=jackpot_amount,
                status='OPEN'
            )
            
            return {
                'success': True,
                'message': '新期次创建成功',
                'data': {
                    'draw_id': str(new_draw.id),
                    'draw_number': new_draw.draw_number,
                    'draw_time': new_draw.draw_time.isoformat(),
                    'sales_end_time': new_draw.sales_end_time.isoformat(),
                    'jackpot_amount': float(new_draw.jackpot_amount),
                }
            }
            
        except Exception as e:
            logger.error(f"创建新期次失败: {str(e)}")
            return {'success': False, 'message': f'创建失败: {str(e)}'}
    
    @staticmethod
    def _calculate_next_draw_time(config: SuperLottoGame) -> datetime:
        """
        计算下一次开奖时间
        """
        from datetime import datetime, timedelta
        
        now = timezone.now()
        draw_days = config.get_draw_days_list()  # [3, 6] 表示周三、周六
        draw_time = config.draw_time
        
        # 从今天开始查找下一个开奖日
        for i in range(7):  # 最多查找一周
            check_date = now + timedelta(days=i)
            weekday = check_date.weekday()  # 0=周一, 6=周日
            
            # 转换为开奖日格式（1=周一, 7=周日）
            draw_weekday = weekday + 1
            if draw_weekday == 7:
                draw_weekday = 0  # 周日为0
            
            if draw_weekday in draw_days:
                # 构造开奖时间
                draw_datetime = timezone.make_aware(
                    datetime.combine(check_date.date(), draw_time)
                )
                
                # 如果是今天，检查是否已过开奖时间
                if i == 0 and now >= draw_datetime:
                    continue  # 今天已过开奖时间，查找下一个开奖日
                
                return draw_datetime
        
        # 如果没找到，默认返回下周三
        next_week = now + timedelta(days=7)
        return timezone.make_aware(
            datetime.combine(next_week.date(), draw_time)
        )
    
    @staticmethod
    def close_draw_sales(draw_id: str) -> Dict[str, Any]:
        """
        停止期次销售
        """
        try:
            draw = SuperLottoDraw.objects.get(id=draw_id)
            
            if draw.status != 'OPEN':
                return {'success': False, 'message': '期次状态不正确'}
            
            draw.status = 'CLOSED'
            draw.save()
            
            return {
                'success': True,
                'message': '期次已停售',
                'data': {
                    'draw_number': draw.draw_number,
                    'status': draw.status
                }
            }
            
        except SuperLottoDraw.DoesNotExist:
            return {'success': False, 'message': '期次不存在'}
        except Exception as e:
            logger.error(f"停售失败: {str(e)}")
            return {'success': False, 'message': f'停售失败: {str(e)}'}