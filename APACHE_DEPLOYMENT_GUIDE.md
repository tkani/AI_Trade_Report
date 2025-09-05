# Apache/WSGI Deployment Guide for AI Trade Report

Deploy the AI Trade Report application alongside your existing Flask application on Apache with WSGI.

## 🖥️ Your Current Setup

- **Server**: Apache with WSGI
- **Domain**: naga.ai-being.com
- **SSL**: Let's Encrypt certificates
- **Existing App**: Flask application at `/var/www/naga/`

## 📋 Deployment Strategy

We'll deploy the AI Trade Report as a separate subdomain or path to avoid conflicts with your existing Flask app.

### Option 1: Subdomain Deployment (Recommended)

- **URL**: `ai-trade.naga.ai-being.com` or `trade.naga.ai-being.com`
- **Path**: `/var/www/ai-trade-report/`

### Option 2: Path-based Deployment

- **URL**: `naga.ai-being.com/ai-trade/`
- **Path**: `/var/www/naga/ai-trade/`

## 🚀 Step-by-Step Deployment

### Step 1: Prepare the Server

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip apache2-dev
```

### Step 2: Deploy the Application

```bash
# Create application directory
sudo mkdir -p /var/www/ai-trade-report
sudo chown -R www-data:www-data /var/www/ai-trade-report
cd /var/www/ai-trade-report

# Clone the repository
sudo -u www-data git clone https://github.com/tkani/AI_Trade_Report.git .

# Create virtual environment
sudo -u www-data python3.11 -m venv venv
sudo -u www-data ./venv/bin/pip install -r requirements.txt
sudo -u www-data ./venv/bin/pip install mod_wsgi
```

### Step 3: Configure Environment

```bash
# Create environment file
sudo -u www-data cp .env_example .env
sudo nano .env
```

Add your OpenAI API key:

```env
OPENAI_API_KEY=sk-proj-your-actual-openai-api-key-here
```

### Step 4: Create WSGI Application File

```bash
# Create WSGI file
sudo nano /var/www/ai-trade-report/ai_trade_report.wsgi
```

Add the following content:

```python
#!/usr/bin/python3.11
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/var/www/ai-trade-report/')

# Activate virtual environment
activate_this = '/var/www/ai-trade-report/venv/bin/activate_this.py'
if os.path.exists(activate_this):
    exec(open(activate_this).read(), dict(__file__=activate_this))

# Import the application
from app import app as application

if __name__ == "__main__":
    application.run()
```

### Step 5: Configure Apache Virtual Host

#### Option A: Subdomain Configuration

```bash
# Create new virtual host
sudo nano /etc/apache2/sites-available/ai-trade-report.conf
```

Add the following configuration:

```apache
<VirtualHost *:80>
    ServerName ai-trade.naga.ai-being.com
    ServerAdmin support@aibeing.com
    DocumentRoot /var/www/ai-trade-report

    # Redirect HTTP to HTTPS
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
</VirtualHost>

<VirtualHost *:443>
    ServerName ai-trade.naga.ai-being.com
    ServerAdmin support@aibeing.com
    DocumentRoot /var/www/ai-trade-report

    # WSGI Configuration
    WSGIDaemonProcess ai-trade-report threads=50 inactivity-timeout=60 python-home=/var/www/ai-trade-report/venv
    WSGIProcessGroup ai-trade-report
    WSGIScriptAlias / /var/www/ai-trade-report/ai_trade_report.wsgi

    # Static files
    Alias /static /var/www/ai-trade-report/static
    <Directory /var/www/ai-trade-report/static/>
        Order allow,deny
        Allow from all
        Require all granted
    </Directory>

    # Reports directory
    Alias /reports /var/www/ai-trade-report/reports
    <Directory /var/www/ai-trade-report/reports/>
        Order allow,deny
        Allow from all
        Require all granted
    </Directory>

    # Application directory
    <Directory /var/www/ai-trade-report/>
        Order allow,deny
        Allow from all
        Require all granted
    </Directory>

    # SSL Configuration
    SSLCertificateFile /etc/letsencrypt/live/ai-trade.naga.ai-being.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/ai-trade.naga.ai-being.com/privkey.pem
    Include /etc/letsencrypt/options-ssl-apache.conf

    # Security headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set X-Content-Type-Options "nosniff"
    Header always set Referrer-Policy "no-referrer-when-downgrade"

    # Logging
    ErrorLog ${APACHE_LOG_DIR}/ai-trade-report_error.log
    CustomLog ${APACHE_LOG_DIR}/ai-trade-report_access.log combined
</VirtualHost>
```

#### Option B: Path-based Configuration (Alternative)

If you prefer to use a path instead of subdomain, modify your existing virtual host:

```bash
# Edit existing virtual host
sudo nano /etc/apache2/sites-available/naga.conf
```

Add this to your existing `<VirtualHost *:443>` block:

```apache
# AI Trade Report - Path-based deployment
WSGIDaemonProcess ai-trade-report threads=50 inactivity-timeout=60 python-home=/var/www/ai-trade-report/venv
WSGIProcessGroup ai-trade-report
WSGIScriptAlias /ai-trade /var/www/ai-trade-report/ai_trade_report.wsgi

# Static files for AI Trade Report
Alias /ai-trade/static /var/www/ai-trade-report/static
<Directory /var/www/ai-trade-report/static/>
    Order allow,deny
    Allow from all
    Require all granted
</Directory>

# Reports directory for AI Trade Report
Alias /ai-trade/reports /var/www/ai-trade-report/reports
<Directory /var/www/ai-trade-report/reports/>
    Order allow,deny
    Allow from all
    Require all granted
