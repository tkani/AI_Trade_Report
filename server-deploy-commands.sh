#!/bin/bash

# AI Trade Report - Direct Server Deployment Commands
# Run these commands on your server: 141.136.36.151

echo "🚀 Starting AI Trade Report deployment on server..."

# Navigate to the cloned repository
cd /var/www/AI_Trade_Report

echo "📦 Installing system dependencies..."

# Update system and install required packages
apt update && apt upgrade -y
apt install -y nginx python3 python3-pip python3-venv certbot python3-certbot-nginx ufw

echo "🐍 Setting up Python environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install gunicorn uvicorn[standard]

echo "⚙️ Configuring environment..."

# Create .env file
cp .env_example .env
echo "OPENAI_API_KEY=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" > .env

echo "🔧 Creating Nginx configuration for aitrade.ai-being.com..."

# Create Nginx configuration
cat > /etc/nginx/sites-available/aitrade.ai-being.com << 'EOF'
server {
    listen 80;
    server_name aitrade.ai-being.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name aitrade.ai-being.com;
    
    # SSL configuration (we'll get certificate)
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
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # File upload size limit
    client_max_body_size 10M;
}
EOF

echo "🔧 Creating systemd service..."

# Create systemd service file
cat > /etc/systemd/system/ai-trade-report.service << 'EOF'
[Unit]
Description=AI Trade Report FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/AI_Trade_Report
Environment="PATH=/var/www/AI_Trade_Report/venv/bin"
ExecStart=/var/www/AI_Trade_Report/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 127.0.0.1:8000 --access-logfile /var/log/ai-trade-report/access.log --error-logfile /var/log/ai-trade-report/error.log
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "📁 Setting up directories and permissions..."

# Create log directory
mkdir -p /var/log/ai-trade-report
chown www-data:www-data /var/log/ai-trade-report

# Set proper permissions
chown -R www-data:www-data /var/www/AI_Trade_Report
chmod -R 755 /var/www/AI_Trade_Report
chmod -R 777 /var/www/AI_Trade_Report/reports

echo "🔒 Getting SSL certificate..."

# Get SSL certificate for subdomain
certbot certonly --webroot -w /var/www/html -d aitrade.ai-being.com --non-interactive --agree-tos --email support@aibeing.com

echo "🔄 Starting services..."

# Enable and start the FastAPI service
systemctl daemon-reload
systemctl enable ai-trade-report
systemctl start ai-trade-report

# Enable Nginx site
ln -sf /etc/nginx/sites-available/aitrade.ai-being.com /etc/nginx/sites-enabled/

# Test Nginx configuration
nginx -t

# Start Nginx
systemctl start nginx
systemctl enable nginx

echo "🔧 Configuring firewall..."

# Configure UFW
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'

echo "✅ Deployment completed!"

# Check service status
echo "📊 Service Status:"
systemctl status ai-trade-report --no-pager -l | head -5
systemctl status nginx --no-pager -l | head -5

echo ""
echo "🌐 Your application should be available at:"
echo "   https://aitrade.ai-being.com"
echo ""
echo "📚 FastAPI Documentation:"
echo "   https://aitrade.ai-being.com/docs"
echo ""
echo "🔧 Useful commands:"
echo "   systemctl status ai-trade-report"
echo "   systemctl restart ai-trade-report"
echo "   journalctl -u ai-trade-report -f"
echo "   tail -f /var/log/ai-trade-report/error.log"
echo ""
echo "🎉 Deployment successful!"
