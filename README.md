# Email Agent

An intelligent email management system that automatically categorizes, prioritizes, and organizes your emails using machine learning and customizable rules.

## 🚀 Quick Start

### Prerequisites
- **Docker** (for PostgreSQL database)
- **Python 3.10+**
- **Node.js 18+**
- **Git**

### 1. Clone and Setup
```bash
git clone <repository-url>
cd email-agent

# Automated setup (recommended)
./setup.sh

# Or manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
```

### 2. Start the Application
```bash
# Start everything (Docker, Backend, Frontend)
./manage_app.sh start

# Check status
./manage_app.sh status
```

### 3. Access the Application
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🛠 Development Workflow

### Application Management
```bash
# Start all services
./manage_app.sh start

# Stop all services
./manage_app.sh stop

# Restart all services
./manage_app.sh restart

# Check service status
./manage_app.sh status

# View logs
./manage_app.sh logs backend
./manage_app.sh logs frontend
./manage_app.sh logs db
```

### Backend Development
```bash
cd backend
source ../venv/bin/activate

# Run tests
./run_tests.sh              # All tests
./run_tests.sh -v           # Verbose output
./run_tests.sh -c           # List all tests
./run_tests.sh -f test_basic_setup.py -v  # Specific test file

# Code quality
black .                     # Format code
flake8                      # Lint code

# Manual server start (if needed)
uvicorn app.main:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend

# Install dependencies (if needed)
npm install

# Start development server
npm run dev

# Run tests
npm run test

# Build for production
npm run build
```

### Database Management
```bash
# Start database only
docker-compose up -d db

# Access database
docker exec -i postgres_db psql -U postgres -d email_agent_db

# Run migrations
cd backend
alembic upgrade head
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
source ../venv/bin/activate

# Quick test run
./run_tests.sh -f test_basic_setup.py -v

# Full test suite
./run_tests.sh

# Test specific functionality
./run_tests.sh -f test_email_model.py -v
./run_tests.sh -f test_gmail_integration.py -v
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Manual Testing
1. **Authentication Flow**:
   - Visit http://localhost:3001
   - Click "Login" → Google OAuth → Should redirect back to frontend

2. **API Testing**:
   - Visit http://localhost:8000/docs
   - Test endpoints using Swagger UI

3. **Database Testing**:
   - Check logs: `./manage_app.sh logs db`
   - Verify connection: `docker exec postgres_db pg_isready`

## 📁 Project Structure
```
email-agent/
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   ├── tests/              # Test suite (116 tests)
│   ├── requirements.txt    # Python dependencies
│   ├── run_tests.sh        # Test runner script
│   └── start_server.sh     # Backend startup script
├── frontend/               # Next.js frontend
│   ├── src/               # Source code
│   └── package.json       # Node.js dependencies
├── manage_app.sh          # Main application manager
├── setup.sh               # First-time setup script
└── docker-compose.yaml    # Database configuration
```

## 🔧 Configuration

### Environment Variables
- **Backend**: `backend/.env` (Google OAuth, Database, Security)
- **Frontend**: `frontend/.env.local` (API endpoints)

### Key Settings
- **Frontend Port**: 3001
- **Backend Port**: 8000
- **Database Port**: 5432
- **Database**: PostgreSQL (Docker)

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Check what's using the port
lsof -i :8000
lsof -i :3001

# Kill processes
./manage_app.sh stop
```

**Database Connection Issues**
```bash
# Restart database
docker-compose down
docker-compose up -d db

# Check database logs
./manage_app.sh logs db
```

**Missing Dependencies**
```bash
# Reinstall backend dependencies
cd backend
source ../venv/bin/activate
pip install -r requirements.txt

# Reinstall frontend dependencies
cd frontend
npm install
```

**Test Failures**
```bash
# Check test database
docker exec postgres_db psql -U postgres -d email_agent_test_db -c "\dt"

# Run specific test with verbose output
./run_tests.sh -f test_basic_setup.py -v
```

### Reset Everything
```bash
# Stop all services
./manage_app.sh stop

# Remove containers and volumes
docker-compose down -v

# Reinstall dependencies
./setup.sh

# Start fresh
./manage_app.sh start
```

## 📚 API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### Key Endpoints
- `GET /auth/login` - Start OAuth flow
- `GET /auth/callback` - OAuth callback
- `GET /emails/` - List emails
- `GET /categories/` - List categories
- `POST /categories/` - Create category

## 🔒 Security

- OAuth2 authentication with Google
- JWT tokens for API access
- CORS configured for localhost development
- Environment-based configuration

## 🤝 Contributing

1. **Setup Development Environment**:
   ```bash
   ./setup.sh
   ./manage_app.sh start
   ```

2. **Run Tests**:
   ```bash
   cd backend && ./run_tests.sh
   cd frontend && npm run test
   ```

3. **Make Changes**:
   - Backend: Edit files in `backend/app/`
   - Frontend: Edit files in `frontend/src/`

4. **Test Your Changes**:
   - Manual testing via browser
   - Automated tests
   - API testing via Swagger UI

## 📞 Support

- **Application Issues**: Check logs with `./manage_app.sh logs [service]`
- **Test Issues**: Run `./run_tests.sh -v` for verbose output
- **Database Issues**: Check Docker logs and connection
- **Authentication Issues**: Verify Google OAuth configuration

---

**Quick Reference**: `./manage_app.sh help` - Shows all available commands