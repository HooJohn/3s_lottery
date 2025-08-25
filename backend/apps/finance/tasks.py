"""
财务模块异步任务
"""

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
from datetime import timedelta

from .models import Transaction, UserBalance, BankAccount
from .services import FinanceService, BankVerificationService
from apps.users.models import User
from apps.core.models import Notification


@shared_task
def process_deposit_callback(transaction_id, status, external_reference='', metadata=None):
    """
    处理存款回调
    """
    try:
        success = FinanceService.process_deposit_callback(
            transaction_id, status, external_reference, metadata or {}
        )
        
        if success:
            return f"存款回调处理成功: {transaction_id}"
        else:
            return f"存款回调处理失败: {transaction_id}"
            
    except Exception as e:
        return f"存款回调处理异常: {str(e)}"


@shared_task
def process_withdraw_request(transaction_id):
    """
    处理提款请求
    """
    try:
        result = FinanceService.process_withdraw_request(transaction_id)
        
        if result['success']:
            return f"提款处理成功: {transaction_id}"
        else:
            return f"提款处理失败: {transaction_id} - {result['message']}"
            
    except Exception as e:
        return f"提款处理异常: {str(e)}"


@shared_task
def send_deposit_success_notification(user_id, amount):
    """
    发送存款成功通知
    """
    try:
        user = User.objects.get(id=user_id)
        
        # 创建系统通知
        Notification.objects.create(
            user=user,
            title='存款成功',
            message=f'您的存款 ₦{amount:,.2f} 已到账，感谢您的使用！',
            type='SUCCESS'
        )
        
        # 发送短信通知
        from apps.users.services import SMSService
        sms_message = f"您的存款 ₦{amount:,.2f} 已成功到账。【彩票平台】"
        SMSService.send_sms(user.phone, sms_message)
        
        # 发送邮件通知
        if user.email:
            send_mail(
                subject='存款成功通知',
                message=f'尊敬的 {user.full_name}，您的存款 ₦{amount:,.2f} 已成功到账。',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )
        
        return f"存款成功通知已发送给用户 {user.phone}"
        
    except User.DoesNotExist:
        return f"用户 {user_id} 不存在"
    except Exception as e:
        return f"发送存款成功通知失败: {str(e)}"


@shared_task
def send_withdraw_success_notification(user_id, amount):
    """
    发送提款成功通知
    """
    try:
        user = User.objects.get(id=user_id)
        
        # 创建系统通知
        Notification.objects.create(
            user=user,
            title='提款成功',
            message=f'您的提款 ₦{amount:,.2f} 已成功处理，请注意查收！',
            type='SUCCESS'
        )
        
        # 发送短信通知
        from apps.users.services import SMSService
        sms_message = f"您的提款 ₦{amount:,.2f} 已成功处理，请注意查收。【彩票平台】"
        SMSService.send_sms(user.phone, sms_message)
        
        # 发送邮件通知
        if user.email:
            send_mail(
                subject='提款成功通知',
                message=f'尊敬的 {user.full_name}，您的提款 ₦{amount:,.2f} 已成功处理。',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )
        
        return f"提款成功通知已发送给用户 {user.phone}"
        
    except User.DoesNotExist:
        return f"用户 {user_id} 不存在"
    except Exception as e:
        return f"发送提款成功通知失败: {str(e)}"


@shared_task
def verify_bank_account(bank_account_id):
    """
    验证银行账户
    """
    try:
        bank_account = BankAccount.objects.get(id=bank_account_id)
        
        result = BankVerificationService.verify_bank_account(bank_account)
        
        if result['success']:
            # 发送验证成功通知
            Notification.objects.create(
                user=bank_account.user,
                title='银行账户验证成功',
                message=f'您的{bank_account.get_bank_code_display()}账户已验证成功，现在可以正常提款。',
                type='SUCCESS'
            )
            
            return f"银行账户验证成功: {bank_account_id}"
        else:
            # 发送验证失败通知
            Notification.objects.create(
                user=bank_account.user,
                title='银行账户验证失败',
                message=f'您的{bank_account.get_bank_code_display()}账户验证失败，请检查账户信息。',
                type='ERROR'
            )
            
            return f"银行账户验证失败: {bank_account_id} - {result['message']}"
        
    except BankAccount.DoesNotExist:
        return f"银行账户 {bank_account_id} 不存在"
    except Exception as e:
        return f"银行账户验证异常: {str(e)}"


