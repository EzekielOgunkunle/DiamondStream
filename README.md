# 💎 DiamondStream - Crypto Investment Platform

A comprehensive cryptocurrency investment platform offering structured investment plans with guaranteed returns. Built with Django REST Framework and designed for both retail and institutional investors.

## 🚀 Features

### Investment Plans
- **Beginners Plan** (48 Hours): 1400-1567% ROI
- **VIP Plans** (72 Hours): 900% ROI  
- **VVIP Plans** (7 Days): 900% ROI
- **Multi-Currency Support**: BTC, ETH, DOGE, Platform Wallets

### Platform Capabilities
- 🔐 **Secure Authentication** with JWT tokens
- 📊 **Real-time Portfolio Tracking** with countdown timers
- 💳 **Cryptocurrency Payment Processing**
- 👥 **Referral System** with commission tracking
- 💬 **Live Chat Support** for user assistance
- 📱 **Mobile-Responsive Design**
- 🔒 **Multi-layered Security** with financial compliance
- 📈 **Analytics Dashboard** for admins
- 🔄 **Automated Payout Processing**

## 🛠 Tech Stack

### Backend
- **Django 5.2.4** - Web framework
- **Django REST Framework 3.16.0** - API development
- **PostgreSQL** - Primary database (SQLite for development)
- **Redis** - Caching and sessions (optional fallback)
- **JWT Authentication** - Secure token-based auth

### Security & Compliance
- Input validation with DRF serializers
- CSRF protection and XSS prevention  
- Rate limiting and secure session management
- Environment variable protection
- Audit trails for financial operations

## 📋 Requirements

- Python 3.11+
- Django 5.2.4
- PostgreSQL (production) / SQLite (development)
- Redis (optional, for enhanced performance)

## 🚦 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/DiamondStream.git
cd DiamondStream
```

### 2. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Load Initial Data
```bash
python manage.py populate_initial_data
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin/` for Django admin interface.

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh

### Investment Endpoints  
- `GET /api/investments/plans/` - List investment plans
- `POST /api/investments/create/` - Create new investment
- `GET /api/investments/user/` - User's investments
- `GET /api/investments/dashboard/` - Dashboard statistics

### User Management
- `GET /api/users/profile/` - User profile
- `PUT /api/users/profile/` - Update profile
- `GET /api/users/wallets/` - User wallets
- `GET /api/users/activity/` - User activity log

## 🏗 Project Structure

```
DiamondStream/
├── diamondstream/          # Main project settings
├── users/                  # User management app
├── investments/            # Investment plans and tracking
├── payments/              # Payment processing
├── notifications/         # Notification system
├── analytics/            # Analytics and reporting
├── chat/                 # Live chat support
├── templates/            # HTML templates
├── static/              # Static files
├── requirements.txt     # Python dependencies
└── manage.py           # Django management script
```

## 🔧 Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```

### Investment Plans Configuration
Investment plans are automatically populated using the management command:
```bash
python manage.py populate_initial_data
```

## 🎯 Target Audience

- **Beginner Investors (60%)**: Ages 20-40, new to crypto, $200-$5K investment capacity
- **Intermediate Investors (30%)**: Ages 25-50, some crypto experience, $2K-$50K capacity  
- **High-Value Investors (10%)**: Ages 30-60, advanced knowledge, 3+ BTC capacity

## 📊 Business Model

- Structured investment plans with time-locked returns
- Multi-tier investment options (Beginners/VIP/VVIP)
- Cryptocurrency payment processing
- Commission-based referral system
- Administrative oversight and approval workflows

## 🛡 Security Features

- Multi-layered authentication system
- Secure cryptocurrency wallet integration
- Financial transaction audit trails
- Rate limiting and DDoS protection
- Input validation and sanitization
- HTTPS enforcement and secure headers

## 🚀 Deployment

### Production Setup
1. Configure PostgreSQL database
2. Set up Redis for caching
3. Configure environment variables
4. Run migrations and collect static files
5. Use Gunicorn + Nginx for production serving

### Docker Support
```bash
# Build and run with Docker
docker-compose up --build
```

## 📈 Monitoring & Analytics

- Real-time investment tracking
- User activity monitoring  
- Payment verification systems
- Performance metrics and reporting
- Administrative dashboard with insights

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 📞 Support

For support and inquiries:
- Create an issue in this repository
- Contact the development team
- Check the documentation in `/docs`

## 🎯 Success Metrics

- **User Acquisition**: 5,000 active investors within 6 months
- **Investment Volume**: $10M total investments within 12 months  
- **Payout Success**: 100% successful payout rate
- **Platform Uptime**: 99.9% availability
- **User Satisfaction**: 95+ NPS score

---

**Built with ❤️ for the crypto investment community**
