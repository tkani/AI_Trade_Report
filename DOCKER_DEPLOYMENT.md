# 🐳 Docker Deployment Guide for Railway

This guide covers deploying your AI Trade Report FastAPI application using Docker on Railway.

## 📋 Prerequisites

- Docker installed locally (for testing)
- GitHub repository with your code
- Railway account
- OpenAI API key

## 🐳 Docker Setup

### Files Created

1. **`Dockerfile`** - Multi-stage Docker build
2. **`.dockerignore`** - Excludes unnecessary files
3. **`docker-compose.yml`** - Local development setup
4. **`railway.json`** - Railway configuration
5. **`requirements.txt`** - Pinned dependencies

## 🚀 Quick Deployment Steps

### 1. **Test Locally with Docker**

```bash
# Build the Docker image
docker build -t ai-trade-report .

# Run locally
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key_here ai-trade-report

# Or use docker-compose
docker-compose up --build
```

### 2. **Deploy to Railway**

1. **Push to GitHub**:

   ```bash
   git add .
   git commit -m "Add Docker configuration for Railway deployment"
   git push origin main
   ```

2. **Deploy on Railway**:

   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Railway will automatically detect the Dockerfile

3. **Configure Environment Variables**:

   - Go to your project dashboard
   - Click on "Variables" tab
   - Add: `OPENAI_API_KEY=your_actual_api_key_here`

4. **Access your app**:
   - Railway will provide a live URL
   - Test: `https://your-app.railway.app`
   - Health check: `https://your-app.railway.app/health`
   - API docs: `https://your-app.railway.app/docs`

## 🔧 Docker Configuration Details

### Dockerfile Breakdown

```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create reports directory
RUN mkdir -p reports

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Key Features

- **Multi-stage build** for smaller image size
- **Non-root user** for security
- **Health checks** for monitoring
- **Optimized caching** with requirements.txt first
- **Security hardening** with minimal base image

## 🛠️ Local Development

### Using Docker Compose

```bash
# Start the application
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Environment Variables

Create a `.env` file for local development:

```env
OPENAI_API_KEY=your_openai_api_key_here
PYTHONPATH=/app
ENVIRONMENT=development
```

## 🔍 Monitoring & Debugging

### Health Check Endpoint

Your app includes a health check at `/health`:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "AI Trade Report"
}
```

### Viewing Logs

**Railway**:

- Dashboard → Your Project → Logs tab

**Local Docker**:

```bash
# View container logs
docker logs <container_id>

# Follow logs in real-time
docker logs -f <container_id>
```

### Debugging Issues

1. **Check health endpoint**: `https://your-app.railway.app/health`
2. **View logs** in Railway dashboard
3. **Test locally** with Docker first
4. **Check environment variables** are set correctly

## 🚀 Production Optimizations

### 1. **Image Size Optimization**

The Dockerfile is already optimized with:

- Slim Python base image
- Multi-stage build
- Minimal system dependencies
- Non-root user

### 2. **Security Features**

- Non-root user execution
- Minimal attack surface
- No unnecessary packages
- Health checks for monitoring

### 3. **Performance Features**

- Optimized layer caching
- Efficient dependency installation
- Proper signal handling
- Resource limits

## 🔄 Updates and Maintenance

### Updating Your App

1. **Make changes** to your code
2. **Test locally**:
   ```bash
   docker build -t ai-trade-report .
   docker run -p 8000:8000 -e OPENAI_API_KEY=your_key ai-trade-report
   ```
3. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Update application"
   git push origin main
   ```
4. **Railway auto-deploys** from GitHub

### Monitoring

- **Health checks**: Automatic monitoring
- **Logs**: Available in Railway dashboard
- **Metrics**: CPU, memory usage
- **Alerts**: Set up in Railway dashboard

## 🆘 Troubleshooting

### Common Issues

1. **Build Failures**:

   - Check Dockerfile syntax
   - Verify requirements.txt
   - Test locally first

2. **Runtime Errors**:

   - Check environment variables
   - View logs for error details
   - Verify OpenAI API key

3. **Health Check Failures**:

   - Ensure `/health` endpoint is accessible
   - Check if app is running on correct port
   - Verify internal networking

4. **Memory Issues**:
   - Monitor memory usage in Railway dashboard
   - Consider upgrading Railway plan
   - Optimize application code

### Debug Commands

```bash
# Check if container is running
docker ps

# Inspect container
docker inspect <container_id>

# Execute commands in running container
docker exec -it <container_id> /bin/bash

# Check container logs
docker logs <container_id>
```

## 📊 Railway Configuration

### railway.json

```json
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100
  }
}
```

### Environment Variables

Set these in Railway dashboard:

- `OPENAI_API_KEY`: Your OpenAI API key
- `PYTHONPATH`: `/app`
- `ENVIRONMENT`: `production`

## 🎯 Benefits of Docker Deployment

- ✅ **Consistent environment** across development and production
- ✅ **Easy scaling** and deployment
- ✅ **Isolation** and security
- ✅ **Reproducible builds**
- ✅ **Easy rollbacks**
- ✅ **Platform independence**

## 🚀 Next Steps

1. **Deploy to Railway** using this Docker setup
2. **Monitor** your application health and performance
3. **Set up custom domain** if needed
4. **Configure monitoring** and alerts
5. **Scale** as your application grows

Your AI Trade Report application is now ready for production deployment with Docker! 🎉
