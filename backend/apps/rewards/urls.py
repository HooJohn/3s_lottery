"""
奖励系统URL配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'referrals', views.ReferralViewSet, basename='referral')
router.register(r'rebates', views.RebateViewSet, basename='rebate')
router.register(r'vip', views.VipViewSet, basename='vip')

app_name = 'rewards'

urlpatterns = [
    path('', include(router.urls)),
    
    # 推荐奖励相关
    path('referral/stats/', views.ReferralStatsView.as_view(), name='referral-stats'),
    path('referral/history/', views.ReferralHistoryView.as_view(), name='referral-history'),
    
    # 返水相关
    path('rebate/calculate/', views.RebateCalculateView.as_view(), name='rebate-calculate'),
    path('rebate/claim/', views.RebateClaimView.as_view(), name='rebate-claim'),
    
    # VIP相关
    path('vip/benefits/', views.VipBenefitsView.as_view(), name='vip-benefits'),
    path('vip/upgrade/', views.VipUpgradeView.as_view(), name='vip-upgrade'),
]