"""
DiamondStream Payment Serializers

Serializers for payment-related API endpoints including cryptocurrency payments,
platform wallets, payout requests, and payment disputes.
"""

from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from .models import PlatformWallet, CryptoPayment, PayoutRequest, PaymentDispute


class PlatformWalletSerializer(serializers.ModelSerializer):
    """Serializer for platform cryptocurrency wallets."""
    
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    balance_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PlatformWallet
        fields = [
            'id', 'currency', 'currency_display', 'address', 'label',
            'balance', 'balance_display', 'is_primary', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'balance', 'created_at', 'updated_at']
    
    def get_balance_display(self, obj):
        """Format balance with currency symbol."""
        return f"{obj.balance} {obj.currency}"


class CryptoPaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating crypto payments."""
    
    investment_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CryptoPayment
        fields = [
            'investment_id', 'transaction_hash', 'amount', 'currency',
            'from_address', 'to_address', 'network_fee'
        ]
    
    def validate_investment_id(self, value):
        """Validate investment exists and belongs to user."""
        from investments.models import Investment
        
        try:
            investment = Investment.objects.get(
                id=value,
                user=self.context['request'].user,
                status='pending'
            )
            return investment
        except Investment.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid investment or investment is not pending payment."
            )
    
    def validate_transaction_hash(self, value):
        """Validate transaction hash format and uniqueness."""
        if not value or len(value) < 40:
            raise serializers.ValidationError("Invalid transaction hash format.")
        
        # Check if transaction hash already exists
        if CryptoPayment.objects.filter(transaction_hash=value).exists():
            raise serializers.ValidationError("Transaction hash already exists.")
        
        return value
    
    def validate(self, attrs):
        """Validate payment details against investment."""
        investment = attrs['investment_id']
        amount = attrs['amount']
        currency = attrs['currency']
        
        # Validate currency matches investment
        if currency != investment.currency:
            raise serializers.ValidationError(
                f"Payment currency must be {investment.currency}."
            )
        
        # Validate amount matches investment (with small tolerance for fees)
        expected_amount = investment.amount
        tolerance = expected_amount * Decimal('0.01')  # 1% tolerance
        
        if abs(amount - expected_amount) > tolerance:
            raise serializers.ValidationError(
                f"Payment amount must be approximately {expected_amount} {currency}."
            )
        
        # Validate to_address is a platform wallet
        try:
            platform_wallet = PlatformWallet.objects.get(
                currency=currency,
                address=attrs['to_address'],
                is_active=True
            )
        except PlatformWallet.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid destination address. Please use the provided platform wallet address."
            )
        
        attrs['investment'] = investment
        attrs['platform_wallet'] = platform_wallet
        
        return attrs
    
    def create(self, validated_data):
        """Create crypto payment."""
        investment = validated_data.pop('investment')
        validated_data.pop('investment_id')
        platform_wallet = validated_data.pop('platform_wallet')
        
        # Create payment
        payment = CryptoPayment.objects.create(
            investment=investment,
            platform_wallet=platform_wallet,
            **validated_data
        )
        
        return payment


class CryptoPaymentSerializer(serializers.ModelSerializer):
    """Serializer for crypto payment details."""
    
    investment_id = serializers.IntegerField(source='investment.id', read_only=True)
    user_email = serializers.EmailField(source='investment.user.email', read_only=True)
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    platform_wallet_label = serializers.CharField(source='platform_wallet.label', read_only=True)
    confirmations_required = serializers.SerializerMethodField()
    
    class Meta:
        model = CryptoPayment
        fields = [
            'id', 'investment_id', 'user_email', 'transaction_hash',
            'amount', 'currency', 'currency_display', 'from_address',
            'to_address', 'platform_wallet_label', 'network_fee',
            'confirmations', 'confirmations_required', 'status',
            'status_display', 'verified_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'confirmations', 'verified_at', 'created_at', 'updated_at'
        ]
    
    def get_confirmations_required(self, obj):
        """Get required confirmations for this currency."""
        confirmation_requirements = {
            'BTC': 3,
            'ETH': 6,
            'DOGE': 6,
        }
        return confirmation_requirements.get(obj.currency, 6)


class PayoutRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payout requests."""
    
    investment_id = serializers.IntegerField(write_only=True)
    wallet_address = serializers.CharField(max_length=255)
    
    class Meta:
        model = PayoutRequest
        fields = [
            'investment_id', 'amount', 'currency', 'wallet_address', 'notes'
        ]
    
    def validate_investment_id(self, value):
        """Validate investment is eligible for payout."""
        from investments.models import Investment
        
        try:
            investment = Investment.objects.get(
                id=value,
                user=self.context['request'].user,
                status='completed'
            )
            return investment
        except Investment.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid investment or investment is not eligible for payout."
            )
    
    def validate_wallet_address(self, value):
        """Validate wallet address format."""
        if not value or len(value) < 20:
            raise serializers.ValidationError("Invalid wallet address format.")
        return value
    
    def validate(self, attrs):
        """Validate payout request details."""
        investment = attrs['investment_id']
        amount = attrs['amount']
        currency = attrs['currency']
        
        # Validate currency matches investment
        if currency != investment.currency:
            raise serializers.ValidationError(
                f"Payout currency must be {investment.currency}."
            )
        
        # Validate amount doesn't exceed available returns
        available_amount = investment.actual_return or investment.expected_return
        if amount > available_amount:
            raise serializers.ValidationError(
                f"Requested amount exceeds available payout of {available_amount} {currency}."
            )
        
        # Check for existing pending payout requests
        existing_request = PayoutRequest.objects.filter(
            investment=investment,
            status='pending'
        ).exists()
        
        if existing_request:
            raise serializers.ValidationError(
                "A payout request for this investment is already pending."
            )
        
        attrs['investment'] = investment
        
        return attrs
    
    def create(self, validated_data):
        """Create payout request."""
        investment = validated_data.pop('investment')
        validated_data.pop('investment_id')
        
        # Create payout request
        payout_request = PayoutRequest.objects.create(
            user=self.context['request'].user,
            investment=investment,
            **validated_data
        )
        
        return payout_request


