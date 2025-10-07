# Docker Deployment Guide for AI Trade Report

This guide explains how to build, run, and deploy the AI Trade Report application using Docker.

## Prerequisites

- Docker Desktop installed and running
- Docker Hub account (for pushing to registry)
- Git (for cloning the repository)

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t ai-trade-report:latest .
```

### 2. Run the Application

#### Option A: Using Docker directly
```bash
docker run -d \
  --name ai-trade-report \
  -p 8000:8000 \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/ai_trade_report.db:/app/ai_trade_report.db \
  ai-trade-report:latest
```

#### Option B: Using Docker Compose (Recommended)
```bash
docker-compose up -d
```

### 3. Access the Application

Open your browser and navigate to: `http://localhost:8000`

## Docker Compose Configuration

The `docker-compose.yml` file includes:

- **Port mapping**: Maps host port 8000 to container port 8000
- **Volume mounts**: Persists reports and database files
- **Health checks**: Monitors application health
- **Restart policy**: Automatically restarts on failure

## Pushing to Registry

### Docker Hub

1. **Login to Docker Hub**:
   ```bash
   docker login
   ```

2. **Tag your image**:
   ```bash
   docker tag ai-trade-report:latest your-username/ai-trade-report:latest
   ```

3. **Push to Docker Hub**:
   ```bash
   docker push your-username/ai-trade-report:latest
   ```

### Using the provided scripts

#### Windows (PowerShell):
```powershell
.\push-to-registry.ps1 -Registry "your-dockerhub-username" -Tag "latest"
```

#### Linux/Mac (Bash):
```bash
./push-to-registry.sh your-dockerhub-username latest
```

## Production Deployment

### Environment Variables

Create a `.env` file with the following variables:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key

# Email Configuration (for password recovery)
SMTP_HOST=your_smtp_host
SMTP_PORT=587
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_password
FROM_EMAIL=your_email@domain.com

# Security
SECRET_KEY=your_secret_key_here

# Database
DATABASE_URL=sqlite:///./ai_trade_report.db
```

### Production Docker Compose

For production deployment, use this enhanced `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  ai-trade-report:
    build: .
    container_name: ai-trade-report-prod
    ports:
      - "80:8000"
    environment:
      - PYTHONPATH=/app
      - PYTHONUNBUFFERED=1
    env_file:
      - .env
    volumes:
      - ./reports:/app/reports
      - ./ai_trade_report.db:/app/ai_trade_report.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - ai-trade-network

networks:
  ai-trade-network:
    driver: bridge
```

## Health Monitoring

The application includes health check endpoints:

- **Health Check**: `GET /health`
- **Status Check**: `GET /status`

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Change the port mapping
   docker run -p 8001:8000 ai-trade-report:latest
   ```

2. **Permission denied on volumes**:
   ```bash
   # Fix ownership
   sudo chown -R 1000:1000 ./reports
   ```

3. **Database connection issues**:
   - Ensure the database file is accessible
   - Check file permissions
   - Verify the database path in environment variables

### Logs

View application logs:
```bash
docker logs ai-trade-report
```

Follow logs in real-time:
```bash
docker logs -f ai-trade-report
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` files to version control
2. **Secrets Management**: Use Docker secrets or external secret management
3. **Network Security**: Use Docker networks to isolate services
4. **Image Security**: Regularly update base images and dependencies

## Scaling

For high-traffic deployments:

1. **Load Balancer**: Use nginx or traefik as a reverse proxy
2. **Multiple Instances**: Run multiple container instances
3. **Database**: Consider using PostgreSQL or MySQL for production
4. **Caching**: Implement Redis for session management

## Backup and Recovery

### Backup Database
```bash
docker exec ai-trade-report cp /app/ai_trade_report.db /app/backup_$(date +%Y%m%d).db
```

### Backup Reports
```bash
docker exec ai-trade-report tar -czf /app/reports_backup_$(date +%Y%m%d).tar.gz /app/reports
```

## Support

For issues and questions:
- Check the application logs
- Review the health check endpoints
- Ensure all environment variables are set correctly
- Verify Docker and Docker Compose versions

## License

This project is licensed under the MIT License.
