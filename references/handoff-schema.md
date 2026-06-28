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

## Handoff Quality Gate

### Needs User Confirmation

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

## Omitted Or Compressed Context

### Compressed

### Dropped

### User-Confirmed Omissions

## Resume Instructions
```

Section guidance:

- `Objective`: current handoff objective. Preserve the user's explicit objective verbatim when one is provided. If the user did not provide one, generate a concise objective from the conversation and mark `Objective Source` as `generated`.
- `Goal Alignment`: whether the current handoff content still supports `Original Objective`; include any drift and recommended action.
- `Handoff Quality Gate`: whether the handoff captures the necessary state accurately. If any save-scope detail is uncertain, list it under `Needs User Confirmation` and ask before writing the final handoff.
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
- `Omitted Or Compressed Context`: what was intentionally summarized or omitted, including anything the user explicitly confirmed could be omitted or compressed.
- `Resume Instructions`: the minimal verification and action sequence for the next AI coding-agent conversation.

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
  "conversation_language": "auto",
  "goal_alignment": "Current state still supports the original objective.",
  "quality_gate": "No unresolved save-scope uncertainty remains.",
  "confirmation_needed": [],
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
  },
  "omitted_or_compressed_context": {
    "compressed": ["Long discussion summarized into the final decision"],
    "dropped": ["Setup noise with no continuing effect"],
    "user_confirmed_omissions": ["User agreed to omit obsolete release discussion"]
  }
}
```

## Quality Bar

A useful handoff lets a new conversation answer these questions within one minute:

- What is the user trying to finish?
- Did the user state the objective directly, or did the agent generate it?
- Is the current state still aligned with the original objective?
- What has already been done?
- What files, commands, and facts are trustworthy?
- What should be read immediately, deferred, or avoided?
- What must not be changed or assumed?
- What, if anything, did the user confirm can be omitted or compressed?
- What information was intentionally compressed away?
- What should the agent do next?

Avoid these failure modes:

- Mixing guesses into verified facts.
- Storing a long transcript instead of task state.
- Omitting exact file paths.
- Forcing the next conversation to re-scan the whole project.
- Saying tests passed without command evidence.
- Omitting user constraints that affect autonomy, permissions, or project boundaries.
- Dropping or heavily compressing possibly important details without asking the user first.
- Failing to distinguish a user-specified objective from a generated or inferred objective.
- Generating the new-conversation resume prompt in a different language from the current conversation when the language is clear.
- Overwriting the original objective after resume without explicit user confirmation.
- Saving drifted work into the same handoff when a new handoff would be clearer.
