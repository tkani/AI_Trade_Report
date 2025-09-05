#!/bin/bash

# AI Trade Report - Apache Coexistence Deployment Script
# For subdomain: aitrade.ai-being.com
# Folder: /var/www/AI_Trade_Report

set -e

echo "🚀 Starting AI Trade Report deployment alongside Apache..."

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

echo "📋 Checking prerequisites..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Please run this script from the AI_Trade_Report directory"
    exit 1
fi

# Check if Apache is running
if ! systemctl is-active --quiet apache2; then
    echo "⚠️  Apache is not running. Starting Apache..."
    sudo systemctl start apache2
fi

echo "📦 Installing Nginx..."

# Install Nginx
sudo apt update
sudo apt install -y nginx

echo "🔧 Configuring Nginx for subdomain..."

# Create Nginx configuration for subdomain
sudo tee /etc/nginx/sites-available/aitrade.ai-being.com > /dev/null <<EOF
server {
    listen 80;
    server_name aitrade.ai-being.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name aitrade.ai-being.com;
    
    # SSL configuration (we'll get certificate in next step)
    ssl_certificate /etc/letsencrypt/live/aitrade.ai-being.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/aitrade.ai-being.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Static files
    location /static/ {
        alias /var/www/AI_Trade_Report/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Reports directory
    location /reports/ {
        alias /var/www/AI_Trade_Report/reports/;
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
    
    # File upload size limit
    client_max_body_size 10M;
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/aitrade.ai-being.com /etc/nginx/sites-enabled/

echo "🐍 Setting up Python environment..."

# Create virtual environment
python3 -m venv venv
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
    echo "   nano /var/www/AI_Trade_Report/.env"
    echo "   Add: OPENAI_API_KEY=sk-proj-your-actual-key-here"
    read -p "Press Enter after updating .env file..."
fi

echo "🔧 Creating systemd service..."

# Create systemd service file
sudo tee /etc/systemd/system/ai-trade-report.service > /dev/null <<EOF
[Unit]
Description=AI Trade Report FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/AI_Trade_Report
Environment="PATH=/var/www/AI_Trade_Report/venv/bin"
ExecStart=/var/www/AI_Trade_Report/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 127.0.0.1:8000 --access-logfile /var/log/ai-trade-report/access.log --error-logfile /var/log/ai-trade-report/error.log
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "📁 Setting up directories and permissions..."

# Create log directory
sudo mkdir -p /var/log/ai-trade-report
sudo chown www-data:www-data /var/log/ai-trade-report

# Set proper permissions
sudo chown -R www-data:www-data /var/www/AI_Trade_Report
sudo chmod -R 755 /var/www/AI_Trade_Report
sudo chmod -R 777 /var/www/AI_Trade_Report/reports

echo "🔒 Getting SSL certificate for subdomain..."

# Install Certbot if not already installed
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate for subdomain
echo "📜 Getting SSL certificate for aitrade.ai-being.com..."
sudo certbot certonly --webroot -w /var/www/html -d aitrade.ai-being.com

echo "🔄 Starting services..."

# Enable and start the FastAPI service
sudo systemctl daemon-reload
sudo systemctl enable ai-trade-report
sudo systemctl start ai-trade-report

# Test Nginx configuration
sudo nginx -t

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

echo "🔧 Configuring firewall..."

# Allow Nginx through firewall
sudo ufw allow 'Nginx Full'

echo "✅ Deployment completed!"

# Check service status
echo "📊 Service Status:"
echo "Apache (existing Flask app):"
sudo systemctl status apache2 --no-pager -l | head -5

echo ""
echo "Nginx (new proxy):"
sudo systemctl status nginx --no-pager -l | head -5

echo ""
echo "FastAPI (AI Trade Report):"
sudo systemctl status ai-trade-report --no-pager -l | head -5

echo ""
echo "🌐 Your applications are now available at:"
echo "   Main domain: https://your-main-domain.com (Apache + Flask)"
echo "   Subdomain: https://aitrade.ai-being.com (Nginx + FastAPI)"
echo ""
echo "📚 FastAPI Documentation:"
echo "   https://aitrade.ai-being.com/docs"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status ai-trade-report"
echo "   sudo systemctl restart ai-trade-report"
echo "   sudo journalctl -u ai-trade-report -f"
echo "   tail -f /var/log/ai-trade-report/error.log"
echo ""
echo "🎉 Both applications are running independently!"