@shared_task
def process_pending_transactions():
    """
    处理待处理的交易
    """
    try:
        # 处理超时的待处理交易
        timeout_threshold = timezone.now() - timedelta(hours=2)
        
        pending_deposits = Transaction.objects.filter(
            type='DEPOSIT',
            status='PENDING',
            created_at__lt=timeout_threshold
        )
        
        timeout_count = 0
        for transaction in pending_deposits:
            transaction.mark_failed('交易超时')
            timeout_count += 1
        
        # 处理待处理的提款
        pending_withdraws = Transaction.objects.filter(
            type='WITHDRAW',
            status='PENDING',
            created_at__lt=timezone.now() - timedelta(minutes=30)
        )
        
        processed_count = 0
        for transaction in pending_withdraws:
            process_withdraw_request.delay(str(transaction.id))
            processed_count += 1
        
        return f"处理完成 - 超时交易: {timeout_count}, 待处理提款: {processed_count}"
        
    except Exception as e:
        return f"处理待处理交易异常: {str(e)}"


@shared_task
def calculate_daily_transaction_stats():
    """
    计算每日交易统计
    """
    try:
        from datetime import date
        from django.db.models import Sum, Count
        
        today = date.today()
        
        # 计算今日交易统计
        daily_stats = {
            'date': today.isoformat(),
            'total_users': User.objects.filter(transactions__created_at__date=today).distinct().count(),
            'deposit_count': Transaction.objects.filter(
                type='DEPOSIT',
                status='COMPLETED',
                created_at__date=today
            ).count(),
            'deposit_amount': Transaction.objects.filter(
                type='DEPOSIT',
                status='COMPLETED',
                created_at__date=today
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0'),
            'withdraw_count': Transaction.objects.filter(
                type='WITHDRAW',
                status='COMPLETED',
                created_at__date=today
            ).count(),
            'withdraw_amount': Transaction.objects.filter(
                type='WITHDRAW',
                status='COMPLETED',
                created_at__date=today
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0'),
        }
        
        # 这里可以将统计数据保存到数据库或发送到监控系统
        
        return f"每日交易统计计算完成: {daily_stats}"
        
    except Exception as e:
        return f"计算每日交易统计异常: {str(e)}"


@shared_task
def sync_balance_with_transactions():
    """
    同步余额与交易记录
    """
    try:
        # 检查余额与交易记录的一致性
        inconsistent_count = 0
        
        for user in User.objects.filter(is_active=True).iterator(chunk_size=100):
            try:
                balance = user.balance
                
                # 计算基于交易记录的余额
                completed_deposits = Transaction.objects.filter(
                    user=user,
                    type='DEPOSIT',
                    status='COMPLETED'
                ).aggregate(total=Sum('actual_amount'))['total'] or Decimal('0')
                
                completed_withdraws = Transaction.objects.filter(
                    user=user,
                    type='WITHDRAW',
                    status='COMPLETED'
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                
                completed_bets = Transaction.objects.filter(
                    user=user,
                    type='BET',
                    status='COMPLETED'
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                
                completed_wins = Transaction.objects.filter(
                    user=user,
                    type='WIN',
                    status='COMPLETED'
                ).aggregate(total=Sum('actual_amount'))['total'] or Decimal('0')
                
                calculated_balance = completed_deposits - completed_withdraws - completed_bets + completed_wins
                actual_balance = balance.get_total_balance()
                
                # 检查差异
                if abs(calculated_balance - actual_balance) > Decimal('0.01'):
                    inconsistent_count += 1
                    
                    # 记录不一致情况
                    from apps.core.models import ActivityLog
                    ActivityLog.objects.create(
                        user=user,
                        action='BALANCE_INCONSISTENCY',
                        details={
                            'calculated_balance': float(calculated_balance),
                            'actual_balance': float(actual_balance),
                            'difference': float(calculated_balance - actual_balance)
                        }
                    )
                    
            except UserBalance.DoesNotExist:
                # 创建缺失的余额记录
                UserBalance.objects.create(user=user)
        
        return f"余额同步完成 - 发现不一致账户: {inconsistent_count}"
        
    except Exception as e:
        return f"余额同步异常: {str(e)}"


@shared_task
def cleanup_old_transactions():
    """
    清理旧交易记录
    """
    try:
        # 清理6个月前的失败交易记录
        cutoff_date = timezone.now() - timedelta(days=180)
        
        deleted_count = Transaction.objects.filter(
            status='FAILED',
            created_at__lt=cutoff_date
        ).delete()[0]
        
        return f"已清理 {deleted_count} 条旧交易记录"
        
    except Exception as e:
        return f"清理旧交易记录异常: {str(e)}"


@shared_task
def send_low_balance_alert(user_id, current_balance):
    """
    发送余额不足提醒
    """
    try:
        user = User.objects.get(id=user_id)
        
        # 创建系统通知
        Notification.objects.create(
            user=user,
            title='余额不足提醒',
            message=f'您的账户余额仅剩 ₦{current_balance:,.2f}，建议及时充值。',
            type='WARNING'
        )
        
        return f"余额不足提醒已发送给用户 {user.phone}"
        
    except User.DoesNotExist:
        return f"用户 {user_id} 不存在"
    except Exception as e:
        return f"发送余额不足提醒失败: {str(e)}"