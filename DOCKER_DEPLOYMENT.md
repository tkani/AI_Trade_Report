# Docker Deployment Guide - AI Trade Report

Complete Docker deployment guide for the AI Trade Report application.

## 🐳 Docker Overview

This guide covers two Docker deployment methods:
1. **Docker Compose** (Recommended for production)
2. **Single Container** (For development/testing)

## 📋 Prerequisites

- Docker installed on your server
- Docker Compose installed
- Domain name pointing to your server (optional)
- OpenAI API key

## 🚀 Method 1: Docker Compose Deployment (Recommended)

### Step 1: Prepare the Environment

```bash
# Clone the repository
git clone https://github.com/tkani/AI_Trade_Report.git
cd AI_Trade_Report

# Create environment file
cp .env_example .env
nano .env
```

Add your OpenAI API key:
```env
OPENAI_API_KEY=sk-proj-your-actual-openai-api-key-here
```

### Step 2: Configure Docker Compose

The `docker-compose.yml` file is already configured with:
- **AI Trade Report** application
- **Nginx** reverse proxy
- **Redis** for caching (optional)

### Step 3: Create Nginx Configuration

```bash
# Create nginx configuration
nano nginx.conf
```

The `nginx.conf` file includes:
- SSL/TLS configuration
- Static file serving
- Reverse proxy setup
- Security headers
- Rate limiting

### Step 4: Deploy with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 5: Set Up SSL (Optional)

If you have a domain name:

```bash
# Create SSL directory
mkdir -p ssl

# Copy your SSL certificates
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem

# Update nginx.conf with your domain
nano nginx.conf
```

## 🔧 Method 2: Single Container Deployment

### Step 1: Build the Docker Image

```bash
# Build the image
docker build -t ai-trade-report .

# Check the image
docker images | grep ai-trade-report
```

### Step 2: Run the Container

```bash
# Run the container
docker run -d \
  --name ai-trade-report \
  -p 8000:8000 \
  -e OPENAI_API_KEY=sk-proj-your-actual-key-here \
  -v $(pwd)/reports:/app/reports \
  ai-trade-report

# Check status
docker ps | grep ai-trade-report
```

### Step 3: Access the Application

- **Application**: `http://your-server-ip:8000`
- **API Docs**: `http://your-server-ip:8000/docs`

## 🐳 Docker Configuration Details

### Dockerfile Breakdown

```dockerfile
# Base image
FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential curl git

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Start command
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app:app", "--bind", "0.0.0.0:8000"]
```

### Docker Compose Services

#### AI Trade Report Service
```yaml
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
```

#### Nginx Service
```yaml
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
```

#### Redis Service (Optional)
```yaml
redis:
  image: redis:alpine
  ports:
    - "6379:6379"
  restart: unless-stopped
  command: redis-server --appendonly yes
  volumes:
    - redis_data:/data
```

## 🔧 Management Commands

### Docker Compose Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f ai-trade-report

# Update and restart
docker-compose pull
docker-compose up -d

# Scale the application
docker-compose up -d --scale ai-trade-report=3
```

### Single Container Commands

```bash
# Start container
docker start ai-trade-report

# Stop container
docker stop ai-trade-report

# Restart container
docker restart ai-trade-report

# View logs
docker logs -f ai-trade-report

# Execute command in container
docker exec -it ai-trade-report bash

# Update container
docker stop ai-trade-report
docker rm ai-trade-report
docker build -t ai-trade-report .
docker run -d --name ai-trade-report -p 8000:8000 -e OPENAI_API_KEY=your-key ai-trade-report
```

## 🔒 Security Configuration

### Environment Variables
```bash
# Create .env file
nano .env
```

```env
# OpenAI API Key
OPENAI_API_KEY=sk-proj-your-actual-key-here

# Optional: Database URL
DATABASE_URL=postgresql://user:password@localhost:5432/ai_trade_report

# Optional: Redis URL
REDIS_URL=redis://localhost:6379

# Optional: Secret Key
SECRET_KEY=your-secret-key-here
```

### SSL Configuration

#### Using Let's Encrypt with Docker
```bash
# Install certbot
sudo apt install -y certbot

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to ssl directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
sudo chown -R $USER:$USER ssl/
```

#### Using Self-Signed Certificates (Development)
```bash
# Create SSL directory
mkdir -p ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"
```

## 📊 Monitoring and Logging

### Health Checks
```bash
# Check container health
docker ps

# Check health status
docker inspect ai-trade-report | grep Health -A 10

# Manual health check
curl -f http://localhost:8000/ || echo "Health check failed"
```

### Log Management
```bash
# View application logs
docker-compose logs -f ai-trade-report

# View nginx logs
docker-compose logs -f nginx

# View all logs
docker-compose logs -f

# Rotate logs (if using logrotate)
sudo nano /etc/logrotate.d/docker-ai-trade-report
```

Add log rotation configuration:
```
/var/lib/docker/containers/*/*-json.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 root root
}
```

## 🔄 Updates and Maintenance

### Update Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backup Data
```bash
# Backup reports directory
tar -czf backup-reports-$(date +%Y%m%d).tar.gz reports/

# Backup Docker volumes
docker run --rm -v ai-trade-report_reports:/data -v $(pwd):/backup alpine tar czf /backup/backup-reports-$(date +%Y%m%d).tar.gz -C /data .
```

### Clean Up
```bash
# Remove unused images
docker image prune -f

# Remove unused containers
docker container prune -f

# Remove unused volumes
docker volume prune -f

# Remove unused networks
docker network prune -f

# Clean everything
docker system prune -a -f
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs
docker logs ai-trade-report

# Check if port is already in use
netstat -tlnp | grep 8000

# Check Docker daemon
sudo systemctl status docker
```

#### 2. Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER reports/
sudo chmod -R 755 reports/

# Check container user
docker exec -it ai-trade-report whoami
```

#### 3. Network Issues
```bash
# Check network connectivity
docker exec -it ai-trade-report ping google.com

# Check DNS resolution
docker exec -it ai-trade-report nslookup google.com
```

#### 4. SSL Issues
```bash
# Check certificate validity
openssl x509 -in ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect your-domain.com:443
```

## 📈 Production Optimizations

### Resource Limits
```yaml
# Add to docker-compose.yml
services:
  ai-trade-report:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### Load Balancing
```yaml
# Scale multiple instances
docker-compose up -d --scale ai-trade-report=3

# Use nginx load balancing
upstream ai_trade_report {
    server ai-trade-report_1:8000;
    server ai-trade-report_2:8000;
    server ai-trade-report_3:8000;
}
```

### Monitoring with Prometheus
```yaml
# Add to docker-compose.yml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

## 🎉 Deployment Complete!

Your AI Trade Report application is now running in Docker!

### Access Points:
- **Application**: `http://your-server-ip:8000` or `https://your-domain.com`
- **API Documentation**: `http://your-server-ip:8000/docs`
- **Health Check**: `http://your-server-ip:8000/`

### Next Steps:
1. Test the application thoroughly
2. Set up monitoring and alerting
3. Configure automated backups
4. Set up log aggregation
5. Implement CI/CD pipeline

For support, check the Docker logs and refer to the troubleshooting section above.
