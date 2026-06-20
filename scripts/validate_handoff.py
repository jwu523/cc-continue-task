#!/usr/bin/env python3
"""Validate an AI coding-agent task handoff."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


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


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Validate an AI coding-agent task handoff.")
    p.add_argument("handoff", help="Path to latest.md or a handoff directory.")
    p.add_argument("--check-files", action="store_true", help="Check metadata file paths that are local to the workspace.")
    return p


def resolve_latest(path: Path) -> Path:
    if path.is_dir():
        return path / "latest.md"
    return path


def section_exists(text: str, section: str) -> bool:
    return re.search(rf"(?m)^##\s+{re.escape(section)}\s*$", text) is not None


def main() -> int:
    args = parser().parse_args()
    target = resolve_latest(Path(args.handoff).resolve())
    errors: list[str] = []
    warnings: list[str] = []

    if not target.exists():
        errors.append(f"Missing handoff markdown: {target}")
    else:
        text = target.read_text(encoding="utf-8")
        if not re.search(r"(?m)^#\s+.+", text):
            errors.append("Missing top-level title.")
        for section in REQUIRED_SECTIONS:
            if not section_exists(text, section):
                errors.append(f"Missing section: {section}")

    metadata_path = target.parent / "handoff.json"
    metadata = {}
    if not metadata_path.exists():
        warnings.append(f"Missing metadata: {metadata_path}")
    else:
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"Invalid JSON metadata: {exc}")
        else:
            if not str(metadata.get("objective", "")).strip():
                errors.append("Missing metadata field: objective")
            if not str(metadata.get("objective_source", "")).strip():
                errors.append("Missing metadata field: objective_source")
            if not str(metadata.get("original_objective", "")).strip():
                errors.append("Missing metadata field: original_objective")
            if not str(metadata.get("goal_alignment", "")).strip():
                warnings.append("Missing metadata field: goal_alignment")
            if "quality_gate" not in metadata:
                warnings.append("Missing metadata field: quality_gate")
            if "confirmation_needed" not in metadata:
                warnings.append("Missing metadata field: confirmation_needed")
            if "omitted_or_compressed_context" not in metadata:
                warnings.append("Missing metadata field: omitted_or_compressed_context")

    if args.check_files and metadata:
        workspace = Path(str(metadata.get("workspace", "")))
        for file_value in metadata.get("files", []):
            file_path = Path(str(file_value))
            if not file_path.is_absolute():
                file_path = workspace / file_path
            if workspace and not file_path.exists():
                warnings.append(f"Referenced file not found: {file_path}")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        return 1
    print(f"OK: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
