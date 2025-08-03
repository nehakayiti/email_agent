#!/bin/bash

# Email Agent Application Management Script
# This script manages the entire application stack: Docker, Database, Backend, and Frontend

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3001
DB_PORT=5432
DB_CONTAINER="postgres_db"
DB_NAME="email_agent_db"
DB_USER="postgres"
DB_PASSWORD="postgres"

# Function to print colored output
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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to wait for database to be ready
wait_for_db() {
    print_status "Waiting for database to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec $DB_CONTAINER pg_isready -U $DB_USER -d $DB_NAME >/dev/null 2>&1; then
            print_success "Database is ready!"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts - Database not ready yet, waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "Database failed to start within $max_attempts attempts"
    return 1
}

# Function to check Docker
check_docker() {
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker is available and running"
}

# Function to start Docker services
start_docker() {
    print_status "Starting Docker services..."
    
    if docker ps | grep -q $DB_CONTAINER; then
        print_warning "Database container is already running"
    else
        print_status "Starting database container..."
        docker-compose up -d db
        sleep 3
    fi
    
    if ! wait_for_db; then
        print_error "Failed to start database"
        exit 1
    fi
    
    print_success "Docker services started successfully"
}

# Function to stop Docker services
stop_docker() {
    print_status "Stopping Docker services..."
    docker-compose down
    print_success "Docker services stopped"
}

# Function to check virtual environment
check_venv() {
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Please create it first:"
        echo "  python3 -m venv venv"
        echo "  source venv/bin/activate"
        echo "  pip install -r backend/requirements.txt"
        exit 1
    fi
    print_success "Virtual environment found"
}

# Function to start backend
start_backend() {
    print_status "Starting backend server..."
    
    if port_in_use $BACKEND_PORT; then
        print_warning "Port $BACKEND_PORT is already in use. Stopping existing processes..."
        lsof -ti :$BACKEND_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    cd backend
    
    # Activate virtual environment and start server
    source ../venv/bin/activate
    nohup uvicorn app.main:app --reload --port $BACKEND_PORT > server.log 2>&1 &
    BACKEND_PID=$!
    
    cd ..
    
    # Wait for backend to start
    sleep 5
    
    if curl -s http://localhost:$BACKEND_PORT/docs >/dev/null 2>&1; then
        print_success "Backend server started on http://localhost:$BACKEND_PORT"
        echo $BACKEND_PID > .backend.pid
    else
        print_error "Failed to start backend server"
        exit 1
    fi
}

# Function to stop backend
stop_backend() {
    print_status "Stopping backend server..."
    
    if [ -f .backend.pid ]; then
        BACKEND_PID=$(cat .backend.pid)
        if ps -p $BACKEND_PID >/dev/null 2>&1; then
            kill -9 $BACKEND_PID 2>/dev/null || true
        fi
        rm -f .backend.pid
    fi
    
    # Also kill any uvicorn processes
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    
    print_success "Backend server stopped"
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend server..."
    
    if port_in_use $FRONTEND_PORT; then
        print_warning "Port $FRONTEND_PORT is already in use. Stopping existing processes..."
        lsof -ti :$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    # Start frontend
    nohup npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    cd ..
    
    # Wait for frontend to start
    sleep 10
    
    if curl -s http://localhost:$FRONTEND_PORT >/dev/null 2>&1; then
        print_success "Frontend server started on http://localhost:$FRONTEND_PORT"
        echo $FRONTEND_PID > .frontend.pid
    else
        print_error "Failed to start frontend server"
        exit 1
    fi
}

# Function to stop frontend
stop_frontend() {
    print_status "Stopping frontend server..."
    
    if [ -f .frontend.pid ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if ps -p $FRONTEND_PID >/dev/null 2>&1; then
            kill -9 $FRONTEND_PID 2>/dev/null || true
        fi
        rm -f .frontend.pid
    fi
    
    # Also kill any node processes running on the frontend port
    lsof -ti :$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
    
    print_success "Frontend server stopped"
}

# Function to check application status
check_status() {
    echo "=== Email Agent Application Status ==="
    echo
    
    # Check Docker
    echo "Docker Services:"
    if docker ps | grep -q $DB_CONTAINER; then
        echo -e "  ${GREEN}✓${NC} Database container is running"
    else
        echo -e "  ${RED}✗${NC} Database container is not running"
    fi
    echo
    
    # Check Backend
    echo "Backend Server:"
    if curl -s http://localhost:$BACKEND_PORT/docs >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Backend is running on http://localhost:$BACKEND_PORT"
    else
        echo -e "  ${RED}✗${NC} Backend is not running"
    fi
    echo
    
    # Check Frontend
    echo "Frontend Server:"
    if curl -s http://localhost:$FRONTEND_PORT >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Frontend is running on http://localhost:$FRONTEND_PORT"
    else
        echo -e "  ${RED}✗${NC} Frontend is not running"
    fi
    echo
    
    # Check Database Connection
    echo "Database Connection:"
    if docker exec $DB_CONTAINER pg_isready -U $DB_USER -d $DB_NAME >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Database is accessible"
    else
        echo -e "  ${RED}✗${NC} Database is not accessible"
    fi
    echo
}

# Function to show logs
show_logs() {
    local service=$1
    
    case $service in
        "backend")
            if [ -f "backend/server.log" ]; then
                tail -f backend/server.log
            else
                print_error "Backend log file not found"
            fi
            ;;
        "frontend")
            if [ -f "frontend.log" ]; then
                tail -f frontend.log
            else
                print_error "Frontend log file not found"
            fi
            ;;
        "db"|"database")
            docker logs -f $DB_CONTAINER
            ;;
        *)
            print_error "Unknown service: $service"
            print_status "Available services: backend, frontend, db"
            ;;
    esac
}

# Function to show help
show_help() {
    echo "Email Agent Application Management Script"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start       Start all services (Docker, Backend, Frontend)"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  status      Show status of all services"
    echo "  logs [service] Show logs for a specific service (backend|frontend|db)"
    echo "  help        Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 stop"
    echo "  $0 status"
    echo "  $0 logs backend"
    echo
}

# Main script logic
case "${1:-help}" in
    "start")
        print_status "Starting Email Agent Application..."
        check_docker
        check_venv
        start_docker
        start_backend
        start_frontend
        print_success "All services started successfully!"
        echo
        echo "Application URLs:"
        echo "  Frontend: http://localhost:$FRONTEND_PORT"
        echo "  Backend API: http://localhost:$BACKEND_PORT"
        echo "  API Docs: http://localhost:$BACKEND_PORT/docs"
        echo
        ;;
    "stop")
        print_status "Stopping Email Agent Application..."
        stop_frontend
        stop_backend
        stop_docker
        print_success "All services stopped successfully!"
        ;;
    "restart")
        print_status "Restarting Email Agent Application..."
        $0 stop
        sleep 2
        $0 start
        ;;
    "status")
        check_status
        ;;
    "logs")
        show_logs $2
        ;;
    "help"|*)
        show_help
        ;;
esac 