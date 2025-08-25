"""
核心模型
"""

import uuid
import json
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ActivityLog(models.Model):
    """
    用户活动日志
    """
    ACTION_CHOICES = [
        ('LOGIN', '登录'),
        ('LOGOUT', '登出'),
        ('REGISTER', '注册'),
        ('KYC_SUBMIT', 'KYC提交'),
        ('KYC_APPROVE', 'KYC通过'),
        ('KYC_REJECT', 'KYC拒绝'),
        ('VIP_UPGRADE', 'VIP升级'),
        ('DEPOSIT', '存款'),
        ('WITHDRAW', '提款'),
        ('BET_PLACE', '投注'),
        ('BET_WIN', '中奖'),
        ('REWARD_RECEIVE', '奖励发放'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'activity_logs'
        indexes = [
            models.Index(fields=['user', 'action', 'created_at']),
            models.Index(fields=['action', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.phone} - {self.get_action_display()} - {self.created_at}"


class SystemConfig(models.Model):
    """
    系统配置
    """
    CONFIG_TYPES = [
        ('SYSTEM', '系统配置'),
        ('GAME', '游戏配置'),
        ('PAYMENT', '支付配置'),
        ('SECURITY', '安全配置'),
        ('NOTIFICATION', '通知配置'),
        ('MAINTENANCE', '维护配置'),
    ]
    
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField()
    config_type = models.CharField(max_length=20, choices=CONFIG_TYPES, default='SYSTEM', verbose_name='配置类型')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_configs'
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
        ordering = ['config_type', 'key']
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"
    
    def get_value(self):
        """获取配置值，尝试解析JSON"""
        try:
            return json.loads(self.value)
        except (json.JSONDecodeError, TypeError):
            return self.value
    
    def set_value(self, value):
        """设置配置值，自动转换为JSON字符串"""
        if isinstance(value, (dict, list)):
            self.value = json.dumps(value, ensure_ascii=False)
        else:
            self.value = str(value)
    
    @classmethod
    def get_config(cls, key, default=None):
        """获取配置值"""
        try:
            config = cls.objects.get(key=key, is_active=True)
            return config.get_value()
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_config(cls, key, value, config_type='SYSTEM', description=''):
        """设置配置值"""
        config, created = cls.objects.get_or_create(
            key=key,
            defaults={
                'config_type': config_type,
                'description': description,
                'is_active': True
            }
        )
        config.set_value(value)
        config.save()
        return config


class Notification(models.Model):
    """
    系统通知
    """
    TYPE_CHOICES = [
        ('INFO', '信息'),
        ('SUCCESS', '成功'),
        ('WARNING', '警告'),
        ('ERROR', '错误'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='INFO')
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'notifications'
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.phone} - {self.title}"

class SystemLog(models.Model):
    """
    系统日志模型
    """
    LOG_LEVELS = [
        ('DEBUG', 'DEBUG'),
        ('INFO', 'INFO'),
        ('WARNING', 'WARNING'),
        ('ERROR', 'ERROR'),
        ('CRITICAL', 'CRITICAL'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    level = models.CharField(max_length=10, choices=LOG_LEVELS, default='INFO', verbose_name='日志级别')
    module = models.CharField(max_length=50, verbose_name='模块名称')
    message = models.TextField(verbose_name='日志消息')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='用户')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    extra_data = models.JSONField(default=dict, blank=True, verbose_name='额外数据')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_logs'
        verbose_name = '系统日志'
        verbose_name_plural = '系统日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['level', 'created_at']),
            models.Index(fields=['module', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"[{self.level}] {self.module}: {self.message[:100]}"
    
    @classmethod
    def log(cls, level, module, message, user=None, ip_address=None, user_agent=None, extra_data=None):
        """记录日志"""
        return cls.objects.create(
            level=level,
            module=module,
            message=message,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent or '',
            extra_data=extra_data or {}
        )
    
    @classmethod
    def debug(cls, module, message, **kwargs):
        return cls.log('DEBUG', module, message, **kwargs)
    
    @classmethod
    def info(cls, module, message, **kwargs):
        return cls.log('INFO', module, message, **kwargs)
    
    @classmethod
    def warning(cls, module, message, **kwargs):
        return cls.log('WARNING', module, message, **kwargs)
    
    @classmethod
    def error(cls, module, message, **kwargs):
        return cls.log('ERROR', module, message, **kwargs)
    
    @classmethod
    def critical(cls, module, message, **kwargs):
        return cls.log('CRITICAL', module, message, **kwargs)


class SecurityEvent(models.Model):
    """
    安全事件模型
    """
    EVENT_TYPES = [
        ('LOGIN_FAILED', '登录失败'),
        ('SUSPICIOUS_ACTIVITY', '可疑活动'),
        ('LARGE_TRANSACTION', '大额交易'),
        ('MULTIPLE_ACCOUNTS', '多账户关联'),
        ('IP_CHANGE', 'IP地址变更'),
        ('DEVICE_CHANGE', '设备变更'),
        ('KYC_FRAUD', 'KYC欺诈'),
        ('BETTING_ANOMALY', '投注异常'),
        ('WITHDRAWAL_RISK', '提款风险'),
        ('SYSTEM_INTRUSION', '系统入侵'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', '低'),
        ('MEDIUM', '中'),
        ('HIGH', '高'),
        ('CRITICAL', '严重'),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', '待处理'),
        ('INVESTIGATING', '调查中'),
        ('RESOLVED', '已解决'),
        ('FALSE_POSITIVE', '误报'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES, verbose_name='事件类型')
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='MEDIUM', verbose_name='严重程度')
    description = models.TextField(verbose_name='事件描述')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='相关用户')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    event_data = models.JSONField(default=dict, blank=True, verbose_name='事件数据')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN', verbose_name='处理状态')
    handled_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, 
                                   related_name='handled_security_events', verbose_name='处理人')
    handled_at = models.DateTimeField(null=True, blank=True, verbose_name='处理时间')
    resolution = models.TextField(blank=True, verbose_name='处理结果')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'security_events'
        verbose_name = '安全事件'
        verbose_name_plural = '安全事件'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'severity', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"[{self.get_severity_display()}] {self.get_event_type_display()}: {self.description[:100]}"
    
    @classmethod
    def create_event(cls, event_type, description, user=None, severity='MEDIUM', 
                     ip_address=None, user_agent=None, event_data=None):
        """创建安全事件"""
        return cls.objects.create(
            event_type=event_type,
            severity=severity,
            description=description,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent or '',
            event_data=event_data or {}
        )


class PerformanceMetric(models.Model):
    """
    性能指标模型
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric_name = models.CharField(max_length=100, verbose_name='指标名称')
    value = models.FloatField(verbose_name='指标值')
    unit = models.CharField(max_length=20, blank=True, verbose_name='单位')
    server_name = models.CharField(max_length=50, blank=True, verbose_name='服务器名称')
    warning_threshold = models.FloatField(null=True, blank=True, verbose_name='警告阈值')
    critical_threshold = models.FloatField(null=True, blank=True, verbose_name='严重阈值')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='元数据')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'performance_metrics'
        verbose_name = '性能指标'
        verbose_name_plural = '性能指标'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['metric_name', 'created_at']),
            models.Index(fields=['server_name', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.metric_name}: {self.value} {self.unit}"
    
    @property
    def is_warning(self):
        """是否达到警告阈值"""
        return self.warning_threshold and self.value >= self.warning_threshold
    
    @property
    def is_critical(self):
        """是否达到严重阈值"""
        return self.critical_threshold and self.value >= self.critical_threshold
    
    @classmethod
    def record_metric(cls, metric_name, value, unit='', server_name='', 
                      warning_threshold=None, critical_threshold=None, metadata=None):
        """记录性能指标"""
        return cls.objects.create(
            metric_name=metric_name,
            value=value,
            unit=unit,
            server_name=server_name,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            metadata=metadata or {}
        )


class GameConfig(models.Model):
    """
    游戏配置模型
    """
    GAME_TYPES = [
        ('11x5', '11选5'),
        ('superlotto', '大乐透'),
        ('scratch666', '666刮刮乐'),
        ('sports', '体育博彩'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game_type = models.CharField(max_length=20, choices=GAME_TYPES, verbose_name='游戏类型')
    config_key = models.CharField(max_length=100, verbose_name='配置键')
    config_value = models.JSONField(verbose_name='配置值')
    description = models.TextField(blank=True, verbose_name='描述')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'game_configs'
        verbose_name = '游戏配置'
        verbose_name_plural = '游戏配置'
        unique_together = ['game_type', 'config_key']
        ordering = ['game_type', 'config_key']
    
    def __str__(self):
        return f"{self.get_game_type_display()} - {self.config_key}"
    
    @classmethod
    def get_game_config(cls, game_type, config_key, default=None):
        """获取游戏配置"""
        try:
            config = cls.objects.get(game_type=game_type, config_key=config_key, is_active=True)
            return config.config_value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_game_config(cls, game_type, config_key, config_value, description=''):
        """设置游戏配置"""
        config, created = cls.objects.get_or_create(
            game_type=game_type,
            config_key=config_key,
            defaults={
                'config_value': config_value,
                'description': description,
                'is_active': True
            }
        )
        if not created:
            config.config_value = config_value
            config.description = description
            config.save()
        return config


class MaintenanceMode(models.Model):
    """
    维护模式模型
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_enabled = models.BooleanField(default=False, verbose_name='是否启用维护模式')
    title = models.CharField(max_length=200, default='系统维护中', verbose_name='维护标题')
    message = models.TextField(default='系统正在维护中，请稍后再试', verbose_name='维护消息')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    allowed_ips = models.JSONField(default=list, blank=True, verbose_name='允许访问的IP')
    affected_modules = models.JSONField(default=list, blank=True, verbose_name='影响的模块')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'maintenance_mode'
        verbose_name = '维护模式'
        verbose_name_plural = '维护模式'
        ordering = ['-created_at']
    
    def __str__(self):
        status = '启用' if self.is_enabled else '禁用'
        return f"维护模式 - {status}"
    
    @property
    def is_active(self):
        """检查维护模式是否激活"""
        if not self.is_enabled:
            return False
        
        now = timezone.now()
        if self.start_time and now < self.start_time:
            return False
        if self.end_time and now > self.end_time:
            return False
        
        return True
    
    @classmethod
    def get_current_maintenance(cls):
        """获取当前维护模式"""
        try:
            return cls.objects.filter(is_enabled=True).first()
        except cls.DoesNotExist:
            return None


class SecurityAuditLog(models.Model):
    """安全审计日志模型"""
    SEVERITY_CHOICES = [
        ('INFO', '信息'),
        ('WARNING', '警告'),
        ('HIGH', '高危'),
        ('CRITICAL', '严重'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=100, verbose_name='事件类型')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='用户')
    details = models.JSONField(default=dict, verbose_name='详细信息')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='INFO', verbose_name='严重程度')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    timestamp = models.DateTimeField(default=timezone.now, verbose_name='时间戳')
    resolved = models.BooleanField(default=False, verbose_name='已解决')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='解决时间')
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='resolved_security_logs', verbose_name='解决人')

    class Meta:
        db_table = 'security_audit_logs'
        verbose_name = '安全审计日志'
        verbose_name_plural = '安全审计日志'
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['severity', 'resolved']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['ip_address']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.event_type} - {self.severity} - {self.timestamp}'


class VulnerabilityScan(models.Model):
    """漏洞扫描记录模型"""
    SCAN_STATUS_CHOICES = [
        ('PENDING', '待处理'),
        ('RUNNING', '运行中'),
        ('COMPLETED', '已完成'),
        ('FAILED', '失败'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scan_id = models.CharField(max_length=100, unique=True, verbose_name='扫描ID')
    scan_type = models.CharField(max_length=50, verbose_name='扫描类型')
    status = models.CharField(max_length=20, choices=SCAN_STATUS_CHOICES, default='PENDING', verbose_name='状态')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    results = models.JSONField(default=dict, verbose_name='扫描结果')
    summary = models.JSONField(default=dict, verbose_name='结果摘要')
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='发起人')

    class Meta:
        db_table = 'vulnerability_scans'
        verbose_name = '漏洞扫描'
        verbose_name_plural = '漏洞扫描'
        indexes = [
            models.Index(fields=['scan_type', 'status']),
            models.Index(fields=['started_at']),
        ]
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.scan_type} - {self.status} - {self.started_at}'


class SecurityIncident(models.Model):
    """安全事件模型"""
    INCIDENT_STATUS_CHOICES = [
        ('OPEN', '开放'),
        ('INVESTIGATING', '调查中'),
        ('RESOLVED', '已解决'),
        ('CLOSED', '已关闭'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', '低'),
        ('MEDIUM', '中'),
        ('HIGH', '高'),
        ('CRITICAL', '严重'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident_id = models.CharField(max_length=100, unique=True, verbose_name='事件ID')
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(verbose_name='描述')
    status = models.CharField(max_length=20, choices=INCIDENT_STATUS_CHOICES, default='OPEN', verbose_name='状态')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM', verbose_name='优先级')
    affected_users = models.ManyToManyField(User, blank=True, verbose_name='受影响用户')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='解决时间')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='assigned_incidents', verbose_name='分配给')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='created_incidents', verbose_name='创建人')
    metadata = models.JSONField(default=dict, verbose_name='元数据')

    class Meta:
        db_table = 'security_incidents'
        verbose_name = '安全事件'
        verbose_name_plural = '安全事件'
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['created_at']),
            models.Index(fields=['assigned_to']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.incident_id} - {self.title}'


class ThreatIntelligence(models.Model):
    """威胁情报模型"""
    THREAT_TYPE_CHOICES = [
        ('IP_BLACKLIST', 'IP黑名单'),
        ('MALWARE_HASH', '恶意软件哈希'),
        ('SUSPICIOUS_DOMAIN', '可疑域名'),
        ('ATTACK_PATTERN', '攻击模式'),
        ('VULNERABILITY', '漏洞信息'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    threat_type = models.CharField(max_length=50, choices=THREAT_TYPE_CHOICES, verbose_name='威胁类型')
    indicator = models.CharField(max_length=500, verbose_name='威胁指标')
    description = models.TextField(blank=True, verbose_name='描述')
    confidence_level = models.IntegerField(default=50, verbose_name='置信度')  # 0-100
    severity = models.CharField(max_length=20, choices=SecurityAuditLog.SEVERITY_CHOICES, 
                               default='INFO', verbose_name='严重程度')
    source = models.CharField(max_length=100, blank=True, verbose_name='来源')
    first_seen = models.DateTimeField(auto_now_add=True, verbose_name='首次发现')
    last_seen = models.DateTimeField(auto_now=True, verbose_name='最后发现')
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    metadata = models.JSONField(default=dict, verbose_name='元数据')

    class Meta:
        db_table = 'threat_intelligence'
        verbose_name = '威胁情报'
        verbose_name_plural = '威胁情报'
        indexes = [
            models.Index(fields=['threat_type', 'is_active']),
            models.Index(fields=['indicator']),
            models.Index(fields=['severity']),
        ]
        ordering = ['-last_seen']

    def __str__(self):
        return f'{self.threat_type} - {self.indicator[:50]}'