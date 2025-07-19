"""
DiamondStream Investment URLs

URL configuration for investment-related API endpoints.
"""

from django.urls import path
from .views import (
    InvestmentPlanListView, InvestmentPlanDetailView, InvestmentCreateView,
    InvestmentListView, InvestmentDetailView, InvestmentHistoryListView,
    ReferralCommissionListView, investment_stats, user_investment_summary,
    referral_stats, cancel_investment
)

app_name = 'investments'

urlpatterns = [
    # Investment plan endpoints
    path('plans/', InvestmentPlanListView.as_view(), name='plan-list'),
    path('plans/<int:pk>/', InvestmentPlanDetailView.as_view(), name='plan-detail'),
    
    # Investment management endpoints
    path('create/', InvestmentCreateView.as_view(), name='investment-create'),
    path('', InvestmentListView.as_view(), name='investment-list'),
    path('<int:pk>/', InvestmentDetailView.as_view(), name='investment-detail'),
    path('<int:investment_id>/cancel/', cancel_investment, name='investment-cancel'),
    
    # Investment history
    path('<int:investment_id>/history/', InvestmentHistoryListView.as_view(), name='investment-history'),
    
    # Statistics and summaries
    path('stats/', investment_stats, name='investment-stats'),
    path('summary/', user_investment_summary, name='investment-summary'),
    
    # Referral system
    path('referrals/commissions/', ReferralCommissionListView.as_view(), name='referral-commissions'),
    path('referrals/stats/', referral_stats, name='referral-stats'),
]
