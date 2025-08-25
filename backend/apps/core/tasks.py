"""
核心模块Celery任务
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .services import (
    SystemMonitorService, 
    LoggingService, 
    AlertService,
    MaintenanceService
)
from .models import SystemLog, SecurityEvent, PerformanceMetric

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def collect_system_metrics(self):
    """
    收集系统性能指标
    """
    try:
        success = SystemMonitorService.collect_system_metrics()
        
        if success:
            SystemLog.debug('MONITOR', '系统性能指标收集完成')
        else:
            SystemLog.error('MONITOR', '系统性能指标收集失败')
            
        return {'success': success}
        
    except Exception as e:
        logger.error(f"Failed to collect system metrics: {e}")
        SystemLog.error('MONITOR', f'系统性能指标收集异常: {str(e)}')
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def check_system_health(self):
    """
    检查系统健康状态
    """
    try:
        health_status = SystemMonitorService.check_system_health()
        
        # 记录健康状态
        SystemLog.info(
            'HEALTH_CHECK',
            f'系统健康检查完成',
            extra_data=health_status
        )
        
        # 如果系统不健康，创建告警
        if not health_status['overall']:
            unhealthy_components = [
                component for component, status in health_status.items() 
                if not status and component != 'overall'
            ]
            
            SecurityEvent.create_event(
                'SYSTEM_INTRUSION',
                f'系统健康检查失败，异常组件: {", ".join(unhealthy_components)}',
                severity='HIGH',
                event_data=health_status
            )
        
        return health_status
        
    except Exception as e:
        logger.error(f"Failed to check system health: {e}")
        SystemLog.error('HEALTH_CHECK', f'系统健康检查异常: {str(e)}')
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def check_performance_alerts(self):
    """
    检查性能告警
    """
    try:
        alerts = AlertService.check_performance_alerts()
        
        for alert in alerts:
            AlertService.send_alert_notification(alert)
        
        SystemLog.info(
            'ALERT_CHECK',
            f'性能告警检查完成，发现 {len(alerts)} 个告警',
            extra_data={'alerts_count': len(alerts)}
        )
        
        return {'alerts_count': len(alerts), 'alerts': alerts}
        
    except Exception as e:
        logger.error(f"Failed to check performance alerts: {e}")
        SystemLog.error('ALERT_CHECK', f'性能告警检查异常: {str(e)}')
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def check_security_alerts(self):
    """
    检查安全告警
    """
    try:
        alerts = AlertService.check_security_alerts()
        
        for alert in alerts:
            AlertService.send_alert_notification(alert)
        
        SystemLog.info(
            'SECURITY_ALERT',
            f'安全告警检查完成，发现 {len(alerts)} 个告警',
            extra_data={'alerts_count': len(alerts)}
        )
        
        return {'alerts_count': len(alerts), 'alerts': alerts}
        
    except Exception as e:
        logger.error(f"Failed to check security alerts: {e}")
        SystemLog.error('SECURITY_ALERT', f'安全告警检查异常: {str(e)}')
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def cleanup_old_data(self):
    """
    清理旧数据
    """
    try:
        # 清理旧的性能指标（保留7天）
        metrics_deleted = SystemMonitorService.cleanup_old_metrics(days=7)
        
        # 清理旧的日志记录（保留30天）
        logs_deleted, events_deleted = LoggingService.cleanup_old_logs(days=30)
        
        result = {
            'metrics_deleted': metrics_deleted,
            'logs_deleted': logs_deleted,
            'events_deleted': events_deleted
        }
        
        SystemLog.info(
            'CLEANUP',
            f'数据清理完成: 性能指标 {metrics_deleted}, 系统日志 {logs_deleted}, 安全事件 {events_deleted}',
            extra_data=result
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to cleanup old data: {e}")
        SystemLog.error('CLEANUP', f'数据清理异常: {str(e)}')
        raise self.retry(exc=e, countdown=300, max_retries=3)


@shared_task(bind=True)
def generate_daily_report(self):
    """
    生成每日系统报告
    """
    try:
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # 统计昨日数据
        daily_stats = {
            'date': yesterday.isoformat(),
            'system_logs': SystemLog.objects.filter(
                created_at__date=yesterday
            ).count(),
            'security_events': SecurityEvent.objects.filter(
                created_at__date=yesterday
            ).count(),
            'performance_metrics': PerformanceMetric.objects.filter(
                created_at__date=yesterday
            ).count(),
        }
        
        # 按级别统计日志
        log_levels = SystemLog.objects.filter(
            created_at__date=yesterday
        ).values('level').annotate(
            count=models.Count('id')
        )
        daily_stats['log_levels'] = {item['level']: item['count'] for item in log_levels}
        
        # 按严重程度统计安全事件
        security_severity = SecurityEvent.objects.filter(
            created_at__date=yesterday
        ).values('severity').annotate(
            count=models.Count('id')
        )
        daily_stats['security_severity'] = {item['severity']: item['count'] for item in security_severity}
        
        # 记录报告
        SystemLog.info(
            'DAILY_REPORT',
            f'{yesterday} 系统日报生成完成',
            extra_data=daily_stats
        )
        
        return daily_stats
        
    except Exception as e:
        logger.error(f"Failed to generate daily report: {e}")
        SystemLog.error('DAILY_REPORT', f'每日报告生成异常: {str(e)}')
        raise self.retry(exc=e, countdown=300, max_retries=3)


@shared_task(bind=True)
def check_maintenance_schedule(self):
    """
    检查维护计划
    """
    try:
        from .models import MaintenanceMode
        
        now = timezone.now()
        
        # 检查是否有计划的维护需要启动
        scheduled_maintenance = MaintenanceMode.objects.filter(
            is_enabled=False,
            start_time__lte=now,
            end_time__gt=now
        ).first()
        
        if scheduled_maintenance:
            scheduled_maintenance.is_enabled = True
            scheduled_maintenance.save()
            
            SystemLog.warning(
                'MAINTENANCE',
                f'计划维护已自动启动: {scheduled_maintenance.title}'
            )
        
        # 检查是否有维护需要结束
        active_maintenance = MaintenanceMode.objects.filter(
            is_enabled=True,
            end_time__lte=now
        ).first()
        
        if active_maintenance:
            active_maintenance.is_enabled = False
            active_maintenance.save()
            
            SystemLog.info(
                'MAINTENANCE',
                f'计划维护已自动结束: {active_maintenance.title}'
            )
        
        return {
            'maintenance_started': scheduled_maintenance is not None,
            'maintenance_ended': active_maintenance is not None
        }
        
    except Exception as e:
        logger.error(f"Failed to check maintenance schedule: {e}")
        SystemLog.error('MAINTENANCE', f'维护计划检查异常: {str(e)}')
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def backup_system_data(self):
    """
    备份系统数据
    """
    try:
        import subprocess
        import os
        from django.conf import settings
        
        # 生成备份文件名
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"system_backup_{timestamp}.sql"
        backup_path = os.path.join('/tmp', backup_filename)
        
        # 执行数据库备份
        db_config = settings.DATABASES['default']
        backup_command = [
            'pg_dump',
            '-h', db_config['HOST'],
            '-p', str(db_config['PORT']),
            '-U', db_config['USER'],
            '-d', db_config['NAME'],
            '-f', backup_path,
            '--no-password'
        ]
        
        # 设置环境变量
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        result = subprocess.run(backup_command, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            # 备份成功，记录日志
            file_size = os.path.getsize(backup_path)
            
            SystemLog.info(
                'BACKUP',
                f'系统数据备份完成: {backup_filename} ({file_size} bytes)',
                extra_data={
                    'backup_file': backup_filename,
                    'file_size': file_size,
                    'backup_path': backup_path
                }
            )
            
            return {
                'success': True,
                'backup_file': backup_filename,
                'file_size': file_size
            }
        else:
            # 备份失败
            error_message = result.stderr
            SystemLog.error(
                'BACKUP',
                f'系统数据备份失败: {error_message}',
                extra_data={'error': error_message}
            )
            
            return {
                'success': False,
                'error': error_message
            }
        
    except Exception as e:
        logger.error(f"Failed to backup system data: {e}")
        SystemLog.error('BACKUP', f'系统数据备份异常: {str(e)}')
        raise self.retry(exc=e, countdown=300, max_retries=3)


# 定期任务调度配置
from celery.schedules import crontab

# 在 celery.py 中添加以下配置
CELERY_BEAT_SCHEDULE = {
    # 每分钟收集系统指标
    'collect-system-metrics': {
        'task': 'apps.core.tasks.collect_system_metrics',
        'schedule': crontab(minute='*'),
    },
    
    # 每5分钟检查系统健康
    'check-system-health': {
        'task': 'apps.core.tasks.check_system_health',
        'schedule': crontab(minute='*/5'),
    },
    
    # 每10分钟检查性能告警
    'check-performance-alerts': {
        'task': 'apps.core.tasks.check_performance_alerts',
        'schedule': crontab(minute='*/10'),
    },
    
    # 每5分钟检查安全告警
    'check-security-alerts': {
        'task': 'apps.core.tasks.check_security_alerts',
        'schedule': crontab(minute='*/5'),
    },
    
    # 每小时清理旧数据
    'cleanup-old-data': {
        'task': 'apps.core.tasks.cleanup_old_data',
        'schedule': crontab(minute=0),
    },
    
    # 每天凌晨2点生成日报
    'generate-daily-report': {
        'task': 'apps.core.tasks.generate_daily_report',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # 每分钟检查维护计划
    'check-maintenance-schedule': {
        'task': 'apps.core.tasks.check_maintenance_schedule',
        'schedule': crontab(minute='*'),
    },
    
    # 每天凌晨3点备份系统数据
    'backup-system-data': {
        'task': 'apps.core.tasks.backup_system_data',
        'schedule': crontab(hour=3, minute=0),
    },
}