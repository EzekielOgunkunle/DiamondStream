"""
DiamondStream Chat Admin

Django admin configuration for chat support system.
"""

from django.contrib import admin
from .models import ChatRoom, ChatMessage, ChatAgent, ChatTemplate, ChatAnalytics


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'assigned_agent', 'status', 'priority', 'total_messages', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['user__email', 'subject']
    readonly_fields = ['created_at', 'last_message_at', 'total_messages']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['chat_room', 'sender', 'message_type', 'content_short', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'created_at']
    search_fields = ['content', 'sender__email']
    readonly_fields = ['created_at', 'updated_at']
    
    def content_short(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_short.short_description = 'Content'


@admin.register(ChatAgent)
class ChatAgentAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'user', 'status', 'current_chat_count', 'max_concurrent_chats', 'avg_rating']
    list_filter = ['status', 'specializations']
    search_fields = ['display_name', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'last_active_at']


@admin.register(ChatTemplate)
class ChatTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'usage_count', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'content']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']


@admin.register(ChatAnalytics)
class ChatAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_chats', 'new_chats', 'avg_rating', 'active_agents']
    list_filter = ['date']
    readonly_fields = ['created_at', 'updated_at']
