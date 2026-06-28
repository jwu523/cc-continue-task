---
name: cc-continue-task
description: Save and resume long-running AI coding-agent tasks across conversations while preserving the task objective, controlling token use, reducing hallucination risk, and avoiding unnecessary project reloads. Use when the user asks to checkpoint, hand off, inherit, continue, resume, preserve, or compress task context for a new conversation, especially for large coding, debugging, research, or operational tasks in Codex, Claude Code, OpenCode, or similar agent tools that would otherwise consume too much context, drift from the original goal, or risk stale reasoning.
---

# CC Continue Task

Use this skill to create durable task handoffs and resume unfinished work from them. A handoff is evidence-backed task state written to disk so a future AI coding-agent conversation can continue without reloading the full prior conversation.

This repository is packaged as a Codex skill, but the handoff format and helper scripts are agent-agnostic. They can be used with Codex, Claude Code, OpenCode, or any comparable coding agent that can read and write local files.

## Design Goals

Optimize every handoff for these outcomes:

- Context budget control: preserve the minimum task state needed to continue, not the full conversation.
- Evidence-backed continuity: separate verified facts, assumptions, and open questions so future work does not rely on stale or invented state.
- Objective continuity: keep resumed and later checkpointed work aligned to the original task objective unless the user explicitly changes direction.
- Objective relevance noise control: omit or summarize conversation details that are unrelated or only weakly related to the active objective.
- Project reload avoidance: name the exact files and commands needed next, and explicitly mark broad project areas that should not be reloaded unless a mismatch appears.
- Resume actionability: make the next conversation able to act from the handoff within one minute, after only cheap verification.

## Core Rule

Separate verified facts from assumptions. Do not present inferred, stale, or unverified state as current truth. On resume, verify cheap drift-prone facts before acting.

## Save Trigger Rule

Only write or refresh a handoff when the user explicitly asks to save, checkpoint, hand off, preserve state, or prepare a new conversation. Do not update or refresh a handoff just because work progressed, a milestone completed, tests changed, a blocker changed, the user gave a new constraint, or a normal response is being sent.

After resuming from a handoff, use it as read-only task state while continuing the work. Mention that a new save is available only when it is useful; do not run `scripts/create_handoff.py`, overwrite `latest.md`, or create checkpoint files unless the user asks for a save.

## Storage

Default to the current workspace:

```text
.codex/handoffs/<task-id>/
  latest.md
  handoff.json
  checkpoints/
```

Use a different location only when the user asks.

## Handoff Quality Gate

Before writing a handoff, decide whether the save can be accurate without user confirmation.

Run the Objective Relevance Noise Filter before choosing what to preserve:

- Keep details that directly affect the objective, next action, code behavior, user constraints, permissions, validation, or risk.
- Compress weakly related details into a short note only when they explain why the current direction was chosen.
- Drop unrelated side discussions, repeated status chatter, transient tool noise, abandoned branches, and implementation trivia that will not change the next conversation's choices.
- If relevance is uncertain and the detail could affect future decisions, ask before dropping it and record the decision in `Omitted Or Compressed Context`.

Always preserve:

- User-stated objective and `Original Objective`.
- Current state, completed work, in-progress work, and next steps.
- Files, artifacts, commands, results, and evidence that affect continuation.
- User constraints, blockers, risks, assumptions, open questions, and decisions that affect future work.
- Context loading boundaries: what to read, defer, and avoid reloading.

Compress when the detail is useful but too large:

- Superseded explorations.
- Failed attempts that explain current direction.
- Tool setup or permission debugging that only matters through its final outcome.
- Background discussion that affected a decision but not the next action.

Drop only when the detail is clearly irrelevant:

- Small talk, repeated explanations, and duplicated outputs.
- Temporary errors with no lasting effect.
- Branches explicitly abandoned by the user or made irrelevant by later decisions.

Ask the user before saving when any of these are true:

- The objective, current state, next step, or stopping point is ambiguous.
- Multiple active subgoals exist and it is unclear which should control the next conversation.
- The conversation is long enough that important details may be lost during compression.
- A detail may affect code, business logic, user constraints, permissions, or future decisions, but would be expensive to preserve fully.
- The user said or implied that details should not be lost.
- You are about to drop or heavily compress material that might still matter.

When confirmation is needed, present a concrete compression plan instead of asking a vague question:

```text
I can save the handoff, but these details need confirmation before I omit or compress them:

- Keep: A, B, C.
- Compress: D into one sentence because it only explains why approach X was rejected.
- Drop: E and F because they were temporary setup noise.
- Unclear: G may affect the next implementation step.

Please confirm whether G should be preserved, compressed, or omitted.
```

Record the result in `Handoff Quality Gate` and `Omitted Or Compressed Context`.

## Create A Handoff

When the user asks to save, checkpoint, hand off, or prepare for a new conversation:

