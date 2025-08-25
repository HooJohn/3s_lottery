"""
666刮刮乐游戏URL配置
"""

from django.urls import path
from . import views

app_name = 'scratch666'

urlpatterns = [
    # 游戏信息
    path('info/', views.game_info, name='game_info'),
    path('product-info/', views.product_info, name='product_info'),
    
    # 核心功能
    path('purchase/', views.purchase_card, name='purchase_card'),
    path('scratch-area/', views.scratch_area, name='scratch_area'),
    path('scratch-all/', views.scratch_all, name='scratch_all'),
    path('auto-scratch/', views.auto_scratch, name='auto_scratch'),
    
    # 用户功能
    path('my-cards/', views.user_cards, name='user_cards'),
    path('my-statistics/', views.user_statistics, name='user_statistics'),
    path('preferences/', views.update_preferences, name='update_preferences'),
    path('participation-records/', views.participation_records, name='participation_records'),
    
    # 统计信息
    path('statistics/', views.game_statistics, name='game_statistics'),
    
    # 管理员接口
    path('admin/statistics/', views.admin_statistics, name='admin_statistics'),
    path('admin/config/', views.admin_update_config, name='admin_update_config'),
]