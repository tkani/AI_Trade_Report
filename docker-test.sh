#!/bin/bash
# Docker Test Script for AI Trade Report

echo "🧪 AI Trade Report - Docker Testing"
echo "===================================="

# Test email functionality
echo "📧 Testing Email Service..."
docker-compose exec ai-trade-report python test_hosted_email.py

echo ""
echo "🤖 Testing OpenAI API..."
docker-compose exec ai-trade-report python test_openai_api.py

echo ""
echo "🔍 Checking Application Health..."
curl -f http://localhost:8000/health || echo "❌ Health check failed"

echo ""
echo "📋 Docker Container Status:"
docker-compose ps

echo ""
echo "📊 Recent Logs:"
docker-compose logs --tail=20
