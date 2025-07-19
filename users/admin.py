"""
DiamondStream User Admin

Django admin configuration for user management models.
Provides comprehensive admin interface for users, profiles, wallets, and activities.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User, UserProfile, UserWallet, UserActivity


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced User admin with custom fields and actions."""
    
    list_display = [
        'email', 'full_name', 'role', 'is_active', 'is_verified', 
        'date_joined', 'referral_code', 'investment_count'
    ]
    list_filter = [
        'role', 'is_active', 'is_verified', 'is_staff', 
        'two_factor_enabled', 'date_joined'
    ]
    search_fields = ['email', 'first_name', 'last_name', 'referral_code']
    ordering = ['-date_joined']
    readonly_fields = ['id', 'date_joined', 'last_login', 'email_verified_at']
    
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name')
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_verified', 'is_staff', 'is_superuser', 
                      'groups', 'user_permissions'),
        }),
        ('Security', {
            'fields': ('two_factor_enabled', 'two_factor_secret', 'email_verified_at'),
        }),
        ('Referral System', {
            'fields': ('referral_code', 'referred_by'),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )
    
    actions = ['activate_users', 'deactivate_users', 'verify_users']
    
    def investment_count(self, obj):
        """Show user's total investment count."""
        count = obj.investments.count()
        if count > 0:
            url = reverse('admin:investments_investment_changelist') + f'?user__id__exact={obj.id}'
            return format_html('<a href="{}">{} investments</a>', url, count)
        return '0 investments'
    investment_count.short_description = 'Investments'
    
    def activate_users(self, request, queryset):
        """Bulk activate users."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users were successfully activated.')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        """Bulk deactivate users."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users were successfully deactivated.')
    deactivate_users.short_description = 'Deactivate selected users'
    
    def verify_users(self, request, queryset):
        """Bulk verify users."""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} users were successfully verified.')
    verify_users.short_description = 'Verify selected users'


class UserWalletInline(admin.TabularInline):
    """Inline editor for user wallets."""
    model = UserWallet
    extra = 0
    fields = ['currency', 'address', 'label', 'is_primary', 'is_verified']
    readonly_fields = ['created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User profile admin interface."""
    
    list_display = [
        'user', 'phone_number', 'country', 'verification_status', 
        'risk_tolerance', 'preferred_currency', 'created_at'
    ]
    list_filter = [
        'verification_status', 'risk_tolerance', 'preferred_currency', 
        'country', 'created_at'
    ]
    search_fields = ['user__email', 'phone_number', 'country', 'city']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Personal Details', {
            'fields': ('phone_number', 'date_of_birth', 'country', 'city', 
                      'address', 'postal_code')
        }),
        ('KYC Verification', {
            'fields': ('verification_status', 'identity_document', 
                      'proof_of_address', 'selfie_verification')
        }),
        ('Preferences', {
            'fields': ('risk_tolerance', 'preferred_currency')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [UserWalletInline]
    
    actions = ['approve_kyc', 'reject_kyc']
    
    def approve_kyc(self, request, queryset):
        """Bulk approve KYC verification."""
        updated = queryset.update(verification_status='verified')
        # Also update user verification status
        user_ids = queryset.values_list('user_id', flat=True)
        User.objects.filter(id__in=user_ids).update(is_verified=True)
        self.message_user(request, f'{updated} KYC profiles were approved.')
    approve_kyc.short_description = 'Approve KYC verification'
    
    def reject_kyc(self, request, queryset):
        """Bulk reject KYC verification."""
        updated = queryset.update(verification_status='rejected')
        self.message_user(request, f'{updated} KYC profiles were rejected.')
    reject_kyc.short_description = 'Reject KYC verification'


@admin.register(UserWallet)
class UserWalletAdmin(admin.ModelAdmin):
    """User wallet admin interface."""
    
    list_display = [
        'user', 'currency', 'address_short', 'label', 
        'is_primary', 'is_verified', 'created_at'
    ]
    list_filter = ['currency', 'is_primary', 'is_verified', 'created_at']
    search_fields = ['user__email', 'address', 'label']
    readonly_fields = ['created_at', 'updated_at']
    
    def address_short(self, obj):
        """Show shortened address for display."""
        if len(obj.address) > 20:
            return f"{obj.address[:10]}...{obj.address[-10:]}"
        return obj.address
    address_short.short_description = 'Address'
    
    actions = ['verify_wallets', 'unverify_wallets', 'set_as_primary']
    
    def verify_wallets(self, request, queryset):
        """Bulk verify wallets."""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} wallets were verified.')
    verify_wallets.short_description = 'Verify selected wallets'
    
    def unverify_wallets(self, request, queryset):
        """Bulk unverify wallets."""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} wallets were unverified.')
    unverify_wallets.short_description = 'Unverify selected wallets'


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """User activity admin interface."""
    
    list_display = [
        'user', 'action', 'description_short', 'ip_address', 'created_at'
    ]
    list_filter = ['action', 'created_at']
    search_fields = ['user__email', 'action', 'description', 'ip_address']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def description_short(self, obj):
        """Show shortened description."""
        if len(obj.description) > 50:
            return f"{obj.description[:50]}..."
        return obj.description
    description_short.short_description = 'Description'
    
    def has_add_permission(self, request):
        """Don't allow manual creation of activity logs."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make activity logs read-only."""
        return False
