# Email Agent Development Guide

## Commands
- Backend tests: `cd backend && pytest` (single test: `pytest tests/test_file.py::test_function`)
- Frontend dev: `cd frontend && npm run dev` (or with turbopack: `next dev --turbopack`)
- Frontend lint: `cd frontend && npm run lint`
- Frontend build: `cd frontend && npm run build`
- DB migrations: `cd backend && alembic upgrade head`

## Code Style
### Backend (Python)
- Imports: standard library → third-party → local
- Snake_case for variables/functions, PascalCase for classes
- Strong typing with Python type hints and Pydantic models
- Prefer async functions for I/O operations
- Early returns and guard clauses for error handling
- Descriptive variable names with auxiliary verbs (e.g., `is_active`)

### Frontend (Next.js/TypeScript)
- Kebab-case for component files
- Prefer React Server Components, minimize client components
- Use semantic HTML and handle loading/error states
- Strict TypeScript typing with interfaces/types
- @/* path aliases for imports from src directory

## Testing
- Prefer actual databases/services over mocks
- Write focused, relevant tests that run quickly