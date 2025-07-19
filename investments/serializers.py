"""
DiamondStream Investment Serializers

Serializers for investment-related API endpoints including investment plans,
investment creation, tracking, and commission management.
"""

from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from .models import InvestmentPlan, Investment, InvestmentHistory, ReferralCommission


class InvestmentPlanSerializer(serializers.ModelSerializer):
    """Serializer for investment plans."""
    
    duration_display = serializers.SerializerMethodField()
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    plan_type_display = serializers.CharField(source='get_plan_type_display', read_only=True)
    
    class Meta:
        model = InvestmentPlan
        fields = [
            'id', 'name', 'plan_type', 'plan_type_display', 'description',
            'min_amount', 'max_amount', 'currency', 'currency_display',
            'roi_percentage', 'return_amount', 'duration_hours', 'duration_days',
            'duration_display', 'max_investments_per_user', 'allowed_payment_methods',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_duration_display(self, obj):
        """Get human-readable duration."""
        if obj.duration_days:
            return f"{obj.duration_days} day{'s' if obj.duration_days > 1 else ''}"
        elif obj.duration_hours:
            return f"{obj.duration_hours} hour{'s' if obj.duration_hours > 1 else ''}"
        return "Not specified"


class InvestmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating investments."""
    
    plan_id = serializers.UUIDField(write_only=True)
    payment_method = serializers.ChoiceField(
        choices=['BTC', 'ETH', 'DOGE', 'PLATFORM_WALLET'],
        write_only=True
    )
    
    class Meta:
        model = Investment
        fields = [
            'plan_id', 'amount', 'payment_method', 'currency'
        ]
    
    def validate_plan_id(self, value):
        """Validate investment plan exists and is active."""
        try:
            plan = InvestmentPlan.objects.get(id=value, is_active=True)
            return plan
        except InvestmentPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive investment plan.")
    
    def validate(self, attrs):
        """Validate investment constraints."""
        plan = attrs['plan_id']
        amount = attrs['amount']
        payment_method = attrs['payment_method']
        user = self.context['request'].user
        
        # Validate amount range
        if amount < plan.min_amount or amount > plan.max_amount:
            raise serializers.ValidationError(
                f"Amount must be between {plan.min_amount} and {plan.max_amount} {plan.currency}."
            )
        
        # Validate currency matches plan
        if attrs.get('currency', plan.currency) != plan.currency:
            raise serializers.ValidationError(
                f"This plan only accepts {plan.currency}."
            )
        
        # Validate payment method is allowed
        if payment_method not in plan.allowed_payment_methods:
            raise serializers.ValidationError(
                f"Payment method {payment_method} is not allowed for this plan."
            )
        
        # Check user investment limits
        user_investment_count = Investment.objects.filter(
            user=user,
            plan=plan,
            status__in=['pending', 'active', 'completed']
        ).count()
        
        if user_investment_count >= plan.max_investments_per_user:
            raise serializers.ValidationError(
                f"You have reached the maximum limit of {plan.max_investments_per_user} "
                f"investments for this plan."
            )
        
        # Set currency from plan if not provided
        attrs['currency'] = plan.currency
        attrs['plan'] = plan
        
        return attrs
    
    def create(self, validated_data):
        """Create investment with calculated maturity date and returns."""
        plan = validated_data.pop('plan')
        validated_data.pop('plan_id')
        payment_method = validated_data.pop('payment_method')
        
        user = self.context['request'].user
        
        # Calculate maturity date
        maturity_date = timezone.now()
        if plan.duration_days:
            maturity_date += timezone.timedelta(days=plan.duration_days)
        elif plan.duration_hours:
            maturity_date += timezone.timedelta(hours=plan.duration_hours)
        
        # Calculate expected return
        if plan.return_amount:
            expected_return = Decimal(str(plan.return_amount))
        else:
            roi_multiplier = Decimal(str(plan.roi_percentage)) / Decimal('100')
            expected_return = validated_data['amount'] * (Decimal('1') + roi_multiplier)
        
        # Create investment
        investment = Investment.objects.create(
            user=user,
            plan=plan,
            maturity_date=maturity_date,
            expected_return=expected_return,
            payment_method=payment_method,
            **validated_data
        )
        
        return investment


class InvestmentResponseSerializer(serializers.ModelSerializer):
    """Serializer for investment responses."""
    
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_type = serializers.CharField(source='plan.plan_type', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Investment
        fields = [
            'id', 'plan_name', 'plan_type', 'amount', 'currency', 
            'expected_return', 'payment_method', 'payment_method_display',
            'status', 'status_display', 'created_at', 'maturity_date'
        ]


class InvestmentSerializer(serializers.ModelSerializer):
    """Serializer for investment details."""
    
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_type = serializers.CharField(source='plan.plan_type', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    days_remaining = serializers.SerializerMethodField()
    roi_percentage = serializers.DecimalField(source='plan.roi_percentage', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Investment
        fields = [
            'id', 'plan_name', 'plan_type', 'user_email', 'amount', 'currency',
            'currency_display', 'expected_return', 'actual_return', 'status',
            'status_display', 'payment_method', 'maturity_date', 'completion_date',
            'days_remaining', 'roi_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'expected_return', 'actual_return', 'completion_date',
            'created_at', 'updated_at'
        ]
    
    def get_days_remaining(self, obj):
        """Calculate days remaining until maturity."""
        if obj.status in ['completed', 'cancelled']:
            return 0
        
        now = timezone.now()
        if obj.maturity_date > now:
            delta = obj.maturity_date - now
            return delta.days
        return 0


class InvestmentHistorySerializer(serializers.ModelSerializer):
    """Serializer for investment history tracking."""
    
    investment_id = serializers.IntegerField(source='investment.id', read_only=True)
    old_status_display = serializers.CharField(source='get_old_status_display', read_only=True)
    new_status_display = serializers.CharField(source='get_new_status_display', read_only=True)
    changed_by_email = serializers.EmailField(source='changed_by.email', read_only=True)
    
    class Meta:
        model = InvestmentHistory
        fields = [
            'id', 'investment_id', 'old_status', 'old_status_display',
            'new_status', 'new_status_display', 'change_reason',
            'changed_by_email', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ReferralCommissionSerializer(serializers.ModelSerializer):
    """Serializer for referral commissions."""
    
    referrer_email = serializers.EmailField(source='referrer.email', read_only=True)
    referred_user_email = serializers.EmailField(source='referred_user.email', read_only=True)
    investment_id = serializers.IntegerField(source='investment.id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ReferralCommission
        fields = [
            'id', 'referrer_email', 'referred_user_email', 'investment_id',
            'commission_rate', 'commission_amount', 'status', 'status_display',
            'paid_at', 'created_at'
        ]
        read_only_fields = ['id', 'commission_amount', 'paid_at', 'created_at']


class InvestmentStatsSerializer(serializers.Serializer):
    """Serializer for investment statistics."""
    
    total_investments = serializers.IntegerField()
    total_invested_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_returns = serializers.DecimalField(max_digits=20, decimal_places=2)
    active_investments = serializers.IntegerField()
    completed_investments = serializers.IntegerField()
    pending_investments = serializers.IntegerField()
    total_profit = serializers.DecimalField(max_digits=20, decimal_places=2)
    average_roi = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    
class UserInvestmentSummarySerializer(serializers.Serializer):
    """Serializer for user investment summary."""
    
    user_email = serializers.EmailField()
    stats = InvestmentStatsSerializer()
    recent_investments = InvestmentSerializer(many=True)
    upcoming_maturities = InvestmentSerializer(many=True)
