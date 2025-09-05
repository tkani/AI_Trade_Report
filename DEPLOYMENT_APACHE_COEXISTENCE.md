# FastAPI Deployment with Apache Coexistence

Deploy AI Trade Report FastAPI application alongside existing Apache Flask application.

## 🎯 Your Setup

- **Existing**: Apache + Flask on main domain
- **New**: FastAPI on subdomain `aitrade.ai-being.com`
- **Folder**: `/var/www/AI_Trade_Report/`
- **SSL**: Existing Let's Encrypt certificate

## 📋 Prerequisites

- Ubuntu/Debian server with Apache already running
- Root/sudo access
- Domain `aitrade.ai-being.com` pointing to your server
- Existing SSL certificate (we'll create a new one for subdomain)

## 🚀 Step-by-Step Deployment

### Step 1: Install Nginx (alongside Apache)

```bash
# Install Nginx
sudo apt update
sudo apt install -y nginx

# Configure Nginx to run on different port initially
sudo nano /etc/nginx/nginx.conf
```

Add this to the `http` block in `/etc/nginx/nginx.conf`:

```nginx
http {
    # ... existing config ...

    # Add upstream for FastAPI
    upstream ai_trade_report {
        server 127.0.0.1:8000;
    }

    # Include subdomain configuration
    include /etc/nginx/sites-available/aitrade.ai-being.com;
}
```

### Step 2: Configure Nginx for Subdomain

```bash
# Create Nginx configuration for subdomain
sudo nano /etc/nginx/sites-available/aitrade.ai-being.com
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name aitrade.ai-being.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
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
        proxy_pass http://ai_trade_report;
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
```

### Step 3: Set Up Application

```bash
# Navigate to your application directory
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
```

Add your OpenAI API key to `.env`:

```env
OPENAI_API_KEY=sk-proj-your-actual-openai-api-key-here
```

### Step 4: Create Systemd Service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/ai-trade-report.service
```

Add this configuration:

```ini
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
```

### Step 5: Set Up Logging and Permissions

```bash
# Create log directory
sudo mkdir -p /var/log/ai-trade-report
sudo chown www-data:www-data /var/log/ai-trade-report

# Set proper permissions
sudo chown -R www-data:www-data /var/www/AI_Trade_Report
sudo chmod -R 755 /var/www/AI_Trade_Report
sudo chmod -R 777 /var/www/AI_Trade_Report/reports
```

### Step 6: Get SSL Certificate for Subdomain

```bash
# Install Certbot if not already installed
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate for subdomain
sudo certbot certonly --webroot -w /var/www/html -d aitrade.ai-being.com

# Alternative method if webroot doesn't work
sudo certbot certonly --standalone -d aitrade.ai-being.com
```

### Step 7: Start Services

```bash
# Enable and start the FastAPI service
sudo systemctl daemon-reload
sudo systemctl enable ai-trade-report
sudo systemctl start ai-trade-report

# Test Nginx configuration
sudo nginx -t

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status ai-trade-report
sudo systemctl status nginx
```

### Step 8: Configure Firewall

```bash
# Allow Nginx through firewall
sudo ufw allow 'Nginx Full'

# Check if Apache is still running on port 80/443
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

## 🔧 Port Configuration

### Apache Configuration (Don't Change)

- **Port 80**: Apache (main domain)
- **Port 443**: Apache (main domain with SSL)

### Nginx Configuration (New)

- **Port 80**: Nginx (aitrade.ai-being.com) → redirects to HTTPS
- **Port 443**: Nginx (aitrade.ai-being.com) → serves FastAPI
- **Port 8000**: FastAPI application (internal)

## 🚨 Troubleshooting

### Check if Both Servers Are Running

```bash
# Check Apache
sudo systemctl status apache2
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Check Nginx
sudo systemctl status nginx
sudo netstat -tlnp | grep :8000

# Check FastAPI
sudo systemctl status ai-trade-report
```

### If Port Conflicts Occur

```bash
# Check what's using port 80/443
sudo lsof -i :80
sudo lsof -i :443

# If Apache is using both ports, configure Nginx to use different ports
# Edit /etc/nginx/sites-available/aitrade.ai-being.com
# Change listen 80 to listen 8080
# Change listen 443 to listen 8443
```

### Test the Setup

```bash
# Test FastAPI directly
curl http://localhost:8000

# Test Nginx proxy
curl http://aitrade.ai-being.com

# Test HTTPS
curl https://aitrade.ai-being.com
```

## 📊 Monitoring Both Applications

### Apache (Existing Flask App)

```bash
# Check Apache logs
sudo tail -f /var/log/apache2/error.log
sudo tail -f /var/log/apache2/access.log

# Check Apache status
sudo systemctl status apache2
```

### Nginx + FastAPI (New AI Trade Report)

```bash
# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Check FastAPI logs
sudo tail -f /var/log/ai-trade-report/error.log
sudo tail -f /var/log/ai-trade-report/access.log

# Check services
sudo systemctl status nginx
sudo systemctl status ai-trade-report
```

## 🔄 Deployment Script

Create a deployment script for easy updates:

```bash
# Create deployment script
nano /var/www/AI_Trade_Report/deploy.sh
```

Add this content:

```bash
#!/bin/bash
set -e

echo "🚀 Deploying AI Trade Report..."

# Navigate to app directory
cd /var/www/AI_Trade_Report

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Restart FastAPI service
sudo systemctl restart ai-trade-report

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

echo "✅ Deployment completed!"
echo "🌐 Application available at: https://aitrade.ai-being.com"
echo "📚 API docs: https://aitrade.ai-being.com/docs"
```

Make it executable:

```bash
chmod +x /var/www/AI_Trade_Report/deploy.sh
```

## 🎯 Final Result

After deployment, you'll have:

- **Main Domain**: `your-main-domain.com` → Apache + Flask (unchanged)
- **Subdomain**: `aitrade.ai-being.com` → Nginx + FastAPI (new)
- **Both applications running independently**
- **SSL certificates for both domains**
- **No interference between applications**

## 🔍 Verification

1. **Test main domain**: `https://your-main-domain.com` (should work as before)
2. **Test subdomain**: `https://aitrade.ai-being.com` (should show AI Trade Report)
3. **Test API docs**: `https://aitrade.ai-being.com/docs`
4. **Check both services**: Both Apache and Nginx should be running

Your existing Flask application will continue to work exactly as before, while the new FastAPI application will be available on the subdomain! 🎉
