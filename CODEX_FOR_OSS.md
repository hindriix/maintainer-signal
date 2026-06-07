# Codex for OSS workflow

Maintainer Signal is built for maintainers who want Codex help without turning AI into an unsupervised maintainer.

## Intended workflow

1. Run Maintainer Signal weekly in GitHub Actions or locally.
2. Review the generated `MAINTAINER_SIGNAL.md` report.
3. Give the report to Codex as context.
4. Ask Codex for narrow maintainer tasks:
   - draft replies for high-risk open issues,
   - generate reproduction checklists,
   - identify release blockers,
   - summarize likely security/regression concerns,
   - propose labels and ownership paths,
   - draft contributor-friendly small issues.
5. Maintainers approve, edit, or reject all suggested actions.

## Why this helps open source

Many public projects fail quietly before they fail technically. The signals are visible but scattered: stale issues, overloaded maintainers, repeated regression reports, security-shaped language in generic bug threads, and hotspot files that only one person understands.

Maintainer Signal collects those signals into one short report so maintainers can use Codex for the work AI is good at — summarization, draft responses, issue grouping, checklist creation — while keeping human judgment on prioritization, security handling, and merges.

## Good Codex prompts

```text
You are helping maintain this public OSS project. Use the Maintainer Signal report below. Draft replies for the top 5 issues. Each reply should ask only one blocking question, avoid overpromising, and include a close/owner/security path.
```

```text
Turn this Maintainer Signal report into a release-blocker checklist. Separate confirmed blockers from needs-reproduction items. Do not mark anything resolved without evidence.
```

```text
Create 3 contributor-friendly issues from the low-risk maintenance opportunities in this report. Each should have context, scope, files to inspect, and a definition of done.
```

## Guardrails

- Do not auto-post Codex replies without maintainer review.
- Do not route security issues through public comments if private disclosure is appropriate.
- Do not let stale automation close high-risk issues solely because they are old.
- Do not treat the risk score as truth; it is a prioritization hint.
