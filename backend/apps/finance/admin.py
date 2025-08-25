"""
财务管理后台配置
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import UserBalance, Transaction, BalanceLog, BankAccount, PaymentMethod


@admin.register(UserBalance)
class UserBalanceAdmin(admin.ModelAdmin):
    """
    用户余额管理
    """
    list_display = [
        'user', 'main_balance', 'bonus_balance', 'frozen_balance',
        'total_balance_display', 'available_balance_display', 'updated_at'
    ]
    list_filter = ['updated_at']
    search_fields = ['user__phone', 'user__full_name', 'user__email']
    readonly_fields = ['updated_at']
    
    def total_balance_display(self, obj):
        return f"₦{obj.get_total_balance():,.2f}"
    total_balance_display.short_description = '总余额'
    
    def available_balance_display(self, obj):
        return f"₦{obj.get_available_balance():,.2f}"
    available_balance_display.short_description = '可用余额'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    交易记录管理
    """
    list_display = [
        'reference_id', 'user', 'type', 'amount_display', 'fee_display',
        'actual_amount_display', 'status', 'created_at', 'processed_at'
    ]
    list_filter = ['type', 'status', 'created_at', 'processed_at']
    search_fields = [
        'reference_id', 'user__phone', 'user__full_name',
        'description'
    ]
    readonly_fields = [
        'id', 'reference_id', 'actual_amount', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('id', 'user', 'type', 'status')
        }),
        ('金额信息', {
            'fields': ('amount', 'fee', 'actual_amount')
        }),
        ('关联信息', {
            'fields': ('reference_id', 'related_transaction', 'description')
        }),
        ('处理信息', {
            'fields': ('processor', 'processed_at', 'metadata')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def amount_display(self, obj):
        return f"₦{obj.amount:,.2f}"
    amount_display.short_description = '金额'
    
    def fee_display(self, obj):
        return f"₦{obj.fee:,.2f}"
    fee_display.short_description = '手续费'
    
    def actual_amount_display(self, obj):
        return f"₦{obj.actual_amount:,.2f}"
    actual_amount_display.short_description = '实际金额'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'processor')
    
    actions = ['mark_completed', 'mark_failed']
    
    def mark_completed(self, request, queryset):
        """批量标记为完成"""
        updated = 0
        for transaction in queryset.filter(status='PENDING'):
            transaction.mark_completed(request.user)
            updated += 1
        
        self.message_user(request, f'成功标记 {updated} 个交易为完成')
    
    mark_completed.short_description = '标记为完成'
    
    def mark_failed(self, request, queryset):
        """批量标记为失败"""
        updated = 0
        for transaction in queryset.filter(status='PENDING'):
            transaction.mark_failed('管理员标记失败')
            updated += 1
        
        self.message_user(request, f'成功标记 {updated} 个交易为失败')
    
    mark_failed.short_description = '标记为失败'


@admin.register(BalanceLog)
class BalanceLogAdmin(admin.ModelAdmin):
    """
    余额变动日志管理
    """
    list_display = [
        'user', 'type', 'amount_display', 'balance_before_display',
        'balance_after_display', 'description', 'created_at'
    ]
    list_filter = ['type', 'created_at']
    search_fields = ['user__phone', 'user__full_name', 'description']
    readonly_fields = ['created_at']
    
    def amount_display(self, obj):
        return f"₦{obj.amount:,.2f}"
    amount_display.short_description = '变动金额'
    
    def balance_before_display(self, obj):
        return f"₦{obj.balance_before:,.2f}"
    balance_before_display.short_description = '变动前余额'
    
    def balance_after_display(self, obj):
        return f"₦{obj.balance_after:,.2f}"
    balance_after_display.short_description = '变动后余额'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'transaction')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    """
    银行账户管理
    """
    list_display = [
        'user', 'bank_display', 'account_number', 'account_name',
        'is_verified', 'is_default', 'created_at'
    ]
    list_filter = ['bank_code', 'is_verified', 'is_default', 'created_at']
    search_fields = [
        'user__phone', 'user__full_name', 'account_number', 'account_name'
    ]
    readonly_fields = ['created_at', 'updated_at', 'verified_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'bank_code', 'account_number', 'account_name')
        }),
        ('状态信息', {
            'fields': ('is_verified', 'is_default')
        }),
        ('验证信息', {
            'fields': ('verification_data', 'verified_at'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def bank_display(self, obj):
        return obj.get_bank_code_display()
    bank_display.short_description = '银行'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    actions = ['verify_accounts', 'set_as_default']
    
    def verify_accounts(self, request, queryset):
        """批量验证银行账户"""
        from .tasks import verify_bank_account
        
        updated = 0
        for account in queryset.filter(is_verified=False):
            verify_bank_account.delay(str(account.id))
            updated += 1
        
        self.message_user(request, f'已提交 {updated} 个银行账户进行验证')
    
    verify_accounts.short_description = '验证银行账户'
    
    def set_as_default(self, request, queryset):
        """设置为默认账户"""
        if queryset.count() != 1:
            self.message_user(request, '请选择一个账户设置为默认', level='error')
            return
        
        account = queryset.first()
        # 取消同用户的其他默认账户
        BankAccount.objects.filter(user=account.user, is_default=True).update(is_default=False)
        account.is_default = True
        account.save()
        
        self.message_user(request, f'已将 {account} 设置为默认账户')
    
    set_as_default.short_description = '设置为默认账户'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """
    支付方式管理
    """
    list_display = [
        'name', 'method_type', 'provider', 'min_amount_display',
        'max_amount_display', 'fee_display', 'is_active',
        'is_deposit_enabled', 'is_withdraw_enabled'
    ]
    list_filter = [
        'method_type', 'provider', 'is_active',
        'is_deposit_enabled', 'is_withdraw_enabled'
    ]
    search_fields = ['name', 'provider']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'method_type', 'provider')
        }),
        ('限制设置', {
            'fields': ('min_amount', 'max_amount', 'daily_limit')
        }),
        ('手续费设置', {
            'fields': ('fee_type', 'fee_value')
        }),
        ('状态设置', {
            'fields': ('is_active', 'is_deposit_enabled', 'is_withdraw_enabled')
        }),
        ('配置信息', {
            'fields': ('config',),
            'classes': ('collapse',)
        }),
    )
    
    def min_amount_display(self, obj):
        return f"₦{obj.min_amount:,.2f}"
    min_amount_display.short_description = '最小金额'
    
    def max_amount_display(self, obj):
        return f"₦{obj.max_amount:,.2f}"
    max_amount_display.short_description = '最大金额'
    
    def fee_display(self, obj):
        if obj.fee_type == 'FIXED':
            return f"₦{obj.fee_value:,.2f}"
        else:
            return f"{obj.fee_value}%"
    fee_display.short_description = '手续费'