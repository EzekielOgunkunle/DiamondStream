"""
DiamondStream Notification API Views

API endpoints for notification management including email notifications,
SMS notifications, and user notification preferences.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import NotificationTemplate, Notification, UserNotificationPreferences
from .serializers import (
    NotificationTemplateSerializer, NotificationSerializer,
    NotificationCreateSerializer, UserNotificationPreferencesSerializer,
    EmailNotificationSerializer, SMSNotificationSerializer, NotificationStatsSerializer
)


class NotificationListView(generics.ListAPIView):
    """List user's notifications."""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user)
        
        # Filter by read status if provided
        is_read = self.request.query_params.get('is_read', None)
        if is_read is not None:
            if is_read.lower() == 'true':
                queryset = queryset.filter(read_at__isnull=False)
            else:
                queryset = queryset.filter(read_at__isnull=True)
        
        return queryset.order_by('-created_at')


class NotificationDetailView(generics.RetrieveUpdateAPIView):
    """Get notification details and mark as read."""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """Mark notification as read when retrieved."""
        instance = self.get_object()
        
        if not instance.read_at:
            instance.read_at = timezone.now()
            instance.save(update_fields=['read_at'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """User notification preferences management."""
    
    serializer_class = UserNotificationPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create notification preferences for user."""
        preference, created = UserNotificationPreferences.objects.get_or_create(
            user=self.request.user
        )
        return preference


class SendEmailNotificationView(APIView):
    """Send email notification (admin only)."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = EmailNotificationSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            try:
                # Send email
                send_mail(
                    subject=data['subject'],
                    message=data['message'],
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[data['recipient_email']],
                    fail_silently=False,
                )
                
                # Create notification record
                # Try to find user by email
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                try:
                    user = User.objects.get(email=data['recipient_email'])
                    Notification.objects.create(
                        user=user,
                        notification_type='email',
                        title=data['subject'],
                        message=data['message'],
                        status='sent',
                        sent_at=timezone.now()
                    )
                except User.DoesNotExist:
                    pass  # External email, don't create notification record
                
                return Response({
                    'message': 'Email sent successfully'
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    'error': f'Failed to send email: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendSMSNotificationView(APIView):
    """Send SMS notification (admin only)."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = SMSNotificationSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            # TODO: Implement SMS sending logic with Twilio
            # For now, just return success
            return Response({
                'message': 'SMS would be sent (Twilio integration needed)',
                'phone_number': data['phone_number'],
                'message': data['message']
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notifications_read(request):
    """Mark multiple notifications as read."""
    notification_ids = request.data.get('notification_ids', [])
    
    if not notification_ids:
        return Response(
            {'error': 'No notification IDs provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    updated_count = Notification.objects.filter(
        user=request.user,
        id__in=notification_ids,
        read_at__isnull=True
    ).update(read_at=timezone.now())
    
    return Response({
        'message': f'{updated_count} notifications marked as read'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all user notifications as read."""
    updated_count = Notification.objects.filter(
        user=request.user,
        read_at__isnull=True
    ).update(read_at=timezone.now())
    
    return Response({
        'message': f'{updated_count} notifications marked as read'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_stats(request):
    """Get user notification statistics."""
    user = request.user
    
    notifications = Notification.objects.filter(user=user)
    
    stats = {
        'total_notifications': notifications.count(),
        'unread_notifications': notifications.filter(read_at__isnull=True).count(),
        'email_notifications': notifications.filter(notification_type='email').count(),
        'sms_notifications': notifications.filter(notification_type='sms').count(),
        'push_notifications': notifications.filter(notification_type='push').count(),
        'sent_notifications': notifications.filter(status='sent').count(),
        'pending_notifications': notifications.filter(status='pending').count(),
        'failed_notifications': notifications.filter(status='failed').count(),
    }
    
    serializer = NotificationStatsSerializer(stats)
    return Response(serializer.data)


# Admin-only views
class AdminNotificationTemplateListView(generics.ListCreateAPIView):
    """Admin view to manage notification templates."""
    
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return NotificationTemplate.objects.none()
        return NotificationTemplate.objects.all()


class AdminNotificationListView(generics.ListAPIView):
    """Admin view to list all notifications."""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return Notification.objects.none()
        
        queryset = Notification.objects.all().order_by('-created_at')
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by type if provided
        type_filter = self.request.query_params.get('type', None)
        if type_filter:
            queryset = queryset.filter(notification_type=type_filter)
        
        return queryset
