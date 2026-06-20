# Demo Import Bug Follow-Up

- Task ID: demo-import-bug-follow-up
- Updated: 2026-06-19T12:20:00+00:00
- Workspace: <workspace>/demo-importer
- Status: in_progress
- Objective Source: user_specified
- Original Objective: Fix the CSV import crash and add a regression test.
- Git Branch: fix/csv-import

## Objective

Review a proposed export redesign that came up while fixing the CSV import crash.

## Goal Alignment

The current objective has materially drifted from the original objective. The original task was to fix a CSV import crash and add a regression test. Export redesign is a different task. Save a new handoff for the redesign unless the user explicitly replaces the original objective.

## Handoff Quality Gate

Do not silently save export redesign details into the original import-bug handoff. User confirmation is needed before omitting the export discussion or splitting it into a new handoff.

### Needs User Confirmation

- Should the next handoff continue the CSV import bug objective, or should export redesign be saved as a separate handoff?

## Current State

The import crash was investigated, but the conversation moved into export redesign before the regression test was added.

## Completed

- Reproduced the import crash with a malformed CSV row.
- Identified missing validation around required columns.

## In Progress

- Regression test is still missing.
- Export redesign is only exploratory.

## Next Steps

- Ask the user whether to return to the import crash objective or save export redesign as a new handoff.
- If returning to the original objective, add the missing regression test first.

## Files And Artifacts

- `src/importer/csv_import.py`: suspected validation fix location.
- `tests/test_csv_import.py`: missing regression test location.

## Context Loading Plan

### Must Read

- `latest.md`
- `src/importer/csv_import.py`
- `tests/test_csv_import.py`

### Read Only If Needed

- `src/exporter/export_plan.md`

### Do Not Reload Unless Mismatch

- Full exporter implementation.
- Unrelated import formats.

## Commands And Results

- `python -m pytest tests/test_csv_import.py`: not run after the latest changes.

## Verified Facts

- The original objective is about CSV import.
- The current discussion is about export redesign.

## Assumptions

- The user may want to split the export redesign into a separate task.

## Risks And Blockers

- Continuing in the same handoff could overwrite the original objective and lose the import bug context.

## Open Questions

- Should this handoff continue the import fix, or should export redesign get a new handoff?

## User Constraints

- Do not silently overwrite the original objective when drift is detected.

## Compression Intent

### Preserve

- Original objective, drift reason, and recommended split.

### Drop

- Detailed export redesign brainstorming unless a new handoff is created.

### Revalidate

- Whether the import regression test exists.
- User's intended objective for the next step.

## Omitted Or Compressed Context

### Compressed

- Export redesign discussion is summarized only as objective drift until the user confirms it should become a separate task.

### Dropped

- None recorded.

### User-Confirmed Omissions

- None recorded; confirmation is still needed.

## Resume Instructions

- Start by reporting the objective drift.
- Ask whether to return to the import fix or create a new handoff for export redesign.
