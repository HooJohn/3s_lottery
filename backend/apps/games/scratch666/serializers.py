"""
666刮刮乐游戏序列化器
"""

from rest_framework import serializers
from .models import (
    Scratch666Game, ScratchCard, ScratchCardTemplate, 
    ScratchStatistics, UserScratchPreference
)


class Scratch666GameSerializer(serializers.ModelSerializer):
    """
    666刮刮乐游戏配置序列化器
    """
    game_name = serializers.CharField(source='game.name', read_only=True)
    game_status = serializers.CharField(source='game.status', read_only=True)
    expected_payout_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Scratch666Game
        fields = [
            'id', 'game_name', 'game_status', 'card_price', 'base_amount',
            'profit_target', 'scratch_areas', 'win_probability_6',
            'win_probability_66', 'win_probability_666', 'multiplier_6',
            'multiplier_66', 'multiplier_666', 'enable_auto_scratch',
            'max_auto_scratch', 'enable_sound', 'enable_music',
            'expected_payout_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_expected_payout_rate(self, obj):
        """
        计算期望派彩率
        """
        return obj.calculate_expected_payout_rate()


class ScratchCardSerializer(serializers.ModelSerializer):
    """
    刮刮乐卡片序列化器
    """
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    game_name = serializers.CharField(source='game.name', read_only=True)
    
    class Meta:
        model = ScratchCard
        fields = [
            'id', 'user_phone', 'game_name', 'card_type', 'price',
            'areas', 'status', 'is_winner', 'total_winnings',
            'win_details', 'purchase_transaction_id', 'win_transaction_id',
            'purchased_at', 'scratched_at'
        ]
        read_only_fields = [
            'id', 'user_phone', 'game_name', 'areas', 'status',
            'is_winner', 'total_winnings', 'win_details',
            'purchase_transaction_id', 'win_transaction_id',
            'purchased_at', 'scratched_at'
        ]


class ScratchCardDetailSerializer(ScratchCardSerializer):
    """
    刮刮乐卡片详细信息序列化器
    """
    areas_display = serializers.SerializerMethodField()
    win_summary = serializers.SerializerMethodField()
    
    class Meta(ScratchCardSerializer.Meta):
        fields = ScratchCardSerializer.Meta.fields + [
            'areas_display', 'win_summary'
        ]
    
    def get_areas_display(self, obj):
        """
        格式化显示刮奖区域
        """
        if not obj.areas:
            return []
        
        display_areas = []
        for area in obj.areas:
            display_areas.append({
                'index': area['index'],
                'content': area['content'],
                'scratched': area['scratched'],
                'win_amount': area.get('win_amount', 0),
                'is_winning': area['content'] in ['6', '66', '666']
            })
        
        return display_areas
    
    def get_win_summary(self, obj):
        """
        获取中奖汇总信息
        """
        if not obj.is_winner or not obj.win_details:
            return None
        
        return {
            'total_amount': obj.total_winnings,
            'win_areas': obj.win_details.get('areas', []),
            'win_count': len(obj.win_details.get('areas', []))
        }


class ScratchCardTemplateSerializer(serializers.ModelSerializer):
    """
    刮刮乐卡片模板序列化器
    """
    game_name = serializers.CharField(source='game.name', read_only=True)
    
    class Meta:
        model = ScratchCardTemplate
        fields = [
            'id', 'name', 'game_name', 'card_type', 'template_data',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ScratchStatisticsSerializer(serializers.ModelSerializer):
    """
    刮刮乐统计序列化器
    """
    game_name = serializers.CharField(source='game.name', read_only=True)
    payout_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = ScratchStatistics
        fields = [
            'id', 'game_name', 'date', 'total_cards_sold', 'total_sales_amount',
            'total_winners', 'total_winnings', 'winners_6', 'winnings_6',
            'winners_66', 'winnings_66', 'winners_666', 'winnings_666',
            'profit', 'profit_rate', 'payout_rate', 'unique_players',
            'avg_cards_per_player', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_payout_rate(self, obj):
        """
        计算派彩率
        """
        return obj.calculate_payout_rate()


class UserScratchPreferenceSerializer(serializers.ModelSerializer):
    """
    用户刮刮乐偏好序列化器
    """
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    win_rate = serializers.SerializerMethodField()
    roi = serializers.SerializerMethodField()
    
    class Meta:
        model = UserScratchPreference
        fields = [
            'id', 'user_phone', 'sound_enabled', 'music_enabled',
            'auto_scratch_enabled', 'auto_scratch_count', 'auto_scratch_stop_on_win',
            'total_cards_purchased', 'total_amount_spent', 'total_winnings',
            'biggest_win', 'win_rate', 'roi', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_phone', 'total_cards_purchased', 'total_amount_spent',
            'total_winnings', 'biggest_win', 'win_rate', 'roi',
            'created_at', 'updated_at'
        ]
    
    def get_win_rate(self, obj):
        """
        获取中奖率
        """
        return obj.get_win_rate()
    
    def get_roi(self, obj):
        """
        获取投资回报率
        """
        return obj.get_roi()


class ScratchAreaSerializer(serializers.Serializer):
    """
    刮奖区域序列化器
    """
    card_id = serializers.UUIDField()
    area_index = serializers.IntegerField(min_value=0)


class AutoScratchSerializer(serializers.Serializer):
    """
    自动连刮序列化器
    """
    count = serializers.IntegerField(min_value=1, max_value=100, default=10)
    stop_on_win = serializers.BooleanField(default=True)


class UserStatisticsSerializer(serializers.Serializer):
    """
    用户统计信息序列化器
    """
    total_cards = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_winnings = serializers.DecimalField(max_digits=15, decimal_places=2)
    biggest_win = serializers.DecimalField(max_digits=15, decimal_places=2)
    win_rate = serializers.FloatField()
    roi = serializers.FloatField()
    recent_cards = ScratchCardSerializer(many=True)


class GameStatisticsSerializer(serializers.Serializer):
    """
    游戏统计信息序列化器
    """
    period_days = serializers.IntegerField()
    total_cards_sold = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_winnings = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_profit = serializers.DecimalField(max_digits=15, decimal_places=2)
    profit_rate = serializers.FloatField()
    payout_rate = serializers.FloatField()
    unique_players = serializers.IntegerField()
    avg_cards_per_player = serializers.FloatField()
    daily_stats = ScratchStatisticsSerializer(many=True)