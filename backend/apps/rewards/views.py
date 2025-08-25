"""
奖励系统视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from django.utils import timezone

from .models import ReferralRewardRecord, RebateRecord, VIPLevel
from .serializers import (
    ReferralRewardRecordSerializer, 
    RebateRecordSerializer, 
    VIPLevelSerializer
)


class ReferralViewSet(viewsets.ReadOnlyModelViewSet):
    """推荐奖励视图集"""
    serializer_class = ReferralRewardRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ReferralRewardRecord.objects.filter(referrer=self.request.user)


class RebateViewSet(viewsets.ReadOnlyModelViewSet):
    """返水视图集"""
    serializer_class = RebateRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RebateRecord.objects.filter(user=self.request.user)


class VipViewSet(viewsets.ReadOnlyModelViewSet):
    """VIP视图集"""
    serializer_class = VIPLevelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return VIPLevel.objects.all()


class ReferralStatsView(APIView):
    """推荐统计视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # 统计推荐数据
        total_referrals = user.referrals.count()
        total_rewards = ReferralRewardRecord.objects.filter(
            referrer=user
        ).aggregate(
            total=Sum('reward_amount')
        )['total'] or 0
        
        return Response({
            'total_referrals': total_referrals,
            'total_rewards': total_rewards,
            'active_referrals': user.referrals.filter(is_active=True).count()
        })


class ReferralHistoryView(APIView):
    """推荐历史视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        rewards = ReferralRewardRecord.objects.filter(
            referrer=request.user
        ).order_by('-created_at')[:20]
        
        serializer = ReferralRewardRecordSerializer(rewards, many=True)
        return Response(serializer.data)


class RebateCalculateView(APIView):
    """返水计算视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 这里应该实现返水计算逻辑
        return Response({
            'available_rebate': 0,
            'next_rebate_time': None
        })


class RebateClaimView(APIView):
    """返水领取视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # 这里应该实现返水领取逻辑
        return Response({
            'success': False,
            'message': '暂无可领取的返水'
        })


class VipBenefitsView(APIView):
    """VIP福利视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        current_vip = getattr(user, 'vip_level', None)
        
        if current_vip:
            # 返回VIP等级信息
            serializer = VIPLevelSerializer(current_vip)
            return Response(serializer.data)
        
        return Response([])


class VipUpgradeView(APIView):
    """VIP升级视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # 这里应该实现VIP升级逻辑
        return Response({
            'success': False,
            'message': 'VIP升级功能暂未开放'
        })