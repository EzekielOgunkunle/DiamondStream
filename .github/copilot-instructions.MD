# DiamondStream - Crypto Investment Platform

DiamondStream is a cryptocurrency investment platform offering structured investment plans with guaranteed returns. This document consolidates the technical and architectural guidelines (originally from `copilot-instructions.md`) and the functional requirements table (originally from `PRD.md`), adapted to use Django and Django REST Framework (DRF) for the backend instead of Node.js. It provides best practices and references to the latest documentation to guide development.

## Project Context

- **Platform Type:** Crypto Investment Management Platform
- **Business Model:** Structured investment plans with guaranteed returns
- **Tech Stack:** React.js + TypeScript (Frontend), Django + DRF (Backend), PostgreSQL + Redis (Database)
- **Key Features:** Investment plans, admin management, payment processing, user tracking, real-time portfolio monitoring
- **Target Audience:**
  - **Beginner Investors (60%):** Ages 20-40, new to crypto, $200-$5,000 investment capacity
  - **Intermediate Investors (30%):** Ages 25-50, some crypto experience, $2,000-$50,000 capacity
  - **High-Value Investors (10%):** Ages 30-60, advanced crypto knowledge, 3+ BTC capacity

## Product Goals and Objectives

### Primary Goals

1. **Security First:** Implement industry-leading security measures
2. **Regulatory Compliance:** Adhere to financial regulations
3. **User Experience:** Provide intuitive, mobile-first design
4. **Educational Platform:** Offer learning resources for crypto investing
5. **Institutional Ready:** Support retail and institutional investors

### Success Metrics

- **User Acquisition:** 5,000 active investors within 6 months
- **Investment Volume:** $10M in total investments within 12 months
- **Payout Success Rate:** 100% successful payouts
- **Platform Uptime:** 99.9% uptime
- **User Satisfaction:** 95+ NPS score

## Investment Plans

- **Beginners Plan (48 Hours):**
  - $200 → $3,000 (1400% ROI)
  - $300 → $5,000 (1567% ROI)
  - Payment Methods: BTC, ETH, DOGE, Platform Wallets
- **VIP Plans (72 Hours):**
  - $2,000 → $20,000 (900% ROI)
  - $3,000 → $30,000 (900% ROI)
  - $5,000 → $50,000 (900% ROI)
  - Payment Methods: BTC, ETH, DOGE, Platform Wallets
- **VVIP Plans (7 Days):**
  - 3 BTC → 30 BTC (900% ROI)
  - 5 BTC → 50 BTC (900% ROI)
  - 10 BTC → 100 BTC (900% ROI)
  - Payment Methods: BTC only

## Functional Requirements Table

