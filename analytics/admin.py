"""
DiamondStream Analytics Admin

Django admin configuration for analytics and reporting.
"""

from django.contrib import admin
from .models import (
    PlatformStats, UserAnalytics, InvestmentAnalytics, PaymentAnalytics,
    SystemPerformance, ConversionFunnel, EventTracking
)


@admin.register(PlatformStats)
class PlatformStatsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_users', 'new_users', 'total_investments', 'daily_investment_volume']
    list_filter = ['date']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'


@admin.register(UserAnalytics)
class UserAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_investments', 'total_invested_amount', 'roi_percentage', 'risk_score']
    list_filter = ['preferred_plan_type', 'risk_score']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(InvestmentAnalytics)
class InvestmentAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'plan_type', 'total_investments', 'total_amount', 'success_rate']
    list_filter = ['date', 'plan_type']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PaymentAnalytics)
class PaymentAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'currency', 'total_payments', 'total_amount', 'success_rate']
    list_filter = ['date', 'currency']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SystemPerformance)
class SystemPerformanceAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'cpu_usage', 'memory_usage', 'active_sessions', 'error_count']
    list_filter = ['timestamp']
    readonly_fields = ['created_at']


@admin.register(ConversionFunnel)
class ConversionFunnelAdmin(admin.ModelAdmin):
    list_display = ['date', 'visitors', 'registrations', 'first_investments', 'investment_rate']
    list_filter = ['date']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EventTracking)
class EventTrackingAdmin(admin.ModelAdmin):
    list_display = ['event_name', 'event_category', 'user', 'timestamp']
    list_filter = ['event_category', 'event_name', 'timestamp']
    search_fields = ['event_name', 'user__email']
    readonly_fields = ['created_at']
