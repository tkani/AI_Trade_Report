#!/bin/bash

echo "============================================================"
echo "🚀 Starting AI Trade Report"
echo "============================================================"
echo

echo "📋 Activating virtual environment..."
source venv/bin/activate

echo
echo "🌐 Starting server..."
echo "   Server will be available at: http://127.0.0.1:8000"
echo "   Press Ctrl+C to stop the server"
echo

python run_server.py
