from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

RISK_WORDS = {
    "security": 5,
    "vulnerability": 5,
    "cve": 5,
    "auth": 3,
    "token": 3,
    "secret": 4,
    "crash": 3,
    "panic": 3,
    "data loss": 5,
    "regression": 3,
    "broken": 2,
    "urgent": 3,
    "production": 2,
}

@dataclass
class GitStats:
    commits_90d: int
    contributors_90d: int
    top_contributor_share: float
    active_files_90d: int
    hotspot_files: list[tuple[str, int]]

@dataclass
class IssueSignal:
    number: int
    title: str
    url: str | None
    labels: list[str]
    age_days: int
    idle_days: int
    comments: int
    risk_score: int
    suggested_action: str

@dataclass
class RepoSignal:
    repo_path: str
    generated_at: str
    git: GitStats
    issues: list[IssueSignal]
    overall_risks: list[str]
    next_actions: list[str]


def run(cmd: list[str], cwd: Path, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, check=check)


def git_stats(repo: Path) -> GitStats:
    since = "90 days ago"
    log = run(["git", "log", f"--since={since}", "--format=%ae"], repo)
    emails = [x.strip() for x in log.stdout.splitlines() if x.strip()]
    commits = len(emails)
    contributors = len(set(emails))
    top_share = 0.0
    if emails:
        top_share = max(emails.count(e) for e in set(emails)) / len(emails)

    names = run(["git", "log", f"--since={since}", "--name-only", "--pretty=format:"], repo)
    counts: dict[str, int] = {}
    for line in names.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("."):
            continue
        counts[line] = counts.get(line, 0) + 1
    hotspots = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:10]

    return GitStats(
        commits_90d=commits,
        contributors_90d=contributors,
        top_contributor_share=round(top_share, 2),
        active_files_90d=len(counts),
        hotspot_files=hotspots,
    )


