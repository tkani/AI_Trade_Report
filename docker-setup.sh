#!/bin/bash
# Docker Setup Script for AI Trade Report

echo "🐳 AI Trade Report - Docker Setup"
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env_example .env
    echo "✅ .env file created from .env_example"
    echo "⚠️  Please edit .env file with your actual values before running Docker"
else
    echo "✅ .env file already exists"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Build and start the application
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting AI Trade Report application..."
docker-compose up -d

echo "✅ Application started successfully!"
echo ""
echo "📋 Useful Commands:"
echo "   View logs:     docker-compose logs -f"
echo "   Stop app:      docker-compose down"
echo "   Restart app:   docker-compose restart"
echo "   Test email:    docker-compose exec ai-trade-report python test_hosted_email.py"
echo "   Test OpenAI:   docker-compose exec ai-trade-report python test_openai_api.py"
echo ""
echo "🌐 Application URL: http://localhost:8000"
echo "📧 Test email functionality with the test scripts above"
