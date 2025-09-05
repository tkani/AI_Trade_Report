# Unix Server Deployment Guide

Complete step-by-step guide for deploying the AI Trade Report application on a Unix server.

## 🖥️ Server Requirements

### Minimum Specifications
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: 2GB minimum, 4GB recommended
- **CPU**: 2 cores minimum
- **Storage**: 20GB minimum
- **Network**: Public IP with ports 80/443 open

### Recommended Specifications
- **OS**: Ubuntu 22.04 LTS
- **RAM**: 8GB
- **CPU**: 4 cores
- **Storage**: 50GB SSD
- **Network**: Static IP with domain name

## 📋 Pre-Deployment Checklist

- [ ] Server with root/sudo access
- [ ] Domain name (optional but recommended)
- [ ] SSL certificate (Let's Encrypt recommended)
- [ ] OpenAI API key
- [ ] Basic Unix command knowledge

## 🚀 Step-by-Step Deployment

### Step 1: Server Setup and Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git vim htop unzip software-properties-common
```

### Step 2: Install Python 3.11+

```bash
# Add deadsnakes PPA for latest Python versions
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11 and pip
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Verify installation
python3.11 --version
pip3 --version
```

### Step 3: Install Nginx (Web Server)

```bash
# Install Nginx
sudo apt install -y nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

### Step 4: Install and Configure Uvicorn/Gunicorn

```bash
# Install Gunicorn for production
pip3 install gunicorn

# Install additional production dependencies
pip3 install uvicorn[standard] gunicorn
```

### Step 5: Deploy Application

```bash
# Create application directory
sudo mkdir -p /var/www/ai-trade-report
sudo chown -R $USER:$USER /var/www/ai-trade-report
cd /var/www/ai-trade-report

# Clone your repository
git clone https://github.com/tkani/AI_Trade_Report.git .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 6: Configure Environment Variables

```bash
# Create environment file
cp .env_example .env
nano .env

# Add your OpenAI API key
OPENAI_API_KEY=sk-proj-your-actual-openai-api-key-here
```

### Step 7: Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/ai-trade-report.service
```

Add the following content:

```ini
[Unit]
Description=AI Trade Report FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ai-trade-report
Environment="PATH=/var/www/ai-trade-report/venv/bin"
ExecStart=/var/www/ai-trade-report/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 127.0.0.1:8000
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### Step 8: Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/ai-trade-report
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # Replace with your domain

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Static files
    location /static/ {
        alias /var/www/ai-trade-report/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Reports directory
    location /reports/ {
        alias /var/www/ai-trade-report/reports/;
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
```

### Step 9: Enable Site and Start Services

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/ai-trade-report /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Start and enable the application service
sudo systemctl daemon-reload
sudo systemctl start ai-trade-report
sudo systemctl enable ai-trade-report

# Restart Nginx
sudo systemctl restart nginx
```

### Step 10: Configure SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

### Step 11: Configure Firewall

```bash
# Install UFW (if not already installed)
sudo apt install -y ufw

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Check status
sudo ufw status
```

### Step 12: Set Up Logging

```bash
# Create log directory
sudo mkdir -p /var/log/ai-trade-report
sudo chown www-data:www-data /var/log/ai-trade-report

# Update systemd service for logging
sudo nano /etc/systemd/system/ai-trade-report.service
```

Add logging configuration:

```ini
[Unit]
Description=AI Trade Report FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ai-trade-report
Environment="PATH=/var/www/ai-trade-report/venv/bin"
ExecStart=/var/www/ai-trade-report/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 127.0.0.1:8000 --access-logfile /var/log/ai-trade-report/access.log --error-logfile /var/log/ai-trade-report/error.log
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### Step 13: Set Up Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Create monitoring script
sudo nano /usr/local/bin/monitor-ai-trade-report.sh
```

Add monitoring script:

```bash
#!/bin/bash
echo "=== AI Trade Report Status ==="
echo "Service Status:"
systemctl status ai-trade-report --no-pager -l
echo ""
echo "Nginx Status:"
systemctl status nginx --no-pager -l
echo ""
echo "Disk Usage:"
df -h
echo ""
echo "Memory Usage:"
free -h
echo ""
echo "Recent Logs:"
tail -n 20 /var/log/ai-trade-report/error.log
```

```bash
# Make script executable
sudo chmod +x /usr/local/bin/monitor-ai-trade-report.sh
```

### Step 14: Set Up Auto-Deployment

```bash
# Create deployment script
nano /var/www/ai-trade-report/deploy.sh
```

Add deployment script:

```bash
#!/bin/bash
set -e

echo "Starting deployment..."

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart ai-trade-report

# Check status
sudo systemctl status ai-trade-report --no-pager

echo "Deployment completed successfully!"
```

```bash
# Make script executable
chmod +x /var/www/ai-trade-report/deploy.sh
```

## 🔧 Production Optimizations

### Step 15: Performance Tuning

```bash
# Optimize Nginx
sudo nano /etc/nginx/nginx.conf
```

Add to `http` block:

```nginx
# Gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_proxied any;
gzip_comp_level 6;
gzip_types
    text/plain
    text/css
    text/xml
    text/javascript
    application/json
    application/javascript
    application/xml+rss
    application/atom+xml
    image/svg+xml;

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

# In your site configuration, add:
# limit_req zone=api burst=20 nodelay;
```

### Step 16: Database Setup (Optional)

If you want to add database functionality:

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE ai_trade_report;
CREATE USER ai_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ai_trade_report TO ai_user;
\q
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Service Won't Start
```bash
# Check service status
sudo systemctl status ai-trade-report

# Check logs
sudo journalctl -u ai-trade-report -f

# Check application logs
tail -f /var/log/ai-trade-report/error.log
```

#### 2. Nginx 502 Bad Gateway
```bash
# Check if application is running
sudo netstat -tlnp | grep 8000

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart ai-trade-report
sudo systemctl restart nginx
```

#### 3. Permission Issues
```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/ai-trade-report

# Fix permissions
sudo chmod -R 755 /var/www/ai-trade-report
sudo chmod -R 777 /var/www/ai-trade-report/reports
```

#### 4. SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

## 📊 Monitoring and Maintenance

### Daily Checks
```bash
# Check service status
sudo systemctl status ai-trade-report nginx

# Check disk space
df -h

# Check memory usage
free -h

# Check logs for errors
tail -n 50 /var/log/ai-trade-report/error.log
```

### Weekly Maintenance
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Clean old logs
sudo find /var/log -name "*.log" -mtime +7 -delete

# Check SSL certificate expiry
sudo certbot certificates
```

### Monthly Tasks
```bash
# Review and rotate logs
sudo logrotate -f /etc/logrotate.conf

# Update application dependencies
cd /var/www/ai-trade-report
source venv/bin/activate
pip list --outdated
pip install --upgrade package_name
```

## 🔒 Security Best Practices

1. **Keep system updated**: Regular security updates
2. **Use strong passwords**: Complex passwords for all accounts
3. **Enable fail2ban**: Protection against brute force attacks
4. **Regular backups**: Automated backup system
5. **Monitor logs**: Regular log analysis
6. **SSL/TLS**: Always use HTTPS in production
7. **Firewall**: Proper firewall configuration
8. **API key security**: Secure storage of API keys

## 📈 Scaling Considerations

### Horizontal Scaling
- Use load balancer (HAProxy, Nginx)
- Multiple application instances
- Database clustering
- CDN for static files

### Vertical Scaling
- Increase server resources
- Optimize application code
- Database optimization
- Caching strategies

## 🆘 Support and Maintenance

### Log Locations
- Application logs: `/var/log/ai-trade-report/`
- Nginx logs: `/var/log/nginx/`
- System logs: `/var/log/syslog`

### Useful Commands
```bash
# Restart application
sudo systemctl restart ai-trade-report

# View real-time logs
sudo journalctl -u ai-trade-report -f

# Check Nginx status
sudo nginx -t

# Test SSL certificate
openssl s_client -connect your-domain.com:443
```

---

**Your AI Trade Report application is now successfully deployed on Unix server!** 🎉

For additional support, check the logs and refer to the troubleshooting section above.
