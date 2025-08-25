"""
用户模型 - 扩展Django用户模型，支持大规模用户
"""

import uuid
import secrets
import string
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.core.cache import cache
from decimal import Decimal


class User(AbstractUser):
    """
    扩展用户模型
    支持手机号登录、VIP等级、推荐系统等功能
    """
    
    # 基础字段
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_regex = RegexValidator(
        regex=r'^\+234[0-9]{10}$',
        message="手机号格式: +2348012345678"
    )
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        unique=True,
        help_text="尼日利亚手机号格式: +2348012345678"
    )
    country = models.CharField(
        max_length=2, 
        default='NG',
        choices=[
            ('NG', 'Nigeria'),
            ('CM', 'Cameroon'),
        ],
        db_index=True
    )
    full_name = models.CharField(max_length=100, help_text="完整姓名")
    
    # KYC相关
    kyc_status = models.CharField(
        max_length=20,
        default='PENDING',
        choices=[
            ('PENDING', '待审核'),
            ('APPROVED', '已通过'),
            ('REJECTED', '已拒绝'),
            ('EXPIRED', '已过期'),
        ],
        db_index=True
    )
    kyc_submitted_at = models.DateTimeField(null=True, blank=True)
    kyc_approved_at = models.DateTimeField(null=True, blank=True)
    
    # VIP等级系统
    vip_level = models.IntegerField(
        default=0,
        choices=[
            (0, 'VIP0'),
            (1, 'VIP1'),
            (2, 'VIP2'),
            (3, 'VIP3'),
            (4, 'VIP4'),
            (5, 'VIP5'),
            (6, 'VIP6'),
            (7, 'VIP7'),
        ],
        db_index=True
    )
    total_turnover = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="累计有效流水"
    )
    
    # 推荐系统
    referral_code = models.CharField(
        max_length=20, 
        unique=True, 
        db_index=True,
        help_text="推荐码(8位字母数字组合)"
    )
    referred_by = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='referrals',
        help_text="推荐人"
    )
    
    # 安全相关
    login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['phone', 'is_active']),
            models.Index(fields=['vip_level', 'total_turnover']),
            models.Index(fields=['referral_code']),
            models.Index(fields=['country', 'is_active']),
            models.Index(fields=['kyc_status']),
            models.Index(fields=['created_at']),
        ]
        
    def save(self, *args, **kwargs):
        # 自动生成推荐码
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
        
        # 自动设置用户名为手机号
        if not self.username:
            self.username = self.phone
            
        super().save(*args, **kwargs)
        
        # 清除相关缓存
        self.clear_cache()
    
    def generate_referral_code(self):
        """生成8位推荐码"""
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            if not User.objects.filter(referral_code=code).exists():
                return code
    
    def get_vip_info(self):
        """获取VIP等级信息"""
        cache_key = f'user_vip_{self.id}'
        vip_info = cache.get(cache_key)
        
        if vip_info is None:
            from apps.rewards.models import VIPLevel
            try:
                vip_level = VIPLevel.objects.get(level=self.vip_level)
                vip_info = {
                    'level': self.vip_level,
                    'name': vip_level.name,
                    'rebate_rate': float(vip_level.rebate_rate),
                    'withdraw_fee_rate': float(vip_level.withdraw_fee_rate),
                    'daily_withdraw_limit': float(vip_level.daily_withdraw_limit),
                    'daily_withdraw_times': vip_level.daily_withdraw_times,
                    'required_turnover': float(vip_level.required_turnover),
                    'current_turnover': float(self.total_turnover),
                    'progress_percentage': min(100, (float(self.total_turnover) / float(vip_level.required_turnover)) * 100) if vip_level.required_turnover > 0 else 100,
                }
                cache.set(cache_key, vip_info, 300)  # 缓存5分钟
            except:
                vip_info = {'level': 0, 'name': 'VIP0'}
                
        return vip_info
    
    def get_referral_tree(self, max_depth=7):
        """获取推荐关系树"""
        cache_key = f'user_referral_tree_{self.id}'
        tree = cache.get(cache_key)
        
        if tree is None:
            tree = []
            current_level = [self]
            
            for depth in range(1, max_depth + 1):
                next_level = []
                for user in current_level:
                    referrals = User.objects.filter(referred_by=user, is_active=True)
                    for referral in referrals:
                        tree.append({
                            'level': depth,
                            'user_id': str(referral.id),
                            'phone': referral.phone,
                            'total_turnover': float(referral.total_turnover),
                            'vip_level': referral.vip_level,
                            'created_at': referral.created_at.isoformat(),
                        })
                        next_level.append(referral)
                current_level = next_level
                
            cache.set(cache_key, tree, 600)  # 缓存10分钟
            
        return tree
    
    def update_vip_level(self):
        """根据流水更新VIP等级"""
        from apps.rewards.models import VIPLevel
        
        # 获取符合条件的最高VIP等级
        new_level = VIPLevel.objects.filter(
            required_turnover__lte=self.total_turnover
        ).order_by('-level').first()
        
        if new_level and new_level.level > self.vip_level:
            old_level = self.vip_level
            self.vip_level = new_level.level
            self.save()
            
            # 记录VIP升级日志
            from apps.core.models import ActivityLog
            ActivityLog.objects.create(
                user=self,
                action='VIP_UPGRADE',
                details={
                    'old_level': old_level,
                    'new_level': self.vip_level,
                    'turnover': float(self.total_turnover)
                }
            )
            
            return True
        return False
    
    def clear_cache(self):
        """清除用户相关缓存"""
        cache_keys = [
            f'user_vip_{self.id}',
            f'user_referral_tree_{self.id}',
            f'user_balance_{self.id}',
        ]
        cache.delete_many(cache_keys)
    
    def __str__(self):
        return f"{self.phone} (VIP{self.vip_level})"


class UserProfile(models.Model):
    """
    用户详细资料
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=1,
        choices=[
            ('M', 'Male'),
            ('F', 'Female'),
            ('O', 'Other'),
        ],
        null=True,
        blank=True
    )
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    
    # 偏好设置
    language = models.CharField(
        max_length=5,
        default='en',
        choices=[
            ('en', 'English'),
            ('fr', 'French'),
        ]
    )
    timezone = models.CharField(max_length=50, default='Africa/Lagos')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'


class KYCDocument(models.Model):
    """
    KYC身份验证文档
    """
    DOCUMENT_TYPES = [
        ('NIN', 'National ID Number'),
        ('PASSPORT', 'International Passport'),
        ('DRIVERS_LICENSE', 'Driver\'s License'),
        ('VOTERS_CARD', 'Voter\'s Card'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', '待审核'),
        ('APPROVED', '已通过'),
        ('REJECTED', '已拒绝'),
        ('EXPIRED', '已过期'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kyc_documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_number = models.CharField(max_length=50)
    
    # 文件上传
    front_image = models.ImageField(upload_to='kyc/documents/')
    back_image = models.ImageField(upload_to='kyc/documents/', null=True, blank=True)
    selfie_image = models.ImageField(upload_to='kyc/selfies/')
    
    # 审核信息
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_kyc_documents'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # OCR识别结果
    ocr_data = models.JSONField(null=True, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'kyc_documents'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['document_type', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.phone} - {self.document_type} ({self.status})"


class LoginLog(models.Model):
    """
    登录日志
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_logs')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    success = models.BooleanField()
    failure_reason = models.CharField(max_length=100, blank=True)
    
    # 地理位置信息
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'login_logs'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['success', 'created_at']),
        ]