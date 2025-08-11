Title: <area>: <short summary>

What
- Concise description of the change and scope.

Why
- Problem being solved and user value.

Changes
- Key files/modules touched and notable decisions.

Screenshots/Video (UI)
- Before/After visuals or short clip if applicable.

DB/Migrations
- Any schema updates, data backfills, or Alembic steps.

Tests
- Added/updated tests and coverage focus; how to run them.

Risk & Rollout
- Risks, toggles/flags, and backout plan.

Checklist
- [ ] Branch created (no direct commits to `main`)
- [ ] All tests pass locally: `cd backend && ./run_tests.sh` and `cd frontend && npm run build && npm run e2e`
- [ ] Linters clean: `black --check . && flake8` (backend), `npm run lint` (frontend)
- [ ] Linked issues and added labels (type/area/priority)
- [ ] Updated docs/README where needed

