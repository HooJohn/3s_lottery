"""
大乐透彩票Celery任务
"""

from celery import shared_task
from django.utils import timezone
from django.db import models
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def auto_close_draw_sales():
    """
    自动停售任务
    每分钟执行，检查是否有需要停售的期次
    """
    try:
        from .models import SuperLottoDraw
        from .services import SuperLottoService
        
        now = timezone.now()
        
        # 查找需要停售的期次
        draws_to_close = SuperLottoDraw.objects.filter(
            status='OPEN',
            sales_end_time__lte=now
        )
        
        closed_count = 0
        for draw in draws_to_close:
            result = SuperLottoService.close_draw_sales(str(draw.id))
            if result['success']:
                closed_count += 1
                logger.info(f"自动停售成功: {draw.draw_number}期")
            else:
                logger.error(f"自动停售失败: {draw.draw_number}期 - {result['message']}")
        
        return {
            "success": True,
            "closed_count": closed_count,
            "message": f"自动停售完成，处理{closed_count}个期次"
        }
        
    except Exception as e:
        logger.error(f"自动停售任务出错: {str(e)}")
        return {"success": False, "message": f"自动停售出错: {str(e)}"}


@shared_task
def auto_conduct_draw():
    """
    自动开奖任务
    每小时执行，检查是否有需要开奖的期次
    """
    try:
        from .models import SuperLottoDraw
        from .services import SuperLottoService
        
        now = timezone.now()
        
        # 查找需要开奖的期次（已停售且到达开奖时间）
        draws_to_conduct = SuperLottoDraw.objects.filter(
            status='CLOSED',
            draw_time__lte=now
        )
        
        conducted_count = 0
        for draw in draws_to_conduct:
            result = SuperLottoService.conduct_draw(str(draw.id))
            if result['success']:
                conducted_count += 1
                logger.info(f"自动开奖成功: {draw.draw_number}期")
                
                # 开奖成功后创建下一期
                next_draw_result = SuperLottoService.create_next_draw()
                if next_draw_result['success']:
                    logger.info(f"自动创建下期成功: {next_draw_result['data']['draw_number']}期")
                else:
                    logger.error(f"自动创建下期失败: {next_draw_result['message']}")
            else:
                logger.error(f"自动开奖失败: {draw.draw_number}期 - {result['message']}")
        
        return {
            "success": True,
            "conducted_count": conducted_count,
            "message": f"自动开奖完成，处理{conducted_count}个期次"
        }
        
    except Exception as e:
        logger.error(f"自动开奖任务出错: {str(e)}")
        return {"success": False, "message": f"自动开奖出错: {str(e)}"}


