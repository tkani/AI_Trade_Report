# Apache Subdomain Deployment Guide

Deploy FastAPI application as subdomain on existing Apache server with Flask app.

## 🎯 Current Setup

- **Main Domain**: naga.ai-being.com (Flask app)
- **Subdomain**: aitrade.ai-being.co.uk (FastAPI app)
- **Server**: Apache with existing SSL certificates
- **Project Folder**: /var/www/AI_Trade_Report

## 📋 Step-by-Step Deployment

### Step 1: Prepare the Application

```bash
# Navigate to your project directory
cd /var/www/AI_Trade_Report

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn uvicorn[standard]

# Create .env file
cp .env_example .env
nano .env
# Add your OpenAI API key: OPENAI_API_KEY=sk-proj-your-actual-key-here
```

### Step 2: Create WSGI Application File

```bash
# Create WSGI file for FastAPI
nano /var/www/AI_Trade_Report/aitrade.wsgi
```

Add this content:

```python
#!/usr/bin/python3
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/var/www/AI_Trade_Report')

# Set environment variables
os.environ['OPENAI_API_KEY'] = 'your-openai-api-key-here'

# Import the FastAPI application
from app import app

# WSGI application
application = app

if __name__ == "__main__":
    application.run()
```

### Step 3: Create Gunicorn Configuration

```bash
# Create Gunicorn config file
nano /var/www/AI_Trade_Report/gunicorn.conf.py
```

Add this content:

```python
# Gunicorn configuration file
bind = "127.0.0.1:8001"  # Use different port than Flask app
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
accesslog = "/var/log/aitrade/access.log"
errorlog = "/var/log/aitrade/error.log"
loglevel = "info"
```

### Step 4: Create Systemd Service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/aitrade.service
```

Add this content:

```ini
[Unit]
Description=AI Trade Report FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/AI_Trade_Report
Environment="PATH=/var/www/AI_Trade_Report/venv/bin"
ExecStart=/var/www/AI_Trade_Report/venv/bin/gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### Step 5: Create Log Directory

```bash
# Create log directory
sudo mkdir -p /var/log/aitrade
sudo chown www-data:www-data /var/log/aitrade
```

### Step 6: Configure Apache Virtual Host

```bash
# Create Apache virtual host configuration
sudo nano /etc/apache2/sites-available/aitrade.ai-being.co.uk.conf
```

Add this content:

```apache
<VirtualHost *:80>
    ServerName aitrade.ai-being.co.uk
    ServerAdmin support@aibeing.com

    # Redirect HTTP to HTTPS
    Redirect permanent / https://aitrade.ai-being.co.uk/
</VirtualHost>

<VirtualHost *:443>
    ServerName aitrade.ai-being.co.uk
    ServerAdmin support@aibeing.com

    # Security headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set X-Content-Type-Options "nosniff"
    Header always set Referrer-Policy "no-referrer-when-downgrade"

    # Static files
    Alias /static /var/www/AI_Trade_Report/static
    <Directory /var/www/AI_Trade_Report/static/>
        Require all granted
        ExpiresActive On
        ExpiresByType text/css "access plus 1 year"
        ExpiresByType application/javascript "access plus 1 year"
        ExpiresByType image/png "access plus 1 year"
        ExpiresByType image/jpg "access plus 1 year"
        ExpiresByType image/jpeg "access plus 1 year"
        ExpiresByType image/gif "access plus 1 year"
        ExpiresByType image/svg+xml "access plus 1 year"
    </Directory>

    # Reports directory
    Alias /reports /var/www/AI_Trade_Report/reports
    <Directory /var/www/AI_Trade_Report/reports/>
        Require all granted
        ExpiresActive On
        ExpiresByType text/html "access plus 1 hour"
    </Directory>

    # Proxy to FastAPI application
    ProxyPreserveHost On
    ProxyPass /static/ !
    ProxyPass /reports/ !
    ProxyPass / http://127.0.0.1:8001/
    ProxyPassReverse / http://127.0.0.1:8001/

    # WebSocket support (if needed)
    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} websocket [NC]
    RewriteCond %{HTTP:Connection} upgrade [NC]
    RewriteRule ^/?(.*) "ws://127.0.0.1:8001/$1" [P,L]

    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/aitrade.ai-being.co.uk/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/aitrade.ai-being.co.uk/privkey.pem
    Include /etc/letsencrypt/options-ssl-apache.conf

    # File upload size limit
    LimitRequestBody 10485760  # 10MB
</VirtualHost>
```

### Step 7: Enable Site and Start Services

```bash
# Enable the site
sudo a2ensite aitrade.ai-being.co.uk.conf

# Enable required Apache modules
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod proxy_wstunnel
sudo a2enmod rewrite
sudo a2enmod headers
sudo a2enmod expires

# Test Apache configuration
sudo apache2ctl configtest

# Start and enable the FastAPI service
sudo systemctl daemon-reload
sudo systemctl start aitrade
sudo systemctl enable aitrade

# Restart Apache
sudo systemctl restart apache2
```

