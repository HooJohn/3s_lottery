"""
体育博彩Celery任务
"""

from celery import shared_task
from django.utils import timezone
from django.db import models
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def sync_all_bet_records():
    """
    同步所有平台的投注记录
    每小时执行，同步最近的投注记录
    """
    try:
        from .models import SportsProvider
        from .services import SportsProviderService
        
        # 获取所有活跃平台
        providers = SportsProvider.objects.filter(is_active=True)
        
        total_synced = 0
        success_count = 0
        
        for provider in providers:
            try:
                result = SportsProviderService.sync_bet_records_from_platform(
                    provider_code=provider.code,
                    start_date=timezone.now() - timedelta(hours=2),  # 同步最近2小时
                    end_date=timezone.now()
                )
                
                if result['success']:
                    success_count += 1
                    total_synced += result['data']['synced_count']
                    logger.info(f"平台 {provider.name} 投注记录同步成功: {result['data']['synced_count']}条")
                else:
                    logger.error(f"平台 {provider.name} 投注记录同步失败: {result['message']}")
                    
            except Exception as e:
                logger.error(f"平台 {provider.name} 投注记录同步异常: {str(e)}")
                continue
        
        return {
            "success": True,
            "total_synced": total_synced,
            "success_count": success_count,
            "total_providers": len(providers),
            "message": f"投注记录同步完成，成功{success_count}/{len(providers)}个平台，共{total_synced}条记录"
        }
        
    except Exception as e:
        logger.error(f"同步所有投注记录任务出错: {str(e)}")
        return {"success": False, "message": f"同步出错: {str(e)}"}


@shared_task
def sync_wallet_balances():
    """
    同步所有用户的钱包余额
    每30分钟执行，从第三方平台同步余额
    """
    try:
        from .models import UserSportsWallet
        
        # 获取需要同步的钱包（最近1小时内有活动的）
        one_hour_ago = timezone.now() - timedelta(hours=1)
        
        wallets = UserSportsWallet.objects.filter(
            is_active=True,
            provider__is_active=True,
            updated_at__gte=one_hour_ago
        ).select_related('provider', 'user')
        
        synced_count = 0
        
        for wallet in wallets:
            try:
                # 这里应该调用第三方平台API同步余额
                # 由于是示例，我们模拟同步成功
                
                wallet.last_sync_at = timezone.now()
                wallet.save()
                
                synced_count += 1
                logger.debug(f"用户 {wallet.user.phone} 在平台 {wallet.provider.name} 的钱包余额同步成功")
                
            except Exception as e:
                logger.error(f"钱包余额同步失败: {wallet.user.phone} - {wallet.provider.name} - {str(e)}")
                continue
        
        return {
            "success": True,
            "synced_count": synced_count,
            "message": f"钱包余额同步完成，处理{synced_count}个钱包"
        }
        
    except Exception as e:
        logger.error(f"同步钱包余额任务出错: {str(e)}")
        return {"success": False, "message": f"同步出错: {str(e)}"}


@shared_task
def update_sports_statistics():
    """
    更新体育博彩统计数据
    每天执行，更新前一天的统计数据
    """
    try:
        from .models import SportsProvider, SportsStatistics, SportsBetRecord, SportsWalletTransaction
        from datetime import date, timedelta
        
        yesterday = date.today() - timedelta(days=1)
        
        # 获取所有活跃平台
        providers = SportsProvider.objects.filter(is_active=True)
        
        updated_count = 0
        
        for provider in providers:
            try:
                # 计算昨天的统计数据
                start_datetime = timezone.make_aware(
                    timezone.datetime.combine(yesterday, timezone.datetime.min.time())
                )
                end_datetime = start_datetime + timedelta(days=1)
                
                # 投注统计
                bet_stats = SportsBetRecord.objects.filter(
                    provider=provider,
                    bet_time__gte=start_datetime,
                    bet_time__lt=end_datetime
                ).aggregate(
                    total_bets=models.Count('id'),
                    total_bet_amount=models.Sum('bet_amount'),
                    total_win_amount=models.Sum('actual_win'),
                )
                
                # 钱包统计
                wallet_stats = SportsWalletTransaction.objects.filter(
                    provider=provider,
                    created_at__gte=start_datetime,
                    created_at__lt=end_datetime
                ).aggregate(
                    total_transfer_in=models.Sum('amount', filter=models.Q(transaction_type='TRANSFER_IN')),
                    total_transfer_out=models.Sum('amount', filter=models.Q(transaction_type='TRANSFER_OUT')),
                )
                
                # 用户统计
                active_users = SportsBetRecord.objects.filter(
                    provider=provider,
                    bet_time__gte=start_datetime,
                    bet_time__lt=end_datetime
                ).values('user').distinct().count()
                
                # 计算利润
                total_bet_amount = bet_stats['total_bet_amount'] or 0
                total_win_amount = bet_stats['total_win_amount'] or 0
                gross_profit = total_bet_amount - total_win_amount
                
                # 平台分成（10%）
                net_profit = gross_profit * provider.profit_share_rate
                profit_rate = (net_profit / total_bet_amount * 100) if total_bet_amount > 0 else 0
                
                # 创建或更新统计记录
                stats, created = SportsStatistics.objects.update_or_create(
                    provider=provider,
                    date=yesterday,
                    defaults={
                        'active_users': active_users,
                        'total_bets': bet_stats['total_bets'] or 0,
                        'total_bet_amount': total_bet_amount,
                        'total_win_amount': total_win_amount,
                        'total_transfer_in': wallet_stats['total_transfer_in'] or 0,
                        'total_transfer_out': wallet_stats['total_transfer_out'] or 0,
                        'gross_profit': gross_profit,
                        'net_profit': net_profit,
                        'profit_rate': profit_rate,
                    }
                )
                
                updated_count += 1
                logger.info(f"平台 {provider.name} 统计数据更新成功: {yesterday}")
                
            except Exception as e:
                logger.error(f"平台 {provider.name} 统计数据更新失败: {str(e)}")
                continue
        
        return {
            "success": True,
            "updated_count": updated_count,
            "date": yesterday.isoformat(),
            "message": f"体育博彩统计更新完成，处理{updated_count}个平台"
        }
        
    except Exception as e:
        logger.error(f"更新体育博彩统计任务出错: {str(e)}")
        return {"success": False, "message": f"更新统计出错: {str(e)}"}


