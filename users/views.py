"""
DiamondStream User API Views

API endpoints for user management including authentication, profile management,
wallet operations, and user activities.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Q, Sum, Count
from .models import User, UserProfile, UserWallet, UserActivity
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserWalletSerializer, UserActivitySerializer, UserDetailSerializer,
    PasswordChangeSerializer, EmailVerificationSerializer
)


class UserRegistrationView(APIView):
    """User registration endpoint."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Log user activity
            UserActivity.objects.create(
                user=user,
                action='registration',
                description='User account created successfully',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            
            return Response({
                'message': 'Registration successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'referral_code': user.referral_code,
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserLoginView(APIView):
    """User login endpoint."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # Log user activity
            UserActivity.objects.create(
                user=user,
                action='login',
                description='User logged in successfully',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            
            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'is_verified': user.is_verified,
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserLogoutView(APIView):
    """User logout endpoint."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Log user activity
            UserActivity.objects.create(
                user=request.user,
                action='logout',
                description='User logged out successfully',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile management endpoint."""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create user profile."""
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile
    
    def perform_update(self, serializer):
        """Log profile update activity."""
        serializer.save()
        
        UserActivity.objects.create(
            user=self.request.user,
            action='profile_update',
            description='User profile updated',
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500]
        )
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserDetailView(generics.RetrieveUpdateAPIView):
    """User detail endpoint with comprehensive information."""
    
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserWalletListCreateView(generics.ListCreateAPIView):
    """User wallet list and creation endpoint."""
    
    serializer_class = UserWalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserWallet.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create wallet and log activity."""
        wallet = serializer.save(user=self.request.user)
        
        UserActivity.objects.create(
            user=self.request.user,
            action='wallet_added',
            description=f'Added {wallet.currency} wallet: {wallet.address[:10]}...',
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500]
        )
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserWalletDetailView(generics.RetrieveUpdateDestroyAPIView):
    """User wallet detail, update, and delete endpoint."""
    
    serializer_class = UserWalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserWallet.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        """Update wallet and log activity."""
        wallet = serializer.save()
        
        UserActivity.objects.create(
            user=self.request.user,
            action='wallet_updated',
            description=f'Updated {wallet.currency} wallet: {wallet.address[:10]}...',
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500]
        )
    
    def perform_destroy(self, instance):
        """Delete wallet and log activity."""
        UserActivity.objects.create(
            user=self.request.user,
            action='wallet_updated',
            description=f'Removed {instance.currency} wallet: {instance.address[:10]}...',
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        instance.delete()
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserActivityListView(generics.ListAPIView):
    """User activity history endpoint."""
    
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserActivity.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


class PasswordChangeView(APIView):
    """Password change endpoint."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # Log password change activity
            UserActivity.objects.create(
                user=request.user,
                action='password_change',
                description='User password changed successfully',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class EmailVerificationView(APIView):
    """Email verification endpoint."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            # In a real implementation, you would validate the code
            # against a stored verification code
            user = request.user
            user.is_verified = True
            user.email_verification_at = timezone.now()
            user.save(update_fields=['is_verified', 'email_verification_at'])
            
            # Log email verification activity
            UserActivity.objects.create(
                user=user,
                action='email_verification',
                description='User email verified successfully',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            
            return Response({
                'message': 'Email verified successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard_stats(request):
    """Get user dashboard statistics."""
    user = request.user
    
    # Get user investment stats
    from investments.models import Investment
    
    investments = Investment.objects.filter(user=user)
    total_investments = investments.count()
    total_invested = investments.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    active_investments = investments.filter(status='active').count()
    completed_investments = investments.filter(status='completed').count()
    pending_investments = investments.filter(status='pending').count()
    
    # Get recent activities
    recent_activities = UserActivity.objects.filter(
        user=user
    ).order_by('-created_at')[:10]
    
    # Get referral stats
    referral_count = user.referrals.count()
    
    stats = {
        'user': {
            'email': user.email,
            'full_name': user.get_full_name(),
            'role': user.role,
            'is_verified': user.is_verified,
            'date_joined': user.date_joined,
            'referral_code': user.referral_code,
        },
        'investments': {
            'total_count': total_investments,
            'total_amount': float(total_invested),
            'active_count': active_investments,
            'completed_count': completed_investments,
            'pending_count': pending_investments,
        },
        'referrals': {
            'count': referral_count,
        },
        'recent_activities': UserActivitySerializer(
            recent_activities, 
            many=True
        ).data
    }
    
    return Response(stats, status=status.HTTP_200_OK)
