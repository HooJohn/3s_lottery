"""
用户认证视图
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import User, KYCDocument, LoginLog
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserDetailSerializer,
    KYCDocumentSerializer,
    PasswordChangeSerializer,
    ReferralTreeSerializer
)
from apps.core.utils import get_client_ip, get_user_agent


class UserRegistrationView(APIView):
    """
    用户注册
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="用户注册",
        description="支持手机号注册，自动生成推荐码",
        request=UserRegistrationSerializer,
        responses={201: UserProfileSerializer}
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                user = serializer.save()
                
                # 记录注册日志
                LoginLog.objects.create(
                    user=user,
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request),
                    success=True
                )
                
                # 生成JWT Token
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'success': True,
                    'message': '注册成功',
                    'data': {
                        'user': UserProfileSerializer(user).data,
                        'tokens': {
                            'access': str(refresh.access_token),
                            'refresh': str(refresh)
                        }
                    }
                }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': '注册失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    用户登录
    支持用户名/邮箱/手机号任一方式登录
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="用户登录",
        description="支持用户名/邮箱/手机号任一方式登录，返回JWT Token",
        request=UserLoginSerializer,
        responses={200: UserProfileSerializer}
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # 检查账户锁定状态
            if user.locked_until and user.locked_until > timezone.now():
                return Response({
                    'success': False,
                    'message': f'账户已锁定，请于{user.locked_until}后重试'
                }, status=status.HTTP_423_LOCKED)
            
            # 重置登录尝试次数
            user.login_attempts = 0
            user.locked_until = None
            user.last_login_ip = get_client_ip(request)
            user.save()
            
            # 记录登录日志
            LoginLog.objects.create(
                user=user,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                success=True
            )
            
            # 生成JWT Token
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': '登录成功',
                'data': {
                    'user': UserProfileSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                }
            }, status=status.HTTP_200_OK)
        
        # 登录失败，记录失败日志
        login_field = request.data.get('login')
        if login_field:
            # 尝试找到用户并增加失败次数
            user = None
            try:
                user = User.objects.get(username=login_field)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=login_field)
                except User.DoesNotExist:
                    try:
                        user = User.objects.get(phone=login_field)
                    except User.DoesNotExist:
                        pass
            
            if user:
                user.login_attempts += 1
                if user.login_attempts >= 5:
                    user.locked_until = timezone.now() + timezone.timedelta(minutes=30)
                user.save()
                
                # 记录失败日志
                LoginLog.objects.create(
                    user=user,
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request),
                    success=False,
                    failure_reason='Invalid credentials'
                )
        
        return Response({
            'success': False,
            'message': '用户名或密码错误',
            'errors': serializer.errors
        }, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    """
    用户登出
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="用户登出",
        description="登出当前用户，使Token失效"
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'success': True,
                'message': '登出成功'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': '登出失败'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    用户资料查看和更新
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        summary="获取用户资料",
        description="获取当前用户的详细资料信息"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="更新用户资料",
        description="更新当前用户的资料信息"
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class UserDetailView(generics.RetrieveAPIView):
    """
    用户详细信息
    """
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        summary="获取用户详细信息",
        description="获取当前用户的完整信息，包括资料和统计数据"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class KYCDocumentView(generics.CreateAPIView, generics.ListAPIView):
    """
    KYC身份验证文档
    """
    serializer_class = KYCDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return KYCDocument.objects.filter(user=self.request.user).order_by('-created_at')
    
    @extend_schema(
        summary="提交KYC文档",
        description="上传身份验证文档进行KYC审核"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    @extend_schema(
        summary="获取KYC文档列表",
        description="获取当前用户的KYC文档提交记录"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PasswordChangeView(APIView):
    """
    密码修改
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="修改密码",
        description="修改当前用户的登录密码",
        request=PasswordChangeSerializer
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': '密码修改成功'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': '密码修改失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ReferralTreeView(APIView):
    """
    推荐关系树
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="获取推荐关系树",
        description="获取当前用户的7级推荐关系树",
        parameters=[
            OpenApiParameter(
                name='max_depth',
                type=int,
                location=OpenApiParameter.QUERY,
                description='最大层级深度 (1-7)',
                default=7
            )
        ],
        responses={200: ReferralTreeSerializer(many=True)}
    )
    def get(self, request):
        max_depth = min(int(request.query_params.get('max_depth', 7)), 7)
        tree = request.user.get_referral_tree(max_depth)
        
        return Response({
            'success': True,
            'data': {
                'referral_code': request.user.referral_code,
                'tree': tree,
                'summary': {
                    'total_referrals': len(tree),
                    'levels': max_depth,
                    'total_turnover': sum(item['total_turnover'] for item in tree)
                }
            }
        }, status=status.HTTP_200_OK)


class VIPStatusView(APIView):
    """
    VIP状态查询
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="获取VIP状态",
        description="获取当前用户的VIP等级信息和升级进度"
    )
    def get(self, request):
        user = request.user
        vip_info = user.get_vip_info()
        
        # 获取下一级VIP信息
        next_vip = None
        if user.vip_level < 7:
            from apps.rewards.models import VIPLevel
            try:
                next_level = VIPLevel.objects.get(level=user.vip_level + 1)
                next_vip = {
                    'level': next_level.level,
                    'name': next_level.name,
                    'required_turnover': float(next_level.required_turnover),
                    'remaining_turnover': max(0, float(next_level.required_turnover) - float(user.total_turnover))
                }
            except VIPLevel.DoesNotExist:
                pass
        
        return Response({
            'success': True,
            'data': {
                'current_vip': vip_info,
                'next_vip': next_vip,
                'can_upgrade': user.update_vip_level()
            }
        }, status=status.HTTP_200_OK)