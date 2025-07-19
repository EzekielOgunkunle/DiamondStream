"""
DiamondStream Notification Serializers

Serializers for notification-related API endpoints including email notifications,
SMS notifications, and user notification preferences.
"""

from rest_framework import serializers
from django.utils import timezone
from .models import NotificationTemplate, Notification, UserNotificationPreferences


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for notification templates."""
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'notification_type', 'channel', 'subject_template', 
            'body_template', 'variables', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notification details."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user_email', 'notification_type', 'notification_type_display',
            'title', 'message', 'status', 'status_display', 'sent_at',
            'read_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'user_email', 'notification_type_display', 'status_display',
            'sent_at', 'read_at', 'created_at'
        ]


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications."""
    
    class Meta:
        model = Notification
        fields = ['notification_type', 'title', 'message']
    
    def create(self, validated_data):
        """Create notification for authenticated user."""
        notification = Notification.objects.create(
            user=self.context['request'].user,
            **validated_data
        )
        return notification


class UserNotificationPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for user notification preferences."""
    
    class Meta:
        model = UserNotificationPreferences
        fields = [
            'id', 'email_notifications', 'sms_notifications', 
            'push_notifications', 'investment_alerts', 'payment_alerts',
            'security_alerts', 'marketing_notifications', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmailNotificationSerializer(serializers.Serializer):
    """Serializer for sending email notifications."""
    
    recipient_email = serializers.EmailField()
    subject = serializers.CharField(max_length=255)
    message = serializers.CharField()
    template_name = serializers.CharField(required=False)
    
    def validate_template_name(self, value):
        """Validate email template exists."""
        if value:
            try:
                NotificationTemplate.objects.get(name=value, is_active=True, channel='email')
            except NotificationTemplate.DoesNotExist:
                raise serializers.ValidationError("Email template not found or inactive.")
        return value


class SMSNotificationSerializer(serializers.Serializer):
    """Serializer for sending SMS notifications."""
    
    phone_number = serializers.CharField(max_length=20)
    message = serializers.CharField(max_length=160)
    template_name = serializers.CharField(required=False)
    
    def validate_template_name(self, value):
        """Validate SMS template exists."""
        if value:
            try:
                NotificationTemplate.objects.get(name=value, is_active=True, channel='sms')
            except NotificationTemplate.DoesNotExist:
                raise serializers.ValidationError("SMS template not found or inactive.")
        return value


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics."""
    
    total_notifications = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()
    email_notifications = serializers.IntegerField()
    sms_notifications = serializers.IntegerField()
    push_notifications = serializers.IntegerField()
    sent_notifications = serializers.IntegerField()
    pending_notifications = serializers.IntegerField()
    failed_notifications = serializers.IntegerField()
