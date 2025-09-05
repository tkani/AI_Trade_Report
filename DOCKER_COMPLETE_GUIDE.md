# Complete Docker Deployment Guide - AI Trade Report

Complete beginner-to-production Docker deployment guide for `aitrade.ai-being.co.uk`.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Docker Installation](#docker-installation)
3. [Project Setup](#project-setup)
4. [Docker Configuration](#docker-configuration)
5. [Deployment](#deployment)
6. [SSL Setup](#ssl-setup)
7. [Production Configuration](#production-configuration)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)

## 🖥️ Prerequisites

- Ubuntu 20.04+ server (or similar Linux distribution)
- Root or sudo access
- Domain name: `aitrade.ai-being.co.uk` pointing to your server
- OpenAI API key

## 🐳 Docker Installation

### Step 1: Update System Packages

```bash
# Update package index
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install required packages
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
```

### Step 2: Add Docker's Official GPG Key

```bash
# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

### Step 3: Add Docker Repository

```bash
# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### Step 4: Install Docker Engine

```bash
# Update package index again
sudo apt update

# Install Docker Engine
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to docker group (to run docker without sudo)
sudo usermod -aG docker $USER

# Log out and log back in for group changes to take effect
# Or run: newgrp docker
```

### Step 5: Install Docker Compose

```bash
# Install Docker Compose
sudo apt install -y docker-compose

# Verify installations
docker --version
docker-compose --version
```

### Step 6: Start and Enable Docker

```bash
# Start Docker service
sudo systemctl start docker

# Enable Docker to start on boot
sudo systemctl enable docker

# Check Docker status
sudo systemctl status docker
```

### Step 7: Test Docker Installation

```bash
# Test Docker with hello-world
docker run hello-world

# If successful, you should see a message about Docker installation
```

## 📁 Project Setup

### Step 1: Create Project Directory

```bash
# Create project directory
sudo mkdir -p /var/www/ai-trade-report
sudo chown -R $USER:$USER /var/www/ai-trade-report
cd /var/www/ai-trade-report
```

### Step 2: Clone Repository

```bash
# Clone the repository
git clone https://github.com/tkani/AI_Trade_Report.git .

# Verify files
ls -la
```

### Step 3: Create Environment File

```bash
# Create environment file
cp .env_example .env
nano .env
```

Add your configuration:
```env
# OpenAI API Key
OPENAI_API_KEY=sk-proj-your-actual-openai-api-key-here

# Application settings
APP_NAME=AI Trade Report
APP_ENV=production
DEBUG=false

# Domain settings
DOMAIN=aitrade.ai-being.co.uk
```

## 🐳 Docker Configuration

### Step 1: Create Dockerfile

The `Dockerfile` is already included in the repository. Here's what it does:

```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create reports directory
RUN mkdir -p reports

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Start command
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app:app", "--bind", "0.0.0.0:8000"]
```

### Step 2: Create Docker Compose Configuration

The `docker-compose.yml` is already included. Here's what it contains:

```yaml
version: '3.8'

services:
  ai-trade-report:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./reports:/app/reports
      - ./static:/app/static
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./static:/var/www/static:ro
      - ./reports:/var/www/reports:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - ai-trade-report
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### Step 3: Create Nginx Configuration

The `nginx.conf` is already included. Here's what it contains:

```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

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

    # Upstream for FastAPI
    upstream ai_trade_report {
        server ai-trade-report:8000;
    }

    # HTTP server (redirect to HTTPS)
    server {
        listen 80;
        server_name aitrade.ai-being.co.uk;
        return 301 https://$host$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name aitrade.ai-being.co.uk;

        # SSL configuration (will be updated with real certificates)
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Static files
        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Reports directory
        location /reports/ {
            alias /var/www/reports/;
            expires 1h;
            add_header Cache-Control "public";
        }

        # Main application
        location / {
            limit_req zone=api burst=20 nodelay;
            
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
}
```

## 🚀 Deployment

### Step 1: Build and Start Services

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 2: Verify Deployment

```bash
# Check if containers are running
docker ps

# Test the application
curl http://localhost:8000

# Check health status
docker-compose exec ai-trade-report curl -f http://localhost:8000/
```

### Step 3: Access the Application

- **Application**: `http://your-server-ip` (will redirect to HTTPS)
- **API Documentation**: `http://your-server-ip/docs`

## 🔒 SSL Setup

### Step 1: Install Certbot

```bash
# Install certbot
sudo apt install -y certbot

# Install nginx plugin for certbot
sudo apt install -y python3-certbot-nginx
```

### Step 2: Create SSL Directory

```bash
# Create SSL directory
mkdir -p ssl

# Generate temporary self-signed certificate for initial setup
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem \
  -subj "/C=GB/ST=England/L=London/O=AI Being/CN=aitrade.ai-being.co.uk"
```

### Step 3: Get Real SSL Certificate

```bash
# Stop nginx container temporarily
docker-compose stop nginx

# Get SSL certificate
sudo certbot certonly --standalone -d aitrade.ai-being.co.uk

# Copy certificates to ssl directory
sudo cp /etc/letsencrypt/live/aitrade.ai-being.co.uk/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/aitrade.ai-being.co.uk/privkey.pem ssl/key.pem
sudo chown -R $USER:$USER ssl/

# Start nginx container
docker-compose start nginx
```

### Step 4: Set Up Auto-Renewal

```bash
# Create renewal script
sudo nano /usr/local/bin/renew-ssl.sh
```

Add this content:
```bash
#!/bin/bash
# Renew SSL certificates
certbot renew --quiet

# Copy new certificates
cp /etc/letsencrypt/live/aitrade.ai-being.co.uk/fullchain.pem /var/www/ai-trade-report/ssl/cert.pem
cp /etc/letsencrypt/live/aitrade.ai-being.co.uk/privkey.pem /var/www/ai-trade-report/ssl/key.pem

# Restart nginx container
cd /var/www/ai-trade-report
docker-compose restart nginx
```

```bash
# Make script executable
sudo chmod +x /usr/local/bin/renew-ssl.sh

# Add to crontab for automatic renewal
sudo crontab -e
```

Add this line:
```
0 2 * * * /usr/local/bin/renew-ssl.sh
```

## 🔧 Production Configuration

### Step 1: Environment Variables

```bash
# Create production environment file
nano .env.production
```

Add production settings:
```env
# OpenAI API Key
OPENAI_API_KEY=sk-proj-your-actual-openai-api-key-here

# Application settings
APP_NAME=AI Trade Report
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Domain settings
DOMAIN=aitrade.ai-being.co.uk
BASE_URL=https://aitrade.ai-being.co.uk

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=aitrade.ai-being.co.uk

# Database (if needed)
DATABASE_URL=sqlite:///./ai_trade_report.db

# Redis (if needed)
REDIS_URL=redis://redis:6379
```

### Step 2: Resource Limits

Update `docker-compose.yml` to add resource limits:

```yaml
services:
  ai-trade-report:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./reports:/app/reports
      - ./static:/app/static
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Step 3: Logging Configuration

```bash
# Create log directory
mkdir -p logs

# Update docker-compose.yml to include logging
```

Add logging configuration to `docker-compose.yml`:
```yaml
services:
  ai-trade-report:
    # ... existing configuration ...
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 📊 Monitoring & Maintenance

### Step 1: Create Monitoring Script

```bash
# Create monitoring script
nano monitor.sh
```

Add this content:
```bash
#!/bin/bash
echo "=== AI Trade Report Status ==="
echo "Docker Status:"
docker ps | grep ai-trade-report
echo ""
echo "Container Health:"
docker inspect ai-trade-report | grep Health -A 10
echo ""
echo "Recent Logs:"
docker-compose logs --tail=20 ai-trade-report
echo ""
echo "Disk Usage:"
df -h
echo ""
echo "Memory Usage:"
free -h
echo ""
echo "Docker System Info:"
docker system df
```

```bash
# Make script executable
chmod +x monitor.sh
```

### Step 2: Backup Script

```bash
# Create backup script
nano backup.sh
```

Add this content:
```bash
#!/bin/bash
BACKUP_DIR="/backup/ai-trade-report"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application files
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /var/www/ai-trade-report --exclude=logs --exclude=__pycache__

# Backup reports
tar -czf $BACKUP_DIR/reports_$DATE.tar.gz /var/www/ai-trade-report/reports

# Backup Docker volumes
docker run --rm -v ai-trade-report_redis_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/redis_$DATE.tar.gz -C /data .

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR"
```

```bash
# Make script executable
chmod +x backup.sh

# Add to crontab for daily backups
crontab -e
```

Add this line:
```
0 3 * * * /var/www/ai-trade-report/backup.sh
```

### Step 3: Update Script

```bash
# Create update script
nano update.sh
```

Add this content:
```bash
#!/bin/bash
echo "Updating AI Trade Report..."

# Pull latest changes
git pull origin main

# Rebuild and restart containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check status
docker-compose ps

echo "Update completed!"
```

```bash
# Make script executable
chmod +x update.sh
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs
docker-compose logs ai-trade-report

# Check if port is in use
netstat -tlnp | grep 8000

# Check Docker daemon
sudo systemctl status docker
```

#### 2. Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER /var/www/ai-trade-report
chmod -R 755 /var/www/ai-trade-report
chmod -R 777 /var/www/ai-trade-report/reports
```

#### 3. SSL Issues
```bash
# Check certificate validity
openssl x509 -in ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect aitrade.ai-being.co.uk:443
```

#### 4. Memory Issues
```bash
# Check memory usage
docker stats

# Clean up unused resources
docker system prune -a -f
```

### Useful Commands

```bash
# View all containers
docker ps -a

# View container logs
docker-compose logs -f ai-trade-report

# Execute command in container
docker-compose exec ai-trade-report bash

# Restart specific service
docker-compose restart ai-trade-report

# Scale application
docker-compose up -d --scale ai-trade-report=3

# View resource usage
docker stats

# Clean up
docker system prune -a -f
```

## 🎉 Deployment Complete!

Your AI Trade Report application should now be available at:
- **Main Application**: `https://aitrade.ai-being.co.uk`
- **API Documentation**: `https://aitrade.ai-being.co.uk/docs`

### Next Steps:
1. Test the application thoroughly
2. Set up monitoring and alerting
3. Configure automated backups
4. Set up log aggregation
5. Implement CI/CD pipeline

### Management Commands:
- **Monitor**: `./monitor.sh`
- **Backup**: `./backup.sh`
- **Update**: `./update.sh`
- **View Logs**: `docker-compose logs -f`
- **Restart**: `docker-compose restart`

For support, check the Docker logs and refer to the troubleshooting section above.
