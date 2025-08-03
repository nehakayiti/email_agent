#!/bin/bash

# Email Agent Backend Server Stop Script

echo "Stopping Email Agent Backend Server..."

# Find and kill uvicorn processes
echo "Finding uvicorn processes..."
PIDS=$(ps aux | grep uvicorn | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "No uvicorn processes found"
else
    echo "Killing uvicorn processes: $PIDS"
    echo $PIDS | xargs kill -9
fi

# Kill any processes on port 8000
echo "Checking for processes on port 8000..."
PORT_PIDS=$(lsof -ti :8000 2>/dev/null)

if [ -z "$PORT_PIDS" ]; then
    echo "No processes found on port 8000"
else
    echo "Killing processes on port 8000: $PORT_PIDS"
    echo $PORT_PIDS | xargs kill -9
fi

echo "Server stopped successfully" 