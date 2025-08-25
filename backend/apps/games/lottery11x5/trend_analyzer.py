"""
11选5走势分析器
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db.models import Count, Q
from django.core.cache import cache

from .models import Lottery11x5Result, Lottery11x5Trend, Lottery11x5HotCold
from apps.games.models import Draw


class Lottery11x5TrendAnalyzer:
    """
    11选5走势分析器
    """
    
    def __init__(self, game):
        self.game = game
        self.cache_timeout = 1800  # 30分钟缓存
    
    def get_trend_data(self, limit: int = 30, date_from: date = None, 
                      date_to: date = None) -> Dict[str, Any]:
        """
        获取走势数据
        """
        cache_key = f'lottery11x5_trend_{limit}_{date_from}_{date_to}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 构建查询条件
        queryset = Lottery11x5Result.objects.filter(
            draw__game=self.game,
            draw__status='COMPLETED'
        ).select_related('draw').order_by('-draw__draw_time')
        
        if date_from:
            queryset = queryset.filter(draw__draw_time__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(draw__draw_time__date__lte=date_to)
        
        results = queryset[:limit]
        
        # 格式化走势数据
        trend_data = []
        for result in results:
            trend_data.append({
                'draw_number': result.draw.draw_number,
                'draw_time': result.draw.draw_time,
                'numbers': result.numbers,
                'sum_value': result.sum_value,
                'odd_count': result.odd_count,
                'even_count': result.even_count,
                'big_count': result.big_count,
                'small_count': result.small_count,
                'span_value': result.span_value,
                'positions': self._get_position_numbers(result.numbers),
            })
        
        # 计算走势统计
        trend_stats = self._calculate_trend_statistics(trend_data)
        
        result_data = {
            'trend_data': trend_data,
            'statistics': trend_stats,
            'period_info': {
                'total_periods': len(trend_data),
                'date_range': {
                    'from': trend_data[-1]['draw_time'] if trend_data else None,
                    'to': trend_data[0]['draw_time'] if trend_data else None,
                }
            }
        }
        
        # 缓存结果
        cache.set(cache_key, result_data, self.cache_timeout)
        
        return result_data  
  def _get_position_numbers(self, numbers: List[int]) -> Dict[str, int]:
        """
        获取各位置号码
        """
        positions = {}
        for i, number in enumerate(numbers):
            positions[f'pos_{i+1}'] = number
        return positions
    
    def _calculate_trend_statistics(self, trend_data: List[Dict]) -> Dict[str, Any]:
        """
        计算走势统计
        """
        if not trend_data:
            return {}
        
        # 和值统计
        sum_values = [item['sum_value'] for item in trend_data]
        sum_stats = {
            'min': min(sum_values),
            'max': max(sum_values),
            'avg': sum(sum_values) / len(sum_values),
            'distribution': self._get_sum_distribution(sum_values)
        }
        
        # 奇偶统计
        odd_counts = [item['odd_count'] for item in trend_data]
        odd_even_stats = {
            'odd_avg': sum(odd_counts) / len(odd_counts),
            'distribution': self._get_odd_even_distribution(odd_counts)
        }
        
        # 大小统计
        big_counts = [item['big_count'] for item in trend_data]
        big_small_stats = {
            'big_avg': sum(big_counts) / len(big_counts),
            'distribution': self._get_big_small_distribution(big_counts)
        }
        
        # 跨度统计
        span_values = [item['span_value'] for item in trend_data]
        span_stats = {
            'min': min(span_values),
            'max': max(span_values),
            'avg': sum(span_values) / len(span_values),
            'distribution': self._get_span_distribution(span_values)
        }
        
        return {
            'sum_value': sum_stats,
            'odd_even': odd_even_stats,
            'big_small': big_small_stats,
            'span_value': span_stats,
        }
    
    def _get_sum_distribution(self, sum_values: List[int]) -> Dict[str, int]:
        """
        获取和值分布
        """
        distribution = {}
        for value in sum_values:
            distribution[str(value)] = distribution.get(str(value), 0) + 1
        return distribution
    
    def _get_odd_even_distribution(self, odd_counts: List[int]) -> Dict[str, int]:
        """
        获取奇偶分布
        """
        distribution = {}
        for count in odd_counts:
            key = f"{count}奇{5-count}偶"
            distribution[key] = distribution.get(key, 0) + 1
        return distribution
    
    def _get_big_small_distribution(self, big_counts: List[int]) -> Dict[str, int]:
        """
        获取大小分布
        """
        distribution = {}
        for count in big_counts:
            key = f"{count}大{5-count}小"
            distribution[key] = distribution.get(key, 0) + 1
        return distribution
    
    def _get_span_distribution(self, span_values: List[int]) -> Dict[str, int]:
        """
        获取跨度分布
        """
        distribution = {}
        for value in span_values:
            distribution[str(value)] = distribution.get(str(value), 0) + 1
        return distribution    
def get_position_trend(self, position: int, limit: int = 50) -> Dict[str, Any]:
        """
        获取指定位置的走势
        """
        if position < 1 or position > 5:
            raise ValueError("位置必须在1-5之间")
        
        cache_key = f'lottery11x5_position_trend_{position}_{limit}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 获取最近的开奖结果
        results = Lottery11x5Result.objects.filter(
            draw__game=self.game,
            draw__status='COMPLETED'
        ).select_related('draw').order_by('-draw__draw_time')[:limit]
        
        position_data = []
        for result in results:
            if len(result.numbers) >= position:
                position_data.append({
                    'draw_number': result.draw.draw_number,
                    'draw_time': result.draw.draw_time,
                    'number': result.numbers[position - 1],
                    'all_numbers': result.numbers,
                })
        
        # 计算位置统计
        position_stats = self._calculate_position_statistics(position_data, position)
        
        result_data = {
            'position': position,
            'position_name': f'第{position}位',
            'trend_data': position_data,
            'statistics': position_stats,
        }
        
        # 缓存结果
        cache.set(cache_key, result_data, self.cache_timeout)
        
        return result_data
    
    def _calculate_position_statistics(self, position_data: List[Dict], position: int) -> Dict[str, Any]:
        """
        计算位置统计
        """
        if not position_data:
            return {}
        
        numbers = [item['number'] for item in position_data]
        
        # 号码频率统计
        frequency = {}
        for num in range(1, 12):
            frequency[str(num)] = numbers.count(num)
        
        # 遗漏值计算
        missing_values = self._calculate_missing_values(numbers)
        
        # 最大遗漏
        max_missing = {}
        for num in range(1, 12):
            max_missing[str(num)] = self._get_max_missing(numbers, num)
        
        # 连出统计
        consecutive_stats = self._calculate_consecutive_stats(numbers)
        
        return {
            'frequency': frequency,
            'missing_values': missing_values,
            'max_missing': max_missing,
            'consecutive_stats': consecutive_stats,
            'most_frequent': max(frequency.items(), key=lambda x: x[1]),
            'least_frequent': min(frequency.items(), key=lambda x: x[1]),
        }
    
    def _calculate_missing_values(self, numbers: List[int]) -> Dict[str, int]:
        """
        计算当前遗漏值
        """
        missing_values = {}
        
        for num in range(1, 12):
            missing = 0
            for number in numbers:
                if number == num:
                    break
                missing += 1
            missing_values[str(num)] = missing if missing < len(numbers) else len(numbers)
        
        return missing_values
    
    def _get_max_missing(self, numbers: List[int], target_num: int) -> int:
        """
        获取最大遗漏值
        """
        max_missing = 0
        current_missing = 0
        
        for number in reversed(numbers):  # 从最早的开始
            if number == target_num:
                max_missing = max(max_missing, current_missing)
                current_missing = 0
            else:
                current_missing += 1
        
        return max(max_missing, current_missing)
    
    def _calculate_consecutive_stats(self, numbers: List[int]) -> Dict[str, Any]:
        """
        计算连出统计
        """
        consecutive_stats = {}
        
        for num in range(1, 12):
            max_consecutive = 0
            current_consecutive = 0
            
            for number in reversed(numbers):  # 从最早的开始
                if number == num:
                    current_consecutive += 1
                    max_consecutive = max(max_consecutive, current_consecutive)
                else:
                    current_consecutive = 0
            
            consecutive_stats[str(num)] = {
                'max_consecutive': max_consecutive,
                'current_consecutive': current_consecutive if numbers and numbers[0] == num else 0
            }
        
        return consecutive_stats    de
f get_missing_analysis(self, limit: int = 100) -> Dict[str, Any]:
        """
        获取遗漏分析
        """
        cache_key = f'lottery11x5_missing_analysis_{limit}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 获取最近的开奖结果
        results = Lottery11x5Result.objects.filter(
            draw__game=self.game,
            draw__status='COMPLETED'
        ).select_related('draw').order_by('-draw__draw_time')[:limit]
        
        if not results:
            return {'error': '暂无开奖数据'}
        
        # 计算每个号码的遗漏情况
        missing_analysis = {}
        
        for num in range(1, 12):
            missing_data = self._analyze_number_missing(results, num)
            missing_analysis[str(num)] = missing_data
        
        # 计算整体遗漏统计
        overall_stats = self._calculate_overall_missing_stats(missing_analysis)
        
        result_data = {
            'number_analysis': missing_analysis,
            'overall_stats': overall_stats,
            'period_count': len(results),
            'analysis_date': timezone.now().isoformat(),
        }
        
        # 缓存结果
        cache.set(cache_key, result_data, self.cache_timeout)
        
        return result_data
    
    def _analyze_number_missing(self, results, target_num: int) -> Dict[str, Any]:
        """
        分析单个号码的遗漏情况
        """
        appearances = []
        missing_periods = []
        
        current_missing = 0
        
        for i, result in enumerate(results):
            if target_num in result.numbers:
                appearances.append({
                    'period': i,
                    'draw_number': result.draw.draw_number,
                    'missing_before': current_missing
                })
                if current_missing > 0:
                    missing_periods.append(current_missing)
                current_missing = 0
            else:
                current_missing += 1
        
        # 如果最后还在遗漏中
        if current_missing > 0:
            missing_periods.append(current_missing)
        
        # 计算统计数据
        if missing_periods:
            avg_missing = sum(missing_periods) / len(missing_periods)
            max_missing = max(missing_periods)
            min_missing = min(missing_periods)
        else:
            avg_missing = max_missing = min_missing = 0
        
        return {
            'appearances': len(appearances),
            'current_missing': current_missing,
            'avg_missing': round(avg_missing, 2),
            'max_missing': max_missing,
            'min_missing': min_missing,
            'missing_periods': missing_periods,
            'appearance_rate': round(len(appearances) / len(results) * 100, 2) if results else 0,
            'last_appearances': appearances[:5]  # 最近5次出现
        }
    
    def _calculate_overall_missing_stats(self, missing_analysis: Dict) -> Dict[str, Any]:
        """
        计算整体遗漏统计
        """
        all_current_missing = [data['current_missing'] for data in missing_analysis.values()]
        all_max_missing = [data['max_missing'] for data in missing_analysis.values()]
        all_avg_missing = [data['avg_missing'] for data in missing_analysis.values()]
        
        return {
            'avg_current_missing': round(sum(all_current_missing) / len(all_current_missing), 2),
            'max_current_missing': max(all_current_missing),
            'min_current_missing': min(all_current_missing),
            'avg_max_missing': round(sum(all_max_missing) / len(all_max_missing), 2),
            'overall_max_missing': max(all_max_missing),
            'avg_avg_missing': round(sum(all_avg_missing) / len(all_avg_missing), 2),
        }
    
    def get_hot_cold_analysis(self, period_types: List[int] = [10, 30, 50, 100]) -> Dict[str, Any]:
        """
        获取冷热号码分析
        """
        cache_key = f'lottery11x5_hot_cold_analysis_{"-".join(map(str, period_types))}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        analysis_result = {}
        
        for period in period_types:
            period_analysis = self._analyze_hot_cold_for_period(period)
            analysis_result[str(period)] = period_analysis
        
        # 综合分析
        comprehensive_analysis = self._get_comprehensive_hot_cold(analysis_result)
        
        result_data = {
            'period_analysis': analysis_result,
            'comprehensive': comprehensive_analysis,
            'analysis_date': timezone.now().isoformat(),
        }
        
        # 缓存结果
        cache.set(cache_key, result_data, self.cache_timeout)
        
        return result_data
    
    def _analyze_hot_cold_for_period(self, period: int) -> Dict[str, Any]:
        """
        分析指定期数的冷热号码
        """
        # 获取最近期数的开奖结果
        results = Lottery11x5Result.objects.filter(
            draw__game=self.game,
            draw__status='COMPLETED'
        ).order_by('-draw__draw_time')[:period]
        
        if len(results) < period:
            return {'error': f'数据不足，需要{period}期，实际{len(results)}期'}
        
        # 统计每个号码的出现次数
        number_counts = {i: 0 for i in range(1, 12)}
        
        for result in results:
            for number in result.numbers:
                number_counts[number] += 1
        
        # 计算理论平均出现次数
        theoretical_avg = period * 5 / 11  # 每期5个号码，共11个号码
        
        # 分类冷热号码
        hot_numbers = []
        cold_numbers = []
        normal_numbers = []
        
        hot_threshold = theoretical_avg * 1.2
        cold_threshold = theoretical_avg * 0.8
        
        for number, count in number_counts.items():
            number_data = {
                'number': number,
                'count': count,
                'rate': round(count / period * 100, 2),
                'deviation': round((count - theoretical_avg) / theoretical_avg * 100, 2)
            }
            
            if count >= hot_threshold:
                hot_numbers.append(number_data)
            elif count <= cold_threshold:
                cold_numbers.append(number_data)
            else:
                normal_numbers.append(number_data)
        
        # 排序
        hot_numbers.sort(key=lambda x: x['count'], reverse=True)
        cold_numbers.sort(key=lambda x: x['count'])
        
        return {
            'period': period,
            'theoretical_avg': round(theoretical_avg, 2),
            'hot_threshold': round(hot_threshold, 2),
            'cold_threshold': round(cold_threshold, 2),
            'hot_numbers': hot_numbers,
            'cold_numbers': cold_numbers,
            'normal_numbers': normal_numbers,
            'hot_count': len(hot_numbers),
            'cold_count': len(cold_numbers),
            'normal_count': len(normal_numbers),
        }
    
    def _get_comprehensive_hot_cold(self, period_analysis: Dict) -> Dict[str, Any]:
        """
        获取综合冷热分析
        """
        # 统计每个号码在不同周期中的表现
        number_scores = {i: 0 for i in range(1, 12)}
        
        for period_str, analysis in period_analysis.items():
            if 'error' in analysis:
                continue
            
            # 热号加分，冷号减分
            for hot_num in analysis['hot_numbers']:
                number_scores[hot_num['number']] += 2
            
            for cold_num in analysis['cold_numbers']:
                number_scores[cold_num['number']] -= 2
        
        # 根据综合得分分类
        comprehensive_hot = []
        comprehensive_cold = []
        comprehensive_normal = []
        
        for number, score in number_scores.items():
            if score >= 4:
                comprehensive_hot.append({'number': number, 'score': score})
            elif score <= -4:
                comprehensive_cold.append({'number': number, 'score': score})
            else:
                comprehensive_normal.append({'number': number, 'score': score})
        
        # 排序
        comprehensive_hot.sort(key=lambda x: x['score'], reverse=True)
        comprehensive_cold.sort(key=lambda x: x['score'])
        
        return {
            'hot_numbers': comprehensive_hot,
            'cold_numbers': comprehensive_cold,
            'normal_numbers': comprehensive_normal,
            'recommendation': {
                'focus_hot': [item['number'] for item in comprehensive_hot[:3]],
                'avoid_cold': [item['number'] for item in comprehensive_cold[:3]],
                'balanced': [item['number'] for item in comprehensive_normal[:5]],
            }
        } 
   def get_complete_trend_chart(self, limit: int = 30) -> Dict[str, Any]:
        """
        获取完整走势图数据
        """
        cache_key = f'lottery11x5_complete_trend_{limit}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 获取最近的开奖结果
        results = Lottery11x5Result.objects.filter(
            draw__game=self.game,
            draw__status='COMPLETED'
        ).select_related('draw').order_by('-draw__draw_time')[:limit]
        
        if not results:
            return {'error': '暂无开奖数据'}
        
        # 生成走势图数据
        chart_data = {
            'headers': self._generate_chart_headers(),
            'rows': [],
            'statistics': {},
        }
        
        # 生成每期数据行
        for result in reversed(results):  # 按时间正序
            row_data = self._generate_chart_row(result)
            chart_data['rows'].append(row_data)
        
        # 计算走势统计
        chart_data['statistics'] = self._calculate_chart_statistics(chart_data['rows'])
        
        # 缓存结果
        cache.set(cache_key, chart_data, self.cache_timeout)
        
        return chart_data
    
    def _generate_chart_headers(self) -> List[Dict[str, Any]]:
        """
        生成走势图表头
        """
        headers = [
            {'key': 'draw_number', 'title': '期号', 'type': 'text'},
            {'key': 'draw_time', 'title': '开奖时间', 'type': 'datetime'},
        ]
        
        # 万位到个位
        for pos in range(1, 6):
            headers.append({
                'key': f'pos_{pos}',
                'title': f'第{pos}位',
                'type': 'position',
                'position': pos
            })
        
        # 号码1-11的出现情况
        for num in range(1, 12):
            headers.append({
                'key': f'num_{num}',
                'title': f'{num:02d}',
                'type': 'number',
                'number': num
            })
        
        # 统计项
        headers.extend([
            {'key': 'sum_value', 'title': '和值', 'type': 'sum'},
            {'key': 'odd_even', 'title': '奇偶', 'type': 'odd_even'},
            {'key': 'big_small', 'title': '大小', 'type': 'big_small'},
            {'key': 'span_value', 'title': '跨度', 'type': 'span'},
        ])
        
        return headers
    
    def _generate_chart_row(self, result: Lottery11x5Result) -> Dict[str, Any]:
        """
        生成走势图数据行
        """
        row = {
            'draw_number': result.draw.draw_number,
            'draw_time': result.draw.draw_time,
            'numbers': result.numbers,
        }
        
        # 位置号码
        for i, number in enumerate(result.numbers):
            row[f'pos_{i+1}'] = number
        
        # 号码出现标记
        for num in range(1, 12):
            row[f'num_{num}'] = num in result.numbers
        
        # 统计数据
        row.update({
            'sum_value': result.sum_value,
            'odd_even': f"{result.odd_count}:{result.even_count}",
            'big_small': f"{result.big_count}:{result.small_count}",
            'span_value': result.span_value,
        })
        
        return row
    
    def _calculate_chart_statistics(self, rows: List[Dict]) -> Dict[str, Any]:
        """
        计算走势图统计数据
        """
        if not rows:
            return {}
        
        stats = {
            'total_periods': len(rows),
            'number_frequency': {str(i): 0 for i in range(1, 12)},
            'position_stats': {f'pos_{i}': {} for i in range(1, 6)},
            'sum_stats': {},
            'span_stats': {},
        }
        
        # 统计号码频率
        for row in rows:
            for num in row['numbers']:
                stats['number_frequency'][str(num)] += 1
        
        # 统计位置号码分布
        for pos in range(1, 6):
            pos_key = f'pos_{pos}'
            pos_numbers = [row[pos_key] for row in rows if pos_key in row]
            
            pos_freq = {}
            for num in pos_numbers:
                pos_freq[str(num)] = pos_freq.get(str(num), 0) + 1
            
            stats['position_stats'][pos_key] = {
                'frequency': pos_freq,
                'most_common': max(pos_freq.items(), key=lambda x: x[1]) if pos_freq else None,
                'least_common': min(pos_freq.items(), key=lambda x: x[1]) if pos_freq else None,
            }
        
        # 和值统计
        sum_values = [row['sum_value'] for row in rows]
        stats['sum_stats'] = {
            'min': min(sum_values),
            'max': max(sum_values),
            'avg': round(sum(sum_values) / len(sum_values), 2),
            'distribution': self._get_distribution(sum_values)
        }
        
        # 跨度统计
        span_values = [row['span_value'] for row in rows]
        stats['span_stats'] = {
            'min': min(span_values),
            'max': max(span_values),
            'avg': round(sum(span_values) / len(span_values), 2),
            'distribution': self._get_distribution(span_values)
        }
        
        return stats
    
    def _get_distribution(self, values: List[int]) -> Dict[str, int]:
        """
        获取数值分布
        """
        distribution = {}
        for value in values:
            key = str(value)
            distribution[key] = distribution.get(key, 0) + 1
        return distribution
    
    def get_prediction_analysis(self, limit: int = 50) -> Dict[str, Any]:
        """
        获取预测分析（基于历史规律）
        """
        cache_key = f'lottery11x5_prediction_{limit}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 获取历史数据
        trend_data = self.get_trend_data(limit)
        missing_data = self.get_missing_analysis(limit)
        hot_cold_data = self.get_hot_cold_analysis([30, 50])
        
        # 生成预测建议
        prediction = {
            'recommended_numbers': self._get_recommended_numbers(missing_data, hot_cold_data),
            'avoid_numbers': self._get_avoid_numbers(missing_data, hot_cold_data),
            'sum_range': self._predict_sum_range(trend_data),
            'odd_even_suggestion': self._predict_odd_even(trend_data),
            'big_small_suggestion': self._predict_big_small(trend_data),
            'analysis_basis': {
                'missing_analysis': '基于遗漏值分析',
                'hot_cold_analysis': '基于冷热号码分析',
                'trend_analysis': '基于历史走势分析',
            },
            'disclaimer': '预测仅供参考，彩票具有随机性，请理性投注'
        }
        
        # 缓存结果
        cache.set(cache_key, prediction, self.cache_timeout // 2)  # 预测数据缓存时间短一些
        
        return prediction
    
    def _get_recommended_numbers(self, missing_data: Dict, hot_cold_data: Dict) -> List[Dict[str, Any]]:
        """
        获取推荐号码
        """
        recommendations = []
        
        # 基于遗漏值推荐
        if 'number_analysis' in missing_data:
            for num_str, analysis in missing_data['number_analysis'].items():
                if analysis['current_missing'] >= analysis['avg_missing'] * 1.5:
                    recommendations.append({
                        'number': int(num_str),
                        'reason': f'遗漏{analysis["current_missing"]}期，超过平均遗漏{analysis["avg_missing"]:.1f}期',
                        'priority': 'high' if analysis['current_missing'] >= analysis['max_missing'] * 0.8 else 'medium'
                    })
        
        # 基于热号推荐
        if 'comprehensive' in hot_cold_data:
            for hot_num in hot_cold_data['comprehensive']['recommendation']['focus_hot']:
                recommendations.append({
                    'number': hot_num,
                    'reason': '综合分析热号',
                    'priority': 'medium'
                })
        
        # 去重并排序
        seen_numbers = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec['number'] not in seen_numbers:
                seen_numbers.add(rec['number'])
                unique_recommendations.append(rec)
        
        # 按优先级排序
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        unique_recommendations.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return unique_recommendations[:8]  # 返回前8个推荐
    
    def _get_avoid_numbers(self, missing_data: Dict, hot_cold_data: Dict) -> List[Dict[str, Any]]:
        """
        获取建议避开的号码
        """
        avoid_list = []
        
        # 基于冷号避开
        if 'comprehensive' in hot_cold_data:
            for cold_num in hot_cold_data['comprehensive']['recommendation']['avoid_cold']:
                avoid_list.append({
                    'number': cold_num,
                    'reason': '综合分析冷号',
                    'priority': 'medium'
                })
        
        return avoid_list[:5]  # 返回前5个避开建议
    
    def _predict_sum_range(self, trend_data: Dict) -> Dict[str, Any]:
        """
        预测和值范围
        """
        if 'statistics' not in trend_data or 'sum_value' not in trend_data['statistics']:
            return {}
        
        sum_stats = trend_data['statistics']['sum_value']
        avg = sum_stats['avg']
        
        return {
            'recommended_range': [int(avg - 5), int(avg + 5)],
            'optimal_range': [int(avg - 3), int(avg + 3)],
            'basis': f'基于最近{len(trend_data.get("trend_data", []))}期平均和值{avg:.1f}'
        }
    
    def _predict_odd_even(self, trend_data: Dict) -> Dict[str, Any]:
        """
        预测奇偶比例
        """
        if 'statistics' not in trend_data or 'odd_even' not in trend_data['statistics']:
            return {}
        
        odd_stats = trend_data['statistics']['odd_even']
        avg_odd = odd_stats['odd_avg']
        
        if avg_odd > 2.8:
            suggestion = "偶数可能回补"
        elif avg_odd < 2.2:
            suggestion = "奇数可能回补"
        else:
            suggestion = "奇偶相对均衡"
        
        return {
            'suggestion': suggestion,
            'recent_avg_odd': round(avg_odd, 1),
            'basis': f'最近平均奇数个数{avg_odd:.1f}个'
        }
    
    def _predict_big_small(self, trend_data: Dict) -> Dict[str, Any]:
        """
        预测大小比例
        """
        if 'statistics' not in trend_data or 'big_small' not in trend_data['statistics']:
            return {}
        
        big_stats = trend_data['statistics']['big_small']
        avg_big = big_stats['big_avg']
        
        if avg_big > 2.8:
            suggestion = "小号可能回补"
        elif avg_big < 2.2:
            suggestion = "大号可能回补"
        else:
            suggestion = "大小相对均衡"
        
        return {
            'suggestion': suggestion,
            'recent_avg_big': round(avg_big, 1),
            'basis': f'最近平均大号个数{avg_big:.1f}个'
        }