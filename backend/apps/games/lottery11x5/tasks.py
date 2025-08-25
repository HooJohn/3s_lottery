"""
11选5彩票游戏Celery任务
"""

from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
from .services import Lottery11x5Service, Lottery11x5DrawService
import logging

logger = logging.getLogger(__name__)


@shared_task
def create_daily_draws():
    """
    创建每日期次任务
    每天凌晨执行，创建当天的期次
    """
    try:
        success = Lottery11x5DrawService.create_daily_draws()
        
        if success:
            logger.info("11选5每日期次创建成功")
            return {"success": True, "message": "期次创建成功"}
        else:
            logger.warning("11选5每日期次创建失败或已存在")
            return {"success": False, "message": "期次创建失败或已存在"}
            
    except Exception as e:
        logger.error(f"创建11选5每日期次时出错: {str(e)}")
        return {"success": False, "message": f"创建期次出错: {str(e)}"}


@shared_task
def close_expired_draws():
    """
    关闭过期期次任务
    每分钟执行，关闭已到封盘时间的期次
    """
    try:
        count = Lottery11x5DrawService.close_expired_draws()
        
        if count > 0:
            logger.info(f"11选5关闭了 {count} 个过期期次")
        
        return {"success": True, "closed_count": count}
        
    except Exception as e:
        logger.error(f"关闭11选5过期期次时出错: {str(e)}")
        return {"success": False, "message": f"关闭期次出错: {str(e)}"}


@shared_task
def auto_draw_lottery():
    """
    自动开奖任务
    每分钟执行，对已到开奖时间的期次进行开奖
    """
    try:
        results = Lottery11x5DrawService.auto_draw_lottery()
        
        if results:
            logger.info(f"11选5自动开奖完成，共开奖 {len(results)} 期")
            
            # 清除相关缓存
            cache.delete_pattern('lottery11x5_*')
        
        return {"success": True, "draw_results": results}
        
    except Exception as e:
        logger.error(f"11选5自动开奖时出错: {str(e)}")
        return {"success": False, "message": f"自动开奖出错: {str(e)}"}


@shared_task
def settlement_verification():
    """
    结算验证任务
    验证已结算期次的准确性
    """
    try:
        from apps.games.models import Draw, Bet
        from .draw_engine import Lottery11x5ProfitController
        
        # 获取最近完成的期次
        recent_draws = Draw.objects.filter(
            game__game_type='11选5',
            status='COMPLETED'
        ).order_by('-draw_time')[:10]
        
        verification_results = []
        profit_controller = Lottery11x5ProfitController()
        
        for draw in recent_draws:
            try:
                # 重新计算该期的理论派彩
                winning_numbers = draw.lottery11x5_result.numbers
                theoretical_analysis = profit_controller.analyze_draw_profitability(
                    str(draw.id), winning_numbers
                )
                
                # 比较实际结果与理论结果
                actual_payout = float(draw.total_payout)
                theoretical_payout = float(theoretical_analysis.get('potential_payout', 0))
                
                variance = abs(actual_payout - theoretical_payout)
                variance_rate = (variance / actual_payout * 100) if actual_payout > 0 else 0
                
                verification_results.append({
                    'draw_number': draw.draw_number,
                    'actual_payout': actual_payout,
                    'theoretical_payout': theoretical_payout,
                    'variance': variance,
                    'variance_rate': variance_rate,
                    'is_accurate': variance_rate < 0.01,  # 允许0.01%的误差
                })
                
                # 如果发现异常，记录警告
                if variance_rate > 1.0:
                    logger.warning(f"期次 {draw.draw_number} 结算异常: 实际派彩 ₦{actual_payout}, 理论派彩 ₦{theoretical_payout}")
                
            except Exception as e:
                logger.error(f"验证期次 {draw.draw_number} 时出错: {str(e)}")
                continue
        
        # 统计验证结果
        total_verified = len(verification_results)
        accurate_count = sum(1 for result in verification_results if result['is_accurate'])
        accuracy_rate = (accurate_count / total_verified * 100) if total_verified > 0 else 0
        
        logger.info(f"结算验证完成: {total_verified} 期, 准确率 {accuracy_rate:.2f}%")
        
        return {
            "success": True,
            "total_verified": total_verified,
            "accurate_count": accurate_count,
            "accuracy_rate": accuracy_rate,
            "verification_results": verification_results
        }
        
    except Exception as e:
        logger.error(f"结算验证时出错: {str(e)}")
        return {"success": False, "message": f"结算验证出错: {str(e)}"}


@shared_task
def update_hot_cold_numbers():
    """
    更新冷热号码统计任务
    每小时执行，更新冷热号码统计数据
    """
    try:
        success = Lottery11x5Service.update_hot_cold_numbers()
        
        if success:
            logger.info("11选5冷热号码统计更新成功")
            
            # 清除冷热号码缓存
            cache.delete_pattern('lottery11x5_hot_cold_*')
        
        return {"success": success}
        
    except Exception as e:
        logger.error(f"更新11选5冷热号码统计时出错: {str(e)}")
        return {"success": False, "message": f"更新统计出错: {str(e)}"}


