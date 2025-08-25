"""
11选5开奖引擎
确保公平性和安全性的随机开奖算法
"""

import random
import hashlib
import time
import secrets
from typing import List, Dict, Any, Tuple
from decimal import Decimal
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Lottery11x5DrawEngine:
    """
    11选5开奖引擎
    """
    
    def __init__(self):
        self.number_range = (1, 11)  # 号码范围1-11
        self.draw_count = 5  # 每期开出5个号码
        self.seed_sources = [
            'system_time',
            'system_random',
            'crypto_random',
            'draw_metadata'
        ]
    
    def generate_winning_numbers(self, draw_id: str, draw_time: timezone.datetime) -> Dict[str, Any]:
        """
        生成开奖号码
        """
        try:
            # 生成随机种子
            seed = self._generate_secure_seed(draw_id, draw_time)
            
            # 使用种子初始化随机数生成器
            rng = random.Random(seed)
            
            # 生成开奖号码
            winning_numbers = self._draw_numbers(rng)
            
            # 验证号码有效性
            if not self._validate_numbers(winning_numbers):
                raise ValueError("生成的号码无效")
            
            # 计算统计信息
            statistics = self._calculate_statistics(winning_numbers)
            
            # 生成开奖证明
            proof = self._generate_draw_proof(draw_id, draw_time, winning_numbers, seed)
            
            return {
                'success': True,
                'winning_numbers': winning_numbers,
                'statistics': statistics,
                'proof': proof,
                'timestamp': timezone.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"开奖号码生成失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': timezone.now().isoformat(),
            }
    
    def _generate_secure_seed(self, draw_id: str, draw_time: timezone.datetime) -> int:
        """
        生成安全的随机种子
        """
        # 收集多个熵源
        entropy_sources = []
        
        # 1. 系统时间（微秒级）
        entropy_sources.append(str(time.time_ns()))
        
        # 2. 期次信息
        entropy_sources.append(str(draw_id))
        entropy_sources.append(draw_time.isoformat())
        
        # 3. 系统随机数
        entropy_sources.append(str(random.getrandbits(256)))
        
        # 4. 加密安全随机数
        entropy_sources.append(secrets.token_hex(32))
        
        # 5. 系统状态信息
        try:
            import os
            entropy_sources.append(str(os.urandom(32).hex()))
        except:
            pass
        
        # 6. 内存地址（额外的随机性）
        entropy_sources.append(str(id(entropy_sources)))
        
        # 合并所有熵源
        combined_entropy = ''.join(entropy_sources)
        
        # 使用SHA-256哈希生成种子
        hash_object = hashlib.sha256(combined_entropy.encode())
        seed_hex = hash_object.hexdigest()
        
        # 转换为整数种子
        seed = int(seed_hex, 16) % (2**32)
        
        logger.info(f"生成开奖种子: draw_id={draw_id}, seed_hash={seed_hex[:16]}...")
        
        return seed
    
    def _draw_numbers(self, rng: random.Random) -> List[int]:
        """
        使用指定随机数生成器抽取号码
        """
        # 从1-11中随机选择5个不重复的号码
        numbers = rng.sample(range(self.number_range[0], self.number_range[1] + 1), self.draw_count)
        
        # 排序号码
        numbers.sort()
        
        return numbers
    
    def _validate_numbers(self, numbers: List[int]) -> bool:
        """
        验证开奖号码的有效性
        """
        # 检查数量
        if len(numbers) != self.draw_count:
            return False
        
        # 检查范围
        if not all(self.number_range[0] <= num <= self.number_range[1] for num in numbers):
            return False
        
        # 检查重复
        if len(set(numbers)) != len(numbers):
            return False
        
        # 检查排序
        if numbers != sorted(numbers):
            return False
        
        return True
    
    def _calculate_statistics(self, numbers: List[int]) -> Dict[str, Any]:
        """
        计算开奖号码统计信息
        """
        # 基本统计
        sum_value = sum(numbers)
        min_value = min(numbers)
        max_value = max(numbers)
        span_value = max_value - min_value
        
        # 奇偶统计
        odd_numbers = [num for num in numbers if num % 2 == 1]
        even_numbers = [num for num in numbers if num % 2 == 0]
        odd_count = len(odd_numbers)
        even_count = len(even_numbers)
        
        # 大小统计（以6为分界线）
        big_numbers = [num for num in numbers if num > 5]
        small_numbers = [num for num in numbers if num <= 5]
        big_count = len(big_numbers)
        small_count = len(small_numbers)
        
        # 连号统计
        consecutive_groups = self._find_consecutive_groups(numbers)
        max_consecutive = max(len(group) for group in consecutive_groups) if consecutive_groups else 1
        
        # 区间分布（1-3, 4-7, 8-11）
        zone_1 = len([num for num in numbers if 1 <= num <= 3])
        zone_2 = len([num for num in numbers if 4 <= num <= 7])
        zone_3 = len([num for num in numbers if 8 <= num <= 11])
        
        return {
            'sum_value': sum_value,
            'min_value': min_value,
            'max_value': max_value,
            'span_value': span_value,
            'odd_count': odd_count,
            'even_count': even_count,
            'odd_numbers': odd_numbers,
            'even_numbers': even_numbers,
            'big_count': big_count,
            'small_count': small_count,
            'big_numbers': big_numbers,
            'small_numbers': small_numbers,
            'consecutive_groups': consecutive_groups,
            'max_consecutive': max_consecutive,
            'zone_distribution': [zone_1, zone_2, zone_3],
            'odd_even_ratio': f"{odd_count}:{even_count}",
            'big_small_ratio': f"{big_count}:{small_count}",
        }
    
    def _find_consecutive_groups(self, numbers: List[int]) -> List[List[int]]:
        """
        查找连续号码组
        """
        if not numbers:
            return []
        
        groups = []
        current_group = [numbers[0]]
        
        for i in range(1, len(numbers)):
            if numbers[i] == numbers[i-1] + 1:
                current_group.append(numbers[i])
            else:
                if len(current_group) >= 2:
                    groups.append(current_group)
                current_group = [numbers[i]]
        
        if len(current_group) >= 2:
            groups.append(current_group)
        
        return groups
    
    def _generate_draw_proof(self, draw_id: str, draw_time: timezone.datetime, 
                           numbers: List[int], seed: int) -> Dict[str, Any]:
        """
        生成开奖证明
        """
        # 创建证明数据
        proof_data = {
            'draw_id': draw_id,
            'draw_time': draw_time.isoformat(),
            'winning_numbers': numbers,
            'seed': seed,
            'algorithm': 'secure_random_sample',
            'version': '1.0',
            'timestamp': timezone.now().isoformat(),
        }
        
        # 生成证明哈希
        proof_string = str(proof_data)
        proof_hash = hashlib.sha256(proof_string.encode()).hexdigest()
        
        return {
            'proof_hash': proof_hash,
            'proof_data': proof_data,
            'verification_url': f"/api/v1/games/lottery11x5/verify-draw/{draw_id}",
        }
    
    def verify_draw_result(self, draw_id: str, draw_time: timezone.datetime, 
                          claimed_numbers: List[int], claimed_seed: int = None) -> Dict[str, Any]:
        """
        验证开奖结果
        """
        try:
            if claimed_seed is None:
                # 重新生成种子进行验证
                regenerated_seed = self._generate_secure_seed(draw_id, draw_time)
                rng = random.Random(regenerated_seed)
                expected_numbers = self._draw_numbers(rng)
                
                # 注意：由于时间戳等动态因素，重新生成的结果可能不同
                # 这里主要验证号码的有效性
                is_valid = self._validate_numbers(claimed_numbers)
                
                return {
                    'valid': is_valid,
                    'message': '号码格式验证通过' if is_valid else '号码格式无效',
                    'verification_type': 'format_check'
                }
            else:
                # 使用提供的种子验证
                rng = random.Random(claimed_seed)
                expected_numbers = self._draw_numbers(rng)
                
                is_match = expected_numbers == claimed_numbers
                
                return {
                    'valid': is_match,
                    'message': '开奖结果验证通过' if is_match else '开奖结果不匹配',
                    'expected_numbers': expected_numbers,
                    'claimed_numbers': claimed_numbers,
                    'verification_type': 'seed_verification'
                }
                
        except Exception as e:
            return {
                'valid': False,
                'message': f'验证失败: {str(e)}',
                'verification_type': 'error'
            }


