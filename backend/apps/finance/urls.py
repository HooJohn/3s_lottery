"""
财务管理URL配置
"""

from django.urls import path
from .views import (
    UserBalanceView,
    BalanceOperationView,
    TransactionListView,
    TransactionDetailView,
    BalanceLogListView,
    BankAccountListCreateView,
    BankAccountDetailView,
    PaymentMethodListView,
    DepositRequestView,
    WithdrawRequestView,
    DepositStatusView,
    financial_summary,
    deposit_limits,
)
from .withdraw_views import (
    WithdrawLimitsView,
    WithdrawStatusView,
    WithdrawHistoryView,
    cancel_withdraw,
    withdraw_guide,
)
from .transaction_views import (
    TransactionAnalyticsView,
    BettingRecordsView,
    TransactionExportView,
    transaction_summary,
    turnover_stats,
)
from .payment_views import (
    paystack_callback,
    flutterwave_callback,
    mobile_money_callback,
    payment_success,
    payment_failed,
)

app_name = 'finance'

urlpatterns = [
    # 余额管理
    path('balance/', UserBalanceView.as_view(), name='balance'),
    path('balance/operation/', BalanceOperationView.as_view(), name='balance_operation'),
    path('balance/logs/', BalanceLogListView.as_view(), name='balance_logs'),
    
    # 交易记录
    path('transactions/', TransactionListView.as_view(), name='transactions'),
    path('transactions/<uuid:pk>/', TransactionDetailView.as_view(), name='transaction_detail'),
    path('transactions/analytics/', TransactionAnalyticsView.as_view(), name='transaction_analytics'),
    path('transactions/export/', TransactionExportView.as_view(), name='transaction_export'),
    path('transactions/summary/', transaction_summary, name='transaction_summary'),
    
    # 投注记录
    path('betting/records/', BettingRecordsView.as_view(), name='betting_records'),
    path('betting/turnover/', turnover_stats, name='turnover_stats'),
    
    # 银行账户管理
    path('bank-accounts/', BankAccountListCreateView.as_view(), name='bank_accounts'),
    path('bank-accounts/<uuid:pk>/', BankAccountDetailView.as_view(), name='bank_account_detail'),
    
    # 支付方式
    path('payment-methods/', PaymentMethodListView.as_view(), name='payment_methods'),
    
    # 存款提款
    path('deposit/', DepositRequestView.as_view(), name='deposit'),
    path('withdraw/', WithdrawRequestView.as_view(), name='withdraw'),
    
    # 财务概览
    path('summary/', financial_summary, name='summary'),
    
    # 存款相关
    path('deposit/status/', DepositStatusView.as_view(), name='deposit_status'),
    path('deposit/limits/', deposit_limits, name='deposit_limits'),
    
    # 提款相关
    path('withdraw/limits/', WithdrawLimitsView.as_view(), name='withdraw_limits'),
    path('withdraw/status/', WithdrawStatusView.as_view(), name='withdraw_status'),
    path('withdraw/history/', WithdrawHistoryView.as_view(), name='withdraw_history'),
    path('withdraw/cancel/', cancel_withdraw, name='cancel_withdraw'),
    path('withdraw/guide/', withdraw_guide, name='withdraw_guide'),
    
    # 支付回调
    path('paystack/callback/', paystack_callback, name='paystack_callback'),
    path('flutterwave/callback/', flutterwave_callback, name='flutterwave_callback'),
    path('mobile-money/callback/', mobile_money_callback, name='mobile_money_callback'),
    
    # 支付结果页面
    path('payment/success/', payment_success, name='payment_success'),
    path('payment/failed/', payment_failed, name='payment_failed'),
]