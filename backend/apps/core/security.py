"""
安全管理器 - 增强版
支持API安全验证、频率限制、数据加密等安全功能
"""

import hashlib
import time
import hmac
import base64
import secrets
import json
import jwt
from typing import Dict, Any, List, Tuple, Optional
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from functools import wraps
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)


class SecurityManager:
    """
    安全管理器
    """
    
    @staticmethod
    def perform_security_check(user, action: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行安全检查
        """
        try:
            # 基础安全检查
            basic_check = SecurityManager._basic_security_check(user, action)
            if not basic_check['allowed']:
                return basic_check
            
            # 频率限制检查
            rate_limit_check = SecurityManager._rate_limit_check(user, action)
            if not rate_limit_check['allowed']:
                return rate_limit_check
            
            # 风险评估
            risk_assessment = SecurityManager._risk_assessment(user, action, metadata)
            if not risk_assessment['allowed']:
                return risk_assessment
            
            # 记录安全事件
            SecurityManager._log_security_event(user, action, 'ALLOWED', metadata)
            
            return {
                'allowed': True,
                'message': '安全检查通过',
                'risk_level': risk_assessment.get('risk_level', 'LOW')
            }
            
        except Exception as e:
            logger.error(f"安全检查失败: {str(e)}")
            return {
                'allowed': False,
                'message': '安全检查失败，请稍后重试'
            }
    
    @staticmethod
    def _basic_security_check(user, action: str) -> Dict[str, Any]:
        """
        基础安全检查
        """
        # 检查用户状态
        if not user.is_active:
            return {
                'allowed': False,
                'message': '账户已被禁用'
            }
        
        # 检查账户锁定状态
        if user.locked_until and user.locked_until > timezone.now():
            return {
                'allowed': False,
                'message': f'账户已锁定，请于{user.locked_until}后重试'
            }
        
        # 检查KYC状态（对于敏感操作）
        sensitive_actions = ['WITHDRAW', 'LARGE_DEPOSIT']
        if action in sensitive_actions and user.kyc_status != 'APPROVED':
            return {
                'allowed': False,
                'message': '请先完成KYC身份验证'
            }
        
        return {'allowed': True}
    
    @staticmethod
    def _rate_limit_check(user, action: str) -> Dict[str, Any]:
        """
        频率限制检查
        """
        # 定义不同操作的频率限制
        rate_limits = {
            'LOGIN': {'count': 5, 'window': 300},  # 5次/5分钟
            'DEPOSIT': {'count': 10, 'window': 3600},  # 10次/小时
            'WITHDRAW': {'count': 3, 'window': 3600},  # 3次/小时
            'BET': {'count': 100, 'window': 3600},  # 100次/小时
            'PASSWORD_CHANGE': {'count': 3, 'window': 3600},  # 3次/小时
        }
        
        if action not in rate_limits:
            return {'allowed': True}
        
        limit_config = rate_limits[action]
        cache_key = f"rate_limit_{user.id}_{action}"
        
        # 获取当前计数
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit_config['count']:
            return {
                'allowed': False,
                'message': f'操作过于频繁，请{limit_config["window"]//60}分钟后重试'
            }
        
        # 增加计数
        cache.set(cache_key, current_count + 1, limit_config['window'])
        
        return {'allowed': True}
    
    @staticmethod
    def _risk_assessment(user, action: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        风险评估
        """
        risk_score = 0
        risk_factors = []
        
        # 用户历史行为风险评估
        user_risk = SecurityManager._assess_user_risk(user)
        risk_score += user_risk['score']
        risk_factors.extend(user_risk['factors'])
        
        # 操作特定风险评估
        action_risk = SecurityManager._assess_action_risk(action, metadata)
        risk_score += action_risk['score']
        risk_factors.extend(action_risk['factors'])
        
        # 设备和IP风险评估
        device_risk = SecurityManager._assess_device_risk(user, metadata)
        risk_score += device_risk['score']
        risk_factors.extend(device_risk['factors'])
        
        # 确定风险等级
        if risk_score >= 80:
            risk_level = 'CRITICAL'
            allowed = False
            message = '检测到高风险行为，操作被拒绝'
        elif risk_score >= 60:
            risk_level = 'HIGH'
            allowed = False
            message = '检测到可疑行为，请联系客服'
        elif risk_score >= 40:
            risk_level = 'MEDIUM'
            allowed = True
            message = '中等风险，已记录'
        else:
            risk_level = 'LOW'
            allowed = True
            message = '风险评估通过'
        
        return {
            'allowed': allowed,
            'message': message,
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors
        }
    
    @staticmethod
    def _assess_user_risk(user) -> Dict[str, Any]:
        """
        评估用户风险
        """
        score = 0
        factors = []
        
        # 新用户风险
        account_age = (timezone.now() - user.created_at).days
        if account_age < 7:
            score += 20
            factors.append('新注册用户')
        elif account_age < 30:
            score += 10
            factors.append('注册时间较短')
        
        # 登录失败次数
        if user.login_attempts >= 3:
            score += 15
            factors.append('多次登录失败')
        
        # KYC状态
        if user.kyc_status != 'APPROVED':
            score += 10
            factors.append('未完成KYC验证')
        
        return {'score': score, 'factors': factors}
    
    @staticmethod
    def _assess_action_risk(action: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        评估操作风险
        """
        score = 0
        factors = []
        
        # 高风险操作
        high_risk_actions = ['WITHDRAW', 'LARGE_DEPOSIT', 'PASSWORD_CHANGE']
        if action in high_risk_actions:
            score += 15
            factors.append(f'高风险操作: {action}')
        
        # 大额交易
        if metadata and 'amount' in metadata:
            amount = float(metadata['amount'])
            if amount >= 100000:  # 10万奈拉
                score += 25
                factors.append('大额交易')
            elif amount >= 50000:  # 5万奈拉
                score += 15
                factors.append('较大金额交易')
        
        return {'score': score, 'factors': factors}
    
    @staticmethod
    def _assess_device_risk(user, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        评估设备和IP风险
        """
        score = 0
        factors = []
        
        # 这里可以添加设备指纹、IP地理位置等检查
        # 由于是示例，我们简化处理
        
        if metadata and 'ip_address' in metadata:
            # 检查IP是否在黑名单中
            ip_address = metadata['ip_address']
            if SecurityManager._is_blacklisted_ip(ip_address):
                score += 50
                factors.append('IP地址在黑名单中')
        
        return {'score': score, 'factors': factors}
    
    @staticmethod
    def _is_blacklisted_ip(ip_address: str) -> bool:
        """
        检查IP是否在黑名单中
        """
        # 这里应该查询IP黑名单数据库
        # 示例中返回False
        return False
    
    @staticmethod
    def _log_security_event(user, action: str, result: str, metadata: Dict[str, Any] = None):
        """
        记录安全事件
        """
        try:
            from apps.core.models import SecurityLog
            
            SecurityLog.objects.create(
                user=user,
                action=action,
                result=result,
                metadata=metadata or {},
                ip_address=metadata.get('ip_address') if metadata else None,
                user_agent=metadata.get('user_agent') if metadata else None,
            )
        except Exception as e:
            logger.error(f"记录安全事件失败: {str(e)}")
    
    @staticmethod
    def generate_csrf_token(user_id: str) -> str:
        """
        生成CSRF令牌
        """
        timestamp = str(int(time.time()))
        data = f"{user_id}_{timestamp}_{settings.SECRET_KEY}"
        token = hashlib.sha256(data.encode()).hexdigest()
        
        # 缓存令牌（1小时有效）
        cache_key = f"csrf_token_{user_id}"
        cache.set(cache_key, token, 3600)
        
        return token
    
    @staticmethod
    def verify_csrf_token(user_id: str, token: str) -> bool:
        """
        验证CSRF令牌
        """
        cache_key = f"csrf_token_{user_id}"
        cached_token = cache.get(cache_key)
        
        return cached_token == token
    
    @staticmethod
    def encrypt_sensitive_data(data: str) -> str:
        """
        加密敏感数据
        """
        from cryptography.fernet import Fernet
        
        # 这里应该使用配置的加密密钥
        # 示例中使用简单的base64编码
        import base64
        return base64.b64encode(data.encode()).decode()
    
    @staticmethod
    def decrypt_sensitive_data(encrypted_data: str) -> str:
        """
        解密敏感数据
        """
        import base64
        try:
            return base64.b64decode(encrypted_data.encode()).decode()
        except:
            return encrypted_data
    
    @staticmethod
    def validate_request_signature(request_data: Dict[str, Any], signature: str, secret: str) -> bool:
        """
        验证请求签名
        """
        import json
        
        # 生成预期签名
        sorted_data = json.dumps(request_data, sort_keys=True, separators=(',', ':'))
        expected_signature = hashlib.sha256(f"{sorted_data}{secret}".encode()).hexdigest()
        
        return signature == expected_signature
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """
        获取安全头部
        """
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
        }


class EnhancedSecurityManager:
    """增强安全管理器"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """获取或创建加密密钥"""
        key = getattr(settings, 'ENCRYPTION_KEY', None)
        if not key:
            # 基于SECRET_KEY生成固定密钥
            password = settings.SECRET_KEY.encode()
            salt = b'lottery_platform_salt'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
        else:
            key = key.encode() if isinstance(key, str) else key
        
        return key
    
    def encrypt_data(self, data: str) -> str:
        """加密数据"""
        try:
            encrypted = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"数据加密失败: {e}")
            return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """解密数据"""
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"数据解密失败: {e}")
            return encrypted_data


class APISecurityValidator:
    """API安全验证器"""
    
    @staticmethod
    def validate_api_signature(request, secret_key: str = None) -> bool:
        """验证API签名"""
        if not secret_key:
            secret_key = settings.SECRET_KEY
        
        # 获取签名头
        signature = request.META.get('HTTP_X_SIGNATURE')
        timestamp = request.META.get('HTTP_X_TIMESTAMP')
        
        if not signature or not timestamp:
            return False
        
        # 检查时间戳（防重放攻击）
        try:
            request_time = int(timestamp)
            current_time = int(time.time())
            if abs(current_time - request_time) > 300:  # 5分钟内有效
                return False
        except ValueError:
            return False
        
        # 生成预期签名
        if request.method == 'GET':
            data = request.GET.urlencode()
        else:
            data = request.body.decode('utf-8') if request.body else ''
        
        message = f"{request.method}{request.path}{data}{timestamp}"
        expected_signature = hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    @staticmethod
    def generate_api_signature(method: str, path: str, data: str, timestamp: int, secret_key: str) -> str:
        """生成API签名"""
        message = f"{method}{path}{data}{timestamp}"
        return hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()


class AdvancedRateLimiter:
    """高级频率限制器"""
    
    @staticmethod
    def check_rate_limit(identifier: str, limit_type: str, custom_limits: Dict = None) -> Tuple[bool, Dict]:
        """检查频率限制"""
        # 默认限制配置
        default_limits = {
            'api_call': {'requests': 1000, 'window': 3600},  # 1000次/小时
            'login': {'requests': 5, 'window': 300},  # 5次/5分钟
            'sensitive_op': {'requests': 10, 'window': 3600},  # 10次/小时
            'payment': {'requests': 20, 'window': 3600},  # 20次/小时
            'global': {'requests': 10000, 'window': 3600},  # 全局限制
        }
        
        limits = custom_limits or default_limits
        
        if limit_type not in limits:
            return True, {'allowed': True}
        
        config = limits[limit_type]
        cache_key = f"rate_limit:{limit_type}:{identifier}"
        
        # 使用滑动窗口算法
        current_time = int(time.time())
        window_start = current_time - config['window']
        
        # 获取当前窗口内的请求记录
        requests_data = cache.get(cache_key, [])
        
        # 清理过期记录
        valid_requests = [req_time for req_time in requests_data if req_time > window_start]
        
        # 检查是否超过限制
        if len(valid_requests) >= config['requests']:
            return False, {
                'allowed': False,
                'limit': config['requests'],
                'window': config['window'],
                'retry_after': valid_requests[0] + config['window'] - current_time
            }
        
        # 添加当前请求
        valid_requests.append(current_time)
        cache.set(cache_key, valid_requests, config['window'])
        
        return True, {
            'allowed': True,
            'remaining': config['requests'] - len(valid_requests),
            'reset_time': window_start + config['window']
        }
    
    @staticmethod
    def get_client_identifier(request) -> str:
        """获取客户端标识符"""
        # 优先使用用户ID
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"user:{request.user.id}"
        
        # 使用IP地址
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        return f"ip:{ip}"


class SecurityAuditor:
    """安全审计器"""
    
    @staticmethod
    def log_security_event(event_type: str, user_id: int = None, details: Dict = None, 
                          severity: str = 'INFO', ip_address: str = None):
        """记录安全事件"""
        try:
            from apps.core.models import SecurityAuditLog
            
            SecurityAuditLog.objects.create(
                event_type=event_type,
                user_id=user_id,
                details=details or {},
                severity=severity,
                ip_address=ip_address,
                timestamp=timezone.now()
            )
        except Exception as e:
            logger.error(f"记录安全事件失败: {e}")
    
    @staticmethod
    def detect_suspicious_activity(user_id: int, activity_type: str, metadata: Dict) -> bool:
        """检测可疑活动"""
        suspicious_patterns = [
            SecurityAuditor._check_rapid_requests(user_id, activity_type),
            SecurityAuditor._check_unusual_amounts(user_id, metadata),
            SecurityAuditor._check_location_anomaly(user_id, metadata),
            SecurityAuditor._check_device_change(user_id, metadata),
        ]
        
        return any(suspicious_patterns)
    
    @staticmethod
    def _check_rapid_requests(user_id: int, activity_type: str) -> bool:
        """检查快速请求模式"""
        cache_key = f"activity_pattern:{user_id}:{activity_type}"
        recent_activities = cache.get(cache_key, [])
        
        current_time = time.time()
        # 清理1分钟前的记录
        recent_activities = [t for t in recent_activities if current_time - t < 60]
        
        # 如果1分钟内超过20次请求，标记为可疑
        if len(recent_activities) > 20:
            return True
        
        recent_activities.append(current_time)
        cache.set(cache_key, recent_activities, 300)
        return False
    
    @staticmethod
    def _check_unusual_amounts(user_id: int, metadata: Dict) -> bool:
        """检查异常金额"""
        if 'amount' not in metadata:
            return False
        
        amount = float(metadata['amount'])
        
        # 获取用户历史平均交易金额
        cache_key = f"avg_amount:{user_id}"
        avg_amount = cache.get(cache_key, 0)
        
        # 如果金额超过历史平均的10倍，标记为可疑
        if avg_amount > 0 and amount > avg_amount * 10:
            return True
        
        return False
    
    @staticmethod
    def _check_location_anomaly(user_id: int, metadata: Dict) -> bool:
        """检查位置异常"""
        # 简化实现，实际应该使用IP地理位置服务
        return False
    
    @staticmethod
    def _check_device_change(user_id: int, metadata: Dict) -> bool:
        """检查设备变更"""
        if 'user_agent' not in metadata:
            return False
        
        cache_key = f"device_fingerprint:{user_id}"
        last_user_agent = cache.get(cache_key)
        
        current_user_agent = metadata['user_agent']
        
        if last_user_agent and last_user_agent != current_user_agent:
            # 设备发生变更
            cache.set(cache_key, current_user_agent, 86400 * 7)  # 缓存7天
            return True
        
        if not last_user_agent:
            cache.set(cache_key, current_user_agent, 86400 * 7)
        
        return False


class VulnerabilityScanner:
    """漏洞扫描器"""
    
    @staticmethod
    def scan_sql_injection(input_data: str) -> bool:
        """扫描SQL注入"""
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            r"(--|#|/\*|\*/)",
            r"(\bUNION\s+SELECT\b)",
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, input_data, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def scan_xss(input_data: str) -> bool:
        """扫描XSS攻击"""
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, input_data, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def scan_path_traversal(input_data: str) -> bool:
        """扫描路径遍历攻击"""
        path_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"/etc/passwd",
            r"/proc/",
            r"\\windows\\",
        ]
        
        for pattern in path_patterns:
            if re.search(pattern, input_data, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def comprehensive_scan(input_data: str) -> Dict[str, bool]:
        """综合漏洞扫描"""
        return {
            'sql_injection': VulnerabilityScanner.scan_sql_injection(input_data),
            'xss': VulnerabilityScanner.scan_xss(input_data),
            'path_traversal': VulnerabilityScanner.scan_path_traversal(input_data),
        }


# 装饰器函数
def require_api_signature(func):
    """要求API签名的装饰器"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not APISecurityValidator.validate_api_signature(request):
            return JsonResponse({
                'error': 'Invalid API signature',
                'code': 'INVALID_SIGNATURE'
            }, status=401)
        
        return func(request, *args, **kwargs)
    return wrapper


def rate_limit_advanced(limit_type: str = 'api_call', custom_limits: Dict = None):
    """高级频率限制装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            identifier = AdvancedRateLimiter.get_client_identifier(request)
            allowed, info = AdvancedRateLimiter.check_rate_limit(identifier, limit_type, custom_limits)
            
            if not allowed:
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'retry_after': info.get('retry_after', 60)
                }, status=429)
            
            # 添加速率限制头部
            response = func(request, *args, **kwargs)
            if hasattr(response, '__setitem__'):
                response['X-RateLimit-Limit'] = info.get('limit', 'unknown')
                response['X-RateLimit-Remaining'] = info.get('remaining', 'unknown')
                response['X-RateLimit-Reset'] = info.get('reset_time', 'unknown')
            
            return response
        return wrapper
    return decorator


def security_scan_input(func):
    """输入安全扫描装饰器"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        # 扫描GET参数
        for key, value in request.GET.items():
            scan_results = VulnerabilityScanner.comprehensive_scan(value)
            if any(scan_results.values()):
                SecurityAuditor.log_security_event(
                    'MALICIOUS_INPUT_DETECTED',
                    user_id=getattr(request.user, 'id', None),
                    details={'parameter': key, 'value': value, 'scan_results': scan_results},
                    severity='HIGH',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                return JsonResponse({
                    'error': 'Malicious input detected',
                    'code': 'SECURITY_VIOLATION'
                }, status=400)
        
        # 扫描POST数据
        if request.method == 'POST' and hasattr(request, 'data'):
            for key, value in request.data.items():
                if isinstance(value, str):
                    scan_results = VulnerabilityScanner.comprehensive_scan(value)
                    if any(scan_results.values()):
                        SecurityAuditor.log_security_event(
                            'MALICIOUS_INPUT_DETECTED',
                            user_id=getattr(request.user, 'id', None),
                            details={'parameter': key, 'value': value, 'scan_results': scan_results},
                            severity='HIGH',
                            ip_address=request.META.get('REMOTE_ADDR')
                        )
                        return JsonResponse({
                            'error': 'Malicious input detected',
                            'code': 'SECURITY_VIOLATION'
                        }, status=400)
        
        return func(request, *args, **kwargs)
    return wrapper


# 全局安全管理器实例
enhanced_security = EnhancedSecurityManager()
security_auditor = SecurityAuditor()
vulnerability_scanner = VulnerabilityScanner()