"""
DiamondStream Chat Models

Models for live chat support system between users and admin support agents.
Supports real-time messaging, file attachments, and chat history.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class ChatRoom(models.Model):
    """
    Chat rooms for individual user support conversations.
    Each user gets a dedicated chat room for support.
    """
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('waiting', 'Waiting for Agent'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms')
    assigned_agent = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_chats',
        limit_choices_to={'role__in': ['admin', 'super_admin']}
    )
    
    # Chat details
    subject = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Metadata
    user_rating = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="User rating 1-5 stars"
    )
    user_feedback = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    agent_assigned_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_messages = models.PositiveIntegerField(default=0)
    avg_response_time = models.DurationField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_rooms'
        verbose_name = 'Chat Room'
        verbose_name_plural = 'Chat Rooms'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['assigned_agent', 'status']),
            models.Index(fields=['status', 'priority', 'created_at']),
            models.Index(fields=['last_message_at']),
        ]
        ordering = ['-last_message_at', '-created_at']
    
    def __str__(self):
        return f"Chat #{self.id} - {self.user.email}"
    
    @property
    def is_active(self):
        """Check if chat room is active."""
        return self.status in ['active', 'waiting']
    
    def assign_agent(self, agent):
        """Assign an agent to this chat room."""
        self.assigned_agent = agent
        self.status = 'active'
        self.agent_assigned_at = timezone.now()
        self.save(update_fields=['assigned_agent', 'status', 'agent_assigned_at'])
    
    def close_chat(self, closed_by=None):
        """Close the chat room."""
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save(update_fields=['status', 'closed_at'])


class ChatMessage(models.Model):
    """
    Individual messages within chat rooms.
    Supports text messages, file attachments, and system messages.
    """
    
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text Message'),
        ('file', 'File Attachment'),
        ('image', 'Image'),
        ('system', 'System Message'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    
    # Message content
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField()
    file_attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    
    # Message status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # System message details
    is_system_message = models.BooleanField(default=False)
    system_action = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_messages'
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        indexes = [
            models.Index(fields=['chat_room', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['is_read', 'created_at']),
        ]
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message in {self.chat_room.id} by {self.sender.email}"
    
    def mark_as_read(self, reader=None):
        """Mark message as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def save(self, *args, **kwargs):
        """Update chat room's last message timestamp."""
        super().save(*args, **kwargs)
        
        # Update chat room's last message time and total messages
        self.chat_room.last_message_at = self.created_at
        self.chat_room.total_messages = self.chat_room.messages.count()
        self.chat_room.save(update_fields=['last_message_at', 'total_messages'])


class ChatAgent(models.Model):
    """
    Chat agent profiles and availability status.
    Tracks agent performance and availability.
    """
    
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('busy', 'Busy'),
        ('away', 'Away'),
        ('offline', 'Offline'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='chat_agent_profile',
        limit_choices_to={'role__in': ['admin', 'super_admin']}
    )
    
    # Agent details
    display_name = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='agent_avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    
    # Availability
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    max_concurrent_chats = models.PositiveIntegerField(default=5)
    current_chat_count = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    total_chats_handled = models.PositiveIntegerField(default=0)
    avg_response_time = models.DurationField(null=True, blank=True)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_ratings = models.PositiveIntegerField(default=0)
    
    # Specializations
    specializations = models.JSONField(
        default=list,
        help_text="List of agent specializations: ['investments', 'payments', 'technical', 'general']"
    )
    
    # Working hours
    timezone = models.CharField(max_length=50, default='UTC')
    work_start_time = models.TimeField(null=True, blank=True)
    work_end_time = models.TimeField(null=True, blank=True)
    
    # Timestamps
    last_active_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_agents'
        verbose_name = 'Chat Agent'
        verbose_name_plural = 'Chat Agents'
        indexes = [
            models.Index(fields=['status', 'current_chat_count']),
            models.Index(fields=['last_active_at']),
        ]
    
    def __str__(self):
        return f"Agent: {self.display_name} ({self.status})"
    
    @property
    def is_available(self):
        """Check if agent is available for new chats."""
        return (
            self.status == 'online' and 
            self.current_chat_count < self.max_concurrent_chats
        )
    
    def update_status(self, status):
        """Update agent status and last active time."""
        self.status = status
        self.last_active_at = timezone.now()
        self.save(update_fields=['status', 'last_active_at'])
    
    def calculate_avg_rating(self):
        """Calculate average rating from chat rooms."""
        ratings = ChatRoom.objects.filter(
            assigned_agent=self.user,
            user_rating__isnull=False
        ).values_list('user_rating', flat=True)
        
        if ratings:
            self.avg_rating = sum(ratings) / len(ratings)
            self.total_ratings = len(ratings)
            self.save(update_fields=['avg_rating', 'total_ratings'])


class ChatTemplate(models.Model):
    """
    Pre-defined message templates for common responses.
    Helps agents respond quickly to common questions.
    """
    
    CATEGORY_CHOICES = [
        ('greeting', 'Greeting'),
        ('investment', 'Investment Help'),
        ('payment', 'Payment Support'),
        ('technical', 'Technical Support'),
        ('closing', 'Chat Closing'),
        ('escalation', 'Escalation'),
        ('general', 'General Support'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    content = models.TextField()
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    
    # Availability
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_templates'
        verbose_name = 'Chat Template'
        verbose_name_plural = 'Chat Templates'
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['usage_count']),
        ]
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    def increment_usage(self):
        """Increment usage count when template is used."""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class ChatAnalytics(models.Model):
    """
    Daily analytics for chat support system.
    """
    
    date = models.DateField(unique=True)
    
    # Chat metrics
    total_chats = models.PositiveIntegerField(default=0)
    new_chats = models.PositiveIntegerField(default=0)
    closed_chats = models.PositiveIntegerField(default=0)
    active_chats = models.PositiveIntegerField(default=0)
    
    # Message metrics
    total_messages = models.PositiveIntegerField(default=0)
    avg_messages_per_chat = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Response metrics
    avg_first_response_time = models.DurationField(null=True, blank=True)
    avg_resolution_time = models.DurationField(null=True, blank=True)
    
    # Satisfaction metrics
    total_ratings = models.PositiveIntegerField(default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    # Agent metrics
    active_agents = models.PositiveIntegerField(default=0)
    total_agent_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_analytics'
        verbose_name = 'Chat Analytics'
        verbose_name_plural = 'Chat Analytics'
        indexes = [
            models.Index(fields=['date']),
        ]
        ordering = ['-date']
    
    def __str__(self):
        return f"Chat Analytics - {self.date}"
