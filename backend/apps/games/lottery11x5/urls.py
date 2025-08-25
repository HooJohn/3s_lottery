"""
11选5彩票游戏URL配置
"""

from django.urls import path
from . import views

app_name = 'lottery11x5'

urlpatterns = [
    # 游戏信息
    path('info/', views.game_info, name='game_info'),
    
    # 期次管理
    path('current-draw/', views.current_draw, name='current_draw'),
    
    # 开奖结果
    path('recent-results/', views.recent_results, name='recent_results'),
    
    # 冷热号码
    path('hot-cold-numbers/', views.hot_cold_numbers, name='hot_cold_numbers'),
    
    # 投注相关
    path('place-bet/', views.place_bet, name='place_bet'),
    path('bet-history/', views.bet_history, name='bet_history'),
    
    # 购彩篮功能
    path('cart/', views.get_cart, name='get_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<str:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<str:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/place-bets/', views.place_cart_bets, name='place_cart_bets'),
    
    # 快捷选号
    path('quick-pick/options/', views.quick_pick_options, name='quick_pick_options'),
    path('quick-pick/numbers/', views.quick_pick_numbers, name='quick_pick_numbers'),
    
    # 投注计算和预览
    path('calculate-bet/', views.calculate_bet, name='calculate_bet'),
    
    # 用户常用号码
    path('favorite-numbers/', views.user_favorite_numbers, name='user_favorite_numbers'),
    path('favorite-numbers/save/', views.save_favorite_numbers, name='save_favorite_numbers'),
    
    # 工具功能
    path('random-numbers/', views.generate_random_numbers, name='random_numbers'),
    
    # 走势分析
    path('trend-analysis/', views.trend_analysis, name='trend_analysis'),
    path('position-trend/<int:position>/', views.position_trend, name='position_trend'),
    path('missing-analysis/', views.missing_analysis, name='missing_analysis'),
    path('complete-trend-chart/', views.complete_trend_chart, name='complete_trend_chart'),
    path('prediction-analysis/', views.prediction_analysis, name='prediction_analysis'),
    path('number-statistics/', views.number_statistics, name='number_statistics'),
    
    # 开奖验证和结算
    path('verify-draw/<str:draw_id>/', views.verify_draw_result, name='verify_draw_result'),
    path('settlement/<str:draw_id>/', views.draw_settlement_details, name='draw_settlement_details'),
    
    # 管理员接口
    path('admin/draw-lottery/', views.admin_draw_lottery, name='admin_draw_lottery'),
    path('admin/force-draw/', views.admin_force_draw, name='admin_force_draw'),
    path('admin/create-draws/', views.admin_create_draws, name='admin_create_draws'),
    path('admin/close-draws/', views.admin_close_draws, name='admin_close_draws'),
    path('admin/profit-analysis/', views.profit_analysis, name='profit_analysis'),
]