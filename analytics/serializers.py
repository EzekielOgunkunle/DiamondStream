"""
DiamondStream Analytics Serializers

Serializers for analytics-related API endpoints including platform statistics,
user analytics, and performance metrics.
"""

from rest_framework import serializers
from django.utils import timezone
from .models import (
    PlatformStats, UserAnalytics, InvestmentAnalytics, 
    PaymentAnalytics, SystemPerformance
)


class PlatformStatsSerializer(serializers.ModelSerializer):
    """Serializer for platform statistics."""
    
    class Meta:
        model = PlatformStats
        fields = [
            'id', 'date', 'total_users', 'new_users', 'active_users',
            'total_investments', 'new_investments', 'total_investment_amount',
            'total_payouts', 'payout_amount', 'platform_revenue',
            'conversion_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for user analytics."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserAnalytics
        fields = [
            'id', 'user_email', 'date', 'page_views', 'session_duration',
            'login_count', 'investments_viewed', 'investments_created',
            'last_activity', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvestmentAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for investment analytics."""
    
    investment_plan_name = serializers.CharField(source='investment_plan.name', read_only=True)
    
    class Meta:
        model = InvestmentAnalytics
        fields = [
            'id', 'date', 'investment_plan_name', 'total_investments',
            'total_amount', 'avg_investment_amount', 'successful_investments',
            'failed_investments', 'total_returns', 'avg_roi', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SystemPerformanceSerializer(serializers.ModelSerializer):
    """Serializer for system performance analytics."""
    
    class Meta:
        model = SystemPerformance
        fields = [
            'id', 'date', 'cpu_usage', 'memory_usage', 'disk_usage',
            'response_time', 'error_rate', 'uptime', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for payment analytics."""
    
    class Meta:
        model = PaymentAnalytics
        fields = [
            'id', 'date', 'currency', 'total_payments', 'total_amount',
            'avg_payment_amount', 'successful_payments', 'failed_payments',
            'pending_payments', 'success_rate', 'avg_confirmation_time',
            'total_fees', 'avg_fee_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for admin dashboard statistics."""
    
    # User metrics
    total_users = serializers.IntegerField()
    new_users_today = serializers.IntegerField()
    active_users_today = serializers.IntegerField()
    
    # Investment metrics
    total_investments = serializers.IntegerField()
    new_investments_today = serializers.IntegerField()
    total_investment_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    
    # Payment metrics
    pending_payments = serializers.IntegerField()
    verified_payments_today = serializers.IntegerField()
    total_payment_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    
    # Payout metrics
    pending_payouts = serializers.IntegerField()
    completed_payouts_today = serializers.IntegerField()
    total_payout_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    
    # Platform metrics
    platform_revenue = serializers.DecimalField(max_digits=20, decimal_places=2)
    conversion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)


class UserAnalyticsSerializer(serializers.Serializer):
    """Serializer for user-specific analytics."""
    
    # Investment metrics
    total_investments = serializers.IntegerField()
    active_investments = serializers.IntegerField()
    completed_investments = serializers.IntegerField()
    total_invested = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_returns = serializers.DecimalField(max_digits=20, decimal_places=2)
    avg_roi = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Activity metrics
    days_active = serializers.IntegerField()
    last_login = serializers.DateTimeField()
    last_investment = serializers.DateTimeField()
    
    # Referral metrics
    referrals_made = serializers.IntegerField()
    referral_earnings = serializers.DecimalField(max_digits=20, decimal_places=2)


class PlatformMetricsSerializer(serializers.Serializer):
    """Serializer for comprehensive platform metrics."""
    
    # Time period
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    
    # Growth metrics
    user_growth_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    investment_growth_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    revenue_growth_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Performance metrics
    user_retention_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    investment_completion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    payment_success_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Financial metrics
    average_investment_size = serializers.DecimalField(max_digits=20, decimal_places=2)
    lifetime_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    cost_per_acquisition = serializers.DecimalField(max_digits=20, decimal_places=2)
