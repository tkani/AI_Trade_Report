# AI Trade Report - Installation Guide

This guide provides step-by-step instructions for installing and configuring the AI Trade Report application.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Configuration](#configuration)
4. [API Keys Setup](#api-keys-setup)
5. [Database Setup](#database-setup)
6. [Email Configuration](#email-configuration)
7. [Running the Application](#running-the-application)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

Before installing the application, ensure you have:

- **Python 3.8+** installed on your system
- **Git** for cloning the repository
- **Internet connection** for downloading dependencies
- **OpenAI API key** for AI report generation
- **Email account** (Gmail recommended) for password recovery

### Check Python Installation
```bash
python --version
# or
python3 --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/)

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/tkani/AI_Trade_Report.git
cd AI_Trade_Report
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create Environment Configuration File
```bash
# Copy the example environment file
copy .env_example .env
# On macOS/Linux:
cp .env_example .env
```

## Configuration

### 1. Environment Variables (.env file)

Edit the `.env` file with your specific configuration:

```env
# Database Configuration
DATABASE_URL=sqlite:///./ai_trade_report.db

# JWT Security
SECRET_KEY=your-super-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

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

### 2. Host and URL Configuration

#### For Local Development:
```env
HOST=127.0.0.1
PORT=8000
```

#### For Production/Server:
```env
HOST=0.0.0.0
PORT=8000
```

#### For Custom Domain:
Update the following files if using a custom domain:

**In `app.py` (if needed):**
```python
# Update CORS origins if using custom domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "https://www.yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**In email templates** (if sending emails with custom domain):
- Update email links to point to your domain
- Update any hardcoded URLs in templates

## API Keys Setup

### 1. OpenAI API Key

1. **Create OpenAI Account:**
   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Sign up or log in to your account

2. **Generate API Key:**
   - Navigate to API Keys section
   - Click "Create new secret key"
   - Copy the generated key
   - Add it to your `.env` file:
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. **Add Billing Information:**
   - Add a payment method to your OpenAI account
   - Set usage limits to control costs

### 2. Email API Configuration

#### Gmail Setup (Recommended):

1. **Enable 2-Factor Authentication:**
   - Go to Google Account settings
   - Enable 2-Step Verification

2. **Generate App Password:**
   - Go to Google Account → Security
   - Under "2-Step Verification", click "App passwords"
   - Generate a new app password for "Mail"
   - Copy the 16-character password

3. **Update .env file:**
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-16-character-app-password
   EMAIL_FROM=your-email@gmail.com
   EMAIL_FROM_NAME=AI Trade Report
   ```

#### Other Email Providers:

**Outlook/Hotmail:**
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

**Yahoo:**
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

**Custom SMTP:**
```env
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
```

## Database Setup

The application uses SQLite by default. The database will be created automatically on first run.

### Database Location:
- **File:** `ai_trade_report.db`
- **Location:** Project root directory
- **Type:** SQLite (included with Python)

### Database Tables (Auto-created):
- `users` - User accounts and authentication
- `product_terms` - Searchable product terms
- `reports` - Generated reports and metadata

### Manual Database Reset (if needed):
```bash
# Delete the database file to reset
rm ai_trade_report.db
# On Windows:
del ai_trade_report.db
```

## Email Configuration

### 1. Test Email Setup

Create a test file to verify email configuration:

```python
# test_email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def test_email():
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    username = os.getenv('SMTP_USERNAME')
    password = os.getenv('SMTP_PASSWORD')
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = username
        msg['Subject'] = "Test Email from AI Trade Report"
        
        body = "This is a test email to verify email configuration."
        msg.attach(MIMEText(body, 'plain'))
        
        server.send_message(msg)
        server.quit()
        print("✅ Email sent successfully!")
        
    except Exception as e:
        print(f"❌ Email failed: {e}")

if __name__ == "__main__":
    test_email()
```

Run the test:
```bash
python test_email.py
```

## Running the Application

### 1. Start the Server

```bash
python run_server.py
```

### 2. Access the Application

- **Local URL:** http://127.0.0.1:8000
- **Network URL:** http://your-ip-address:8000

### 3. First Time Setup

1. **Register an Account:**
   - Go to the registration page
   - Fill in your details
   - Create your account

2. **Login:**
   - Use your credentials to log in
   - You'll be redirected to the main dashboard

3. **Generate Your First Report:**
   - Fill in the form with your business details
   - Select AI model and language
   - Click "Generate Report"

## Production Deployment

### 1. Environment Variables for Production

```env
# Production settings
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Use strong secret key
SECRET_KEY=your-very-strong-secret-key-for-production

# Database (consider PostgreSQL for production)
DATABASE_URL=sqlite:///./ai_trade_report.db

# Email settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-production-email@gmail.com
SMTP_PASSWORD=your-app-password

# OpenAI API
OPENAI_API_KEY=your-openai-api-key
```

### 2. Using Gunicorn (Recommended for Production)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app:app
```

### 3. Using PM2 (Process Manager)

```bash
# Install PM2
npm install -g pm2

# Create ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'ai-trade-report',
    script: 'run_server.py',
    interpreter: 'python',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    }
  }]
}
EOF

# Start with PM2
pm2 start ecosystem.config.js
```

## Troubleshooting

### Common Issues and Solutions

#### 1. "Module not found" errors
```bash
# Ensure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall requirements
pip install -r requirements.txt
```

#### 2. "OpenAI API key not found"
- Check your `.env` file has the correct API key
- Ensure the `.env` file is in the project root
- Restart the application after adding the key

#### 3. "Email sending failed"
- Verify SMTP credentials in `.env` file
- Check if 2FA is enabled and app password is used
- Test with the provided email test script

#### 4. "Database locked" error
- Stop the application
- Delete `ai_trade_report.db`
- Restart the application

#### 5. "Port already in use"
```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # macOS/Linux

# Kill the process or use different port
# Change PORT in .env file
```

#### 6. "Permission denied" errors
- Ensure you have write permissions in the project directory
- Run with appropriate user permissions

### Logs and Debugging

#### Enable Debug Mode
```env
DEBUG=True
```

#### View Application Logs
```bash
# Logs will appear in the terminal where you started the application
python run_server.py
```

#### Check Database
```bash
# Install SQLite browser or use command line
sqlite3 ai_trade_report.db
.tables
.schema users
```

## Security Considerations

### 1. Environment Variables
- Never commit `.env` file to version control
- Use strong, unique secret keys
- Rotate API keys regularly

### 2. Database Security
- Use strong database passwords in production
- Consider using PostgreSQL for production
- Regular database backups

### 3. API Security
- Rate limiting (implement if needed)
- Input validation
- CORS configuration

### 4. Email Security
- Use app passwords, not main passwords
- Enable 2FA on email accounts
- Monitor email usage

## Support

If you encounter issues not covered in this guide:

1. Check the application logs
2. Verify all environment variables
3. Test individual components (email, API, database)
4. Check the GitHub repository for updates

## File Structure

```
AI_Trade_Report/
├── app.py                 # Main application file
├── run_server.py          # Server runner
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .env_example          # Environment template
├── ai_trade_report.db    # SQLite database (auto-created)
├── auth/                 # Authentication module
├── database/             # Database models
├── schemas/              # Pydantic schemas
├── services/             # Email service
├── static/               # CSS, JS, images
├── templates/            # HTML templates
└── reports/              # Generated reports (auto-created)
```

---

**Note:** This installation guide covers the most common scenarios. For specific deployment environments (Docker, cloud platforms, etc.), additional configuration may be required.
