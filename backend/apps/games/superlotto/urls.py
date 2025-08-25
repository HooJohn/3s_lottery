"""
大乐透彩票URL配置
"""

from django.urls import path
from . import views

app_name = 'superlotto'

urlpatterns = [
    # 游戏信息
    path('info/', views.game_info, name='game_info'),
    
    # 期次信息
    path('current-draw/', views.current_draw, name='current_draw'),
    path('draw/<str:draw_number>/', views.draw_info, name='draw_info'),
    path('latest-draws/', views.latest_draws, name='latest_draws'),
    
    # 投注相关
    path('calculate-bet/', views.calculate_bet, name='calculate_bet'),
    path('place-bet/', views.place_bet, name='place_bet'),
    path('user-bets/', views.user_bets, name='user_bets'),
    
    # 工具功能
    path('random-numbers/', views.random_numbers, name='random_numbers'),
    path('validate-numbers/', views.validate_numbers, name='validate_numbers'),
    
    # 管理员开奖功能
    path('admin/generate-draw-numbers/', views.generate_draw_numbers, name='generate_draw_numbers'),
    path('admin/conduct-draw/', views.conduct_draw, name='conduct_draw'),
    path('admin/create-next-draw/', views.create_next_draw, name='create_next_draw'),
    path('admin/close-draw-sales/', views.close_draw_sales, name='close_draw_sales'),
]