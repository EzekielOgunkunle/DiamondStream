"""
DiamondStream Notification URLs

URL configuration for notification-related API endpoints.
"""

from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # User notifications
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<uuid:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    
    # Notification preferences
    path('preferences/', views.NotificationPreferenceView.as_view(), name='notification-preferences'),
    
    # Notification actions
    path('mark-read/', views.mark_notifications_read, name='mark-notifications-read'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
    
    # Notification statistics
    path('stats/', views.notification_stats, name='notification-stats'),
    
    # Admin endpoints
    path('admin/send-email/', views.SendEmailNotificationView.as_view(), name='admin-send-email'),
    path('admin/send-sms/', views.SendSMSNotificationView.as_view(), name='admin-send-sms'),
    path('admin/templates/', views.AdminNotificationTemplateListView.as_view(), name='admin-notification-templates'),
    path('admin/notifications/', views.AdminNotificationListView.as_view(), name='admin-notification-list'),
]
