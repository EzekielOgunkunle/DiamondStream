"""
DiamondStream Chat API Views

API endpoints for chat and support functionality including support tickets,
live chat sessions, and FAQ management.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count, Avg
from django.utils import timezone
from .models import ChatRoom, ChatMessage, ChatTemplate, ChatAnalytics
from .serializers import (
    ChatRoomSerializer, ChatRoomCreateSerializer, ChatMessageSerializer, 
    ChatMessageCreateSerializer, ChatTemplateSerializer, ChatStatsSerializer
)


class SupportTicketListView(generics.ListAPIView):
    """List user's support tickets."""
    
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatRoom.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


class SupportTicketCreateView(generics.CreateAPIView):
    """Create a new support ticket."""
    
    serializer_class = ChatRoomCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class SupportTicketDetailView(generics.RetrieveAPIView):
    """Get support ticket details."""
    
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatRoom.objects.filter(user=self.request.user)


class ChatSessionListView(generics.ListAPIView):
    """List user's chat sessions."""
    
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatRoom.objects.filter(
            user=self.request.user
        ).order_by('-updated_at')


class ChatSessionCreateView(generics.CreateAPIView):
    """Create a new chat session."""
    
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """Create chat session and set initial status."""
        session = serializer.save(
            user=self.request.user,
            status='waiting',
            created_at=timezone.now()
        )


class ChatSessionDetailView(generics.RetrieveAPIView):
    """Get chat session details."""
    
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return ChatRoom.objects.all()
        return ChatRoom.objects.filter(user=self.request.user)


class ChatMessageListView(generics.ListAPIView):
    """List messages in a chat session."""
    
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        session_id = self.kwargs.get('session_id')
        
        # Verify user has access to this session
        if self.request.user.is_staff:
            session = ChatRoom.objects.get(id=session_id)
        else:
            session = ChatRoom.objects.get(id=session_id, user=self.request.user)
        
        # Mark messages as read
        session.messages.filter(
            is_read=False
        ).exclude(sender=self.request.user).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return session.messages.order_by('sent_at')


class ChatMessageCreateView(generics.CreateAPIView):
    """Send a message in a chat session."""
    
    serializer_class = ChatMessageCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['session_id'] = self.kwargs.get('session_id')
        return context
    
    def perform_create(self, serializer):
        session_id = self.kwargs.get('session_id')
        
        # Verify user has access to this session
        if self.request.user.is_staff:
            session = ChatRoom.objects.get(id=session_id)
        else:
            session = ChatRoom.objects.get(id=session_id, user=self.request.user)
        
        serializer.save()


class FAQListView(generics.ListAPIView):
    """List published FAQs."""
    
    serializer_class = ChatTemplateSerializer
    permission_classes = [permissions.AllowAny]  # Public access
    
    def get_queryset(self):
        queryset = ChatTemplate.objects.filter(is_active=True).order_by('name', 'id')
        
        # Filter by category if provided
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Search in questions and answers
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(content__icontains=search)
            )
        
        return queryset


class FAQDetailView(generics.RetrieveAPIView):
    """Get FAQ details and increment view count."""
    
    serializer_class = ChatTemplateSerializer
    permission_classes = [permissions.AllowAny]  # Public access
    
    def get_queryset(self):
        return ChatTemplate.objects.filter(is_active=True)
    
    def retrieve(self, request, *args, **kwargs):
        """Increment view count when FAQ is accessed."""
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def end_chat_session(request, session_id):
    """End a chat session."""
    try:
        if request.user.is_staff:
            session = ChatRoom.objects.get(id=session_id)
        else:
            session = ChatRoom.objects.get(id=session_id, user=request.user)
    except ChatRoom.DoesNotExist:
        return Response(
            {'error': 'Chat session not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if session.status != 'closed':
        session.status = 'closed'
        session.updated_at = timezone.now()
        session.save()
    
    return Response({'message': 'Chat session ended successfully'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chat_stats(request):
    """Get chat and support statistics."""
    user = request.user
    
    # User's stats
    tickets = ChatRoom.objects.filter(user=user)
    chat_sessions = ChatRoom.objects.filter(user=user)
    
    stats = {
        'total_tickets': tickets.count(),
        'open_tickets': tickets.filter(status__in=['active', 'waiting']).count(),
        'resolved_tickets': tickets.filter(status='closed').count(),
        'avg_resolution_time': None,  # TODO: Calculate based on timestamps
        'total_chat_sessions': chat_sessions.count(),
        'active_chat_sessions': chat_sessions.filter(status='active').count(),
        'avg_response_time': None,  # TODO: Calculate based on message timestamps
        'user_satisfaction_score': 4.5,  # Placeholder
    }
    
    serializer = ChatStatsSerializer(stats)
    return Response(serializer.data)


# Admin-only views
class AdminSupportTicketListView(generics.ListAPIView):
    """Admin view to list all support tickets."""
    
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return ChatRoom.objects.none()
        
        queryset = ChatRoom.objects.all().order_by('-created_at')
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by priority if provided
        priority_filter = self.request.query_params.get('priority', None)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        return queryset


class AdminChatSessionListView(generics.ListAPIView):
    """Admin view to list all chat sessions."""
    
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return ChatRoom.objects.none()
        
        queryset = ChatRoom.objects.all().order_by('-updated_at')
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset


class AdminFAQListView(generics.ListCreateAPIView):
    """Admin view to manage FAQs."""
    
    serializer_class = ChatTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return ChatTemplate.objects.none()
        return ChatTemplate.objects.all().order_by('name', 'id')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def admin_assign_ticket(request, ticket_id):
    """Admin endpoint to assign a support ticket."""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        ticket = ChatRoom.objects.get(id=ticket_id)
    except ChatRoom.DoesNotExist:
        return Response(
            {'error': 'Support ticket not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    ticket.assigned_agent = request.user
    ticket.status = 'active'
    ticket.save()
    
    return Response({'message': 'Ticket assigned successfully'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def admin_resolve_ticket(request, ticket_id):
    """Admin endpoint to resolve a support ticket."""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        ticket = ChatRoom.objects.get(id=ticket_id)
    except ChatRoom.DoesNotExist:
        return Response(
            {'error': 'Support ticket not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    resolution = request.data.get('resolution', '')
    
    ticket.status = 'closed'
    ticket.notes = resolution
    ticket.updated_at = timezone.now()
    ticket.save()
    
    return Response({'message': 'Ticket resolved successfully'})
