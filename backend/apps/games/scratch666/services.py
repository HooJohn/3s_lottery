"""
666刮刮乐游戏服务
"""

import random
import uuid
from typing import Dict, List, Any, Optional
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache

from apps.games.models import Game
from apps.finance.models import Transaction, UserBalance
from .models import Scratch666Game, ScratchCard, ScratchStatistics, UserScratchPreference


class Scratch666Service:
    """
    666刮刮乐游戏服务
    """
    
    @staticmethod
    def get_game():
        """
        获取666刮刮乐游戏
        """
        try:
            game = Game.objects.get(code='scratch666', game_type='刮刮乐')
            return game
        except Game.DoesNotExist:
            return None
    
    @staticmethod
    def get_game_config():
        """
        获取666刮刮乐游戏配置
        """
        game = Scratch666Service.get_game()
        if not game:
            return None
        
        try:
            config = Scratch666Game.objects.get(game=game)
            return config
        except Scratch666Game.DoesNotExist:
            return None
    
    @staticmethod
    def purchase_card(user) -> Dict[str, Any]:
        """
        购买刮刮乐卡片
        """
        try:
            config = Scratch666Service.get_game_config()
            if not config:
                return {
                    'success': False,
                    'message': '游戏配置不存在'
                }
            
            # 检查用户余额
            try:
                balance = user.balance
                if balance.get_available_balance() < config.card_price:
                    return {
                        'success': False,
                        'message': f'余额不足，需要 ₦{config.card_price}，当前可用余额 ₦{balance.get_available_balance()}'
                    }
            except UserBalance.DoesNotExist:
                return {
                    'success': False,
                    'message': '用户余额信息不存在'
                }
            
            with transaction.atomic():
                # 扣除余额
                balance.deduct_balance(config.card_price, 'available', f'购买刮刮乐 {config.game.name}')
                
                # 创建购买交易记录
                purchase_transaction = Transaction.objects.create(
                    user=user,
                    type='BET',  # 刮刮乐购买也算作投注
                    amount=config.card_price,
                    fee=Decimal('0.00'),
                    actual_amount=config.card_price,
                    status='COMPLETED',
                    reference_id=str(uuid.uuid4()),
                    description=f'购买刮刮乐 {config.game.name}',
                    metadata={
                        'game_type': config.game.game_type,
                        'game_name': config.game.name,
                        'card_type': '666',
                        'card_price': float(config.card_price),
                    }
                )
                
                # 生成刮刮乐卡片
                card = Scratch666Service._generate_card(user, config.game, config, purchase_transaction.id)
                
                # 更新用户偏好统计
                Scratch666Service._update_user_stats(user, config.card_price)
                
                return {
                    'success': True,
                    'message': '购买成功',
                    'data': {
                        'card_id': str(card.id),
                        'card_type': card.card_type,
                        'price': float(card.price),
                        'areas': card.areas,
                        'purchased_at': card.purchased_at.isoformat(),
                        'balance_after': float(balance.get_available_balance()),
                    }
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'购买失败: {str(e)}'
            }
    
    @staticmethod
    def _generate_card(user, game: Game, config: Scratch666Game, transaction_id: uuid.UUID) -> ScratchCard:
        """
        生成刮刮乐卡片
        """
        # 生成9个刮奖区域
        areas = []
        for i in range(config.scratch_areas):
            content = Scratch666Service._generate_area_content(config)
            areas.append({
                'index': i,
                'content': content,
                'scratched': False,
                'win_amount': Scratch666Service._calculate_area_win_amount(content, config)
            })
        
        # 创建卡片
        card = ScratchCard.objects.create(
            user=user,
            game=game,
            card_type='666',
            price=config.card_price,
            areas=areas,
            purchase_transaction_id=transaction_id
        )
        
        return card
    
    @staticmethod
    def _generate_area_content(config: Scratch666Game) -> str:
        """
        生成区域内容
        """
        # 根据概率生成内容
        rand = random.random()
        
        if rand < float(config.win_probability_666):
            return '666'
        elif rand < float(config.win_probability_666) + float(config.win_probability_66):
            return '66'
        elif rand < float(config.win_probability_666) + float(config.win_probability_66) + float(config.win_probability_6):
            return '6'
        else:
            # 生成其他随机内容（不中奖）
            other_contents = ['1', '2', '3', '4', '5', '7', '8', '9', '0', 'X', 'O']
            return random.choice(other_contents)
    
    @staticmethod
    def _calculate_area_win_amount(content: str, config: Scratch666Game) -> float:
        """
        计算区域中奖金额
        """
        if content == '666':
            return float(config.base_amount * config.multiplier_666)
        elif content == '66':
            return float(config.base_amount * config.multiplier_66)
        elif content == '6':
            return float(config.base_amount * config.multiplier_6)
        else:
            return 0.0
    
    @staticmethod
    def scratch_area(user, card_id: str, area_index: int) -> Dict[str, Any]:
        """
        刮开指定区域
        """
        try:
            card = ScratchCard.objects.get(id=card_id, user=user)
            
            if card.status != 'ACTIVE':
                return {
                    'success': False,
                    'message': '卡片已刮开或已过期'
                }
            
            if area_index < 0 or area_index >= len(card.areas):
                return {
                    'success': False,
                    'message': '无效的区域索引'
                }
            
            if card.areas[area_index]['scratched']:
                return {
                    'success': False,
                    'message': '该区域已经刮开'
                }
            
            # 刮开区域
            card.scratch_area(area_index)
            
            # 检查是否完成刮奖
            progress = card.get_scratch_progress()
            
            result = {
                'success': True,
                'message': '刮奖成功',
                'data': {
                    'card_id': str(card.id),
                    'area_index': area_index,
                    'area_content': card.areas[area_index]['content'],
                    'area_win_amount': card.areas[area_index]['win_amount'],
                    'progress': progress,
                    'is_complete': progress['is_complete'],
                }
            }
            
            # 如果刮奖完成，处理中奖
            if progress['is_complete']:
                win_result = Scratch666Service._process_card_completion(card)
                result['data']['completion_result'] = win_result
            
            return result
            
        except ScratchCard.DoesNotExist:
            return {
                'success': False,
                'message': '卡片不存在或不属于当前用户'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'刮奖失败: {str(e)}'
            }
    
    @staticmethod
    def scratch_all(user, card_id: str) -> Dict[str, Any]:
        """
        刮开所有区域
        """
        try:
            card = ScratchCard.objects.get(id=card_id, user=user)
            
            if card.status != 'ACTIVE':
                return {
                    'success': False,
                    'message': '卡片已刮开或已过期'
                }
            
            # 刮开所有区域
            card.scratch_all()
            
            # 处理中奖
            win_result = Scratch666Service._process_card_completion(card)
            
            return {
                'success': True,
                'message': '刮奖完成',
                'data': {
                    'card_id': str(card.id),
                    'areas': card.areas,
                    'total_winnings': float(card.total_winnings),
                    'is_winner': card.is_winner,
                    'win_details': card.win_details,
                    'completion_result': win_result,
                }
            }
            
        except ScratchCard.DoesNotExist:
            return {
                'success': False,
                'message': '卡片不存在或不属于当前用户'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'刮奖失败: {str(e)}'
            }
    
    @staticmethod
    def _process_card_completion(card: ScratchCard) -> Dict[str, Any]:
        """
        处理卡片完成刮奖
        """
        if not card.is_winner or card.total_winnings <= 0:
            return {
                'is_winner': False,
                'message': '很遗憾，本次未中奖'
            }
        
        try:
            with transaction.atomic():
                # 派发奖金到用户余额
                user_balance = card.user.balance
                user_balance.add_balance(card.total_winnings, 'available', f'刮刮乐中奖 {card.card_type}')
                
                # 创建中奖交易记录
                win_transaction = Transaction.objects.create(
                    user=card.user,
                    type='WIN',
                    amount=card.total_winnings,
                    fee=Decimal('0.00'),
                    actual_amount=card.total_winnings,
                    status='COMPLETED',
                    reference_id=str(uuid.uuid4()),
                    description=f'刮刮乐中奖 {card.card_type}',
                    metadata={
                        'game_type': card.game.game_type,
                        'game_name': card.game.name,
                        'card_id': str(card.id),
                        'card_type': card.card_type,
                        'win_details': card.win_details,
                    }
                )
                
                card.win_transaction_id = win_transaction.id
                card.save()
                
                # 更新用户统计
                Scratch666Service._update_user_win_stats(card.user, card.total_winnings)
                
                return {
                    'is_winner': True,
                    'message': f'恭喜中奖 ₦{card.total_winnings}！',
                    'win_amount': float(card.total_winnings),
                    'win_details': card.win_details,
                    'balance_after': float(user_balance.get_available_balance()),
                }
                
        except Exception as e:
            return {
                'is_winner': True,
                'message': f'中奖处理失败: {str(e)}',
                'win_amount': float(card.total_winnings),
            }
    
    @staticmethod
    def _update_user_stats(user, amount_spent: Decimal):
        """
        更新用户统计
        """
        preference, created = UserScratchPreference.objects.get_or_create(
            user=user,
            defaults={
                'total_cards_purchased': 0,
                'total_amount_spent': Decimal('0.00'),
                'total_winnings': Decimal('0.00'),
                'biggest_win': Decimal('0.00'),
            }
        )
        
        preference.total_cards_purchased += 1
        preference.total_amount_spent += amount_spent
        preference.save()
    
    @staticmethod
    def _update_user_win_stats(user, win_amount: Decimal):
        """
        更新用户中奖统计
        """
        try:
            preference = user.scratch_preference
            preference.total_winnings += win_amount
            if win_amount > preference.biggest_win:
                preference.biggest_win = win_amount
            preference.save()
        except UserScratchPreference.DoesNotExist:
            pass
    
    @staticmethod
    def get_user_cards(user, limit: int = 20, status: str = None) -> List[Dict[str, Any]]:
        """
        获取用户的刮刮乐卡片
        """
        queryset = ScratchCard.objects.filter(user=user)
        
        if status:
            queryset = queryset.filter(status=status)
        
        cards = queryset.order_by('-purchased_at')[:limit]
        
        result = []
        for card in cards:
            result.append({
                'card_id': str(card.id),
                'card_type': card.card_type,
                'price': float(card.price),
                'status': card.status,
                'areas': card.areas,
                'total_winnings': float(card.total_winnings),
                'is_winner': card.is_winner,
                'win_details': card.win_details,
                'purchased_at': card.purchased_at,
                'scratched_at': card.scratched_at,
                'progress': card.get_scratch_progress(),
            })
        
        return result
    
    @staticmethod
    def get_user_statistics(user) -> Dict[str, Any]:
        """
        获取用户统计信息
        """
        try:
            preference = user.scratch_preference
            
            return {
                'total_cards_purchased': preference.total_cards_purchased,
                'total_amount_spent': float(preference.total_amount_spent),
                'total_winnings': float(preference.total_winnings),
                'biggest_win': float(preference.biggest_win),
                'win_rate': preference.get_win_rate(),
                'roi': preference.get_roi(),
                'net_result': float(preference.total_winnings - preference.total_amount_spent),
                'preferences': {
                    'sound_enabled': preference.sound_enabled,
                    'music_enabled': preference.music_enabled,
                    'auto_scratch_enabled': preference.auto_scratch_enabled,
                    'auto_scratch_count': preference.auto_scratch_count,
                    'auto_scratch_stop_on_win': preference.auto_scratch_stop_on_win,
                }
            }
            
        except UserScratchPreference.DoesNotExist:
            return {
                'total_cards_purchased': 0,
                'total_amount_spent': 0.0,
                'total_winnings': 0.0,
                'biggest_win': 0.0,
                'win_rate': 0.0,
                'roi': 0.0,
                'net_result': 0.0,
                'preferences': {
                    'sound_enabled': True,
                    'music_enabled': True,
                    'auto_scratch_enabled': False,
                    'auto_scratch_count': 10,
                    'auto_scratch_stop_on_win': True,
                }
            }
    
    @staticmethod
    def update_user_preferences(user, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新用户偏好设置
        """
        try:
            preference, created = UserScratchPreference.objects.get_or_create(
                user=user,
                defaults={
                    'total_cards_purchased': 0,
                    'total_amount_spent': Decimal('0.00'),
                    'total_winnings': Decimal('0.00'),
                    'biggest_win': Decimal('0.00'),
                }
            )
            
            # 更新偏好设置
            if 'sound_enabled' in preferences:
                preference.sound_enabled = preferences['sound_enabled']
            if 'music_enabled' in preferences:
                preference.music_enabled = preferences['music_enabled']
            if 'auto_scratch_enabled' in preferences:
                preference.auto_scratch_enabled = preferences['auto_scratch_enabled']
            if 'auto_scratch_count' in preferences:
                preference.auto_scratch_count = min(max(preferences['auto_scratch_count'], 1), 100)
            if 'auto_scratch_stop_on_win' in preferences:
                preference.auto_scratch_stop_on_win = preferences['auto_scratch_stop_on_win']
            
            preference.save()
            
            return {
                'success': True,
                'message': '偏好设置更新成功',
                'preferences': {
                    'sound_enabled': preference.sound_enabled,
                    'music_enabled': preference.music_enabled,
                    'auto_scratch_enabled': preference.auto_scratch_enabled,
                    'auto_scratch_count': preference.auto_scratch_count,
                    'auto_scratch_stop_on_win': preference.auto_scratch_stop_on_win,
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'更新偏好设置失败: {str(e)}'
            }  
  @staticmethod
    def auto_scratch(user, count: int = 10, stop_on_win: bool = True) -> Dict[str, Any]:
        """
        自动连刮功能
        """
        try:
            config = Scratch666Service.get_game_config()
            if not config or not config.enable_auto_scratch:
                return {
                    'success': False,
                    'message': '自动连刮功能未启用'
                }
            
            # 限制连刮次数
            count = min(count, config.max_auto_scratch)
            
            # 检查用户余额
            balance = user.balance
            total_cost = config.card_price * count
            
            if balance.get_available_balance() < total_cost:
                # 计算能购买的最大数量
                max_affordable = int(balance.get_available_balance() / config.card_price)
                if max_affordable == 0:
                    return {
                        'success': False,
                        'message': '余额不足，无法购买刮刮乐'
                    }
                count = max_affordable
            
            results = []
            total_spent = Decimal('0.00')
            total_won = Decimal('0.00')
            cards_purchased = 0
            winning_cards = 0
            
            for i in range(count):
                # 购买卡片
                purchase_result = Scratch666Service.purchase_card(user)
                
                if not purchase_result['success']:
                    break
                
                card_id = purchase_result['data']['card_id']
                cards_purchased += 1
                total_spent += config.card_price
                
                # 自动刮开所有区域
                scratch_result = Scratch666Service.scratch_all(user, card_id)
                
                if scratch_result['success']:
                    card_data = scratch_result['data']
                    
                    if card_data['is_winner']:
                        winning_cards += 1
                        total_won += Decimal(str(card_data['total_winnings']))
                        
                        # 如果设置了中奖停止，则停止连刮
                        if stop_on_win:
                            results.append({
                                'card_index': i + 1,
                                'card_id': card_id,
                                'is_winner': True,
                                'win_amount': card_data['total_winnings'],
                                'win_details': card_data['win_details'],
                                'stopped_on_win': True
                            })
                            break
                    
                    results.append({
                        'card_index': i + 1,
                        'card_id': card_id,
                        'is_winner': card_data['is_winner'],
                        'win_amount': card_data['total_winnings'],
                        'win_details': card_data.get('win_details', {}),
                        'areas': card_data['areas']
                    })
                else:
                    results.append({
                        'card_index': i + 1,
                        'card_id': card_id,
                        'error': scratch_result['message']
                    })
            
            # 计算最终结果
            net_result = total_won - total_spent
            
            return {
                'success': True,
                'message': f'自动连刮完成，购买{cards_purchased}张，中奖{winning_cards}张',
                'data': {
                    'cards_purchased': cards_purchased,
                    'winning_cards': winning_cards,
                    'total_spent': float(total_spent),
                    'total_won': float(total_won),
                    'net_result': float(net_result),
                    'win_rate': round(winning_cards / cards_purchased * 100, 2) if cards_purchased > 0 else 0,
                    'results': results,
                    'balance_after': float(balance.get_available_balance()),
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'自动连刮失败: {str(e)}'
            }
    
    @staticmethod
    def get_game_statistics(days: int = 7) -> Dict[str, Any]:
        """
        获取游戏统计信息
        """
        try:
            from datetime import timedelta
            
            game = Scratch666Service.get_game()
            if not game:
                return {'error': '游戏不存在'}
            
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days-1)
            
            # 获取期间统计
            stats = ScratchStatistics.objects.filter(
                game=game,
                date__range=[start_date, end_date]
            ).order_by('-date')
            
            if not stats.exists():
                return {
                    'period': {'start_date': start_date, 'end_date': end_date, 'days': days},
                    'summary': {
                        'total_cards_sold': 0,
                        'total_sales_amount': 0.0,
                        'total_winners': 0,
                        'total_winnings': 0.0,
                        'profit': 0.0,
                        'profit_rate': 0.0,
                        'payout_rate': 0.0,
                    },
                    'daily_stats': []
                }
            
            # 计算汇总数据
            total_cards_sold = sum(stat.total_cards_sold for stat in stats)
            total_sales_amount = sum(stat.total_sales_amount for stat in stats)
            total_winners = sum(stat.total_winners for stat in stats)
            total_winnings = sum(stat.total_winnings for stat in stats)
            total_profit = sum(stat.profit for stat in stats)
            
            avg_profit_rate = (total_profit / total_sales_amount * 100) if total_sales_amount > 0 else 0
            payout_rate = (total_winnings / total_sales_amount * 100) if total_sales_amount > 0 else 0
            
            # 每日统计
            daily_stats = []
            for stat in stats:
                daily_stats.append({
                    'date': stat.date,
                    'cards_sold': stat.total_cards_sold,
                    'sales_amount': float(stat.total_sales_amount),
                    'winners': stat.total_winners,
                    'winnings': float(stat.total_winnings),
                    'profit': float(stat.profit),
                    'profit_rate': float(stat.profit_rate),
                    'payout_rate': stat.calculate_payout_rate(),
                    'win_rate': round(stat.total_winners / stat.total_cards_sold * 100, 2) if stat.total_cards_sold > 0 else 0,
                })
            
            return {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'days': days
                },
                'summary': {
                    'total_cards_sold': total_cards_sold,
                    'total_sales_amount': float(total_sales_amount),
                    'total_winners': total_winners,
                    'total_winnings': float(total_winnings),
                    'profit': float(total_profit),
                    'profit_rate': round(avg_profit_rate, 2),
                    'payout_rate': round(payout_rate, 2),
                    'win_rate': round(total_winners / total_cards_sold * 100, 2) if total_cards_sold > 0 else 0,
                },
                'daily_stats': daily_stats
            }
            
        except Exception as e:
            return {'error': f'获取统计失败: {str(e)}'}
    
    @staticmethod
    def update_daily_statistics():
        """
        更新每日统计数据
        """
        try:
            game = Scratch666Service.get_game()
            if not game:
                return False
            
            today = timezone.now().date()
            
            # 获取今日数据
            today_cards = ScratchCard.objects.filter(
                game=game,
                purchased_at__date=today
            )
            
            if not today_cards.exists():
                return True  # 没有数据也算成功
            
            # 计算统计数据
            total_cards_sold = today_cards.count()
            total_sales_amount = sum(card.price for card in today_cards)
            
            winning_cards = today_cards.filter(is_winner=True)
            total_winners = winning_cards.count()
            total_winnings = sum(card.total_winnings for card in winning_cards)
            
            # 按奖项统计
            winners_6 = sum(1 for card in winning_cards if '6' in str(card.win_details))
            winners_66 = sum(1 for card in winning_cards if '66' in str(card.win_details))
            winners_666 = sum(1 for card in winning_cards if '666' in str(card.win_details))
            
            winnings_6 = sum(
                sum(area['amount'] for area in card.win_details.get('areas', []) if area['content'] == '6')
                for card in winning_cards
            )
            winnings_66 = sum(
                sum(area['amount'] for area in card.win_details.get('areas', []) if area['content'] == '66')
                for card in winning_cards
            )
            winnings_666 = sum(
                sum(area['amount'] for area in card.win_details.get('areas', []) if area['content'] == '666')
                for card in winning_cards
            )
            
            # 计算利润
            profit = total_sales_amount - total_winnings
            profit_rate = (profit / total_sales_amount * 100) if total_sales_amount > 0 else Decimal('0.00')
            
            # 用户统计
            unique_players = today_cards.values('user').distinct().count()
            avg_cards_per_player = total_cards_sold / unique_players if unique_players > 0 else 0
            
            # 创建或更新统计记录
            stats, created = ScratchStatistics.objects.update_or_create(
                game=game,
                date=today,
                defaults={
                    'total_cards_sold': total_cards_sold,
                    'total_sales_amount': total_sales_amount,
                    'total_winners': total_winners,
                    'total_winnings': total_winnings,
                    'winners_6': winners_6,
                    'winnings_6': Decimal(str(winnings_6)),
                    'winners_66': winners_66,
                    'winnings_66': Decimal(str(winnings_66)),
                    'winners_666': winners_666,
                    'winnings_666': Decimal(str(winnings_666)),
                    'profit': profit,
                    'profit_rate': profit_rate,
                    'unique_players': unique_players,
                    'avg_cards_per_player': Decimal(str(avg_cards_per_player)),
                }
            )
            
            return True
            
        except Exception as e:
            print(f"更新刮刮乐统计失败: {str(e)}")
            return False