# Program Internal Reviews

Each autonomous work package must create one markdown file and one JSON file in this directory.

The review route is `codex_internal_review`.

Each review must record:

- major stage
- work package
- commit
- changed files
- reviewer_mode
- Security Reviewer
- Domain / Quant Reviewer
- Integration Reviewer
- Test / Reproducibility Reviewer
- Public Repo Hygiene Reviewer
- risk_agent review status when trade tickets are created or changed
- findings
- fixes applied
- tests
- pass/fail
- requires user attention
- promote to next work package

Use `reviewer_mode=subagents` when reviewer subagents ran. Use `reviewer_mode=simulated_separate_passes` when subagents were unavailable and Codex performed separate reviewer passes.

Final trading is manually decided by the user.
