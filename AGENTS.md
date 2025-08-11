# Repository Guidelines

## Project Structure & Modules
- Backend (FastAPI): `backend/app` (routers, models, services); tests in `backend/tests`.
- Frontend (Next.js): `frontend/src` (app, components, lib, utils).
- Tooling/Ops: `manage_app.sh`, `docker-compose.yaml`, `setup.sh`, `backend/run_tests.sh`.

## Build, Test, Run
- Setup: `./setup.sh` or `pip install -r backend/requirements.txt && (cd frontend && npm install)`.
- Start/Stop/Status: `./manage_app.sh start|stop|status`.
- Backend dev: `cd backend && source ../venv/bin/activate && uvicorn app.main:app --reload --port 8000`.
- Backend tests: `cd backend && ./run_tests.sh [-v|-c|-f <file>]`.
- Frontend dev: `cd frontend && npm run dev` (3001); build: `npm run build`; e2e: `npm run e2e`.

## Coding Style & Naming
- Python: 4‑space indent; `black .` and `flake8` before pushing; files/modules `snake_case`; Pydantic schemas in `backend/app/schemas`.
- TypeScript/React: `npm run lint`; components in `frontend/src/components` use `PascalCase`; hooks/utilities `camelCase`.
- API layout: routes in `backend/app/routers`; request/response models in `schemas`; business logic in `services`.

## Testing Guidelines
- Backend: `pytest` via `./run_tests.sh`; name tests `test_*.py`; mark slow with `@pytest.mark.slow`.
- Frontend: Playwright tests in `frontend/tests`; run `npm run e2e` or `npm run test:real-api`.
- Coverage focus: auth, email sync, action execution, migrations.

## Commit & Pull Requests
- Branching: CHANGES SHOULD ALWAYS BE MADE IN A SEPARATE BRANCH (e.g., `git checkout -b feat/<scope>`). Never commit to `main`.
- Commits: present‑tense, scoped prefix (e.g., `backend: fix token refresh`); one topic per commit.
- PRs: small and focused (<300 LOC). Include description, linked issues, test steps, UI screenshots if relevant, and migration notes.
- Tests: All Backend and Frontend tests MUST pass locally and in CI.

## Git Workflow (Quick)
- Create: `git checkout -b feat/<scope>`
- Sync: `git fetch origin && git rebase origin/main`
- Commit/Push: `git add -A && git commit -m "<area>: <change>" && git push -u origin feat/<scope>`
- Open PR → request review → rebase before merge; prefer squash merge.

## CI Checks
- Lint: `black --check .` and `flake8` (backend); `npm run lint` (frontend).
- Backend tests: `cd backend && ./run_tests.sh`.
- Frontend e2e: `cd frontend && npm run e2e` (headed/real‑api variants available).
- Build sanity: `cd frontend && npm run build`; backend starts via `uvicorn` without errors.

## Security & Config
- Never commit secrets; use `backend/.env`, `backend/.env.test`, `frontend/.env.local`.
- Default ports: API 8000, UI 3001, DB 5432; DB only: `docker-compose up -d db`; migrations: `cd backend && alembic upgrade head`.
