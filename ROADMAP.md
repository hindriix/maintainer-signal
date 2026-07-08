# Roadmap

Maintainer Signal is early. The goal is to stay small, local-first, and useful for maintainers who want AI-assisted workflows without giving up review, traceability, or control.

## v0.1 — Maintainer health report

- [x] Git activity summary
- [x] Contributor concentration / bus-factor signal
- [x] Hotspot file detection
- [x] Open issue risk scoring from GitHub issue data
- [x] Markdown and JSON output
- [x] GitHub Actions example

## v0.2 — Agent failure review

- [x] Built-in agent / CI failure review checklist
- [x] Standalone `--format agent-template` output
- [x] Documentation for reviewing GitHub artifacts after failed agent runs
- [ ] Parse recent failed GitHub Actions runs through `gh run list`
- [ ] Link failed workflow runs to likely issue/PR context
- [ ] Add a structured failure-review JSON schema

## v0.3 — Better maintainer triage

- [ ] Configurable risk words and weights
- [ ] Label-aware scoring profiles
- [ ] Separate security-shaped issues from public triage suggestions
- [ ] Contributor-friendly issue suggestion mode
- [ ] Release-blocker summary mode

## v0.4 — Packaging and examples

- [ ] Publish package to PyPI
- [ ] Add more example reports from public repositories
- [ ] Add screenshots / terminal demo GIF
- [ ] Add weekly report workflow with artifact upload and optional issue creation

## Design constraints

- Zero required runtime dependencies
- Human maintainer approval stays in the loop
- No auto-posting, auto-closing, or unsupervised maintainer actions
- GitHub artifacts and source data should remain auditable