@shared_task
def cleanup_old_data():
    """
    清理旧数据任务
    每天执行，清理过期的数据
    """
    try:
        from .models import Lottery11x5Trend, Lottery11x5HotCold
        from datetime import timedelta
        
        # 清理超过1年的走势数据
        cutoff_date = timezone.now().date() - timedelta(days=365)
        deleted_trends = Lottery11x5Trend.objects.filter(date__lt=cutoff_date).delete()
        
        # 清理过期的购物车数据
        cache.delete_pattern('lottery11x5_cart_*')
        
        logger.info(f"11选5清理了 {deleted_trends[0]} 条过期走势数据")
        
        return {
            "success": True,
            "deleted_trends": deleted_trends[0]
        }
        
    except Exception as e:
        logger.error(f"清理11选5旧数据时出错: {str(e)}")
        return {"success": False, "message": f"清理数据出错: {str(e)}"}


@shared_task
def generate_statistics_report():
    """
    生成统计报告任务
    每天执行，生成游戏统计报告
    """
    try:
        from apps.games.models import GameStatistics
        from .models import Lottery11x5Result
        from decimal import Decimal
        
        game = Lottery11x5Service.get_game()
        if not game:
            return {"success": False, "message": "游戏不存在"}
        
        today = timezone.now().date()
        
        # 获取今日开奖结果
        today_results = Lottery11x5Result.objects.filter(
            draw__game=game,
            draw__draw_time__date=today,
            draw__status='COMPLETED'
        )
        
        if not today_results.exists():
            return {"success": True, "message": "今日暂无开奖数据"}
        
        # 计算统计数据
        total_draws = today_results.count()
        total_bets = sum(result.draw.total_bets for result in today_results)
        total_amount = sum(result.draw.total_amount for result in today_results)
        total_payout = sum(result.draw.total_payout for result in today_results)
        profit = total_amount - total_payout
        profit_rate = (profit / total_amount * 100) if total_amount > 0 else Decimal('0.00')
        
        # 获取参与用户数
        from apps.games.models import Bet
        total_users = Bet.objects.filter(
            game=game,
            bet_time__date=today
        ).values('user').distinct().count()
        
        # 创建或更新统计记录
        stats, created = GameStatistics.objects.update_or_create(
            game=game,
            date=today,
            defaults={
                'total_draws': total_draws,
                'total_bets': total_bets,
                'total_users': total_users,
                'total_amount': total_amount,
                'total_payout': total_payout,
                'profit': profit,
                'profit_rate': profit_rate,
            }
        )
        
        logger.info(f"11选5统计报告生成成功: {today} - 利润: ₦{profit}")
        
        return {
            "success": True,
            "date": str(today),
            "total_draws": total_draws,
            "total_bets": total_bets,
            "total_users": total_users,
            "total_amount": float(total_amount),
            "total_payout": float(total_payout),
            "profit": float(profit),
            "profit_rate": float(profit_rate),
        }
        
    except Exception as e:
        logger.error(f"生成11选5统计报告时出错: {str(e)}")
        return {"success": False, "message": f"生成报告出错: {str(e)}"}


@shared_task
def send_draw_notifications(draw_id):
    """
    发送开奖通知任务
    开奖后执行，向相关用户发送开奖通知
    """
    try:
        from apps.games.models import Draw, Bet
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        draw = Draw.objects.get(id=draw_id)
        
        # 获取该期投注的用户
        bet_users = Bet.objects.filter(
            draw=draw
        ).select_related('user').values('user', 'status').distinct()
        
        notification_count = 0
        winner_notifications = 0
        
        for bet_user in bet_users:
            try:
                user = User.objects.get(id=bet_user['user'])
                
                # 区分中奖和未中奖通知
                if bet_user['status'] == 'WON':
                    # 中奖通知
                    user_winning_bets = Bet.objects.filter(
                        draw=draw,
                        user=user,
                        status='WON'
                    )
                    total_win_amount = sum(bet.payout for bet in user_winning_bets)
                    
                    logger.info(f"向用户 {user.phone} 发送11选5中奖通知: {draw.draw_number}, 中奖金额: ₦{total_win_amount}")
                    winner_notifications += 1
                else:
                    # 普通开奖通知
                    logger.info(f"向用户 {user.phone} 发送11选5开奖通知: {draw.draw_number}")
                
                notification_count += 1
                
            except User.DoesNotExist:
                continue
        
        return {
            "success": True,
            "draw_number": draw.draw_number,
            "notification_count": notification_count,
            "winner_notifications": winner_notifications
        }
        
    except Exception as e:
        logger.error(f"发送11选5开奖通知时出错: {str(e)}")
        return {"success": False, "message": f"发送通知出错: {str(e)}"}


