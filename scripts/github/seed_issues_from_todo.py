#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from typing import List, Optional


INC_RE = re.compile(r"^###\s+Increment\s+(?P<num>\d+):\s*(?P<title>.+)")
PROMPT_RE = re.compile(r"^####\s+Prompt\s+(?P<num>[\d\.]+):\s*(?P<title>.+)")
SECTION_RE = re.compile(r"^\*\*(?P<name>[^*]+)\*\*:\s*$")


@dataclass
class Prompt:
    increment_num: int
    increment_title: str
    prompt_num: str
    title: str
    goal: str = ""
    atomic_change: List[str] = field(default_factory=list)
    testing_instructions: List[str] = field(default_factory=list)
    expected_result: List[str] = field(default_factory=list)

    @property
    def issue_title(self) -> str:
        return f"feat: Increment {self.increment_num} — {self.title}"[:240]

    def to_issue_body(self) -> str:
        ac_items = "\n".join(f"- {line}" for line in self.expected_result if line.strip())
        atomic = "\n".join(f"- {line}" for line in self.atomic_change if line.strip())
        tests = "\n".join(self.testing_instructions)
        return f"""
What
- {self.increment_title}: {self.title}

Why
- {self.goal.strip() or 'See increment goal.'}

Acceptance Criteria
{ac_items or '- Defined and validated in PR.'}

Plan / Changes
{atomic or '- See implementation details in PR.'}

Tests
{tests or '- Add unit/integration/e2e as applicable.'}

Edge Cases
- Empty results, pagination bounds, stale data, auth failures

Dependencies
- Increment {self.increment_num}
""".strip()


def parse_todo(path: str, only_increment: Optional[int] = None) -> List[Prompt]:
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    prompts: List[Prompt] = []
    inc_num = None
    inc_title = ""
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        inc_m = INC_RE.match(line)
        if inc_m:
            inc_num = int(inc_m.group("num"))
            inc_title = inc_m.group("title").strip()
            i += 1
            continue

        pr_m = PROMPT_RE.match(line)
        if pr_m and inc_num is not None:
            if only_increment is not None and inc_num != only_increment:
                # skip this prompt block entirely
                i += 1
                continue
            prompt = Prompt(
                increment_num=inc_num,
                increment_title=inc_title,
                prompt_num=pr_m.group("num"),
                title=pr_m.group("title").strip(),
            )
            # parse sections until next prompt/increment
            section = None
            buf: List[str] = []
            j = i + 1
            def flush_section(name: Optional[str]):
                nonlocal buf, prompt
                content = [b.strip() for b in buf if b.strip()]
                if not name:
                    return
                name = name.lower()
                if name.startswith("goal"):
                    prompt.goal = " ".join(content)
                elif name.startswith("atomic change"):
                    # strip Markdown list markers
                    prompt.atomic_change.extend([re.sub(r"^[-*]\s*", "", c) for c in content])
                elif name.startswith("testing instructions"):
                    prompt.testing_instructions.extend(content)
                elif name.startswith("expected result"):
                    prompt.expected_result.extend([re.sub(r"^[-*]\s*", "", c) for c in content])

            while j < len(lines):
                l2 = lines[j].rstrip("\n")
                if PROMPT_RE.match(l2) or INC_RE.match(l2):
                    flush_section(section)
                    break
                sec_m = SECTION_RE.match(l2)
                if sec_m:
                    # new section header
                    flush_section(section)
                    section = sec_m.group("name")
                    buf = []
                else:
                    buf.append(l2)
                j += 1

            # flush at end of block
            flush_section(section)
            prompts.append(prompt)
            i = j
            continue

        i += 1

    return prompts


def run(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def ensure_gh() -> None:
    if run(["gh", "--version"]).returncode != 0:
        print("GitHub CLI 'gh' is required. Install: https://cli.github.com/", file=sys.stderr)
        sys.exit(1)


def create_issue(repo: str, title: str, body: str, labels: List[str], dry_run: bool) -> Optional[str]:
    if dry_run:
        print(f"[DRY-RUN] Would create issue in {repo}: {title}")
        return None
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md") as tf:
        tf.write(body)
        tf.flush()
        cmd = [
            "gh", "issue", "create",
            "--repo", repo,
            "--title", title,
            "--body-file", tf.name,
        ]
        for lab in labels:
            cmd.extend(["--label", lab])
        proc = run(cmd)
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        sys.exit(proc.returncode)
    url = proc.stdout.strip()
    print(f"Created: {url}")
    return url


def add_to_project(owner: str, project_number: int, issue_url: str, dry_run: bool) -> None:
    if dry_run:
        print(f"[DRY-RUN] Would add to project {owner}/{project_number}: {issue_url}")
        return
    cmd = [
        "gh", "project", "item-add",
        "--owner", owner,
        "--number", str(project_number),
        "--url", issue_url,
    ]
    proc = run(cmd)
    if proc.returncode != 0:
        print("Failed to add issue to project. Ensure you have access and gh is recent.", file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        sys.exit(proc.returncode)


def main():
    ap = argparse.ArgumentParser(description="Seed GitHub issues from a TODO file and add to a user project")
    ap.add_argument("--todo", default="docs/TODO", help="Path to TODO file (default: docs/TODO)")
    ap.add_argument("--repo", required=True, help="Target repo in OWNER/REPO format")
    ap.add_argument("--project-owner", required=True, help="User or org that owns the project (e.g., nehakayiti)")
    ap.add_argument("--project-number", type=int, required=True, help="Project number (e.g., 1)")
    ap.add_argument("--only-increment", type=int, help="Only create issues for a specific increment number")
    ap.add_argument("--area", choices=["backend","frontend","db","devops","ui"], help="Area label to apply to all created issues")
    ap.add_argument("--priority", choices=["priority:P0","priority:P1","priority:P2","priority:P3"], default="priority:P2")
    ap.add_argument("--apply", action="store_true", help="Actually create issues (default is dry-run)")
    args = ap.parse_args()

    ensure_gh()
    prompts = parse_todo(args.todo, only_increment=args.only_increment)
    if not prompts:
        print("No prompts found. Check your TODO path and format.", file=sys.stderr)
        sys.exit(1)

    for p in prompts:
        labels = ["type:feature", f"increment:{p.increment_num}", args.priority]
        if args.area:
            labels.append(f"area:{args.area}")
        body = p.to_issue_body()
        issue_url = create_issue(args.repo, p.issue_title, body, labels, dry_run=(not args.apply))
        if issue_url:
            add_to_project(args.project_owner, args.project_number, issue_url, dry_run=False)

    print("Done.")


if __name__ == "__main__":
    main()

