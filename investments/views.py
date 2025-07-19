"""
DiamondStream Investment API Views

API endpoints for investment management including plans, investments,
history tracking, and commission management.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q, Sum, Count, Avg
from decimal import Decimal
from .models import InvestmentPlan, Investment, InvestmentHistory, ReferralCommission
from .serializers import (
    InvestmentPlanSerializer, InvestmentCreateSerializer, InvestmentSerializer,
    InvestmentHistorySerializer, ReferralCommissionSerializer,
    InvestmentStatsSerializer, UserInvestmentSummarySerializer
)


class InvestmentPlanListView(generics.ListAPIView):
    """List all active investment plans."""
    
    serializer_class = InvestmentPlanSerializer
    permission_classes = [permissions.AllowAny]  # Plans can be viewed without authentication
    
    def get_queryset(self):
        """Get active investment plans."""
        queryset = InvestmentPlan.objects.filter(is_active=True)
        
        # Filter by plan type if specified
        plan_type = self.request.query_params.get('plan_type', None)
        if plan_type:
            queryset = queryset.filter(plan_type=plan_type)
        
        # Filter by currency if specified
        currency = self.request.query_params.get('currency', None)
        if currency:
            queryset = queryset.filter(currency=currency)
        
        return queryset.order_by('plan_type', 'min_amount')


class InvestmentPlanDetailView(generics.RetrieveAPIView):
    """Get detailed information about a specific investment plan."""
    
    serializer_class = InvestmentPlanSerializer
    permission_classes = [permissions.AllowAny]
    queryset = InvestmentPlan.objects.filter(is_active=True)


class InvestmentCreateView(generics.CreateAPIView):
    """Create a new investment."""
    
    serializer_class = InvestmentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Override create to return proper response."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        investment = self.perform_create(serializer)
        
        # Return investment details with proper serialization
        from .serializers import InvestmentResponseSerializer
        response_serializer = InvestmentResponseSerializer(investment)
        
        return Response({
            'message': 'Investment created successfully',
            'investment': response_serializer.data,
            'payment_instructions': {
                'method': investment.payment_method,
                'amount': str(investment.amount),
                'currency': investment.currency,
                'note': 'Please submit payment and upload proof to activate your investment.'
            }
        }, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        """Create investment and log user activity."""
        investment = serializer.save()
        
        # Log user activity
        from users.models import UserActivity
        UserActivity.objects.create(
            user=self.request.user,
            action='investment_created',
            description=f'Created investment for {investment.plan.name} - {investment.amount} {investment.currency}',
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500],
            metadata={
                'investment_id': str(investment.id),
                'plan_id': str(investment.plan.id),
                'amount': float(investment.amount),
                'currency': investment.currency
            }
        )
        
        # Create investment history entry
        InvestmentHistory.objects.create(
            investment=investment,
            status_from='',
            status_to='pending',
            notes='Investment created',
            changed_by=self.request.user
        )
        
        return investment
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class InvestmentListView(generics.ListAPIView):
    """List user's investments."""
    
    serializer_class = InvestmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's investments with filtering."""
        queryset = Investment.objects.filter(user=self.request.user)
        
        # Filter by status if specified
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by plan type if specified
        plan_type = self.request.query_params.get('plan_type', None)
        if plan_type:
            queryset = queryset.filter(plan__plan_type=plan_type)
        
        return queryset.order_by('-created_at')


class InvestmentDetailView(generics.RetrieveAPIView):
    """Get detailed information about a specific investment."""
    
    serializer_class = InvestmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Investment.objects.filter(user=self.request.user)


class InvestmentHistoryListView(generics.ListAPIView):
    """List investment history for a specific investment."""
    
    serializer_class = InvestmentHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get investment history for user's investments."""
        investment_id = self.kwargs.get('investment_id')
        
        # Verify the investment belongs to the current user
        investment = Investment.objects.filter(
            id=investment_id,
            user=self.request.user
        ).first()
        
        if not investment:
            return InvestmentHistory.objects.none()
        
        return InvestmentHistory.objects.filter(
            investment=investment
        ).order_by('-created_at')


