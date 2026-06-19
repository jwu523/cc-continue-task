# Contributing

Thanks for helping improve `cc-continue-task`.

This project is small by design. Changes should keep the skill easy to install, easy to audit, and safe to use with private task context.

## Development Setup

Use Python 3. No third-party runtime dependencies are required.

Run the local checks before opening a pull request:

```powershell
python -m py_compile scripts/create_handoff.py scripts/list_handoffs.py scripts/make_resume_prompt.py scripts/validate_handoff.py scripts/sanitize_handoff.py
python -m unittest discover -s tests
python scripts/sanitize_handoff.py .
```

## Pull Request Guidelines

- Keep changes focused.
- Update `README.md` and `README_zh.md` when user-facing behavior changes.
- Update `docs/install.md` or `docs/demo.md` when install or workflow behavior changes.
- Update `CHANGELOG.md` for notable changes.
- Add or update tests for script behavior changes.
- Keep examples fictional and sanitized.

## Handoff Safety

Do not commit generated handoffs from real work.

Never include:

- `.codex/handoffs/`
- local cache directories
- real credentials, tokens, API keys, or private keys
- internal project names or issue details unless they are intentionally public
- real local user paths or private network addresses

Use the sanitizer as a first pass:

```powershell
python scripts/sanitize_handoff.py <path>
```

The sanitizer is not a guarantee. Review any handoff or example manually before publishing it.

## Schema Changes

If you change the handoff schema, update these together:

- `references/handoff-schema.md`
- `scripts/create_handoff.py`
- `scripts/validate_handoff.py`
- `examples/*/latest.md`
- `tests/test_scripts.py`
- README documentation

Schema changes should preserve the core contract: a new conversation must be able to resume from the handoff without reading the full prior conversation.
