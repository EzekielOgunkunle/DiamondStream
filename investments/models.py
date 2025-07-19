"""
DiamondStream Investment Models

Models for investment plans, user investments, and ROI tracking.
Supports Beginners, VIP, and VVIP investment plans with different durations and returns.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
from datetime import timedelta

User = get_user_model()


class InvestmentPlan(models.Model):
    """
    Investment plan templates (Beginners, VIP, VVIP).
    Defines the structure and rules for different investment tiers.
    """
    
    PLAN_TYPE_CHOICES = [
        ('beginners', 'Beginners Plan'),
        ('vip', 'VIP Plan'),
        ('vvip', 'VVIP Plan'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('DOGE', 'Dogecoin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
    description = models.TextField()
    
    # Investment amounts
    min_amount = models.DecimalField(max_digits=15, decimal_places=8)
    max_amount = models.DecimalField(max_digits=15, decimal_places=8)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='USD')
    
    # Returns
    roi_percentage = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10000)]
    )
    return_amount = models.DecimalField(max_digits=15, decimal_places=8)
    
    # Duration
    duration_hours = models.PositiveIntegerField(null=True, blank=True)  # For hours-based plans
    duration_days = models.PositiveIntegerField(null=True, blank=True)   # For days-based plans
    
    # Availability
    is_active = models.BooleanField(default=True)
    max_investments_per_user = models.PositiveIntegerField(default=1)
    total_slots = models.PositiveIntegerField(null=True, blank=True)  # Limited slots
    used_slots = models.PositiveIntegerField(default=0)
    
    # Payment methods
    allowed_payment_methods = models.JSONField(
        default=list,
        help_text="List of allowed payment methods: ['BTC', 'ETH', 'DOGE', 'PLATFORM_WALLET']"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'investment_plans'
        verbose_name = 'Investment Plan'
        verbose_name_plural = 'Investment Plans'
        indexes = [
            models.Index(fields=['plan_type', 'is_active']),
            models.Index(fields=['currency']),
        ]
        ordering = ['plan_type', 'min_amount']
    
    def __str__(self):
        return f"{self.name} ({self.plan_type})"
    
    @property
    def duration_str(self):
        """Human-readable duration string."""
        if self.duration_hours:
            return f"{self.duration_hours} hours"
        elif self.duration_days:
            return f"{self.duration_days} days"
        return "Unknown duration"
    
    @property
    def is_available(self):
        """Check if plan is available for new investments."""
        if not self.is_active:
            return False
        if self.total_slots and self.used_slots >= self.total_slots:
            return False
        return True
    
    def calculate_maturity_date(self, start_date=None):
        """Calculate when an investment in this plan will mature."""
        if start_date is None:
            start_date = timezone.now()
        
        if self.duration_hours:
            return start_date + timedelta(hours=self.duration_hours)
        elif self.duration_days:
            return start_date + timedelta(days=self.duration_days)
        
        return start_date


class Investment(models.Model):
    """
    User investments tracking individual investment instances.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('payment_submitted', 'Payment Submitted'),
        ('confirmed', 'Payment Confirmed'),
        ('active', 'Active Investment'),
        ('matured', 'Matured'),
        ('paid', 'Payout Completed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('DOGE', 'Dogecoin'),
        ('PLATFORM_WALLET', 'Platform Wallet'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments')
    plan = models.ForeignKey(InvestmentPlan, on_delete=models.PROTECT, related_name='investments')
    
    # Investment details
    amount = models.DecimalField(max_digits=15, decimal_places=8)
    currency = models.CharField(max_length=10)
    expected_return = models.DecimalField(max_digits=15, decimal_places=8)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    # Status and dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_submitted_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    maturity_date = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Payment tracking
    transaction_hash = models.CharField(max_length=255, blank=True)
    payment_address = models.CharField(max_length=255, blank=True)
    payment_proof = models.FileField(upload_to='payment_proofs/', null=True, blank=True)
    
    # Admin notes
    admin_notes = models.TextField(blank=True)
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_investments'
    )
    
    # Payout details
    payout_transaction_hash = models.CharField(max_length=255, blank=True)
    payout_address = models.CharField(max_length=255, blank=True)
    payout_amount = models.DecimalField(max_digits=15, decimal_places=8, null=True, blank=True)
    
    class Meta:
        db_table = 'investments'
        verbose_name = 'Investment'
        verbose_name_plural = 'Investments'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'maturity_date']),
            models.Index(fields=['created_at']),
            models.Index(fields=['transaction_hash']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name} - {self.amount} {self.currency}"
    
    @property
    def is_matured(self):
        """Check if investment has reached maturity date."""
        return timezone.now() >= self.maturity_date
    
    @property
    def time_until_maturity(self):
        """Time remaining until investment matures."""
        if self.is_matured:
            return timedelta(0)
        return self.maturity_date - timezone.now()
    
    @property
    def roi_percentage(self):
        """Calculate ROI percentage for this investment."""
        if self.amount > 0:
            return ((self.expected_return - self.amount) / self.amount) * 100
        return 0
    
    def save(self, *args, **kwargs):
        """Override save to set maturity date and expected return."""
        if not self.maturity_date:
            self.maturity_date = self.plan.calculate_maturity_date(self.created_at)
        
        if not self.expected_return:
            self.expected_return = self.plan.return_amount
        
        super().save(*args, **kwargs)


class InvestmentHistory(models.Model):
    """
    Track status changes and important events for investments.
    """
    
    investment = models.ForeignKey(
        Investment, 
        on_delete=models.CASCADE, 
        related_name='history'
    )
    status_from = models.CharField(max_length=20, blank=True)
    status_to = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'investment_history'
        verbose_name = 'Investment History'
        verbose_name_plural = 'Investment History'
        indexes = [
            models.Index(fields=['investment', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.investment.id} - {self.status_from} → {self.status_to}"


class ReferralCommission(models.Model):
    """
    Track referral commissions earned from investment referrals.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('earned', 'Earned'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    referrer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='earned_commissions'
    )
    referred_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='generated_commissions'
    )
    investment = models.ForeignKey(
        Investment, 
        on_delete=models.CASCADE, 
        related_name='referral_commissions'
    )
    
    # Commission details
    commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Commission rate as percentage (e.g., 5.00 for 5%)"
    )
    commission_amount = models.DecimalField(max_digits=15, decimal_places=8)
    currency = models.CharField(max_length=10)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payout details
    paid_at = models.DateTimeField(null=True, blank=True)
    payout_transaction_hash = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'referral_commissions'
        verbose_name = 'Referral Commission'
        verbose_name_plural = 'Referral Commissions'
        indexes = [
            models.Index(fields=['referrer', 'status']),
            models.Index(fields=['investment']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.referrer.email} - {self.commission_amount} {self.currency}"
