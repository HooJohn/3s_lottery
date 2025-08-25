"""
11选5投注计算器
"""

from typing import Dict, List, Any, Tuple
from decimal import Decimal
from math import comb


class Lottery11x5BetCalculator:
    """
    11选5投注计算器
    """
    
    # 标准赔率配置
    STANDARD_ODDS = {
        'POSITION': Decimal('9.90'),    # 定位胆
        'ANY_1': Decimal('2.20'),       # 任选一
        'ANY_2': Decimal('5.50'),       # 任选二
        'ANY_3': Decimal('16.50'),      # 任选三
        'ANY_4': Decimal('66.00'),      # 任选四
        'ANY_5': Decimal('330.00'),     # 任选五
    }
    
    @staticmethod
    def calculate_bet_details(bet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算投注详情
        """
        bet_method = bet_data['bet_method']
        numbers = bet_data['numbers']
        positions = bet_data.get('positions', [])
        selected_count = bet_data.get('selected_count', 0)
        amount = Decimal(str(bet_data['amount']))
        multiplier = bet_data.get('multiplier', 1)
        mode = bet_data.get('mode', '元')
        
        # 根据模式调整基础金额
        base_amount = amount
        if mode == '角':
            base_amount = amount / 10
        elif mode == '分':
            base_amount = amount / 100
        
        # 计算注数
        bet_count = Lottery11x5BetCalculator.calculate_bet_count(
            bet_method, numbers, positions, selected_count
        )
        
        # 应用倍数
        total_bet_count = bet_count * multiplier
        
        # 计算总金额
        total_amount = base_amount * total_bet_count
        
        # 获取赔率
        odds = Lottery11x5BetCalculator.get_odds(bet_method, selected_count)
        
        # 计算潜在派彩
        potential_payout = base_amount * odds * total_bet_count
        
        # 计算中奖概率
        win_probability = Lottery11x5BetCalculator.calculate_win_probability(
            bet_method, len(numbers), positions, selected_count
        )
        
        return {
            'bet_count': bet_count,
            'total_bet_count': total_bet_count,
            'base_amount': float(base_amount),
            'total_amount': float(total_amount),
            'odds': float(odds),
            'potential_payout': float(potential_payout),
            'win_probability': win_probability,
            'expected_return': float(potential_payout * Decimal(str(win_probability))),
            'is_multiple': bet_count > 1,
            'multiplier': multiplier,
            'mode': mode,
        }
    
    @staticmethod
    def calculate_bet_count(bet_method: str, numbers: List[int], 
                           positions: List[int] = None, selected_count: int = 0) -> int:
        """
        计算投注注数
        """
        if bet_method == 'POSITION':
            # 定位胆：每个位置一注
            return len(positions) if positions else 1
            
        elif bet_method == 'ANY':
            # 任选：组合数计算
            if len(numbers) == selected_count:
                return 1  # 单式
            elif len(numbers) > selected_count:
                return comb(len(numbers), selected_count)  # 复式
            else:
                return 0  # 无效
                
        elif bet_method == 'GROUP':
            # 组选：简化计算，暂时返回1
            return 1
            
        return 1
    
    @staticmethod
    def get_odds(bet_method: str, selected_count: int = 0) -> Decimal:
        """
        获取赔率
        """
        if bet_method == 'POSITION':
            return Lottery11x5BetCalculator.STANDARD_ODDS['POSITION']
        elif bet_method == 'ANY':
            odds_key = f'ANY_{selected_count}'
            return Lottery11x5BetCalculator.STANDARD_ODDS.get(odds_key, Decimal('2.00'))
        elif bet_method == 'GROUP':
            return Decimal('10.00')  # 组选默认赔率
        
        return Decimal('2.00')
    
    @staticmethod
    def calculate_win_probability(bet_method: str, number_count: int, 
                                positions: List[int] = None, selected_count: int = 0) -> float:
        """
        计算中奖概率
        """
        if bet_method == 'POSITION':
            # 定位胆：每个位置1/11的概率
            single_position_prob = 1.0 / 11
            if positions and len(positions) > 1:
                # 多个位置都要中奖的概率
                return single_position_prob ** len(positions)
            return single_position_prob
            
        elif bet_method == 'ANY':
            # 任选：超几何分布计算
            # 从11个号码中开出5个，选择的号码中至少有selected_count个中奖的概率
            total_numbers = 11
            drawn_numbers = 5
            
            if selected_count == 1:
                # 任选一：至少中1个的概率
                prob_miss_all = comb(total_numbers - number_count, drawn_numbers) / comb(total_numbers, drawn_numbers)
                return 1.0 - prob_miss_all
            elif selected_count == 2:
                # 任选二：至少中2个的概率
                prob_hit_2_or_more = 0.0
                for hit_count in range(selected_count, min(number_count, drawn_numbers) + 1):
                    prob_hit_2_or_more += (
                        comb(number_count, hit_count) * 
                        comb(total_numbers - number_count, drawn_numbers - hit_count) /
                        comb(total_numbers, drawn_numbers)
                    )
                return prob_hit_2_or_more
            else:
                # 其他任选：简化计算
                return comb(number_count, selected_count) * comb(total_numbers - number_count, drawn_numbers - selected_count) / comb(total_numbers, drawn_numbers)
                
        elif bet_method == 'GROUP':
            # 组选：简化计算
            return 0.1
        
        return 0.0
    
    @staticmethod
    def validate_bet_limits(bet_data: Dict[str, Any], bet_type_limits: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证投注限额
        """
        total_amount = Decimal(str(bet_data.get('total_amount', 0)))
        potential_payout = Decimal(str(bet_data.get('potential_payout', 0)))
        
        min_bet = Decimal(str(bet_type_limits.get('min_bet', 1)))
        max_bet = Decimal(str(bet_type_limits.get('max_bet', 10000)))
        max_payout = Decimal(str(bet_type_limits.get('max_payout', 100000)))
        
        errors = []
        
        if total_amount < min_bet:
            errors.append(f'投注金额不能少于 ₦{min_bet}')
        
        if total_amount > max_bet:
            errors.append(f'投注金额不能超过 ₦{max_bet}')
        
        if potential_payout > max_payout:
            errors.append(f'潜在派彩不能超过 ₦{max_payout}')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def calculate_profit_margin(total_bets: Decimal, total_payouts: Decimal) -> Dict[str, Any]:
        """
        计算利润率
        """
        if total_bets == 0:
            return {
                'profit': Decimal('0.00'),
                'profit_rate': Decimal('0.00'),
                'payout_rate': Decimal('0.00')
            }
        
        profit = total_bets - total_payouts
        profit_rate = (profit / total_bets) * 100
        payout_rate = (total_payouts / total_bets) * 100
        
        return {
            'profit': profit,
            'profit_rate': profit_rate,
            'payout_rate': payout_rate
        }
    
    @staticmethod
    def suggest_bet_optimization(bet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        投注优化建议
        """
        bet_method = bet_data['bet_method']
        numbers = bet_data['numbers']
        selected_count = bet_data.get('selected_count', 0)
        win_probability = bet_data.get('win_probability', 0)
        expected_return = bet_data.get('expected_return', 0)
        total_amount = bet_data.get('total_amount', 0)
        
        suggestions = []
        
        # 中奖概率建议
        if win_probability < 0.1:
            suggestions.append({
                'type': 'probability',
                'message': '中奖概率较低，建议考虑降低投注金额或选择其他玩法',
                'priority': 'medium'
            })
        elif win_probability > 0.8:
            suggestions.append({
                'type': 'probability',
                'message': '中奖概率很高，但赔率可能较低，注意风险收益比',
                'priority': 'low'
            })
        
        # 期望收益建议
        expected_profit = expected_return - total_amount
        if expected_profit < 0:
            suggestions.append({
                'type': 'expected_return',
                'message': f'期望收益为负 (₦{expected_profit:.2f})，建议谨慎投注',
                'priority': 'high'
            })
        
        # 投注方式建议
        if bet_method == 'ANY' and len(numbers) > selected_count + 3:
            suggestions.append({
                'type': 'bet_method',
                'message': '选择号码过多，可考虑减少号码数量以降低成本',
                'priority': 'medium'
            })
        
        # 金额建议
        if total_amount > 100:
            suggestions.append({
                'type': 'amount',
                'message': '投注金额较大，建议分散投注以控制风险',
                'priority': 'medium'
            })
        
        return {
            'suggestions': suggestions,
            'risk_level': Lottery11x5BetCalculator._assess_risk_level(bet_data),
            'optimization_score': Lottery11x5BetCalculator._calculate_optimization_score(bet_data)
        }
    
    @staticmethod
    def _assess_risk_level(bet_data: Dict[str, Any]) -> str:
        """
        评估风险等级
        """
        win_probability = bet_data.get('win_probability', 0)
        total_amount = bet_data.get('total_amount', 0)
        expected_return = bet_data.get('expected_return', 0)
        
        risk_score = 0
        
        # 概率风险
        if win_probability < 0.1:
            risk_score += 3
        elif win_probability < 0.3:
            risk_score += 2
        elif win_probability < 0.5:
            risk_score += 1
        
        # 金额风险
        if total_amount > 500:
            risk_score += 3
        elif total_amount > 100:
            risk_score += 2
        elif total_amount > 50:
            risk_score += 1
        
        # 期望收益风险
        if expected_return < total_amount * 0.5:
            risk_score += 2
        elif expected_return < total_amount * 0.8:
            risk_score += 1
        
        if risk_score >= 6:
            return 'high'
        elif risk_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def _calculate_optimization_score(bet_data: Dict[str, Any]) -> float:
        """
        计算优化评分 (0-100)
        """
        win_probability = bet_data.get('win_probability', 0)
        expected_return = bet_data.get('expected_return', 0)
        total_amount = bet_data.get('total_amount', 0)
        
        # 基础分数
        score = 50.0
        
        # 概率加分
        if 0.2 <= win_probability <= 0.6:
            score += 20
        elif 0.1 <= win_probability < 0.2 or 0.6 < win_probability <= 0.8:
            score += 10
        
        # 期望收益加分
        if expected_return > total_amount:
            score += 20
        elif expected_return > total_amount * 0.8:
            score += 10
        else:
            score -= 10
        
        # 金额合理性
        if 10 <= total_amount <= 100:
            score += 10
        elif total_amount > 500:
            score -= 20
        
        return max(0, min(100, score))


class Lottery11x5BetValidator:
    """
    11选5投注验证器
    """
    
    @staticmethod
    def validate_bet_request(bet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证投注请求
        """
        errors = []
        
        # 验证必需字段
        required_fields = ['draw_id', 'bet_type_id', 'numbers', 'amount', 'bet_method']
        for field in required_fields:
            if field not in bet_data or bet_data[field] is None:
                errors.append(f'缺少必需字段: {field}')
        
        if errors:
            return {'valid': False, 'errors': errors}
        
        # 验证号码
        numbers_validation = Lottery11x5BetValidator.validate_numbers(bet_data)
        if not numbers_validation['valid']:
            errors.extend(numbers_validation['errors'])
        
        # 验证投注方法
        method_validation = Lottery11x5BetValidator.validate_bet_method(bet_data)
        if not method_validation['valid']:
            errors.extend(method_validation['errors'])
        
        # 验证金额
        amount_validation = Lottery11x5BetValidator.validate_amount(bet_data)
        if not amount_validation['valid']:
            errors.extend(amount_validation['errors'])
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_numbers(bet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证号码
        """
        numbers = bet_data.get('numbers', [])
        errors = []
        
        if not isinstance(numbers, list):
            errors.append('号码必须是数组格式')
            return {'valid': False, 'errors': errors}
        
        if len(numbers) == 0:
            errors.append('至少需要选择一个号码')
        
        if len(numbers) > 11:
            errors.append('选择的号码不能超过11个')
        
        # 检查号码范围
        for num in numbers:
            if not isinstance(num, int) or num < 1 or num > 11:
                errors.append(f'号码 {num} 不在有效范围内 (1-11)')
        
        # 检查重复号码
        if len(numbers) != len(set(numbers)):
            errors.append('号码不能重复')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_bet_method(bet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证投注方法
        """
        bet_method = bet_data.get('bet_method')
        numbers = bet_data.get('numbers', [])
        positions = bet_data.get('positions', [])
        selected_count = bet_data.get('selected_count', 0)
        errors = []
        
        if bet_method not in ['POSITION', 'ANY', 'GROUP']:
            errors.append('无效的投注方法')
            return {'valid': False, 'errors': errors}
        
        if bet_method == 'POSITION':
            if not positions:
                errors.append('定位胆投注必须指定位置')
            elif len(positions) != len(numbers):
                errors.append('定位胆投注的号码数量必须与位置数量相等')
            elif not all(1 <= pos <= 5 for pos in positions):
                errors.append('位置必须在1-5之间')
            elif len(positions) != len(set(positions)):
                errors.append('位置不能重复')
        
        elif bet_method == 'ANY':
            if selected_count < 1 or selected_count > 5:
                errors.append('任选投注的选择数量必须在1-5之间')
            elif len(numbers) < selected_count:
                errors.append('选择的号码数量不能少于任选数量')
        
        elif bet_method == 'GROUP':
            if len(numbers) < 2:
                errors.append('组选投注至少需要选择2个号码')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_amount(bet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证投注金额
        """
        amount = bet_data.get('amount')
        multiplier = bet_data.get('multiplier', 1)
        errors = []
        
        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                errors.append('投注金额必须大于0')
        except (ValueError, TypeError):
            errors.append('投注金额格式错误')
        
        try:
            multiplier = int(multiplier)
            if multiplier < 1 or multiplier > 999:
                errors.append('倍数必须在1-999之间')
        except (ValueError, TypeError):
            errors.append('倍数格式错误')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_user_eligibility(user, bet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证用户投注资格
        """
        errors = []
        
        # 检查用户状态
        if not user.is_active:
            errors.append('用户账户已被禁用')
        
        # 检查KYC状态
        try:
            kyc = user.kyc_profile
            if kyc.status != 'APPROVED':
                errors.append('请先完成身份验证')
        except:
            errors.append('请先完成身份验证')
        
        # 检查余额
        try:
            balance = user.balance
            total_amount = Decimal(str(bet_data.get('total_amount', 0)))
            if balance.get_available_balance() < total_amount:
                errors.append('账户余额不足')
        except:
            errors.append('无法获取账户余额信息')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }