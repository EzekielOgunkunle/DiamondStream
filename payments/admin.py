"""
DiamondStream Payment Admin

Django admin configuration for payment management.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import PlatformWallet, CryptoPayment, PayoutRequest, TransactionFee, PaymentDispute


@admin.register(PlatformWallet)
class PlatformWalletAdmin(admin.ModelAdmin):
    list_display = ['currency', 'label', 'address_short', 'is_active', 'is_primary', 'balance', 'total_received']
    list_filter = ['currency', 'is_active', 'is_primary']
    search_fields = ['address', 'label']
    
    def address_short(self, obj):
        return f"{obj.address[:10]}...{obj.address[-10:]}" if len(obj.address) > 20 else obj.address
    address_short.short_description = 'Address'


@admin.register(CryptoPayment)
class CryptoPaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'currency', 'amount', 'status', 'confirmations', 'created_at']
    list_filter = ['currency', 'status', 'created_at']
    search_fields = ['user__email', 'transaction_hash', 'from_address']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['currency', 'status', 'created_at']
    search_fields = ['user__email', 'transaction_hash']
    readonly_fields = ['created_at']


@admin.register(TransactionFee)
class TransactionFeeAdmin(admin.ModelAdmin):
    list_display = ['currency', 'operation', 'base_fee', 'percentage_fee', 'network_congestion']
    list_filter = ['currency', 'operation', 'network_congestion']


@admin.register(PaymentDispute)
class PaymentDisputeAdmin(admin.ModelAdmin):
    list_display = ['user', 'dispute_type', 'status', 'assigned_to', 'created_at']
    list_filter = ['dispute_type', 'status', 'created_at']
    search_fields = ['user__email', 'description']
