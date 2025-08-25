"""
11选5彩票游戏序列化器
"""

from rest_framework import serializers
from apps.games.models import Game, Draw, BetType, Bet
from .models import (
    Lottery11x5Game,
    Lottery11x5Bet,
    Lottery11x5Result,
    Lottery11x5Trend,
    Lottery11x5HotCold,
    Lottery11x5UserNumber
)


class Lottery11x5GameSerializer(serializers.ModelSerializer):
    """
    11选5游戏配置序列化器
    """
    game_name = serializers.CharField(source='game.name', read_only=True)
    
    class Meta:
        model = Lottery11x5Game
        fields = [
            'game_name', 'draw_count_per_day', 'first_draw_time',
            'draw_interval_minutes', 'close_before_minutes',
            'auto_create_draws', 'auto_draw_results', 'profit_target',
            'enable_position_bets', 'enable_any_bets', 'enable_group_bets',
            'position_odds', 'any_1_odds', 'any_2_odds', 'any_3_odds',
            'any_4_odds', 'any_5_odds', 'created_at', 'updated_at'
        ]


class Lottery11x5DrawSerializer(serializers.ModelSerializer):
    """
    11选5期次序列化器
    """
    game_name = serializers.CharField(source='game.name', read_only=True)
    is_open_for_betting = serializers.SerializerMethodField()
    time_until_close = serializers.SerializerMethodField()
    time_until_draw = serializers.SerializerMethodField()
    
    class Meta:
        model = Draw
        fields = [
            'id', 'game_name', 'draw_number', 'draw_time', 'close_time',
            'status', 'result', 'winning_numbers', 'total_bets',
            'total_amount', 'total_payout', 'profit',
            'is_open_for_betting', 'time_until_close', 'time_until_draw',
            'created_at', 'updated_at'
        ]
    
    def get_is_open_for_betting(self, obj):
        return obj.is_open_for_betting()
    
    def get_time_until_close(self, obj):
        return obj.time_until_close()
    
    def get_time_until_draw(self, obj):
        return obj.time_until_draw()


class Lottery11x5BetSerializer(serializers.ModelSerializer):
    """
    11选5投注序列化器
    """
    bet_id = serializers.CharField(source='bet.id', read_only=True)
    user_phone = serializers.CharField(source='bet.user.phone', read_only=True)
    draw_number = serializers.CharField(source='bet.draw.draw_number', read_only=True)
    bet_type_name = serializers.CharField(source='bet.bet_type.name', read_only=True)
    numbers = serializers.JSONField(source='bet.numbers', read_only=True)
    amount = serializers.DecimalField(source='bet.amount', max_digits=10, decimal_places=2, read_only=True)
    odds = serializers.DecimalField(source='bet.odds', max_digits=10, decimal_places=2, read_only=True)
    potential_payout = serializers.DecimalField(source='bet.potential_payout', max_digits=15, decimal_places=2, read_only=True)
    status = serializers.CharField(source='bet.status', read_only=True)
    payout = serializers.DecimalField(source='bet.payout', max_digits=15, decimal_places=2, read_only=True)
    bet_time = serializers.DateTimeField(source='bet.bet_time', read_only=True)
    settled_at = serializers.DateTimeField(source='bet.settled_at', read_only=True)
    
    class Meta:
        model = Lottery11x5Bet
        fields = [
            'bet_id', 'user_phone', 'draw_number', 'bet_type_name',
            'bet_method', 'positions', 'selected_count', 'is_multiple',
            'multiple_count', 'numbers', 'amount', 'odds',
            'potential_payout', 'status', 'payout',
            'bet_time', 'settled_at', 'created_at'
        ]


