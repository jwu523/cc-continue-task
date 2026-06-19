## Summary

Describe the change.

## Checklist

- [ ] I kept the change focused.
- [ ] I updated README/docs for user-facing behavior changes.
- [ ] I added or updated tests for script behavior changes.
- [ ] I kept examples fictional and sanitized.
- [ ] I did not commit generated `.codex/handoffs/` data.

## Local Checks

```powershell
python -m py_compile scripts/create_handoff.py scripts/list_handoffs.py scripts/make_resume_prompt.py scripts/validate_handoff.py scripts/sanitize_handoff.py
python -m unittest discover -s tests
python scripts/sanitize_handoff.py .
```

Paste relevant sanitized output or explain why a check was not run.