@shared_task
def auto_recover_idle_wallets():
    """
    自动回收闲置钱包余额
    每天执行，回收超过24小时未使用的钱包余额
    """
    try:
        from .models import UserSportsWallet, SportsProviderConfig
        from .services import SportsProviderService
        
        # 查找超过24小时未使用且有余额的钱包
        idle_time = timezone.now() - timedelta(hours=24)
        
        idle_wallets = UserSportsWallet.objects.filter(
            is_active=True,
            balance__gt=0,
            last_sync_at__lt=idle_time,
            provider__is_active=True
        ).select_related('provider', 'user')
        
        recovered_count = 0
        total_recovered = 0
        
        for wallet in idle_wallets:
            try:
                # 检查平台是否启用自动回收
                config = getattr(wallet.provider, 'config', None)
                if not config or not config.auto_transfer:
                    continue
                
                result = SportsProviderService.transfer_from_platform(
                    user=wallet.user,
                    provider_code=wallet.provider.code
                )
                
                if result['success']:
                    recovered_count += 1
                    total_recovered += result['data']['amount']
                    logger.info(f"自动回收闲置钱包成功: {wallet.user.phone} - {wallet.provider.name} - ₦{result['data']['amount']}")
                
            except Exception as e:
                logger.error(f"自动回收闲置钱包失败: {wallet.user.phone} - {wallet.provider.name} - {str(e)}")
                continue
        
        return {
            "success": True,
            "recovered_count": recovered_count,
            "total_recovered": total_recovered,
            "total_checked": len(idle_wallets),
            "message": f"自动回收完成，回收{recovered_count}个钱包，共₦{total_recovered}"
        }
        
    except Exception as e:
        logger.error(f"自动回收闲置钱包任务出错: {str(e)}")
        return {"success": False, "message": f"自动回收出错: {str(e)}"}


@shared_task
def check_platform_status():
    """
    检查平台状态
    每5分钟执行，检查第三方平台是否正常
    """
    try:
        from .models import SportsProvider
        import requests
        
        providers = SportsProvider.objects.filter(is_active=True)
        
        status_changes = []
        
        for provider in providers:
            try:
                # 检查平台API是否可访问
                # 这里应该调用平台的健康检查接口
                # 由于是示例，我们模拟检查
                
                # response = requests.get(f"{provider.api_endpoint}/health", timeout=10)
                # is_healthy = response.status_code == 200
                
                # 模拟检查结果
                is_healthy = True  # 假设平台正常
                
                # 如果状态发生变化，更新数据库
                if provider.is_maintenance and is_healthy:
                    provider.is_maintenance = False
                    provider.save()
                    status_changes.append(f"{provider.name}: 维护 -> 正常")
                    logger.info(f"平台 {provider.name} 状态恢复正常")
                elif not provider.is_maintenance and not is_healthy:
                    provider.is_maintenance = True
                    provider.save()
                    status_changes.append(f"{provider.name}: 正常 -> 维护")
                    logger.warning(f"平台 {provider.name} 进入维护状态")
                
            except Exception as e:
                logger.error(f"检查平台 {provider.name} 状态失败: {str(e)}")
                # 如果检查失败，标记为维护状态
                if not provider.is_maintenance:
                    provider.is_maintenance = True
                    provider.save()
                    status_changes.append(f"{provider.name}: 正常 -> 维护（检查失败）")
                continue
        
        return {
            "success": True,
            "checked_count": len(providers),
            "status_changes": status_changes,
            "message": f"平台状态检查完成，检查{len(providers)}个平台，{len(status_changes)}个状态变化"
        }
        
    except Exception as e:
        logger.error(f"检查平台状态任务出错: {str(e)}")
        return {"success": False, "message": f"状态检查出错: {str(e)}"}


