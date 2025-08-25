"""
用户服务层
"""

import requests
import base64
from typing import Dict, Any, Optional
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import User, KYCDocument


class KYCService:
    """
    KYC身份验证服务
    """
    
    @staticmethod
    def process_document_ocr(document: KYCDocument) -> Dict[str, Any]:
        """
        处理文档OCR识别
        这里可以集成第三方OCR服务，如Google Vision API、AWS Textract等
        """
        try:
            # 模拟OCR处理结果
            ocr_result = {
                'document_type': document.document_type,
                'document_number': document.document_number,
                'extracted_text': {
                    'name': 'John Doe',
                    'number': document.document_number,
                    'issue_date': '2020-01-01',
                    'expiry_date': '2030-01-01',
                },
                'confidence_scores': {
                    'overall': 0.95,
                    'name': 0.98,
                    'number': 0.97,
                    'dates': 0.92,
                }
            }
            
            # 更新文档OCR数据
            document.ocr_data = ocr_result
            document.confidence_score = ocr_result['confidence_scores']['overall']
            document.save()
            
            return ocr_result
            
        except Exception as e:
            return {
                'error': str(e),
                'confidence_scores': {'overall': 0.0}
            }
    
    @staticmethod
    def validate_document_authenticity(document: KYCDocument) -> Dict[str, Any]:
        """
        验证文档真实性
        可以集成政府API或第三方验证服务
        """
        try:
            # 模拟文档验证
            validation_result = {
                'is_valid': True,
                'verification_status': 'VERIFIED',
                'checks': {
                    'format_check': True,
                    'security_features': True,
                    'database_match': True,
                },
                'risk_score': 0.1,  # 0-1，越低越安全
            }
            
            return validation_result
            
        except Exception as e:
            return {
                'is_valid': False,
                'verification_status': 'ERROR',
                'error': str(e),
                'risk_score': 1.0,
            }
    
    @staticmethod
    def perform_face_verification(document: KYCDocument) -> Dict[str, Any]:
        """
        人脸识别验证
        比较身份证件照片与自拍照
        """
        try:
            # 模拟人脸识别结果
            face_match_result = {
                'match_score': 0.92,  # 0-1，相似度分数
                'is_match': True,
                'confidence': 0.95,
                'quality_checks': {
                    'face_detected': True,
                    'image_quality': 'HIGH',
                    'lighting': 'GOOD',
                    'angle': 'FRONTAL',
                }
            }
            
            return face_match_result
            
        except Exception as e:
            return {
                'match_score': 0.0,
                'is_match': False,
                'error': str(e),
                'confidence': 0.0,
            }
    
    @staticmethod
    def auto_review_kyc(document: KYCDocument) -> bool:
        """
        自动审核KYC文档
        基于OCR、文档验证和人脸识别结果
        """
        try:
            # 执行OCR识别
            ocr_result = KYCService.process_document_ocr(document)
            
            # 验证文档真实性
            validation_result = KYCService.validate_document_authenticity(document)
            
            # 人脸识别验证
            face_result = KYCService.perform_face_verification(document)
            
            # 综合评分
            total_score = 0
            max_score = 0
            
            # OCR置信度 (权重: 30%)
            if 'confidence_scores' in ocr_result:
                total_score += ocr_result['confidence_scores']['overall'] * 0.3
            max_score += 0.3
            
            # 文档验证 (权重: 40%)
            if validation_result.get('is_valid'):
                total_score += (1 - validation_result.get('risk_score', 1)) * 0.4
            max_score += 0.4
            
            # 人脸识别 (权重: 30%)
            if face_result.get('is_match'):
                total_score += face_result.get('match_score', 0) * 0.3
            max_score += 0.3
            
            # 计算最终分数
            final_score = total_score / max_score if max_score > 0 else 0
            
            # 自动通过阈值: 0.85
            auto_approve_threshold = 0.85
            
            if final_score >= auto_approve_threshold:
                document.status = 'APPROVED'
                document.reviewed_at = timezone.now()
                document.save()
                
                # 更新用户KYC状态
                document.user.kyc_status = 'APPROVED'
                document.user.kyc_approved_at = timezone.now()
                document.user.save()
                
                return True
            
            # 自动拒绝阈值: 0.3
            auto_reject_threshold = 0.3
            
            if final_score < auto_reject_threshold:
                document.status = 'REJECTED'
                document.reviewed_at = timezone.now()
                document.rejection_reason = f'自动审核未通过 (评分: {final_score:.2f})'
                document.save()
                
                # 更新用户KYC状态
                document.user.kyc_status = 'REJECTED'
                document.user.save()
                
                return True
            
            # 中间分数需要人工审核
            return False
            
        except Exception as e:
            # 出错时标记为需要人工审核
            return False
    
    @staticmethod
    def manual_review_kyc(document: KYCDocument, reviewer: User, 
                         action: str, reason: str = '') -> bool:
        """
        人工审核KYC文档
        """
        try:
            if action == 'APPROVE':
                document.status = 'APPROVED'
                document.user.kyc_status = 'APPROVED'
                document.user.kyc_approved_at = timezone.now()
                document.user.save()
                
            elif action == 'REJECT':
                document.status = 'REJECTED'
                document.rejection_reason = reason
                document.user.kyc_status = 'REJECTED'
                document.user.save()
            
            document.reviewed_by = reviewer
            document.reviewed_at = timezone.now()
            document.save()
            
            # 记录审核日志
            from apps.core.models import ActivityLog
            ActivityLog.objects.create(
                user=document.user,
                action=f'KYC_{action}',
                details={
                    'document_id': str(document.id),
                    'document_type': document.document_type,
                    'reviewer_id': str(reviewer.id),
                    'reason': reason,
                }
            )
            
            return True
            
        except Exception as e:
            return False