class ReferralCommissionListView(generics.ListAPIView):
    """List user's referral commissions."""
    
    serializer_class = ReferralCommissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's referral commissions."""
        queryset = ReferralCommission.objects.filter(referrer=self.request.user)
        
        # Filter by status if specified
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def investment_stats(request):
    """Get comprehensive investment statistics for the user."""
    user = request.user
    
    # Get all user investments
    investments = Investment.objects.filter(user=user)
    
    # Calculate statistics
    total_investments = investments.count()
    total_invested_amount = investments.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    total_returns = investments.filter(
        status='completed'
    ).aggregate(
        total=Sum('actual_return')
    )['total'] or Decimal('0')
    
    # If no actual returns, calculate expected returns for completed investments
    if total_returns == 0:
        total_returns = investments.filter(
            status='completed'
        ).aggregate(
            total=Sum('expected_return')
        )['total'] or Decimal('0')
    
    active_investments = investments.filter(status='active').count()
    completed_investments = investments.filter(status='completed').count()
    pending_investments = investments.filter(status='pending').count()
    
    total_profit = total_returns - total_invested_amount
    
    # Calculate average ROI
    if total_invested_amount > 0:
        average_roi = (total_profit / total_invested_amount) * 100
    else:
        average_roi = Decimal('0')
    
    stats = InvestmentStatsSerializer({
        'total_investments': total_investments,
        'total_invested_amount': total_invested_amount,
        'total_returns': total_returns,
        'active_investments': active_investments,
        'completed_investments': completed_investments,
        'pending_investments': pending_investments,
        'total_profit': total_profit,
        'average_roi': average_roi,
    })
    
    return Response(stats.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_investment_summary(request):
    """Get comprehensive investment summary for the user."""
    user = request.user
    
    # Get investment stats
    investments = Investment.objects.filter(user=user)
    
    total_investments = investments.count()
    total_invested_amount = investments.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    total_returns = investments.filter(
        status='completed'
    ).aggregate(
        total=Sum('actual_return')
    )['total'] or Decimal('0')
    
    if total_returns == 0:
        total_returns = investments.filter(
            status='completed'
        ).aggregate(
            total=Sum('expected_return')
        )['total'] or Decimal('0')
    
    active_investments = investments.filter(status='active').count()
    completed_investments = investments.filter(status='completed').count()
    pending_investments = investments.filter(status='pending').count()
    
    total_profit = total_returns - total_invested_amount
    
    if total_invested_amount > 0:
        average_roi = (total_profit / total_invested_amount) * 100
    else:
        average_roi = Decimal('0')
    
    # Get recent investments (last 5)
    recent_investments = investments.order_by('-created_at')[:5]
    
    # Get upcoming maturities (next 5 investments to mature)
    upcoming_maturities = investments.filter(
        status='active',
        maturity_date__gt=timezone.now()
    ).order_by('maturity_date')[:5]
    
    summary = {
        'user_email': user.email,
        'stats': {
            'total_investments': total_investments,
            'total_invested_amount': total_invested_amount,
            'total_returns': total_returns,
            'active_investments': active_investments,
            'completed_investments': completed_investments,
            'pending_investments': pending_investments,
            'total_profit': total_profit,
            'average_roi': average_roi,
        },
        'recent_investments': InvestmentSerializer(
            recent_investments, 
            many=True
        ).data,
        'upcoming_maturities': InvestmentSerializer(
            upcoming_maturities, 
            many=True
        ).data
    }
    
    return Response(summary, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def referral_stats(request):
    """Get referral statistics for the user."""
    user = request.user
    
    # Get referral commissions
    commissions = ReferralCommission.objects.filter(referrer=user)
    
    total_commissions = commissions.count()
    total_commission_amount = commissions.filter(
        status='paid'
    ).aggregate(
        total=Sum('commission_amount')
    )['total'] or Decimal('0')
    
    pending_commissions = commissions.filter(status='pending').count()
    paid_commissions = commissions.filter(status='paid').count()
    
    # Get referrals count
    referrals_count = user.referrals.count()
    
    # Get recent commissions
    recent_commissions = commissions.order_by('-created_at')[:10]
    
    stats = {
        'total_referrals': referrals_count,
        'total_commissions': total_commissions,
        'total_commission_amount': float(total_commission_amount),
        'pending_commissions': pending_commissions,
        'paid_commissions': paid_commissions,
        'recent_commissions': ReferralCommissionSerializer(
            recent_commissions,
            many=True
        ).data
    }
    
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_investment(request, investment_id):
    """Cancel a pending investment."""
    try:
        investment = Investment.objects.get(
            id=investment_id,
            user=request.user,
            status='pending'
        )
        
        # Update investment status
        old_status = investment.status
        investment.status = 'cancelled'
        investment.save()
        
        # Create history entry
        InvestmentHistory.objects.create(
            investment=investment,
            old_status=old_status,
            new_status='cancelled',
            change_reason='Cancelled by user',
            changed_by=request.user
        )
        
        # Log user activity
        from users.models import UserActivity
        UserActivity.objects.create(
            user=request.user,
            action='investment_cancelled',
            description=f'Cancelled investment for {investment.plan.name} - {investment.amount} {investment.currency}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            metadata={
                'investment_id': investment.id,
                'plan_id': investment.plan.id,
                'amount': float(investment.amount),
                'currency': investment.currency
            }
        )
        
        return Response({
            'message': 'Investment cancelled successfully'
        }, status=status.HTTP_200_OK)
        
    except Investment.DoesNotExist:
        return Response({
            'error': 'Investment not found or cannot be cancelled'
        }, status=status.HTTP_404_NOT_FOUND)


def get_client_ip(request):
    """Get client IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