class Lottery11x5ProfitController:
    """
    11选5利润控制器
    确保18%毛利率
    """
    
    def __init__(self, target_profit_rate: Decimal = Decimal('0.18')):
        self.target_profit_rate = target_profit_rate
        self.min_profit_rate = Decimal('0.15')  # 最低利润率
        self.max_profit_rate = Decimal('0.25')  # 最高利润率
    
    def analyze_draw_profitability(self, draw_id: str, potential_numbers: List[int]) -> Dict[str, Any]:
        """
        分析期次盈利能力
        """
        try:
            from apps.games.models import Draw, Bet
            from .services import Lottery11x5Service
            
            # 获取期次信息
            draw = Draw.objects.get(id=draw_id)
            
            # 获取所有投注
            bets = Bet.objects.filter(draw=draw, status='PENDING')
            
            if not bets.exists():
                return {
                    'total_bets': 0,
                    'total_amount': Decimal('0.00'),
                    'potential_payout': Decimal('0.00'),
                    'profit': Decimal('0.00'),
                    'profit_rate': Decimal('0.00'),
                    'meets_target': True,
                    'recommendation': 'no_bets'
                }
            
            # 计算总投注金额
            total_amount = sum(bet.amount * bet.lottery11x5_detail.multiple_count for bet in bets)
            
            # 模拟结算，计算潜在派彩
            total_payout = Decimal('0.00')
            
            for bet in bets:
                lottery_bet = bet.lottery11x5_detail
                is_win, win_amount = Lottery11x5Service.check_win(
                    bet_numbers=bet.numbers,
                    winning_numbers=potential_numbers,
                    bet_method=lottery_bet.bet_method,
                    positions=lottery_bet.positions,
                    selected_count=lottery_bet.selected_count,
                    odds=bet.odds,
                    bet_amount=bet.amount,
                    multiple_count=lottery_bet.multiple_count
                )
                
                if is_win:
                    total_payout += win_amount
            
            # 计算利润
            profit = total_amount - total_payout
            profit_rate = (profit / total_amount) if total_amount > 0 else Decimal('0.00')
            
            # 评估是否符合目标
            meets_target = self.min_profit_rate <= profit_rate <= self.max_profit_rate
            
            # 生成建议
            recommendation = self._generate_recommendation(profit_rate)
            
            return {
                'total_bets': bets.count(),
                'total_amount': total_amount,
                'potential_payout': total_payout,
                'profit': profit,
                'profit_rate': profit_rate,
                'target_profit_rate': self.target_profit_rate,
                'meets_target': meets_target,
                'recommendation': recommendation,
                'analysis_time': timezone.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"分析期次盈利能力失败: {str(e)}")
            return {
                'error': str(e),
                'recommendation': 'error'
            }
    
    def _generate_recommendation(self, profit_rate: Decimal) -> str:
        """
        生成利润控制建议
        """
        if profit_rate < self.min_profit_rate:
            return 'low_profit'  # 利润过低
        elif profit_rate > self.max_profit_rate:
            return 'high_profit'  # 利润过高
        else:
            return 'optimal'  # 利润适中
    
    def should_adjust_odds(self, recent_profit_rates: List[Decimal]) -> Dict[str, Any]:
        """
        判断是否需要调整赔率
        """
        if not recent_profit_rates:
            return {'should_adjust': False, 'reason': 'no_data'}
        
        avg_profit_rate = sum(recent_profit_rates) / len(recent_profit_rates)
        
        # 连续偏离目标的期数
        deviation_count = 0
        for rate in recent_profit_rates[-5:]:  # 检查最近5期
            if abs(rate - self.target_profit_rate) > Decimal('0.05'):
                deviation_count += 1
        
        should_adjust = (
            abs(avg_profit_rate - self.target_profit_rate) > Decimal('0.03') or
            deviation_count >= 3
        )
        
        adjustment_direction = 'increase' if avg_profit_rate < self.target_profit_rate else 'decrease'
        
        return {
            'should_adjust': should_adjust,
            'current_avg_rate': avg_profit_rate,
            'target_rate': self.target_profit_rate,
            'deviation_count': deviation_count,
            'adjustment_direction': adjustment_direction,
            'suggested_adjustment': abs(avg_profit_rate - self.target_profit_rate) * Decimal('0.5')
        }


