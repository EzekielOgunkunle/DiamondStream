"""
DiamondStream User URLs

URL configuration for user-related API endpoints.
"""

from django.urls import path
from .views import (
    UserRegistrationView, UserLoginView, UserLogoutView,
    UserProfileView, UserDetailView, UserWalletListCreateView,
    UserWalletDetailView, UserActivityListView, PasswordChangeView,
    EmailVerificationView, user_dashboard_stats
)

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/logout/', UserLogoutView.as_view(), name='logout'),
    path('auth/verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('auth/change-password/', PasswordChangeView.as_view(), name='change-password'),
    
    # User management endpoints
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('detail/', UserDetailView.as_view(), name='detail'),
    path('dashboard-stats/', user_dashboard_stats, name='dashboard-stats'),
    
    # Wallet management endpoints
    path('wallets/', UserWalletListCreateView.as_view(), name='wallet-list'),
    path('wallets/<int:pk>/', UserWalletDetailView.as_view(), name='wallet-detail'),
    
    # Activity tracking
    path('activities/', UserActivityListView.as_view(), name='activity-list'),
]
