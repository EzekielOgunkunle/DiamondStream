"""
DiamondStream Payment URLs

URL configuration for payment-related API endpoints.
"""

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Platform wallets
    path('wallets/', views.PlatformWalletListView.as_view(), name='platform-wallets'),
    
    # Crypto payments
    path('crypto/create/', views.CryptoPaymentCreateView.as_view(), name='crypto-payment-create'),
    path('crypto/', views.CryptoPaymentListView.as_view(), name='crypto-payment-list'),
    path('crypto/<uuid:pk>/', views.CryptoPaymentDetailView.as_view(), name='crypto-payment-detail'),
    
    # Payout requests
    path('payouts/create/', views.PayoutRequestCreateView.as_view(), name='payout-request-create'),
    path('payouts/', views.PayoutRequestListView.as_view(), name='payout-request-list'),
    
    # Payment disputes
    path('disputes/create/', views.PaymentDisputeCreateView.as_view(), name='payment-dispute-create'),
    path('disputes/', views.PaymentDisputeListView.as_view(), name='payment-dispute-list'),
    
    # User payment statistics
    path('stats/', views.payment_stats, name='payment-stats'),
    
    # Admin endpoints
    path('admin/payments/', views.AdminPaymentListView.as_view(), name='admin-payment-list'),
    path('admin/payouts/', views.AdminPayoutListView.as_view(), name='admin-payout-list'),
    path('admin/payments/<uuid:payment_id>/verify/', views.admin_verify_payment, name='admin-verify-payment'),
    path('admin/payouts/<uuid:payout_id>/process/', views.admin_process_payout, name='admin-process-payout'),
]
