# Agent Failure Review Using GitHub Artifacts

Maintainer Signal is built for maintainers who want AI help without losing visibility or control. Use this workflow when a human or AI agent fails to complete a task correctly and you need to evaluate what happened, correct the behavior, and teach the workflow how to improve.

## 1. Start with GitHub artifacts

Do not guess from the final error message alone. Review the evidence GitHub already captured:

- Pull request description, commits, and diff
- Issue requirements and acceptance criteria
- Checks tab and failed GitHub Actions logs
- Workflow run results and uploaded artifacts
- Review comments and maintainer decisions

These artifacts show what the agent changed, what validation ran, and where the task diverged from intent.

## 2. Compare intent with results

Intent usually lives in:

- Issue descriptions
- Acceptance criteria
- Pull request descriptions
- Maintainer comments
- Repository instructions such as `AGENTS.md`, `CLAUDE.md`, or contribution docs

Results live in:

- Commits and file diffs
- Workflow logs and artifacts
- Test failures
- Generated reports, screenshots, or build outputs

Ask:

- Did the agent solve the requested problem?
- Did it satisfy the acceptance criteria?
- Did it change files outside scope?
- Did it validate the result with the right command or workflow?

## 3. Classify the root cause

### Reasoning error

The agent made the wrong decision.

Examples:

- Misread the requirement
- Implemented the wrong logic
- Ignored acceptance criteria
- Invented plausible but unverified behavior

Correction:

- Tighten acceptance criteria
- Add examples and non-examples
- Require explicit verification evidence

### Tool misuse

The agent used commands, workflows, or GitHub operations incorrectly.

Examples:

- Ran tests from the wrong directory
- Used a stale branch
- Skipped dependency setup
- Misconfigured a workflow trigger
- Failed to inspect CI logs before changing code

Correction:

- Add exact commands to repository instructions
- Add preflight checks
- Improve workflow defaults and artifact upload

### Context issue

The agent acted on missing, stale, or conflicting information.

Examples:

- Did not read current PR discussion
- Used old issue state
- Missed prior maintainer decisions
- Had conflicting instructions across docs

Correction:

- Establish a single source of truth
- Update issues or PRs with current decisions
- Remove stale context from instructions

## 4. Improve the operating system

Agent behavior improves through three levers:

1. Prompts and instructions
   - Clarify scope, acceptance criteria, and definition of done.
   - Update repo instructions and contribution docs.

2. Memory and state
   - Put decisions in issues/PRs where future agents will read them.
   - Remove or supersede stale context.

3. Tool configuration
   - Fix `.github/workflows/` triggers, permissions, and required checks.
   - Upload useful artifacts such as test reports, coverage, screenshots, and generated outputs.

## 5. Use a feedback loop

1. Run the agent on a task.
2. Observe the failure in GitHub artifacts.
3. Identify the root cause.
4. Update prompts, state, or tooling.
5. Re-run the workflow.
6. Document the correction in a PR, issue, or commit.

## Maintainer Signal support

Generate the built-in review checklist:

```bash
maintainer-signal . --format agent-template -o AGENT_FAILURE_REVIEW.md
```

Or include the checklist at the bottom of the normal maintainer report:

```bash
maintainer-signal . -o MAINTAINER_SIGNAL.md
```

## Key takeaway

Agent failures are not just errors to fix once. They are signals that the maintainer operating system needs better instructions, fresher state, or stronger validation. GitHub artifacts make those failures observable and teachable.
