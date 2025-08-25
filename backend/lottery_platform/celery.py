"""
Celery配置 - 异步任务处理
"""

import os
from celery import Celery

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lottery_platform.settings')

app = Celery('lottery_platform')

# 从Django设置中加载配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')