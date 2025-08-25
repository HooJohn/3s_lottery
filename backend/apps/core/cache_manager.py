# -*- coding: utf-8 -*-
"""
Redis缓存管理器
多层缓存策略实现
"""

from django.core.cache import cache, caches
from django.conf import settings
import redis
import json
import hashlib
import logging
from typing import Any, Dict, List, Optional, Union
from functools import wraps
import time

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器"""
    
    # 缓存键前缀
    USER_PREFIX = 'user'
    GAME_PREFIX = 'game'
    FINANCE_PREFIX = 'finance'
    SYSTEM_PREFIX = 'system'
    API_PREFIX = 'api'
    
    # 缓存超时时间(秒)
    CACHE_TIMEOUTS = {
        'user_session': 3600,      # 用户会话 1小时
        'user_balance': 300,       # 用户余额 5分钟
        'user_profile': 1800,      # 用户资料 30分钟
        'game_config': 3600,       # 游戏配置 1小时
        'lottery_draw': 600,       # 彩票期次 10分钟
        'api_response': 180,       # API响应 3分钟
        'system_config': 7200,     # 系统配置 2小时
        'vip_levels': 3600,        # VIP等级 1小时
        'hot_data': 60,            # 热点数据 1分钟
    }
    
    @classmethod
    def get_cache_key(cls, prefix: str, *args) -> str:
        """生成缓存键"""
        key_parts = [prefix] + [str(arg) for arg in args]
        return ':'.join(key_parts)
    
    @classmethod
    def set_cache(cls, key: str, value: Any, timeout: Optional[int] = None, cache_type: str = 'default') -> bool:
        """设置缓存"""
        try:
            cache_instance = caches[cache_type] if cache_type != 'default' else cache
            
            # 序列化复杂对象
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            cache_instance.set(key, value, timeout)
            return True
        except Exception as e:
            logger.error(f"设置缓存失败 {key}: {e}")
            return False
    
    @classmethod
    def get_cache(cls, key: str, cache_type: str = 'default') -> Any:
        """获取缓存"""
        try:
            cache_instance = caches[cache_type] if cache_type != 'default' else cache
            value = cache_instance.get(key)
            
            # 尝试反序列化JSON
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            
            return value
        except Exception as e:
            logger.error(f"获取缓存失败 {key}: {e}")
            return None
    
    @classmethod
    def delete_cache(cls, key: str, cache_type: str = 'default') -> bool:
        """删除缓存"""
        try:
            cache_instance = caches[cache_type] if cache_type != 'default' else cache
            cache_instance.delete(key)
            return True
        except Exception as e:
            logger.error(f"删除缓存失败 {key}: {e}")
            return False
    
    @classmethod
    def clear_pattern(cls, pattern: str, cache_type: str = 'default') -> int:
        """按模式清除缓存"""
        try:
            cache_instance = caches[cache_type] if cache_type != 'default' else cache
            
            if hasattr(cache_instance, 'delete_pattern'):
                return cache_instance.delete_pattern(pattern)
            else:
                # 手动实现模式删除
                redis_client = cache_instance._cache.get_client()
                keys = redis_client.keys(pattern)
                if keys:
                    return redis_client.delete(*keys)
                return 0
        except Exception as e:
            logger.error(f"按模式清除缓存失败 {pattern}: {e}")
            return 0


class UserCacheManager(CacheManager):
    """用户缓存管理器"""
    
    @classmethod
    def cache_user_balance(cls, user_id: int, balance_data: Dict) -> bool:
        """缓存用户余额"""
        key = cls.get_cache_key(cls.USER_PREFIX, user_id, 'balance')
        return cls.set_cache(key, balance_data, cls.CACHE_TIMEOUTS['user_balance'])
    
    @classmethod
    def get_user_balance(cls, user_id: int) -> Optional[Dict]:
        """获取用户余额缓存"""
        key = cls.get_cache_key(cls.USER_PREFIX, user_id, 'balance')
        return cls.get_cache(key)
    
    @classmethod
    def cache_user_profile(cls, user_id: int, profile_data: Dict) -> bool:
        """缓存用户资料"""
        key = cls.get_cache_key(cls.USER_PREFIX, user_id, 'profile')
        return cls.set_cache(key, profile_data, cls.CACHE_TIMEOUTS['user_profile'])
    
    @classmethod
    def get_user_profile(cls, user_id: int) -> Optional[Dict]:
        """获取用户资料缓存"""
        key = cls.get_cache_key(cls.USER_PREFIX, user_id, 'profile')
        return cls.get_cache(key)
    
    @classmethod
    def cache_user_vip_status(cls, user_id: int, vip_data: Dict) -> bool:
        """缓存用户VIP状态"""
        key = cls.get_cache_key(cls.USER_PREFIX, user_id, 'vip')
        return cls.set_cache(key, vip_data, cls.CACHE_TIMEOUTS['vip_levels'])
    
    @classmethod
    def invalidate_user_cache(cls, user_id: int) -> None:
        """清除用户相关缓存"""
        patterns = [
            f"{cls.USER_PREFIX}:{user_id}:*",
            f"{cls.FINANCE_PREFIX}:{user_id}:*"
        ]
        
        for pattern in patterns:
            cls.clear_pattern(pattern)


class GameCacheManager(CacheManager):
    """游戏缓存管理器"""
    
    @classmethod
    def cache_lottery_draw(cls, draw_id: str, draw_data: Dict) -> bool:
        """缓存彩票期次信息"""
        key = cls.get_cache_key(cls.GAME_PREFIX, 'lottery', draw_id)
        return cls.set_cache(key, draw_data, cls.CACHE_TIMEOUTS['lottery_draw'])
    
    @classmethod
    def get_lottery_draw(cls, draw_id: str) -> Optional[Dict]:
        """获取彩票期次缓存"""
        key = cls.get_cache_key(cls.GAME_PREFIX, 'lottery', draw_id)
        return cls.get_cache(key)
    
    @classmethod
    def cache_game_config(cls, game_type: str, config_data: Dict) -> bool:
        """缓存游戏配置"""
        key = cls.get_cache_key(cls.GAME_PREFIX, 'config', game_type)
        return cls.set_cache(key, config_data, cls.CACHE_TIMEOUTS['game_config'])
    
    @classmethod
    def cache_hot_numbers(cls, game_type: str, numbers_data: List) -> bool:
        """缓存热门号码"""
        key = cls.get_cache_key(cls.GAME_PREFIX, 'hot_numbers', game_type)
        return cls.set_cache(key, numbers_data, cls.CACHE_TIMEOUTS['hot_data'])


class APICacheManager(CacheManager):
    """API缓存管理器"""
    
    @classmethod
    def generate_api_cache_key(cls, request_path: str, query_params: Dict) -> str:
        """生成API缓存键"""
        # 创建查询参数的哈希
        params_str = json.dumps(query_params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        
        return cls.get_cache_key(cls.API_PREFIX, request_path.replace('/', '_'), params_hash)
    
    @classmethod
    def cache_api_response(cls, request_path: str, query_params: Dict, response_data: Any) -> bool:
        """缓存API响应"""
        key = cls.generate_api_cache_key(request_path, query_params)
        return cls.set_cache(key, response_data, cls.CACHE_TIMEOUTS['api_response'])
    
    @classmethod
    def get_api_response(cls, request_path: str, query_params: Dict) -> Any:
        """获取API响应缓存"""
        key = cls.generate_api_cache_key(request_path, query_params)
        return cls.get_cache(key)


def cache_api_response(timeout: int = 180, cache_type: str = 'default'):
    """API响应缓存装饰器"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # 只缓存GET请求
            if request.method != 'GET':
                return view_func(request, *args, **kwargs)
            
            # 生成缓存键
            cache_key = APICacheManager.generate_api_cache_key(
                request.path, 
                dict(request.GET.items())
            )
            
            # 尝试从缓存获取
            cached_response = APICacheManager.get_cache(cache_key, cache_type)
            if cached_response:
                logger.debug(f"API缓存命中: {request.path}")
                return cached_response
            
            # 执行视图函数
            response = view_func(request, *args, **kwargs)
            
            # 缓存成功响应
            if hasattr(response, 'status_code') and response.status_code == 200:
                APICacheManager.set_cache(cache_key, response, timeout, cache_type)
                logger.debug(f"API响应已缓存: {request.path}")
            
            return response
        return wrapper
    return decorator


