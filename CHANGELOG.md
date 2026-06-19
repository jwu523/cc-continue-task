# Changelog

## v0.1.0 - 2026-06-20

Initial public version.

### Added

- Agent-agnostic handoff workflow instructions for saving and resuming long-running task handoffs, packaged as a Codex skill.
- Handoff schema with objective provenance, original-objective preservation, goal alignment, context loading plan, and compression intent.
- Helper scripts:
  - `create_handoff.py`
  - `list_handoffs.py`
  - `validate_handoff.py`
  - `sanitize_handoff.py`
  - `make_resume_prompt.py`
- Automatic resume prompt output after handoff creation.
- Sanitized examples for basic saves, generated objectives, and objective drift.
- Dependency-free unit tests.
- GitHub Actions CI.
- English and Chinese README files.
- Install guide.
