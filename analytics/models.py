"""
DiamondStream Analytics Models

Models for tracking platform analytics, user behavior, and business metrics.
Supports admin dashboard analytics and performance monitoring.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()


class PlatformStats(models.Model):
    """
    Daily platform statistics for dashboard analytics.
    Aggregated data for performance monitoring.
    """
    
    date = models.DateField(unique=True)
    
    # User metrics
    total_users = models.PositiveIntegerField(default=0)
    new_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    verified_users = models.PositiveIntegerField(default=0)
    
    # Investment metrics
    total_investments = models.PositiveIntegerField(default=0)
    new_investments = models.PositiveIntegerField(default=0)
    active_investments = models.PositiveIntegerField(default=0)
    matured_investments = models.PositiveIntegerField(default=0)
    
    # Financial metrics
    total_investment_volume = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    daily_investment_volume = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    total_payouts = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    daily_payouts = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    
    # Platform metrics
    total_revenue = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    daily_revenue = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    referral_commissions = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    
    # Payment metrics
    successful_payments = models.PositiveIntegerField(default=0)
    failed_payments = models.PositiveIntegerField(default=0)
    pending_payments = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'platform_stats'
        verbose_name = 'Platform Statistics'
        verbose_name_plural = 'Platform Statistics'
        indexes = [
            models.Index(fields=['date']),
        ]
        ordering = ['-date']
    
    def __str__(self):
        return f"Platform Stats - {self.date}"


class UserAnalytics(models.Model):
    """
    Individual user analytics and behavior tracking.
    Helps understand user engagement patterns.
    """
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='analytics')
    
    # Engagement metrics
    total_logins = models.PositiveIntegerField(default=0)
    last_login_date = models.DateTimeField(null=True, blank=True)
    session_count = models.PositiveIntegerField(default=0)
    avg_session_duration = models.DurationField(null=True, blank=True)
    
    # Investment behavior
    total_investments = models.PositiveIntegerField(default=0)
    total_invested_amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    avg_investment_amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    preferred_plan_type = models.CharField(max_length=20, blank=True)
    
    # Financial metrics
    total_returns = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    total_profit = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    roi_percentage = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Referral metrics
    total_referrals = models.PositiveIntegerField(default=0)
    successful_referrals = models.PositiveIntegerField(default=0)
    referral_earnings = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    
    # Platform usage
    kyc_completion_date = models.DateTimeField(null=True, blank=True)
    first_investment_date = models.DateTimeField(null=True, blank=True)
    last_investment_date = models.DateTimeField(null=True, blank=True)
    
    # Risk profile
    risk_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        help_text="User risk score based on behavior (0-100)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_analytics'
        verbose_name = 'User Analytics'
        verbose_name_plural = 'User Analytics'
        indexes = [
            models.Index(fields=['total_invested_amount']),
            models.Index(fields=['roi_percentage']),
            models.Index(fields=['risk_score']),
        ]
    
    def __str__(self):
        return f"{self.user.email} Analytics"
    
    def calculate_roi(self):
        """Calculate user's overall ROI percentage."""
        if self.total_invested_amount > 0:
            self.roi_percentage = ((self.total_returns - self.total_invested_amount) / self.total_invested_amount) * 100
            self.save(update_fields=['roi_percentage'])


class InvestmentAnalytics(models.Model):
    """
    Analytics for investment plans and performance.
    Tracks plan popularity and success rates.
    """
    
    date = models.DateField()
    plan_type = models.CharField(max_length=20)
    
    # Investment metrics
    total_investments = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    avg_investment_size = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    
    # Completion metrics
    matured_investments = models.PositiveIntegerField(default=0)
    paid_investments = models.PositiveIntegerField(default=0)
    cancelled_investments = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_completion_time = models.DurationField(null=True, blank=True)
    
    # User metrics
    unique_investors = models.PositiveIntegerField(default=0)
    repeat_investors = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'investment_analytics'
        verbose_name = 'Investment Analytics'
        verbose_name_plural = 'Investment Analytics'
        unique_together = ['date', 'plan_type']
        indexes = [
            models.Index(fields=['date', 'plan_type']),
        ]
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date} - {self.plan_type} Analytics"


