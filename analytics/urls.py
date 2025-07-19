"""
DiamondStream Analytics URLs

URL configuration for analytics-related API endpoints.
"""

from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Platform statistics
    path('platform-stats/', views.PlatformStatsListView.as_view(), name='platform-stats'),
    path('user-analytics/', views.UserAnalyticsListView.as_view(), name='user-analytics-list'),
    path('investment-analytics/', views.InvestmentAnalyticsListView.as_view(), name='investment-analytics'),
    path('system-performance/', views.SystemPerformanceListView.as_view(), name='system-performance'),
    path('payment-analytics/', views.PaymentAnalyticsListView.as_view(), name='payment-analytics'),
    
    # Dashboard analytics
    path('dashboard/', views.admin_dashboard_stats, name='admin-dashboard-stats'),
    path('user/', views.user_analytics, name='user-analytics'),
    path('metrics/', views.platform_metrics, name='platform-metrics'),
]
