"""
体育博彩URL配置
"""

from django.urls import path
from . import views

app_name = 'sports'

urlpatterns = [
    # 平台信息
    path('providers/', views.providers_list, name='providers_list'),
    path('provider/<str:provider_code>/', views.provider_detail, name='provider_detail'),
    
    # 钱包管理
    path('wallets/', views.user_wallets, name='user_wallets'),
    path('wallet/<str:provider_code>/', views.wallet_detail, name='wallet_detail'),
    path('wallet/transactions/', views.wallet_transactions, name='wallet_transactions'),
    
    # 转账功能
    path('transfer/to-platform/', views.transfer_to_platform, name='transfer_to_platform'),
    path('transfer/from-platform/', views.transfer_from_platform, name='transfer_from_platform'),
    
    # 平台启动
    path('launch/', views.get_launch_url, name='get_launch_url'),
    
    # 同步功能
    path('sync/balance/', views.sync_wallet_balance, name='sync_wallet_balance'),
    
    # 自动转账功能
    path('auto-transfer/enter/', views.auto_transfer_on_enter, name='auto_transfer_on_enter'),
    path('auto-transfer/exit/', views.auto_transfer_on_exit, name='auto_transfer_on_exit'),
    path('batch-recover/', views.batch_recover_wallets, name='batch_recover_wallets'),
    
    # 投注记录聚合
    path('bet-records/', views.aggregated_bet_records, name='aggregated_bet_records'),
    path('user-statistics/', views.user_sports_statistics, name='user_sports_statistics'),
    
    # 单钱包模式检查
    path('check-single-wallet/<str:provider_code>/', views.check_single_wallet_mode, name='check_single_wallet_mode'),
    
    # 管理员功能
    path('admin/sync-bet-records/', views.sync_bet_records, name='sync_bet_records'),
]