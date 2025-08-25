"""
核心服务模块
"""

import psutil
import time
import logging
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from .models import SystemLog, SecurityEvent, PerformanceMetric, SystemConfig


logger = logging.getLogger(__name__)


class SystemMonitorService:
    """
    系统监控服务
    """
    
    @staticmethod
    def collect_system_metrics():
        """
        收集系统性能指标
        """
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            PerformanceMetric.record_metric(
                'cpu_usage', cpu_percent, '%', 
                warning_threshold=70, critical_threshold=90
            )
            
            # 内存使用率
            memory = psutil.virtual_memory()
            PerformanceMetric.record_metric(
                'memory_usage', memory.percent, '%',
                warning_threshold=80, critical_threshold=95
            )
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            PerformanceMetric.record_metric(
                'disk_usage', disk_percent, '%',
                warning_threshold=80, critical_threshold=90
            )
            
            # 数据库连接数
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM pg_stat_activity;")
                db_connections = cursor.fetchone()[0]
                PerformanceMetric.record_metric(
                    'db_connections', db_connections, 'connections',
                    warning_threshold=80, critical_threshold=100
                )
            
            # Redis内存使用
            try:
                redis_info = cache._cache.get_client().info('memory')
                redis_memory_mb = redis_info['used_memory'] / 1024 / 1024
                PerformanceMetric.record_metric(
                    'redis_memory', redis_memory_mb, 'MB',
                    warning_threshold=500, critical_threshold=1000
                )
            except Exception as e:
                logger.warning(f"Failed to collect Redis metrics: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return False
    
    @staticmethod
    def check_system_health():
        """
        检查系统健康状态
        """
        health_status = {
            'database': False,
            'cache': False,
            'disk_space': False,
            'memory': False,
            'overall': False
        }
        
        try:
            # 检查数据库连接
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_status['database'] = True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            SecurityEvent.create_event(
                'SYSTEM_INTRUSION', 
                f'数据库连接失败: {str(e)}',
                severity='HIGH'
            )
        
        try:
            # 检查缓存
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                health_status['cache'] = True
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
        
        # 检查磁盘空间
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        health_status['disk_space'] = disk_percent < 90
        
        # 检查内存使用
        memory = psutil.virtual_memory()
        health_status['memory'] = memory.percent < 95
        
        # 整体健康状态
        health_status['overall'] = all([
            health_status['database'],
            health_status['cache'],
            health_status['disk_space'],
            health_status['memory']
        ])
        
        return health_status
    
    @staticmethod
    def cleanup_old_metrics(days=7):
        """
        清理旧的性能指标数据
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = PerformanceMetric.objects.filter(
            created_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old performance metrics")
        return deleted_count


class LoggingService:
    """
    日志记录服务
    """
    
    @staticmethod
    def log_user_activity(user, action, details=None, ip_address=None, user_agent=None):
        """
        记录用户活动日志
        """
        try:
            SystemLog.info(
                'USER_ACTIVITY',
                f'用户 {user.phone} 执行操作: {action}',
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                extra_data={
                    'action': action,
                    'details': details or {}
                }
            )
        except Exception as e:
            logger.error(f"Failed to log user activity: {e}")
    
    @staticmethod
    def log_system_event(level, module, message, user=None, extra_data=None):
        """
        记录系统事件日志
        """
        try:
            SystemLog.log(
                level=level,
                module=module,
                message=message,
                user=user,
                extra_data=extra_data or {}
            )
        except Exception as e:
            logger.error(f"Failed to log system event: {e}")
    
    @staticmethod
    def log_security_event(event_type, description, user=None, severity='MEDIUM', 
                          ip_address=None, user_agent=None, event_data=None):
        """
        记录安全事件
        """
        try:
            SecurityEvent.create_event(
                event_type=event_type,
                description=description,
                user=user,
                severity=severity,
                ip_address=ip_address,
                user_agent=user_agent,
                event_data=event_data or {}
            )
            
            # 同时记录到系统日志
            SystemLog.warning(
                'SECURITY',
                f'安全事件: {description}',
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                extra_data={
                    'event_type': event_type,
                    'severity': severity,
                    'event_data': event_data or {}
                }
            )
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    @staticmethod
    def cleanup_old_logs(days=30):
        """
        清理旧的日志记录
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # 清理系统日志
        system_logs_deleted = SystemLog.objects.filter(
            created_at__lt=cutoff_date
        ).delete()[0]
        
        # 清理已解决的安全事件（保留未解决的）
        security_events_deleted = SecurityEvent.objects.filter(
            created_at__lt=cutoff_date,
            status='RESOLVED'
        ).delete()[0]
        
        logger.info(f"Cleaned up {system_logs_deleted} system logs and {security_events_deleted} security events")
        return system_logs_deleted, security_events_deleted


class ConfigurationService:
    """
    配置管理服务
    """
    
    @staticmethod
    def get_system_config(key: str, default: Any = None) -> Any:
        """
        获取系统配置
        """
        return SystemConfig.get_config(key, default)
    
    @staticmethod
    def set_system_config(key: str, value: Any, config_type: str = 'SYSTEM', 
                         description: str = '') -> SystemConfig:
        """
        设置系统配置
        """
        return SystemConfig.set_config(key, value, config_type, description)
    
    @staticmethod
    def initialize_default_configs():
        """
        初始化默认系统配置
        """
        default_configs = [
            # 系统配置
            ('SITE_NAME', '非洲彩票博彩平台', 'SYSTEM', '网站名称'),
            ('SITE_URL', 'https://lottery.example.com', 'SYSTEM', '网站URL'),
            ('MAINTENANCE_MODE', False, 'SYSTEM', '维护模式开关'),
            ('MAX_LOGIN_ATTEMPTS', 5, 'SECURITY', '最大登录尝试次数'),
            ('SESSION_TIMEOUT', 3600, 'SECURITY', '会话超时时间（秒）'),
            
            # 游戏配置
            ('11X5_ENABLED', True, 'GAME', '11选5游戏开关'),
            ('SUPERLOTTO_ENABLED', True, 'GAME', '大乐透游戏开关'),
            ('SCRATCH666_ENABLED', True, 'GAME', '666刮刮乐游戏开关'),
            ('SPORTS_ENABLED', True, 'GAME', '体育博彩开关'),
            
            # 支付配置
            ('MIN_DEPOSIT_AMOUNT', 100, 'PAYMENT', '最小存款金额'),
            ('MAX_DEPOSIT_AMOUNT', 1000000, 'PAYMENT', '最大存款金额'),
            ('MIN_WITHDRAW_AMOUNT', 200, 'PAYMENT', '最小提款金额'),
            ('MAX_WITHDRAW_AMOUNT', 500000, 'PAYMENT', '最大提款金额'),
            
            # 通知配置
            ('EMAIL_NOTIFICATIONS', True, 'NOTIFICATION', '邮件通知开关'),
            ('SMS_NOTIFICATIONS', True, 'NOTIFICATION', '短信通知开关'),
            ('PUSH_NOTIFICATIONS', True, 'NOTIFICATION', '推送通知开关'),
        ]
        
        for key, value, config_type, description in default_configs:
            if not SystemConfig.objects.filter(key=key).exists():
                SystemConfig.set_config(key, value, config_type, description)
        
        logger.info("Default system configurations initialized")


class AlertService:
    """
    告警服务
    """
    
    @staticmethod
    def check_performance_alerts():
        """
        检查性能告警
        """
        alerts = []
        
        # 获取最新的性能指标
        latest_metrics = PerformanceMetric.objects.filter(
            created_at__gte=timezone.now() - timedelta(minutes=5)
        ).order_by('metric_name', '-created_at').distinct('metric_name')
        
        for metric in latest_metrics:
            if metric.is_critical:
                alerts.append({
                    'level': 'CRITICAL',
                    'message': f'{metric.metric_name} 达到严重阈值: {metric.value} {metric.unit}',
                    'metric': metric
                })
                
                # 创建安全事件
                SecurityEvent.create_event(
                    'SYSTEM_INTRUSION',
                    f'系统性能指标 {metric.metric_name} 达到严重阈值: {metric.value} {metric.unit}',
                    severity='HIGH'
                )
                
            elif metric.is_warning:
                alerts.append({
                    'level': 'WARNING',
                    'message': f'{metric.metric_name} 达到警告阈值: {metric.value} {metric.unit}',
                    'metric': metric
                })
        
        return alerts
    
    @staticmethod
    def check_security_alerts():
        """
        检查安全告警
        """
        alerts = []
        
        # 检查最近的高危安全事件
        recent_events = SecurityEvent.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=1),
            severity__in=['HIGH', 'CRITICAL'],
            status='OPEN'
        )
        
        for event in recent_events:
            alerts.append({
                'level': event.severity,
                'message': f'安全事件: {event.description}',
                'event': event
            })
        
        return alerts
    
    @staticmethod
    def send_alert_notification(alert):
        """
        发送告警通知
        """
        # 这里可以集成邮件、短信、钉钉等通知方式
        logger.critical(f"ALERT: {alert['message']}")
        
        # 记录告警日志
        SystemLog.critical(
            'ALERT',
            alert['message'],
            extra_data=alert
        )


