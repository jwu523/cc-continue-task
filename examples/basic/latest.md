# Demo CLI Refactor

- Task ID: demo-cli-refactor
- Updated: 2026-06-19T12:00:00+00:00
- Workspace: <workspace>/demo-cli
- Status: in_progress
- Objective Source: user_specified
- Original Objective: Refactor the demo CLI parser and verify existing commands still work.
- Git Branch: feature/parser-cleanup

## Objective

Refactor the demo CLI parser and verify existing commands still work.

## Goal Alignment

Current work is aligned with the original objective. The parser split is implemented, and the remaining work is verification.

## Current State

The parser has been split into a dedicated module. Command handlers still call the same public entrypoints.

## Completed

- Added `src/demo_cli/parser.py`.
- Updated `src/demo_cli/main.py` to use the new parser module.
- Ran import checks for the changed modules.

## In Progress

- Full CLI command verification has not been run yet.

## Next Steps

- Run the focused CLI test suite.
- Manually verify `demo-cli init`, `demo-cli run`, and `demo-cli status`.
- Update docs if any command help text changed.

## Files And Artifacts

- `src/demo_cli/parser.py`: new parser module.
- `src/demo_cli/main.py`: CLI entrypoint using the parser.
- `tests/test_cli_parser.py`: focused parser coverage.

## Context Loading Plan

### Must Read

- `latest.md`
- `src/demo_cli/parser.py`
- `tests/test_cli_parser.py`

### Read Only If Needed

- `src/demo_cli/main.py`
- `README.md`

### Do Not Reload Unless Mismatch

- Unrelated application modules.
- Historical conversation transcript.

## Commands And Results

- `python -m py_compile src/demo_cli/parser.py src/demo_cli/main.py`: passed.

## Verified Facts

- The new parser module exists.
- The CLI entrypoint imports the new parser module.
- No generated handoff files should be committed.

## Assumptions

- Existing CLI behavior should remain unchanged unless tests show otherwise.

## Risks And Blockers

- Command help text may have changed as a side effect of parser cleanup.

## Open Questions

- Should docs include the new parser module as an extension point?

## User Constraints

- Keep the refactor small and avoid unrelated formatting churn.

## Compression Intent

### Preserve

- Objective, changed files, test status, and remaining verification steps.

### Drop

- Transcript-level discussion about early implementation alternatives.

### Revalidate

- Git status.
- Focused CLI test results.

## Resume Instructions

- Read this handoff first.
- Inspect the three files listed under Must Read.
- Run the focused CLI tests before making further changes.