| Requirement | Description | User Story | Expected Behaviour/Results |
|-------------|-------------|------------|---------------------------|
| **User Registration** | Users can create accounts with email verification | As a new user, I want to register for an account so that I can start investing | User receives email verification, creates password, account is activated |
| **Investment Plan Selection** | Users can view and select from available investment plans | As a user, I want to see all available investment plans so that I can choose the best option for me | Display of all plans with ROI, duration, and minimum investment clearly shown |
| **Crypto Payment Submission** | Users can submit investments by transferring crypto to provided wallets | As a user, I want to easily send my crypto investment so that I can start earning returns | User receives wallet address, submits transaction hash, payment is verified |
| **Investment Tracking** | Users can track their active investments and countdown timers | As a user, I want to see the status of my investments so that I know when to expect returns | Dashboard shows active investments, time remaining, expected payout amount |
| **Payout Processing** | Admin processes returns to user wallets at plan completion | As a user, I want to receive my returns automatically so that I can access my earnings | Returns are sent to user's wallet address within 24 hours of plan completion |
| **Live Chat Support** | Users can chat with support team for assistance | As a user, I want to get help quickly so that I can resolve any issues | Real-time chat interface connects user to available support agent |
| **Admin Dashboard** | Admins can manage users, investments, and transactions | As an admin, I want to oversee all platform activity so that I can manage operations efficiently | Comprehensive dashboard showing all users, investments, pending payments, chat requests |
| **Super Admin Control** | Super admin can manage all admin accounts and permissions | As a super admin, I want to control admin access so that I can maintain security | Ability to create/edit/delete admin accounts, set specific permissions per admin |
| **Payment Verification** | System verifies incoming crypto payments automatically | As an admin, I want payment verification to be automated so that I can process investments faster | Blockchain integration checks payment amounts and confirms transactions |
| **Wallet Management** | Admins can manage multiple crypto wallet addresses | As an admin, I want to manage wallet addresses so that I can organize incoming payments | Interface to add/remove/monitor wallet addresses for BTC, ETH, DOGE |
| **Investment History** | Users can view complete history of all investments | As a user, I want to see my investment history so that I can track my performance | Complete list of past investments with dates, amounts, returns, and status |
| **Referral System** | Users can refer others and earn commissions | As a user, I want to earn from referrals so that I can increase my income | Unique referral links generate commissions when new users invest |
| **Mobile Responsive** | Platform works seamlessly on mobile devices | As a user, I want to access the platform on my phone so that I can manage investments anywhere | Fully responsive design that works on all mobile devices |
| **Security Features** | Platform implements security measures to protect user data | As a user, I want my data to be secure so that I can invest with confidence | SSL encryption, secure authentication, data protection measures |
| **Notification System** | Users receive notifications about investment status | As a user, I want to be notified about my investments so that I stay informed | Email and in-app notifications for investment confirmations, completions, payouts |
| **Content Management** | Super admin can update website content through CMS | As a super admin, I want to update website content easily so that I can maintain fresh information | CMS interface allows editing of pages, investment plans, announcements |
| **User Verification** | Basic user verification for account security | As a platform, we want to verify users so that we can prevent fraud | Identity verification process with document upload and approval workflow |
| **Analytics Dashboard** | Admins can view platform analytics and metrics | As an admin, I want to see platform metrics so that I can make informed decisions | Analytics showing user activity, investment volumes, conversion rates |
| **Backup Systems** | Platform has backup and recovery systems | As a platform owner, I want data backup so that we can recover from disasters | Automated daily backups with disaster recovery procedures |
| **Multi-Currency Support** | Platform supports BTC, ETH, DOGE payments | As a user, I want payment options so that I can invest with my preferred crypto | Wallet integration for multiple cryptocurrencies with automatic conversion |
| **Two-Factor Authentication** | Enhanced security with 2FA for user accounts | As a user, I want extra security so that my account is protected from unauthorized access | SMS/Google Authenticator integration with mandatory 2FA for withdrawals |
| **Payment Proof Upload** | Users can upload screenshots of crypto transfers | As a user, I want to provide proof of payment so that my investment is processed faster | File upload interface accepts images, automatic processing by admin |
| **Countdown Timers** | Live countdown showing time remaining for payouts | As a user, I want to see exactly when my investment matures so that I can plan accordingly | Real-time countdown timer displaying days, hours, minutes until payout |
| **Investment Status Tracking** | Visual indicators showing investment progress | As a user, I want to see my investment status clearly so that I understand the current stage | Status badges: Pending, Confirmed, Active, Matured, Paid with color coding |
| **Bulk Payment Processing** | Admins can process multiple payouts simultaneously | As an admin, I want to process multiple payments at once so that I can work more efficiently | Batch selection interface with one-click bulk processing and confirmation |
| **User Activity Monitoring** | Track all user actions for security purposes | As an admin, I want to monitor user activity so that I can detect suspicious behavior | Comprehensive activity log showing logins, transactions, profile changes |
| **Emergency Admin Access** | Secondary admin access for critical situations | As a super admin, I want backup access so that platform operations can continue if primary admin is unavailable | Secondary admin credentials with limited but critical platform access |
| **Maintenance Mode** | Ability to put platform in maintenance mode | As an admin, I want to perform maintenance so that I can update the platform safely | Maintenance page display with estimated downtime and admin-only access |
| **Dispute Resolution** | System for handling payment disputes | As an admin, I want to handle disputes systematically so that issues are resolved fairly | Dispute tracking system with evidence upload and resolution workflow |

