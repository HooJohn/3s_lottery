"""
11选5彩票游戏服务
"""

import random
import uuid
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Count, F, Q
from django.core.cache import cache

from apps.games.models import Game, Draw, BetType, Bet
from apps.finance.models import Transaction, UserBalance
from .models import (
    Lottery11x5Game, 
    Lottery11x5Bet, 
    Lottery11x5Result,
    Lottery11x5Trend,
    Lottery11x5HotCold,
    Lottery11x5UserNumber
)


class Lottery11x5Service:
    """
    11选5彩票游戏服务
    """
    
    @staticmethod
    def get_game():
        """
        获取11选5游戏
        """
        try:
            game = Game.objects.get(code='11x5', game_type='11选5')
            return game
        except Game.DoesNotExist:
            return None
    
    @staticmethod
    def get_game_config():
        """
        获取11选5游戏配置
        """
        game = Lottery11x5Service.get_game()
        if not game:
            return None
        
        try:
            config = Lottery11x5Game.objects.get(game=game)
            return config
        except Lottery11x5Game.DoesNotExist:
            return None
    
    @staticmethod
    def get_current_draw():
        """
        获取当前可投注的期数
        """
        config = Lottery11x5Service.get_game_config()
        if not config:
            return None
        
        return config.get_current_draw()
    
    @staticmethod
    def get_next_draw_time():
        """
        获取下一期开奖时间
        """
        config = Lottery11x5Service.get_game_config()
        if not config:
            return None
        
        return config.get_next_draw_time()
    
    @staticmethod
    def create_draws_for_today():
        """
        创建今日期数
        """
        config = Lottery11x5Service.get_game_config()
        if not config or not config.auto_create_draws:
            return []
        
        today = timezone.now().date()
        return config.create_draws_for_date(today)
    
    @staticmethod
    def create_draws_for_tomorrow():
        """
        创建明日期数
        """
        config = Lottery11x5Service.get_game_config()
        if not config or not config.auto_create_draws:
            return []
        
        tomorrow = timezone.now().date() + timedelta(days=1)
        return config.create_draws_for_date(tomorrow)
    
    @staticmethod
    def get_bet_types():
        """
        获取投注类型
        """
        game = Lottery11x5Service.get_game()
        if not game:
            return []
        
        return BetType.objects.filter(game=game, is_active=True).order_by('sort_order')
    
    @staticmethod
    def get_recent_results(limit: int = 10):
        """
        获取最近开奖结果
        """
        game = Lottery11x5Service.get_game()
        if not game:
            return []
        
        recent_draws = Draw.objects.filter(
            game=game,
            status='COMPLETED'
        ).order_by('-draw_time')[:limit]
        
        results = []
        for draw in recent_draws:
            try:
                result = draw.lottery11x5_result
                results.append({
                    'draw_number': draw.draw_number,
                    'draw_time': draw.draw_time,
                    'numbers': result.numbers,
                    'sum_value': result.sum_value,
                    'odd_count': result.odd_count,
                    'even_count': result.even_count,
                    'big_count': result.big_count,
                    'small_count': result.small_count,
                    'span_value': result.span_value,
                })
            except Lottery11x5Result.DoesNotExist:
                continue
        
        return results
    
    @staticmethod
    def get_hot_cold_numbers(period_type: int = 50):
        """
        获取冷热号码
        """
        game = Lottery11x5Service.get_game()
        if not game:
            return {}
        
        # 从缓存获取
        cache_key = f'lottery11x5_hot_cold_{period_type}'
        hot_cold = cache.get(cache_key)
        if hot_cold:
            return hot_cold
        
        # 从数据库获取
        hot_cold_numbers = Lottery11x5HotCold.objects.filter(
            game=game,
            period_type=period_type
        ).order_by('number')
        
        if not hot_cold_numbers.exists():
            # 如果没有数据，则计算并保存
            Lottery11x5Service.update_hot_cold_numbers()
            hot_cold_numbers = Lottery11x5HotCold.objects.filter(
                game=game,
                period_type=period_type
            ).order_by('number')
        
        # 格式化结果
        result = {
            'period_type': period_type,
            'numbers': []
        }
        
        for item in hot_cold_numbers:
            result['numbers'].append({
                'number': item.number,
                'frequency': item.frequency,
                'last_appearance': item.last_appearance,
                'is_hot': item.is_hot,
                'is_cold': item.is_cold,
            })
        
        # 缓存结果
        cache.set(cache_key, result, 3600)  # 缓存1小时
        
        return result
    
    @staticmethod
    def update_hot_cold_numbers():
        """
        更新冷热号码统计
        """
        game = Lottery11x5Service.get_game()
        if not game:
            return False
        
        # 获取最近的开奖结果
        recent_results = Lottery11x5Result.objects.filter(
            draw__game=game,
            draw__status='COMPLETED'
        ).order_by('-draw__draw_time')
        
        # 定义统计周期
        periods = [10, 30, 50, 100]
        
        # 对每个周期进行统计
        for period in periods:
            # 获取指定期数的结果
            period_results = recent_results[:period]
            if period_results.count() < period:
                continue  # 数据不足，跳过
            
            # 统计每个号码的出现次数
            number_counts = {i: 0 for i in range(1, 12)}  # 初始化1-11号码计数
            last_appearance = {i: period for i in range(1, 12)}  # 初始化最后出现期数
            
            for i, result in enumerate(period_results):
                for number in result.numbers:
                    number_counts[number] = number_counts.get(number, 0) + 1
                    if last_appearance[number] == period:  # 如果还没有记录过
                        last_appearance[number] = i  # 记录最后出现期数
            
            # 计算热号和冷号
            avg_frequency = period / 11 * 5  # 平均每个号码在period期内应该出现的次数
            hot_threshold = avg_frequency * 1.2  # 热号阈值
            cold_threshold = avg_frequency * 0.8  # 冷号阈值
            
            # 更新或创建统计记录
            for number in range(1, 12):
                frequency = number_counts[number]
                is_hot = frequency >= hot_threshold
                is_cold = frequency <= cold_threshold
                
                Lottery11x5HotCold.objects.update_or_create(
                    game=game,
                    period_type=period,
                    number=number,
                    defaults={
                        'frequency': frequency,
                        'last_appearance': last_appearance[number],
                        'is_hot': is_hot,
                        'is_cold': is_cold,
                    }
                )
        
        return True
    
    @staticmethod
    def generate_random_numbers(count: int = 5) -> List[int]:
        """
        生成随机号码
        """
        return random.sample(range(1, 12), count)
    
    @staticmethod
    def place_bet(user, draw_id: str, bet_type_id: str, numbers: List[int], 
                 amount: Decimal, bet_method: str, positions: List[int] = None, 
                 selected_count: int = 0, multiplier: int = 1) -> Dict[str, Any]:
        """
        投注
        """
        try:
            from .bet_calculator import Lottery11x5BetValidator, Lottery11x5BetCalculator
            
            # 获取游戏和期数
            draw = Draw.objects.get(id=draw_id)
            bet_type = BetType.objects.get(id=bet_type_id)
            game = draw.game
            
            # 检查期数是否可投注
            if not draw.is_open_for_betting():
                return {
                    'success': False,
                    'message': '当前期数已封盘或不可投注'
                }
            
            # 准备投注数据进行验证
            bet_data = {
                'draw_id': draw_id,
                'bet_type_id': bet_type_id,
                'numbers': numbers,
                'amount': amount,
                'bet_method': bet_method,
                'positions': positions,
                'selected_count': selected_count,
                'multiplier': multiplier,
            }
            
            # 验证投注请求
            validation_result = Lottery11x5BetValidator.validate_bet_request(bet_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'message': '; '.join(validation_result['errors'])
                }
            
            # 验证用户资格
            user_validation = Lottery11x5BetValidator.validate_user_eligibility(user, bet_data)
            if not user_validation['valid']:
                return {
                    'success': False,
                    'message': '; '.join(user_validation['errors'])
                }
            
            # 计算投注详情
            bet_details = Lottery11x5BetCalculator.calculate_bet_details(bet_data)
            
            # 验证投注限额
            bet_type_limits = {
                'min_bet': bet_type.min_bet,
                'max_bet': bet_type.max_bet,
                'max_payout': bet_type.max_payout,
            }
            
            limits_validation = Lottery11x5BetCalculator.validate_bet_limits(bet_details, bet_type_limits)
            if not limits_validation['valid']:
                return {
                    'success': False,
                    'message': '; '.join(limits_validation['errors'])
                }
            
            # 获取计算结果
            total_amount = Decimal(str(bet_details['total_amount']))
            multiple_count = bet_details['total_bet_count']
            is_multiple = bet_details['is_multiple']
            potential_payout = Decimal(str(bet_details['potential_payout']))
            
            # 检查用户余额
            try:
                balance = user.balance
                if balance.get_available_balance() < total_amount:
                    return {
                        'success': False,
                        'message': f'余额不足，需要 ₦{total_amount}，当前可用余额 ₦{balance.get_available_balance()}'
                    }
            except UserBalance.DoesNotExist:
                return {
                    'success': False,
                    'message': '用户余额信息不存在'
                }
            
            # 创建投注记录
            with transaction.atomic():
                # 扣除余额
                balance.deduct_balance(total_amount, 'available', f'投注 {game.name} {draw.draw_number}')
                
                # 创建交易记录
                bet_transaction = Transaction.objects.create(
                    user=user,
                    type='BET',
                    amount=total_amount,
                    fee=Decimal('0.00'),
                    actual_amount=total_amount,
                    status='COMPLETED',
                    reference_id=str(uuid.uuid4()),
                    description=f'投注 {game.name} {draw.draw_number}',
                    metadata={
                        'game_type': game.game_type,
                        'game_name': game.name,
                        'draw_number': draw.draw_number,
                        'bet_type': bet_type.name,
                        'bet_method': bet_method,
                        'numbers': numbers,
                        'positions': positions,
                        'selected_count': selected_count,
                        'is_multiple': is_multiple,
                        'multiple_count': multiple_count,
                        'multiplier': multiplier,
                        'bet_details': bet_details,
                    }
                )
                
                # 创建投注记录
                bet = Bet.objects.create(
                    user=user,
                    game=game,
                    draw=draw,
                    bet_type=bet_type,
                    numbers=numbers,
                    amount=amount,
                    odds=Decimal(str(bet_details['odds'])),
                    potential_payout=potential_payout,
                    transaction_id=bet_transaction.id
                )
                
                # 创建11选5投注详情
                lottery_bet = Lottery11x5Bet.objects.create(
                    bet=bet,
                    bet_method=bet_method,
                    positions=positions or [],
                    selected_count=selected_count,
                    is_multiple=is_multiple,
                    multiple_count=multiple_count
                )
                
                # 更新期数投注统计
                draw.total_bets = F('total_bets') + multiple_count
                draw.total_amount = F('total_amount') + total_amount
                draw.save(update_fields=['total_bets', 'total_amount'])
                
                return {
                    'success': True,
                    'message': '投注成功',
                    'data': {
                        'bet_id': str(bet.id),
                        'draw_number': draw.draw_number,
                        'numbers': numbers,
                        'amount': float(amount),
                        'total_amount': float(total_amount),
                        'multiple_count': multiple_count,
                        'multiplier': multiplier,
                        'potential_payout': float(potential_payout),
                        'odds': bet_details['odds'],
                        'win_probability': bet_details['win_probability'],
                        'bet_time': bet.bet_time.isoformat(),
                        'bet_details': bet_details,
                    }
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'投注失败: {str(e)}'
            }
    
    @staticmethod
    def validate_numbers(numbers: List[int], bet_method: str, positions: List[int] = None, 
                        selected_count: int = 0) -> bool:
        """
        验证投注号码
        """
        # 检查号码范围
        if not all(1 <= num <= 11 for num in numbers):
            return False
        
        # 检查号码重复
        if len(numbers) != len(set(numbers)):
            return False
        
        if bet_method == 'POSITION':
            # 定位胆玩法
            if not positions or len(positions) == 0:
                return False
            
            # 检查位置范围
            if not all(1 <= pos <= 5 for pos in positions):
                return False
            
            # 每个位置只能选择一个号码
            if len(numbers) != len(positions):
                return False
                
        elif bet_method == 'ANY':
            # 任选玩法
            if selected_count < 1 or selected_count > 5:
                return False
            
            # 选择的号码数量必须大于等于任选数量
            if len(numbers) < selected_count:
                return False
                
        elif bet_method == 'GROUP':
            # 组选玩法（暂时简单验证）
            if len(numbers) < 2:
                return False
        
        return True
    
    @staticmethod
    def draw_lottery(draw_id: str, force_numbers: List[int] = None) -> Dict[str, Any]:
        """
        开奖
        """
        try:
            from .draw_engine import Lottery11x5DrawEngine, Lottery11x5DrawValidator, Lottery11x5ProfitController
            
            draw = Draw.objects.get(id=draw_id)
            
            # 验证开奖条件
            validation_result = Lottery11x5DrawValidator.validate_draw_conditions(draw_id)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'message': '; '.join(validation_result['errors']),
                    'validation_errors': validation_result['errors']
                }
            
            # 记录警告信息
            if validation_result['warnings']:
                logger.warning(f"开奖警告 {draw.draw_number}: {'; '.join(validation_result['warnings'])}")
            
            # 生成开奖号码
            if force_numbers:
                # 强制指定号码（测试或特殊情况）
                numbers_validation = Lottery11x5DrawValidator.validate_winning_numbers(force_numbers)
                if not numbers_validation['valid']:
                    return {
                        'success': False,
                        'message': f'指定号码无效: {"; ".join(numbers_validation["errors"])}'
                    }
                
                winning_numbers = force_numbers
                draw_result = {
                    'success': True,
                    'winning_numbers': winning_numbers,
                    'statistics': {},
                    'proof': {'forced': True},
                    'timestamp': timezone.now().isoformat(),
                }
            else:
                # 使用开奖引擎生成号码
                draw_engine = Lottery11x5DrawEngine()
                draw_result = draw_engine.generate_winning_numbers(draw_id, draw.draw_time)
                
                if not draw_result['success']:
                    return {
                        'success': False,
                        'message': f'生成开奖号码失败: {draw_result.get("error", "未知错误")}'
                    }
                
                winning_numbers = draw_result['winning_numbers']
            
            # 分析盈利能力
            profit_controller = Lottery11x5ProfitController()
            profit_analysis = profit_controller.analyze_draw_profitability(draw_id, winning_numbers)
            
            # 记录盈利分析结果
            logger.info(f"期次 {draw.draw_number} 盈利分析: 利润率 {profit_analysis.get('profit_rate', 0):.2%}")
            
            with transaction.atomic():
                # 更新期数状态和结果
                draw.status = 'COMPLETED'
                
                # 获取统计信息
                statistics = draw_result.get('statistics', {})
                
                draw.result = {
                    'numbers': winning_numbers,
                    'sum_value': statistics.get('sum_value', sum(winning_numbers)),
                    'odd_count': statistics.get('odd_count', sum(1 for num in winning_numbers if num % 2 == 1)),
                    'even_count': statistics.get('even_count', sum(1 for num in winning_numbers if num % 2 == 0)),
                    'big_count': statistics.get('big_count', sum(1 for num in winning_numbers if num > 5)),
                    'small_count': statistics.get('small_count', sum(1 for num in winning_numbers if num <= 5)),
                    'span_value': statistics.get('span_value', max(winning_numbers) - min(winning_numbers)),
                    'statistics': statistics,
                    'proof': draw_result.get('proof', {}),
                    'profit_analysis': profit_analysis,
                }
                draw.winning_numbers = ','.join(map(str, winning_numbers))
                draw.save()
                
                # 创建开奖结果详情
                lottery_result = Lottery11x5Result.objects.create(
                    draw=draw,
                    numbers=winning_numbers,
                    sum_value=draw.result['sum_value'],
                    odd_count=draw.result['odd_count'],
                    even_count=draw.result['even_count'],
                    big_count=draw.result['big_count'],
                    small_count=draw.result['small_count'],
                    span_value=draw.result['span_value']
                )
                
                # 结算投注
                settlement_result = Lottery11x5Service.settle_bets(draw, winning_numbers)
                total_payout = settlement_result['total_payout']
                total_winners = settlement_result['total_winners']
                
                # 更新期数统计
                draw.total_payout = total_payout
                draw.profit = draw.total_amount - total_payout
                draw.save(update_fields=['total_payout', 'profit'])
                
                # 创建游戏结果记录
                GameResult.objects.create(
                    game=draw.game,
                    draw=draw,
                    result_data=draw.result,
                    winning_numbers=draw.winning_numbers,
                    total_bets=draw.total_bets,
                    total_winners=total_winners,
                    total_amount=draw.total_amount,
                    total_payout=total_payout,
                    profit=draw.profit,
                    profit_rate=(draw.profit / draw.total_amount * 100) if draw.total_amount > 0 else Decimal('0.00')
                )
                
                # 更新走势数据
                Lottery11x5Service.update_trend_data(draw, winning_numbers)
                
                # 更新冷热号码统计
                Lottery11x5Service.update_hot_cold_numbers()
                
                # 发送开奖通知
                from .tasks import send_draw_notifications
                send_draw_notifications.delay(draw_id)
                
                return {
                    'success': True,
                    'message': '开奖成功',
                    'data': {
                        'draw_number': draw.draw_number,
                        'winning_numbers': winning_numbers,
                        'statistics': statistics,
                        'total_bets': draw.total_bets,
                        'total_amount': float(draw.total_amount),
                        'total_payout': float(total_payout),
                        'total_winners': total_winners,
                        'profit': float(draw.profit),
                        'profit_rate': float((draw.profit / draw.total_amount * 100) if draw.total_amount > 0 else 0),
                        'profit_analysis': profit_analysis,
                        'proof': draw_result.get('proof', {}),
                        'settlement_details': settlement_result,
                    }
                }
                
        except Exception as e:
            logger.error(f"开奖失败 {draw_id}: {str(e)}")
            return {
                'success': False,
                'message': f'开奖失败: {str(e)}'
            }
    
    @staticmethod
    def settle_bets(draw: Draw, winning_numbers: List[int]) -> Dict[str, Any]:
        """
        结算投注
        """
        import logging
        logger = logging.getLogger(__name__)
        
        total_payout = Decimal('0.00')
        total_winners = 0
        settlement_details = {
            'total_bets': 0,
            'winning_bets': 0,
            'losing_bets': 0,
            'error_bets': 0,
            'bet_type_stats': {},
            'user_wins': [],
            'errors': []
        }
        
        # 获取该期所有投注
        bets = Bet.objects.filter(draw=draw, status='PENDING').select_related('user', 'bet_type')
        settlement_details['total_bets'] = bets.count()
        
        if not bets.exists():
            logger.info(f"期次 {draw.draw_number} 没有待结算的投注")
            return {
                'total_payout': total_payout,
                'total_winners': total_winners,
                'settlement_details': settlement_details
            }
        
        logger.info(f"开始结算期次 {draw.draw_number}，共 {bets.count()} 注投注")
        
        for bet in bets:
            try:
                # 获取投注详情
                lottery_bet = bet.lottery11x5_detail
                
                # 检查是否中奖
                is_win, win_amount = Lottery11x5Service.check_win(
                    bet_numbers=bet.numbers, 
                    winning_numbers=winning_numbers, 
                    bet_method=lottery_bet.bet_method,
                    positions=lottery_bet.positions,
                    selected_count=lottery_bet.selected_count,
                    odds=bet.odds,
                    bet_amount=bet.amount,
                    multiple_count=lottery_bet.multiple_count
                )
                
                # 统计投注类型
                bet_type_key = f"{bet.bet_type.name}_{lottery_bet.bet_method}"
                if bet_type_key not in settlement_details['bet_type_stats']:
                    settlement_details['bet_type_stats'][bet_type_key] = {
                        'total_bets': 0,
                        'total_amount': Decimal('0.00'),
                        'winning_bets': 0,
                        'total_payout': Decimal('0.00')
                    }
                
                stats = settlement_details['bet_type_stats'][bet_type_key]
                stats['total_bets'] += 1
                stats['total_amount'] += bet.amount * lottery_bet.multiple_count
                
                if is_win and win_amount > 0:
                    # 中奖处理
                    bet.status = 'WON'
                    bet.payout = win_amount
                    bet.result = {
                        'is_win': True,
                        'win_amount': float(win_amount),
                        'winning_numbers': winning_numbers,
                        'matched_numbers': list(set(bet.numbers) & set(winning_numbers)),
                        'bet_method': lottery_bet.bet_method,
                        'positions': lottery_bet.positions,
                        'selected_count': lottery_bet.selected_count,
                    }
                    
                    # 派发奖金到用户余额
                    user_balance = bet.user.balance
                    user_balance.add_balance(win_amount, 'available', f'11选5中奖 {draw.draw_number}')
                    
                    # 创建中奖交易记录
                    win_transaction = Transaction.objects.create(
                        user=bet.user,
                        type='WIN',
                        amount=win_amount,
                        fee=Decimal('0.00'),
                        actual_amount=win_amount,
                        status='COMPLETED',
                        reference_id=str(uuid.uuid4()),
                        description=f'11选5中奖 {draw.draw_number}',
                        metadata={
                            'game_type': draw.game.game_type,
                            'game_name': draw.game.name,
                            'draw_number': draw.draw_number,
                            'bet_id': str(bet.id),
                            'winning_numbers': winning_numbers,
                            'bet_numbers': bet.numbers,
                            'bet_method': lottery_bet.bet_method,
                            'win_amount': float(win_amount),
                        }
                    )
                    
                    bet.win_transaction_id = win_transaction.id
                    total_payout += win_amount
                    total_winners += 1
                    settlement_details['winning_bets'] += 1
                    
                    # 统计中奖信息
                    stats['winning_bets'] += 1
                    stats['total_payout'] += win_amount
                    
                    # 记录用户中奖信息
                    settlement_details['user_wins'].append({
                        'user_id': str(bet.user.id),
                        'user_phone': bet.user.phone,
                        'bet_id': str(bet.id),
                        'bet_amount': float(bet.amount * lottery_bet.multiple_count),
                        'win_amount': float(win_amount),
                        'bet_type': bet.bet_type.name,
                        'bet_method': lottery_bet.bet_method,
                        'numbers': bet.numbers,
                        'odds': float(bet.odds),
                    })
                    
                    logger.info(f"用户 {bet.user.phone} 中奖: 投注 ₦{bet.amount * lottery_bet.multiple_count}, 中奖 ₦{win_amount}")
                    
                else:
                    # 未中奖
                    bet.status = 'LOST'
                    bet.payout = Decimal('0.00')
                    bet.result = {
                        'is_win': False,
                        'win_amount': 0,
                        'winning_numbers': winning_numbers,
                        'matched_numbers': list(set(bet.numbers) & set(winning_numbers)),
                        'bet_method': lottery_bet.bet_method,
                        'positions': lottery_bet.positions,
                        'selected_count': lottery_bet.selected_count,
                    }
                    
                    settlement_details['losing_bets'] += 1
                
                bet.settled_at = timezone.now()
                bet.save()
                
            except Exception as e:
                # 记录错误但继续处理其他投注
                error_msg = f"结算投注 {bet.id} 时出错: {str(e)}"
                logger.error(error_msg)
                settlement_details['errors'].append(error_msg)
                settlement_details['error_bets'] += 1
                continue
        
        # 计算各投注类型的盈利率
        for bet_type_key, stats in settlement_details['bet_type_stats'].items():
            if stats['total_amount'] > 0:
                profit = stats['total_amount'] - stats['total_payout']
                profit_rate = (profit / stats['total_amount']) * 100
                stats['profit'] = profit
                stats['profit_rate'] = profit_rate
            else:
                stats['profit'] = Decimal('0.00')
                stats['profit_rate'] = Decimal('0.00')
        
        logger.info(f"期次 {draw.draw_number} 结算完成: 总投注 {settlement_details['total_bets']} 注, "
                   f"中奖 {total_winners} 注, 派彩 ₦{total_payout}")
        
        return {
            'total_payout': total_payout,
            'total_winners': total_winners,
            'settlement_details': settlement_details
        }
    
    @staticmethod
    def check_win(bet_numbers: List[int], winning_numbers: List[int], bet_method: str,
                 positions: List[int] = None, selected_count: int = 0, odds: Decimal = None,
                 bet_amount: Decimal = None, multiple_count: int = 1) -> Tuple[bool, Decimal]:
        """
        检查是否中奖并计算奖金
        """
        if bet_method == 'POSITION':
            # 定位胆玩法：检查指定位置的号码是否匹配
            if not positions:
                return False, Decimal('0.00')
            
            win_positions = 0
            for i, pos in enumerate(positions):
                if pos <= len(winning_numbers) and bet_numbers[i] == winning_numbers[pos - 1]:
                    win_positions += 1
            
            if win_positions > 0:
                # 按中奖位置数计算奖金
                win_amount = bet_amount * odds * win_positions * multiple_count
                return True, win_amount
            
        elif bet_method == 'ANY':
            # 任选玩法：检查选中的号码有多少个在开奖号码中
            matched_count = len(set(bet_numbers) & set(winning_numbers))
            
            if matched_count >= selected_count:
                # 中奖，计算奖金
                win_amount = bet_amount * odds * multiple_count
                return True, win_amount
        
        elif bet_method == 'GROUP':
            # 组选玩法（简化实现）
            matched_count = len(set(bet_numbers) & set(winning_numbers))
            if matched_count >= len(bet_numbers):
                win_amount = bet_amount * odds * multiple_count
                return True, win_amount
        
        return False, Decimal('0.00')
    
    @staticmethod
    def update_trend_data(draw: Draw, winning_numbers: List[int]):
        """
        更新走势数据
        """
        try:
            # 计算位置号码
            positions = {}
            for i, number in enumerate(winning_numbers):
                positions[str(i + 1)] = number
            
            # 计算统计数据
            sum_value = sum(winning_numbers)
            odd_count = sum(1 for num in winning_numbers if num % 2 == 1)
            even_count = 5 - odd_count
            big_count = sum(1 for num in winning_numbers if num > 5)
            small_count = 5 - big_count
            
            # 创建走势记录
            Lottery11x5Trend.objects.create(
                game=draw.game,
                date=draw.draw_time.date(),
                draw_number=draw.draw_number,
                numbers=winning_numbers,
                positions=positions,
                sum_value=sum_value,
                odd_even=f"{odd_count}:{even_count}",
                big_small=f"{big_count}:{small_count}"
            )
            
        except Exception as e:
            print(f"更新走势数据时出错: {str(e)}")
    
    @staticmethod
    def get_user_bet_history(user, limit: int = 20, status: str = None):
        """
        获取用户投注历史
        """
        game = Lottery11x5Service.get_game()
        if not game:
            return []
        
        queryset = Bet.objects.filter(
            user=user,
            game=game
        ).select_related('draw', 'bet_type').order_by('-bet_time')
        
        if status:
            queryset = queryset.filter(status=status)
        
        bets = queryset[:limit]
        
        result = []
        for bet in bets:
            try:
                lottery_bet = bet.lottery11x5_detail
                result.append({
                    'bet_id': str(bet.id),
                    'draw_number': bet.draw.draw_number,
                    'draw_time': bet.draw.draw_time,
                    'bet_type': bet.bet_type.name,
                    'bet_method': lottery_bet.get_bet_method_display(),
                    'numbers': bet.numbers,
                    'positions': lottery_bet.positions,
                    'amount': float(bet.amount),
                    'multiple_count': lottery_bet.multiple_count,
                    'total_amount': float(bet.amount * lottery_bet.multiple_count),
                    'odds': float(bet.odds),
                    'potential_payout': float(bet.potential_payout),
                    'status': bet.get_status_display(),
                    'payout': float(bet.payout),
                    'bet_time': bet.bet_time,
                    'settled_at': bet.settled_at,
                    'result': bet.result,
                })
            except Lottery11x5Bet.DoesNotExist:
                continue
        
        return result


