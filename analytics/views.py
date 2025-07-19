"""
DiamondStream Analytics API Views

API endpoints for analytics and reporting including platform statistics,
user analytics, and performance metrics.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from .models import (
    PlatformStats, UserAnalytics, InvestmentAnalytics, 
    PaymentAnalytics, SystemPerformance
)
from .serializers import (
    PlatformStatsSerializer, UserAnalyticsSerializer, InvestmentAnalyticsSerializer,
    SystemPerformanceSerializer, PaymentAnalyticsSerializer, DashboardStatsSerializer,
    UserAnalyticsSerializer as UserStatsSerializer, PlatformMetricsSerializer
)

User = get_user_model()


class PlatformStatsListView(generics.ListAPIView):
    """List platform statistics (admin only)."""
    
    serializer_class = PlatformStatsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return PlatformStats.objects.none()
        
        queryset = PlatformStats.objects.all().order_by('-date')
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset


class UserAnalyticsListView(generics.ListAPIView):
    """List user analytics (admin only)."""
    
    serializer_class = UserAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return UserAnalytics.objects.none()
        
        return UserAnalytics.objects.all().order_by('-date')


class InvestmentAnalyticsListView(generics.ListAPIView):
    """List investment analytics (admin only)."""
    
    serializer_class = InvestmentAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return InvestmentAnalytics.objects.none()
        
        return InvestmentAnalytics.objects.all().order_by('-date')


class SystemPerformanceListView(generics.ListAPIView):
    """List system performance analytics (admin only)."""
    
    serializer_class = SystemPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return SystemPerformance.objects.none()
        
        return SystemPerformance.objects.all().order_by('-date')


class PaymentAnalyticsListView(generics.ListAPIView):
    """List payment analytics (admin only)."""
    
    serializer_class = PaymentAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return PaymentAnalytics.objects.none()
        
        queryset = PaymentAnalytics.objects.all().order_by('-date')
        
        # Filter by currency if provided
        currency = self.request.query_params.get('currency', None)
        if currency:
            queryset = queryset.filter(currency=currency)
        
        return queryset


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def admin_dashboard_stats(request):
    """Get comprehensive admin dashboard statistics."""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    from investments.models import Investment
    from payments.models import CryptoPayment, PayoutRequest
    
    today = timezone.now().date()
    
    # User metrics
    total_users = User.objects.count()
    new_users_today = User.objects.filter(date_joined__date=today).count()
    active_users_today = UserAnalytics.objects.filter(
        date=today,
        login_count__gt=0
    ).count()
    
    # Investment metrics
    investments = Investment.objects.all()
    total_investments = investments.count()
    new_investments_today = investments.filter(created_at__date=today).count()
    total_investment_amount = investments.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Payment metrics
    payments = CryptoPayment.objects.all()
    pending_payments = payments.filter(status__in=['pending', 'submitted', 'confirming']).count()
    verified_payments_today = payments.filter(
        verified_at__date=today,
        status='confirmed'
    ).count()
    total_payment_amount = payments.filter(status='confirmed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Payout metrics
    payouts = PayoutRequest.objects.all()
    pending_payouts = payouts.filter(status='pending').count()
    completed_payouts_today = payouts.filter(
        processed_at__date=today,
        status='completed'
    ).count()
    total_payout_amount = payouts.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Platform metrics
    platform_revenue = total_investment_amount * 0.1  # Assume 10% platform fee
    conversion_rate = (new_investments_today / max(new_users_today, 1)) * 100
    
    stats = {
        'total_users': total_users,
        'new_users_today': new_users_today,
        'active_users_today': active_users_today,
        'total_investments': total_investments,
        'new_investments_today': new_investments_today,
        'total_investment_amount': total_investment_amount,
        'pending_payments': pending_payments,
        'verified_payments_today': verified_payments_today,
        'total_payment_amount': total_payment_amount,
        'pending_payouts': pending_payouts,
        'completed_payouts_today': completed_payouts_today,
        'total_payout_amount': total_payout_amount,
        'platform_revenue': platform_revenue,
        'conversion_rate': conversion_rate,
    }
    
    serializer = DashboardStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_analytics(request):
    """Get analytics for the authenticated user."""
    user = request.user
    
    from investments.models import Investment
    
    # Investment metrics
    investments = Investment.objects.filter(user=user)
    total_investments = investments.count()
    active_investments = investments.filter(status='active').count()
    completed_investments = investments.filter(status='completed').count()
    
    total_invested = investments.aggregate(total=Sum('amount'))['total'] or 0
    total_returns = investments.filter(
        status='completed'
    ).aggregate(total=Sum('actual_return'))['total'] or 0
    
    avg_roi = 0
    if total_invested > 0:
        avg_roi = (total_returns / total_invested) * 100
    
    # Activity metrics
    user_analytics = UserAnalytics.objects.filter(user=user)
    days_active = user_analytics.count()
    
    last_investment = investments.order_by('-created_at').first()
    last_investment_date = last_investment.created_at if last_investment else None
    
    # Referral metrics
    referrals_made = User.objects.filter(referred_by=user).count()
    referral_earnings = 0  # TODO: Calculate from commission model
    
    stats = {
        'total_investments': total_investments,
        'active_investments': active_investments,
        'completed_investments': completed_investments,
        'total_invested': total_invested,
        'total_returns': total_returns,
        'avg_roi': avg_roi,
        'days_active': days_active,
        'last_login': user.last_login,
        'last_investment': last_investment_date,
        'referrals_made': referrals_made,
        'referral_earnings': referral_earnings,
    }
    
    serializer = UserStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def platform_metrics(request):
    """Get comprehensive platform metrics (admin only)."""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get date range parameters
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)  # Default to last 30 days
    
    start_param = request.query_params.get('start_date')
    end_param = request.query_params.get('end_date')
    
    if start_param:
        start_date = datetime.strptime(start_param, '%Y-%m-%d').date()
    if end_param:
        end_date = datetime.strptime(end_param, '%Y-%m-%d').date()
    
    # Calculate previous period for growth rates
    period_length = (end_date - start_date).days
    prev_start_date = start_date - timedelta(days=period_length)
    prev_end_date = start_date
    
    from investments.models import Investment
    from payments.models import CryptoPayment
    
    # Current period metrics
    current_users = User.objects.filter(
        date_joined__date__range=[start_date, end_date]
    ).count()
    current_investments = Investment.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).count()
    current_revenue = Investment.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Previous period metrics
    prev_users = User.objects.filter(
        date_joined__date__range=[prev_start_date, prev_end_date]
    ).count()
    prev_investments = Investment.objects.filter(
        created_at__date__range=[prev_start_date, prev_end_date]
    ).count()
    prev_revenue = Investment.objects.filter(
        created_at__date__range=[prev_start_date, prev_end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate growth rates
    user_growth_rate = ((current_users - prev_users) / max(prev_users, 1)) * 100
    investment_growth_rate = ((current_investments - prev_investments) / max(prev_investments, 1)) * 100
    revenue_growth_rate = ((current_revenue - prev_revenue) / max(prev_revenue, 1)) * 100
    
    # Performance metrics
    total_users = User.objects.count()
    returning_users = User.objects.filter(
        last_login__date__range=[start_date, end_date],
        date_joined__date__lt=start_date
    ).count()
    user_retention_rate = (returning_users / max(total_users, 1)) * 100
    
    completed_investments = Investment.objects.filter(
        status='completed',
        created_at__date__range=[start_date, end_date]
    ).count()
    investment_completion_rate = (completed_investments / max(current_investments, 1)) * 100
    
    successful_payments = CryptoPayment.objects.filter(
        status='confirmed',
        created_at__date__range=[start_date, end_date]
    ).count()
    total_payments = CryptoPayment.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).count()
    payment_success_rate = (successful_payments / max(total_payments, 1)) * 100
    
    # Financial metrics
    avg_investment = Investment.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).aggregate(avg=Avg('amount'))['avg'] or 0
    
    lifetime_value = 1000  # Placeholder - calculate based on user behavior
    cost_per_acquisition = 50  # Placeholder - calculate based on marketing spend
    
    metrics = {
        'start_date': start_date,
        'end_date': end_date,
        'user_growth_rate': user_growth_rate,
        'investment_growth_rate': investment_growth_rate,
        'revenue_growth_rate': revenue_growth_rate,
        'user_retention_rate': user_retention_rate,
        'investment_completion_rate': investment_completion_rate,
        'payment_success_rate': payment_success_rate,
        'average_investment_size': avg_investment,
        'lifetime_value': lifetime_value,
        'cost_per_acquisition': cost_per_acquisition,
    }
    
    serializer = PlatformMetricsSerializer(metrics)
    return Response(serializer.data)
