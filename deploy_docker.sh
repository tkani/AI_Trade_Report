#!/bin/bash

# AI Trade Report - Docker Deployment Script
# For aitrade.ai-being.co.uk

set -e

DOMAIN="aitrade.ai-being.co.uk"
PROJECT_DIR="/var/www/ai-trade-report"

echo "🚀 Deploying AI Trade Report with Docker to $DOMAIN..."

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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   Follow the Docker installation guide in DOCKER_COMPLETE_GUIDE.md"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   Follow the Docker installation guide in DOCKER_COMPLETE_GUIDE.md"
    exit 1
fi

echo "📋 Setting up project directory..."

# Create project directory if it doesn't exist
if [ ! -d "$PROJECT_DIR" ]; then
    echo "📁 Creating project directory..."
    sudo mkdir -p $PROJECT_DIR
    sudo chown -R $USER:$USER $PROJECT_DIR
    cd $PROJECT_DIR
    
    echo "📥 Cloning repository..."
    git clone https://github.com/tkani/AI_Trade_Report.git .
else
    echo "📁 Project directory exists, updating..."
    cd $PROJECT_DIR
    git pull origin main
fi

echo "⚙️ Configuring environment..."

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env_example .env
    echo "⚠️  Please edit .env file and add your OpenAI API key:"
    echo "   nano $PROJECT_DIR/.env"
    echo "   Add: OPENAI_API_KEY=sk-proj-your-actual-key-here"
    read -p "Press Enter after updating .env file..."
fi

echo "🔧 Setting up SSL certificates..."

# Create SSL directory
mkdir -p ssl

# Check if SSL certificates exist
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    echo "📜 Creating temporary self-signed SSL certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout ssl/key.pem \
      -out ssl/cert.pem \
      -subj "/C=GB/ST=England/L=London/O=AI Being/CN=$DOMAIN"
    
    echo "⚠️  Temporary SSL certificate created. Please replace with real certificate:"
    echo "   sudo certbot certonly --standalone -d $DOMAIN"
    echo "   sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ssl/cert.pem"
    echo "   sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ssl/key.pem"
    echo "   sudo chown -R $USER:$USER ssl/"
fi

echo "🐳 Building and starting Docker containers..."

# Build and start services
docker-compose up -d --build

echo "⏳ Waiting for services to start..."
sleep 10

echo "🔍 Checking service status..."

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Containers are running successfully!"
else
    echo "❌ Some containers failed to start. Checking logs..."
    docker-compose logs
    exit 1
fi

echo "🧪 Testing application..."

# Test the application
if curl -f http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ Application is responding!"
else
    echo "⚠️  Application test failed. Checking logs..."
    docker-compose logs ai-trade-report
fi

echo "📊 Creating management scripts..."

# Create monitoring script
cat > monitor.sh << 'EOF'
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
EOF

# Create update script
cat > update.sh << 'EOF'
#!/bin/bash
echo "Updating AI Trade Report..."
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
echo "Update completed!"
EOF

# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/ai-trade-report"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /var/www/ai-trade-report --exclude=logs --exclude=__pycache__
tar -czf $BACKUP_DIR/reports_$DATE.tar.gz /var/www/ai-trade-report/reports
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
echo "Backup completed: $BACKUP_DIR"
EOF

# Make scripts executable
chmod +x monitor.sh update.sh backup.sh

echo "✅ Deployment completed!"

# Display status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🌐 Your AI Trade Report application should be available at:"
echo "   https://$DOMAIN"
echo ""
echo "📚 FastAPI Documentation:"
echo "   https://$DOMAIN/docs"
echo ""
echo "🔧 Management Commands:"
echo "   ./monitor.sh    - Check application status"
echo "   ./update.sh     - Update application"
echo "   ./backup.sh     - Create backup"
echo "   docker-compose logs -f  - View logs"
echo "   docker-compose restart - Restart services"
echo ""
echo "⚠️  Next Steps:"
echo "   1. Update your DNS to point $DOMAIN to this server"
echo "   2. Replace temporary SSL certificate with real certificate"
echo "   3. Test the application thoroughly"
echo "   4. Set up monitoring and backups"
echo ""
echo "🎉 Docker deployment successful!"
