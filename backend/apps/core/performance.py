# -*- coding: utf-8 -*-
"""
API性能优化和并发处理
支持10万+用户的高并发优化方案
"""

import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework.response import Response
from rest_framework import status
from functools import wraps
import logging
from typing import Dict, List, Any, Callable, Optional
import json
import hashlib
from collections import defaultdict
import psutil
import gc

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.request_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.concurrent_requests = 0
        self.max_concurrent = 0
        self.lock = threading.Lock()
    
    def record_request(self, endpoint: str, duration: float, status_code: int):
        """记录请求性能"""
        with self.lock:
            self.request_times[endpoint].append(duration)
            
            # 只保留最近1000次请求的记录
            if len(self.request_times[endpoint]) > 1000:
                self.request_times[endpoint] = self.request_times[endpoint][-1000:]
            
            if status_code >= 400:
                self.error_counts[endpoint] += 1
    
    def get_stats(self) -> Dict:
        """获取性能统计"""
        with self.lock:
            stats = {}
            
            for endpoint, times in self.request_times.items():
                if times:
                    stats[endpoint] = {
                        'avg_response_time': sum(times) / len(times),
                        'max_response_time': max(times),
                        'min_response_time': min(times),
                        'request_count': len(times),
                        'error_count': self.error_counts.get(endpoint, 0),
                        'error_rate': (self.error_counts.get(endpoint, 0) / len(times)) * 100
                    }
            
            return stats
    
    def increment_concurrent(self):
        """增加并发计数"""
        with self.lock:
            self.concurrent_requests += 1
            self.max_concurrent = max(self.max_concurrent, self.concurrent_requests)
    
    def decrement_concurrent(self):
        """减少并发计数"""
        with self.lock:
            self.concurrent_requests = max(0, self.concurrent_requests - 1)


# 全局性能监控实例
performance_monitor = PerformanceMonitor()


def performance_tracking(func):
    """性能跟踪装饰器"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        start_time = time.time()
        endpoint = request.path
        
        performance_monitor.increment_concurrent()
        
        try:
            response = func(request, *args, **kwargs)
            status_code = getattr(response, 'status_code', 200)
        except Exception as e:
            logger.error(f"请求处理异常 {endpoint}: {e}")
            status_code = 500
            response = JsonResponse({'error': '服务器内部错误'}, status=500)
        finally:
            duration = time.time() - start_time
            performance_monitor.record_request(endpoint, duration, status_code)
            performance_monitor.decrement_concurrent()
            
            # 记录慢请求
            if duration > 1.0:  # 超过1秒的请求
                logger.warning(f"慢请求检测: {endpoint} 耗时 {duration:.3f}s")
        
        return response
    return wrapper


class ConcurrencyLimiter:
    """并发限制器"""
    
    def __init__(self, max_concurrent: int = 1000):
        self.max_concurrent = max_concurrent
        self.current_requests = 0
        self.lock = threading.Lock()
        self.semaphore = threading.Semaphore(max_concurrent)
    
    def __enter__(self):
        if not self.semaphore.acquire(blocking=False):
            raise Exception("服务器繁忙，请稍后重试")
        
        with self.lock:
            self.current_requests += 1
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.lock:
            self.current_requests -= 1
        
        self.semaphore.release()
    
    def get_current_load(self) -> float:
        """获取当前负载百分比"""
        with self.lock:
            return (self.current_requests / self.max_concurrent) * 100


# 全局并发限制器
concurrency_limiter = ConcurrencyLimiter(max_concurrent=1000)


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """频率限制装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # 获取客户端IP
            client_ip = get_client_ip(request)
            
            # 生成限制键
            rate_key = f"rate_limit:{client_ip}:{func.__name__}"
            
            # 检查当前请求数
            current_requests = cache.get(rate_key, 0)
            
            if current_requests >= max_requests:
                return JsonResponse({
                    'error': '请求过于频繁，请稍后重试',
                    'retry_after': window_seconds
                }, status=429)
            
            # 增加请求计数
            cache.set(rate_key, current_requests + 1, window_seconds)
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def get_client_ip(request) -> str:
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class ResponseOptimizer:
    """响应优化器"""
    
    @staticmethod
    def compress_response(data: Any) -> str:
        """压缩响应数据"""
        import gzip
        import base64
        
        json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        compressed = gzip.compress(json_str.encode('utf-8'))
        return base64.b64encode(compressed).decode('ascii')
    
    @staticmethod
    def paginate_response(queryset, page: int = 1, page_size: int = 20) -> Dict:
        """分页响应优化"""
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        
        paginator = Paginator(queryset, page_size)
        
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        return {
            'results': list(page_obj),
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'page_size': page_size,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        }
    
    @staticmethod
    def optimize_queryset(queryset, select_related: List[str] = None, 
                         prefetch_related: List[str] = None):
        """优化查询集"""
        if select_related:
            queryset = queryset.select_related(*select_related)
        
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)
        
        return queryset


