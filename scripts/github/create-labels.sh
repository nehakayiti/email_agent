#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI 'gh' is required. Install: https://cli.github.com/" >&2
  exit 1
fi

create_or_update() {
  local name="$1"; local color="$2"; local desc="$3"
  if gh label list --limit 1000 | awk '{print $1}' | grep -Fxq "$name"; then
    gh label edit "$name" --color "$color" --description "$desc" >/dev/null
  else
    gh label create "$name" --color "$color" --description "$desc" >/dev/null
  fi
  echo "✓ $name"
}

echo "Creating/updating standard labels..."

# Types
create_or_update "type:feature" "0E8A16" "Feature or increment"
create_or_update "type:bug" "D93F0B" "Bug or regression"
create_or_update "type:chore" "BFDADC" "Maintenance/chore"
create_or_update "type:docs" "0052CC" "Documentation"

# Areas
create_or_update "area:backend" "5319E7" "Backend / FastAPI"
create_or_update "area:frontend" "1D76DB" "Frontend / Next.js"
create_or_update "area:db" "0B7261" "Database / migrations"
create_or_update "area:devops" "6F42C1" "Infra / CI / tooling"
create_or_update "area:ui" "A2EEEF" "UI / Components"

# Priority
create_or_update "priority:P0" "E11D21" "Critical — immediate attention"
create_or_update "priority:P1" "EB6420" "High — next up"
create_or_update "priority:P2" "FBCA04" "Medium"
create_or_update "priority:P3" "CCCCCC" "Low"

# Status helpers
create_or_update "status:blocked" "B60205" "Blocked by dependency/info"
create_or_update "status:needs-info" "BFD4F2" "Needs more info"

# Increments (customize as needed)
create_or_update "increment:1" "0366D6" "Increment 1"
create_or_update "increment:2" "0969DA" "Increment 2"
create_or_update "increment:3" "2188FF" "Increment 3"

echo "Done. If prompted, run 'gh auth login' and rerun."

