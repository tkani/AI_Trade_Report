#!/bin/bash

# AI Trade Report - Quick Deployment Script for aitrade.ai-being.com
# Assumes repository is already cloned to /var/www/AI_Trade_Report/

set -e

APP_DIR="/var/www/AI_Trade_Report"
DOMAIN="aitrade.ai-being.com"

echo "🚀 Deploying AI Trade Report to $DOMAIN..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root for security reasons"
   exit 1
fi

# Check if user has sudo privileges
if ! sudo -n true 2>/dev/null; then
    echo "❌ This script requires sudo privileges"
    exit 1
fi

# Check if directory exists
if [ ! -d "$APP_DIR" ]; then
    echo "❌ Directory $APP_DIR does not exist. Please clone the repository first:"
    echo "   sudo mkdir -p $APP_DIR"
    echo "   sudo chown -R $USER:$USER $APP_DIR"
    echo "   git clone https://github.com/tkani/AI_Trade_Report.git $APP_DIR"
    exit 1
fi

echo "📋 Setting up Python environment..."

# Navigate to project directory
cd $APP_DIR

# Create virtual environment
sudo -u www-data python3.11 -m venv venv

# Install dependencies
sudo -u www-data ./venv/bin/pip install -r requirements.txt
sudo -u www-data ./venv/bin/pip install mod_wsgi

echo "⚙️ Configuring environment..."

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    sudo -u www-data cp .env_example .env
    echo "⚠️  Please edit .env file and add your OpenAI API key:"
    echo "   sudo nano $APP_DIR/.env"
    echo "   Add: OPENAI_API_KEY=sk-proj-your-actual-key-here"
    read -p "Press Enter after updating .env file..."
fi

echo "🔧 Creating WSGI application files..."

# Create WSGI adapter
sudo -u www-data tee wsgi_app.py > /dev/null <<EOF
from app import app
import os

# Set environment variables
os.environ.setdefault('PYTHONPATH', '$APP_DIR/')

# WSGI application
application = app
EOF

# Create main WSGI file
sudo -u www-data tee ai_trade_report.wsgi > /dev/null <<EOF
#!/usr/bin/python3.11
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '$APP_DIR/')

# Activate virtual environment
activate_this = '$APP_DIR/venv/bin/activate_this.py'
if os.path.exists(activate_this):
    exec(open(activate_this).read(), dict(__file__=activate_this))

# Import the WSGI application
from wsgi_app import application

if __name__ == "__main__":
    application.run()
EOF

echo "🌐 Configuring Apache virtual host..."

# Create Apache virtual host configuration
sudo tee /etc/apache2/sites-available/aitrade.conf > /dev/null <<EOF
<VirtualHost *:80>
    ServerName $DOMAIN
    ServerAdmin support@aibeing.com
    DocumentRoot $APP_DIR
    
    # Redirect HTTP to HTTPS
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
</VirtualHost>

<VirtualHost *:443>
    ServerName $DOMAIN
    ServerAdmin support@aibeing.com
    DocumentRoot $APP_DIR

    # WSGI Configuration
    WSGIDaemonProcess aitrade threads=50 inactivity-timeout=60 python-home=$APP_DIR/venv
    WSGIProcessGroup aitrade
    WSGIScriptAlias / $APP_DIR/ai_trade_report.wsgi
    
    # Static files
    Alias /static $APP_DIR/static
    <Directory $APP_DIR/static/>
        Order allow,deny
        Allow from all
        Require all granted
    </Directory>
    
    # Reports directory
    Alias /reports $APP_DIR/reports
    <Directory $APP_DIR/reports/>
        Order allow,deny
        Allow from all
        Require all granted
    </Directory>
    
    # Application directory
    <Directory $APP_DIR/>
        Order allow,deny
        Allow from all
        Require all granted
    </Directory>

    # SSL Configuration (will be updated by certbot)
    # SSLCertificateFile /etc/letsencrypt/live/$DOMAIN/fullchain.pem
    # SSLCertificateKeyFile /etc/letsencrypt/live/$DOMAIN/privkey.pem
    # Include /etc/letsencrypt/options-ssl-apache.conf
    
    # Security headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set X-Content-Type-Options "nosniff"
    Header always set Referrer-Policy "no-referrer-when-downgrade"
    
    # Logging
    ErrorLog \${APACHE_LOG_DIR}/aitrade_error.log
    CustomLog \${APACHE_LOG_DIR}/aitrade_access.log combined
</VirtualHost>
EOF

echo "📁 Setting up directories and permissions..."

# Create reports directory
sudo -u www-data mkdir -p reports

# Set proper ownership
sudo chown -R www-data:www-data $APP_DIR

echo "🔄 Enabling Apache modules and site..."

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

echo "🔒 Setting up SSL certificate..."

# Get SSL certificate
if command -v certbot &> /dev/null; then
    echo "📜 Obtaining SSL certificate..."
    sudo certbot --apache -d $DOMAIN --non-interactive --agree-tos --email support@aibeing.com
else
    echo "⚠️  Certbot not found. Please install certbot and run:"
    echo "   sudo certbot --apache -d $DOMAIN"
fi

echo "✅ Deployment completed!"

# Check Apache status
echo "📊 Apache Status:"
sudo systemctl status apache2 --no-pager -l

echo ""
echo "🌐 Your AI Trade Report application should be available at:"
echo "   https://$DOMAIN"
echo ""
echo "📚 FastAPI Documentation:"
echo "   https://$DOMAIN/docs"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status apache2"
echo "   sudo systemctl restart apache2"
echo "   sudo tail -f /var/log/apache2/aitrade_error.log"
echo "   sudo tail -f /var/log/apache2/aitrade_access.log"
echo ""
echo "⚠️  Don't forget to:"
echo "   1. Update your DNS to point $DOMAIN to this server"
echo "   2. Configure your OpenAI API key in .env file"
echo "   3. Test the application thoroughly"
echo ""
echo "🎉 Apache deployment successful!"