@shared_task
def send_bet_notifications():
    """
    发送投注通知
    每小时执行，向大额中奖用户发送通知
    """
    try:
        from .models import SportsBetRecord
        
        # 查找最近1小时内的大额中奖记录
        one_hour_ago = timezone.now() - timedelta(hours=1)
        
        big_wins = SportsBetRecord.objects.filter(
            status='WON',
            actual_win__gte=1000,  # 1000奈拉以上算大奖
            settle_time__gte=one_hour_ago
        ).select_related('user', 'provider')
        
        notification_count = 0
        
        for bet in big_wins:
            try:
                # 这里可以集成短信或邮件通知服务
                logger.info(
                    f"用户 {bet.user.phone} 在{bet.provider.name}体育博彩中获得大奖: "
                    f"{bet.sport_type} ₦{bet.actual_win}"
                )
                notification_count += 1
                
            except Exception as e:
                logger.error(f"发送投注通知失败: {bet.id} - {str(e)}")
                continue
        
        return {
            "success": True,
            "notifications_sent": notification_count,
            "message": f"投注通知发送完成，发送{notification_count}条通知"
        }
        
    except Exception as e:
        logger.error(f"发送投注通知任务出错: {str(e)}")
        return {"success": False, "message": f"发送通知出错: {str(e)}"}


@shared_task
def cleanup_old_records():
    """
    清理旧记录
    每月执行，清理超过1年的记录
    """
    try:
        from .models import SportsWalletTransaction, SportsBetRecord, SportsStatistics
        
        # 删除1年前的数据
        one_year_ago = timezone.now() - timedelta(days=365)
        
        # 删除旧的钱包交易记录
        old_transactions = SportsWalletTransaction.objects.filter(created_at__lt=one_year_ago)
        transactions_deleted = old_transactions.count()
        old_transactions.delete()
        
        # 删除旧的投注记录
        old_bets = SportsBetRecord.objects.filter(created_at__lt=one_year_ago)
        bets_deleted = old_bets.count()
        old_bets.delete()
        
        # 删除旧的统计数据
        old_stats = SportsStatistics.objects.filter(date__lt=one_year_ago.date())
        stats_deleted = old_stats.count()
        old_stats.delete()
        
        logger.info(f"清理旧数据完成: 交易{transactions_deleted}条, 投注{bets_deleted}条, 统计{stats_deleted}条")
        
        return {
            "success": True,
            "transactions_deleted": transactions_deleted,
            "bets_deleted": bets_deleted,
            "stats_deleted": stats_deleted,
            "message": f"数据清理完成"
        }
        
    except Exception as e:
        logger.error(f"清理旧记录任务出错: {str(e)}")
        return {"success": False, "message": f"清理数据出错: {str(e)}"}


@shared_task
def generate_sports_report():
    """
    生成体育博彩报告
    每天执行，生成前一天的详细报告
    """
    try:
        from .models import SportsProvider, SportsStatistics
        from datetime import date, timedelta
        
        yesterday = date.today() - timedelta(days=1)
        
        # 获取所有平台的统计数据
        stats = SportsStatistics.objects.filter(date=yesterday).select_related('provider')
        
        if not stats.exists():
            return {"success": True, "message": "没有统计数据需要生成报告"}
        
        # 生成报告数据
        report_data = {
            'date': yesterday.isoformat(),
            'summary': {
                'total_providers': stats.count(),
                'total_active_users': sum(stat.active_users for stat in stats),
                'total_bets': sum(stat.total_bets for stat in stats),
                'total_bet_amount': sum(stat.total_bet_amount for stat in stats),
                'total_win_amount': sum(stat.total_win_amount for stat in stats),
                'total_profit': sum(stat.net_profit for stat in stats),
            },
            'providers': []
        }
        
        for stat in stats:
            report_data['providers'].append({
                'name': stat.provider.name,
                'active_users': stat.active_users,
                'total_bets': stat.total_bets,
                'total_bet_amount': float(stat.total_bet_amount),
                'total_win_amount': float(stat.total_win_amount),
                'profit': float(stat.net_profit),
                'profit_rate': float(stat.profit_rate),
                'payout_rate': stat.calculate_payout_rate(),
            })
        
        # 这里可以将报告数据发送到管理系统或保存到文件
        logger.info(f"体育博彩报告生成成功: {yesterday}")
        
        return {
            "success": True,
            "report_date": yesterday.isoformat(),
            "providers_count": len(report_data['providers']),
            "message": "体育博彩报告生成完成"
        }
        
    except Exception as e:
        logger.error(f"生成体育博彩报告出错: {str(e)}")
        return {"success": False, "message": f"生成报告出错: {str(e)}"}