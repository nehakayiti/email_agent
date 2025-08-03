# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload  # Start development server

# Testing
pytest                         # Run all tests
pytest -m "not slow"          # Skip slow tests  
pytest -k test_name           # Run specific test

# Database migrations
alembic upgrade head          # Apply migrations
alembic revision --autogenerate -m "description"  # Create migration
```

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev                   # Start development server on port 3001
npm run build                 # Build for production
npm run start                 # Start production server
npm run lint                  # Lint code

# Testing (Playwright E2E)
npm run e2e                   # Run end-to-end tests
npm run test:real-api         # Run tests against real API
npm run test:real-api:headed  # Run tests with browser UI
npm run test:real-api:debug   # Run tests in debug mode

# Gmail Credentials Refresh (when tests fail with invalid_grant)
python refresh_test_credentials.py  # Refresh expired Gmail test credentials
```

## Architecture Overview

This is an **intelligent email management system** with AI-powered categorization and Gmail integration.

### Backend Architecture (FastAPI)
- **Main App**: `app/main.py` - FastAPI application with lifespan management and router setup
- **Configuration**: `app/config.py` - Pydantic settings with environment variables
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Authentication**: OAuth2 with Google, JWT tokens
- **Key Services**:
  - `services/email_sync_service.py` - Gmail API integration and sync
  - `services/categorization_service.py` - AI-powered email categorization
  - `services/action_engine_service.py` - Automated email actions (archive/trash)
  - `services/analytics/` - Email analytics and reporting
- **Models**: SQLAlchemy models in `models/` (User, Email, EmailCategory, etc.)
- **API Routes**: Organized in `routers/` by feature area

### Frontend Architecture (Next.js 15)
- **App Router**: Modern Next.js app directory structure
- **Layout**: `src/app/layout.tsx` - Root layout with CategoryProvider context
- **API Client**: `src/lib/api.ts` - Centralized API communication with auth handling
- **Key Features**:
  - Email management interface with categorization
  - Analytics dashboard with charts (Chart.js)
  - Category management (keywords, sender rules)
  - Action engine for automated email processing
- **Components**: Reusable UI components in `src/components/`
- **Styling**: Tailwind CSS with custom components

### Key Integrations
- **Gmail API**: Full email sync, labeling, and operations
- **Machine Learning**: Naive Bayes classifier for email categorization
- **Real-time Sync**: Bidirectional sync between Gmail and local database

## Development Workflow

### Environment Setup
- Backend requires `.env` file with Google OAuth credentials and database URL
- Frontend requires `.env.local` with API URL and test mode flag
- PostgreSQL database (default: `email_agent_db`)

### Testing Strategy
- **Backend**: pytest with real database integration tests
- **Frontend**: Playwright E2E tests with test mode support
- Tests use real API connections, not mocks
- Special test mode available via `NEXT_PUBLIC_TEST_MODE=true`

### Key Development Patterns
- **Backend**: Functional programming over classes, Pydantic models, dependency injection
- **Frontend**: Server Components preferred, Client Components for interactivity only
- **Error Handling**: Graceful auth error handling with automatic login redirects
- **API Design**: RESTful with consistent response formats

## Security Requirements

**🔒 CRITICAL: NO SECRETS IN SOURCE CODE**
- **NEVER** commit API keys, client secrets, tokens, or passwords to git
- **ALWAYS** use environment variables (.env, .env.test) for sensitive data
- **NEVER** hardcode credentials in any source files
- When providing credential refresh instructions, use `os.getenv()` to read from environment
- All OAuth credentials must be stored in `.env.test` and referenced dynamically

## Important Notes

- The system operates in two modes: PLAN (gather info) and ACT (make changes)
- Memory bank files in `memory-bank/` contain project context
- Cursor rules in `.cursor/rules/` define coding standards
- ML models stored in `models/` directory (created at runtime)
- Logging configured centrally in `backend/app/core/logging_config.py`
- CORS configured for localhost development
- Database migrations managed through Alembic
- **Gmail Test Credential Refresh**: When tests fail with `invalid_grant`, use manual OAuth flow with credentials from `.env.test`

## File Locations
- **Backend config**: `backend/app/config.py`
- **API client**: `frontend/src/lib/api.ts`
- **Main layouts**: `frontend/src/app/layout.tsx`, `frontend/src/components/layout/`
- **Database models**: `backend/app/models/`
- **Test configurations**: `backend/pytest.ini`, `frontend/playwright.config*.ts`