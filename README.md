# AI Trade Report Generator

A professional, multilingual AI-powered market analysis generator that creates comprehensive trade reports using OpenAI's GPT-5. Built with FastAPI and featuring a modern, mobile-responsive web interface with user authentication and report management.

## 🚀 Features

### Core Functionality
- **AI-Powered Analysis**: Uses OpenAI GPT-5 for intelligent market analysis
- **Multilingual Support**: English and Italian language options
- **Professional Reports**: Generates comprehensive HTML reports with market insights
- **PDF Export**: Download reports as PDF with professional formatting
- **Print Support**: Print-friendly report layouts
- **Mobile Responsive**: Fully optimized for desktop, tablet, and mobile devices

### User Management
- **User Authentication**: Secure registration and login system
- **Password Recovery**: Email-based password reset functionality
- **Profile Management**: User profile editing and management
- **Report History**: Save and manage generated reports
- **Session Management**: Secure JWT-based authentication

### User Experience
- **Language Selection Modal**: Choose language on first visit
- **Modern UI/UX**: Professional design with gradient backgrounds and animations
- **Loading Animation**: Engaging splash screen during report generation
- **Touch-Friendly**: Optimized for mobile and touch devices
- **Real-time Translation**: Dynamic UI translation based on language selection
- **Product Search**: Advanced Select2-powered product search with autocomplete

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- **OpenAI API key** for AI report generation
- **Email account** (Gmail recommended) for password recovery
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

## 🛠️ Quick Installation

### Option 1: Automated Setup (Recommended)

#### Windows:
```bash
git clone https://github.com/tkani/AI_Trade_Report.git
cd AI_Trade_Report
setup.bat
```

#### Unix/Linux/macOS:
```bash
git clone https://github.com/tkani/AI_Trade_Report.git
cd AI_Trade_Report
chmod +x setup.sh
./setup.sh
```

#### Cross-platform:
```bash
git clone https://github.com/tkani/AI_Trade_Report.git
cd AI_Trade_Report
python setup.py
```

### Option 2: Manual Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tkani/AI_Trade_Report.git
   cd AI_Trade_Report
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env_example .env
   # Edit .env with your API keys and settings
   ```

5. **Start the application**
   ```bash
   python run_server.py
   ```

## ⚙️ Configuration

### Required Environment Variables

Create a `.env` file with the following configuration:

```env
# Database Configuration
DATABASE_URL=sqlite:///./ai_trade_report.db

# Security Configuration
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Email Configuration (for password recovery)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
EMAIL_FROM=your-email@gmail.com
EMAIL_FROM_NAME=AI Trade Report

# Application Settings
APP_NAME=AI Trade Report
APP_VERSION=1.0.0
DEBUG=False

