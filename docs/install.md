# Install CC Continue Task

This guide covers installing the Codex skill package, verifying the handoff workflow, and updating it later. The handoff format and scripts are usable with other AI coding agents as well.

## Skill Directory

For Codex, install the repository under your Codex skills directory:

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

For PowerShell on Windows, replace `<CODEX_HOME>` with your actual Codex home path or chosen install path.

## Manual Install

1. Download or copy this repository.
2. Place it at `<CODEX_HOME>/skills/cc-continue-task`.
3. Restart Codex or reload skills if your Codex environment requires it.

For Claude Code, OpenCode, or other agents, keep the repository wherever the agent can read and execute the helper scripts, then adapt `SKILL.md` into that agent's custom-instruction or workflow mechanism.

## Verify Installation

Start an agent conversation in any workspace and ask:

```text
Use cc-continue-task to checkpoint this.
```

Expected behavior:

- In Codex, the `cc-continue-task` skill is selected.
- If you did not specify an objective, the agent generates one from the conversation.
- If the save scope is ambiguous, the agent asks what to preserve, compress, or drop before writing the handoff.
- A handoff is written under `.codex/handoffs/<task-id>/`.
- The agent reports the saved objective after writing the handoff.
- The agent prints a resume prompt generated from the saved handoff.

You can also verify the helper scripts directly:

```powershell
python scripts/create_handoff.py --workspace . --title "Install Smoke Test" --print-path
python scripts/list_handoffs.py --workspace .
```

## Resume From A New Conversation

After saving a handoff, the skill should print a prompt for the next conversation automatically. You can regenerate it manually:

```powershell
python scripts/make_resume_prompt.py .codex/handoffs/<task-id>
```

Paste the generated prompt into a new agent conversation.

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
