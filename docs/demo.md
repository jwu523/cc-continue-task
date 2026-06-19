# Demo: Save And Resume A Task

This demo shows the intended workflow: save a compact handoff, start a new conversation, and resume from the generated prompt.

## 1. Save A Handoff

During a long-running task, ask your AI coding agent:

```text
Use cc-continue-task to save this task.
Task objective: finish the CLI parser refactor and verify existing commands still work.
```

Expected result:

- A handoff is written under `.codex/handoffs/<task-id>/`.
- The saved objective is printed.
- A resume prompt is printed automatically.

The resume prompt looks like this:

```text
Use cc-continue-task to resume this handoff:
.codex/handoffs/<task-id>/latest.md

Follow the Context Loading Plan first. Read Must Read items before broader project exploration.
Preserve the Original Objective when saving the next checkpoint.
Report objective drift or stale state before continuing.
```

## 2. Start A New Conversation

Open a new agent conversation and paste the generated resume prompt.

The agent should:

- read `latest.md`
- follow the `Context Loading Plan`
- verify cheap drift-prone facts
- continue from `Next Steps`
- preserve the `Original Objective` on the next save

## 3. Save Again After Progress

After meaningful progress, ask:

```text
Use cc-continue-task to save this task.
```

The skill should keep the original objective unless you explicitly change it. If the task has drifted, it should ask whether to adjust the objective or save a new handoff.

## 4. Share Safely

Before sharing any generated handoff:

```powershell
python scripts/validate_handoff.py .codex/handoffs/<task-id> --check-files
python scripts/sanitize_handoff.py .codex/handoffs/<task-id>
```

Review the handoff manually. The sanitizer is a first-pass scanner, not a guarantee.