class AsyncTaskProcessor:
    """异步任务处理器"""
    
    def __init__(self, max_workers: int = 10):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def submit_task(self, func: Callable, *args, **kwargs):
        """提交异步任务"""
        future = self.executor.submit(func, *args, **kwargs)
        return future
    
    def submit_batch_tasks(self, tasks: List[tuple]) -> List:
        """批量提交任务"""
        futures = []
        
        for task_func, args, kwargs in tasks:
            future = self.executor.submit(task_func, *args, **kwargs)
            futures.append(future)
        
        # 等待所有任务完成
        results = []
        for future in as_completed(futures):
            try:
                result = future.result(timeout=30)  # 30秒超时
                results.append(result)
            except Exception as e:
                logger.error(f"异步任务执行失败: {e}")
                results.append(None)
        
        return results
    
    def shutdown(self):
        """关闭线程池"""
        self.executor.shutdown(wait=True)


# 全局异步任务处理器
async_processor = AsyncTaskProcessor(max_workers=20)


class MemoryOptimizer:
    """内存优化器"""
    
    @staticmethod
    def get_memory_usage() -> Dict:
        """获取内存使用情况"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss,  # 物理内存
            'vms': memory_info.vms,  # 虚拟内存
            'percent': process.memory_percent(),  # 内存使用百分比
            'available': psutil.virtual_memory().available
        }
    
    @staticmethod
    def force_garbage_collection():
        """强制垃圾回收"""
        collected = gc.collect()
        logger.info(f"垃圾回收完成，回收对象数: {collected}")
        return collected
    
    @staticmethod
    def monitor_memory_threshold(threshold_percent: float = 80.0):
        """监控内存阈值"""
        memory_percent = psutil.virtual_memory().percent
        
        if memory_percent > threshold_percent:
            logger.warning(f"内存使用率过高: {memory_percent:.1f}%")
            MemoryOptimizer.force_garbage_collection()
            return True
        
        return False


class DatabaseConnectionOptimizer:
    """数据库连接优化器"""
    
    @staticmethod
    def get_connection_stats() -> Dict:
        """获取数据库连接统计"""
        from django.db import connections
        
        stats = {}
        for alias, connection in connections.all():
            if hasattr(connection, 'queries'):
                stats[alias] = {
                    'query_count': len(connection.queries),
                    'is_usable': connection.is_usable()
                }
        
        return stats
    
    @staticmethod
    def close_old_connections():
        """关闭旧连接"""
        from django.db import connections
        
        for connection in connections.all():
            connection.close_if_unusable_or_obsolete()
    
    @staticmethod
    def reset_queries():
        """重置查询记录"""
        from django.db import connections, reset_queries
        
        reset_queries()
        logger.info("数据库查询记录已重置")


class APIOptimizationMiddleware:
    """API优化中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 请求前处理
        start_time = time.time()
        
        # 检查并发限制
        try:
            with concurrency_limiter:
                # 内存监控
                MemoryOptimizer.monitor_memory_threshold()
                
                response = self.get_response(request)
        except Exception as e:
            logger.error(f"并发限制触发: {e}")
            return JsonResponse({
                'error': '服务器繁忙，请稍后重试'
            }, status=503)
        
        # 请求后处理
        duration = time.time() - start_time
        
        # 添加性能头信息
        response['X-Response-Time'] = f"{duration:.3f}s"
        response['X-Server-Load'] = f"{concurrency_limiter.get_current_load():.1f}%"
        
        return response


