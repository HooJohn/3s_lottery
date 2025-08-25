"""
666刮刮乐游戏Celery任务
"""

from celery import shared_task
from django.utils import timezone
from django.db import models
import logging

logger = logging.getLogger(__name__)


@shared_task
def update_daily_statistics():
    """
    更新每日统计数据任务
    每天执行，更新前一天的统计数据
    """
    try:
        from .services import Scratch666Service
        
        success = Scratch666Service.update_daily_statistics()
        
        if success:
            logger.info("666刮刮乐每日统计更新成功")
            return {"success": True, "message": "统计更新成功"}
        else:
            logger.warning("666刮刮乐每日统计更新失败")
            return {"success": False, "message": "统计更新失败"}
            
    except Exception as e:
        logger.error(f"更新666刮刮乐每日统计时出错: {str(e)}")
        return {"success": False, "message": f"更新统计出错: {str(e)}"}


@shared_task
def expire_old_cards():
    """
    过期旧卡片任务
    每天执行，将超过30天未刮开的卡片标记为过期
    """
    try:
        from .models import ScratchCard
        from datetime import timedelta
        
        # 30天前的日期
        expire_date = timezone.now() - timedelta(days=30)
        
        # 查找需要过期的卡片
        expired_cards = ScratchCard.objects.filter(
            status='ACTIVE',
            purchased_at__lt=expire_date
        )
        
        # 标记为过期
        count = expired_cards.update(status='EXPIRED')
        
        logger.info(f"666刮刮乐过期了 {count} 张旧卡片")
        
        return {
            "success": True,
            "expired_count": count
        }
        
    except Exception as e:
        logger.error(f"过期666刮刮乐旧卡片时出错: {str(e)}")
        return {"success": False, "message": f"过期卡片出错: {str(e)}"}


@shared_task
def check_profit_rate():
    """
    检查利润率任务
    每天执行，检查实际利润率是否符合目标
    """
    try:
        from .services import Scratch666Service
        from .models import Scratch666Game, ScratchStatistics
        from decimal import Decimal
        from datetime import timedelta
        
        # 获取游戏配置
        game = Scratch666Service.get_game()
        if not game:
            return {"success": False, "message": "游戏不存在"}
        
        config = Scratch666Service.get_game_config()
        if not config:
            return {"success": False, "message": "游戏配置不存在"}
        
        # 获取最近7天的统计数据
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)
        
        stats = ScratchStatistics.objects.filter(
            game=game,
            date__range=[start_date, end_date]
        ).aggregate(
            total_sales=models.Sum('total_sales_amount'),
            total_winnings=models.Sum('total_winnings'),
            total_profit=models.Sum('profit')
        )
        
        if stats['total_sales'] and stats['total_sales'] > 0:
            actual_profit_rate = (stats['total_profit'] / stats['total_sales']) * 100
            target_profit_rate = float(config.profit_target) * 100
            
            # 如果实际利润率偏离目标超过5%，发送警告
            if abs(actual_profit_rate - target_profit_rate) > 5:
                logger.warning(
                    f"666刮刮乐利润率异常: 目标{target_profit_rate:.2f}%, "
                    f"实际{actual_profit_rate:.2f}%"
                )
                
                return {
                    "success": True,
                    "warning": True,
                    "target_rate": target_profit_rate,
                    "actual_rate": actual_profit_rate,
                    "message": "利润率偏离目标"
                }
        
        return {
            "success": True,
            "message": "利润率检查完成"
        }
        
    except Exception as e:
        logger.error(f"检查666刮刮乐利润率时出错: {str(e)}")
        return {"success": False, "message": f"检查利润率出错: {str(e)}"}


@shared_task
def send_win_notifications():
    """
    发送中奖通知任务
    每小时执行，向大奖中奖用户发送通知
    """
    try:
        from .models import ScratchCard
        from datetime import timedelta
        
        # 查找最近1小时内的大奖中奖记录
        one_hour_ago = timezone.now() - timedelta(hours=1)
        
        big_winners = ScratchCard.objects.filter(
            is_winner=True,
            total_winnings__gte=1000,  # 1000奈拉以上算大奖
            scratched_at__gte=one_hour_ago
        ).select_related('user')
        
        notification_count = 0
        
        for card in big_winners:
            # 这里可以集成短信或邮件通知服务
            logger.info(
                f"用户 {card.user.phone} 在666刮刮乐中获得大奖: ₦{card.total_winnings}"
            )
            notification_count += 1
        
        return {
            "success": True,
            "notifications_sent": notification_count
        }
        
    except Exception as e:
        logger.error(f"发送666刮刮乐中奖通知时出错: {str(e)}")
        return {"success": False, "message": f"发送通知出错: {str(e)}"}


@shared_task
def cleanup_old_statistics():
    """
    清理旧统计数据任务
    每月执行，清理超过1年的统计数据
    """
    try:
        from .models import ScratchStatistics
        from datetime import timedelta
        
        # 删除1年前的统计数据
        one_year_ago = timezone.now().date() - timedelta(days=365)
        
        deleted_count = ScratchStatistics.objects.filter(
            date__lt=one_year_ago
        ).delete()[0]
        
        logger.info(f"清理了 {deleted_count} 条666刮刮乐旧统计数据")
        
        return {
            "success": True,
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"清理666刮刮乐旧统计数据时出错: {str(e)}")
        return {"success": False, "message": f"清理数据出错: {str(e)}"}