#!/bin/bash

# Backend Test Runner Script

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

# Check if we're in the backend directory
if [ ! -f "app/main.py" ]; then
    print_error "Please run this script from the backend directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    print_error "Virtual environment not found at ../venv"
    print_status "Please run the setup script first: ../setup.sh"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source ../venv/bin/activate

# Check if pytest is available
if ! command -v pytest >/dev/null 2>&1; then
    print_error "pytest not found. Please install test dependencies:"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Parse command line arguments
TEST_FILE=""
VERBOSE=""
COLLECT_ONLY=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -c|--collect-only)
            COLLECT_ONLY="--collect-only"
            shift
            ;;
        -f|--file)
            TEST_FILE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Backend Test Runner"
            echo
            echo "Usage: $0 [OPTIONS]"
            echo
            echo "Options:"
            echo "  -v, --verbose       Run tests with verbose output"
            echo "  -c, --collect-only  Only collect tests, don't run them"
            echo "  -f, --file FILE     Run specific test file"
            echo "  -h, --help          Show this help message"
            echo
            echo "Examples:"
            echo "  $0                    # Run all tests"
            echo "  $0 -v                 # Run all tests with verbose output"
            echo "  $0 -c                 # List all available tests"
            echo "  $0 -f test_basic_setup.py  # Run specific test file"
            echo "  $0 -f test_basic_setup.py -v  # Run specific test file with verbose output"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Run tests
print_status "Running backend tests..."

if [ -n "$COLLECT_ONLY" ]; then
    print_status "Collecting test information..."
    pytest $COLLECT_ONLY
elif [ -n "$TEST_FILE" ]; then
    if [ -f "tests/$TEST_FILE" ]; then
        print_status "Running test file: tests/$TEST_FILE"
        pytest tests/$TEST_FILE $VERBOSE
    else
        print_error "Test file not found: tests/$TEST_FILE"
        exit 1
    fi
else
    print_status "Running all tests..."
    pytest $VERBOSE
fi

# Check exit code
if [ $? -eq 0 ]; then
    print_success "All tests completed successfully!"
else
    print_error "Some tests failed!"
    exit 1
fi 