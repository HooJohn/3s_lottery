"""
KYC相关视图
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from .models import KYCDocument
from .serializers import KYCDocumentSerializer
from .services import TwoFactorService
from .tasks import process_kyc_document, send_2fa_code


class KYCSubmissionView(APIView):
    """
    KYC文档提交
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="提交KYC文档",
        description="上传身份证件和自拍照进行KYC验证",
        request=KYCDocumentSerializer
    )
    def post(self, request):
        serializer = KYCDocumentSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            document = serializer.save()
            
            # 更新用户KYC状态为提交中
            request.user.kyc_status = 'PENDING'
            request.user.kyc_submitted_at = timezone.now()
            request.user.save()
            
            # 异步处理KYC文档
            process_kyc_document.delay(str(document.id))
            
            return Response({
                'success': True,
                'message': 'KYC文档提交成功，正在审核中',
                'data': {
                    'document_id': str(document.id),
                    'status': document.status,
                    'estimated_review_time': '1-3个工作日'
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'KYC文档提交失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class KYCStatusView(APIView):
    """
    KYC状态查询
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="查询KYC状态",
        description="获取当前用户的KYC验证状态和历史记录"
    )
    def get(self, request):
        user = request.user
        
        # 获取最新的KYC文档
        latest_document = KYCDocument.objects.filter(user=user).order_by('-created_at').first()
        
        # 获取所有KYC文档历史
        documents = KYCDocument.objects.filter(user=user).order_by('-created_at')
        
        response_data = {
            'kyc_status': user.kyc_status,
            'kyc_submitted_at': user.kyc_submitted_at,
            'kyc_approved_at': user.kyc_approved_at,
            'latest_document': None,
            'documents_history': KYCDocumentSerializer(documents, many=True).data,
            'can_submit': user.kyc_status in ['PENDING', 'REJECTED'] and not documents.filter(status='PENDING').exists(),
            'required_documents': [
                {
                    'type': 'NIN',
                    'name': '国民身份证号码',
                    'required': True,
                    'description': '尼日利亚国民身份证正反面照片'
                },
                {
                    'type': 'SELFIE',
                    'name': '手持身份证自拍',
                    'required': True,
                    'description': '手持身份证的清晰自拍照'
                }
            ]
        }
        
        if latest_document:
            response_data['latest_document'] = KYCDocumentSerializer(latest_document).data
        
        return Response({
            'success': True,
            'data': response_data
        }, status=status.HTTP_200_OK)


class TwoFactorAuthView(APIView):
    """
    双因子认证
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="发送双因子认证验证码",
        description="向用户手机发送双因子认证验证码"
    )
    def post(self, request):
        user = request.user
        
        # 异步发送验证码
        send_2fa_code.delay(str(user.id))
        
        return Response({
            'success': True,
            'message': f'验证码已发送到 {user.phone[-4:]}',
            'data': {
                'phone_masked': f'{user.phone[:4]}****{user.phone[-4:]}',
                'expires_in': 300  # 5分钟
            }
        }, status=status.HTTP_200_OK)


class TwoFactorVerifyView(APIView):
    """
    双因子认证验证
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="验证双因子认证码",
        description="验证用户输入的双因子认证验证码"
    )
    def post(self, request):
        code = request.data.get('code')
        
        if not code:
            return Response({
                'success': False,
                'message': '请输入验证码'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证验证码
        is_valid = TwoFactorService.verify_2fa_code(request.user, code)
        
        if is_valid:
            # 启用双因子认证
            request.user.two_factor_enabled = True
            request.user.save()
            
            return Response({
                'success': True,
                'message': '双因子认证验证成功',
                'data': {
                    'two_factor_enabled': True
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': '验证码错误或已过期'
            }, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorDisableView(APIView):
    """
    禁用双因子认证
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="禁用双因子认证",
        description="禁用当前用户的双因子认证功能"
    )
    def post(self, request):
        password = request.data.get('password')
        
        if not password:
            return Response({
                'success': False,
                'message': '请输入密码确认'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证密码
        if not request.user.check_password(password):
            return Response({
                'success': False,
                'message': '密码错误'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 禁用双因子认证
        request.user.two_factor_enabled = False
        request.user.save()
        
        return Response({
            'success': True,
            'message': '双因子认证已禁用',
            'data': {
                'two_factor_enabled': False
            }
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def kyc_requirements(request):
    """
    获取KYC要求和指南
    """
    requirements = {
        'supported_documents': [
            {
                'type': 'NIN',
                'name': 'National ID Number',
                'description': '尼日利亚国民身份证',
                'requirements': [
                    '身份证正面照片清晰可见',
                    '身份证反面照片清晰可见',
                    '照片中文字和数字清晰可读',
                    '身份证在有效期内'
                ]
            },
            {
                'type': 'PASSPORT',
                'name': 'International Passport',
                'description': '国际护照',
                'requirements': [
                    '护照个人信息页清晰可见',
                    '护照在有效期内',
                    '照片中文字和数字清晰可读'
                ]
            },
            {
                'type': 'DRIVERS_LICENSE',
                'name': 'Driver\'s License',
                'description': '驾驶执照',
                'requirements': [
                    '驾照正面照片清晰可见',
                    '驾照反面照片清晰可见',
                    '驾照在有效期内'
                ]
            }
        ],
        'selfie_requirements': [
            '手持身份证件的清晰自拍照',
            '面部清晰可见，无遮挡',
            '身份证件信息清晰可读',
            '光线充足，无反光',
            '背景简洁，无杂物'
        ],
        'photo_guidelines': {
            'format': ['JPG', 'PNG'],
            'max_size': '5MB',
            'min_resolution': '800x600',
            'quality': '高清晰度，无模糊'
        },
        'review_process': {
            'auto_review': '系统自动初审（通常几分钟内完成）',
            'manual_review': '人工审核（1-3个工作日）',
            'notification': '审核结果将通过短信和站内消息通知'
        }
    }
    
    return Response({
        'success': True,
        'data': requirements
    }, status=status.HTTP_200_OK)