#!/bin/bash

echo "============================================================"
echo "🚀 AI Trade Report - Quick Setup (Unix/Linux/macOS)"
echo "============================================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $2 -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
        exit 1
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "📋 Checking Python installation..."
python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    print_status "Python 3.8+ is required but not found" 1
fi
print_status "Python $(python3 --version | cut -d' ' -f2) detected" 0

echo
echo "📦 Creating virtual environment..."
python3 -m venv venv
print_status "Virtual environment created" $?

echo
echo "📚 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt
print_status "Dependencies installed" $?

echo
echo "⚙️  Setting up configuration..."
if [ ! -f .env ]; then
    cp .env_example .env
    print_status ".env file created from template" 0
else
    print_warning ".env file already exists"
fi

echo
echo "📁 Creating directories..."
mkdir -p reports static/css static/js static/images templates
print_status "Directories created" 0

echo
echo "🔧 Making scripts executable..."
chmod +x setup.sh run.sh
print_status "Scripts made executable" 0

echo
echo "============================================================"
echo "🎉 Setup Complete!"
echo "============================================================"
echo
echo "📋 Next Steps:"
echo "1. Edit the .env file with your configuration:"
echo "   - OpenAI API key"
echo "   - Email settings (for password recovery)"
echo "   - Secret key (change the default)"
echo
echo "2. Start the application:"
echo "   ./run.sh"
echo
echo "3. Open your browser and go to:"
echo "   http://127.0.0.1:8000"
echo
echo "📖 For detailed instructions, see INSTALLATION.md"
echo
