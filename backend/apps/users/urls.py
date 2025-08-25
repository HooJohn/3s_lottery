"""
用户认证URL配置
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    UserDetailView,
    KYCDocumentView,
    PasswordChangeView,
    ReferralTreeView,
    VIPStatusView,
)
from .kyc_views import (
    KYCSubmissionView,
    KYCStatusView,
    TwoFactorAuthView,
    TwoFactorVerifyView,
    TwoFactorDisableView,
    kyc_requirements,
)

app_name = 'users'

urlpatterns = [
    # 认证相关
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 用户资料
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('detail/', UserDetailView.as_view(), name='detail'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    
    # KYC身份验证
    path('kyc/', KYCDocumentView.as_view(), name='kyc'),
    path('kyc/submit/', KYCSubmissionView.as_view(), name='kyc_submit'),
    path('kyc/status/', KYCStatusView.as_view(), name='kyc_status'),
    path('kyc/requirements/', kyc_requirements, name='kyc_requirements'),
    
    # 双因子认证
    path('2fa/send/', TwoFactorAuthView.as_view(), name='2fa_send'),
    path('2fa/verify/', TwoFactorVerifyView.as_view(), name='2fa_verify'),
    path('2fa/disable/', TwoFactorDisableView.as_view(), name='2fa_disable'),
    
    # 推荐系统
    path('referral/tree/', ReferralTreeView.as_view(), name='referral_tree'),
    
    # VIP系统
    path('vip/status/', VIPStatusView.as_view(), name='vip_status'),
]