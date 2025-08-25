"""
统一返水奖励系统Celery任务
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def calculate_daily_rebate():
    """
    计算每日返水任务
    每天凌晨执行，计算前一天的返水
    """
    try:
        from .services import RebateService
        
        yesterday = timezone.now().date() - timedelta(days=1)
        result = RebateService.batch_calculate_daily_rebates(yesterday)
        
        if result['success']:
            logger.info(f"每日返水计算成功: {yesterday}, {result['data']['calculated_count']}用户, ₦{result['data']['total_rebate_amount']}")
            return {
                "success": True,
                "date": yesterday.isoformat(),
                "users_processed": result['data']['calculated_count'],
                "total_amount": result['data']['total_rebate_amount'],
                "message": f"每日返水计算成功"
            }
        else:
            logger.error(f"每日返水计算失败: {result['message']}")
            return {"success": False, "message": result['message']}
        
    except Exception as e:
        logger.error(f"每日返水计算任务出错: {str(e)}")
        return {"success": False, "message": f"计算出错: {str(e)}"}


@shared_task
def calculate_comprehensive_rewards():
    """
    计算综合奖励任务（返水+推荐奖励+其他奖励）
    每天凌晨执行，使用RewardCalculation模型记录个人返水金额、推荐奖励金额和总奖励
    """
    try:
        from .services import RebateService
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        yesterday = timezone.now().date() - timedelta(days=1)
        
        # 获取所有活跃用户
        active_users = User.objects.filter(is_active=True)
        
        calculated_count = 0
        total_reward_amount = 0
        
        for user in active_users:
            try:
                result = RebateService.calculate_comprehensive_reward(user, yesterday)
                
                if result['success']:
                    calculated_count += 1
                    total_reward_amount += result['data']['total_reward_amount']
                    
            except Exception as e:
                logger.error(f"计算用户综合奖励失败 (用户ID: {user.id}): {str(e)}")
                continue
        
        logger.info(f"综合奖励计算完成: {yesterday}, {calculated_count}用户, 总奖励₦{total_reward_amount}")
        
        return {
            "success": True,
            "date": yesterday.isoformat(),
            "users_processed": calculated_count,
            "total_reward_amount": total_reward_amount,
            "message": "综合奖励计算成功"
        }
        
    except Exception as e:
        logger.error(f"综合奖励计算任务出错: {str(e)}")
        return {"success": False, "message": f"计算出错: {str(e)}"}


@shared_task
def calculate_daily_referral_rewards():
    """
    计算每日推荐奖励任务
    每天凌晨执行，计算前一天的推荐奖励
    """
    try:
        from .services import ReferralService
        
        yesterday = timezone.now().date() - timedelta(days=1)
        result = ReferralService.calculate_daily_referral_rewards(yesterday)
        
        if result['success']:
            logger.info(f"每日推荐奖励计算成功: {yesterday}, {result['data']['success_count']}条记录, ₦{result['data']['total_reward_amount']}")
            return {
                "success": True,
                "date": yesterday.isoformat(),
                "records_processed": result['data']['success_count'],
                "total_amount": result['data']['total_reward_amount'],
                "message": f"每日推荐奖励计算成功"
            }
        else:
            logger.error(f"每日推荐奖励计算失败: {result['message']}")
            return {"success": False, "message": result['message']}
        
    except Exception as e:
        logger.error(f"每日推荐奖励计算任务出错: {str(e)}")
        return {"success": False, "message": f"计算出错: {str(e)}"}


@shared_task
def process_rebate_payment():
    """
    处理返水发放任务
    每天上午10点执行，发放已计算的返水
    """
    try:
        from .services import RebateService
        
        # 批量发放待处理的返水
        pending_records = RebateService.get_pending_rebate_records()
        
        success_count = 0
        total_paid_amount = 0
        
        for record_id in pending_records:
            try:
                result = RebateService.pay_rebate(record_id)
                if result['success']:
                    success_count += 1
                    total_paid_amount += result['data']['rebate_amount']
            except Exception as e:
                logger.error(f"发放返水失败 (记录ID: {record_id}): {str(e)}")
                continue
        
        logger.info(f"返水发放完成: {success_count}条记录, 总金额₦{total_paid_amount}")
        
        return {
            "success": True,
            "records_processed": success_count,
            "total_amount": total_paid_amount,
            "message": f"返水发放成功"
        }
        
    except Exception as e:
        logger.error(f"返水发放任务出错: {str(e)}")
        return {"success": False, "message": f"发放出错: {str(e)}"}


@shared_task
def process_referral_reward_payment():
    """
    处理推荐奖励发放任务
    每天上午10点执行，发放已计算的推荐奖励
    """
    try:
        from .services import ReferralService
        
        result = ReferralService.batch_process_referral_reward_payment()
        
        if result['success']:
            logger.info(f"推荐奖励发放成功: {result['data']['success_count']}条, ₦{result['data']['total_paid_amount']}")
            return {
                "success": True,
                "records_processed": result['data']['success_count'],
                "total_amount": result['data']['total_paid_amount'],
                "message": f"推荐奖励发放成功"
            }
        else:
            logger.error(f"推荐奖励发放失败: {result['message']}")
            return {"success": False, "message": result['message']}
        
    except Exception as e:
        logger.error(f"推荐奖励发放任务出错: {str(e)}")
        return {"success": False, "message": f"发放出错: {str(e)}"}


@shared_task
def reset_monthly_statistics():
    """
    重置月度统计任务
    每月1日凌晨执行，重置月度统计数据
    """
    try:
        from .models import UserVIPStatus, UserReferralStats
        
        # 重置VIP月度统计
        vip_update_count = UserVIPStatus.objects.update(
            monthly_turnover=0,
            monthly_rebate_received=0
        )
        
        # 重置推荐月度统计
        referral_update_count = UserReferralStats.objects.update(
            monthly_reward_earned=0,
            team_monthly_turnover=0
        )
        
        logger.info(f"月度统计重置成功: {vip_update_count}个VIP状态, {referral_update_count}个推荐统计")
        
        return {
            "success": True,
            "vip_reset_count": vip_update_count,
            "referral_reset_count": referral_update_count,
            "message": "月度统计重置成功"
        }
        
    except Exception as e:
        logger.error(f"重置月度统计任务出错: {str(e)}")
        return {"success": False, "message": f"重置出错: {str(e)}"}


@shared_task
def update_reward_statistics():
    """
    更新奖励统计任务
    每天凌晨执行，更新前一天的奖励统计
    """
    try:
        from .models import RebateRecord, ReferralRewardRecord, RewardStatistics, UserVIPStatus
        from django.db.models import Sum, Count
        
        yesterday = timezone.now().date() - timedelta(days=1)
        
        # 获取返水统计
        rebate_stats = RebateRecord.objects.filter(period_date=yesterday).aggregate(
            total_amount=Sum('rebate_amount') or 0,
            total_users=Count('user', distinct=True)
        )
        
        # 获取推荐奖励统计
        referral_stats = ReferralRewardRecord.objects.filter(period_date=yesterday).aggregate(
            total_amount=Sum('reward_amount') or 0,
            total_users=Count('referrer', distinct=True)
        )
        
        # 获取VIP等级分布
        vip_distribution = {}
        for level in range(8):  # VIP0-VIP7
            user_count = UserVIPStatus.objects.filter(current_level__level=level).count()
            vip_distribution[f'VIP{level}'] = user_count
        
        # 创建或更新统计记录
        stats, created = RewardStatistics.objects.update_or_create(
            date=yesterday,
            defaults={
                'total_rebate_amount': rebate_stats['total_amount'],
                'total_rebate_users': rebate_stats['total_users'],
                'total_referral_reward': referral_stats['total_amount'],
                'total_referral_users': referral_stats['total_users'],
                'vip_distribution': vip_distribution,
                'total_reward_amount': rebate_stats['total_amount'] + referral_stats['total_amount']
            }
        )
        
        logger.info(f"奖励统计更新成功: {yesterday}, 返水₦{rebate_stats['total_amount']}, 推荐奖励₦{referral_stats['total_amount']}")
        
        return {
            "success": True,
            "date": yesterday.isoformat(),
            "total_rebate": float(rebate_stats['total_amount']),
            "total_referral": float(referral_stats['total_amount']),
            "total_reward": float(rebate_stats['total_amount'] + referral_stats['total_amount']),
            "message": "奖励统计更新成功"
        }
        
    except Exception as e:
        logger.error(f"更新奖励统计任务出错: {str(e)}")
        return {"success": False, "message": f"更新出错: {str(e)}"}


@shared_task
def send_birthday_bonus():
    """
    发送生日奖金任务
    每天凌晨执行，检查当天生日的用户并发送奖金
    """
    try:
        from django.contrib.auth import get_user_model
        from .models import UserVIPStatus
        from apps.finance.models import Transaction
        import uuid
        from decimal import Decimal
        
        User = get_user_model()
        today = timezone.now().date()
        
        # 查找今天生日的用户
        birthday_users = User.objects.filter(
            birthday__month=today.month,
            birthday__day=today.day,
            is_active=True
        ).select_related('vip_status')
        
        bonus_count = 0
        total_bonus = Decimal('0.00')
        
        for user in birthday_users:
            try:
                # 获取用户VIP等级
                vip_status = getattr(user, 'vip_status', None)
                if not vip_status:
                    continue
                
                # 获取生日奖金
                birthday_bonus = vip_status.current_level.birthday_bonus
                if birthday_bonus <= 0:
                    continue
                
                # 发放奖金
                user_balance = user.balance
                user_balance.add_balance(
                    birthday_bonus, 
                    'bonus', 
                    f'VIP{vip_status.current_level.level}生日奖金'
                )
                
                # 创建交易记录
                Transaction.objects.create(
                    user=user,
                    type='BONUS',
                    amount=birthday_bonus,
                    fee=Decimal('0.00'),
                    actual_amount=birthday_bonus,
                    status='COMPLETED',
                    reference_id=str(uuid.uuid4()),
                    description=f'VIP{vip_status.current_level.level}生日奖金',
                    metadata={
                        'bonus_type': 'birthday',
                        'vip_level': vip_status.current_level.level,
                    }
                )
                
                bonus_count += 1
                total_bonus += birthday_bonus
                
                logger.info(f"用户 {user.phone} 获得生日奖金: ₦{birthday_bonus}")
                
            except Exception as e:
                logger.error(f"发送生日奖金失败 (用户ID: {user.id}): {str(e)}")
                continue
        
        logger.info(f"生日奖金发放完成: {bonus_count}用户, 总金额₦{total_bonus}")
        
        return {
            "success": True,
            "bonus_count": bonus_count,
            "total_bonus": float(total_bonus),
            "date": today.isoformat(),
            "message": "生日奖金发放完成"
        }
        
    except Exception as e:
        logger.error(f"发送生日奖金任务出错: {str(e)}")
        return {"success": False, "message": f"发放出错: {str(e)}"}


@shared_task
def send_monthly_bonus():
    """
    发送月度奖金任务
    每月1日凌晨执行，发送月度奖金
    """
    try:
        from .models import UserVIPStatus
        from apps.finance.models import Transaction
        import uuid
        from decimal import Decimal
        
        today = timezone.now().date()
        
        # 只在每月1日执行
        if today.day != 1:
            return {"success": False, "message": "只在每月1日执行"}
        
        # 查找有月度奖金的VIP用户
        vip_users = UserVIPStatus.objects.filter(
            current_level__monthly_bonus__gt=0,
            user__is_active=True
        ).select_related('user', 'current_level')
        
        bonus_count = 0
        total_bonus = Decimal('0.00')
        
        for vip_status in vip_users:
            try:
                user = vip_status.user
                monthly_bonus = vip_status.current_level.monthly_bonus
                
                # 发放奖金
                user_balance = user.balance
                user_balance.add_balance(
                    monthly_bonus, 
                    'bonus', 
                    f'VIP{vip_status.current_level.level}月度奖金'
                )
                
                # 创建交易记录
                Transaction.objects.create(
                    user=user,
                    type='BONUS',
                    amount=monthly_bonus,
                    fee=Decimal('0.00'),
                    actual_amount=monthly_bonus,
                    status='COMPLETED',
                    reference_id=str(uuid.uuid4()),
                    description=f'VIP{vip_status.current_level.level}月度奖金',
                    metadata={
                        'bonus_type': 'monthly',
                        'vip_level': vip_status.current_level.level,
                        'month': today.month,
                        'year': today.year,
                    }
                )
                
                bonus_count += 1
                total_bonus += monthly_bonus
                
                logger.info(f"用户 {user.phone} 获得月度奖金: ₦{monthly_bonus}")
                
            except Exception as e:
                logger.error(f"发送月度奖金失败 (用户ID: {vip_status.user.id}): {str(e)}")
                continue
        
        logger.info(f"月度奖金发放完成: {bonus_count}用户, 总金额₦{total_bonus}")
        
        return {
            "success": True,
            "bonus_count": bonus_count,
            "total_bonus": float(total_bonus),
            "date": today.isoformat(),
            "message": "月度奖金发放完成"
        }
        
    except Exception as e:
        logger.error(f"发送月度奖金任务出错: {str(e)}")
        return {"success": False, "message": f"发放出错: {str(e)}"}


@shared_task
def cleanup_old_records():
    """
    清理旧记录任务
    每月执行，清理超过1年的记录
    """
    try:
        from .models import RebateRecord, ReferralRewardRecord
        from datetime import timedelta
        
        # 删除1年前的数据
        one_year_ago = timezone.now().date() - timedelta(days=365)
        
        # 删除旧的返水记录
        rebate_deleted = RebateRecord.objects.filter(period_date__lt=one_year_ago).delete()[0]
        
        # 删除旧的推荐奖励记录
        referral_deleted = ReferralRewardRecord.objects.filter(period_date__lt=one_year_ago).delete()[0]
        
        logger.info(f"清理旧奖励记录完成: 返水{rebate_deleted}条, 推荐奖励{referral_deleted}条")
        
        return {
            "success": True,
            "rebate_deleted": rebate_deleted,
            "referral_deleted": referral_deleted,
            "message": "清理旧记录完成"
        }
        
    except Exception as e:
        logger.error(f"清理旧记录任务出错: {str(e)}")
        return {"success": False, "message": f"清理出错: {str(e)}"}