"""
DiamondStream URL Configuration

Main URL configuration for the DiamondStream cryptocurrency investment platform.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

# API version prefix
API_VERSION = 'v1'

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # API endpoints
    path(f'api/{API_VERSION}/users/', include('users.urls')),
    path(f'api/{API_VERSION}/investments/', include('investments.urls')),
    path(f'api/{API_VERSION}/payments/', include('payments.urls')),
    path(f'api/{API_VERSION}/notifications/', include('notifications.urls')),
    path(f'api/{API_VERSION}/analytics/', include('analytics.urls')),
    path(f'api/{API_VERSION}/chat/', include('chat.urls')),
    
    # API documentation (optional - can be added later)
    # path('api/docs/', include_docs_urls(title='DiamondStream API')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
