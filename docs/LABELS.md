# Labels

- type:feature: Feature or increment work.
- type:bug: Defect or regression.
- type:docs | type:chore: Documentation or maintenance.
- area:backend | area:frontend | area:db | area:devops | area:ui: Primary subsystem touched.
- priority:P0–P3: Urgency (P0 critical → P3 low).
- status:blocked | status:needs-info: Workflow helpers.
- increment:1/2/3: Links to roadmap increments.

Usage
- Always add one type and one area.
- Add one priority (default P2 if unset).
- Add increment label when tied to a roadmap epic.

Create labels quickly
- Run: `bash scripts/github/create-labels.sh` (requires GitHub CLI `gh auth login`).

