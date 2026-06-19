# CC Continue Task Skill

Save and resume long-running Codex tasks across conversations while preserving the objective, controlling token use, reducing hallucination risk, and avoiding unnecessary project reloads. | 为长时间 Codex 任务保存和恢复可继续执行的状态，保持目标一致，控制 token 消耗，降低幻觉风险，并避免重复加载项目上下文。

[Quick Start](#install) · [Usage](#usage) · [简体中文](README_zh.md)

`cc-continue-task` is a Codex skill for checkpointing work that spans multiple conversations. It writes a durable handoff artifact to disk so a new conversation can continue from verified task state instead of relying on a long chat transcript.

## Repository Layout

- `SKILL.md`: skill instructions and operating rules.
- `agents/openai.yaml`: Codex agent metadata.
- `references/handoff-schema.md`: expected handoff Markdown and JSON structure.
- `scripts/create_handoff.py`: create or update a handoff.
- `scripts/list_handoffs.py`: list saved handoffs.
- `scripts/validate_handoff.py`: validate a handoff before relying on it.

## Install

Clone or copy this repository into your Codex skills directory as:

```text
<CODEX_HOME>/skills/cc-continue-task
```

Restart Codex or reload skills if your Codex environment requires it.

## Why This Exists

Large tasks often take many model turns. Keeping everything in one conversation can consume a large context budget and increase the chance that the model relies on stale or invented details. Starting a new conversation saves context, but usually loses task continuity.

This skill bridges that gap by saving only the state needed to continue:

- the task objective and its source
- current progress and next steps
- verified facts, assumptions, risks, and open questions
- exact files, commands, and artifacts that matter
- a context loading plan that says what to read, defer, or avoid
- compression intent that says what to preserve, drop, and revalidate

## Usage

Ask Codex to save a handoff when a task reaches a useful checkpoint:

```text
Use cc-continue-task to save this task.
Task objective: finish the refactor and verify the CLI still works.
```

If you do not provide an objective, the skill should generate one from the conversation and print it after the handoff is written:

```text
Use cc-continue-task to checkpoint this.
```

Resume from a saved handoff in a new conversation:

```text
Use cc-continue-task to resume the latest handoff for this workspace.
```

Or point to a specific handoff:

```text
Use cc-continue-task to resume .codex/handoffs/my-task/latest.md.
```

## Objective Continuity

The skill records both the current `Objective` and the stable `Original Objective`.

On later saves after a resume, the handoff should stay aligned with the original objective. If the conversation has drifted, or if a newly supplied objective conflicts with the original objective, the skill should stop and guide the user to either adjust the objective explicitly or save a new handoff.

This prevents a long-running handoff from silently becoming a different task.

## Handoff Files

By default, handoffs are written under the current workspace:

```text
.codex/handoffs/<task-id>/
  latest.md
  handoff.json
  checkpoints/
```

`latest.md` is optimized for a human and a future Codex conversation. `handoff.json` is an indexable summary for tooling. `checkpoints/` preserves older Markdown snapshots.

## Script Examples

Create a handoff:

```powershell
python scripts/create_handoff.py `
  --workspace . `
  --title "Refactor CLI parser" `
  --objective "Finish the CLI parser refactor and verify existing commands still work." `
  --objective-source user_specified `
  --current-state "Parser split is implemented; tests still need to run." `
  --next-step "Run the focused CLI test suite." `
  --must-read "latest.md" `
  --print-path
```

List handoffs:

```powershell
python scripts/list_handoffs.py --workspace .
```

Validate a handoff:

```powershell
python scripts/validate_handoff.py .codex/handoffs/refactor-cli-parser --check-files
```

## Privacy And Sanitization

Handoff files may contain local paths, command output, issue details, or operational context. Before publishing, sharing, or attaching generated handoffs, review them for secrets and environment-specific data.

This repository should contain the skill and helper scripts only. Do not commit generated `.codex/handoffs/` data, local caches, credentials, tokens, or private project notes.

## License

MIT