class RedisClusterManager:
    """Redis集群管理器"""
    
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.CACHES['default']['LOCATION'])
    
    def get_cluster_info(self) -> Dict:
        """获取Redis集群信息"""
        try:
            info = self.redis_client.info()
            return {
                'redis_version': info.get('redis_version'),
                'used_memory': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_commands_processed': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits'),
                'keyspace_misses': info.get('keyspace_misses'),
                'hit_rate': self._calculate_hit_rate(info)
            }
        except Exception as e:
            logger.error(f"获取Redis信息失败: {e}")
            return {}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """计算缓存命中率"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return round((hits / total) * 100, 2)
    
    def monitor_memory_usage(self) -> Dict:
        """监控内存使用情况"""
        try:
            info = self.redis_client.info('memory')
            return {
                'used_memory': info.get('used_memory'),
                'used_memory_human': info.get('used_memory_human'),
                'used_memory_peak': info.get('used_memory_peak'),
                'used_memory_peak_human': info.get('used_memory_peak_human'),
                'mem_fragmentation_ratio': info.get('mem_fragmentation_ratio')
            }
        except Exception as e:
            logger.error(f"监控Redis内存失败: {e}")
            return {}
    
    def cleanup_expired_keys(self) -> int:
        """清理过期键"""
        try:
            # 获取所有键的数量
            total_keys = self.redis_client.dbsize()
            
            # 执行过期键清理
            self.redis_client.execute_command('MEMORY', 'PURGE')
            
            # 返回清理后的键数量差异
            remaining_keys = self.redis_client.dbsize()
            return total_keys - remaining_keys
        except Exception as e:
            logger.error(f"清理过期键失败: {e}")
            return 0


class CacheWarmer:
    """缓存预热器"""
    
    @staticmethod
    def warm_user_cache(user_id: int):
        """预热用户缓存"""
        from apps.users.models import User
        from apps.finance.models import UserBalance
        
        try:
            # 预热用户基本信息
            user = User.objects.select_related('userbalance').get(id=user_id)
            
            profile_data = {
                'id': user.id,
                'username': user.username,
                'phone': user.phone,
                'vip_level': user.vip_level,
                'total_turnover': float(user.total_turnover)
            }
            UserCacheManager.cache_user_profile(user_id, profile_data)
            
            # 预热用户余额
            balance_data = {
                'main_balance': float(user.userbalance.main_balance),
                'bonus_balance': float(user.userbalance.bonus_balance),
                'frozen_balance': float(user.userbalance.frozen_balance)
            }
            UserCacheManager.cache_user_balance(user_id, balance_data)
            
            logger.info(f"用户缓存预热完成: {user_id}")
            
        except Exception as e:
            logger.error(f"用户缓存预热失败 {user_id}: {e}")
    
    @staticmethod
    def warm_game_cache():
        """预热游戏缓存"""
        from apps.games.lottery11x5.models import LotteryDraw
        
        try:
            # 预热当前期次信息
            current_draw = LotteryDraw.objects.filter(status='OPEN').first()
            if current_draw:
                draw_data = {
                    'draw_number': current_draw.draw_number,
                    'draw_time': current_draw.draw_time.isoformat(),
                    'close_time': current_draw.close_time.isoformat(),
                    'status': current_draw.status
                }
                GameCacheManager.cache_lottery_draw(current_draw.draw_number, draw_data)
            
            logger.info("游戏缓存预热完成")
            
        except Exception as e:
            logger.error(f"游戏缓存预热失败: {e}")