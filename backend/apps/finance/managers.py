"""
财务管理模型管理器
"""

from django.db import models
from django.utils import timezone
from datetime import date, timedelta


class TransactionManager(models.Manager):
    """
    交易记录管理器
    """
    
    def get_table_name(self, date_obj):
        """获取按月分表的表名"""
        return f"transactions_{date_obj.strftime('%Y_%m')}"
    
    def create_monthly_table(self, date_obj):
        """创建月度交易表（如果需要）"""
        from django.db import connection
        from django.core.management.color import no_style
        from django.db import models
        
        table_name = self.get_table_name(date_obj)
        
        # 检查表是否已存在
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, [table_name])
            
            if not cursor.fetchone()[0]:
                # 创建分表，继承主表结构
                cursor.execute(f"""
                    CREATE TABLE {table_name} (
                        LIKE finance_transaction INCLUDING DEFAULTS INCLUDING CONSTRAINTS INCLUDING INDEXES
                    );
                """)
                
                # 添加分区约束（可选）
                start_date = date_obj.replace(day=1)
                if date_obj.month == 12:
                    end_date = start_date.replace(year=start_date.year + 1, month=1)
                else:
                    end_date = start_date.replace(month=start_date.month + 1)
                
                cursor.execute(f"""
                    ALTER TABLE {table_name} 
                    ADD CONSTRAINT {table_name}_date_check 
                    CHECK (created_at >= %s AND created_at < %s);
                """, [start_date, end_date])
                
                return True
        return False
    
    def get_user_transactions(self, user, days=30):
        """获取用户最近交易记录"""
        start_date = timezone.now() - timedelta(days=days)
        return self.filter(
            user=user,
            created_at__gte=start_date
        ).order_by('-created_at')
    
    def get_pending_transactions(self):
        """获取待处理的交易"""
        return self.filter(status='PENDING')
    
    def get_daily_stats(self, date_obj=None):
        """获取每日交易统计"""
        if date_obj is None:
            date_obj = date.today()
        
        return self.filter(
            created_at__date=date_obj,
            status='COMPLETED'
        ).aggregate(
            total_count=models.Count('id'),
            total_amount=models.Sum('amount'),
            deposit_count=models.Count('id', filter=models.Q(type='DEPOSIT')),
            deposit_amount=models.Sum('amount', filter=models.Q(type='DEPOSIT')),
            withdraw_count=models.Count('id', filter=models.Q(type='WITHDRAW')),
            withdraw_amount=models.Sum('amount', filter=models.Q(type='WITHDRAW')),
        )


class BalanceLogManager(models.Manager):
    """
    余额日志管理器
    """
    
    def get_user_logs(self, user, days=30):
        """获取用户余额变动日志"""
        start_date = timezone.now() - timedelta(days=days)
        return self.filter(
            user=user,
            created_at__gte=start_date
        ).order_by('-created_at')
    
    def get_balance_changes(self, user, start_date=None, end_date=None):
        """获取指定时间段的余额变动"""
        queryset = self.filter(user=user)
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset.order_by('-created_at')


class BankAccountManager(models.Manager):
    """
    银行账户管理器
    """
    
    def get_user_accounts(self, user):
        """获取用户银行账户"""
        return self.filter(user=user).order_by('-is_default', '-created_at')
    
    def get_default_account(self, user):
        """获取用户默认银行账户"""
        return self.filter(user=user, is_default=True).first()
    
    def get_verified_accounts(self, user):
        """获取用户已验证的银行账户"""
        return self.filter(user=user, is_verified=True)


class PaymentMethodManager(models.Manager):
    """
    支付方式管理器
    """
    
    def get_active_methods(self):
        """获取活跃的支付方式"""
        return self.filter(is_active=True).order_by('name')
    
    def get_deposit_methods(self):
        """获取支持存款的支付方式"""
        return self.filter(is_active=True, is_deposit_enabled=True).order_by('name')
    
    def get_withdraw_methods(self):
        """获取支持提款的支付方式"""
        return self.filter(is_active=True, is_withdraw_enabled=True).order_by('name')
    
    def get_by_provider(self, provider):
        """根据提供商获取支付方式"""
        return self.filter(provider=provider, is_active=True)