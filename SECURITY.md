# Security Policy

## Supported Versions

Security fixes are applied to the latest public release and the `main` branch.

## Reporting A Security Issue

If you find a security issue, please report it privately instead of opening a public issue with sensitive details.

If the issue involves leaked data, include only the minimum needed to explain the problem. Redact secrets, tokens, private paths, and internal project details.

## Sensitive Data Guidance

`cc-continue-task` creates handoff files that may include local paths, command output, issue context, and operational notes. Treat generated handoffs as private by default.

Do not publish handoffs that contain:

- credentials, tokens, API keys, private keys, or session material
- private project names, customer details, or internal issue data
- local user paths
- private network addresses
- confidential command output or logs

Before sharing a handoff, run:

```powershell
python scripts/sanitize_handoff.py <handoff-path>
```

The sanitizer is a first-pass scanner, not a substitute for review. Always inspect generated handoffs manually before sharing or committing them.
