#!/usr/bin/env python3
"""
Stable server runner for AI Trade Report application.
This script provides better error handling and stability.
"""

import uvicorn
import sys
import os
import signal
import asyncio
from pathlib import Path

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print(f"\nReceived signal {signum}, shutting down gracefully...")
    sys.exit(0)

def main():
    """Main server runner with improved stability"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Configure asyncio for better stability
    if sys.platform == "win32":
        # Windows-specific asyncio configuration
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Server configuration
    # Use 0.0.0.0 for cloud deployment, 127.0.0.1 for local development
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    # Disable reload in production (cloud deployment)
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    config = {
        "app": "app:app",
        "host": host,
        "port": port,
        "reload": reload,
        "reload_dirs": [str(Path(__file__).parent)] if reload else None,
        "reload_excludes": ["*.pyc", "__pycache__", ".git", "*.log"],
        "log_level": "info",
        "access_log": True,
        "loop": "asyncio",
        "http": "httptools",  # Use httptools for better performance
        "ws": "websockets",
        "lifespan": "on",
        "timeout_keep_alive": 30,
        "timeout_graceful_shutdown": 30,
        "limit_concurrency": 1000,
        "limit_max_requests": 10000,
    }
    
    # Remove None values from config
    config = {k: v for k, v in config.items() if v is not None}
    
    try:
        print("Starting AI Trade Report server...")
        print(f"Server will be available at: http://{host}:{port}")
        print("Press Ctrl+C to stop the server")
        
        uvicorn.run(**config)
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
