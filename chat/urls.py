"""
DiamondStream Chat URLs

URL configuration for chat and support-related API endpoints.
"""

from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Support tickets
    path('tickets/', views.SupportTicketListView.as_view(), name='support-ticket-list'),
    path('tickets/create/', views.SupportTicketCreateView.as_view(), name='support-ticket-create'),
    path('tickets/<uuid:pk>/', views.SupportTicketDetailView.as_view(), name='support-ticket-detail'),
    
    # Chat sessions
    path('sessions/', views.ChatSessionListView.as_view(), name='chat-session-list'),
    path('sessions/create/', views.ChatSessionCreateView.as_view(), name='chat-session-create'),
    path('sessions/<uuid:pk>/', views.ChatSessionDetailView.as_view(), name='chat-session-detail'),
    path('sessions/<uuid:session_id>/end/', views.end_chat_session, name='end-chat-session'),
    
    # Chat messages
    path('sessions/<uuid:session_id>/messages/', views.ChatMessageListView.as_view(), name='chat-message-list'),
    path('sessions/<uuid:session_id>/messages/send/', views.ChatMessageCreateView.as_view(), name='chat-message-create'),
    
    # FAQ
    path('faq/', views.FAQListView.as_view(), name='faq-list'),
    path('faq/<uuid:pk>/', views.FAQDetailView.as_view(), name='faq-detail'),
    
    # Chat statistics
    path('stats/', views.chat_stats, name='chat-stats'),
    
    # Admin endpoints
    path('admin/tickets/', views.AdminSupportTicketListView.as_view(), name='admin-support-ticket-list'),
    path('admin/sessions/', views.AdminChatSessionListView.as_view(), name='admin-chat-session-list'),
    path('admin/faq/', views.AdminFAQListView.as_view(), name='admin-faq-list'),
    path('admin/tickets/<uuid:ticket_id>/assign/', views.admin_assign_ticket, name='admin-assign-ticket'),
    path('admin/tickets/<uuid:ticket_id>/resolve/', views.admin_resolve_ticket, name='admin-resolve-ticket'),
]
