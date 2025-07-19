"""
DiamondStream Payment API Views

API endpoints for payment processing including cryptocurrency payments,
platform wallets, payout requests, and payment disputes.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import PlatformWallet, CryptoPayment, PayoutRequest, PaymentDispute
from .serializers import (
    PlatformWalletSerializer, CryptoPaymentCreateSerializer, CryptoPaymentSerializer,
    PayoutRequestCreateSerializer, PayoutRequestSerializer, 
    PaymentDisputeCreateSerializer, PaymentDisputeSerializer, PaymentStatsSerializer
)

User = get_user_model()


class PlatformWalletListView(generics.ListAPIView):
    """List active platform wallets for payment submissions."""
    
    serializer_class = PlatformWalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PlatformWallet.objects.filter(is_active=True)


class CryptoPaymentCreateView(generics.CreateAPIView):
    """Create crypto payment submission."""
    
    serializer_class = CryptoPaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """Create payment and update investment status."""
        payment = serializer.save()
        
        # Update investment status to 'payment_submitted'
        if payment.investment:
            payment.investment.status = 'payment_submitted'
            payment.investment.payment_submitted_at = timezone.now()
            payment.investment.save()


class CryptoPaymentListView(generics.ListAPIView):
    """List user's crypto payments."""
    
    serializer_class = CryptoPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CryptoPayment.objects.filter(
            investment__user=self.request.user
        ).order_by('-created_at')


class CryptoPaymentDetailView(generics.RetrieveAPIView):
    """Get crypto payment details."""
    
    serializer_class = CryptoPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CryptoPayment.objects.filter(
            investment__user=self.request.user
        )


class PayoutRequestCreateView(generics.CreateAPIView):
    """Create payout request for completed investments."""
    
    serializer_class = PayoutRequestCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class PayoutRequestListView(generics.ListAPIView):
    """List user's payout requests."""
    
    serializer_class = PayoutRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PayoutRequest.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


class PaymentDisputeCreateView(generics.CreateAPIView):
    """Create payment dispute."""
    
    serializer_class = PaymentDisputeCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class PaymentDisputeListView(generics.ListAPIView):
    """List user's payment disputes."""
    
    serializer_class = PaymentDisputeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PaymentDispute.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_stats(request):
    """Get user payment statistics."""
    user = request.user
    
    # User's payment stats
    payments = CryptoPayment.objects.filter(investment__user=user)
    payouts = PayoutRequest.objects.filter(user=user)
    disputes = PaymentDispute.objects.filter(user=user)
    
    stats = {
        'total_payments': payments.count(),
        'total_payment_amount': payments.aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'verified_payments': payments.filter(status='confirmed').count(),
        'pending_payments': payments.filter(status__in=['pending', 'submitted', 'confirming']).count(),
        'failed_payments': payments.filter(status='failed').count(),
        'total_payouts': payouts.count(),
        'total_payout_amount': payouts.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'pending_payouts': payouts.filter(status='pending').count(),
        'open_disputes': disputes.filter(status__in=['open', 'investigating']).count(),
    }
    
    serializer = PaymentStatsSerializer(stats)
    return Response(serializer.data)


# Admin-only views for payment management
class AdminPaymentListView(generics.ListAPIView):
    """Admin view to list all payments for verification."""
    
    serializer_class = CryptoPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return CryptoPayment.objects.none()
        
        queryset = CryptoPayment.objects.all().order_by('-created_at')
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset


class AdminPayoutListView(generics.ListAPIView):
    """Admin view to list all payout requests."""
    
    serializer_class = PayoutRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return PayoutRequest.objects.none()
        
        queryset = PayoutRequest.objects.all().order_by('-created_at')
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def admin_verify_payment(request, payment_id):
    """Admin endpoint to verify a crypto payment."""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        payment = CryptoPayment.objects.get(id=payment_id)
    except CryptoPayment.DoesNotExist:
        return Response(
            {'error': 'Payment not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    action = request.data.get('action')  # 'confirm' or 'reject'
    admin_notes = request.data.get('admin_notes', '')
    
    if action == 'confirm':
        payment.status = 'confirmed'
        payment.verified_by = request.user
        payment.verified_at = timezone.now()
        payment.admin_notes = admin_notes
        payment.save()
        
        # Update investment status to 'active'
        if payment.investment:
            payment.investment.status = 'active'
            payment.investment.payment_confirmed_at = timezone.now()
            payment.investment.save()
        
        return Response({'message': 'Payment confirmed successfully'})
    
    elif action == 'reject':
        payment.status = 'failed'
        payment.verified_by = request.user
        payment.verified_at = timezone.now()
        payment.admin_notes = admin_notes
        payment.save()
        
        # Update investment status back to 'pending'
        if payment.investment:
            payment.investment.status = 'pending'
            payment.investment.save()
        
        return Response({'message': 'Payment rejected'})
    
    else:
        return Response(
            {'error': 'Invalid action. Use "confirm" or "reject"'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def admin_process_payout(request, payout_id):
    """Admin endpoint to process a payout request."""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        payout = PayoutRequest.objects.get(id=payout_id)
    except PayoutRequest.DoesNotExist:
        return Response(
            {'error': 'Payout request not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    action = request.data.get('action')  # 'approve' or 'reject'
    transaction_hash = request.data.get('transaction_hash', '')
    admin_notes = request.data.get('admin_notes', '')
    
    if action == 'approve':
        payout.status = 'completed'
        payout.transaction_hash = transaction_hash
        payout.admin_notes = admin_notes
        payout.processed_by = request.user
        payout.processed_at = timezone.now()
        payout.save()
        
        # Update investment status to 'completed'
        if payout.investment:
            payout.investment.status = 'completed'
            payout.investment.completed_at = timezone.now()
            payout.investment.save()
        
        return Response({'message': 'Payout processed successfully'})
    
    elif action == 'reject':
        payout.status = 'rejected'
        payout.admin_notes = admin_notes
        payout.processed_by = request.user
        payout.processed_at = timezone.now()
        payout.save()
        
        return Response({'message': 'Payout request rejected'})
    
    else:
        return Response(
            {'error': 'Invalid action. Use "approve" or "reject"'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
