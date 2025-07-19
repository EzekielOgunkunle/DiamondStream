"""
DiamondStream User Models

Custom user model with email authentication and investment-specific fields.
Includes User, UserProfile, and role-based access control.
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with email authentication.
    Extends Django's AbstractBaseUser for cryptocurrency investment platform.
    """
    
    ROLE_CHOICES = [
        ('user', 'Regular User'),
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    
    # User status fields
    is_active = models.BooleanField(default=False)  # Requires email verification
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)  # KYC verification
    
    # Role-based access control
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Security fields
    email_verified_at = models.DateTimeField(null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    
    # Referral system
    referral_code = models.CharField(max_length=10, unique=True, blank=True)
    referred_by = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='referrals'
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['referral_code']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_admin(self):
        """Check if user is an admin."""
        return self.role in ['admin', 'super_admin'] or self.is_staff
    
    @property
    def is_super_admin(self):
        """Check if user is a super admin."""
        return self.role == 'super_admin' or self.is_superuser
    
    def save(self, *args, **kwargs):
        """Override save to generate referral code."""
        if not self.referral_code:
            self.referral_code = self._generate_referral_code()
        super().save(*args, **kwargs)
    
    def _generate_referral_code(self):
        """Generate a unique referral code."""
        import string
        import random
        
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not User.objects.filter(referral_code=code).exists():
                return code
    
    def get_full_name(self):
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email


class UserProfile(models.Model):
    """
    Extended user profile with KYC and investment-specific information.
    """
    
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal information
    phone_number = models.CharField(
        max_length=20, 
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')]
    )
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # KYC verification
    verification_status = models.CharField(
        max_length=20, 
        choices=VERIFICATION_STATUS_CHOICES, 
        default='pending'
    )
    identity_document = models.FileField(
        upload_to='documents/identity/', 
        null=True, 
        blank=True
    )
    proof_of_address = models.FileField(
        upload_to='documents/address/', 
        null=True, 
        blank=True
    )
    selfie_verification = models.FileField(
        upload_to='documents/selfie/', 
        null=True, 
        blank=True
    )
    
    # Investment preferences
    risk_tolerance = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
        ],
        default='medium'
    )
    preferred_currency = models.CharField(
        max_length=10,
        choices=[
            ('USD', 'US Dollar'),
            ('BTC', 'Bitcoin'),
            ('ETH', 'Ethereum'),
            ('DOGE', 'Dogecoin'),
        ],
        default='USD'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.email} Profile"


class UserWallet(models.Model):
    """
    User cryptocurrency wallet addresses for receiving payouts.
    """
    
    CURRENCY_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('DOGE', 'Dogecoin'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES)
    address = models.CharField(max_length=255)
    label = models.CharField(max_length=100, blank=True)  # User-defined label
    is_primary = models.BooleanField(default=False)  # Primary wallet for this currency
    is_verified = models.BooleanField(default=False)  # Admin verification
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_wallets'
        verbose_name = 'User Wallet'
        verbose_name_plural = 'User Wallets'
        unique_together = ['user', 'currency', 'address']
        indexes = [
            models.Index(fields=['user', 'currency']),
            models.Index(fields=['address']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.currency} Wallet"
    
    def save(self, *args, **kwargs):
        """Ensure only one primary wallet per currency per user."""
        if self.is_primary:
            UserWallet.objects.filter(
                user=self.user, 
                currency=self.currency, 
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class UserActivity(models.Model):
    """
    Track user activities for security and audit purposes.
    """
    
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('registration', 'Registration'),
        ('password_change', 'Password Change'),
        ('email_verification', 'Email Verification'),
        ('profile_update', 'Profile Update'),
        ('investment_created', 'Investment Created'),
        ('investment_cancelled', 'Investment Cancelled'),
        ('wallet_added', 'Wallet Added'),
        ('wallet_updated', 'Wallet Updated'),
        ('payout_requested', 'Payout Requested'),
        ('kyc_submitted', 'KYC Submitted'),
        ('two_factor_enabled', 'Two Factor Enabled'),
        ('two_factor_disabled', 'Two Factor Disabled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Additional context data (JSON)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activities'
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.action} at {self.created_at}"
