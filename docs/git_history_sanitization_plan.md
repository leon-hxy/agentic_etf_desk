# Git History Sanitization Plan

Current `HEAD` sanitization and git history sanitization are different tasks.

## Current Stage

Stage 2A.5 only sanitizes current `HEAD`. It does not rewrite history, delete remote refs, recreate the repository, rotate secrets, or change GitHub settings.

## If History Metadata Needs Cleanup

If the user decides that old local paths, version details, process identifiers, or other non-secret metadata should be removed from history, choose one of these paths:

1. Use `git filter-repo` to rewrite history after a reviewed backup and coordination plan.
2. Create a new clean public repository and archive the old one.
3. Keep the current history and accept that prior non-secret metadata remains visible.

## If A Real Secret Was Committed

Rotate the secret immediately. History rewriting may reduce future exposure, but it does not invalidate a leaked secret. Rotation is required for real secrets, tokens, auth values, provider keys, Feishu App Secret values, and broker credentials.

## Approval Boundary

Do not execute history rewriting automatically. Do not delete or recreate the GitHub repository automatically. Do not rotate or modify secrets automatically. Each action requires explicit user approval and a separate plan.
