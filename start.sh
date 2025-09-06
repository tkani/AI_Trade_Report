#!/bin/bash
set -e

# Activate virtual environment
source /opt/venv/bin/activate

# Start the application
exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
