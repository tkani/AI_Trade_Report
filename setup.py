#!/usr/bin/env python3
"""
AI Trade Report - Quick Setup Script
This script helps you set up the AI Trade Report application quickly.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    print("=" * 60)
    print("🚀 AI Trade Report - Quick Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("📋 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def create_virtual_environment():
    """Create virtual environment"""
    print("\n📦 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False

def install_dependencies():
    """Install required packages"""
    print("\n📚 Installing dependencies...")
    try:
        # Determine the correct pip path
        if os.name == 'nt':  # Windows
            pip_path = "venv\\Scripts\\pip"
        else:  # macOS/Linux
            pip_path = "venv/bin/pip"
        
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_env_file():
    """Create .env file from template"""
    print("\n⚙️  Setting up environment configuration...")
    
    if os.path.exists(".env"):
        print("⚠️  .env file already exists")
        response = input("   Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("   Keeping existing .env file")
            return True
    
    if not os.path.exists(".env_example"):
        print("❌ .env_example file not found")
        return False
    
    try:
        shutil.copy(".env_example", ".env")
        print("✅ .env file created from template")
        print("   📝 Please edit .env file with your configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating necessary directories...")
    directories = ["reports", "static/css", "static/js", "static/images", "templates"]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")
    return True

def show_next_steps():
    """Show next steps to the user"""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    print()
    print("📋 Next Steps:")
    print("1. Edit the .env file with your configuration:")
    print("   - OpenAI API key")
    print("   - Email settings (for password recovery)")
    print("   - Secret key (change the default)")
    print()
    print("2. Activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # macOS/Linux
        print("   source venv/bin/activate")
    print()
    print("3. Start the application:")
    print("   python run_server.py")
    print()
    print("4. Open your browser and go to:")
    print("   http://127.0.0.1:8000")
    print()
    print("📖 For detailed instructions, see INSTALLATION.md")
    print()

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main()