class PayoutRequestSerializer(serializers.ModelSerializer):
    """Serializer for payout request details."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    investment_id = serializers.IntegerField(source='investment.id', read_only=True)
    investment_plan = serializers.CharField(source='investment.plan.name', read_only=True)
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    processed_by_email = serializers.EmailField(source='processed_by.email', read_only=True)
    
    class Meta:
        model = PayoutRequest
        fields = [
            'id', 'user_email', 'investment_id', 'investment_plan',
            'amount', 'currency', 'currency_display', 'wallet_address',
            'status', 'status_display', 'transaction_hash', 'network_fee',
            'notes', 'admin_notes', 'processed_by_email', 'processed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'transaction_hash', 'network_fee', 'admin_notes',
            'processed_by_email', 'processed_at', 'created_at', 'updated_at'
        ]


class PaymentDisputeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payment disputes."""
    
    payment_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = PaymentDispute
        fields = [
            'payment_id', 'dispute_type', 'description', 'evidence'
        ]
    
    def validate_payment_id(self, value):
        """Validate payment exists and belongs to user."""
        try:
            payment = CryptoPayment.objects.get(
                id=value,
                investment__user=self.context['request'].user
            )
            return payment
        except CryptoPayment.DoesNotExist:
            raise serializers.ValidationError("Invalid payment or access denied.")
    
    def validate(self, attrs):
        """Validate dispute creation."""
        payment = attrs['payment_id']
        
        # Check if payment already has an open dispute
        existing_dispute = PaymentDispute.objects.filter(
            payment=payment,
            status__in=['open', 'under_review']
        ).exists()
        
        if existing_dispute:
            raise serializers.ValidationError(
                "This payment already has an open dispute."
            )
        
        attrs['payment'] = payment
        
        return attrs
    
    def create(self, validated_data):
        """Create payment dispute."""
        payment = validated_data.pop('payment')
        validated_data.pop('payment_id')
        
        # Create dispute
        dispute = PaymentDispute.objects.create(
            user=self.context['request'].user,
            payment=payment,
            **validated_data
        )
        
        return dispute


class PaymentDisputeSerializer(serializers.ModelSerializer):
    """Serializer for payment dispute details."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    payment_transaction_hash = serializers.CharField(source='payment.transaction_hash', read_only=True)
    dispute_type_display = serializers.CharField(source='get_dispute_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    resolved_by_email = serializers.EmailField(source='resolved_by.email', read_only=True)
    
    class Meta:
        model = PaymentDispute
        fields = [
            'id', 'user_email', 'payment_transaction_hash', 'dispute_type',
            'dispute_type_display', 'description', 'evidence', 'status',
            'status_display', 'admin_response', 'resolved_by_email',
            'resolved_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'admin_response', 'resolved_by_email', 'resolved_at',
            'created_at', 'updated_at'
        ]


class PaymentStatsSerializer(serializers.Serializer):
    """Serializer for payment statistics."""
    
    total_payments = serializers.IntegerField()
    total_payment_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    verified_payments = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    failed_payments = serializers.IntegerField()
    total_payouts = serializers.IntegerField()
    total_payout_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    pending_payouts = serializers.IntegerField()
    open_disputes = serializers.IntegerField()
