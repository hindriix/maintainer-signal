from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import build_signal, render_agent_failure_review_template, render_markdown, to_json


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="maintainer-signal",
        description="Generate a maintainer health report for an open-source GitHub repository.",
    )
    parser.add_argument("repo", nargs="?", default=".", help="Path to a local git repository. Default: current directory")
    parser.add_argument("--issues-json", type=Path, help="Path to gh issue JSON export for offline or test runs")
    parser.add_argument("--issue-limit", type=int, default=50, help="Max open issues to fetch with gh. Default: 50")
    parser.add_argument("--format", choices=["markdown", "json", "agent-template"], default="markdown", help="Output format")
    parser.add_argument("--output", "-o", type=Path, help="Write report to this file instead of stdout")
    parser.add_argument("--version", action="version", version=f"maintainer-signal {__version__}")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo = Path(args.repo)
    if not (repo / ".git").exists():
        print(f"error: {repo} does not look like a git repository", file=sys.stderr)
        return 2
    if args.format == "agent-template":
        content = render_agent_failure_review_template(str(repo.resolve()))
    else:
        signal = build_signal(repo, issue_limit=args.issue_limit, issues_json=args.issues_json)
        content = to_json(signal) if args.format == "json" else render_markdown(signal)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content)
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
