"""
大乐透彩票序列化器
"""

from rest_framework import serializers
from .models import SuperLottoGame, SuperLottoDraw, SuperLottoBet, SuperLottoStatistics


class SuperLottoGameSerializer(serializers.ModelSerializer):
    """
    大乐透游戏配置序列化器
    """
    game_name = serializers.CharField(source='game.name', read_only=True)
    game_status = serializers.CharField(source='game.status', read_only=True)
    draw_days_list = serializers.SerializerMethodField()
    expected_payout_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = SuperLottoGame
        fields = [
            'id', 'game_name', 'game_status', 'base_bet_amount', 'max_multiplier',
            'front_zone_min', 'front_zone_max', 'front_zone_count',
            'back_zone_min', 'back_zone_max', 'back_zone_count',
            'jackpot_allocation_rate', 'second_prize_allocation_rate',
            'third_prize_amount', 'fourth_prize_amount', 'fifth_prize_amount',
            'sixth_prize_amount', 'seventh_prize_amount', 'eighth_prize_amount',
            'ninth_prize_amount', 'profit_target', 'draw_days', 'draw_days_list',
            'draw_time', 'sales_stop_minutes', 'expected_payout_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_draw_days_list(self, obj):
        """获取开奖日期列表"""
        return obj.get_draw_days_list()
    
    def get_expected_payout_rate(self, obj):
        """计算期望派彩率"""
        return obj.calculate_expected_payout_rate()


class SuperLottoDrawSerializer(serializers.ModelSerializer):
    """
    大乐透开奖期次序列化器
    """
    game_name = serializers.CharField(source='game.name', read_only=True)
    winning_numbers_display = serializers.SerializerMethodField()
    total_winners = serializers.SerializerMethodField()
    is_sales_open = serializers.SerializerMethodField()
    
    class Meta:
        model = SuperLottoDraw
        fields = [
            'id', 'game_name', 'draw_number', 'draw_time', 'sales_end_time',
            'front_numbers', 'back_numbers', 'winning_numbers_display',
            'jackpot_amount', 'total_sales', 'first_prize_winners',
            'first_prize_amount', 'second_prize_winners', 'second_prize_amount',
            'third_prize_winners', 'fourth_prize_winners', 'fifth_prize_winners',
            'sixth_prize_winners', 'seventh_prize_winners', 'eighth_prize_winners',
            'ninth_prize_winners', 'total_winners', 'status', 'is_sales_open',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'winning_numbers_display', 'total_winners', 'is_sales_open',
            'created_at', 'updated_at'
        ]
    
    def get_winning_numbers_display(self, obj):
        """获取开奖号码显示格式"""
        return obj.get_winning_numbers_display()
    
    def get_total_winners(self, obj):
        """计算总中奖人数"""
        return obj.calculate_total_winners()
    
    def get_is_sales_open(self, obj):
        """检查是否在销售期内"""
        return obj.is_sales_open()


class SuperLottoBetSerializer(serializers.ModelSerializer):
    """
    大乐透投注记录序列化器
    """
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    draw_number = serializers.CharField(source='draw.draw_number', read_only=True)
    draw_time = serializers.DateTimeField(source='draw.draw_time', read_only=True)
    bet_type_display = serializers.CharField(source='get_bet_type_display', read_only=True)
    numbers_display = serializers.SerializerMethodField()
    
    class Meta:
        model = SuperLottoBet
        fields = [
            'id', 'user_phone', 'draw_number', 'draw_time', 'bet_type',
            'bet_type_display', 'front_numbers', 'back_numbers',
            'front_dan_numbers', 'front_tuo_numbers', 'back_dan_numbers',
            'back_tuo_numbers', 'numbers_display', 'multiplier', 'bet_count',
            'single_amount', 'total_amount', 'is_winner', 'winning_level',
            'winning_amount', 'winning_details', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_phone', 'draw_number', 'draw_time', 'bet_type_display',
            'numbers_display', 'is_winner', 'winning_level', 'winning_amount',
            'winning_details', 'status', 'created_at', 'updated_at'
        ]
    
    def get_numbers_display(self, obj):
        """获取号码显示格式"""
        return obj.get_numbers_display()


class SuperLottoStatisticsSerializer(serializers.ModelSerializer):
    """
    大乐透统计序列化器
    """
    game_name = serializers.CharField(source='game.name', read_only=True)
    draw_number = serializers.CharField(source='draw.draw_number', read_only=True)
    payout_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = SuperLottoStatistics
        fields = [
            'id', 'game_name', 'draw_number', 'total_bets', 'total_bet_count',
            'total_sales_amount', 'total_winners', 'total_winning_amount',
            'first_prize_bets', 'first_prize_amount', 'second_prize_bets',
            'second_prize_amount', 'third_prize_bets', 'third_prize_amount',
            'fourth_prize_bets', 'fourth_prize_amount', 'fifth_prize_bets',
            'fifth_prize_amount', 'sixth_prize_bets', 'sixth_prize_amount',
            'seventh_prize_bets', 'seventh_prize_amount', 'eighth_prize_bets',
            'eighth_prize_amount', 'ninth_prize_bets', 'ninth_prize_amount',
            'profit', 'profit_rate', 'payout_rate', 'unique_players',
            'avg_bet_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'payout_rate', 'created_at', 'updated_at']
    
    def get_payout_rate(self, obj):
        """计算派彩率"""
        return obj.calculate_payout_rate()


# 请求/响应序列化器
class BetCalculationSerializer(serializers.Serializer):
    """
    投注计算请求序列化器
    """
    bet_type = serializers.ChoiceField(choices=['SINGLE', 'MULTIPLE', 'SYSTEM'])
    front_numbers = serializers.ListField(child=serializers.IntegerField(min_value=1, max_value=35))
    back_numbers = serializers.ListField(child=serializers.IntegerField(min_value=1, max_value=12))
    front_dan_numbers = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=35),
        required=False, allow_empty=True
    )
    front_tuo_numbers = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=35),
        required=False, allow_empty=True
    )
    back_dan_numbers = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=12),
        required=False, allow_empty=True
    )
    back_tuo_numbers = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=12),
        required=False, allow_empty=True
    )
    multiplier = serializers.IntegerField(min_value=1, max_value=99, default=1)


class PlaceBetSerializer(BetCalculationSerializer):
    """
    投注下单序列化器
    """
    pass


class NumberValidationSerializer(serializers.Serializer):
    """
    号码验证序列化器
    """
    front_numbers = serializers.ListField(child=serializers.IntegerField(min_value=1, max_value=35))
    back_numbers = serializers.ListField(child=serializers.IntegerField(min_value=1, max_value=12))


class RandomNumbersResponseSerializer(serializers.Serializer):
    """
    随机号码响应序列化器
    """
    success = serializers.BooleanField()
    front_numbers = serializers.ListField(child=serializers.IntegerField(), required=False)
    back_numbers = serializers.ListField(child=serializers.IntegerField(), required=False)
    message = serializers.CharField(required=False)


class BetCalculationResponseSerializer(serializers.Serializer):
    """
    投注计算响应序列化器
    """
    success = serializers.BooleanField()
    bet_count = serializers.IntegerField(required=False)
    single_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    multiplier = serializers.IntegerField(required=False)
    message = serializers.CharField(required=False)