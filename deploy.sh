#!/bin/bash

# AI Trade Report - Quick Deployment Script
# Usage: ./deploy.sh [production|staging|development]

set -e

ENVIRONMENT=${1:-production}
APP_NAME="ai-trade-report"
APP_DIR="/var/www/$APP_NAME"
SERVICE_NAME="ai-trade-report"
NGINX_SITE="ai-trade-report"

echo "🚀 Starting deployment for $ENVIRONMENT environment..."

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

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "📦 Installing git..."
    sudo apt update
    sudo apt install -y git
fi

# Check if Python 3.11+ is installed
if ! command -v python3.11 &> /dev/null; then
    echo "📦 Installing Python 3.11..."
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
fi

# Check if Nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "📦 Installing Nginx..."
    sudo apt install -y nginx
fi

echo "🔧 Setting up application directory..."

# Create application directory
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

# Clone or update repository
if [ -d "$APP_DIR/.git" ]; then
    echo "📥 Updating existing repository..."
    cd $APP_DIR
    git pull origin main
else
    echo "📥 Cloning repository..."
    git clone https://github.com/tkani/AI_Trade_Report.git $APP_DIR
    cd $APP_DIR
fi

echo "🐍 Setting up Python environment..."

# Create virtual environment
python3.11 -m venv venv
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
    echo "   nano $APP_DIR/.env"
    echo "   Add: OPENAI_API_KEY=sk-proj-your-actual-key-here"
    read -p "Press Enter after updating .env file..."
fi

echo "🔧 Creating systemd service..."

# Create systemd service file
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=AI Trade Report FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 127.0.0.1:8000 --access-logfile /var/log/$APP_NAME/access.log --error-logfile /var/log/$APP_NAME/error.log
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "🌐 Configuring Nginx..."

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/$NGINX_SITE > /dev/null <<EOF
server {
    listen 80;
    server_name _;  # Replace with your domain

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Static files
    location /static/ {
        alias $APP_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Reports directory
    location /reports/ {
        alias $APP_DIR/reports/;
        expires 1h;
        add_header Cache-Control "public";
    }

    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    client_max_body_size 10M;
}
EOF

echo "📁 Setting up directories and permissions..."

# Create log directory
sudo mkdir -p /var/log/$APP_NAME
sudo chown www-data:www-data /var/log/$APP_NAME

# Create reports directory
mkdir -p reports
sudo chown -R www-data:www-data $APP_DIR

echo "🔄 Starting services..."

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/$NGINX_SITE /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

echo "🔒 Setting up firewall..."

# Configure UFW
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

echo "✅ Deployment completed!"

# Check service status
echo "📊 Service Status:"
sudo systemctl status $SERVICE_NAME --no-pager -l

echo ""
echo "🌐 Your application should be available at:"
echo "   http://your-server-ip"
echo ""
echo "📚 FastAPI Documentation:"
echo "   http://your-server-ip/docs"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status $SERVICE_NAME"
echo "   sudo systemctl restart $SERVICE_NAME"
echo "   sudo journalctl -u $SERVICE_NAME -f"
echo "   tail -f /var/log/$APP_NAME/error.log"
echo ""
echo "⚠️  Don't forget to:"
echo "   1. Update your domain name in Nginx config"
echo "   2. Set up SSL certificate with: sudo certbot --nginx -d your-domain.com"
echo "   3. Configure your OpenAI API key in .env file"
echo ""
echo "🎉 Deployment successful!"
