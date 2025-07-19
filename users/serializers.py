"""
DiamondStream User Serializers

Serializers for user-related API endpoints including authentication,
profile management, and wallet operations.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile, UserWallet, UserActivity


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    referred_by_code = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'password', 
            'password_confirm', 'referred_by_code'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        """Validate password confirmation and referral code."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        
        # Validate referral code if provided
        referred_by_code = attrs.get('referred_by_code')
        if referred_by_code:
            try:
                referrer = User.objects.get(referral_code=referred_by_code)
                attrs['referred_by'] = referrer
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid referral code.")
        
        return attrs
    
    def create(self, validated_data):
        """Create user with validated data."""
        # Remove password_confirm and referred_by_code from validated_data
        validated_data.pop('password_confirm', None)
        validated_data.pop('referred_by_code', None)
        
        # Create user
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Validate user credentials."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include "email" and "password".')


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile management."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'user_email', 'user_name', 'phone_number', 'date_of_birth',
            'country', 'city', 'address', 'postal_code', 'verification_status',
            'identity_document', 'proof_of_address', 'selfie_verification',
            'risk_tolerance', 'preferred_currency', 'created_at', 'updated_at'
        ]
        read_only_fields = ['verification_status', 'created_at', 'updated_at']


class UserWalletSerializer(serializers.ModelSerializer):
    """Serializer for user cryptocurrency wallets."""
    
    class Meta:
        model = UserWallet
        fields = [
            'id', 'currency', 'address', 'label', 'is_primary', 
            'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']
    
    def validate_address(self, value):
        """Validate cryptocurrency address format."""
        # Basic validation - in production, use proper crypto address validation
        if not value or len(value) < 20:
            raise serializers.ValidationError("Invalid wallet address format.")
        return value
    
    def validate(self, attrs):
        """Validate wallet constraints."""
        user = self.context['request'].user
        currency = attrs.get('currency')
        is_primary = attrs.get('is_primary', False)
        
        # Check if user already has a primary wallet for this currency
        if is_primary:
            existing_primary = UserWallet.objects.filter(
                user=user, 
                currency=currency, 
                is_primary=True
            ).exclude(id=self.instance.id if self.instance else None)
            
            if existing_primary.exists():
                raise serializers.ValidationError(
                    f"You already have a primary {currency} wallet."
                )
        
        return attrs


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for user activity logs."""
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'action', 'description', 'ip_address',
            'user_agent', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer with profile and wallet information."""
    
    profile = UserProfileSerializer(read_only=True)
    wallets = UserWalletSerializer(many=True, read_only=True)
    total_investments = serializers.SerializerMethodField()
    total_invested_amount = serializers.SerializerMethodField()
    referral_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role', 
            'is_verified', 'referral_code', 'date_joined',
            'profile', 'wallets', 'total_investments', 
            'total_invested_amount', 'referral_count'
        ]
        read_only_fields = [
            'id', 'email', 'role', 'is_verified', 'referral_code', 'date_joined'
        ]
    
    def get_total_investments(self, obj):
        """Get total number of investments."""
        return obj.investments.count()
    
    def get_total_invested_amount(self, obj):
        """Get total invested amount across all investments."""
        from django.db.models import Sum
        total = obj.investments.aggregate(
            total=Sum('amount')
        )['total']
        return float(total) if total else 0.0
    
    def get_referral_count(self, obj):
        """Get number of users referred by this user."""
        return obj.referrals.count()


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    current_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(style={'input_type': 'password'})
    
    def validate_current_password(self, value):
        """Validate current password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs
    
    def save(self):
        """Change user password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification."""
    
    verification_code = serializers.CharField(max_length=6)
    
    def validate_verification_code(self, value):
        """Validate verification code."""
        # In a real implementation, you would validate against a stored code
        # For now, we'll accept any 6-digit code
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("Invalid verification code format.")
        return value
