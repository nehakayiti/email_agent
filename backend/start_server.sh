#!/bin/bash

# Email Agent Backend Server Startup Script

echo "Starting Email Agent Backend Server..."

# Check if we're in the backend directory
if [ ! -f "app/main.py" ]; then
    echo "Error: Please run this script from the backend directory"
    echo "Current directory: $(pwd)"
    echo "Expected: /path/to/email_agent/backend"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "Error: Virtual environment not found at ../venv"
    echo "Please ensure the virtual environment is set up"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source ../venv/bin/activate

# Check if port 8000 is already in use
if lsof -i :8000 > /dev/null 2>&1; then
    echo "Warning: Port 8000 is already in use"
    echo "Killing existing processes on port 8000..."
    lsof -ti :8000 | xargs kill -9
    sleep 2
fi

# Start the server
echo "Starting uvicorn server on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo "----------------------------------------"

uvicorn app.main:app --reload --port 8000 