"""
用户模块管理后台配置
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, KYCDocument, LoginLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    用户管理
    """
    list_display = [
        'phone', 'full_name', 'email', 'country', 'vip_level',
        'total_turnover', 'kyc_status', 'is_active', 'created_at'
    ]
    list_filter = [
        'country', 'vip_level', 'kyc_status', 'is_active',
        'two_factor_enabled', 'created_at'
    ]
    search_fields = ['phone', 'email', 'full_name', 'referral_code']
    ordering = ['-created_at']
    readonly_fields = [
        'id', 'referral_code', 'total_turnover', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('id', 'phone', 'email', 'full_name', 'country')
        }),
        ('认证信息', {
            'fields': ('username', 'password', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('VIP信息', {
            'fields': ('vip_level', 'total_turnover')
        }),
        ('推荐信息', {
            'fields': ('referral_code', 'referred_by')
        }),
        ('KYC信息', {
            'fields': ('kyc_status',)
        }),
        ('安全信息', {
            'fields': ('two_factor_enabled', 'login_attempts', 'locked_until', 'last_login_ip')
        }),
        ('时间信息', {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    用户资料管理
    """
    list_display = ['user', 'gender', 'city', 'state', 'language', 'created_at']
    list_filter = ['gender', 'language', 'email_notifications', 'sms_notifications']
    search_fields = ['user__phone', 'user__full_name', 'city', 'state']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    """
    KYC文档管理
    """
    list_display = [
        'user', 'document_type', 'document_number', 'status',
        'confidence_score', 'created_at'
    ]
    list_filter = ['document_type', 'status', 'created_at']
    search_fields = ['user__phone', 'user__full_name', 'document_number']
    readonly_fields = ['created_at', 'updated_at', 'ocr_data', 'confidence_score']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'document_type', 'document_number')
        }),
        ('文档图片', {
            'fields': ('front_image', 'back_image', 'selfie_image')
        }),
        ('审核信息', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'rejection_reason')
        }),
        ('OCR识别', {
            'fields': ('ocr_data', 'confidence_score'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'reviewed_by')
    
    actions = ['approve_documents', 'reject_documents']
    
    def approve_documents(self, request, queryset):
        """批量通过KYC文档"""
        from django.utils import timezone
        
        updated = queryset.filter(status='PENDING').update(
            status='APPROVED',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        
        # 更新用户KYC状态
        for doc in queryset.filter(status='APPROVED'):
            doc.user.kyc_status = 'APPROVED'
            doc.user.kyc_approved_at = timezone.now()
            doc.user.save()
        
        self.message_user(request, f'成功通过 {updated} 个KYC文档')
    
    approve_documents.short_description = '通过选中的KYC文档'
    
    def reject_documents(self, request, queryset):
        """批量拒绝KYC文档"""
        from django.utils import timezone
        
        updated = queryset.filter(status='PENDING').update(
            status='REJECTED',
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
            rejection_reason='批量拒绝'
        )
        
        # 更新用户KYC状态
        for doc in queryset.filter(status='REJECTED'):
            doc.user.kyc_status = 'REJECTED'
            doc.user.save()
        
        self.message_user(request, f'成功拒绝 {updated} 个KYC文档')
    
    reject_documents.short_description = '拒绝选中的KYC文档'


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    """
    登录日志管理
    """
    list_display = [
        'user', 'ip_address', 'success', 'failure_reason',
        'country', 'city', 'created_at'
    ]
    list_filter = ['success', 'country', 'created_at']
    search_fields = ['user__phone', 'user__full_name', 'ip_address']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False