# Handoff Schema

Use this reference when creating, validating, or repairing a handoff.

## Markdown Sections

`latest.md` should contain these sections in this order:

```markdown
# <Task Title>

- Task ID:
- Updated:
- Workspace:
- Status:
- Objective Source:
- Original Objective:

## Objective

## Goal Alignment

## Current State

## Completed

## In Progress

## Next Steps

## Files And Artifacts

## Context Loading Plan

### Must Read

### Read Only If Needed

### Do Not Reload Unless Mismatch

## Commands And Results

## Verified Facts

## Assumptions

## Risks And Blockers

## Open Questions

## User Constraints

## Compression Intent

### Preserve

### Drop

### Revalidate

## Resume Instructions
```

Section guidance:

- `Objective`: current handoff objective. Preserve the user's explicit objective verbatim when one is provided. If the user did not provide one, generate a concise objective from the conversation and mark `Objective Source` as `generated`.
- `Goal Alignment`: whether the current handoff content still supports `Original Objective`; include any drift and recommended action.
- `Current State`: short operational summary of where the task stands now.
- `Completed`: work that is actually done.
- `In Progress`: partially completed work and exact stopping point.
- `Next Steps`: ordered, executable steps for the next conversation.
- `Files And Artifacts`: absolute or workspace-relative paths and why they matter.
- `Context Loading Plan`: what the next conversation should read immediately, what it should defer, and what broad areas should not be reloaded unless verification fails.
- `Commands And Results`: commands run, important output, failures, and test status.
- `Verified Facts`: facts backed by files, command output, user statements, or tool results.
- `Assumptions`: plausible but unverified beliefs.
- `Risks And Blockers`: approvals, missing credentials, sandbox limits, failing tests, unresolved design risks.
- `Open Questions`: questions that need user input or further inspection.
- `User Constraints`: explicit user instructions, boundaries, preferences, or prohibited actions.
- `Compression Intent`: what to preserve, what to intentionally drop, and what to revalidate because it can drift.
- `Resume Instructions`: the minimal verification and action sequence for the next Codex conversation.

## JSON Metadata

`handoff.json` should be an indexable summary, not a full transcript.

```json
{
  "task_id": "short-stable-id",
  "title": "Human readable task title",
  "workspace": "D:/Workspace/example",
  "status": "in_progress",
  "updated": "2026-06-16T12:34:56+08:00",
  "objective": "One sentence final objective",
  "objective_source": "user_specified",
  "original_objective": "Stable objective from the first handoff in this task chain",
  "goal_alignment": "Current state still supports the original objective.",
  "next_steps": ["First executable step"],
  "files": ["relative/or/absolute/path"],
  "context_loading_plan": {
    "must_read": ["Required path or artifact"],
    "read_only_if_needed": ["Deferred path or artifact"],
    "do_not_reload_unless_mismatch": ["Broad path or topic to avoid reloading"]
  },
  "commands": ["command and result summary"],
  "verified_facts": ["Evidence-backed fact"],
  "assumptions": ["Unverified assumption"],
  "risks": ["Known risk or blocker"],
  "user_constraints": ["Explicit user constraint"],
  "compression_intent": {
    "preserve": ["State to carry forward"],
    "drop": ["Transcript detail or irrelevant exploration to discard"],
    "revalidate": ["Volatile fact to check cheaply on resume"]
  }
}
```

## Quality Bar

A useful handoff lets a new conversation answer these questions within one minute:

- What is the user trying to finish?
- Did the user state the objective directly, or did Codex generate it?
- Is the current state still aligned with the original objective?
- What has already been done?
- What files, commands, and facts are trustworthy?
- What should be read immediately, deferred, or avoided?
- What must not be changed or assumed?
- What information was intentionally compressed away?
- What should Codex do next?

Avoid these failure modes:

- Mixing guesses into verified facts.
- Storing a long transcript instead of task state.
- Omitting exact file paths.
- Forcing the next conversation to re-scan the whole project.
- Saying tests passed without command evidence.
- Omitting user constraints that affect autonomy, permissions, or project boundaries.
- Failing to distinguish a user-specified objective from a generated or inferred objective.
- Overwriting the original objective after resume without explicit user confirmation.
- Saving drifted work into the same handoff when a new handoff would be clearer.
