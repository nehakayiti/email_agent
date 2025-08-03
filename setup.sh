#!/bin/bash

# Email Agent Setup Script
# This script sets up the project for first-time users

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.yaml" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Setting up Email Agent project..."

# Check if Docker is installed and running
if ! command -v docker >/dev/null 2>&1; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_success "Docker is available"

# Check if Python 3 is installed
if ! command -v python3 >/dev/null 2>&1; then
    print_error "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

print_success "Python 3 is available"

# Check if Node.js is installed
if ! command -v node >/dev/null 2>&1; then
    print_error "Node.js is not installed. Please install Node.js first."
    exit 1
fi

print_success "Node.js is available"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment and install backend dependencies
print_status "Installing backend dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
print_success "Backend dependencies installed"

# Install frontend dependencies
print_status "Installing frontend dependencies..."
cd frontend
npm install
cd ..
print_success "Frontend dependencies installed"

# Start Docker services
print_status "Starting Docker services..."
docker-compose up -d db

# Wait for database to be ready
print_status "Waiting for database to be ready..."
sleep 10

# Check if database is accessible
if docker exec postgres_db pg_isready -U postgres -d email_agent_db >/dev/null 2>&1; then
    print_success "Database is ready"
else
    print_warning "Database might not be fully ready yet, but setup is complete"
fi

print_success "Setup completed successfully!"
echo
echo "Next steps:"
echo "1. Start the application: ./manage_app.sh start"
echo "2. Check status: ./manage_app.sh status"
echo "3. Access the application:"
echo "   - Frontend: http://localhost:3001"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo
echo "For more information, run: ./manage_app.sh help" 