class PaymentAnalytics(models.Model):
    """
    Analytics for payment processing and cryptocurrency trends.
    """
    
    date = models.DateField()
    currency = models.CharField(max_length=10)
    
    # Payment volume
    total_payments = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    avg_payment_amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    
    # Processing metrics
    successful_payments = models.PositiveIntegerField(default=0)
    failed_payments = models.PositiveIntegerField(default=0)
    pending_payments = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_confirmation_time = models.DurationField(null=True, blank=True)
    
    # Fee metrics
    total_fees = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    avg_fee_percentage = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_analytics'
        verbose_name = 'Payment Analytics'
        verbose_name_plural = 'Payment Analytics'
        unique_together = ['date', 'currency']
        indexes = [
            models.Index(fields=['date', 'currency']),
        ]
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date} - {self.currency} Payment Analytics"


class SystemPerformance(models.Model):
    """
    System performance metrics and monitoring data.
    """
    
    timestamp = models.DateTimeField(default=timezone.now)
    
    # System metrics
    cpu_usage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    memory_usage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    disk_usage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Application metrics
    active_sessions = models.PositiveIntegerField(default=0)
    api_requests_per_minute = models.PositiveIntegerField(default=0)
    avg_response_time = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    
    # Database metrics
    db_connections = models.PositiveIntegerField(default=0)
    db_query_time = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    cache_hit_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Error metrics
    error_count = models.PositiveIntegerField(default=0)
    warning_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_performance'
        verbose_name = 'System Performance'
        verbose_name_plural = 'System Performance'
        indexes = [
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"System Performance - {self.timestamp}"


class ConversionFunnel(models.Model):
    """
    Track user conversion funnel from registration to investment.
    """
    
    date = models.DateField()
    
    # Funnel stages
    visitors = models.PositiveIntegerField(default=0)
    registrations = models.PositiveIntegerField(default=0)
    email_verifications = models.PositiveIntegerField(default=0)
    kyc_submissions = models.PositiveIntegerField(default=0)
    kyc_approvals = models.PositiveIntegerField(default=0)
    first_investments = models.PositiveIntegerField(default=0)
    
    # Conversion rates
    registration_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    verification_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    kyc_submission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    kyc_approval_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    investment_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conversion_funnel'
        verbose_name = 'Conversion Funnel'
        verbose_name_plural = 'Conversion Funnel'
        indexes = [
            models.Index(fields=['date']),
        ]
        ordering = ['-date']
    
    def __str__(self):
        return f"Conversion Funnel - {self.date}"
    
    def calculate_conversion_rates(self):
        """Calculate conversion rates for funnel stages."""
        if self.visitors > 0:
            self.registration_rate = (self.registrations / self.visitors) * 100
        
        if self.registrations > 0:
            self.verification_rate = (self.email_verifications / self.registrations) * 100
            
        if self.email_verifications > 0:
            self.kyc_submission_rate = (self.kyc_submissions / self.email_verifications) * 100
            
        if self.kyc_submissions > 0:
            self.kyc_approval_rate = (self.kyc_approvals / self.kyc_submissions) * 100
            
        if self.kyc_approvals > 0:
            self.investment_rate = (self.first_investments / self.kyc_approvals) * 100
        
        self.save(update_fields=[
            'registration_rate', 'verification_rate', 'kyc_submission_rate',
            'kyc_approval_rate', 'investment_rate'
        ])


class EventTracking(models.Model):
    """
    Track custom events for analytics and user behavior analysis.
    """
    
    EVENT_CATEGORY_CHOICES = [
        ('user', 'User Action'),
        ('investment', 'Investment'),
        ('payment', 'Payment'),
        ('system', 'System Event'),
        ('marketing', 'Marketing'),
        ('security', 'Security'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Event details
    event_name = models.CharField(max_length=100)
    event_category = models.CharField(max_length=20, choices=EVENT_CATEGORY_CHOICES)
    event_label = models.CharField(max_length=255, blank=True)
    event_value = models.DecimalField(max_digits=15, decimal_places=8, null=True, blank=True)
    
    # Context
    page_url = models.URLField(blank=True)
    referrer_url = models.URLField(blank=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    timestamp = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'event_tracking'
        verbose_name = 'Event Tracking'
        verbose_name_plural = 'Event Tracking'
        indexes = [
            models.Index(fields=['event_name', 'timestamp']),
            models.Index(fields=['event_category', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.event_name} - {self.timestamp}"
