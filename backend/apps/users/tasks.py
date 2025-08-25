"""
用户模块异步任务
"""

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import User, KYCDocument
from .services import KYCService, SMSService
from apps.core.models import ActivityLog, Notification


@shared_task
def process_kyc_document(document_id):
    """
    异步处理KYC文档
    """
    try:
        document = KYCDocument.objects.get(id=document_id)
        
        # 记录处理开始
        ActivityLog.objects.create(
            user=document.user,
            action='KYC_PROCESS_START',
            details={'document_id': str(document.id)}
        )
        
        # 执行自动审核
        auto_approved = KYCService.auto_review_kyc(document)
        
        if auto_approved:
            # 发送通知
            if document.status == 'APPROVED':
                send_kyc_approval_notification.delay(document.user.id)
            elif document.status == 'REJECTED':
                send_kyc_rejection_notification.delay(document.user.id, document.rejection_reason)
        else:
            # 需要人工审核
            send_kyc_manual_review_notification.delay(document.id)
        
        return f"KYC文档 {document_id} 处理完成"
        
    except KYCDocument.DoesNotExist:
        return f"KYC文档 {document_id} 不存在"
    except Exception as e:
        return f"处理KYC文档 {document_id} 时出错: {str(e)}"


@shared_task
def send_kyc_approval_notification(user_id):
    """
    发送KYC通过通知
    """
    try:
        user = User.objects.get(id=user_id)
        
        # 发送短信通知
        SMSService.send_kyc_notification(user, 'APPROVED')
        
        # 创建系统通知
        Notification.objects.create(
            user=user,
            title='身份验证通过',
            message='恭喜！您的身份验证已通过，现在可以正常使用所有功能。',
            type='SUCCESS'
        )
        
        # 发送邮件通知
        if user.email:
            send_mail(
                subject='身份验证通过通知',
                message=f'尊敬的 {user.full_name}，您的身份验证已通过审核。',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )
        
        # 记录活动日志
        ActivityLog.objects.create(
            user=user,
            action='KYC_APPROVE',
            details={'notification_sent': True}
        )
        
        return f"KYC通过通知已发送给用户 {user.phone}"
        
    except User.DoesNotExist:
        return f"用户 {user_id} 不存在"
    except Exception as e:
        return f"发送KYC通过通知时出错: {str(e)}"


@shared_task
def send_kyc_rejection_notification(user_id, reason):
    """
    发送KYC拒绝通知
    """
    try:
        user = User.objects.get(id=user_id)
        
        # 发送短信通知
        SMSService.send_kyc_notification(user, 'REJECTED')
        
        # 创建系统通知
        Notification.objects.create(
            user=user,
            title='身份验证未通过',
            message=f'很抱歉，您的身份验证未通过。原因：{reason}。请重新提交正确的身份证件。',
            type='ERROR'
        )
        
        # 发送邮件通知
        if user.email:
            send_mail(
                subject='身份验证未通过通知',
                message=f'尊敬的 {user.full_name}，您的身份验证未通过审核。原因：{reason}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )
        
        # 记录活动日志
        ActivityLog.objects.create(
            user=user,
            action='KYC_REJECT',
            details={'reason': reason, 'notification_sent': True}
        )
        
        return f"KYC拒绝通知已发送给用户 {user.phone}"
        
    except User.DoesNotExist:
        return f"用户 {user_id} 不存在"
    except Exception as e:
        return f"发送KYC拒绝通知时出错: {str(e)}"


@shared_task
def send_kyc_manual_review_notification(document_id):
    """
    发送KYC需要人工审核通知（给管理员）
    """
    try:
        document = KYCDocument.objects.get(id=document_id)
        
        # 发送邮件给管理员
        admin_emails = User.objects.filter(is_staff=True, is_active=True).values_list('email', flat=True)
        
        if admin_emails:
            send_mail(
                subject='KYC文档需要人工审核',
                message=f'用户 {document.user.phone} 提交的KYC文档需要人工审核。\n'
                       f'文档类型: {document.get_document_type_display()}\n'
                       f'提交时间: {document.created_at}\n'
                       f'请登录管理后台进行审核。',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=list(admin_emails),
                fail_silently=True
            )
        
        return f"KYC人工审核通知已发送，文档ID: {document_id}"
        
    except KYCDocument.DoesNotExist:
        return f"KYC文档 {document_id} 不存在"
    except Exception as e:
        return f"发送KYC人工审核通知时出错: {str(e)}"


@shared_task
def cleanup_expired_kyc_documents():
    """
    清理过期的KYC文档
    """
    try:
        from datetime import timedelta
        
        # 清理30天前被拒绝的文档
        expired_date = timezone.now() - timedelta(days=30)
        expired_docs = KYCDocument.objects.filter(
            status='REJECTED',
            reviewed_at__lt=expired_date
        )
        
        count = expired_docs.count()
        expired_docs.delete()
        
        return f"已清理 {count} 个过期的KYC文档"
        
    except Exception as e:
        return f"清理过期KYC文档时出错: {str(e)}"


@shared_task
def send_welcome_message(user_id):
    """
    发送欢迎消息给新用户
    """
    try:
        user = User.objects.get(id=user_id)
        
        # 创建欢迎通知
        Notification.objects.create(
            user=user,
            title='欢迎加入彩票平台',
            message=f'欢迎 {user.full_name}！为了保障您的账户安全，请尽快完成身份验证。',
            type='INFO'
        )
        
        # 发送欢迎短信
        welcome_message = f"欢迎加入彩票平台！您的推荐码是 {user.referral_code}，分享给朋友可获得奖励。【彩票平台】"
        SMSService.send_sms(user.phone, welcome_message)
        
        # 记录活动日志
        ActivityLog.objects.create(
            user=user,
            action='REGISTER',
            details={'welcome_sent': True}
        )
        
        return f"欢迎消息已发送给用户 {user.phone}"
        
    except User.DoesNotExist:
        return f"用户 {user_id} 不存在"
    except Exception as e:
        return f"发送欢迎消息时出错: {str(e)}"


@shared_task
def update_user_vip_levels():
    """
    批量更新用户VIP等级
    """
    try:
        updated_count = 0
        
        # 获取所有活跃用户
        users = User.objects.filter(is_active=True).iterator(chunk_size=1000)
        
        for user in users:
            if user.update_vip_level():
                updated_count += 1
        
        return f"已更新 {updated_count} 个用户的VIP等级"
        
    except Exception as e:
        return f"更新用户VIP等级时出错: {str(e)}"


@shared_task
def send_2fa_code(user_id):
    """
    发送双因子认证验证码
    """
    try:
        user = User.objects.get(id=user_id)
        
        from .services import TwoFactorService
        success = TwoFactorService.send_2fa_code(user)
        
        if success:
            return f"双因子认证验证码已发送给用户 {user.phone}"
        else:
            return f"发送双因子认证验证码失败，用户 {user.phone}"
        
    except User.DoesNotExist:
        return f"用户 {user_id} 不存在"
    except Exception as e:
        return f"发送双因子认证验证码时出错: {str(e)}"