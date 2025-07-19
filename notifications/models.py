"""
DiamondStream Notifications Models

Models for email and in-app notifications, templates, and user preferences.
Supports investment updates, security alerts, and system notifications.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class NotificationTemplate(models.Model):
    """
    Templates for different types of notifications.
    Admin-configurable templates for consistent messaging.
    """
    
    NOTIFICATION_TYPE_CHOICES = [
        ('welcome', 'Welcome Email'),
        ('email_verification', 'Email Verification'),
        ('password_reset', 'Password Reset'),
        ('investment_created', 'Investment Created'),
        ('payment_received', 'Payment Received'),
        ('payment_confirmed', 'Payment Confirmed'),
        ('investment_matured', 'Investment Matured'),
        ('payout_processed', 'Payout Processed'),
        ('kyc_approved', 'KYC Approved'),
        ('kyc_rejected', 'KYC Rejected'),
        ('referral_earned', 'Referral Commission Earned'),
        ('security_alert', 'Security Alert'),
        ('maintenance_notice', 'Maintenance Notice'),
        ('system_update', 'System Update'),
        ('admin_message', 'Admin Message'),
    ]
    
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('in_app', 'In-App Notification'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    
    # Template content
    subject = models.CharField(max_length=255, help_text="For email notifications")
    title = models.CharField(max_length=255, help_text="For in-app notifications")
    content = models.TextField(help_text="Template content with placeholders")
    html_content = models.TextField(blank=True, help_text="HTML version for emails")
    
    # Template settings
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False, help_text="System templates cannot be deleted")
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent'),
        ],
        default='medium'
    )
    
    # Auto-send settings
    auto_send = models.BooleanField(default=True)
    delay_minutes = models.PositiveIntegerField(default=0, help_text="Delay before sending")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
        indexes = [
            models.Index(fields=['notification_type', 'channel']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.channel})"
    
    def render_content(self, context=None):
        """Render template content with context variables."""
        if context is None:
            context = {}
        
        content = self.content
        html_content = self.html_content
        subject = self.subject
        title = self.title
        
        # Simple template rendering (replace with Jinja2 for advanced templates)
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
            html_content = html_content.replace(placeholder, str(value))
            subject = subject.replace(placeholder, str(value))
            title = title.replace(placeholder, str(value))
        
        return {
            'subject': subject,
            'title': title,
            'content': content,
            'html_content': html_content
        }


class Notification(models.Model):
    """
    Individual notifications sent to users.
    Tracks delivery status and user interactions.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('in_app', 'In-App Notification'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    template = models.ForeignKey(
        NotificationTemplate, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Notification content
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    subject = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    html_content = models.TextField(blank=True)
    
    # Delivery details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Scheduling
    scheduled_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # User interaction
    read_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    # External service details
    external_id = models.CharField(max_length=255, blank=True, help_text="ID from email/SMS service")
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    
    # Context data
    context_data = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['channel', 'status']),
            models.Index(fields=['read_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.title} ({self.channel})"
    
    @property
    def is_read(self):
        """Check if notification has been read."""
        return self.read_at is not None
    
    @property
    def is_clicked(self):
        """Check if notification has been clicked."""
        return self.clicked_at is not None
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])
    
    def mark_as_clicked(self):
        """Mark notification as clicked."""
        if not self.clicked_at:
            self.clicked_at = timezone.now()
            self.save(update_fields=['clicked_at'])


class UserNotificationPreferences(models.Model):
    """
    User preferences for different types of notifications.
    Allows users to control what notifications they receive.
    """
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='notification_preferences'
    )
    
    # Email preferences
    email_investment_updates = models.BooleanField(default=True)
    email_payment_confirmations = models.BooleanField(default=True)
    email_payout_notifications = models.BooleanField(default=True)
    email_security_alerts = models.BooleanField(default=True)
    email_marketing = models.BooleanField(default=False)
    email_system_updates = models.BooleanField(default=True)
    
    # In-app preferences
    inapp_investment_updates = models.BooleanField(default=True)
    inapp_payment_confirmations = models.BooleanField(default=True)
    inapp_payout_notifications = models.BooleanField(default=True)
    inapp_security_alerts = models.BooleanField(default=True)
    inapp_system_updates = models.BooleanField(default=True)
    
    # SMS preferences
    sms_enabled = models.BooleanField(default=False)
    sms_security_alerts = models.BooleanField(default=False)
    sms_payment_confirmations = models.BooleanField(default=False)
    sms_two_factor = models.BooleanField(default=True)
    
    # Push notification preferences
    push_enabled = models.BooleanField(default=False)
    push_investment_updates = models.BooleanField(default=True)
    push_payment_confirmations = models.BooleanField(default=True)
    
    # General preferences
    digest_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('daily', 'Daily Digest'),
            ('weekly', 'Weekly Digest'),
            ('monthly', 'Monthly Digest'),
            ('disabled', 'Disabled'),
        ],
        default='immediate'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_notification_preferences'
        verbose_name = 'User Notification Preferences'
        verbose_name_plural = 'User Notification Preferences'
    
    def __str__(self):
        return f"{self.user.email} Notification Preferences"
    
    def allows_notification(self, notification_type, channel):
        """Check if user allows a specific type of notification via channel."""
        field_name = f"{channel}_{notification_type}"
        return getattr(self, field_name, True)


class NotificationQueue(models.Model):
    """
    Queue for scheduled and batch notifications.
    Handles delayed sending and bulk processing.
    """
    
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    notification = models.OneToOneField(
        Notification, 
        on_delete=models.CASCADE, 
        related_name='queue_entry'
    )
    
    # Queue details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    priority = models.PositiveIntegerField(default=5, help_text="Lower number = higher priority")
    
    # Scheduling
    execute_at = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Processing details
    worker_id = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_queue'
        verbose_name = 'Notification Queue Entry'
        verbose_name_plural = 'Notification Queue Entries'
        indexes = [
            models.Index(fields=['status', 'priority', 'execute_at']),
            models.Index(fields=['execute_at']),
        ]
        ordering = ['priority', 'execute_at']
    
    def __str__(self):
        return f"Queue: {self.notification.title} - {self.status}"


class NotificationStats(models.Model):
    """
    Statistics and analytics for notification performance.
    Tracks delivery rates, open rates, and click rates.
    """
    
    date = models.DateField()
    channel = models.CharField(max_length=20)
    notification_type = models.CharField(max_length=30)
    
    # Counts
    total_sent = models.PositiveIntegerField(default=0)
    total_delivered = models.PositiveIntegerField(default=0)
    total_failed = models.PositiveIntegerField(default=0)
    total_read = models.PositiveIntegerField(default=0)
    total_clicked = models.PositiveIntegerField(default=0)
    
    # Rates (calculated)
    delivery_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    open_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    click_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_stats'
        verbose_name = 'Notification Statistics'
        verbose_name_plural = 'Notification Statistics'
        unique_together = ['date', 'channel', 'notification_type']
        indexes = [
            models.Index(fields=['date', 'channel']),
        ]
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date} - {self.channel} - {self.notification_type}"
    
    def calculate_rates(self):
        """Calculate delivery, open, and click rates."""
        if self.total_sent > 0:
            self.delivery_rate = (self.total_delivered / self.total_sent) * 100
        
        if self.total_delivered > 0:
            self.open_rate = (self.total_read / self.total_delivered) * 100
            self.click_rate = (self.total_clicked / self.total_delivered) * 100
        
        self.save(update_fields=['delivery_rate', 'open_rate', 'click_rate'])
