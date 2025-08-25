"""
游戏模块URL配置
"""

from django.urls import path, include

app_name = 'games'

urlpatterns = [
    # 11选5彩票
    path('lottery11x5/', include('apps.games.lottery11x5.urls')),
]