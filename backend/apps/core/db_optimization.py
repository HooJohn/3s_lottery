# -*- coding: utf-8 -*-
"""
数据库查询优化和索引配置
支持10万+用户的高性能数据库优化方案
"""

from django.db import models, connection
from django.core.cache import cache
from django.conf import settings
import logging
from typing import Dict, List, Any, Optional
from functools import wraps
import time

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """数据库优化器"""
    
    @staticmethod
    def create_indexes():
        """创建性能优化索引"""
        indexes = [
            # 用户相关索引
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_phone_active ON users_user(phone, is_active);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_vip_turnover ON users_user(vip_level, total_turnover);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_referral_code ON users_user(referral_code);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_country_active ON users_user(country, is_active);",
            
            # 交易记录索引
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_user_time ON finance_transaction(user_id, created_at DESC);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_type_status ON finance_transaction(type, status);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_amount_time ON finance_transaction(amount, created_at);",
            
            # 投注记录索引
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_lottery_bets_user_draw ON games_lottery11x5_lotterybet(user_id, draw_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_lottery_bets_draw_time ON games_lottery11x5_lotterybet(draw_id, created_at);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_lottery_bets_status ON games_lottery11x5_lotterybet(status);",
            
            # 余额记录索引
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_balance_updated ON finance_userbalance(updated_at);",
            
            # 奖励记录索引
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_rewards_user_type ON rewards_reward(user_id, reward_type);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_rewards_created_at ON rewards_reward(created_at DESC);",
            
            # 复合索引优化
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_vip_country ON users_user(vip_level, country) WHERE is_active = true;",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_user_type_time ON finance_transaction(user_id, type, created_at DESC);",
        ]
        
        with connection.cursor() as cursor:
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    logger.info(f"创建索引成功: {index_sql[:50]}...")
                except Exception as e:
                    logger.error(f"创建索引失败: {e}")
    
    @staticmethod
    def analyze_slow_queries():
        """分析慢查询"""
        slow_queries = []
        
        with connection.cursor() as cursor:
            # PostgreSQL慢查询分析
            cursor.execute("""
                SELECT query, calls, total_time, mean_time, rows
                FROM pg_stat_statements 
                WHERE mean_time > 100 
                ORDER BY mean_time DESC 
                LIMIT 10;
            """)
            
            for row in cursor.fetchall():
                slow_queries.append({
                    'query': row[0][:100],
                    'calls': row[1],
                    'total_time': row[2],
                    'mean_time': row[3],
                    'rows': row[4]
                })
        
        return slow_queries
    
    @staticmethod
    def optimize_table_statistics():
        """优化表统计信息"""
        tables = [
            'users_user',
            'finance_transaction', 
            'finance_userbalance',
            'games_lottery11x5_lotterybet',
            'rewards_reward'
        ]
        
        with connection.cursor() as cursor:
            for table in tables:
                try:
                    cursor.execute(f"ANALYZE {table};")
                    logger.info(f"优化表统计信息: {table}")
                except Exception as e:
                    logger.error(f"优化表统计信息失败 {table}: {e}")


class QueryOptimizer:
    """查询优化器"""
    
    @staticmethod
    def get_user_with_balance(user_id: int):
        """优化的用户余额查询"""
        from apps.users.models import User
        from apps.finance.models import UserBalance
        
        cache_key = f'user_balance_{user_id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            user = User.objects.select_related('userbalance').get(id=user_id)
            data = {
                'user': user,
                'balance': user.userbalance,
                'total_balance': user.userbalance.get_total_balance()
            }
            cache.set(cache_key, data, 300)  # 缓存5分钟
            return data
        except (User.DoesNotExist, UserBalance.DoesNotExist):
            return None
    
    @staticmethod
    def get_user_transactions(user_id: int, limit: int = 50, transaction_type: str = None):
        """优化的交易记录查询"""
        from apps.finance.models import Transaction
        
        cache_key = f'user_transactions_{user_id}_{transaction_type}_{limit}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        queryset = Transaction.objects.filter(user_id=user_id)\
                                    .select_related('user')\
                                    .order_by('-created_at')
        
        if transaction_type:
            queryset = queryset.filter(type=transaction_type)
        
        transactions = list(queryset[:limit])
        cache.set(cache_key, transactions, 180)  # 缓存3分钟
        return transactions
    
    @staticmethod
    def get_lottery_stats():
        """优化的彩票统计查询"""
        from django.db.models import Count, Sum, Avg
        from apps.games.lottery11x5.models import LotteryBet
        
        cache_key = 'lottery_stats'
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return cached_stats
        
        stats = LotteryBet.objects.aggregate(
            total_bets=Count('id'),
            total_amount=Sum('amount'),
            total_winnings=Sum('actual_win'),
            avg_bet=Avg('amount')
        )
        
        cache.set(cache_key, stats, 600)  # 缓存10分钟
        return stats
    
    @staticmethod
    def get_vip_user_distribution():
        """VIP用户分布统计"""
        from django.db.models import Count
        from apps.users.models import User
        
        cache_key = 'vip_distribution'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        distribution = User.objects.filter(is_active=True)\
                                 .values('vip_level')\
                                 .annotate(count=Count('id'))\
                                 .order_by('vip_level')
        
        result = list(distribution)
        cache.set(cache_key, result, 1800)  # 缓存30分钟
        return result


def query_performance_monitor(func):
    """查询性能监控装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # 记录查询前的数据库连接数
        queries_before = len(connection.queries)
        
        result = func(*args, **kwargs)
        
        # 计算执行时间和查询数量
        execution_time = time.time() - start_time
        queries_count = len(connection.queries) - queries_before
        
        # 记录慢查询
        if execution_time > 0.5:  # 超过500ms的查询
            logger.warning(
                f"慢查询检测: {func.__name__} "
                f"执行时间: {execution_time:.3f}s "
                f"查询数量: {queries_count}"
            )
        
        return result
    return wrapper


class ConnectionPoolOptimizer:
    """数据库连接池优化"""
    
    @staticmethod
    def get_optimized_db_config():
        """获取优化的数据库配置"""
        return {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': settings.DATABASES['default']['NAME'],
                'USER': settings.DATABASES['default']['USER'],
                'PASSWORD': settings.DATABASES['default']['PASSWORD'],
                'HOST': settings.DATABASES['default']['HOST'],
                'PORT': settings.DATABASES['default']['PORT'],
                'OPTIONS': {
                    'MAX_CONNS': 100,  # 最大连接数
                    'CONN_MAX_AGE': 600,  # 连接最大存活时间(秒)
                    'CONN_HEALTH_CHECKS': True,  # 连接健康检查
                    'OPTIONS': {
                        '-c default_transaction_isolation=read committed',
                        '-c timezone=UTC',
                        '-c shared_preload_libraries=pg_stat_statements',
                    }
                },
                'ATOMIC_REQUESTS': True,  # 原子请求
                'AUTOCOMMIT': True,
            },
            # 读写分离配置
            'read_replica': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': settings.DATABASES['default']['NAME'],
                'USER': settings.DATABASES['default']['USER'],
                'PASSWORD': settings.DATABASES['default']['PASSWORD'],
                'HOST': settings.DATABASES.get('read_replica', {}).get('HOST', 
                                             settings.DATABASES['default']['HOST']),
                'PORT': settings.DATABASES['default']['PORT'],
                'OPTIONS': {
                    'MAX_CONNS': 50,
                    'CONN_MAX_AGE': 300,
                    'CONN_HEALTH_CHECKS': True,
                },
            }
        }
    
    @staticmethod
    def monitor_connections():
        """监控数据库连接"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    count(*) as total_connections,
                    count(*) FILTER (WHERE state = 'active') as active_connections,
                    count(*) FILTER (WHERE state = 'idle') as idle_connections
                FROM pg_stat_activity 
                WHERE datname = current_database();
            """)
            
            result = cursor.fetchone()
            return {
                'total_connections': result[0],
                'active_connections': result[1], 
                'idle_connections': result[2]
            }


class BatchProcessor:
    """批量处理优化器"""
    
    @staticmethod
    def bulk_create_optimized(model_class, objects: List[Any], batch_size: int = 1000):
        """优化的批量创建"""
        total_created = 0
        
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            try:
                model_class.objects.bulk_create(batch, ignore_conflicts=True)
                total_created += len(batch)
                logger.info(f"批量创建 {len(batch)} 条记录")
            except Exception as e:
                logger.error(f"批量创建失败: {e}")
        
        return total_created
    
    @staticmethod
    def bulk_update_optimized(model_class, objects: List[Any], fields: List[str], batch_size: int = 1000):
        """优化的批量更新"""
        total_updated = 0
        
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            try:
                model_class.objects.bulk_update(batch, fields, batch_size=batch_size)
                total_updated += len(batch)
                logger.info(f"批量更新 {len(batch)} 条记录")
            except Exception as e:
                logger.error(f"批量更新失败: {e}")
        
        return total_updated