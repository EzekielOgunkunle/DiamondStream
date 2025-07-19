"""
Django management command to populate initial investment plans and platform data.
Creates the investment plans as defined in the project requirements.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from investments.models import InvestmentPlan
from payments.models import PlatformWallet
from notifications.models import NotificationTemplate


class Command(BaseCommand):
    help = 'Populate initial data for DiamondStream platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            InvestmentPlan.objects.all().delete()
            PlatformWallet.objects.all().delete()
            NotificationTemplate.objects.all().delete()

        self.create_investment_plans()
        self.create_platform_wallets()
        self.create_notification_templates()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated initial data!')
        )

    def create_investment_plans(self):
        """Create investment plans as per requirements."""
        self.stdout.write('Creating investment plans...')
        
        # Beginners Plans (48 Hours)
        beginners_plans = [
            {
                'name': 'Beginners Plan - $200',
                'description': 'Perfect for newcomers to cryptocurrency investment',
                'min_amount': 200,
                'max_amount': 200,
                'return_amount': 3000,
                'roi_percentage': 1400,  # 1400% ROI
                'duration_hours': 48,
            },
            {
                'name': 'Beginners Plan - $300',
                'description': 'Enhanced beginners investment option',
                'min_amount': 300,
                'max_amount': 300,
                'return_amount': 5000,
                'roi_percentage': 1567,  # ~1567% ROI
                'duration_hours': 48,
            },
        ]
        
        for plan_data in beginners_plans:
            plan, created = InvestmentPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults={
                    'plan_type': 'beginners',
                    'description': plan_data['description'],
                    'min_amount': plan_data['min_amount'],
                    'max_amount': plan_data['max_amount'],
                    'currency': 'USD',
                    'roi_percentage': plan_data['roi_percentage'],
                    'return_amount': plan_data['return_amount'],
                    'duration_hours': plan_data['duration_hours'],
                    'max_investments_per_user': 5,
                    'allowed_payment_methods': ['BTC', 'ETH', 'DOGE', 'PLATFORM_WALLET'],
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'  Created: {plan.name}')
        
        # VIP Plans (72 Hours)
        vip_plans = [
            {
                'name': 'VIP Plan - $2,000',
                'description': 'Premium investment for serious investors',
                'min_amount': 2000,
                'max_amount': 2000,
                'return_amount': 20000,
                'roi_percentage': 900,  # 900% ROI
                'duration_hours': 72,
            },
            {
                'name': 'VIP Plan - $3,000',
                'description': 'Enhanced VIP investment opportunity',
                'min_amount': 3000,
                'max_amount': 3000,
                'return_amount': 30000,
                'roi_percentage': 900,  # 900% ROI
                'duration_hours': 72,
            },
            {
                'name': 'VIP Plan - $5,000',
                'description': 'Maximum VIP investment tier',
                'min_amount': 5000,
                'max_amount': 5000,
                'return_amount': 50000,
                'roi_percentage': 900,  # 900% ROI
                'duration_hours': 72,
            },
        ]
        
        for plan_data in vip_plans:
            plan, created = InvestmentPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults={
                    'plan_type': 'vip',
                    'description': plan_data['description'],
                    'min_amount': plan_data['min_amount'],
                    'max_amount': plan_data['max_amount'],
                    'currency': 'USD',
                    'roi_percentage': plan_data['roi_percentage'],
                    'return_amount': plan_data['return_amount'],
                    'duration_hours': plan_data['duration_hours'],
                    'max_investments_per_user': 3,
                    'allowed_payment_methods': ['BTC', 'ETH', 'DOGE', 'PLATFORM_WALLET'],
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'  Created: {plan.name}')
        
        # VVIP Plans (7 Days)
        vvip_plans = [
            {
                'name': 'VVIP Plan - 3 BTC',
                'description': 'Exclusive Bitcoin-only investment for high-value investors',
                'min_amount': 3,
                'max_amount': 3,
                'return_amount': 30,
                'roi_percentage': 900,  # 900% ROI
                'duration_days': 7,
            },
            {
                'name': 'VVIP Plan - 5 BTC',
                'description': 'Premium Bitcoin investment tier',
                'min_amount': 5,
                'max_amount': 5,
                'return_amount': 50,
                'roi_percentage': 900,  # 900% ROI
                'duration_days': 7,
            },
            {
                'name': 'VVIP Plan - 10 BTC',
                'description': 'Ultimate Bitcoin investment opportunity',
                'min_amount': 10,
                'max_amount': 10,
                'return_amount': 100,
                'roi_percentage': 900,  # 900% ROI
                'duration_days': 7,
            },
        ]
        
        for plan_data in vvip_plans:
            plan, created = InvestmentPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults={
                    'plan_type': 'vvip',
                    'description': plan_data['description'],
                    'min_amount': plan_data['min_amount'],
                    'max_amount': plan_data['max_amount'],
                    'currency': 'BTC',
                    'roi_percentage': plan_data['roi_percentage'],
                    'return_amount': plan_data['return_amount'],
                    'duration_days': plan_data['duration_days'],
                    'max_investments_per_user': 1,
                    'allowed_payment_methods': ['BTC'],
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'  Created: {plan.name}')

    def create_platform_wallets(self):
        """Create platform wallets for receiving payments."""
        self.stdout.write('Creating platform wallets...')
        
        wallets = [
            {
                'currency': 'BTC',
                'address': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
                'label': 'Primary Bitcoin Wallet',
                'is_primary': True,
                'is_active': True,
            },
            {
                'currency': 'ETH',
                'address': '0x742d35Cc6634C0532925a3b8D2ff6e2166Bb2e33',
                'label': 'Primary Ethereum Wallet',
                'is_primary': True,
                'is_active': True,
            },
            {
                'currency': 'DOGE',
                'address': 'DG2mPCnCPXzbwiqKpE1husv3FA9s5t1WMt',
                'label': 'Primary Dogecoin Wallet',
                'is_primary': True,
                'is_active': True,
            },
        ]
        
        for wallet_data in wallets:
            wallet, created = PlatformWallet.objects.get_or_create(
                address=wallet_data['address'],
                defaults=wallet_data
            )
            if created:
                self.stdout.write(f'  Created: {wallet.currency} wallet - {wallet.label}')

    def create_notification_templates(self):
        """Create notification templates."""
        self.stdout.write('Creating notification templates...')
        
        templates = [
            {
                'name': 'Welcome Email',
                'notification_type': 'welcome',
                'channel': 'email',
                'subject': 'Welcome to DiamondStream - Your Investment Journey Begins!',
                'title': 'Welcome to DiamondStream',
                'content': '''Dear {{user_name}},

Welcome to DiamondStream, the premier cryptocurrency investment platform!

We're excited to have you join our community of successful investors. Here's what you can do next:

1. Complete your profile verification (KYC)
2. Add your cryptocurrency wallet addresses
3. Explore our investment plans
4. Start your first investment

If you have any questions, our support team is here to help 24/7.

Best regards,
The DiamondStream Team''',
                'html_content': '''<h2>Welcome to DiamondStream!</h2>
<p>Dear {{user_name}},</p>
<p>Welcome to DiamondStream, the premier cryptocurrency investment platform!</p>
<p>We're excited to have you join our community of successful investors.</p>''',
                'auto_send': True,
                'priority': 'medium',
            },
            {
                'name': 'Investment Created',
                'notification_type': 'investment_created',
                'channel': 'email',
                'subject': 'Investment Created - {{plan_name}}',
                'title': 'Investment Created Successfully',
                'content': '''Your investment has been created successfully!

Investment Details:
- Plan: {{plan_name}}
- Amount: {{amount}} {{currency}}
- Expected Return: {{expected_return}} {{currency}}
- Maturity Date: {{maturity_date}}

Please send your payment to complete the investment.''',
                'auto_send': True,
                'priority': 'high',
            },
            {
                'name': 'Payment Confirmed',
                'notification_type': 'payment_confirmed',
                'channel': 'email',
                'subject': 'Payment Confirmed - Investment Activated',
                'title': 'Payment Confirmed',
                'content': '''Great news! Your payment has been confirmed and your investment is now active.

Your investment will mature on {{maturity_date}} and you will receive {{expected_return}} {{currency}}.

Thank you for investing with DiamondStream!''',
                'auto_send': True,
                'priority': 'high',
            },
        ]
        
        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                self.stdout.write(f'  Created: {template.name}')