### Step 8: Set Up SSL Certificate

```bash
# Get SSL certificate for subdomain
sudo certbot --apache -d aitrade.ai-being.co.uk

# Test certificate renewal
sudo certbot renew --dry-run
```

### Step 9: Set Permissions

```bash
# Set proper ownership
sudo chown -R www-data:www-data /var/www/AI_Trade_Report

# Set proper permissions
sudo chmod -R 755 /var/www/AI_Trade_Report
sudo chmod -R 777 /var/www/AI_Trade_Report/reports
sudo chmod +x /var/www/AI_Trade_Report/aitrade.wsgi
```

### Step 10: Test the Deployment

```bash
# Check service status
sudo systemctl status aitrade

# Check Apache status
sudo systemctl status apache2

# Test the application
curl -I https://aitrade.ai-being.co.uk/

# Check logs
tail -f /var/log/aitrade/error.log
tail -f /var/log/apache2/error.log
```

## 🔧 Alternative: Using mod_wsgi (Recommended)

If you prefer to use mod_wsgi instead of proxy:

### Install mod_wsgi

```bash
# Install mod_wsgi
sudo apt install libapache2-mod-wsgi-py3

# Enable the module
sudo a2enmod wsgi
```

### Create WSGI Application

```bash
# Create WSGI file
nano /var/www/AI_Trade_Report/aitrade.wsgi
```

```python
#!/usr/bin/python3
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/var/www/AI_Trade_Report')

# Set environment variables
os.environ['OPENAI_API_KEY'] = 'your-openai-api-key-here'

# Import the FastAPI application
from app import app

# WSGI application
application = app

if __name__ == "__main__":
    application.run()
```

### Update Apache Configuration

```apache
<VirtualHost *:443>
    ServerName aitrade.ai-being.co.uk
    ServerAdmin support@aibeing.com

    # Security headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set X-Content-Type-Options "nosniff"

    # Static files
    Alias /static /var/www/AI_Trade_Report/static
    <Directory /var/www/AI_Trade_Report/static/>
        Require all granted
    </Directory>

    # Reports directory
    Alias /reports /var/www/AI_Trade_Report/reports
    <Directory /var/www/AI_Trade_Report/reports/>
        Require all granted
    </Directory>

    # WSGI configuration
    WSGIDaemonProcess aitrade python-path=/var/www/AI_Trade_Report python-home=/var/www/AI_Trade_Report/venv
    WSGIProcessGroup aitrade
    WSGIScriptAlias / /var/www/AI_Trade_Report/aitrade.wsgi

    <Directory /var/www/AI_Trade_Report/>
        WSGIProcessGroup aitrade
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>

    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/aitrade.ai-being.co.uk/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/aitrade.ai-being.co.uk/privkey.pem
    Include /etc/letsencrypt/options-ssl-apache.conf
</VirtualHost>
```

## 🚨 Troubleshooting

### Common Issues

1. **Service won't start**:

   ```bash
   sudo journalctl -u aitrade -f
   ```

2. **Apache 500 error**:

   ```bash
   sudo tail -f /var/log/apache2/error.log
   ```

3. **Permission issues**:

   ```bash
   sudo chown -R www-data:www-data /var/www/AI_Trade_Report
   sudo chmod -R 755 /var/www/AI_Trade_Report
   ```

4. **Module not found**:
   ```bash
   sudo a2enmod proxy proxy_http rewrite headers expires
   sudo systemctl restart apache2
   ```

### Useful Commands

```bash
# Restart services
sudo systemctl restart aitrade
sudo systemctl restart apache2

# Check status
sudo systemctl status aitrade
sudo systemctl status apache2

# View logs
tail -f /var/log/aitrade/error.log
tail -f /var/log/apache2/error.log

# Test configuration
sudo apache2ctl configtest
```

## 📊 Monitoring

### Health Check Script

```bash
# Create health check script
nano /usr/local/bin/check-aitrade.sh
```

```bash
#!/bin/bash
echo "=== AI Trade Report Status ==="
echo "Service Status:"
systemctl status aitrade --no-pager -l
echo ""
echo "Apache Status:"
systemctl status apache2 --no-pager -l
echo ""
echo "Port 8001:"
netstat -tlnp | grep 8001
echo ""
echo "Recent Errors:"
tail -n 10 /var/log/aitrade/error.log
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/check-aitrade.sh
```

## 🎉 Final Result

After successful deployment:

- **Main App**: https://naga.ai-being.com (Flask)
- **Subdomain**: https://aitrade.ai-being.co.uk (FastAPI)
- **API Docs**: https://aitrade.ai-being.co.uk/docs
- **Reports**: https://aitrade.ai-being.co.uk/reports/

Both applications will run independently on the same server with proper SSL certificates and security headers.