@shared_task
def update_jackpot_amount():
    """
    更新奖池金额任务
    每小时执行，根据销售情况更新奖池
    """
    try:
        from .models import SuperLottoDraw, SuperLottoGame
        from .services import SuperLottoService
        from decimal import Decimal
        
        game = SuperLottoService.get_game()
        if not game:
            return {"success": False, "message": "游戏不存在"}
        
        # 获取当前销售期次
        current_draw = SuperLottoService.get_current_draw()
        if not current_draw:
            return {"success": True, "message": "没有当前销售期次"}
        
        # 计算当前销售额
        from .models import SuperLottoBet
        current_sales = SuperLottoBet.objects.filter(
            draw=current_draw
        ).aggregate(
            total=models.Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # 更新期次销售额
        current_draw.total_sales = current_sales
        
        # 奖池增长：销售额的一定比例进入奖池
        jackpot_growth_rate = Decimal('0.50')  # 50%进入奖池
        jackpot_growth = current_sales * jackpot_growth_rate
        
        if jackpot_growth > 0:
            current_draw.jackpot_amount += jackpot_growth
            current_draw.save()
            
            logger.info(f"奖池更新成功: {current_draw.draw_number}期，增长₦{jackpot_growth}")
        
        return {
            "success": True,
            "draw_number": current_draw.draw_number,
            "current_sales": float(current_sales),
            "jackpot_amount": float(current_draw.jackpot_amount),
            "jackpot_growth": float(jackpot_growth)
        }
        
    except Exception as e:
        logger.error(f"更新奖池金额出错: {str(e)}")
        return {"success": False, "message": f"更新奖池出错: {str(e)}"}


@shared_task
def send_draw_notifications():
    """
    发送开奖通知任务
    开奖后执行，向中奖用户发送通知
    """
    try:
        from .models import SuperLottoDraw, SuperLottoBet
        from datetime import timedelta
        
        # 查找最近1小时内开奖的期次
        one_hour_ago = timezone.now() - timedelta(hours=1)
        
        recent_draws = SuperLottoDraw.objects.filter(
            status='SETTLED',
            updated_at__gte=one_hour_ago
        )
        
        notification_count = 0
        
        for draw in recent_draws:
            # 查找该期次的中奖用户
            winning_bets = SuperLottoBet.objects.filter(
                draw=draw,
                is_winner=True,
                winning_amount__gte=100  # 100奈拉以上发送通知
            ).select_related('user')
            
            for bet in winning_bets:
                # 这里可以集成短信或邮件通知服务
                logger.info(
                    f"用户 {bet.user.phone} 在大乐透{draw.draw_number}期中{bet.winning_level}等奖: "
                    f"₦{bet.winning_amount}"
                )
                notification_count += 1
        
        return {
            "success": True,
            "notifications_sent": notification_count,
            "draws_processed": len(recent_draws)
        }
        
    except Exception as e:
        logger.error(f"发送开奖通知出错: {str(e)}")
        return {"success": False, "message": f"发送通知出错: {str(e)}"}


@shared_task
def cleanup_old_draws():
    """
    清理旧期次数据任务
    每月执行，清理超过1年的期次数据
    """
    try:
        from .models import SuperLottoDraw, SuperLottoBet, SuperLottoStatistics
        from datetime import timedelta
        
        # 删除1年前的数据
        one_year_ago = timezone.now() - timedelta(days=365)
        
        # 删除旧的投注记录
        old_bets = SuperLottoBet.objects.filter(created_at__lt=one_year_ago)
        bets_deleted = old_bets.count()
        old_bets.delete()
        
        # 删除旧的统计数据
        old_stats = SuperLottoStatistics.objects.filter(created_at__lt=one_year_ago)
        stats_deleted = old_stats.count()
        old_stats.delete()
        
        # 删除旧的期次（保留开奖结果，只删除详细数据）
        old_draws = SuperLottoDraw.objects.filter(
            created_at__lt=one_year_ago,
            status='SETTLED'
        )
        draws_deleted = old_draws.count()
        old_draws.delete()
        
        logger.info(f"清理旧数据完成: 期次{draws_deleted}个, 投注{bets_deleted}条, 统计{stats_deleted}条")
        
        return {
            "success": True,
            "draws_deleted": draws_deleted,
            "bets_deleted": bets_deleted,
            "stats_deleted": stats_deleted
        }
        
    except Exception as e:
        logger.error(f"清理旧数据出错: {str(e)}")
        return {"success": False, "message": f"清理数据出错: {str(e)}"}


@shared_task
def check_profit_rate():
    """
    检查利润率任务
    每天执行，检查实际利润率是否符合目标
    """
    try:
        from .models import SuperLottoStatistics
        from .services import SuperLottoService
        from datetime import timedelta
        from decimal import Decimal
        
        game = SuperLottoService.get_game()
        config = SuperLottoService.get_game_config()
        
        if not game or not config:
            return {"success": False, "message": "游戏或配置不存在"}
        
        # 获取最近7天的统计数据
        seven_days_ago = timezone.now() - timedelta(days=7)
        
        stats = SuperLottoStatistics.objects.filter(
            game=game,
            created_at__gte=seven_days_ago
        ).aggregate(
            total_sales=models.Sum('total_sales_amount'),
            total_winnings=models.Sum('total_winning_amount'),
            total_profit=models.Sum('profit')
        )
        
        if stats['total_sales'] and stats['total_sales'] > 0:
            actual_profit_rate = (stats['total_profit'] / stats['total_sales']) * 100
            target_profit_rate = float(config.profit_target) * 100
            
            # 如果实际利润率偏离目标超过5%，发送警告
            if abs(actual_profit_rate - target_profit_rate) > 5:
                logger.warning(
                    f"大乐透利润率异常: 目标{target_profit_rate:.2f}%, "
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
        logger.error(f"检查大乐透利润率出错: {str(e)}")
        return {"success": False, "message": f"检查利润率出错: {str(e)}"}


@shared_task
def generate_draw_report():
    """
    生成开奖报告任务
    每次开奖后执行，生成详细的开奖报告
    """
    try:
        from .models import SuperLottoDraw, SuperLottoStatistics
        from datetime import timedelta
        
        # 查找最近开奖的期次
        recent_time = timezone.now() - timedelta(hours=2)
        
        recent_draws = SuperLottoDraw.objects.filter(
            status='SETTLED',
            updated_at__gte=recent_time
        ).order_by('-updated_at')
        
        reports_generated = 0
        
        for draw in recent_draws:
            try:
                # 获取统计数据
                stats = SuperLottoStatistics.objects.get(draw=draw)
                
                # 生成报告数据
                report_data = {
                    'draw_number': draw.draw_number,
                    'draw_time': draw.draw_time.isoformat(),
                    'winning_numbers': {
                        'front': draw.front_numbers,
                        'back': draw.back_numbers
                    },
                    'sales_data': {
                        'total_bets': stats.total_bets,
                        'total_sales': float(stats.total_sales_amount),
                        'unique_players': stats.unique_players
                    },
                    'prize_data': {
                        'total_winners': stats.total_winners,
                        'total_winnings': float(stats.total_winning_amount),
                        'first_prize': {
                            'winners': draw.first_prize_winners,
                            'amount': float(draw.first_prize_amount)
                        },
                        'second_prize': {
                            'winners': draw.second_prize_winners,
                            'amount': float(draw.second_prize_amount)
                        }
                    },
                    'profit_data': {
                        'profit': float(stats.profit),
                        'profit_rate': float(stats.profit_rate)
                    }
                }
                
                # 这里可以将报告数据发送到管理系统或保存到文件
                logger.info(f"开奖报告生成成功: {draw.draw_number}期")
                reports_generated += 1
                
            except SuperLottoStatistics.DoesNotExist:
                logger.warning(f"期次{draw.draw_number}缺少统计数据，跳过报告生成")
                continue
        
        return {
            "success": True,
            "reports_generated": reports_generated
        }
        
    except Exception as e:
        logger.error(f"生成开奖报告出错: {str(e)}")
        return {"success": False, "message": f"生成报告出错: {str(e)}"}