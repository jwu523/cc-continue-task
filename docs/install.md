# Install CC Continue Task

This guide covers installing the skill, verifying that Codex can use it, and updating it later.

## Skill Directory

Install the repository under your Codex skills directory:

```text
<CODEX_HOME>/skills/cc-continue-task
```

Common locations:

```text
Windows: %USERPROFILE%\.codex\skills\cc-continue-task
macOS:   $HOME/.codex/skills/cc-continue-task
Linux:   $HOME/.codex/skills/cc-continue-task
```

## Clone Install

```powershell
git clone https://github.com/jwu523/cc-continue-task.git <CODEX_HOME>\skills\cc-continue-task
```

For PowerShell on Windows, replace `<CODEX_HOME>` with your actual Codex home path.

## Manual Install

1. Download or copy this repository.
2. Place it at `<CODEX_HOME>/skills/cc-continue-task`.
3. Restart Codex or reload skills if your Codex environment requires it.

## Verify Installation

Start a Codex conversation in any workspace and ask:

```text
Use cc-continue-task to checkpoint this.
```

Expected behavior:

- Codex selects the `cc-continue-task` skill.
- If you did not specify an objective, Codex generates one from the conversation.
- A handoff is written under `.codex/handoffs/<task-id>/`.
- Codex reports the saved objective after writing the handoff.

You can also verify the helper scripts directly:

```powershell
python scripts/create_handoff.py --workspace . --title "Install Smoke Test" --print-path
python scripts/list_handoffs.py --workspace .
```

## Resume From A New Conversation

After saving a handoff, generate a prompt for the next conversation:

```powershell
python scripts/make_resume_prompt.py .codex/handoffs/<task-id>
```

Paste the generated prompt into a new Codex conversation.

## Update

If installed with Git:

```powershell
cd <CODEX_HOME>\skills\cc-continue-task
git pull
```

If installed manually, replace the skill directory with the new version and preserve only files you intentionally keep outside Git.

## Troubleshooting

- If Codex does not recognize the skill, restart Codex or reload skills.
- If a handoff is missing required sections, run `python scripts/validate_handoff.py <handoff>`.
- If a handoff may contain private data, run `python scripts/sanitize_handoff.py <handoff>` before sharing it.