class Lottery11x5DrawService:
    """
    11选5期次管理服务
    """
    
    @staticmethod
    def create_daily_draws():
        """
        创建每日期次
        """
        config = Lottery11x5Service.get_game_config()
        if not config:
            return False
        
        # 创建今日和明日的期次
        today_draws = Lottery11x5Service.create_draws_for_today()
        tomorrow_draws = Lottery11x5Service.create_draws_for_tomorrow()
        
        return len(today_draws) + len(tomorrow_draws) > 0
    
    @staticmethod
    def close_expired_draws():
        """
        关闭过期的期数
        """
        now = timezone.now()
        
        # 查找需要关闭的期数
        expired_draws = Draw.objects.filter(
            game__game_type='11选5',
            status='OPEN',
            close_time__lte=now
        )
        
        count = 0
        for draw in expired_draws:
            draw.status = 'CLOSED'
            draw.save(update_fields=['status'])
            count += 1
        
        return count
    
    @staticmethod
    def auto_draw_lottery():
        """
        自动开奖
        """
        config = Lottery11x5Service.get_game_config()
        if not config or not config.auto_draw_results:
            return []
        
        now = timezone.now()
        
        # 查找需要开奖的期数
        draws_to_draw = Draw.objects.filter(
            game__game_type='11选5',
            status='CLOSED',
            draw_time__lte=now
        )
        
        results = []
        for draw in draws_to_draw:
            result = Lottery11x5Service.draw_lottery(str(draw.id))
            results.append({
                'draw_number': draw.draw_number,
                'result': result
            })
        
        return results
    
    @staticmethod
    def get_draw_countdown(draw_id: str = None):
        """
        获取开奖倒计时
        """
        if draw_id:
            try:
                draw = Draw.objects.get(id=draw_id)
            except Draw.DoesNotExist:
                return None
        else:
            draw = Lottery11x5Service.get_current_draw()
        
        if not draw:
            return None
        
        now = timezone.now()
        
        # 计算距离封盘时间
        time_until_close = draw.time_until_close()
        
        # 计算距离开奖时间
        time_until_draw = draw.time_until_draw()
        
        return {
            'draw_number': draw.draw_number,
            'draw_time': draw.draw_time,
            'close_time': draw.close_time,
            'status': draw.status,
            'is_open_for_betting': draw.is_open_for_betting(),
            'time_until_close': int(time_until_close),
            'time_until_draw': int(time_until_draw),
            'close_countdown': {
                'hours': int(time_until_close // 3600),
                'minutes': int((time_until_close % 3600) // 60),
                'seconds': int(time_until_close % 60),
            } if time_until_close > 0 else None,
            'draw_countdown': {
                'hours': int(time_until_draw // 3600),
                'minutes': int((time_until_draw % 3600) // 60),
                'seconds': int(time_until_draw % 60),
            } if time_until_draw > 0 else None,
        }