"""
DiamondStream Investment Admin

Django admin configuration for investment management.
Provides admin interface for plans, investments, history, and referral commissions.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import InvestmentPlan, Investment, InvestmentHistory, ReferralCommission


@admin.register(InvestmentPlan)
class InvestmentPlanAdmin(admin.ModelAdmin):
    """Investment plan admin interface."""
    
    list_display = [
        'name', 'plan_type', 'min_amount', 'max_amount', 'currency',
        'roi_percentage', 'duration_str', 'is_active', 'investment_count'
    ]
    list_filter = ['plan_type', 'currency', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'used_slots', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'plan_type', 'description', 'is_active')
        }),
        ('Investment Details', {
            'fields': ('min_amount', 'max_amount', 'currency', 'roi_percentage', 'return_amount')
        }),
        ('Duration', {
            'fields': ('duration_hours', 'duration_days')
        }),
        ('Availability', {
            'fields': ('max_investments_per_user', 'total_slots', 'used_slots')
        }),
        ('Payment Methods', {
            'fields': ('allowed_payment_methods',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def investment_count(self, obj):
        """Show total investments for this plan."""
        count = obj.investments.count()
        if count > 0:
            url = reverse('admin:investments_investment_changelist') + f'?plan__id__exact={obj.id}'
            return format_html('<a href="{}">{} investments</a>', url, count)
        return '0 investments'
    investment_count.short_description = 'Total Investments'
    
    actions = ['activate_plans', 'deactivate_plans']
    
    def activate_plans(self, request, queryset):
        """Bulk activate plans."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} plans were activated.')
    activate_plans.short_description = 'Activate selected plans'
    
    def deactivate_plans(self, request, queryset):
        """Bulk deactivate plans."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} plans were deactivated.')
    deactivate_plans.short_description = 'Deactivate selected plans'


class InvestmentHistoryInline(admin.TabularInline):
    """Inline editor for investment history."""
    model = InvestmentHistory
    extra = 0
    readonly_fields = ['created_at']
    fields = ['status_from', 'status_to', 'notes', 'changed_by', 'created_at']


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    """Investment admin interface."""
    
    list_display = [
        'id_short', 'user', 'plan', 'amount', 'currency', 'status',
        'created_at', 'maturity_date', 'time_remaining', 'roi_display'
    ]
    list_filter = [
        'status', 'currency', 'payment_method', 'plan__plan_type',
        'created_at', 'maturity_date'
    ]
    search_fields = [
        'user__email', 'transaction_hash', 'payout_transaction_hash',
        'id', 'plan__name'
    ]
    readonly_fields = [
        'id', 'created_at', 'maturity_date', 'roi_percentage',
        'time_until_maturity', 'is_matured'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Investment Details', {
            'fields': ('user', 'plan', 'amount', 'currency', 'expected_return', 'payment_method')
        }),
        ('Status & Dates', {
            'fields': ('status', 'created_at', 'payment_submitted_at', 
                      'confirmed_at', 'maturity_date', 'completed_at')
        }),
        ('Payment Information', {
            'fields': ('transaction_hash', 'payment_address', 'payment_proof'),
            'classes': ('collapse',)
        }),
        ('Admin Notes', {
            'fields': ('admin_notes', 'verified_by'),
            'classes': ('collapse',)
        }),
        ('Payout Information', {
            'fields': ('payout_transaction_hash', 'payout_address', 'payout_amount'),
            'classes': ('collapse',)
        }),
        ('Calculated Fields', {
            'fields': ('roi_percentage', 'time_until_maturity', 'is_matured'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [InvestmentHistoryInline]
    
    def id_short(self, obj):
        """Show shortened ID."""
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def time_remaining(self, obj):
        """Show time remaining until maturity."""
        if obj.is_matured:
            return format_html('<span style="color: green;">✓ Matured</span>')
        
        remaining = obj.time_until_maturity
        if remaining.days > 0:
            return f"{remaining.days}d {remaining.seconds//3600}h"
        else:
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    time_remaining.short_description = 'Time Remaining'
    
    def roi_display(self, obj):
        """Show ROI percentage with color coding."""
        roi = obj.roi_percentage
        if roi >= 500:
            color = 'green'
        elif roi >= 100:
            color = 'orange'
        else:
            color = 'red'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, roi)
    roi_display.short_description = 'ROI %'
    
    actions = [
        'confirm_payments', 'activate_investments', 'process_payouts',
        'cancel_investments'
    ]
    
    def confirm_payments(self, request, queryset):
        """Bulk confirm payments."""
        updated = queryset.filter(status='payment_submitted').update(
            status='confirmed',
            confirmed_at=timezone.now()
        )
        self.message_user(request, f'{updated} payments were confirmed.')
    confirm_payments.short_description = 'Confirm payments'
    
    def activate_investments(self, request, queryset):
        """Bulk activate investments."""
        updated = queryset.filter(status='confirmed').update(status='active')
        self.message_user(request, f'{updated} investments were activated.')
    activate_investments.short_description = 'Activate investments'
    
    def process_payouts(self, request, queryset):
        """Mark investments as paid."""
        updated = queryset.filter(status='matured').update(
            status='paid',
            completed_at=timezone.now()
        )
        self.message_user(request, f'{updated} investments were marked as paid.')
    process_payouts.short_description = 'Mark as paid'
    
    def cancel_investments(self, request, queryset):
        """Cancel investments."""
        updated = queryset.exclude(status__in=['paid', 'cancelled']).update(
            status='cancelled'
        )
        self.message_user(request, f'{updated} investments were cancelled.')
    cancel_investments.short_description = 'Cancel investments'


@admin.register(InvestmentHistory)
class InvestmentHistoryAdmin(admin.ModelAdmin):
    """Investment history admin interface."""
    
    list_display = [
        'investment', 'status_from', 'status_to', 'changed_by', 'created_at'
    ]
    list_filter = ['status_from', 'status_to', 'created_at']
    search_fields = ['investment__id', 'investment__user__email', 'notes']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """Don't allow manual creation."""
        return False


@admin.register(ReferralCommission)
class ReferralCommissionAdmin(admin.ModelAdmin):
    """Referral commission admin interface."""
    
    list_display = [
        'referrer', 'referred_user', 'commission_amount', 'currency',
        'commission_rate', 'status', 'created_at'
    ]
    list_filter = ['currency', 'status', 'created_at']
    search_fields = [
        'referrer__email', 'referred_user__email', 
        'investment__id'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Commission Details', {
            'fields': ('referrer', 'referred_user', 'investment')
        }),
        ('Amount & Rate', {
            'fields': ('commission_rate', 'commission_amount', 'currency')
        }),
        ('Status & Payout', {
            'fields': ('status', 'paid_at', 'payout_transaction_hash')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_paid', 'mark_as_earned']
    
    def mark_as_paid(self, request, queryset):
        """Mark commissions as paid."""
        updated = queryset.filter(status='earned').update(
            status='paid',
            paid_at=timezone.now()
        )
        self.message_user(request, f'{updated} commissions were marked as paid.')
    mark_as_paid.short_description = 'Mark as paid'
    
    def mark_as_earned(self, request, queryset):
        """Mark commissions as earned."""
        updated = queryset.filter(status='pending').update(status='earned')
        self.message_user(request, f'{updated} commissions were marked as earned.')
    mark_as_earned.short_description = 'Mark as earned'
