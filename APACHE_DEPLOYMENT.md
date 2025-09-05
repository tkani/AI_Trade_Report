# Apache Deployment Guide - AI Trade Report

Complete step-by-step deployment guide for `aitrade.ai-being.com` on your existing Apache server.

## 🎯 Your Setup
- **Subdomain**: `aitrade.ai-being.com`
- **Folder**: `/var/www/AI_Trade_Report/` (already cloned)
- **Server**: Apache with WSGI (existing Flask app)
- **SSL**: Let's Encrypt certificates

## 📋 Prerequisites
- [x] Server with Apache and WSGI
- [x] Domain `aitrade.ai-being.com` pointing to your server
- [x] Repository cloned to `/var/www/AI_Trade_Report/`
- [x] Sudo access to the server

## 🚀 Step-by-Step Deployment

### Step 1: Prepare the Server

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.11 if not already installed
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip apache2-dev
```

### Step 2: Set Up Python Environment

```bash
# Navigate to your project directory
cd /var/www/AI_Trade_Report

# Create virtual environment
sudo -u www-data python3.11 -m venv venv

# Activate virtual environment and install dependencies
sudo -u www-data ./venv/bin/pip install -r requirements.txt
sudo -u www-data ./venv/bin/pip install mod_wsgi
```

### Step 3: Configure Environment Variables

```bash
# Create environment file
sudo -u www-data cp .env_example .env

# Edit the environment file
sudo nano .env
```

Add your OpenAI API key:
```env
OPENAI_API_KEY=sk-proj-your-actual-openai-api-key-here
```

### Step 4: Create WSGI Application Files

```bash
# Create WSGI adapter
sudo -u www-data nano wsgi_app.py
```

Add this content:
```python
from app import app
import os

# Set environment variables
os.environ.setdefault('PYTHONPATH', '/var/www/AI_Trade_Report/')

# WSGI application
application = app
```

```bash
# Create main WSGI file
sudo -u www-data nano ai_trade_report.wsgi
```

Add this content:
```python
#!/usr/bin/python3.11
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/var/www/AI_Trade_Report/')

# Activate virtual environment
activate_this = '/var/www/AI_Trade_Report/venv/bin/activate_this.py'
if os.path.exists(activate_this):
    exec(open(activate_this).read(), dict(__file__=activate_this))

# Import the WSGI application
from wsgi_app import application

if __name__ == "__main__":
    application.run()
```

### Step 5: Create Apache Virtual Host

```bash
# Create virtual host configuration
sudo nano /etc/apache2/sites-available/aitrade.conf
```

Add this configuration:
```apache
<VirtualHost *:80>
    ServerName aitrade.ai-being.com
    ServerAdmin support@aibeing.com
    DocumentRoot /var/www/AI_Trade_Report
    
    # Redirect HTTP to HTTPS
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
</VirtualHost>

<VirtualHost *:443>
    ServerName aitrade.ai-being.com
    ServerAdmin support@aibeing.com
    DocumentRoot /var/www/AI_Trade_Report

    # WSGI Configuration
    WSGIDaemonProcess aitrade threads=50 inactivity-timeout=60 python-home=/var/www/AI_Trade_Report/venv
    WSGIProcessGroup aitrade
    WSGIScriptAlias / /var/www/AI_Trade_Report/ai_trade_report.wsgi
    
    # Static files
    Alias /static /var/www/AI_Trade_Report/static
    <Directory /var/www/AI_Trade_Report/static/>
        Order allow,deny
        Allow from all
        Require all granted
    </Directory>
    
    # Reports directory
    Alias /reports /var/www/AI_Trade_Report/reports
    <Directory /var/www/AI_Trade_Report/reports/>
        Order allow,deny
        Allow from all
        Require all granted
    </Directory>
    
    # Application directory
    <Directory /var/www/AI_Trade_Report/>
        Order allow,deny
        Allow from all
        Require all granted
    </Directory>

    # SSL Configuration (will be updated by certbot)
    # SSLCertificateFile /etc/letsencrypt/live/aitrade.ai-being.com/fullchain.pem
    # SSLCertificateKeyFile /etc/letsencrypt/live/aitrade.ai-being.com/privkey.pem
    # Include /etc/letsencrypt/options-ssl-apache.conf
    
    # Security headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set X-Content-Type-Options "nosniff"
    Header always set Referrer-Policy "no-referrer-when-downgrade"
    
    # Logging
    ErrorLog ${APACHE_LOG_DIR}/aitrade_error.log
    CustomLog ${APACHE_LOG_DIR}/aitrade_access.log combined