class SMSService:
    """
    短信服务
    """
    
    @staticmethod
    def send_verification_code(phone: str, code: str) -> bool:
        """
        发送验证码短信
        """
        try:
            # 这里集成实际的短信服务提供商
            # 如Twilio、AWS SNS、阿里云短信等
            
            message = f"您的验证码是: {code}，5分钟内有效。请勿泄露给他人。【彩票平台】"
            
            # 模拟发送成功
            print(f"发送短信到 {phone}: {message}")
            
            return True
            
        except Exception as e:
            print(f"短信发送失败: {e}")
            return False
    
    @staticmethod
    def send_kyc_notification(user: User, status: str) -> bool:
        """
        发送KYC状态通知短信
        """
        try:
            if status == 'APPROVED':
                message = "恭喜！您的身份验证已通过，现在可以正常使用所有功能。【彩票平台】"
            elif status == 'REJECTED':
                message = "很抱歉，您的身份验证未通过，请重新提交正确的身份证件。【彩票平台】"
            else:
                message = "您的身份验证正在审核中，请耐心等待。【彩票平台】"
            
            return SMSService.send_sms(user.phone, message)
            
        except Exception as e:
            return False
    
    @staticmethod
    def send_sms(phone: str, message: str) -> bool:
        """
        发送短信的通用方法
        """
        try:
            # 实际短信发送逻辑
            print(f"发送短信到 {phone}: {message}")
            return True
        except Exception as e:
            print(f"短信发送失败: {e}")
            return False


class TwoFactorService:
    """
    双因子认证服务
    """
    
    @staticmethod
    def generate_verification_code() -> str:
        """
        生成6位数字验证码
        """
        import random
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    @staticmethod
    def send_2fa_code(user: User) -> bool:
        """
        发送双因子认证验证码
        """
        try:
            from django.core.cache import cache
            
            # 生成验证码
            code = TwoFactorService.generate_verification_code()
            
            # 缓存验证码，5分钟有效
            cache_key = f'2fa_code_{user.id}'
            cache.set(cache_key, code, 300)
            
            # 发送短信
            return SMSService.send_verification_code(user.phone, code)
            
        except Exception as e:
            return False
    
    @staticmethod
    def verify_2fa_code(user: User, code: str) -> bool:
        """
        验证双因子认证码
        """
        try:
            from django.core.cache import cache
            
            cache_key = f'2fa_code_{user.id}'
            cached_code = cache.get(cache_key)
            
            if cached_code and cached_code == code:
                # 验证成功，删除缓存
                cache.delete(cache_key)
                return True
            
            return False
            
        except Exception as e:
            return False