@shared_task
def check_system_health():
    """
    系统健康检查任务
    定期检查11选5系统状态
    """
    try:
        from apps.games.models import Draw
        
        # 检查是否有当前可投注的期次
        current_draw = Lottery11x5Service.get_current_draw()
        
        # 检查是否有待开奖的期次
        pending_draws = Draw.objects.filter(
            game__game_type='11选5',
            status__in=['CLOSED', 'DRAWING']
        ).count()
        
        # 检查游戏配置
        config = Lottery11x5Service.get_game_config()
        
        health_status = {
            "current_draw_available": current_draw is not None,
            "pending_draws_count": pending_draws,
            "config_available": config is not None,
            "auto_create_enabled": config.auto_create_draws if config else False,
            "auto_draw_enabled": config.auto_draw_results if config else False,
        }
        
        # 检查是否有异常
        issues = []
        if not current_draw:
            issues.append("没有当前可投注的期次")
        
        if pending_draws > 10:
            issues.append(f"待开奖期次过多: {pending_draws}")
        
        if not config:
            issues.append("游戏配置不存在")
        
        if issues:
            logger.warning(f"11选5系统健康检查发现问题: {', '.join(issues)}")
        else:
            logger.info("11选5系统健康检查正常")
        
        return {
            "success": True,
            "health_status": health_status,
            "issues": issues,
            "timestamp": timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"11选5系统健康检查时出错: {str(e)}")
        return {"success": False, "message": f"健康检查出错: {str(e)}"}


@shared_task
def odds_adjustment_analysis():
    """
    赔率调整分析任务
    分析最近的盈利情况，建议是否需要调整赔率
    """
    try:
        from apps.games.models import Draw
        from .draw_engine import Lottery11x5ProfitController
        from datetime import timedelta
        
        # 获取最近30期的数据
        recent_draws = Draw.objects.filter(
            game__game_type='11选5',
            status='COMPLETED'
        ).order_by('-draw_time')[:30]
        
        if not recent_draws:
            return {"success": True, "message": "暂无开奖数据"}
        
        # 计算利润率
        profit_rates = []
        for draw in recent_draws:
            if draw.total_amount > 0:
                profit_rate = draw.profit / draw.total_amount
                profit_rates.append(profit_rate)
        
        if not profit_rates:
            return {"success": True, "message": "暂无有效数据"}
        
        # 分析是否需要调整赔率
        profit_controller = Lottery11x5ProfitController()
        adjustment_analysis = profit_controller.should_adjust_odds(profit_rates)
        
        if adjustment_analysis['should_adjust']:
            logger.warning(f"建议调整11选5赔率: {adjustment_analysis}")
        else:
            logger.info("11选5赔率无需调整")
        
        return {
            "success": True,
            "analysis": adjustment_analysis,
            "recent_profit_rates": [float(rate) for rate in profit_rates[-10:]],  # 最近10期
            "avg_profit_rate": float(sum(profit_rates) / len(profit_rates)),
        }
        
    except Exception as e:
        logger.error(f"赔率调整分析时出错: {str(e)}")
        return {"success": False, "message": f"分析出错: {str(e)}"}


# 定时任务配置示例（需要在settings.py中配置）
"""
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # 每天凌晨0:30创建期次
    'lottery11x5-create-daily-draws': {
        'task': 'apps.games.lottery11x5.tasks.create_daily_draws',
        'schedule': crontab(hour=0, minute=30),
    },
    
    # 每分钟关闭过期期次
    'lottery11x5-close-expired-draws': {
        'task': 'apps.games.lottery11x5.tasks.close_expired_draws',
        'schedule': crontab(minute='*'),
    },
    
    # 每分钟自动开奖
    'lottery11x5-auto-draw': {
        'task': 'apps.games.lottery11x5.tasks.auto_draw_lottery',
        'schedule': crontab(minute='*'),
    },
    
    # 每小时更新冷热号码
    'lottery11x5-update-hot-cold': {
        'task': 'apps.games.lottery11x5.tasks.update_hot_cold_numbers',
        'schedule': crontab(minute=0),
    },
    
    # 每天凌晨2:00清理旧数据
    'lottery11x5-cleanup-old-data': {
        'task': 'apps.games.lottery11x5.tasks.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # 每天凌晨1:00生成统计报告
    'lottery11x5-generate-statistics': {
        'task': 'apps.games.lottery11x5.tasks.generate_statistics_report',
        'schedule': crontab(hour=1, minute=0),
    },
    
    # 每5分钟系统健康检查
    'lottery11x5-health-check': {
        'task': 'apps.games.lottery11x5.tasks.check_system_health',
        'schedule': crontab(minute='*/5'),
    },
    
    # 每小时结算验证
    'lottery11x5-settlement-verification': {
        'task': 'apps.games.lottery11x5.tasks.settlement_verification',
        'schedule': crontab(minute=30),
    },
    
    # 每天分析赔率调整
    'lottery11x5-odds-analysis': {
        'task': 'apps.games.lottery11x5.tasks.odds_adjustment_analysis',
        'schedule': crontab(hour=3, minute=0),
    },
}
"""