</VirtualHost>
```

### Step 6: Enable Apache Modules and Site

```bash
# Enable required Apache modules
sudo a2enmod wsgi
sudo a2enmod ssl
sudo a2enmod rewrite
sudo a2enmod headers

# Enable the site
sudo a2ensite aitrade.conf

# Test Apache configuration
sudo apache2ctl configtest

# Restart Apache
sudo systemctl restart apache2
```

### Step 7: Set Up SSL Certificate

```bash
# Install certbot if not already installed
sudo apt install -y certbot python3-certbot-apache

# Get SSL certificate for your subdomain
sudo certbot --apache -d aitrade.ai-being.com --non-interactive --agree-tos --email support@aibeing.com
```

### Step 8: Set Up Permissions

```bash
# Set proper ownership
sudo chown -R www-data:www-data /var/www/AI_Trade_Report

# Create reports directory with proper permissions
sudo -u www-data mkdir -p /var/www/AI_Trade_Report/reports
sudo chmod -R 755 /var/www/AI_Trade_Report
sudo chmod -R 777 /var/www/AI_Trade_Report/reports
```

### Step 9: Test the Deployment

```bash
# Check Apache status
sudo systemctl status apache2

# Check if the site is enabled
sudo a2ensite -l

# Test the WSGI application
sudo -u www-data /var/www/AI_Trade_Report/venv/bin/python /var/www/AI_Trade_Report/ai_trade_report.wsgi
```

### Step 10: Verify Everything Works

1. **Visit your site**: `https://aitrade.ai-being.com`
2. **Check API docs**: `https://aitrade.ai-being.com/docs`
3. **Test report generation**: Fill out the form and generate a report
4. **Check logs**: `sudo tail -f /var/log/apache2/aitrade_error.log`

## 🔧 Management Commands

### Update the Application
```bash
cd /var/www/AI_Trade_Report
sudo -u www-data git pull origin main
sudo -u www-data ./venv/bin/pip install -r requirements.txt
sudo systemctl reload apache2
```

### Check Logs
```bash
# Error logs
sudo tail -f /var/log/apache2/aitrade_error.log

# Access logs
sudo tail -f /var/log/apache2/aitrade_access.log

# Apache error logs
sudo tail -f /var/log/apache2/error.log
```

### Restart Services
```bash
# Restart Apache
sudo systemctl restart apache2

# Reload Apache (without stopping)
sudo systemctl reload apache2
```

## 🚨 Troubleshooting

### Common Issues

#### 1. WSGI Import Errors
```bash
# Test Python path
sudo -u www-data /var/www/AI_Trade_Report/venv/bin/python -c "import sys; print(sys.path)"

# Test WSGI file directly
sudo -u www-data /var/www/AI_Trade_Report/venv/bin/python /var/www/AI_Trade_Report/ai_trade_report.wsgi
```

#### 2. Permission Issues
```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/AI_Trade_Report

# Fix permissions
sudo chmod -R 755 /var/www/AI_Trade_Report
sudo chmod -R 777 /var/www/AI_Trade_Report/reports
```

#### 3. Apache Configuration Issues
```bash
# Test configuration
sudo apache2ctl configtest

# Check if site is enabled
sudo a2ensite -l

# Check Apache error logs
sudo tail -f /var/log/apache2/error.log
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

## 📊 Monitoring

### Create a monitoring script
```bash
sudo nano /usr/local/bin/monitor-aitrade.sh
```

Add this content:
```bash
#!/bin/bash
echo "=== AI Trade Report Status ==="
echo "Apache Status:"
systemctl status apache2 --no-pager -l
echo ""
echo "Recent Error Logs:"
tail -n 20 /var/log/apache2/aitrade_error.log
echo ""
echo "Recent Access Logs:"
tail -n 10 /var/log/apache2/aitrade_access.log
echo ""
echo "Disk Usage:"
df -h /var/www/AI_Trade_Report
```

```bash
# Make script executable
sudo chmod +x /usr/local/bin/monitor-aitrade.sh
```

## 🎉 Deployment Complete!

Your AI Trade Report should now be available at:
- **Main Application**: `https://aitrade.ai-being.com`
- **API Documentation**: `https://aitrade.ai-being.com/docs`
- **Reports**: `https://aitrade.ai-being.com/reports/`

### Next Steps:
1. Test the application thoroughly
2. Set up monitoring and backups
3. Configure any additional security measures
4. Update your DNS if the subdomain isn't working yet

For support, check the Apache error logs and refer to the troubleshooting section above.
