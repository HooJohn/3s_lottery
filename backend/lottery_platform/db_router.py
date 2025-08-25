"""
数据库路由器 - 实现读写分离
"""

class DatabaseRouter:
    """
    数据库路由器，实现读写分离
    """
    
    def db_for_read(self, model, **hints):
        """读操作路由到从数据库"""
        return 'read_replica'
    
    def db_for_write(self, model, **hints):
        """写操作路由到主数据库"""
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """允许关系操作"""
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """只在主数据库执行迁移"""
        return db == 'default'