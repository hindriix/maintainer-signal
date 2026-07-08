# Maintainer Signal

Maintainer Signal is a zero-dependency CLI that generates a practical maintainer health report for an open-source GitHub repository.

It is built for maintainers in the AI-agent era: people who want help from Codex/Claude-style tools for triage, summaries, and review planning, but still need GitHub evidence, human approval, and traceable decisions.

It looks at two signals maintainers usually feel before they can prove:

1. Git activity: recent contributor concentration, hotspot files, and bus-factor pressure.
2. Open issues: stale/high-risk issues, security/regression language, comment-heavy threads, and suggested next actions.
3. Agent-assisted maintenance failures: a reusable checklist for comparing task intent against PR diffs, workflow logs, commits, checks, and artifacts.

The output is a Markdown report that can be reviewed by humans or handed to Codex to draft replies, reproduction checklists, PR review plans, release blockers, or weekly maintainer summaries.

## Why this exists

Open-source maintainers do not just need another dashboard. They need a small, boring tool that turns public repo state into a weekly action list:

- Which open issues are most likely to be security/regression/maintainer-risk items?
- Which files are turning into maintenance hotspots?
- Is one person carrying most of the recent work?
- What should we triage first this week?
- What context should we give Codex before asking it to help?

Maintainer Signal is designed for critical public projects where maintainers want help without handing off judgment or write access to an AI agent.

## Install from source

```bash
git clone https://github.com/hindriix/maintainer-signal.git
cd maintainer-signal
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Quick start

From any local GitHub repository:

```bash
maintainer-signal . --output MAINTAINER_SIGNAL.md
```

If you have the GitHub CLI authenticated, Maintainer Signal will fetch open issues:

```bash
gh auth login
maintainer-signal /path/to/repo --issue-limit 100 -o MAINTAINER_SIGNAL.md
```

Offline/demo mode:

```bash
maintainer-signal . --issues-json examples/issues.json -o MAINTAINER_SIGNAL.md
```

JSON output:

```bash
maintainer-signal . --format json -o maintainer-signal.json
```

Agent failure review template:

```bash
maintainer-signal . --format agent-template -o AGENT_FAILURE_REVIEW.md
```

Use this when an AI agent, workflow, or maintainer automation fails and you need a structured way to review GitHub artifacts before changing prompts, instructions, or tooling. See `docs/agent-failure-review.md` for the full workflow.

## Example output

```markdown
# Maintainer Signal Report

## 1. Git activity
- Commits in last 90 days: 42
- Contributors in last 90 days: 3
- Top contributor share: 81%

## 3. Highest-signal open issues
| Risk | Issue | Age | Idle | Comments | Labels | Suggested action |
|---:|---|---:|---:|---:|---|---|
| 12 | #42 Regression: auth token refresh crashes | 90d | 30d | 14 | bug, regression | Escalate... |
```

## GitHub Action

Copy `examples/github-actions/maintainer-signal.yml` into `.github/workflows/maintainer-signal.yml` in any public repository and schedule it weekly.

The workflow produces a `MAINTAINER_SIGNAL.md` artifact. You can also commit the report, open an issue, or paste the artifact into Codex for maintainer review.

## Suggested Codex workflow

1. Generate the report weekly.
2. Paste the Markdown into Codex.
3. Ask Codex to draft:
   - issue replies for the top 5 risk-scored issues,
   - a release-blocker list,
   - reproduction questions,
   - stale-but-important issue revival notes,
   - a contributor-friendly maintenance plan.
4. Maintainer reviews every action before posting or merging.

See `CODEX_FOR_OSS.md` for the intended open-source maintenance workflow and `docs/agent-failure-review.md` for the GitHub-artifact failure review process.

## Roadmap

See `ROADMAP.md` for planned work around GitHub Actions failure parsing, structured failure-review JSON, configurable risk scoring, release-blocker summaries, and packaging.

## Design principles

- Zero dependencies by default.
- Human-maintainer approval stays in the loop.
- High-signal over high-volume.
- Works locally, in CI, and with `gh`.
- Useful before a repo has budget for heavyweight tooling.

## Development

```bash
python -m pip install -e . pytest
python -m pytest
python -m maintainer_signal.cli . --issues-json examples/issues.json -o /tmp/maintainer-signal.md
```

## License

MIT
