# Contributing

Thanks for considering a contribution.

## Useful first contributions

- Add scoring signals for specific ecosystems.
- Improve the GitHub Action workflow.
- Add output formats for issue templates or release blockers.
- Add tests for edge cases in `gh issue list` JSON.
- Improve documentation for maintainer/Codex workflows.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e . pytest
python -m pytest
```

## Pull request expectations

- Keep the default CLI zero-dependency unless there is a strong reason.
- Include tests for scoring or parsing changes.
- Avoid adding automation that posts comments, closes issues, or changes labels without explicit maintainer approval.