# Host and Port Configuration
HOST=127.0.0.1
PORT=8000
```

### API Keys Setup

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account and generate an API key
3. Add billing information to your account
4. Add the key to your `.env` file

#### Email Configuration (Gmail)
1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password for "Mail"
3. Use the 16-character app password in your `.env` file

## 🎯 Usage

### 1. First Time Setup
1. **Register an Account**: Create your user account
2. **Login**: Access the main dashboard
3. **Configure Settings**: Set up your preferences

### 2. Generate Reports
1. **Fill the Form**: Enter your business details
   - Brand name
   - Products/services (with advanced search)
   - Investment budget
   - Enterprise size
   - Additional information
2. **Select Options**: Choose AI model and language
3. **Generate**: Click "Generate Report" and wait for processing
4. **View Report**: Review the generated analysis
5. **Save/Export**: Save to your account or export as PDF

### 3. Manage Reports
- **View Saved Reports**: Access your report history
- **Download PDFs**: Export reports for offline use
- **Delete Reports**: Remove unwanted reports
- **Search Reports**: Find specific reports quickly

## 📁 Project Structure

```
AI_Trade_Report/
├── app.py                      # Main FastAPI application
├── run_server.py               # Server runner script
├── generate_prompt.py          # AI prompt generation
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── .env_example               # Environment template
├── INSTALLATION.md            # Detailed installation guide
├── setup.py                   # Cross-platform setup script
├── setup.bat                  # Windows setup script
├── setup.sh                   # Unix/Linux setup script
├── run.bat                    # Windows run script
├── run.sh                     # Unix/Linux run script
├── auth/                      # Authentication module
│   ├── __init__.py
│   ├── auth.py               # JWT and password utilities
│   └── auth_routes.py        # Authentication routes
├── database/                  # Database models
│   ├── __init__.py
│   └── models.py             # SQLAlchemy models
├── schemas/                   # Pydantic schemas
│   ├── __init__.py
│   └── schemas.py            # Data validation schemas
├── services/                  # Business logic services
│   └── email_service.py      # Email sending service
├── static/                    # Static assets
│   ├── css/
│   │   └── style.css         # Main stylesheet
│   ├── js/
│   │   └── main.js           # Frontend JavaScript
│   └── logo_trade_on_chain.png # Application logo
├── templates/                 # HTML templates
│   ├── index.html            # Main dashboard
│   ├── login.html            # Login page
│   ├── register.html         # Registration page
│   ├── profile.html          # User profile
│   ├── forgot_password.html  # Password recovery
│   └── reset_password.html   # Password reset
└── reports/                   # Generated reports (auto-created)
```

## 🔧 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout
- `GET /profile` - User profile
- `POST /profile/update` - Update profile
- `POST /forgot-password` - Request password reset
- `POST /reset-password` - Reset password

### Report Generation
- `POST /generate` - Generate AI report
- `GET /report/{filename}` - View generated report
- `GET /download/{filename}` - Download report
- `POST /save-report` - Save report to account
- `GET /my-reports` - Get user's saved reports
- `DELETE /delete-report/{id}` - Delete saved report

### Search & Data
- `GET /api/search-terms` - Search product terms
- `GET /api/select2-terms` - Select2 search endpoint

### System
- `GET /health` - Health check
- `GET /status` - System status

## 🚀 Running the Application

### Development Mode
```bash
python run_server.py
```

### Production Mode
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app:app

# Using PM2
npm install -g pm2
pm2 start run_server.py --name "ai-trade-report"
```

### Access Points
- **Main Application**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Alternative Docs**: http://127.0.0.1:8000/redoc

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password hashing
- **CORS Protection**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLAlchemy ORM protection
- **Rate Limiting**: Built-in request rate limiting
- **Secure Headers**: Security headers middleware

## 📱 Mobile Support

- **Responsive Design**: Optimized for all screen sizes
- **Touch-Friendly**: Mobile-optimized interface
- **Progressive Web App**: Installable on mobile devices
- **Offline Support**: Basic offline functionality
- **Fast Loading**: Optimized for mobile networks

## 🌐 Internationalization

- **Multi-language Support**: English and Italian
- **Dynamic Translation**: Real-time language switching
- **Localized Content**: Region-specific content
- **RTL Support**: Right-to-left language support ready

## 🛠️ Development

### Prerequisites
- Python 3.8+
- Node.js (for frontend development)
- Git

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/tkani/AI_Trade_Report.git
cd AI_Trade_Report

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env_example .env
# Edit .env with your configuration

# Run development server
python run_server.py
```

### Code Structure
- **Backend**: FastAPI with SQLAlchemy ORM
- **Frontend**: Vanilla JavaScript with modern ES6+
- **Styling**: Custom CSS with CSS Grid and Flexbox
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT with bcrypt password hashing

## 📊 Performance

- **Fast Loading**: Optimized static assets
- **Efficient Queries**: Database query optimization
- **Caching**: Built-in response caching
- **Compression**: Gzip compression enabled
- **CDN Ready**: Static asset CDN support

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

2. **"OpenAI API key not found"**
   - Check `.env` file has correct API key
   - Restart application after adding key

3. **"Email sending failed"**
   - Verify SMTP credentials in `.env`
   - Check 2FA is enabled and app password is used

4. **"Database locked" error**
   - Stop application
   - Delete `ai_trade_report.db`
   - Restart application

5. **"Port already in use"**
   - Change PORT in `.env` file
   - Or kill process using the port

### Getting Help

- Check the [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions
- Review the application logs for error details
- Verify all environment variables are correctly set
- Test individual components (email, API, database)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

## 🎉 Acknowledgments

- OpenAI for providing the GPT-5 API
- FastAPI for the excellent web framework
- SQLAlchemy for database ORM
- All contributors and users

---

**Made with ❤️ for professional market analysis**