class Lottery11x5ResultSerializer(serializers.ModelSerializer):
    """
    11选5开奖结果序列化器
    """
    draw_number = serializers.CharField(source='draw.draw_number', read_only=True)
    draw_time = serializers.DateTimeField(source='draw.draw_time', read_only=True)
    total_bets = serializers.IntegerField(source='draw.total_bets', read_only=True)
    total_amount = serializers.DecimalField(source='draw.total_amount', max_digits=15, decimal_places=2, read_only=True)
    total_payout = serializers.DecimalField(source='draw.total_payout', max_digits=15, decimal_places=2, read_only=True)
    profit = serializers.DecimalField(source='draw.profit', max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = Lottery11x5Result
        fields = [
            'draw_number', 'draw_time', 'numbers', 'sum_value',
            'odd_count', 'even_count', 'big_count', 'small_count',
            'span_value', 'total_bets', 'total_amount',
            'total_payout', 'profit', 'created_at'
        ]


class Lottery11x5TrendSerializer(serializers.ModelSerializer):
    """
    11选5走势序列化器
    """
    game_name = serializers.CharField(source='game.name', read_only=True)
    
    class Meta:
        model = Lottery11x5Trend
        fields = [
            'game_name', 'date', 'draw_number', 'numbers',
            'positions', 'sum_value', 'odd_even', 'big_small',
            'created_at'
        ]


class Lottery11x5HotColdSerializer(serializers.ModelSerializer):
    """
    11选5冷热号码序列化器
    """
    game_name = serializers.CharField(source='game.name', read_only=True)
    period_display = serializers.CharField(source='get_period_type_display', read_only=True)
    
    class Meta:
        model = Lottery11x5HotCold
        fields = [
            'game_name', 'period_type', 'period_display', 'number',
            'frequency', 'last_appearance', 'is_hot', 'is_cold',
            'updated_at'
        ]


class Lottery11x5UserNumberSerializer(serializers.ModelSerializer):
    """
    11选5用户常用号码序列化器
    """
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    game_name = serializers.CharField(source='game.name', read_only=True)
    bet_method_display = serializers.CharField(source='get_bet_method_display', read_only=True)
    win_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Lottery11x5UserNumber
        fields = [
            'id', 'user_phone', 'game_name', 'name', 'numbers',
            'bet_method', 'bet_method_display', 'positions',
            'selected_count', 'is_favorite', 'usage_count',
            'win_count', 'win_rate', 'created_at', 'updated_at'
        ]
    
    def get_win_rate(self, obj):
        if obj.usage_count == 0:
            return 0.0
        return round(obj.win_count / obj.usage_count * 100, 2)


class BetPlaceSerializer(serializers.Serializer):
    """
    投注请求序列化器
    """
    draw_id = serializers.UUIDField()
    bet_type_id = serializers.UUIDField()
    numbers = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=11),
        min_length=1,
        max_length=11
    )
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1)
    bet_method = serializers.ChoiceField(choices=['POSITION', 'ANY', 'GROUP'])
    positions = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=5),
        required=False,
        allow_empty=True
    )
    selected_count = serializers.IntegerField(min_value=0, max_value=5, required=False, default=0)
    
    def validate_numbers(self, value):
        """验证号码"""
        # 检查号码重复
        if len(value) != len(set(value)):
            raise serializers.ValidationError("号码不能重复")
        
        # 检查号码范围
        for num in value:
            if not (1 <= num <= 11):
                raise serializers.ValidationError("号码必须在1-11之间")
        
        return value
    
    def validate(self, data):
        """验证整体数据"""
        bet_method = data['bet_method']
        numbers = data['numbers']
        positions = data.get('positions', [])
        selected_count = data.get('selected_count', 0)
        
        if bet_method == 'POSITION':
            # 定位胆玩法验证
            if not positions:
                raise serializers.ValidationError("定位胆玩法必须指定位置")
            
            if len(numbers) != len(positions):
                raise serializers.ValidationError("定位胆玩法号码数量必须与位置数量相等")
            
            # 检查位置重复
            if len(positions) != len(set(positions)):
                raise serializers.ValidationError("位置不能重复")
                
        elif bet_method == 'ANY':
            # 任选玩法验证
            if selected_count < 1 or selected_count > 5:
                raise serializers.ValidationError("任选玩法选择数量必须在1-5之间")
            
            if len(numbers) < selected_count:
                raise serializers.ValidationError("选择的号码数量不能少于任选数量")
                
        elif bet_method == 'GROUP':
            # 组选玩法验证
            if len(numbers) < 2:
                raise serializers.ValidationError("组选玩法至少需要选择2个号码")
        
        return data


class RandomNumbersSerializer(serializers.Serializer):
    """
    随机号码生成序列化器
    """
    count = serializers.IntegerField(min_value=1, max_value=11, default=5)


class TrendAnalysisSerializer(serializers.Serializer):
    """
    走势分析请求序列化器
    """
    limit = serializers.IntegerField(min_value=1, max_value=100, default=30)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)


class NumberStatisticsSerializer(serializers.Serializer):
    """
    号码统计请求序列化器
    """
    limit = serializers.IntegerField(min_value=1, max_value=500, default=100)
    period_type = serializers.ChoiceField(choices=[10, 30, 50, 100], default=50)