class MaintenanceService:
    """
    维护服务
    """
    
    @staticmethod
    def enable_maintenance_mode(title="系统维护中", message="系统正在维护中，请稍后再试", 
                               start_time=None, end_time=None, allowed_ips=None):
        """
        启用维护模式
        """
        from .models import MaintenanceMode
        
        # 禁用所有现有的维护模式
        MaintenanceMode.objects.update(is_enabled=False)
        
        # 创建新的维护模式
        maintenance = MaintenanceMode.objects.create(
            is_enabled=True,
            title=title,
            message=message,
            start_time=start_time,
            end_time=end_time,
            allowed_ips=allowed_ips or []
        )
        
        SystemLog.warning(
            'MAINTENANCE',
            f'维护模式已启用: {title}',
            extra_data={
                'start_time': start_time.isoformat() if start_time else None,
                'end_time': end_time.isoformat() if end_time else None
            }
        )
        
        return maintenance
    
    @staticmethod
    def disable_maintenance_mode():
        """
        禁用维护模式
        """
        from .models import MaintenanceMode
        
        updated = MaintenanceMode.objects.filter(is_enabled=True).update(is_enabled=False)
        
        if updated:
            SystemLog.info('MAINTENANCE', '维护模式已禁用')
        
        return updated > 0
    
    @staticmethod
    def is_maintenance_active():
        """
        检查维护模式是否激活
        """
        from .models import MaintenanceMode
        
        maintenance = MaintenanceMode.get_current_maintenance()
        return maintenance and maintenance.is_active if maintenance else False


# 初始化服务
def initialize_system():
    """
    初始化系统服务
    """
    try:
        # 初始化默认配置
        ConfigurationService.initialize_default_configs()
        
        # 记录系统启动日志
        SystemLog.info('SYSTEM', '系统服务初始化完成')
        
        logger.info("System services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize system services: {e}")
        SystemLog.error('SYSTEM', f'系统服务初始化失败: {str(e)}')