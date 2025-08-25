"""
统一返水奖励系统服务
"""

import uuid
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone
from django.db import transaction, models
from django.core.cache import cache
import logging

from apps.finance.models import Transaction, UserBalance
from .models import (
    VIPLevel, UserVIPStatus, RebateRecord, ReferralRelation,
    ReferralReward, ReferralRewardRecord, UserReferralStats, RewardStatistics,
    RewardCalculation
)

logger = logging.getLogger(__name__)


class VIPService:
    """
    VIP等级服务
    """
    
    @staticmethod
    def get_all_vip_levels() -> List[Dict[str, Any]]:
        """
        获取所有VIP等级配置
        """
        try:
            levels = VIPLevel.objects.all().order_by('level')
            
            result = []
            for level in levels:
                result.append({
                    'level': level.level,
                    'name': level.name,
                    'required_turnover': float(level.required_turnover),
                    'rebate_rate': float(level.rebate_rate),
                    'rebate_percentage': level.get_rebate_percentage(),
                    'daily_withdraw_limit': float(level.daily_withdraw_limit),
                    'daily_withdraw_times': level.daily_withdraw_times,
                    'withdraw_fee_rate': float(level.withdraw_fee_rate),
                    'withdraw_fee_percentage': level.get_withdraw_fee_percentage(),
                    'monthly_bonus': float(level.monthly_bonus),
                    'birthday_bonus': float(level.birthday_bonus),
                    'priority_support': level.priority_support,
                    'dedicated_manager': level.dedicated_manager,
                    'exclusive_promotions': level.exclusive_promotions,
                    'higher_bonus_rates': level.higher_bonus_rates,
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取VIP等级配置失败: {str(e)}")
            return []
    
    @staticmethod
    def get_user_vip_status(user) -> Dict[str, Any]:
        """
        获取用户VIP状态
        """
        try:
            # 获取或创建用户VIP状态
            vip_status, created = UserVIPStatus.objects.get_or_create(
                user=user,
                defaults={
                    'current_level': VIPLevel.objects.get(level=0),  # 默认VIP0
                    'total_turnover': Decimal('0.00'),
                    'monthly_turnover': Decimal('0.00'),
                }
            )
            
            if created:
                # 新用户，计算下一级所需流水
                VIPService._update_next_level_turnover(vip_status)
            
            # 检查是否需要升级
            VIPService.check_and_upgrade_vip(user)
            
            # 重新获取最新状态
            vip_status.refresh_from_db()
            
            return {
                'current_level': vip_status.current_level.level,
                'level_name': vip_status.current_level.name,
                'total_turnover': float(vip_status.total_turnover),
                'monthly_turnover': float(vip_status.monthly_turnover),
                'upgrade_progress': vip_status.get_upgrade_progress(),
                'next_level_turnover': float(vip_status.next_level_turnover or 0),
                'remaining_turnover': float(vip_status.get_remaining_turnover_for_upgrade()),
                'rebate_rate': float(vip_status.current_level.rebate_rate),
                'rebate_percentage': vip_status.current_level.get_rebate_percentage(),
                'daily_withdraw_limit': float(vip_status.current_level.daily_withdraw_limit),
                'daily_withdraw_times': vip_status.current_level.daily_withdraw_times,
                'daily_withdraw_used': vip_status.daily_withdraw_used,
                'daily_withdraw_amount': float(vip_status.daily_withdraw_amount),
                'withdraw_fee_rate': float(vip_status.current_level.withdraw_fee_rate),
                'withdraw_fee_percentage': vip_status.current_level.get_withdraw_fee_percentage(),
                'total_rebate_received': float(vip_status.total_rebate_received),
                'monthly_rebate_received': float(vip_status.monthly_rebate_received),
                'upgrade_time': vip_status.upgrade_time.isoformat() if vip_status.upgrade_time else None,
                'privileges': {
                    'monthly_bonus': float(vip_status.current_level.monthly_bonus),
                    'birthday_bonus': float(vip_status.current_level.birthday_bonus),
                    'priority_support': vip_status.current_level.priority_support,
                    'dedicated_manager': vip_status.current_level.dedicated_manager,
                    'exclusive_promotions': vip_status.current_level.exclusive_promotions,
                    'higher_bonus_rates': vip_status.current_level.higher_bonus_rates,
                }
            }
            
        except Exception as e:
            logger.error(f"获取用户VIP状态失败: {str(e)}")
            return {
                'current_level': 0,
                'level_name': 'VIP0',
                'total_turnover': 0,
                'monthly_turnover': 0,
                'upgrade_progress': 0,
                'next_level_turnover': 0,
                'remaining_turnover': 0,
                'rebate_rate': 0.0038,
                'rebate_percentage': 0.38,
            }
    
    @staticmethod
    def _update_next_level_turnover(vip_status: UserVIPStatus):
        """
        更新下一级所需流水
        """
        try:
            next_level = VIPLevel.objects.filter(
                level__gt=vip_status.current_level.level
            ).order_by('level').first()
            
            if next_level:
                vip_status.next_level_turnover = next_level.required_turnover
            else:
                vip_status.next_level_turnover = None  # 已达到最高等级
            
            vip_status.save()
            
        except Exception as e:
            logger.error(f"更新下一级流水失败: {str(e)}")
    
    @staticmethod
    def check_and_upgrade_vip(user) -> Dict[str, Any]:
        """
        检查并升级VIP等级
        """
        try:
            vip_status = UserVIPStatus.objects.get(user=user)
            
            # 查找符合条件的最高等级
            eligible_level = VIPLevel.objects.filter(
                required_turnover__lte=vip_status.total_turnover
            ).order_by('-level').first()
            
            if not eligible_level:
                return {'upgraded': False, 'message': '未找到符合条件的等级'}
            
            # 检查是否需要升级
            if eligible_level.level > vip_status.current_level.level:
                old_level = vip_status.current_level.level
                
                with transaction.atomic():
                    # 更新VIP等级
                    vip_status.current_level = eligible_level
                    vip_status.upgrade_time = timezone.now()
                    vip_status.save()
                    
                    # 更新下一级所需流水
                    VIPService._update_next_level_turnover(vip_status)
                    
                    # 记录升级日志
                    logger.info(f"用户 {user.phone} VIP等级升级: VIP{old_level} -> VIP{eligible_level.level}")
                    
                    # 发送升级奖励（如果有）
                    if eligible_level.monthly_bonus > 0:
                        VIPService._send_upgrade_bonus(user, eligible_level)
                
                return {
                    'upgraded': True,
                    'old_level': old_level,
                    'new_level': eligible_level.level,
                    'message': f'恭喜升级到VIP{eligible_level.level}！'
                }
            
            return {'upgraded': False, 'message': '当前等级已是最高符合条件的等级'}
            
        except UserVIPStatus.DoesNotExist:
            return {'upgraded': False, 'message': 'VIP状态不存在'}
        except Exception as e:
            logger.error(f"检查VIP升级失败: {str(e)}")
            return {'upgraded': False, 'message': f'升级检查失败: {str(e)}'}
    
    @staticmethod
    def _send_upgrade_bonus(user, vip_level: VIPLevel):
        """
        发送升级奖金
        """
        try:
            if vip_level.monthly_bonus <= 0:
                return
            
            with transaction.atomic():
                # 添加奖金到用户余额
                user_balance = user.balance
                user_balance.add_balance(
                    vip_level.monthly_bonus, 
                    'bonus', 
                    f'VIP{vip_level.level}升级奖金'
                )
                
                # 创建交易记录
                Transaction.objects.create(
                    user=user,
                    type='BONUS',
                    amount=vip_level.monthly_bonus,
                    fee=Decimal('0.00'),
                    actual_amount=vip_level.monthly_bonus,
                    status='COMPLETED',
                    reference_id=str(uuid.uuid4()),
                    description=f'VIP{vip_level.level}升级奖金',
                    metadata={
                        'bonus_type': 'vip_upgrade',
                        'vip_level': vip_level.level,
                    }
                )
                
                logger.info(f"用户 {user.phone} 获得VIP{vip_level.level}升级奖金: ₦{vip_level.monthly_bonus}")
                
        except Exception as e:
            logger.error(f"发送升级奖金失败: {str(e)}")
    
    @staticmethod
    def update_user_turnover(user, amount: Decimal, game_type: str = None):
        """
        更新用户有效流水
        """
        try:
            vip_status, created = UserVIPStatus.objects.get_or_create(
                user=user,
                defaults={
                    'current_level': VIPLevel.objects.get(level=0),
                    'total_turnover': Decimal('0.00'),
                    'monthly_turnover': Decimal('0.00'),
                }
            )
            
            # 更新流水
            vip_status.total_turnover += amount
            vip_status.monthly_turnover += amount
            vip_status.save()
            
            # 检查升级
            upgrade_result = VIPService.check_and_upgrade_vip(user)
            
            logger.debug(f"用户 {user.phone} 流水更新: +₦{amount}, 总流水: ₦{vip_status.total_turnover}")
            
            return {
                'success': True,
                'total_turnover': float(vip_status.total_turnover),
                'upgrade_result': upgrade_result
            }
            
        except Exception as e:
            logger.error(f"更新用户流水失败: {str(e)}")
            return {'success': False, 'message': f'更新失败: {str(e)}'}
    
    @staticmethod
    def can_user_withdraw(user, amount: Decimal) -> Tuple[bool, str]:
        """
        检查用户是否可以提现
        """
        try:
            vip_status = UserVIPStatus.objects.get(user=user)
            return vip_status.can_withdraw_today(amount)
            
        except UserVIPStatus.DoesNotExist:
            return False, "VIP状态不存在"
        except Exception as e:
            logger.error(f"检查提现权限失败: {str(e)}")
            return False, f"检查失败: {str(e)}"
    
    @staticmethod
    def record_user_withdrawal(user, amount: Decimal):
        """
        记录用户提现
        """
        try:
            vip_status = UserVIPStatus.objects.get(user=user)
            
            today = timezone.now().date()
            if vip_status.last_withdraw_date != today:
                vip_status.daily_withdraw_used = 0
                vip_status.daily_withdraw_amount = Decimal('0.00')
            
            vip_status.daily_withdraw_used += 1
            vip_status.daily_withdraw_amount += amount
            vip_status.last_withdraw_date = today
            vip_status.save()
            
            logger.debug(f"用户 {user.phone} 提现记录更新: ₦{amount}")
            
        except Exception as e:
            logger.error(f"记录用户提现失败: {str(e)}")
    
    @staticmethod
    def get_vip_level_comparison() -> List[Dict[str, Any]]:
        """
        获取VIP等级对比表
        """
        try:
            levels = VIPLevel.objects.all().order_by('level')
            
            result = []
            for level in levels:
                result.append({
                    'level': level.level,
                    'name': level.name,
                    'required_turnover': float(level.required_turnover),
                    'rebate_percentage': level.get_rebate_percentage(),
                    'withdraw_fee_percentage': level.get_withdraw_fee_percentage(),
                    'daily_withdraw_limit': float(level.daily_withdraw_limit),
                    'daily_withdraw_times': level.daily_withdraw_times,
                    'monthly_bonus': float(level.monthly_bonus),
                    'birthday_bonus': float(level.birthday_bonus),
                    'privileges': {
                        'priority_support': level.priority_support,
                        'dedicated_manager': level.dedicated_manager,
                        'exclusive_promotions': level.exclusive_promotions,
                        'higher_bonus_rates': level.higher_bonus_rates,
                    }
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取VIP等级对比失败: {str(e)}")
            return []


class RebateService:
    """
    返水计算服务
    """
    
    @staticmethod
    def calculate_daily_rebate(user, target_date: date = None) -> Dict[str, Any]:
        """
        计算用户每日返水
        """
        try:
            if target_date is None:
                target_date = timezone.now().date() - timedelta(days=1)  # 默认计算昨天的返水
            
            # 获取用户VIP状态
            try:
                vip_status = UserVIPStatus.objects.get(user=user)
            except UserVIPStatus.DoesNotExist:
                return {'success': False, 'message': 'VIP状态不存在'}
            
            # 检查是否已经计算过返水
            existing_record = RebateRecord.objects.filter(
                user=user, period_date=target_date
            ).first()
            
            if existing_record:
                return {
                    'success': False,
                    'message': '该日期的返水已经计算过',
                    'existing_record': {
                        'rebate_amount': float(existing_record.rebate_amount),
                        'status': existing_record.status
                    }
                }
            
            # 计算当日有效流水
            turnover_data = RebateService._calculate_daily_turnover(user, target_date)
            
            if turnover_data['total_turnover'] < Decimal('1.00'):
                return {
                    'success': False,
                    'message': '当日有效流水不足1NGN，不符合返水条件'
                }
            
            # 计算返水金额
            rebate_amount = turnover_data['total_turnover'] * vip_status.current_level.rebate_rate
            
            # 创建返水记录
            rebate_record = RebateRecord.objects.create(
                user=user,
                period_date=target_date,
                vip_level=vip_status.current_level.level,
                rebate_rate=vip_status.current_level.rebate_rate,
                total_turnover=turnover_data['total_turnover'],
                game_turnover_breakdown=turnover_data['game_breakdown'],
                rebate_amount=rebate_amount,
                status='PENDING'
            )
            
            return {
                'success': True,
                'message': '返水计算完成',
                'data': {
                    'record_id': str(rebate_record.id),
                    'period_date': target_date.isoformat(),
                    'vip_level': vip_status.current_level.level,
                    'rebate_rate': float(vip_status.current_level.rebate_rate),
                    'rebate_percentage': vip_status.current_level.get_rebate_percentage(),
                    'total_turnover': float(turnover_data['total_turnover']),
                    'rebate_amount': float(rebate_amount),
                    'game_breakdown': turnover_data['game_breakdown']
                }
            }
            
        except Exception as e:
            logger.error(f"计算每日返水失败: {str(e)}")
            return {'success': False, 'message': f'计算失败: {str(e)}'}
    
    @staticmethod
    def _calculate_daily_turnover(user, target_date: date) -> Dict[str, Any]:
        """
        计算用户当日有效流水
        """
        try:
            from apps.games.lottery11x5.models import LotteryBet as Lottery11x5Bet
            from apps.games.scratch666.models import ScratchCard
            from apps.games.superlotto.models import SuperLottoBet
            from apps.games.sports.models import SportsBetRecord
            
            # 计算日期范围
            start_datetime = timezone.make_aware(
                timezone.datetime.combine(target_date, timezone.datetime.min.time())
            )
            end_datetime = start_datetime + timedelta(days=1)
            
            game_breakdown = {}
            total_turnover = Decimal('0.00')
            
            # 11选5彩票流水
            try:
                lottery11x5_turnover = Lottery11x5Bet.objects.filter(
                    user=user,
                    created_at__gte=start_datetime,
                    created_at__lt=end_datetime,
                    status__in=['WINNING', 'LOSING', 'SETTLED']  # 已结算的投注
                ).aggregate(total=models.Sum('total_amount'))['total'] or Decimal('0.00')
                
                if lottery11x5_turnover > 0:
                    game_breakdown['11选5'] = float(lottery11x5_turnover)
                    total_turnover += lottery11x5_turnover
            except:
                pass  # 如果模型不存在，跳过
            
            # 刮刮乐流水
            try:
                scratch_turnover = ScratchCard.objects.filter(
                    user=user,
                    purchased_at__gte=start_datetime,
                    purchased_at__lt=end_datetime,
                    status__in=['SCRATCHED', 'COMPLETED']  # 已刮开的卡片
                ).aggregate(total=models.Sum('price'))['total'] or Decimal('0.00')
                
                if scratch_turnover > 0:
                    game_breakdown['刮刮乐'] = float(scratch_turnover)
                    total_turnover += scratch_turnover
            except:
                pass
            
            # 大乐透流水
            try:
                superlotto_turnover = SuperLottoBet.objects.filter(
                    user=user,
                    created_at__gte=start_datetime,
                    created_at__lt=end_datetime,
                    status__in=['WINNING', 'LOSING', 'SETTLED']  # 已结算的投注
                ).aggregate(total=models.Sum('total_amount'))['total'] or Decimal('0.00')
                
                if superlotto_turnover > 0:
                    game_breakdown['大乐透'] = float(superlotto_turnover)
                    total_turnover += superlotto_turnover
            except:
                pass
            
            # 体育博彩流水
            try:
                sports_turnover = SportsBetRecord.objects.filter(
                    user=user,
                    bet_time__gte=start_datetime,
                    bet_time__lt=end_datetime,
                    status__in=['WON', 'LOST']  # 已结算的投注
                ).aggregate(total=models.Sum('bet_amount'))['total'] or Decimal('0.00')
                
                if sports_turnover > 0:
                    game_breakdown['体育博彩'] = float(sports_turnover)
                    total_turnover += sports_turnover
            except:
                pass
            
            return {
                'total_turnover': total_turnover,
                'game_breakdown': game_breakdown
            }
            
        except Exception as e:
            logger.error(f"计算每日流水失败: {str(e)}")
            return {
                'total_turnover': Decimal('0.00'),
                'game_breakdown': {}
            }
    
    @staticmethod
    def pay_rebate(record_id: str) -> Dict[str, Any]:
        """
        发放返水
        """
        try:
            record = RebateRecord.objects.get(id=record_id)
            
            if record.status != 'PENDING':
                return {
                    'success': False,
                    'message': f'返水记录状态不正确: {record.get_status_display()}'
                }
            
            with transaction.atomic():
                # 添加返水到用户余额
                user_balance = record.user.balance
                user_balance.add_balance(
                    record.rebate_amount, 
                    'bonus', 
                    f'{record.period_date}返水'
                )
                
                # 创建交易记录
                rebate_transaction = Transaction.objects.create(
                    user=record.user,
                    type='REBATE',
                    amount=record.rebate_amount,
                    fee=Decimal('0.00'),
                    actual_amount=record.rebate_amount,
                    status='COMPLETED',
                    reference_id=str(uuid.uuid4()),
                    description=f'{record.period_date}返水',
                    metadata={
                        'rebate_record_id': str(record.id),
                        'period_date': record.period_date.isoformat(),
                        'vip_level': record.vip_level,
                        'rebate_rate': float(record.rebate_rate),
                        'total_turnover': float(record.total_turnover),
                    }
                )
                
                # 更新返水记录状态
                record.status = 'PAID'
                record.paid_at = timezone.now()
                record.transaction_id = rebate_transaction.id
                record.save()
                
                # 更新用户VIP状态中的返水统计
                vip_status = record.user.vip_status
                vip_status.total_rebate_received += record.rebate_amount
                vip_status.monthly_rebate_received += record.rebate_amount
                vip_status.save()
                
                logger.info(f"用户 {record.user.phone} 返水发放成功: ₦{record.rebate_amount}")
                
                return {
                    'success': True,
                    'message': '返水发放成功',
                    'data': {
                        'transaction_id': str(rebate_transaction.id),
                        'rebate_amount': float(record.rebate_amount),
                        'balance_after': float(user_balance.get_available_balance()),
                    }
                }
                
        except RebateRecord.DoesNotExist:
            return {'success': False, 'message': '返水记录不存在'}
        except Exception as e:
            logger.error(f"发放返水失败: {str(e)}")
            return {'success': False, 'message': f'发放失败: {str(e)}'}
    
    @staticmethod
    def batch_calculate_daily_rebates(target_date: date = None) -> Dict[str, Any]:
        """
        批量计算每日返水
        """
        try:
            if target_date is None:
                target_date = timezone.now().date() - timedelta(days=1)
            
            # 获取所有活跃用户
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            active_users = User.objects.filter(
                is_active=True,
                vip_status__isnull=False
            ).select_related('vip_status')
            
            calculated_count = 0
            paid_count = 0
            total_rebate_amount = Decimal('0.00')
            errors = []
            
            for user in active_users:
                try:
                    # 计算返水
                    calc_result = RebateService.calculate_daily_rebate(user, target_date)
                    
                    if calc_result['success']:
                        calculated_count += 1
                        rebate_amount = Decimal(str(calc_result['data']['rebate_amount']))
                        total_rebate_amount += rebate_amount
                        
                        # 自动发放返水
                        record_id = calc_result['data']['record_id']
                        pay_result = RebateService.pay_rebate(record_id)
                        
                        if pay_result['success']:
                            paid_count += 1
                        else:
                            errors.append(f"用户 {user.phone} 返水发放失败: {pay_result['message']}")
                    
                except Exception as e:
                    errors.append(f"用户 {user.phone} 返水计算失败: {str(e)}")
                    continue
            
            return {
                'success': True,
                'message': f'批量返水计算完成',
                'data': {
                    'target_date': target_date.isoformat(),
                    'total_users': len(active_users),
                    'calculated_count': calculated_count,
                    'paid_count': paid_count,
                    'total_rebate_amount': float(total_rebate_amount),
                    'errors': errors
                }
            }
            
        except Exception as e:
            logger.error(f"批量计算返水失败: {str(e)}")
            return {'success': False, 'message': f'批量计算失败: {str(e)}'}
    
    @staticmethod
    def get_user_rebate_records(user, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取用户返水记录
        """
        try:
            records = RebateRecord.objects.filter(user=user).order_by('-period_date')[:limit]
            
            result = []
            for record in records:
                result.append({
                    'record_id': str(record.id),
                    'period_date': record.period_date.isoformat(),
                    'vip_level': record.vip_level,
                    'rebate_rate': float(record.rebate_rate),
                    'rebate_percentage': float(record.rebate_rate * 100),
                    'total_turnover': float(record.total_turnover),
                    'rebate_amount': float(record.rebate_amount),
                    'game_breakdown': record.game_turnover_breakdown,
                    'status': record.status,
                    'status_display': record.get_status_display(),
                    'paid_at': record.paid_at.isoformat() if record.paid_at else None,
                    'created_at': record.created_at.isoformat(),
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取用户返水记录失败: {str(e)}")
            return []
    
    @staticmethod
    def get_rebate_statistics(start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        """
        获取返水统计数据
        """
        try:
            if not start_date:
                start_date = timezone.now().date() - timedelta(days=30)
            if not end_date:
                end_date = timezone.now().date()
            
            # 获取期间内的返水记录
            records = RebateRecord.objects.filter(
                period_date__range=[start_date, end_date],
                status='PAID'
            )
            
            # 基础统计
            total_records = records.count()
            total_amount = records.aggregate(
                total=models.Sum('rebate_amount')
            )['total'] or Decimal('0.00')
            
            total_turnover = records.aggregate(
                total=models.Sum('total_turnover')
            )['total'] or Decimal('0.00')
            
            # 按VIP等级统计
            vip_stats = records.values('vip_level').annotate(
                count=models.Count('id'),
                amount=models.Sum('rebate_amount'),
                turnover=models.Sum('total_turnover')
            ).order_by('vip_level')
            
            # 按日期统计
            daily_stats = records.values('period_date').annotate(
                count=models.Count('id'),
                amount=models.Sum('rebate_amount'),
                turnover=models.Sum('total_turnover')
            ).order_by('period_date')
            
            # 用户统计
            unique_users = records.values('user').distinct().count()
            avg_rebate_per_user = (total_amount / unique_users) if unique_users > 0 else Decimal('0.00')
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': (end_date - start_date).days + 1
                },
                'summary': {
                    'total_records': total_records,
                    'total_amount': float(total_amount),
                    'total_turnover': float(total_turnover),
                    'unique_users': unique_users,
                    'avg_rebate_per_user': float(avg_rebate_per_user),
                    'avg_rebate_rate': float(total_amount / total_turnover * 100) if total_turnover > 0 else 0
                },
                'vip_breakdown': [
                    {
                        'vip_level': stat['vip_level'],
                        'count': stat['count'],
                        'amount': float(stat['amount']),
                        'turnover': float(stat['turnover']),
                        'avg_amount': float(stat['amount'] / stat['count']) if stat['count'] > 0 else 0
                    }
                    for stat in vip_stats
                ],
                'daily_breakdown': [
                    {
                        'date': stat['period_date'].isoformat(),
                        'count': stat['count'],
                        'amount': float(stat['amount']),
                        'turnover': float(stat['turnover'])
                    }
                    for stat in daily_stats
                ]
            }
            
        except Exception as e:
            logger.error(f"获取返水统计失败: {str(e)}")
            return {
                'period': {'start_date': '', 'end_date': '', 'days': 0},
                'summary': {
                    'total_records': 0,
                    'total_amount': 0,
                    'total_turnover': 0,
                    'unique_users': 0,
                    'avg_rebate_per_user': 0,
                    'avg_rebate_rate': 0
                },
                'vip_breakdown': [],
                'daily_breakdown': []
            }

class Re
ferralService:
    """
    推荐奖励服务
    """
    
    @staticmethod
    def create_referral_relation(referrer, referee, referral_code: str) -> Dict[str, Any]:
        """
        创建推荐关系
        """
        try:
            # 检查是否已存在推荐关系
            existing_relation = ReferralRelation.objects.filter(referee=referee).first()
            if existing_relation:
                return {'success': False, 'message': '用户已有推荐关系'}
            
            # 检查推荐码是否正确
            if referrer.referral_code != referral_code:
                return {'success': False, 'message': '推荐码不正确'}
            
            # 检查不能自己推荐自己
            if referrer.id == referee.id:
                return {'success': False, 'message': '不能推荐自己'}
            
            with transaction.atomic():
                # 创建直接推荐关系（一级）
                ReferralRelation.objects.create(
                    referrer=referrer,
                    referee=referee,
                    level=1,
                    referral_code=referral_code
                )
                
                # 创建多级推荐关系（二级到七级）
                current_referrer = referrer
                for level in range(2, 8):  # 2-7级
                    # 查找上级的推荐人
                    upper_relation = ReferralRelation.objects.filter(
                        referee=current_referrer, level=1
                    ).first()
                    
                    if not upper_relation:
                        break  # 没有更上级的推荐人
                    
                    # 创建多级推荐关系
                    ReferralRelation.objects.create(
                        referrer=upper_relation.referrer,
                        referee=referee,
                        level=level,
                        referral_code=referral_code
                    )
                    
                    current_referrer = upper_relation.referrer
                
                # 更新推荐人的统计数据
                ReferralService._update_referrer_stats(referrer)
                
                logger.info(f"创建推荐关系成功: {referrer.phone} -> {referee.phone}")
                
                return {
                    'success': True,
                    'message': '推荐关系创建成功',
                    'referrer_phone': referrer.phone,
                    'referee_phone': referee.phone
                }
                
        except Exception as e:
            logger.error(f"创建推荐关系失败: {str(e)}")
            return {'success': False, 'message': f'创建失败: {str(e)}'}
    
    @staticmethod
    def _update_referrer_stats(referrer):
        """
        更新推荐人统计数据
        """
        try:
            stats, created = UserReferralStats.objects.get_or_create(user=referrer)
            
            # 统计各级推荐人数
            level_counts = {}
            for level in range(1, 8):
                count = ReferralRelation.objects.filter(
                    referrer=referrer, level=level, is_active=True
                ).count()
                level_counts[level] = count
            
            # 更新统计数据
            stats.total_referrals = sum(level_counts.values())
            stats.level1_count = level_counts[1]
            stats.level2_count = level_counts[2]
            stats.level3_count = level_counts[3]
            stats.level4_count = level_counts[4]
            stats.level5_count = level_counts[5]
            stats.level6_count = level_counts[6]
            stats.level7_count = level_counts[7]
            
            # 统计活跃推荐人数（最近30天有流水的）
            thirty_days_ago = timezone.now().date() - timedelta(days=30)
            
            active_referees = ReferralRelation.objects.filter(
                referrer=referrer,
                level=1,
                is_active=True,
                referee__last_login__gte=thirty_days_ago
            ).values_list('referee_id', flat=True)
            
            stats.active_referrals = len(active_referees)
            stats.save()
            
        except Exception as e:
            logger.error(f"更新推荐人统计失败: {str(e)}")
    
    @staticmethod
    def calculate_daily_referral_rewards(date_obj=None) -> Dict[str, Any]:
        """
        计算每日推荐奖励
        """
        try:
            if date_obj is None:
                date_obj = timezone.now().date() - timedelta(days=1)  # 默认计算昨天的奖励
            
            # 获取推荐奖励配置
            reward_configs = {}
            for config in ReferralReward.objects.all():
                reward_configs[config.level] = config.reward_rate
            
            if not reward_configs:
                return {'success': False, 'message': '推荐奖励配置不存在'}
            
            # 获取昨天有流水的用户
            start_datetime = timezone.make_aware(timezone.datetime.combine(date_obj, timezone.datetime.min.time()))
            end_datetime = start_datetime + timedelta(days=1)
            
            users_with_turnover = ReferralService._get_users_with_turnover_for_referral(start_datetime, end_datetime)
            
            total_records = 0
            success_count = 0
            total_reward_amount = Decimal('0.00')
            
            for user_id, turnover_amount in users_with_turnover.items():
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(id=user_id)
                    
                    # 获取该用户的所有推荐人
                    referral_relations = ReferralRelation.objects.filter(
                        referee=user, is_active=True
                    ).select_related('referrer')
                    
                    for relation in referral_relations:
                        # 检查是否已经计算过
                        existing_record = ReferralRewardRecord.objects.filter(
                            referrer=relation.referrer,
                            referee=user,
                            period_date=date_obj
                        ).first()
                        
                        if existing_record:
                            continue  # 已经计算过，跳过
                        
                        # 获取奖励比例
                        reward_rate = reward_configs.get(relation.level, Decimal('0.00'))
                        if reward_rate <= 0:
                            continue
                        
                        # 计算奖励金额
                        reward_amount = turnover_amount * reward_rate
                        
                        if reward_amount <= 0:
                            continue
                        
                        # 创建推荐奖励记录
                        with transaction.atomic():
                            reward_record = ReferralRewardRecord.objects.create(
                                referrer=relation.referrer,
                                referee=user,
                                period_date=date_obj,
                                referral_level=relation.level,
                                reward_rate=reward_rate,
                                referee_turnover=turnover_amount,
                                reward_amount=reward_amount,
                                status='PENDING'
                            )
                            
                            total_records += 1
                            success_count += 1
                            total_reward_amount += reward_amount
                            
                            logger.info(f"推荐奖励计算: {relation.referrer.phone} <- {user.phone} (L{relation.level}) ₦{reward_amount}")
                    
                except Exception as e:
                    logger.error(f"计算用户推荐奖励失败 (用户ID: {user_id}): {str(e)}")
                    continue
            
            logger.info(f"{date_obj}推荐奖励计算完成: {success_count}条记录, 总金额₦{total_reward_amount}")
            
            return {
                'success': True,
                'message': '推荐奖励计算完成',
                'data': {
                    'date': date_obj.isoformat(),
                    'total_records': total_records,
                    'success_count': success_count,
                    'total_reward_amount': float(total_reward_amount),
                }
            }
            
        except Exception as e:
            logger.error(f"计算推荐奖励失败: {str(e)}")
            return {'success': False, 'message': f'计算失败: {str(e)}'}
    
    @staticmethod
    def _get_users_with_turnover_for_referral(start_datetime, end_datetime) -> Dict[str, Decimal]:
        """
        获取指定时间段内有流水的用户及其流水金额
        """
        try:
            user_turnover = {}
            
            # 11选5彩票流水
            try:
                from apps.games.lottery11x5.models import LotteryBet as Lottery11x5Bet
                bets = Lottery11x5Bet.objects.filter(
                    created_at__gte=start_datetime,
                    created_at__lt=end_datetime,
                    status__in=['WINNING', 'LOSING', 'SETTLED']
                ).values('user_id').annotate(total=models.Sum('total_amount'))
                
                for bet in bets:
                    user_id = str(bet['user_id'])
                    amount = bet['total'] or Decimal('0.00')
                    user_turnover[user_id] = user_turnover.get(user_id, Decimal('0.00')) + amount
                    
            except Exception as e:
                logger.error(f"获取11选5推荐流水失败: {str(e)}")
            
            # 刮刮乐流水
            try:
                from apps.games.scratch666.models import ScratchCard
                cards = ScratchCard.objects.filter(
                    purchased_at__gte=start_datetime,
                    purchased_at__lt=end_datetime,
                    status__in=['SCRATCHED', 'COMPLETED']
                ).values('user_id').annotate(total=models.Sum('price'))
                
                for card in cards:
                    user_id = str(card['user_id'])
                    amount = card['total'] or Decimal('0.00')
                    user_turnover[user_id] = user_turnover.get(user_id, Decimal('0.00')) + amount
                    
            except Exception as e:
                logger.error(f"获取刮刮乐推荐流水失败: {str(e)}")
            
            # 大乐透流水
            try:
                from apps.games.superlotto.models import SuperLottoBet
                bets = SuperLottoBet.objects.filter(
                    created_at__gte=start_datetime,
                    created_at__lt=end_datetime,
                    status__in=['WINNING', 'LOSING', 'SETTLED']
                ).values('user_id').annotate(total=models.Sum('total_amount'))
                
                for bet in bets:
                    user_id = str(bet['user_id'])
                    amount = bet['total'] or Decimal('0.00')
                    user_turnover[user_id] = user_turnover.get(user_id, Decimal('0.00')) + amount
                    
            except Exception as e:
                logger.error(f"获取大乐透推荐流水失败: {str(e)}")
            
            # 体育博彩流水
            try:
                from apps.games.sports.models import SportsBetRecord
                bets = SportsBetRecord.objects.filter(
                    bet_time__gte=start_datetime,
                    bet_time__lt=end_datetime,
                    status__in=['WON', 'LOST']
                ).values('user_id').annotate(total=models.Sum('bet_amount'))
                
                for bet in bets:
                    user_id = str(bet['user_id'])
                    amount = bet['total'] or Decimal('0.00')
                    user_turnover[user_id] = user_turnover.get(user_id, Decimal('0.00')) + amount
                    
            except Exception as e:
                logger.error(f"获取体育博彩推荐流水失败: {str(e)}")
            
            return user_turnover
            
        except Exception as e:
            logger.error(f"获取推荐流水失败: {str(e)}")
            return {}
    
    @staticmethod
    def process_referral_reward_payment(record_id: str) -> Dict[str, Any]:
        """
        处理推荐奖励发放
        """
        try:
            try:
                record = ReferralRewardRecord.objects.get(id=record_id)
            except ReferralRewardRecord.DoesNotExist:
                return {'success': False, 'message': '推荐奖励记录不存在'}
            
            if record.status != 'PENDING':
                return {'success': False, 'message': f'推荐奖励记录状态不正确: {record.status}'}
            
            if record.reward_amount <= 0:
                record.status = 'CANCELLED'
                record.remark = '奖励金额为0，取消发放'
                record.save()
                return {'success': False, 'message': '奖励金额为0'}
            
            with transaction.atomic():
                # 添加奖励到推荐人余额
                user_balance = record.referrer.balance
                user_balance.add_balance(
                    record.reward_amount, 
                    'bonus', 
                    f'{record.period_date}推荐奖励(L{record.referral_level})'
                )
                
                # 创建交易记录
                transaction_obj = Transaction.objects.create(
                    user=record.referrer,
                    type='REFERRAL_REWARD',
                    amount=record.reward_amount,
                    fee=Decimal('0.00'),
                    actual_amount=record.reward_amount,
                    status='COMPLETED',
                    reference_id=str(uuid.uuid4()),
                    description=f'{record.period_date}推荐奖励(L{record.referral_level})',
                    metadata={
                        'referral_record_id': str(record.id),
                        'period_date': record.period_date.isoformat(),
                        'referral_level': record.referral_level,
                        'reward_rate': float(record.reward_rate),
                        'referee_turnover': float(record.referee_turnover),
                        'referee_phone': record.referee.phone,
                    }
                )
                
                # 更新推荐奖励记录
                record.status = 'PAID'
                record.paid_at = timezone.now()
                record.transaction_id = transaction_obj.id
                record.save()
                
                # 更新推荐人的奖励统计
                referral_stats, created = UserReferralStats.objects.get_or_create(user=record.referrer)
                referral_stats.total_reward_earned += record.reward_amount
                referral_stats.monthly_reward_earned += record.reward_amount
                referral_stats.save()
                
                logger.info(f"推荐奖励发放成功: {record.referrer.phone} <- {record.referee.phone} (L{record.referral_level}) ₦{record.reward_amount}")
                
                return {
                    'success': True,
                    'message': '推荐奖励发放成功',
                    'data': {
                        'record_id': str(record.id),
                        'referrer_id': str(record.referrer.id),
                        'reward_amount': float(record.reward_amount),
                        'transaction_id': str(transaction_obj.id),
                        'paid_at': record.paid_at.isoformat(),
                    }
                }
                
        except Exception as e:
            logger.error(f"处理推荐奖励发放失败: {str(e)}")
            return {'success': False, 'message': f'发放失败: {str(e)}'}
    
    @staticmethod
    def batch_process_referral_reward_payment() -> Dict[str, Any]:
        """
        批量处理推荐奖励发放
        """
        try:
            # 获取所有待发放的推荐奖励记录
            pending_records = ReferralRewardRecord.objects.filter(status='PENDING')
            
            total_records = pending_records.count()
            processed_count = 0
            success_count = 0
            total_paid_amount = Decimal('0.00')
            
            for record in pending_records:
                try:
                    result = ReferralService.process_referral_reward_payment(str(record.id))
                    
                    if result['success']:
                        success_count += 1
                        total_paid_amount += Decimal(str(result['data']['reward_amount']))
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"批量发放推荐奖励失败 (记录ID: {record.id}): {str(e)}")
                    continue
            
            logger.info(f"推荐奖励批量发放完成: {success_count}/{total_records}条, 总金额₦{total_paid_amount}")
            
            return {
                'success': True,
                'message': '批量发放完成',
                'data': {
                    'total_records': total_records,
                    'processed_count': processed_count,
                    'success_count': success_count,
                    'total_paid_amount': float(total_paid_amount),
                }
            }
            
        except Exception as e:
            logger.error(f"批量发放推荐奖励失败: {str(e)}")
            return {'success': False, 'message': f'批量发放失败: {str(e)}'}
    
    @staticmethod
    def get_user_referral_team(user, level: int = None) -> Dict[str, Any]:
        """
        获取用户推荐团队信息
        """
        try:
            # 获取推荐统计
            try:
                stats = UserReferralStats.objects.get(user=user)
            except UserReferralStats.DoesNotExist:
                stats = UserReferralStats.objects.create(user=user)
            
            # 获取推荐关系
            relations_query = ReferralRelation.objects.filter(
                referrer=user, is_active=True
            ).select_related('referee')
            
            if level:
                relations_query = relations_query.filter(level=level)
            
            relations = relations_query.order_by('level', '-created_at')
            
            # 构建团队数据
            team_data = []
            for relation in relations:
                referee = relation.referee
                
                # 获取下级用户的流水统计
                try:
                    referee_vip = UserVIPStatus.objects.get(user=referee)
                    total_turnover = referee_vip.total_turnover
                    monthly_turnover = referee_vip.monthly_turnover
                except UserVIPStatus.DoesNotExist:
                    total_turnover = Decimal('0.00')
                    monthly_turnover = Decimal('0.00')
                
                # 获取该下级贡献的奖励
                total_contribution = ReferralRewardRecord.objects.filter(
                    referrer=user,
                    referee=referee,
                    status='PAID'
                ).aggregate(total=models.Sum('reward_amount'))['total'] or Decimal('0.00')
                
                team_data.append({
                    'user_id': str(referee.id),
                    'phone': referee.phone,
                    'username': referee.username,
                    'level': relation.level,
                    'join_date': relation.created_at.isoformat(),
                    'total_turnover': float(total_turnover),
                    'monthly_turnover': float(monthly_turnover),
                    'total_contribution': float(total_contribution),
                    'is_active': referee.last_login and (timezone.now() - referee.last_login).days <= 7,
                })
            
            # 获取各级统计
            level_stats = []
            for level in range(1, 8):
                count = getattr(stats, f'level{level}_count', 0)
                
                # 计算该级别的总贡献
                level_contribution = ReferralRewardRecord.objects.filter(
                    referrer=user,
                    referral_level=level,
                    status='PAID'
                ).aggregate(total=models.Sum('reward_amount'))['total'] or Decimal('0.00')
                
                level_stats.append({
                    'level': level,
                    'count': count,
                    'contribution': float(level_contribution),
                })
            
            return {
                'success': True,
                'data': {
                    'referral_code': user.referral_code,
                    'total_referrals': stats.total_referrals,
                    'active_referrals': stats.active_referrals,
                    'total_reward_earned': float(stats.total_reward_earned),
                    'monthly_reward_earned': float(stats.monthly_reward_earned),
                    'team_total_turnover': float(stats.team_total_turnover),
                    'team_monthly_turnover': float(stats.team_monthly_turnover),
                    'level_stats': level_stats,
                    'team_members': team_data,
                }
            }
            
        except Exception as e:
            logger.error(f"获取推荐团队信息失败: {str(e)}")
            return {'success': False, 'message': f'获取失败: {str(e)}'}
    
    @staticmethod
    def get_user_referral_rewards(user, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取用户推荐奖励记录
        """
        try:
            records = ReferralRewardRecord.objects.filter(
                referrer=user
            ).select_related('referee').order_by('-period_date', '-created_at')[:limit]
            
            result = []
            for record in records:
                result.append({
                    'record_id': str(record.id),
                    'period_date': record.period_date.isoformat(),
                    'referee_phone': record.referee.phone,
                    'referral_level': record.referral_level,
                    'reward_rate': float(record.reward_rate),
                    'reward_percentage': float(record.reward_rate * 100),
                    'referee_turnover': float(record.referee_turnover),
                    'reward_amount': float(record.reward_amount),
                    'status': record.status,
                    'status_display': record.get_status_display(),
                    'paid_at': record.paid_at.isoformat() if record.paid_at else None,
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取推荐奖励记录失败: {str(e)}")
            return []
    
    @staticmethod
    def generate_referral_link(user) -> Dict[str, Any]:
        """
        生成推荐链接和二维码
        """
        try:
            from django.conf import settings
            import qrcode
            from io import BytesIO
            import base64
            
            # 生成推荐链接
            base_url = getattr(settings, 'FRONTEND_URL', 'https://example.com')
            referral_link = f"{base_url}/register?ref={user.referral_code}"
            
            # 生成二维码
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(referral_link)
            qr.make(fit=True)
            
            # 创建二维码图片
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # 转换为base64
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                'success': True,
                'data': {
                    'referral_code': user.referral_code,
                    'referral_link': referral_link,
                    'qr_code': f"data:image/png;base64,{qr_base64}",
                }
            }
            
        except Exception as e:
            logger.error(f"生成推荐链接失败: {str(e)}")
            return {'success': False, 'message': f'生成失败: {str(e)}'}
    
    @staticmethod
    def get_referral_statistics(start_date=None, end_date=None) -> Dict[str, Any]:
        """
        获取推荐奖励统计数据
        """
        try:
            if not start_date:
                start_date = timezone.now().date() - timedelta(days=30)
            if not end_date:
                end_date = timezone.now().date()
            
            # 获取时间范围内的推荐奖励记录
            records = ReferralRewardRecord.objects.filter(
                period_date__gte=start_date,
                period_date__lte=end_date
            )
            
            # 计算总体统计
            total_stats = records.aggregate(
                total_amount=models.Sum('reward_amount'),
                total_records=models.Count('id'),
                paid_amount=models.Sum('reward_amount', filter=models.Q(status='PAID')),
                paid_records=models.Count('id', filter=models.Q(status='PAID')),
                unique_referrers=models.Count('referrer', distinct=True),
                unique_referees=models.Count('referee', distinct=True),
            )
            
            # 计算每日统计
            daily_stats = []
            current_date = start_date
            while current_date <= end_date:
                day_records = records.filter(period_date=current_date)
                day_stats = day_records.aggregate(
                    total_amount=models.Sum('reward_amount') or Decimal('0.00'),
                    total_records=models.Count('id'),
                    paid_amount=models.Sum('reward_amount', filter=models.Q(status='PAID')) or Decimal('0.00'),
                    paid_records=models.Count('id', filter=models.Q(status='PAID')),
                )
                
                daily_stats.append({
                    'date': current_date.isoformat(),
                    'total_amount': float(day_stats['total_amount']),
                    'total_records': day_stats['total_records'],
                    'paid_amount': float(day_stats['paid_amount']),
                    'paid_records': day_stats['paid_records'],
                })
                
                current_date += timedelta(days=1)
            
            # 计算各级奖励分布
            level_distribution = {}
            for level in range(1, 8):  # L1-L7
                level_records = records.filter(referral_level=level)
                level_stats = level_records.aggregate(
                    total_amount=models.Sum('reward_amount') or Decimal('0.00'),
                    total_records=models.Count('id'),
                    unique_referrers=models.Count('referrer', distinct=True),
                )
                
                level_distribution[f'L{level}'] = {
                    'total_amount': float(level_stats['total_amount']),
                    'total_records': level_stats['total_records'],
                    'unique_referrers': level_stats['unique_referrers'],
                }
            
            return {
                'success': True,
                'data': {
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'days': (end_date - start_date).days + 1,
                    },
                    'total_stats': {
                        'total_amount': float(total_stats['total_amount'] or Decimal('0.00')),
                        'total_records': total_stats['total_records'],
                        'paid_amount': float(total_stats['paid_amount'] or Decimal('0.00')),
                        'paid_records': total_stats['paid_records'],
                        'unique_referrers': total_stats['unique_referrers'],
                        'unique_referees': total_stats['unique_referees'],
                    },
                    'daily_stats': daily_stats,
                    'level_distribution': level_distribution,
                }
            }
            
        except Exception as e:
            logger.error(f"获取推荐奖励统计失败: {str(e)}")
            return {'success': False, 'message': f'获取统计失败: {str(e)}'}
    
    @staticmethod
    def get_pending_rebate_records() -> List[str]:
        """
        获取待处理的返水记录ID列表
        """
        try:
            records = RebateRecord.objects.filter(status='PENDING').values_list('id', flat=True)
            return [str(record_id) for record_id in records]
        except Exception as e:
            logger.error(f"获取待处理返水记录失败: {str(e)}")
            return []    

    @staticmethod
    def calculate_comprehensive_reward(user, period_date: date = None) -> Dict[str, Any]:
        """
        计算用户综合奖励（返水+推荐奖励+其他奖励）
        """
        try:
            if period_date is None:
                period_date = timezone.now().date() - timedelta(days=1)
            
            # 检查是否已经计算过
            existing_calculation = RewardCalculation.objects.filter(
                user=user, period_date=period_date, period_type='DAILY'
            ).first()
            
            if existing_calculation:
                return {
                    'success': False,
                    'message': '该日期的综合奖励已经计算过',
                    'existing_calculation': existing_calculation.get_reward_breakdown()
                }
            
            # 获取用户VIP状态
            try:
                vip_status = UserVIPStatus.objects.get(user=user)
            except UserVIPStatus.DoesNotExist:
                return {'success': False, 'message': 'VIP状态不存在'}
            
            # 计算当日有效流水
            turnover_data = RebateService._calculate_daily_turnover(user, period_date)
            total_turnover = turnover_data['total_turnover']
            
            # 计算返水金额
            rebate_amount = Decimal('0.00')
            if total_turnover >= Decimal('1.00'):  # 最低1NGN起计算返水
                rebate_amount = total_turnover * vip_status.current_level.rebate_rate
            
            # 计算推荐奖励金额
            referral_reward_amount = Decimal('0.00')
            referral_breakdown = {}
            
            try:
                referral_records = ReferralRewardRecord.objects.filter(
                    referrer=user, period_date=period_date, status='PAID'
                )
                
                for record in referral_records:
                    referral_reward_amount += record.reward_amount
                    level_key = f'L{record.referral_level}'
                    referral_breakdown[level_key] = referral_breakdown.get(level_key, 0) + float(record.reward_amount)
                    
            except Exception as e:
                logger.error(f"计算推荐奖励失败: {str(e)}")
            
            # 计算其他奖励（生日奖金、月度奖金等）
            bonus_amount = Decimal('0.00')
            today = timezone.now().date()
            
            # 检查生日奖金
            if (user.birthday and user.birthday.month == period_date.month and 
                user.birthday.day == period_date.day):
                bonus_amount += vip_status.current_level.birthday_bonus
            
            # 检查月度奖金（每月1日）
            if period_date.day == 1:
                bonus_amount += vip_status.current_level.monthly_bonus
            
            # 创建综合奖励计算记录
            with transaction.atomic():
                reward_calculation = RewardCalculation.objects.create(
                    user=user,
                    period_date=period_date,
                    period_type='DAILY',
                    vip_level=vip_status.current_level.level,
                    total_turnover=total_turnover,
                    rebate_rate=vip_status.current_level.rebate_rate,
                    rebate_amount=rebate_amount,
                    referral_reward_amount=referral_reward_amount,
                    referral_reward_breakdown=referral_breakdown,
                    bonus_amount=bonus_amount,
                    status='CALCULATED'
                )
                
                logger.info(f"用户 {user.phone} {period_date}综合奖励计算完成: 返水₦{rebate_amount}, 推荐₦{referral_reward_amount}, 奖金₦{bonus_amount}, 总计₦{reward_calculation.total_reward_amount}")
                
                return {
                    'success': True,
                    'message': '综合奖励计算完成',
                    'data': {
                        'calculation_id': str(reward_calculation.id),
                        'period_date': period_date.isoformat(),
                        'vip_level': vip_status.current_level.level,
                        'total_turnover': float(total_turnover),
                        'rebate_amount': float(rebate_amount),
                        'referral_reward_amount': float(referral_reward_amount),
                        'bonus_amount': float(bonus_amount),
                        'total_reward_amount': float(reward_calculation.total_reward_amount),
                        'reward_breakdown': reward_calculation.get_reward_breakdown()
                    }
                }
                
        except Exception as e:
            logger.error(f"计算综合奖励失败: {str(e)}")
            return {'success': False, 'message': f'计算失败: {str(e)}'}
    
    @staticmethod
    def get_user_reward_calculations(user, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取用户奖励计算记录
        """
        try:
            calculations = RewardCalculation.objects.filter(
                user=user
            ).order_by('-period_date', '-created_at')[:limit]
            
            result = []
            for calc in calculations:
                result.append({
                    'calculation_id': str(calc.id),
                    'period_date': calc.period_date.isoformat(),
                    'period_type': calc.period_type,
                    'vip_level': calc.vip_level,
                    'total_turnover': float(calc.total_turnover),
                    'rebate_amount': float(calc.rebate_amount),
                    'referral_reward_amount': float(calc.referral_reward_amount),
                    'bonus_amount': float(calc.bonus_amount),
                    'total_reward_amount': float(calc.total_reward_amount),
                    'status': calc.status,
                    'paid_at': calc.paid_at.isoformat() if calc.paid_at else None,
                    'reward_breakdown': calc.get_reward_breakdown(),
                    'created_at': calc.created_at.isoformat(),
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取用户奖励计算记录失败: {str(e)}")
            return []