1. Use the user's explicitly stated objective when provided. Preserve it verbatim unless it contains obvious typos that would change meaning.
2. If the user did not provide an objective, generate a concise objective from the conversation content and mark it as `generated` in the handoff. Do not leave the objective empty.
3. If the conversation began casually and the objective only became clear later, prefer the later explicit objective over earlier exploratory wording.
4. Record `Original Objective`. For a new handoff, this is the same as `Objective`; for a resumed handoff, preserve the original objective from the loaded state.
5. Add `Goal Alignment` explaining whether the saved state still fits the original objective.
6. Run the Handoff Quality Gate. If important save-scope details are uncertain, ask the user to confirm the compression plan before writing the handoff.
7. Inspect local state cheaply: workspace path, `git status --short`, branch, and relevant files already known from the task.
8. Write only evidence-backed state under `Verified Facts`.
9. Put guesses under `Assumptions`; put unknowns under `Open Questions`.
10. Include exact paths, commands, results, blockers, approvals, and user constraints that affect continuation.
11. Add a `Context Loading Plan` with `Must Read`, `Read Only If Needed`, and `Do Not Reload Unless Mismatch`.
12. Add a `Compression Intent` with `Preserve`, `Drop`, and `Revalidate`.
13. Add `Omitted Or Compressed Context` with `Compressed`, `Dropped`, and `User-Confirmed Omissions`.
14. End with concrete `Resume Instructions` that a new conversation can execute directly.
15. Use `scripts/create_handoff.py` when useful to create `latest.md`, `handoff.json`, and checkpoint history.
16. Run `scripts/validate_handoff.py` before reporting success when time allows.
17. After writing the handoff, run `scripts/make_resume_prompt.py` for the saved handoff and include the generated resume prompt in the response. Generate the prompt in the current conversation language when clear; otherwise let the script auto-detect from handoff metadata.
18. Explicitly tell the user the objective that was saved. If the objective was generated, say that it was generated and can be corrected.

When using `scripts/create_handoff.py`, pass `--objective-source user_specified` if the user directly provided the objective. Pass `--objective-source generated` if the agent generated it from the conversation.

When the current conversation language is clear, pass `--conversation-language zh` or `--conversation-language en` so the printed resume prompt matches the user's language. If it is mixed or unclear, omit the flag and use the script's auto-detection.

User-specified objective examples:

```text
Use cc-continue-task to save state. Task objective: finish the MariaDB migration and verify the dashboard still works.
```

```text
Checkpoint this as: build a reusable workflow for continuing long-running AI coding tasks across conversations.
```

Prefer a concise but complete handoff over a transcript-like dump. The goal is continuity, not conversation archival.

## Objective Drift

When saving after resuming from a handoff:

1. Preserve `Original Objective` from the loaded handoff.
2. Compare the current work and any newly supplied objective against `Original Objective`.
3. If the content still supports the original objective, save normally and record the alignment.
4. If the content has drifted materially, tell the user the mismatch and ask whether to adjust the original objective or save a new handoff.
5. If the user manually specifies a new objective that conflicts with `Original Objective`, do not silently overwrite the original objective. Recommend a new handoff unless the user explicitly says the original objective should be replaced.

## Resume A Handoff

When the user asks to continue or inherit a saved task:

1. Find the requested handoff. If no task id is given, use `scripts/list_handoffs.py` and choose the most recent plausible match.
2. Read `latest.md` first. Read `references/handoff-schema.md` only if the structure is unclear or a repair is needed.
3. Verify current workspace, git status, referenced files, and any cheap environment checks listed in `Resume Instructions`.
4. Treat `Objective Source: user_specified` as the controlling objective unless the user overrides it.
5. Treat `Objective Source: generated` or `Objective Source: inferred` as useful but lower confidence; confirm it against the handoff and current user request before making broad changes.
6. Follow `Context Loading Plan`: read `Must Read` first, defer `Read Only If Needed`, and avoid `Do Not Reload Unless Mismatch` unless verification fails.
7. Follow `Compression Intent`: preserve listed facts and decisions, drop transcript-level detail, and revalidate listed volatile items.
8. Report mismatches briefly before making changes.
9. Continue from `Next Steps`, preserving `User Constraints` and avoiding unrelated project reloads.
10. On the next save, preserve `Original Objective`; do not let the new handoff drift into a different task without user confirmation.
11. If the handoff is stale or incomplete, do the minimum new exploration needed and continue from the corrected state. Do not update the handoff unless the user explicitly asks to save.

## Maintain A Handoff

For long tasks, maintain the handoff only in response to an explicit user save request.

Treat these as useful moments to offer a save, not as permission to write one:

- A feature or fix is implemented.
- A test result changes the known state.
- A blocker is removed or added.
- The user gives a new constraint.
- The next action changes materially.
- The conversation has grown long enough that a checkpoint would reduce context risk.

When the user asks to save, keep previous checkpoint files. Do not overwrite history unless the user explicitly asks.

## Scripts

- `scripts/create_handoff.py`: create or update a task handoff with Markdown, JSON metadata, and checkpoint history.
- `scripts/list_handoffs.py`: list known handoffs under a workspace.
- `scripts/make_resume_prompt.py`: generate a ready-to-paste prompt for resuming a handoff in a new conversation.
- `scripts/validate_handoff.py`: check required sections and referenced file existence.

## Reference

Read `references/handoff-schema.md` when implementing or repairing the handoff format.
