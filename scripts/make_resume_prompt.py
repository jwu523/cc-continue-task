#!/usr/bin/env python3
"""Generate a prompt for resuming a saved handoff in a new conversation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generate a resume prompt for a Codex task handoff.")
    p.add_argument("handoff", help="Path to a handoff directory, latest.md, or handoff.json.")
    p.add_argument("--json", action="store_true", help="Print prompt data as JSON.")
    p.add_argument("--no-next-steps", action="store_true", help="Do not include next steps from handoff.json.")
    return p


def resolve_paths(value: str) -> tuple[Path, Path | None]:
    path = Path(value).expanduser().resolve()
    if path.is_dir():
        latest_md = path / "latest.md"
        metadata_path = path / "handoff.json"
    elif path.name == "handoff.json":
        metadata_path = path
        latest_md = path.parent / "latest.md"
    else:
        latest_md = path
        metadata_path = path.parent / "handoff.json"

    if not latest_md.exists():
        raise SystemExit(f"Missing handoff markdown: {latest_md}")
    if not metadata_path.exists():
        metadata_path = None
    return latest_md, metadata_path


def read_metadata(metadata_path: Path | None) -> dict[str, Any]:
    if metadata_path is None:
        return {}
    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"Invalid handoff metadata: {metadata_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"Invalid handoff metadata: {metadata_path}: expected JSON object")
    return data


def as_lines(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def build_prompt(latest_md: Path, metadata: dict[str, Any], include_next_steps: bool) -> str:
    objective = str(metadata.get("objective") or "").strip()
    original_objective = str(metadata.get("original_objective") or "").strip()
    objective_source = str(metadata.get("objective_source") or "").strip()
    goal_alignment = str(metadata.get("goal_alignment") or "").strip()
    status = str(metadata.get("status") or "").strip()
    next_steps = as_lines(metadata.get("next_steps")) if include_next_steps else []

    lines = [
        "Use cc-continue-task to resume this handoff:",
        str(latest_md),
        "",
        "Follow the Context Loading Plan first. Read Must Read items before broader project exploration.",
        "Preserve the Original Objective when saving the next checkpoint.",
        "Report objective drift or stale state before continuing.",
    ]

    details: list[str] = []
    if original_objective:
        details.append(f"Original objective: {original_objective}")
    if objective and objective != original_objective:
        details.append(f"Current objective: {objective}")
    elif objective and not original_objective:
        details.append(f"Objective: {objective}")
    if objective_source:
        details.append(f"Objective source: {objective_source}")
    if status:
        details.append(f"Status: {status}")
    if goal_alignment:
        details.append(f"Goal alignment: {goal_alignment}")

    if details:
        lines.extend(["", "Known handoff metadata:", *[f"- {item}" for item in details]])

    if next_steps:
        lines.extend(["", "Next steps from handoff.json:"])
        lines.extend(f"{index}. {step}" for index, step in enumerate(next_steps, start=1))

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parser().parse_args()
    latest_md, metadata_path = resolve_paths(args.handoff)
    metadata = read_metadata(metadata_path)
    prompt = build_prompt(latest_md, metadata, include_next_steps=not args.no_next_steps)

    if args.json:
        print(
            json.dumps(
                {
                    "latest_md": str(latest_md),
                    "metadata": str(metadata_path) if metadata_path else None,
                    "prompt": prompt,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(prompt, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
