#!/usr/bin/env python3
"""Create or update an AI coding-agent task handoff."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from make_resume_prompt import build_prompt


REQUIRED_SECTIONS = [
    "Objective",
    "Goal Alignment",
    "Handoff Quality Gate",
    "Current State",
    "Completed",
    "In Progress",
    "Next Steps",
    "Files And Artifacts",
    "Context Loading Plan",
    "Commands And Results",
    "Verified Facts",
    "Assumptions",
    "Risks And Blockers",
    "Open Questions",
    "User Constraints",
    "Compression Intent",
    "Omitted Or Compressed Context",
    "Resume Instructions",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value[:80] or "task-handoff"


def run_git(workspace: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=workspace,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=10,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - defensive for varied hosts
        return f"git unavailable: {exc}"
    return result.stdout.strip()


def bullet_list(items: list[str], empty: str = "Not recorded.") -> str:
    cleaned = [item.strip() for item in items if item and item.strip()]
    if not cleaned:
        return f"- {empty}"
    return "\n".join(f"- {item}" for item in cleaned)


def text_block(value: str, empty: str = "Not recorded.") -> str:
    value = (value or "").strip()
    return value if value else empty


def section(title: str, body: str) -> str:
    return f"## {title}\n\n{body.strip()}\n"


def subsection(title: str, body: str) -> str:
    return f"### {title}\n\n{body.strip()}\n"


def context_loading_plan(args: argparse.Namespace) -> str:
    return "\n".join(
        [
            subsection("Must Read", bullet_list(args.must_read)),
            subsection("Read Only If Needed", bullet_list(args.read_if_needed)),
            subsection("Do Not Reload Unless Mismatch", bullet_list(args.do_not_reload)),
        ]
    ).strip()


def compression_intent(args: argparse.Namespace) -> str:
    return "\n".join(
        [
            subsection("Preserve", bullet_list(args.preserve)),
            subsection("Drop", bullet_list(args.drop)),
            subsection("Revalidate", bullet_list(args.revalidate)),
        ]
    ).strip()


def quality_gate(args: argparse.Namespace) -> str:
    return "\n".join(
        [
            text_block(args.quality_gate, "No unresolved save-scope uncertainty recorded."),
            "",
            subsection("Needs User Confirmation", bullet_list(args.confirmation_needed, "None recorded.")),
        ]
    ).strip()


def omitted_or_compressed_context(args: argparse.Namespace) -> str:
    return "\n".join(
        [
            subsection("Compressed", bullet_list(args.compressed_context, "None recorded.")),
            subsection("Dropped", bullet_list(args.dropped_context, "None recorded.")),
            subsection("User-Confirmed Omissions", bullet_list(args.user_confirmed_omission, "None recorded.")),
        ]
    ).strip()


def build_markdown(args: argparse.Namespace, workspace: Path, updated: str) -> str:
    git_branch = run_git(workspace, ["branch", "--show-current"])
    git_status = run_git(workspace, ["status", "--short"])
    if not git_status:
        git_status = "Clean or not a git repository."

    parts = [
        f"# {args.title}\n",
        f"- Task ID: {args.task_id}",
        f"- Updated: {updated}",
        f"- Workspace: {workspace}",
        f"- Status: {args.status}",
        f"- Objective Source: {args.objective_source}",
        f"- Original Objective: {args.original_objective}",
        f"- Git Branch: {git_branch or 'Not recorded.'}",
        "",
    ]

    parts.append(section("Objective", text_block(args.objective)))
    parts.append(section("Goal Alignment", text_block(args.goal_alignment, "Not assessed.")))
    parts.append(section("Handoff Quality Gate", quality_gate(args)))
    parts.append(section("Current State", text_block(args.current_state)))
    parts.append(section("Completed", bullet_list(args.completed)))
    parts.append(section("In Progress", bullet_list(args.in_progress)))
    parts.append(section("Next Steps", bullet_list(args.next_step)))
    parts.append(section("Files And Artifacts", bullet_list(args.file)))
    parts.append(section("Context Loading Plan", context_loading_plan(args)))
    parts.append(section("Commands And Results", bullet_list(args.command_result)))
    parts.append(section("Verified Facts", bullet_list(args.verified_fact)))
    parts.append(section("Assumptions", bullet_list(args.assumption)))
    parts.append(section("Risks And Blockers", bullet_list(args.risk)))
    parts.append(section("Open Questions", bullet_list(args.open_question)))
    parts.append(section("User Constraints", bullet_list(args.user_constraint)))
    parts.append(section("Compression Intent", compression_intent(args)))
    parts.append(section("Omitted Or Compressed Context", omitted_or_compressed_context(args)))
    parts.append(section("Resume Instructions", bullet_list(args.resume_instruction)))
    parts.append(section("Workspace Snapshot", f"```text\n{git_status}\n```"))

    if args.notes:
        parts.append(section("Additional Notes", text_block(args.notes)))

    return "\n".join(parts).rstrip() + "\n"


def build_json(args: argparse.Namespace, workspace: Path, updated: str) -> dict:
    return {
        "task_id": args.task_id,
        "title": args.title,
        "workspace": str(workspace),
        "status": args.status,
        "updated": updated,
        "objective": args.objective,
        "objective_source": args.objective_source,
        "original_objective": args.original_objective,
        "goal_alignment": args.goal_alignment,
        "quality_gate": args.quality_gate,
        "confirmation_needed": args.confirmation_needed,
        "current_state": args.current_state,
        "next_steps": args.next_step,
        "files": args.file,
        "context_loading_plan": {
            "must_read": args.must_read,
            "read_only_if_needed": args.read_if_needed,
            "do_not_reload_unless_mismatch": args.do_not_reload,
        },
        "commands": args.command_result,
        "verified_facts": args.verified_fact,
        "assumptions": args.assumption,
        "risks": args.risk,
        "open_questions": args.open_question,
        "user_constraints": args.user_constraint,
        "compression_intent": {
            "preserve": args.preserve,
            "drop": args.drop,
            "revalidate": args.revalidate,
        },
        "omitted_or_compressed_context": {
            "compressed": args.compressed_context,
            "dropped": args.dropped_context,
            "user_confirmed_omissions": args.user_confirmed_omission,
        },
        "resume_instructions": args.resume_instruction,
    }


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Create or update an AI coding-agent task handoff.")
    p.add_argument("--workspace", default=".", help="Workspace root. Defaults to current directory.")
    p.add_argument("--handoff-root", default=".codex/handoffs", help="Handoff root relative to workspace unless absolute.")
    p.add_argument("--task-id", help="Stable handoff id. Defaults to a slug of --title.")
    p.add_argument("--title", required=True, help="Human-readable task title.")
    p.add_argument("--status", default="in_progress", choices=["in_progress", "blocked", "complete", "paused"])
    p.add_argument("--objective", "--goal", dest="objective", default="", help="Task objective. If omitted, the script uses --title as a generated objective fallback; agents should pass a conversation-derived objective when possible.")
    p.add_argument("--objective-source", choices=["user_specified", "generated", "inferred", "unknown"], help="Where the objective came from. Defaults to user_specified when --objective is set, otherwise generated.")
    p.add_argument("--original-objective", default="", help="Stable objective from the first handoff in a resumed task chain. Defaults to --objective.")
    p.add_argument("--goal-alignment", default="", help="Short assessment of whether this handoff still aligns with the original objective.")
    p.add_argument("--quality-gate", default="", help="Assessment of whether the handoff captures the necessary task state without unresolved save-scope uncertainty.")
    p.add_argument("--confirmation-needed", action="append", default=[], help="Point that should be confirmed with the user before omitting or compressing context.")
    p.add_argument("--current-state", default="")
    p.add_argument("--completed", action="append", default=[])
    p.add_argument("--in-progress", action="append", default=[])
    p.add_argument("--next-step", action="append", default=[])
    p.add_argument("--file", action="append", default=[])
    p.add_argument("--must-read", action="append", default=[], help="File, artifact, or context the next conversation should read first.")
    p.add_argument("--read-if-needed", action="append", default=[], help="File, artifact, or context to defer until needed.")
    p.add_argument("--do-not-reload", action="append", default=[], help="Broad area to avoid reloading unless verification fails.")
    p.add_argument("--command-result", action="append", default=[])
    p.add_argument("--verified-fact", action="append", default=[])
    p.add_argument("--assumption", action="append", default=[])
    p.add_argument("--risk", action="append", default=[])
    p.add_argument("--open-question", action="append", default=[])
    p.add_argument("--user-constraint", action="append", default=[])
    p.add_argument("--preserve", action="append", default=[], help="State, decision, or fact to preserve across conversations.")
    p.add_argument("--drop", action="append", default=[], help="Detail intentionally omitted to save context.")
    p.add_argument("--revalidate", action="append", default=[], help="Volatile fact to check cheaply before relying on it.")
    p.add_argument("--compressed-context", action="append", default=[], help="Context intentionally compressed into a shorter summary.")
    p.add_argument("--dropped-context", action="append", default=[], help="Context intentionally omitted because it is irrelevant or superseded.")
    p.add_argument("--user-confirmed-omission", action="append", default=[], help="Context the user explicitly agreed can be omitted or compressed.")
    p.add_argument("--resume-instruction", action="append", default=[])
    p.add_argument("--notes", default="")
    p.add_argument("--print-path", action="store_true")
    return p


def main() -> int:
    args = parser().parse_args()
    workspace = Path(args.workspace).resolve()
    if not workspace.exists():
        raise SystemExit(f"Workspace does not exist: {workspace}")

    args.task_id = args.task_id or slugify(args.title)
    objective_was_provided = bool(args.objective.strip())
    if not objective_was_provided:
        args.objective = args.title.strip()
    if args.objective_source is None:
        args.objective_source = "user_specified" if objective_was_provided else "generated"
    if not args.original_objective.strip():
        args.original_objective = args.objective
    root = Path(args.handoff_root)
    if not root.is_absolute():
        root = workspace / root
    handoff_dir = root / args.task_id
    checkpoints = handoff_dir / "checkpoints"
    checkpoints.mkdir(parents=True, exist_ok=True)

    updated = now_iso()
    markdown = build_markdown(args, workspace, updated)
    metadata = build_json(args, workspace, updated)

    latest_md = handoff_dir / "latest.md"
    latest_json = handoff_dir / "handoff.json"
    checkpoint_md = checkpoints / f"{updated.replace(':', '').replace('+', '_')}.md"

    latest_md.write_text(markdown, encoding="utf-8", newline="\n")
    latest_json.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    checkpoint_md.write_text(markdown, encoding="utf-8", newline="\n")

    if args.print_path:
        print(latest_md)
    else:
        print(f"Wrote handoff: {latest_md}")
        print(f"Wrote metadata: {latest_json}")
        print(f"Wrote checkpoint: {checkpoint_md}")
        print(f"Saved objective ({args.objective_source}): {args.objective}")
        print(f"Original objective: {args.original_objective}")
        print()
        print("Resume prompt:")
        print(build_prompt(latest_md, metadata, include_next_steps=True), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