def _parse_dt(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def score_issue(title: str, labels: Iterable[str], age_days: int, idle_days: int, comments: int) -> int:
    text = " ".join([title, *labels]).lower()
    score = 0
    for word, weight in RISK_WORDS.items():
        if word in text:
            score += weight
    if age_days >= 30:
        score += 1
    if age_days >= 90:
        score += 2
    if idle_days >= 14:
        score += 1
    if idle_days >= 60:
        score += 2
    if comments >= 10:
        score += 2
    return score


def suggest_action(issue: IssueSignal | dict) -> str:
    labels = [x.lower() for x in (issue.labels if isinstance(issue, IssueSignal) else issue["labels"])]
    title = (issue.title if isinstance(issue, IssueSignal) else issue["title"]).lower()
    risk = issue.risk_score if isinstance(issue, IssueSignal) else issue["risk_score"]
    idle = issue.idle_days if isinstance(issue, IssueSignal) else issue["idle_days"]
    if risk >= 7:
        return "Escalate: likely maintainer/security/regression risk; assign owner and request reproduction."
    if "bug" in labels or "regression" in title:
        return "Triage as bug: confirm reproduction, version, expected behavior, and impacted users."
    if idle >= 30:
        return "Revive or close: ask for current reproduction, mark stale only after maintainer review."
    if "enhancement" in labels or "feature" in title:
        return "Route to roadmap: clarify scope and invite a focused PR if maintainer-aligned."
    return "Triage: label, ask one blocking question, and decide owner/close path."


def load_issues_from_json(path: Path) -> list[IssueSignal]:
    raw = json.loads(path.read_text())
    return [_issue_from_gh(item) for item in raw]


def fetch_issues_with_gh(repo: Path, limit: int) -> list[IssueSignal]:
    if not shutil.which("gh"):
        return []
    cmd = [
        "gh", "issue", "list", "--state", "open", "--limit", str(limit),
        "--json", "number,title,url,labels,createdAt,updatedAt,comments",
    ]
    result = run(cmd, repo)
    if result.returncode != 0 or not result.stdout.strip():
        return []
    return [_issue_from_gh(item) for item in json.loads(result.stdout)]


def _issue_from_gh(item: dict) -> IssueSignal:
    now = datetime.now(timezone.utc)
    created = _parse_dt(item.get("createdAt"))
    updated = _parse_dt(item.get("updatedAt"))
    labels = [l.get("name", str(l)) if isinstance(l, dict) else str(l) for l in item.get("labels", [])]
    age = max(0, (now - created).days)
    idle = max(0, (now - updated).days)
    comments = int(item.get("comments") or 0)
    title = item.get("title", "")
    risk = score_issue(title, labels, age, idle, comments)
    issue = IssueSignal(
        number=int(item.get("number", 0)),
        title=title,
        url=item.get("url"),
        labels=labels,
        age_days=age,
        idle_days=idle,
        comments=comments,
        risk_score=risk,
        suggested_action="",
    )
    issue.suggested_action = suggest_action(issue)
    return issue


def build_signal(repo: Path, issue_limit: int = 50, issues_json: Optional[Path] = None) -> RepoSignal:
    repo = repo.resolve()
    stats = git_stats(repo)
    if issues_json:
        issues = load_issues_from_json(issues_json)
    else:
        issues = fetch_issues_with_gh(repo, issue_limit)
    issues = sorted(issues, key=lambda i: (-i.risk_score, -i.idle_days, -i.comments, i.number))

    risks: list[str] = []
    if stats.contributors_90d <= 1 and stats.commits_90d > 0:
        risks.append("Bus-factor risk: one active contributor owns nearly all recent work.")
    if stats.top_contributor_share >= 0.8 and stats.commits_90d >= 5:
        risks.append("Maintainer concentration: top contributor authored >=80% of recent commits.")
    stale_high = [i for i in issues if i.risk_score >= 5 and i.idle_days >= 14]
    if stale_high:
        risks.append(f"{len(stale_high)} high-risk open issues have been idle for at least 14 days.")
    if not issues:
        risks.append("No GitHub issue data available; run inside a GitHub repo with gh auth or pass --issues-json.")

    actions = [
        "Review the top 5 risk-scored issues and assign each: close, owner, reproduction request, or security path.",
        "Turn this report into a weekly GitHub Action artifact so maintainers see drift before backlog grows.",
    ]
    if stats.hotspot_files:
        actions.append(f"Add ownership/review notes for hotspot file: {stats.hotspot_files[0][0]}.")
    if stats.contributors_90d <= 2:
        actions.append("Create 2-3 contributor-ready issues from low-risk maintenance work to reduce maintainer bottleneck.")

    return RepoSignal(
        repo_path=str(repo),
        generated_at=datetime.now(timezone.utc).isoformat(),
        git=stats,
        issues=issues,
        overall_risks=risks,
        next_actions=actions,
    )


def render_markdown(signal: RepoSignal) -> str:
    lines = [
        "# Maintainer Signal Report",
        "",
        f"Generated: `{signal.generated_at}`",
        f"Repository: `{signal.repo_path}`",
        "",
        "## 1. Git activity",
        "",
        f"- Commits in last 90 days: **{signal.git.commits_90d}**",
        f"- Contributors in last 90 days: **{signal.git.contributors_90d}**",
        f"- Top contributor share: **{signal.git.top_contributor_share:.0%}**",
        f"- Files touched in last 90 days: **{signal.git.active_files_90d}**",
        "",
        "### Hotspot files",
        "",
    ]
    if signal.git.hotspot_files:
        for path, count in signal.git.hotspot_files:
            lines.append(f"- `{path}` — {count} recent touches")
    else:
        lines.append("- No recent hotspot files found.")

    lines += ["", "## 2. Overall risks", ""]
    for risk in signal.overall_risks:
        lines.append(f"- {risk}")

    lines += ["", "## 3. Highest-signal open issues", ""]
    if signal.issues:
        lines.append("| Risk | Issue | Age | Idle | Comments | Labels | Suggested action |")
        lines.append("|---:|---|---:|---:|---:|---|---|")
        for issue in signal.issues[:15]:
            title = issue.title.replace("|", "\\|")
            target = f"[#{issue.number} {title}]({issue.url})" if issue.url else f"#{issue.number} {title}"
            labels = ", ".join(issue.labels).replace("|", "\\|") or "—"
            action = issue.suggested_action.replace("|", "\\|")
            lines.append(f"| {issue.risk_score} | {target} | {issue.age_days}d | {issue.idle_days}d | {issue.comments} | {labels} | {action} |")
    else:
        lines.append("No issue data available.")

    lines += ["", "## 4. Next maintainer actions", ""]
    for action in signal.next_actions:
        lines.append(f"- {action}")

    lines += [
        "",
        "## 5. How to use with Codex",
        "",
        "Paste this report into Codex and ask it to draft issue replies, reproduction checklists, release blockers, or PR review plans. Keep maintainer approval in the loop for any security or high-risk change.",
    ]
    return "\n".join(lines) + "\n"


def to_json(signal: RepoSignal) -> str:
    return json.dumps(asdict(signal), indent=2)