def optimize_json_response(data: Any, status_code: int = 200) -> JsonResponse:
    """优化JSON响应"""
    # 移除None值以减少响应大小
    if isinstance(data, dict):
        data = {k: v for k, v in data.items() if v is not None}
    
    response = JsonResponse(data, status=status_code, json_dumps_params={
        'ensure_ascii': False,
        'separators': (',', ':')  # 紧凑格式
    })
    
    # 启用压缩
    response['Content-Encoding'] = 'gzip'
    
    return response


class BatchAPIProcessor:
    """批量API处理器"""
    
    @staticmethod
    def process_batch_requests(requests: List[Dict]) -> List[Dict]:
        """处理批量请求"""
        results = []
        
        for req in requests:
            try:
                # 这里可以根据请求类型分发到不同的处理函数
                result = BatchAPIProcessor._process_single_request(req)
                results.append({
                    'success': True,
                    'data': result,
                    'request_id': req.get('id')
                })
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'request_id': req.get('id')
                })
        
        return results
    
    @staticmethod
    def _process_single_request(request_data: Dict) -> Any:
        """处理单个请求"""
        # 根据请求类型处理
        request_type = request_data.get('type')
        
        if request_type == 'user_balance':
            return BatchAPIProcessor._get_user_balance(request_data.get('user_id'))
        elif request_type == 'lottery_draw':
            return BatchAPIProcessor._get_lottery_draw(request_data.get('draw_id'))
        else:
            raise ValueError(f"不支持的请求类型: {request_type}")
    
    @staticmethod
    def _get_user_balance(user_id: int) -> Dict:
        """获取用户余额"""
        from apps.core.cache_manager import UserCacheManager
        
        cached_balance = UserCacheManager.get_user_balance(user_id)
        if cached_balance:
            return cached_balance
        
        # 从数据库获取
        from apps.finance.models import UserBalance
        try:
            balance = UserBalance.objects.get(user_id=user_id)
            balance_data = {
                'main_balance': float(balance.main_balance),
                'bonus_balance': float(balance.bonus_balance),
                'frozen_balance': float(balance.frozen_balance)
            }
            
            # 缓存结果
            UserCacheManager.cache_user_balance(user_id, balance_data)
            return balance_data
        except UserBalance.DoesNotExist:
            return {'main_balance': 0, 'bonus_balance': 0, 'frozen_balance': 0}
    
    @staticmethod
    def _get_lottery_draw(draw_id: str) -> Dict:
        """获取彩票期次信息"""
        from apps.core.cache_manager import GameCacheManager
        
        cached_draw = GameCacheManager.get_lottery_draw(draw_id)
        if cached_draw:
            return cached_draw
        
        # 从数据库获取
        from apps.games.lottery11x5.models import LotteryDraw
        try:
            draw = LotteryDraw.objects.get(draw_number=draw_id)
            draw_data = {
                'draw_number': draw.draw_number,
                'draw_time': draw.draw_time.isoformat(),
                'status': draw.status,
                'winning_numbers': draw.winning_numbers
            }
            
            # 缓存结果
            GameCacheManager.cache_lottery_draw(draw_id, draw_data)
            return draw_data
        except LotteryDraw.DoesNotExist:
            raise ValueError(f"期次不存在: {draw_id}")


# 性能监控视图
def performance_stats_view(request):
    """性能统计视图"""
    stats = performance_monitor.get_stats()
    memory_usage = MemoryOptimizer.get_memory_usage()
    connection_stats = DatabaseConnectionOptimizer.get_connection_stats()
    
    return JsonResponse({
        'api_performance': stats,
        'memory_usage': memory_usage,
        'database_connections': connection_stats,
        'concurrent_requests': performance_monitor.concurrent_requests,
        'max_concurrent': performance_monitor.max_concurrent
    })