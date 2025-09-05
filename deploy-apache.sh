#!/bin/bash

# AI Trade Report - Apache Subdomain Deployment Script
# For existing Apache server with Flask app on naga.ai-being.com

set -e

SUBDOMAIN="aitrade.ai-being.co.uk"
PROJECT_DIR="/var/www/AI_Trade_Report"
SERVICE_NAME="aitrade"

echo "🚀 Deploying AI Trade Report to subdomain: $SUBDOMAIN"

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

echo "📋 Pre-deployment checks..."

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project directory $PROJECT_DIR not found"
    echo "Please clone the repository first:"
    echo "git clone https://github.com/tkani/AI_Trade_Report.git $PROJECT_DIR"
    exit 1
fi

cd $PROJECT_DIR

echo "🐍 Setting up Python environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn uvicorn[standard]

echo "⚙️ Configuring environment..."

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env_example .env
    echo "⚠️  Please edit .env file and add your OpenAI API key:"
    echo "   nano $PROJECT_DIR/.env"
    echo "   Add: OPENAI_API_KEY=sk-proj-your-actual-key-here"
    read -p "Press Enter after updating .env file..."
fi

echo "🔧 Creating WSGI application file..."

# Create WSGI file
cat > aitrade.wsgi << 'EOF'
#!/usr/bin/python3
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/var/www/AI_Trade_Report')

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Import the FastAPI application
from app import app

# WSGI application
application = app

if __name__ == "__main__":
    application.run()
EOF

echo "🔧 Creating Gunicorn configuration..."

# Create Gunicorn config
cat > gunicorn.conf.py << 'EOF'
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
EOF

echo "🔧 Creating systemd service..."

# Create systemd service file
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=AI Trade Report FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "📁 Creating directories and setting permissions..."

# Create log directory
sudo mkdir -p /var/log/aitrade
sudo chown www-data:www-data /var/log/aitrade

# Set proper ownership and permissions
sudo chown -R www-data:www-data $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR
sudo chmod -R 777 $PROJECT_DIR/reports
sudo chmod +x $PROJECT_DIR/aitrade.wsgi

echo "🌐 Creating Apache virtual host configuration..."

# Create Apache virtual host configuration
sudo tee /etc/apache2/sites-available/$SUBDOMAIN.conf > /dev/null <<EOF
<VirtualHost *:80>
    ServerName $SUBDOMAIN
    ServerAdmin support@aibeing.com
    
    # Redirect HTTP to HTTPS
    Redirect permanent / https://$SUBDOMAIN/
</VirtualHost>

<VirtualHost *:443>
    ServerName $SUBDOMAIN
    ServerAdmin support@aibeing.com
    
    # Security headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set X-Content-Type-Options "nosniff"
    Header always set Referrer-Policy "no-referrer-when-downgrade"
    
    # Static files
    Alias /static $PROJECT_DIR/static
    <Directory $PROJECT_DIR/static/>
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
    Alias /reports $PROJECT_DIR/reports
    <Directory $PROJECT_DIR/reports/>
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
    RewriteRule ^/?(.*) "ws://127.0.0.1:8001/\$1" [P,L]
    
    # SSL Configuration (will be updated by certbot)
    SSLEngine on
    # SSLCertificateFile /etc/letsencrypt/live/$SUBDOMAIN/fullchain.pem
    # SSLCertificateKeyFile /etc/letsencrypt/live/$SUBDOMAIN/privkey.pem
    # Include /etc/letsencrypt/options-ssl-apache.conf
    
    # File upload size limit
    LimitRequestBody 10485760  # 10MB
</VirtualHost>
EOF

echo "🔧 Enabling Apache modules and site..."

# Enable required Apache modules
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod proxy_wstunnel
sudo a2enmod rewrite
sudo a2enmod headers
sudo a2enmod expires

# Enable the site
sudo a2ensite $SUBDOMAIN.conf

# Test Apache configuration
sudo apache2ctl configtest

echo "🔄 Starting services..."

# Start and enable the FastAPI service
sudo systemctl daemon-reload
sudo systemctl start $SERVICE_NAME
sudo systemctl enable $SERVICE_NAME

# Restart Apache
sudo systemctl restart apache2

echo "🔒 Setting up SSL certificate..."

# Get SSL certificate for subdomain
echo "Getting SSL certificate for $SUBDOMAIN..."
sudo certbot --apache -d $SUBDOMAIN --non-interactive --agree-tos --email support@aibeing.com

echo "✅ Deployment completed!"

# Check service status
echo "📊 Service Status:"
sudo systemctl status $SERVICE_NAME --no-pager -l

echo ""
echo "🌐 Your application should be available at:"
echo "   https://$SUBDOMAIN"
echo ""
echo "📚 FastAPI Documentation:"
echo "   https://$SUBDOMAIN/docs"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status $SERVICE_NAME"
echo "   sudo systemctl restart $SERVICE_NAME"
echo "   sudo journalctl -u $SERVICE_NAME -f"
echo "   tail -f /var/log/aitrade/error.log"
echo ""
echo "🎉 Deployment successful!"
echo "Your FastAPI app is now running alongside your Flask app!"