## Architecture Guidelines

### Frontend (React + TypeScript)

- Use functional components with hooks
- Implement atomic design pattern (atoms → molecules → organisms → pages)
- Use React Query/TanStack Query for server state management
- Apply strict TypeScript with proper type definitions
- Follow component-based architecture with clear separation of concerns
- **References:**
  - [React 18 Documentation](https://react.dev/)
  - [TypeScript Handbook](https://www.typescriptlang.org/docs/)
  - [TanStack Query Documentation](https://tanstack.com/query/latest)
  - [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)

### Backend (Django + DRF)

- Use Django with DRF for RESTful API development
- Implement modular app structure (e.g., users, investments, payments)
- Use Python type hints for type safety
- Apply layered architecture: URLs → views → serializers → services → models
- Implement error handling with DRF’s exception handling
- **References:**
  - [Django Documentation](https://docs.djangoproject.com/en/stable/)
  - [Django REST Framework Documentation](https://www.django-rest-framework.org/)
  - [Django Channels Documentation](https://channels.readthedocs.io/en/stable/)
  - [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Database Design

- **PostgreSQL** for primary data storage
- **Redis** for caching and session management
- Use proper indexing for performance
- Implement database transactions for financial operations
- **References:**
  - [PostgreSQL Documentation](https://www.postgresql.org/docs/)
  - [Django ORM Optimization](https://docs.djangoproject.com/en/stable/topics/db/optimization/)
  - [Redis Documentation](https://redis.io/docs/)

## Security & Compliance

- **Security First:** Multi-layered security for financial operations
- **Authentication:** Use DRF Simple JWT with role-based access control (RBAC)
- **Data Validation:** Use DRF serializers and Pydantic for runtime validation
- **Crypto Security:** Never store private keys; use environment variables
- **API Security:** Implement rate limiting, input sanitization, and CORS
- **Compliance:** Follow financial regulations, implement audit trails
- **References:**
  - [DRF Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
  - [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
  - [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)
  - [Cryptocurrency Security Standard](https://cryptoconsortium.github.io/CCSS/)

## Key Features Implementation

### User Management

- User registration with email verification
- KYC/AML compliance integration
- Multi-wallet support (BTC, ETH, DOGE)
- Investment history and portfolio tracking
- Real-time status updates with countdown timers

### Admin System

- Super admin with full platform control
- Regular admins with limited permissions
- Bulk payment processing capabilities
- Investment verification and approval workflow
- Comprehensive analytics dashboard

### Investment Processing

- Real-time crypto price integration via APIs
- Automated payment verification using blockchain APIs
- Investment maturity calculation and tracking
- Automated return calculation based on plan parameters
- Payment processing and payout management
- **References:**
  - [Web3.py Documentation](https://web3py.readthedocs.io/)
  - [CoinGecko API](https://www.coingecko.com/en/api/documentation)

## UI/UX Guidelines

- **Design System:** Crypto-themed aesthetics with Tailwind CSS
- **Responsiveness:** Mobile-first design
- **Accessibility:** WCAG 2.1 compliance
- **Performance:** Optimize for fast loading times
- **Real-time Updates:** Use Django Channels for WebSocket updates
- **User Feedback:** Clear status indicators and progress tracking
- **References:**
  - [Tailwind CSS Documentation](https://tailwindcss.com/docs)
  - [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
  - [Django Channels Documentation](https://channels.readthedocs.io/en/stable/)

## Testing Strategy

- Unit tests for Django models, services, and views using pytest
- Integration tests for API endpoints
- E2E tests for critical user journeys using Playwright
- Security testing for vulnerabilities
- Performance testing for scalability
- **References:**
  - [Pytest Documentation](https://docs.pytest.org/)
  - [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
  - [Playwright Documentation](https://playwright.dev/)

## Performance & Monitoring

- Implement Django caching with Redis
- Optimize database queries with Django ORM
- Use Django Prometheus for real-time monitoring
- Error tracking with Sentry
- Performance metrics with New Relic
- **References:**
  - [Django Redis Cache](https://github.com/jazzband/django-redis)
  - [Django Prometheus](https://github.com/korfuri/django-prometheus)
  - [Sentry Documentation](https://docs.sentry.io/)
  - [New Relic Documentation](https://docs.newrelic.com/)

## Code Quality Standards

- Use Flake8 and Black for code formatting
- Implement pre-commit hooks with pre-commit
- Follow PEP 8 style guidelines
- Maintain high test coverage (>80%)
- Use descriptive variable/function names
- Add comprehensive docstrings
- **References:**
  - [Flake8 Documentation](https://flake8.pycqa.org/)
  - [Black Documentation](https://black.readthedocs.io/)
  - [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
  - [pre-commit Documentation](https://pre-commit.com/)

## State Management

- **React Context + useReducer** for global state
- **React Query/TanStack Query** for server state
- **Zustand** for simple client state if needed
- **References:**
  - [React Context](https://react.dev/learn/passing-data-deeply-with-context)
  - [Zustand Documentation](https://zustand.docs.pmnd.rs/)

## Security Checklist

- [ ] Input validation on all forms (DRF serializers, Pydantic)
- [ ] SQL injection prevention (Django ORM)
- [ ] XSS protection (Django templates, input sanitization)
- [ ] CSRF protection (Django CSRF middleware)
- [ ] Rate limiting (django-ratelimit)
- [ ] Secure session management (Django sessions)
- [ ] Password hashing with Django’s default hasher
- [ ] Environment variable protection
- [ ] HTTPS enforcement
- [ ] Content Security Policy headers
- **References:**
  - [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
  - [django-ratelimit](https://github.com/jsocol/django-ratelimit)

## Environment Configuration

- Use environment variables for sensitive data (e.g., `SECRET_KEY`, `ENCRYPTION_KEY`)
- Configure PostgreSQL, Redis, and third-party services (SMTP, Twilio)
- **References:**
  - [Django Environment Variables](https://django-environ.readthedocs.io/)
  - [Twelve-Factor App](https://12factor.net/)

## Deployment Guidelines

- Use Docker with Gunicorn for Django deployment
- Implement health check endpoints
- Configure auto-scaling on AWS/Digital Ocean
- **References:**
  - [Docker Documentation](https://docs.docker.com/)
  - [Gunicorn Documentation](https://gunicorn.org/)
  - [AWS Documentation](https://docs.aws.amazon.com/)
  - [Digital Ocean Docs](https://docs.digitalocean.com/)

## Monitoring & Logging

- Use Django StructLog for structured logging
- Monitor performance with Prometheus and Grafana
- Track errors with Sentry
- **References:**
  - [Django StructLog](https://github.com/jrobichaud/django-structlog)
  - [Prometheus Documentation](https://prometheus.io/docs/)
  - [Grafana Documentation](https://grafana.com/docs/)

## Code Generation Guidelines

When generating code, ensure:

1. Follow latest Django/DRF documentation
2. Adhere to PEP 8 and Django coding standards
3. Use Python type hints and Pydantic for validation
4. Implement security-first patterns
5. Optimize for performance with Django ORM and caching
6. Include comprehensive error handling
7. Follow WCAG accessibility guidelines
8. Write tests with pytest
9. Use strict TypeScript in frontend
10. Leverage modern React patterns (hooks, suspense)

---

**Document Status:** Draft v1.1  
**Last Updated:** July 19, 2025  
**Next Review:** August 1, 2025
