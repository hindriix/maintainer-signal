from __future__ import annotations

import json
import subprocess
from pathlib import Path

from maintainer_signal.core import build_signal, render_agent_failure_review_template, render_markdown, score_issue


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
    (repo / "app.py").write_text("print('hello')\n")
    subprocess.run(["git", "add", "app.py"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True, capture_output=True)
    (repo / "app.py").write_text("print('hello again')\n")
    subprocess.run(["git", "add", "app.py"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "touch app"], cwd=repo, check=True, capture_output=True)
    return repo


def test_score_issue_prioritizes_security_and_staleness() -> None:
    score = score_issue(
        "Security regression leaks token",
        ["bug"],
        age_days=120,
        idle_days=90,
        comments=12,
    )
    assert score >= 12


def test_build_signal_from_offline_issue_json(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    issues = tmp_path / "issues.json"
    issues.write_text(json.dumps([
        {
            "number": 1,
            "title": "Regression: crash on login",
            "url": "https://github.com/acme/repo/issues/1",
            "labels": [{"name": "bug"}],
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
            "comments": 11,
        }
    ]))
    signal = build_signal(repo, issues_json=issues)
    assert signal.git.commits_90d == 2
    assert signal.git.contributors_90d == 1
    assert signal.issues[0].number == 1
    assert signal.issues[0].risk_score >= 7
    assert "Escalate" in signal.issues[0].suggested_action


def test_render_markdown_has_action_sections(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    signal = build_signal(repo, issues_json=tmp_path / "missing.json") if False else build_signal(repo, issues_json=None)
    markdown = render_markdown(signal)
    assert "# Maintainer Signal Report" in markdown
    assert "## 4. Next maintainer actions" in markdown
    assert "How to use with Codex" in markdown
    assert "Agent / CI failure review checklist" in markdown


def test_agent_failure_template_focuses_on_github_artifacts() -> None:
    template = render_agent_failure_review_template("/tmp/example-repo")
    assert "Pull request description" in template
    assert "failed GitHub Actions logs" in template
    assert "Root-cause category" in template
    assert "Reasoning error" in template
    assert "Tool misuse" in template
    assert "Context issue" in template
