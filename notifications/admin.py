"""
DiamondStream Notifications Admin

Django admin configuration for notification management.
"""

from django.contrib import admin
from .models import (
    NotificationTemplate, Notification, UserNotificationPreferences,
    NotificationQueue, NotificationStats
)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'notification_type', 'channel', 'is_active', 'priority']
    list_filter = ['notification_type', 'channel', 'is_active', 'priority']
    search_fields = ['name', 'subject', 'content']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'channel', 'status', 'priority', 'created_at', 'read_at']
    list_filter = ['channel', 'status', 'priority', 'created_at']
    search_fields = ['user__email', 'title', 'content']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserNotificationPreferences)
class UserNotificationPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_investment_updates', 'sms_enabled', 'push_enabled', 'digest_frequency']
    list_filter = ['email_investment_updates', 'sms_enabled', 'push_enabled', 'digest_frequency']
    search_fields = ['user__email']


@admin.register(NotificationQueue)
class NotificationQueueAdmin(admin.ModelAdmin):
    list_display = ['notification', 'status', 'priority', 'execute_at', 'retry_count']
    list_filter = ['status', 'priority', 'execute_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NotificationStats)
class NotificationStatsAdmin(admin.ModelAdmin):
    list_display = ['date', 'channel', 'notification_type', 'total_sent', 'delivery_rate', 'open_rate']
    list_filter = ['date', 'channel', 'notification_type']
    readonly_fields = ['created_at', 'updated_at']
