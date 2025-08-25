"""
奖励系统序列化器
"""

from rest_framework import serializers
from .models import ReferralRewardRecord, RebateRecord, VIPLevel


class ReferralRewardRecordSerializer(serializers.ModelSerializer):
    """推荐奖励记录序列化器"""
    
    class Meta:
        model = ReferralRewardRecord
        fields = [
            'id', 'referrer', 'referee', 'period_date',
            'referral_level', 'reward_rate', 'referee_turnover',
            'reward_amount', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RebateRecordSerializer(serializers.ModelSerializer):
    """返水记录序列化器"""
    
    class Meta:
        model = RebateRecord
        fields = [
            'id', 'user', 'period_date', 'vip_level',
            'rebate_rate', 'total_turnover', 'rebate_amount',
            'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class VIPLevelSerializer(serializers.ModelSerializer):
    """VIP等级序列化器"""
    
    class Meta:
        model = VIPLevel
        fields = [
            'id', 'level', 'name', 'required_turnover',
            'rebate_rate', 'daily_withdraw_limit', 'daily_withdraw_times',
            'withdraw_fee_rate', 'monthly_bonus', 'birthday_bonus'
        ]
        read_only_fields = ['id']