class Lottery11x5DrawValidator:
    """
    11选5开奖验证器
    """
    
    @staticmethod
    def validate_draw_conditions(draw_id: str) -> Dict[str, Any]:
        """
        验证开奖条件
        """
        try:
            from apps.games.models import Draw
            
            draw = Draw.objects.get(id=draw_id)
            errors = []
            warnings = []
            
            # 检查期次状态
            if draw.status != 'CLOSED':
                errors.append(f'期次状态错误: {draw.status}，应为CLOSED')
            
            # 检查开奖时间
            now = timezone.now()
            if now < draw.draw_time:
                errors.append(f'尚未到开奖时间: {draw.draw_time}')
            
            # 检查是否已经开奖
            if draw.status == 'COMPLETED':
                errors.append('该期次已经开奖')
            
            # 检查投注数量
            if draw.total_bets == 0:
                warnings.append('该期次没有投注')
            
            # 检查投注金额
            if draw.total_amount == 0:
                warnings.append('该期次投注金额为0')
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'draw_info': {
                    'draw_number': draw.draw_number,
                    'draw_time': draw.draw_time,
                    'status': draw.status,
                    'total_bets': draw.total_bets,
                    'total_amount': float(draw.total_amount),
                }
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f'验证失败: {str(e)}'],
                'warnings': []
            }
    
    @staticmethod
    def validate_winning_numbers(numbers: List[int]) -> Dict[str, Any]:
        """
        验证开奖号码
        """
        errors = []
        
        # 检查数量
        if len(numbers) != 5:
            errors.append(f'号码数量错误: {len(numbers)}，应为5个')
        
        # 检查范围
        for num in numbers:
            if not isinstance(num, int) or num < 1 or num > 11:
                errors.append(f'号码 {num} 超出范围 (1-11)')
        
        # 检查重复
        if len(set(numbers)) != len(numbers):
            errors.append('号码不能重复')
        
        # 检查排序
        if numbers != sorted(numbers):
            errors.append('号码必须按升序排列')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }