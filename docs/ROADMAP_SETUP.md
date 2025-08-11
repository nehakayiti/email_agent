# Roadmap Setup (GitHub Free)

Goal: Clear execution roadmap with Issues, Projects, Milestones, and templates.

1) Create the Project (once)
- In GitHub → Projects → New Project → name "FlowMail Roadmap".
- Fields (single-select):
  - Status: Todo, Doing, Blocked, Done
  - Priority: P0, P1, P2, P3
- Fields (others):
  - Iteration: add biweekly iterations (optional)
  - Milestone: link to repo milestones
- Views: Board (group by Status), Table (sort by Priority), Roadmap (Timeline by Milestone or Iteration).
- Automation: enable "Auto-add" so new issues appear in the project.

2) Define Milestones
- Create a Milestone per increment/release (e.g., Increment 2 — Flow Buckets) with a target date.

3) Use Epic Issues
- Create an Epic issue per major increment; in its body, add a task list of child issues:
  - [ ] Flow Buckets service (2.0)
  - [ ] Flow Buckets API (2.1)
  - [ ] Tabs component (2.2)
  - [ ] Email list (2.3)
  - [ ] Dashboard page (2.4)
- Link the Epic to the Project and Milestone.

4) Create Child Issues with the Template
- Use "Feature" template to capture What, Why, Acceptance Criteria, Tests, Edge Cases.
- Add labels: type:feature, area:<subsystem>, priority:P?, increment:<n>.
- Each issue is auto-added to the Project; set Status (Todo/Doing/Done).

5) Branch Protections (recommended)
- Settings → Branches → Add rule for `main`:
  - Require pull request before merging
  - Require status checks to pass (CI jobs)
  - Dismiss stale approvals on new commits

Notes
- Keep issues small and shippable; the Project shows progress live.
- Use the PR template for consistent change docs and checks.

