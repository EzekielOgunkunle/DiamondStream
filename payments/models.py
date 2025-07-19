"""
DiamondStream Payment Models

Models for crypto payment processing, transaction verification, and wallet management.
Supports Bitcoin, Ethereum, and Dogecoin payments with admin verification.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import RegexValidator
from decimal import Decimal
import uuid

User = get_user_model()


class PlatformWallet(models.Model):
    """
    Platform-owned cryptocurrency wallets for receiving payments.
    Admin-managed wallets for different cryptocurrencies.
    """
    
    CURRENCY_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('DOGE', 'Dogecoin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES)
    address = models.CharField(max_length=255, unique=True)
    label = models.CharField(max_length=100, help_text="Admin label for wallet identification")
    
    # Wallet status
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)  # Primary wallet for this currency
    
    # Balance tracking (optional - can be updated via API)
    balance = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    last_balance_update = models.DateTimeField(null=True, blank=True)
    
    # Security and monitoring
    daily_limit = models.DecimalField(
        max_digits=15, 
        decimal_places=8, 
        null=True, 
        blank=True,
        help_text="Daily receiving limit for this wallet"
    )
    total_received = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    transaction_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'platform_wallets'
        verbose_name = 'Platform Wallet'
        verbose_name_plural = 'Platform Wallets'
        unique_together = ['currency', 'address']
        indexes = [
            models.Index(fields=['currency', 'is_active']),
            models.Index(fields=['address']),
        ]
    
    def __str__(self):
        return f"{self.currency} Wallet - {self.label}"
    
    def save(self, *args, **kwargs):
        """Ensure only one primary wallet per currency."""
        if self.is_primary:
            PlatformWallet.objects.filter(
                currency=self.currency, 
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class CryptoPayment(models.Model):
    """
    Individual cryptocurrency payment transactions.
    Links user payments to platform wallets with verification status.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('submitted', 'Payment Submitted'),
        ('confirming', 'Confirming on Blockchain'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]
    
    CURRENCY_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('DOGE', 'Dogecoin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crypto_payments')
    investment = models.OneToOneField(
        'investments.Investment', 
        on_delete=models.CASCADE, 
        related_name='payment',
        null=True,
        blank=True
    )
    
    # Payment details
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=8)
    platform_wallet = models.ForeignKey(
        PlatformWallet, 
        on_delete=models.PROTECT, 
        related_name='received_payments'
    )
    
    # Transaction information
    transaction_hash = models.CharField(max_length=255, blank=True, db_index=True)
    from_address = models.CharField(max_length=255, blank=True)
    to_address = models.CharField(max_length=255)  # Should match platform_wallet.address
    
    # Verification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    confirmations = models.PositiveIntegerField(default=0)
    required_confirmations = models.PositiveIntegerField(default=3)
    
    # Blockchain data
    block_number = models.PositiveIntegerField(null=True, blank=True)
    block_hash = models.CharField(max_length=255, blank=True)
    gas_used = models.DecimalField(max_digits=15, decimal_places=8, null=True, blank=True)
    gas_price = models.DecimalField(max_digits=15, decimal_places=8, null=True, blank=True)
    
    # Admin verification
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_payments'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    
    # Payment proof (user uploaded)
    payment_proof = models.FileField(
        upload_to='payment_proofs/', 
        null=True, 
        blank=True,
        help_text="Screenshot or proof of payment uploaded by user"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crypto_payments'
        verbose_name = 'Crypto Payment'
        verbose_name_plural = 'Crypto Payments'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['platform_wallet', 'status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} {self.currency} ({self.status})"
    
    @property
    def is_confirmed(self):
        """Check if payment has enough confirmations."""
        return self.confirmations >= self.required_confirmations
    
    @property
    def usd_value(self):
        """Get USD value of payment (requires price API integration)."""
        # This would integrate with crypto price APIs
        # For now, return None
        return None


class PayoutRequest(models.Model):
    """
    Payout requests for completed investments.
    Admin processes these to send returns to users.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    CURRENCY_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('DOGE', 'Dogecoin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payout_requests')
    investment = models.OneToOneField(
        'investments.Investment',
        on_delete=models.CASCADE,
        related_name='payout_request'
    )
    
    # Payout details
    amount = models.DecimalField(max_digits=15, decimal_places=8)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES)
    payout_address = models.CharField(max_length=255)
    
    # Status and processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payouts'
    )
    
    # Transaction details
    transaction_hash = models.CharField(max_length=255, blank=True)
    transaction_fee = models.DecimalField(max_digits=15, decimal_places=8, null=True, blank=True)
    net_amount = models.DecimalField(max_digits=15, decimal_places=8, null=True, blank=True)
    
    # Admin notes
    admin_notes = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payout_requests'
        verbose_name = 'Payout Request'
        verbose_name_plural = 'Payout Requests'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['investment']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payout: {self.user.email} - {self.amount} {self.currency}"


class TransactionFee(models.Model):
    """
    Track transaction fees for different cryptocurrencies and operations.
    Used for calculating optimal transaction fees.
    """
    
    OPERATION_CHOICES = [
        ('payment', 'Payment Processing'),
        ('payout', 'Payout Processing'),
        ('transfer', 'Internal Transfer'),
    ]
    
    currency = models.CharField(max_length=10)
    operation = models.CharField(max_length=20, choices=OPERATION_CHOICES)
    
    # Fee structure
    base_fee = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    per_byte_fee = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    percentage_fee = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    
    # Network conditions
    network_congestion = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
        ],
        default='medium'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transaction_fees'
        verbose_name = 'Transaction Fee'
        verbose_name_plural = 'Transaction Fees'
        unique_together = ['currency', 'operation']
    
    def __str__(self):
        return f"{self.currency} - {self.operation} Fee"
    
    def calculate_fee(self, amount, transaction_size_bytes=250):
        """Calculate total fee for a transaction."""
        fee = self.base_fee
        fee += self.per_byte_fee * transaction_size_bytes
        fee += (amount * self.percentage_fee / 100)
        return fee


class PaymentDispute(models.Model):
    """
    Handle payment disputes and resolution tracking.
    """
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    DISPUTE_TYPE_CHOICES = [
        ('payment_not_received', 'Payment Not Received'),
        ('incorrect_amount', 'Incorrect Amount'),
        ('duplicate_payment', 'Duplicate Payment'),
        ('unauthorized_payment', 'Unauthorized Payment'),
        ('technical_issue', 'Technical Issue'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_disputes')
    payment = models.ForeignKey(
        CryptoPayment, 
        on_delete=models.CASCADE, 
        related_name='disputes',
        null=True,
        blank=True
    )
    investment = models.ForeignKey(
        'investments.Investment',
        on_delete=models.CASCADE,
        related_name='payment_disputes',
        null=True,
        blank=True
    )
    
    # Dispute details
    dispute_type = models.CharField(max_length=30, choices=DISPUTE_TYPE_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Resolution
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_disputes'
    )
    resolution_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_disputes'
    )
    
    # Evidence
    evidence_files = models.JSONField(
        default=list,
        help_text="List of file paths for evidence documents"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_disputes'
        verbose_name = 'Payment Dispute'
        verbose_name_plural = 'Payment Disputes'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['assigned_to']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Dispute #{self.id} - {self.user.email} - {self.dispute_type}"
