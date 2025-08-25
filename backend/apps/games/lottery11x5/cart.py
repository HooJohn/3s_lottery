"""
11选5投注购物车服务
"""

import json
from typing import Dict, List, Any, Optional
from decimal import Decimal
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .services import Lottery11x5Service

User = get_user_model()


class Lottery11x5Cart:
    """
    11选5投注购物车
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.cache_key = f'lottery11x5_cart_{user_id}'
        self.cache_timeout = 3600  # 1小时过期
    
    def add_bet(self, bet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加投注到购物车
        """
        try:
            # 验证投注数据
            validation_result = self._validate_bet_data(bet_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'message': validation_result['message']
                }
            
            # 获取当前购物车
            cart_items = self.get_cart_items()
            
            # 生成投注项ID
            bet_id = self._generate_bet_id(bet_data)
            
            # 计算投注详情
            bet_details = self._calculate_bet_details(bet_data)
            
            # 添加到购物车
            cart_item = {
                'id': bet_id,
                'draw_id': bet_data['draw_id'],
                'draw_number': bet_data.get('draw_number', ''),
                'bet_type_id': bet_data['bet_type_id'],
                'bet_type_name': bet_data.get('bet_type_name', ''),
                'bet_method': bet_data['bet_method'],
                'numbers': bet_data['numbers'],
                'positions': bet_data.get('positions', []),
                'selected_count': bet_data.get('selected_count', 0),
                'amount': float(bet_data['amount']),
                'multiplier': bet_data.get('multiplier', 1),
                'mode': bet_data.get('mode', '元'),  # 元/角/分
                'is_multiple': bet_details['is_multiple'],
                'multiple_count': bet_details['multiple_count'],
                'total_amount': bet_details['total_amount'],
                'potential_payout': bet_details['potential_payout'],
                'odds': bet_details['odds'],
                'created_at': bet_details['created_at'],
            }
            
            # 检查是否已存在相同投注
            existing_index = None
            for i, item in enumerate(cart_items):
                if item['id'] == bet_id:
                    existing_index = i
                    break
            
            if existing_index is not None:
                # 更新现有投注
                cart_items[existing_index] = cart_item
            else:
                # 添加新投注
                cart_items.append(cart_item)
            
            # 保存到缓存
            self._save_cart(cart_items)
            
            return {
                'success': True,
                'message': '添加到购彩篮成功',
                'data': {
                    'cart_item': cart_item,
                    'cart_count': len(cart_items),
                    'cart_total': self._calculate_cart_total(cart_items)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'添加到购彩篮失败: {str(e)}'
            }
    
    def remove_bet(self, bet_id: str) -> Dict[str, Any]:
        """
        从购物车移除投注
        """
        try:
            cart_items = self.get_cart_items()
            
            # 查找并移除投注项
            cart_items = [item for item in cart_items if item['id'] != bet_id]
            
            # 保存到缓存
            self._save_cart(cart_items)
            
            return {
                'success': True,
                'message': '移除成功',
                'data': {
                    'cart_count': len(cart_items),
                    'cart_total': self._calculate_cart_total(cart_items)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'移除失败: {str(e)}'
            }
    
    def update_bet(self, bet_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新购物车中的投注
        """
        try:
            cart_items = self.get_cart_items()
            
            # 查找投注项
            item_index = None
            for i, item in enumerate(cart_items):
                if item['id'] == bet_id:
                    item_index = i
                    break
            
            if item_index is None:
                return {
                    'success': False,
                    'message': '投注项不存在'
                }
            
            # 更新投注项
            cart_item = cart_items[item_index]
            
            # 允许更新的字段
            updatable_fields = ['amount', 'multiplier', 'mode']
            for field in updatable_fields:
                if field in updates:
                    cart_item[field] = updates[field]
            
            # 重新计算投注详情
            bet_data = {
                'draw_id': cart_item['draw_id'],
                'bet_type_id': cart_item['bet_type_id'],
                'bet_method': cart_item['bet_method'],
                'numbers': cart_item['numbers'],
                'positions': cart_item['positions'],
                'selected_count': cart_item['selected_count'],
                'amount': Decimal(str(cart_item['amount'])),
                'multiplier': cart_item['multiplier'],
            }
            
            bet_details = self._calculate_bet_details(bet_data)
            cart_item.update({
                'is_multiple': bet_details['is_multiple'],
                'multiple_count': bet_details['multiple_count'],
                'total_amount': bet_details['total_amount'],
                'potential_payout': bet_details['potential_payout'],
                'odds': bet_details['odds'],
            })
            
            cart_items[item_index] = cart_item
            
            # 保存到缓存
            self._save_cart(cart_items)
            
            return {
                'success': True,
                'message': '更新成功',
                'data': {
                    'cart_item': cart_item,
                    'cart_total': self._calculate_cart_total(cart_items)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'更新失败: {str(e)}'
            }
    
    def get_cart_items(self) -> List[Dict[str, Any]]:
        """
        获取购物车项目
        """
        cart_data = cache.get(self.cache_key, '[]')
        if isinstance(cart_data, str):
            return json.loads(cart_data)
        return cart_data or []
    
    def get_cart_summary(self) -> Dict[str, Any]:
        """
        获取购物车摘要
        """
        cart_items = self.get_cart_items()
        
        return {
            'count': len(cart_items),
            'total_amount': self._calculate_cart_total(cart_items),
            'total_potential_payout': sum(item['potential_payout'] for item in cart_items),
            'items': cart_items
        }
    
    def clear_cart(self) -> Dict[str, Any]:
        """
        清空购物车
        """
        try:
            cache.delete(self.cache_key)
            
            return {
                'success': True,
                'message': '购彩篮已清空'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'清空失败: {str(e)}'
            }
    
    def place_all_bets(self, user) -> Dict[str, Any]:
        """
        提交购物车中的所有投注
        """
        try:
            cart_items = self.get_cart_items()
            
            if not cart_items:
                return {
                    'success': False,
                    'message': '购彩篮为空'
                }
            
            # 检查用户余额
            total_amount = self._calculate_cart_total(cart_items)
            user_balance = user.balance.get_available_balance()
            
            if user_balance < total_amount:
                return {
                    'success': False,
                    'message': f'余额不足，需要 ₦{total_amount}，当前余额 ₦{user_balance}'
                }
            
            # 逐个提交投注
            successful_bets = []
            failed_bets = []
            
            for item in cart_items:
                bet_result = Lottery11x5Service.place_bet(
                    user=user,
                    draw_id=item['draw_id'],
                    bet_type_id=item['bet_type_id'],
                    numbers=item['numbers'],
                    amount=Decimal(str(item['amount'])),
                    bet_method=item['bet_method'],
                    positions=item['positions'],
                    selected_count=item['selected_count']
                )
                
                if bet_result['success']:
                    successful_bets.append({
                        'cart_item_id': item['id'],
                        'bet_id': bet_result['data']['bet_id'],
                        'draw_number': bet_result['data']['draw_number'],
                        'amount': bet_result['data']['total_amount']
                    })
                else:
                    failed_bets.append({
                        'cart_item_id': item['id'],
                        'error': bet_result['message']
                    })
            
            # 如果有成功的投注，清空购物车
            if successful_bets:
                self.clear_cart()
            
            return {
                'success': len(successful_bets) > 0,
                'message': f'成功投注 {len(successful_bets)} 注，失败 {len(failed_bets)} 注',
                'data': {
                    'successful_bets': successful_bets,
                    'failed_bets': failed_bets,
                    'total_successful': len(successful_bets),
                    'total_failed': len(failed_bets)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'提交投注失败: {str(e)}'
            }
    
    def _validate_bet_data(self, bet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证投注数据
        """
        required_fields = ['draw_id', 'bet_type_id', 'numbers', 'amount', 'bet_method']
        
        for field in required_fields:
            if field not in bet_data:
                return {
                    'valid': False,
                    'message': f'缺少必需字段: {field}'
                }
        
        # 验证号码
        numbers = bet_data['numbers']
        if not isinstance(numbers, list) or len(numbers) == 0:
            return {
                'valid': False,
                'message': '号码不能为空'
            }
        
        # 验证号码范围
        if not all(1 <= num <= 11 for num in numbers):
            return {
                'valid': False,
                'message': '号码必须在1-11之间'
            }
        
        # 验证投注金额
        try:
            amount = Decimal(str(bet_data['amount']))
            if amount <= 0:
                return {
                    'valid': False,
                    'message': '投注金额必须大于0'
                }
        except:
            return {
                'valid': False,
                'message': '投注金额格式错误'
            }
        
        # 验证投注方法
        bet_method = bet_data['bet_method']
        if bet_method not in ['POSITION', 'ANY', 'GROUP']:
            return {
                'valid': False,
                'message': '无效的投注方法'
            }
        
        # 使用现有的验证逻辑
        is_valid = Lottery11x5Service.validate_numbers(
            numbers=numbers,
            bet_method=bet_method,
            positions=bet_data.get('positions', []),
            selected_count=bet_data.get('selected_count', 0)
        )
        
        if not is_valid:
            return {
                'valid': False,
                'message': '投注号码验证失败'
            }
        
        return {
            'valid': True,
            'message': '验证通过'
        }
    
    def _calculate_bet_details(self, bet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算投注详情
        """
        from apps.games.models import BetType
        from django.utils import timezone
        
        # 获取投注类型
        bet_type = BetType.objects.get(id=bet_data['bet_type_id'])
        
        # 计算复式投注注数
        is_multiple = False
        multiple_count = 1
        
        if bet_data['bet_method'] == 'ANY' and len(bet_data['numbers']) > bet_data.get('selected_count', 0):
            from math import comb
            selected_count = bet_data.get('selected_count', 0)
            if selected_count > 0:
                is_multiple = True
                multiple_count = comb(len(bet_data['numbers']), selected_count)
        
        # 应用倍数
        multiplier = bet_data.get('multiplier', 1)
        multiple_count *= multiplier
        
        # 计算总金额
        base_amount = bet_data['amount']
        
        # 根据模式调整金额
        mode = bet_data.get('mode', '元')
        if mode == '角':
            base_amount = base_amount / 10
        elif mode == '分':
            base_amount = base_amount / 100
        
        total_amount = float(base_amount * multiple_count)
        
        # 计算潜在派彩
        potential_payout = float(base_amount * bet_type.odds * multiple_count)
        
        return {
            'is_multiple': is_multiple,
            'multiple_count': multiple_count,
            'total_amount': total_amount,
            'potential_payout': potential_payout,
            'odds': float(bet_type.odds),
            'created_at': timezone.now().isoformat(),
        }
    
    def _generate_bet_id(self, bet_data: Dict[str, Any]) -> str:
        """
        生成投注项ID
        """
        import hashlib
        
        # 使用关键信息生成唯一ID
        key_info = f"{bet_data['draw_id']}_{bet_data['bet_type_id']}_{bet_data['bet_method']}_{sorted(bet_data['numbers'])}_{bet_data.get('positions', [])}_{bet_data.get('selected_count', 0)}"
        
        return hashlib.md5(key_info.encode()).hexdigest()[:12]
    
    def _calculate_cart_total(self, cart_items: List[Dict[str, Any]]) -> float:
        """
        计算购物车总金额
        """
        return sum(item['total_amount'] for item in cart_items)
    
    def _save_cart(self, cart_items: List[Dict[str, Any]]):
        """
        保存购物车到缓存
        """
        cache.set(self.cache_key, json.dumps(cart_items), self.cache_timeout)


class Lottery11x5QuickPick:
    """
    11选5快捷选号服务
    """
    
    @staticmethod
    def get_all_numbers() -> List[int]:
        """
        获取全部号码 (01-11)
        """
        return list(range(1, 12))
    
    @staticmethod
    def get_big_numbers() -> List[int]:
        """
        获取大号 (06-11)
        """
        return list(range(6, 12))
    
    @staticmethod
    def get_small_numbers() -> List[int]:
        """
        获取小号 (01-05)
        """
        return list(range(1, 6))
    
    @staticmethod
    def get_odd_numbers() -> List[int]:
        """
        获取奇数号码
        """
        return [1, 3, 5, 7, 9, 11]
    
    @staticmethod
    def get_even_numbers() -> List[int]:
        """
        获取偶数号码
        """
        return [2, 4, 6, 8, 10]
    
    @staticmethod
    def get_hot_numbers(period: int = 50) -> List[int]:
        """
        获取热门号码
        """
        hot_cold_data = Lottery11x5Service.get_hot_cold_numbers(period)
        
        if not hot_cold_data or 'numbers' not in hot_cold_data:
            return []
        
        hot_numbers = []
        for item in hot_cold_data['numbers']:
            if item['is_hot']:
                hot_numbers.append(item['number'])
        
        return sorted(hot_numbers)
    
    @staticmethod
    def get_cold_numbers(period: int = 50) -> List[int]:
        """
        获取冷门号码
        """
        hot_cold_data = Lottery11x5Service.get_hot_cold_numbers(period)
        
        if not hot_cold_data or 'numbers' not in hot_cold_data:
            return []
        
        cold_numbers = []
        for item in hot_cold_data['numbers']:
            if item['is_cold']:
                cold_numbers.append(item['number'])
        
        return sorted(cold_numbers)
    
    @staticmethod
    def get_random_numbers(count: int = 5) -> List[int]:
        """
        获取随机号码
        """
        return Lottery11x5Service.generate_random_numbers(count)
    
    @staticmethod
    def get_quick_pick_options() -> Dict[str, Any]:
        """
        获取所有快捷选号选项
        """
        return {
            'all': {
                'name': '全',
                'description': '选择全部号码 (01-11)',
                'numbers': Lottery11x5QuickPick.get_all_numbers()
            },
            'big': {
                'name': '大',
                'description': '选择大号 (06-11)',
                'numbers': Lottery11x5QuickPick.get_big_numbers()
            },
            'small': {
                'name': '小',
                'description': '选择小号 (01-05)',
                'numbers': Lottery11x5QuickPick.get_small_numbers()
            },
            'odd': {
                'name': '奇',
                'description': '选择奇数号码',
                'numbers': Lottery11x5QuickPick.get_odd_numbers()
            },
            'even': {
                'name': '偶',
                'description': '选择偶数号码',
                'numbers': Lottery11x5QuickPick.get_even_numbers()
            },
            'hot': {
                'name': '热',
                'description': '选择热门号码',
                'numbers': Lottery11x5QuickPick.get_hot_numbers()
            },
            'cold': {
                'name': '冷',
                'description': '选择冷门号码',
                'numbers': Lottery11x5QuickPick.get_cold_numbers()
            },
            'random': {
                'name': '机选',
                'description': '随机选择号码',
                'numbers': Lottery11x5QuickPick.get_random_numbers()
            }
        }