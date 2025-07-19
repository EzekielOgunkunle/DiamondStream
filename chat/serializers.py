"""
DiamondStream Chat Serializers

Serializers for chat and support-related API endpoints including support tickets,
live chat messages, and FAQ management.
"""

from rest_framework import serializers
from django.utils import timezone
from .models import ChatRoom, ChatMessage, ChatTemplate, ChatAnalytics


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer for chat room details."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    assigned_agent_email = serializers.EmailField(source='assigned_agent.email', read_only=True)
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'user_email', 'subject', 'priority', 'priority_display', 
            'status', 'status_display', 'assigned_agent_email', 'notes',
            'created_at', 'updated_at', 'is_resolved'
        ]
        read_only_fields = [
            'id', 'user_email', 'assigned_agent_email', 'notes',
            'created_at', 'updated_at', 'is_resolved'
        ]


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating chat rooms."""
    
    class Meta:
        model = ChatRoom
        fields = ['subject', 'priority']
    
    def create(self, validated_data):
        """Create chat room for authenticated user."""
        room = ChatRoom.objects.create(
            user=self.context['request'].user,
            **validated_data
        )
        return room


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat session details."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    agent_email = serializers.EmailField(source='assigned_agent.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    unread_messages = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'user_email', 'agent_email', 'subject', 'status',
            'status_display', 'unread_messages', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_email', 'agent_email', 'created_at', 'updated_at'
        ]
    
    def get_unread_messages(self, obj):
        """Get count of unread messages for current user."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        
        return obj.messages.filter(
            is_read=False
        ).exclude(sender=request.user).count()


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat message details."""
    
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'sender_email', 'sender_name', 'message', 'message_type',
            'is_read', 'sent_at', 'read_at'
        ]
        read_only_fields = [
            'id', 'sender_email', 'sender_name', 'sent_at', 'read_at'
        ]
    
    def get_sender_name(self, obj):
        """Get sender display name."""
        if obj.sender.is_staff:
            return f"Support Agent ({obj.sender.first_name or obj.sender.email})"
        return obj.sender.get_full_name() or obj.sender.email


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating chat messages."""
    
    class Meta:
        model = ChatMessage
        fields = ['message', 'message_type']
    
    def create(self, validated_data):
        """Create chat message for authenticated user."""
        session_id = self.context.get('session_id')
        session = ChatRoom.objects.get(id=session_id)
        
        message = ChatMessage.objects.create(
            chat_room=session,
            sender=self.context['request'].user,
            **validated_data
        )
        
        # Update session activity
        session.updated_at = timezone.now()
        session.save()
        
        return message


class ChatTemplateSerializer(serializers.ModelSerializer):
    """Serializer for chat template details."""
    
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    
    class Meta:
        model = ChatTemplate
        fields = [
            'id', 'name', 'content', 'template_type', 'template_type_display',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatStatsSerializer(serializers.Serializer):
    """Serializer for chat statistics."""
    
    total_tickets = serializers.IntegerField()
    open_tickets = serializers.IntegerField()
    resolved_tickets = serializers.IntegerField()
    avg_resolution_time = serializers.DurationField()
    total_chat_sessions = serializers.IntegerField()
    active_chat_sessions = serializers.IntegerField()
    avg_response_time = serializers.DurationField()
    user_satisfaction_score = serializers.DecimalField(max_digits=3, decimal_places=2)