</Directory>
```

### Step 6: Enable the Site and SSL

#### For Subdomain Option:

```bash
# Enable the site
sudo a2ensite ai-trade-report.conf

# Enable required Apache modules
sudo a2enmod wsgi
sudo a2enmod ssl
sudo a2enmod rewrite
sudo a2enmod headers

# Restart Apache
sudo systemctl restart apache2

# Get SSL certificate for subdomain
sudo certbot --apache -d ai-trade.naga.ai-being.com
```

#### For Path-based Option:

```bash
# Enable required Apache modules
sudo a2enmod wsgi
sudo a2enmod headers

# Restart Apache
sudo systemctl restart apache2
```

### Step 7: Set Up Logging

```bash
# Create log rotation configuration
sudo nano /etc/logrotate.d/ai-trade-report
```

Add:

```
/var/log/apache2/ai-trade-report_*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload apache2
    endscript
}
```

### Step 8: Create Management Scripts

```bash
# Create deployment script
sudo nano /var/www/ai-trade-report/deploy.sh
```

Add:

```bash
#!/bin/bash
set -e

echo "🚀 Deploying AI Trade Report..."

# Pull latest changes
cd /var/www/ai-trade-report
sudo -u www-data git pull origin main

# Update dependencies
sudo -u www-data ./venv/bin/pip install -r requirements.txt

# Restart Apache
sudo systemctl reload apache2

echo "✅ Deployment completed!"
```

```bash
# Make script executable
sudo chmod +x /var/www/ai-trade-report/deploy.sh
```

### Step 9: Set Up Monitoring

```bash
# Create monitoring script
sudo nano /usr/local/bin/monitor-ai-trade-report.sh
```

Add:

```bash
#!/bin/bash
echo "=== AI Trade Report Status ==="
echo "Apache Status:"
systemctl status apache2 --no-pager -l
echo ""
echo "Recent Error Logs:"
tail -n 20 /var/log/apache2/ai-trade-report_error.log
echo ""
echo "Recent Access Logs:"
tail -n 10 /var/log/apache2/ai-trade-report_access.log
echo ""
echo "Disk Usage:"
df -h /var/www/ai-trade-report
```

```bash
# Make script executable
sudo chmod +x /usr/local/bin/monitor-ai-trade-report.sh
```

## 🔧 Configuration Adjustments

### Update FastAPI for WSGI

Create a WSGI-compatible version of your app:

```bash
# Create WSGI adapter
sudo nano /var/www/ai-trade-report/wsgi_app.py
```

Add:

```python
from app import app
import os

# Set environment variables
os.environ.setdefault('PYTHONPATH', '/var/www/ai-trade-report')

# WSGI application
application = app
```

### Update the WSGI file:

```bash
sudo nano /var/www/ai-trade-report/ai_trade_report.wsgi
```

Replace content with:

```python
#!/usr/bin/python3.11
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/var/www/ai-trade-report/')

# Activate virtual environment
activate_this = '/var/www/ai-trade-report/venv/bin/activate_this.py'
if os.path.exists(activate_this):
    exec(open(activate_this).read(), dict(__file__=activate_this))

# Import the WSGI application
from wsgi_app import application

if __name__ == "__main__":
    application.run()
```

## 🚨 Troubleshooting

### Common Issues

#### 1. WSGI Import Errors

```bash
# Check Python path
sudo -u www-data /var/www/ai-trade-report/venv/bin/python -c "import sys; print(sys.path)"

# Test WSGI file
sudo -u www-data /var/www/ai-trade-report/venv/bin/python /var/www/ai-trade-report/ai_trade_report.wsgi
```

#### 2. Permission Issues

```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/ai-trade-report

# Fix permissions
sudo chmod -R 755 /var/www/ai-trade-report
sudo chmod -R 777 /var/www/ai-trade-report/reports
```

#### 3. Apache Configuration Issues

```bash
# Test Apache configuration
sudo apache2ctl configtest

# Check Apache error logs
sudo tail -f /var/log/apache2/error.log

# Check site-specific logs
sudo tail -f /var/log/apache2/ai-trade-report_error.log
```

#### 4. SSL Certificate Issues

```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

## 📊 Access Your Application

### Subdomain Option:

- **Main App**: `https://naga.ai-being.com`
- **AI Trade Report**: `https://ai-trade.naga.ai-being.com`
- **API Docs**: `https://ai-trade.naga.ai-being.com/docs`

### Path-based Option:

- **Main App**: `https://naga.ai-being.com`
- **AI Trade Report**: `https://naga.ai-being.com/ai-trade/`
- **API Docs**: `https://naga.ai-being.com/ai-trade/docs`

## 🔄 Updates and Maintenance

### Update Application

```bash
# Run deployment script
sudo /var/www/ai-trade-report/deploy.sh
```

### Monitor Application

```bash
# Check status
sudo /usr/local/bin/monitor-ai-trade-report.sh

# View real-time logs
sudo tail -f /var/log/apache2/ai-trade-report_error.log
```

### Backup

```bash
# Create backup script
sudo nano /usr/local/bin/backup-ai-trade-report.sh
```

Add:

```bash
#!/bin/bash
BACKUP_DIR="/backup/ai-trade-report"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/ai-trade-report_$DATE.tar.gz /var/www/ai-trade-report
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

## 🎉 Deployment Complete!

Your AI Trade Report application is now deployed alongside your existing Flask application. Both applications will run independently without conflicts.

### Next Steps:

1. Test the application at your chosen URL
2. Set up monitoring and backups
3. Configure any additional security measures
4. Update your DNS if using subdomain option

For support, check the Apache error logs and refer to the troubleshooting section above.
