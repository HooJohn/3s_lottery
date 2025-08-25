"""
安全防护中间件 - 增强版
支持API安全验证、频率限制、数据加密等安全功能
"""

import time
import json
import re
import hashlib
import hmac
import base64
from django.http import JsonResponse
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.utils import timezone
from .utils import get_client_ip
from .security import (
    AdvancedRateLimiter, 
    SecurityAuditor, 
    VulnerabilityScanner,
    APISecurityValidator
)
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """
    API频率限制中间件
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        # 获取客户端IP
        client_ip = get_client_ip(request)
        
        # 不同API的频率限制配置
        rate_limits = {
            '/api/v1/auth/login/': {'requests': 5, 'window': 300},  # 5次/5分钟
            '/api/v1/auth/register/': {'requests': 3, 'window': 3600},  # 3次/小时
            '/api/v1/users/2fa/send/': {'requests': 3, 'window': 300},  # 3次/5分钟
            '/api/v1/users/kyc/submit/': {'requests': 2, 'window': 3600},  # 2次/小时
        }
        
        # 检查当前路径是否需要限制
        path = request.path
        if path in rate_limits:
            limit_config = rate_limits[path]
            cache_key = f'rate_limit_{client_ip}_{path}'
            
            # 获取当前请求计数
            current_requests = cache.get(cache_key, 0)
            
            if current_requests >= limit_config['requests']:
                return JsonResponse({
                    'success': False,
                    'message': '请求过于频繁，请稍后再试',
                    'error_code': 'RATE_LIMIT_EXCEEDED'
                }, status=429)
            
            # 增加请求计数
            cache.set(cache_key, current_requests + 1, limit_config['window'])
        
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    安全头部中间件
    """
    
    def process_response(self, request, response):
        # 添加安全头部
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Content-Security-Policy'] = "default-src 'self'"
        
        # HTTPS相关头部（生产环境）
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class IPWhitelistMiddleware(MiddlewareMixin):
    """
    IP白名单中间件
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_whitelist = getattr(settings, 'ADMIN_IP_WHITELIST', [])
        super().__init__(get_response)
    
    def process_request(self, request):
        # 只对管理后台进行IP限制
        if request.path.startswith('/admin/'):
            client_ip = get_client_ip(request)
            
            if self.admin_whitelist and client_ip not in self.admin_whitelist:
                return JsonResponse({
                    'success': False,
                    'message': '访问被拒绝',
                    'error_code': 'IP_NOT_ALLOWED'
                }, status=403)
        
        return None


class DeviceTrackingMiddleware(MiddlewareMixin):
    """
    设备追踪中间件
    """
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # 生成设备指纹
            device_fingerprint = self.generate_device_fingerprint(request)
            
            # 检查设备是否可信
            if not self.is_trusted_device(request.user, device_fingerprint):
                # 记录可疑登录
                self.log_suspicious_activity(request.user, device_fingerprint, request)
        
        return None
    
    def generate_device_fingerprint(self, request):
        """
        生成设备指纹
        """
        import hashlib
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
        
        fingerprint_data = f"{user_agent}|{accept_language}|{accept_encoding}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()
    
    def is_trusted_device(self, user, device_fingerprint):
        """
        检查设备是否可信
        """
        cache_key = f'trusted_device_{user.id}_{device_fingerprint}'
        return cache.get(cache_key, False)
    
    def log_suspicious_activity(self, user, device_fingerprint, request):
        """
        记录可疑活动
        """
        from apps.core.models import ActivityLog
        
        ActivityLog.objects.create(
            user=user,
            action='SUSPICIOUS_LOGIN',
            details={
                'device_fingerprint': device_fingerprint,
                'ip_address': get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    请求日志中间件
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        # 计算请求处理时间
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # 记录慢请求
            if duration > 2.0:  # 超过2秒的请求
                self.log_slow_request(request, response, duration)
        
        return response
    
    def log_slow_request(self, request, response, duration):
        """
        记录慢请求
        """
        import logging
        
        logger = logging.getLogger('apps.performance')
        logger.warning(
            f"Slow request: {request.method} {request.path} "
            f"took {duration:.2f}s, status: {response.status_code}"
        )


class SystemMonitoringMiddleware(MiddlewareMixin):
    """
    系统监控中间件
    """
    
    def process_request(self, request):
        """
        请求开始监控
        """
        request.start_time = time.time()
        request.client_ip = get_client_ip(request)
        return None
    
    def process_response(self, request, response):
        """
        响应监控和日志记录
        """
        try:
            from .models import SystemLog, SecurityEvent
            from django.utils import timezone
            
            duration = time.time() - getattr(request, 'start_time', time.time())
            
            # 记录慢请求
            if duration > 5.0:  # 超过5秒的请求
                SystemLog.warning(
                    'PERFORMANCE',
                    f'慢请求检测: {request.method} {request.path} 耗时 {duration:.2f}s',
                    user=getattr(request, 'user', None) if hasattr(request, 'user') and request.user.is_authenticated else None,
                    ip_address=request.client_ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    extra_data={
                        'method': request.method,
                        'path': request.path,
                        'duration': duration,
                        'status_code': response.status_code
                    }
                )
            
            # 记录错误响应
            if response.status_code >= 400:
                level = 'ERROR' if response.status_code >= 500 else 'WARNING'
                SystemLog.log(
                    level,
                    'HTTP_ERROR',
                    f'HTTP错误: {response.status_code} {request.method} {request.path}',
                    user=getattr(request, 'user', None) if hasattr(request, 'user') and request.user.is_authenticated else None,
                    ip_address=request.client_ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    extra_data={
                        'method': request.method,
                        'path': request.path,
                        'status_code': response.status_code,
                        'duration': duration
                    }
                )
            
            # 检测可疑活动
            self.detect_suspicious_activity(request, response, duration)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to monitor request: {e}")
        
        return response
    
    def process_exception(self, request, exception):
        """
        异常监控
        """
        try:
            from .models import SystemLog
            
            SystemLog.error(
                'EXCEPTION',
                f'请求异常: {str(exception)}',
                user=getattr(request, 'user', None) if hasattr(request, 'user') and request.user.is_authenticated else None,
                ip_address=getattr(request, 'client_ip', None),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                extra_data={
                    'method': request.method,
                    'path': request.path,
                    'exception_type': type(exception).__name__,
                    'exception_message': str(exception)
                }
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to log exception: {e}")
        
        return None
    
    def detect_suspicious_activity(self, request, response, duration):
        """
        检测可疑活动
        """
        try:
            from .models import ActivityLog, SecurityEvent
            from django.utils import timezone
            
            # 检测频繁请求
            if hasattr(request, 'user') and request.user.is_authenticated:
                # 检查用户在过去1分钟内的请求次数
                recent_requests = ActivityLog.objects.filter(
                    user=request.user,
                    created_at__gte=timezone.now() - timezone.timedelta(minutes=1)
                ).count()
                
                if recent_requests > 100:  # 1分钟内超过100次请求
                    SecurityEvent.create_event(
                        'SUSPICIOUS_ACTIVITY',
                        f'用户 {request.user.phone} 在1分钟内发起了 {recent_requests} 次请求',
                        user=request.user,
                        severity='MEDIUM',
                        ip_address=request.client_ip,
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        event_data={
                            'request_count': recent_requests,
                            'time_window': '1_minute'
                        }
                    )
            
            # 检测异常IP活动
            if request.client_ip:
                from .models import SystemLog
                
                # 检查IP在过去5分钟内的请求次数
                recent_ip_requests = SystemLog.objects.filter(
                    ip_address=request.client_ip,
                    created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
                ).count()
                
                if recent_ip_requests > 500:  # 5分钟内超过500次请求
                    SecurityEvent.create_event(
                        'SUSPICIOUS_ACTIVITY',
                        f'IP {request.client_ip} 在5分钟内发起了 {recent_ip_requests} 次请求',
                        severity='HIGH',
                        ip_address=request.client_ip,
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        event_data={
                            'request_count': recent_ip_requests,
                            'time_window': '5_minutes'
                        }
                    )
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to detect suspicious activity: {e}")


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    维护模式中间件
    """
    
    def process_request(self, request):
        """
        检查维护模式
        """
        try:
            from .models import MaintenanceMode
            
            maintenance = MaintenanceMode.get_current_maintenance()
            if maintenance and maintenance.is_active:
                # 检查IP是否在白名单中
                client_ip = get_client_ip(request)
                if client_ip not in maintenance.allowed_ips:
                    # 检查是否是管理后台请求
                    if not request.path.startswith('/admin/'):
                        return JsonResponse({
                            'success': False,
                            'message': maintenance.message,
                            'title': maintenance.title,
                            'error_code': 'MAINTENANCE_MODE'
                        }, status=503)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to check maintenance mode: {e}")
        
        return None


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    性能监控中间件
    """
    
    def process_request(self, request):
        """
        记录请求开始时间和内存使用
        """
        import psutil
        import os
        
        request.start_time = time.time()
        request.start_memory = psutil.Process(os.getpid()).memory_info().rss
        return None
    
    def process_response(self, request, response):
        """
        记录性能指标
        """
        try:
            import psutil
            import os
            from .models import PerformanceMetric
            
            # 计算处理时间
            duration = time.time() - getattr(request, 'start_time', time.time())
            
            # 计算内存使用变化
            current_memory = psutil.Process(os.getpid()).memory_info().rss
            memory_delta = current_memory - getattr(request, 'start_memory', current_memory)
            
            # 记录API性能指标
            if request.path.startswith('/api/'):
                PerformanceMetric.record_metric(
                    'api_response_time',
                    duration * 1000,  # 转换为毫秒
                    'ms',
                    metadata={
                        'method': request.method,
                        'path': request.path,
                        'status_code': response.status_code,
                        'memory_delta': memory_delta
                    }
                )
                
                # 记录内存使用
                if abs(memory_delta) > 1024 * 1024:  # 超过1MB的内存变化
                    PerformanceMetric.record_metric(
                        'memory_usage_delta',
                        memory_delta / 1024 / 1024,  # 转换为MB
                        'MB',
                        metadata={
                            'method': request.method,
                            'path': request.path,
                            'duration': duration
                        }
                    )
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to record performance metrics: {e}")
        
        return response