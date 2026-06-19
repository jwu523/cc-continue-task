# CC Continue Task Skill

[![CI](https://github.com/jwu523/cc-continue-task/actions/workflows/ci.yml/badge.svg)](https://github.com/jwu523/cc-continue-task/actions/workflows/ci.yml)

Save and resume long-running Codex tasks across conversations while preserving the objective, controlling token use, reducing hallucination risk, and avoiding unnecessary project reloads. | 为长时间 Codex 任务保存和恢复可继续执行的状态，保持目标一致，控制 token 消耗，降低幻觉风险，并避免重复加载项目上下文。

[Quick Start](#install) · [Usage](#usage) · [简体中文](README_zh.md)

`cc-continue-task` is a Codex skill for checkpointing work that spans multiple conversations. It writes a durable handoff artifact to disk so a new conversation can continue from verified task state instead of relying on a long chat transcript.

## Repository Layout

- `SKILL.md`: skill instructions and operating rules.
- `agents/openai.yaml`: Codex agent metadata.
- `CHANGELOG.md`: release history.
- `CONTRIBUTING.md`: contribution guidelines.
- `docs/install.md`: detailed installation, verification, and update guide.
- `docs/demo.md`: end-to-end save and resume walkthrough.
- `examples/`: sanitized example handoffs for common continuation scenarios.
- `references/handoff-schema.md`: expected handoff Markdown and JSON structure.
- `scripts/create_handoff.py`: create or update a handoff.
- `scripts/list_handoffs.py`: list saved handoffs.
- `scripts/make_resume_prompt.py`: generate a prompt for resuming a handoff in a new conversation.
- `scripts/sanitize_handoff.py`: scan handoff files for secrets and environment-specific data.
- `scripts/validate_handoff.py`: validate a handoff before relying on it.
- `SECURITY.md`: sensitive-data handling and reporting guidance.
- `tests/`: dependency-free unit tests for the helper scripts.

## Documentation

- [Install Guide](docs/install.md)
- [Demo Workflow](docs/demo.md)
- [Release Notes](docs/releases/v0.1.0.md)
- [Contributing](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)

## Install

Clone or copy this repository into your Codex skills directory as:

```text
<CODEX_HOME>/skills/cc-continue-task
```

Restart Codex or reload skills if your Codex environment requires it.

For detailed setup and verification, see [docs/install.md](docs/install.md).

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

After saving, the skill should automatically generate a ready-to-paste resume prompt with `scripts/make_resume_prompt.py` and include it in the response.

Resume from a saved handoff in a new conversation:

```text
Use cc-continue-task to resume the latest handoff for this workspace.
```

Or point to a specific handoff:

```text
Use cc-continue-task to resume .codex/handoffs/my-task/latest.md.
```

You can also regenerate the resume prompt manually:

```powershell
python scripts/make_resume_prompt.py .codex/handoffs/my-task
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

Without `--print-path`, `create_handoff.py` prints the saved objective and a resume prompt generated from the new handoff. Keep `--print-path` for scripting when you only want the Markdown path.

List handoffs:

```powershell
python scripts/list_handoffs.py --workspace .
```

Generate a prompt for a new conversation:

```powershell
python scripts/make_resume_prompt.py .codex/handoffs/refactor-cli-parser
```

Validate a handoff:

```powershell
python scripts/validate_handoff.py .codex/handoffs/refactor-cli-parser --check-files
```

Scan a handoff before sharing it:

```powershell
python scripts/sanitize_handoff.py .codex/handoffs/refactor-cli-parser
```

Create redacted copies:

```powershell
python scripts/sanitize_handoff.py .codex/handoffs/refactor-cli-parser --redact-to redacted-handoffs
```

## Examples

The `examples/` directory contains sanitized fictional handoffs:

- `examples/basic/`: a normal checkpoint with a user-specified objective.
- `examples/generated-objective/`: a checkpoint where Codex generated the objective.
- `examples/objective-drift/`: a resumed task that should split into a new handoff because it drifted from the original objective.

## Quality Checks

Run the local checks with the Python standard library:

```powershell
python -m py_compile scripts/create_handoff.py scripts/list_handoffs.py scripts/make_resume_prompt.py scripts/validate_handoff.py scripts/sanitize_handoff.py
python -m unittest discover -s tests
python scripts/sanitize_handoff.py examples
```

GitHub Actions runs the same checks on push and pull requests.

## Privacy And Sanitization

Handoff files may contain local paths, command output, issue details, or operational context. Before publishing, sharing, or attaching generated handoffs, review them for secrets and environment-specific data.

Use `scripts/sanitize_handoff.py` as a first pass before sharing a handoff. It reports likely credentials, private keys, local user paths, and private network addresses without printing the original secret value.

This repository should contain the skill and helper scripts only. Do not commit generated `.codex/handoffs/` data, local caches, credentials, tokens, or private project notes.

## License

MIT
