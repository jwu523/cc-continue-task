#!/usr/bin/env python3
"""Generate a prompt for resuming a saved handoff in a new conversation."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


CJK_PATTERN = re.compile(r"[\u3400-\u9fff]")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generate a resume prompt for an AI coding-agent task handoff.")
    p.add_argument("handoff", help="Path to a handoff directory, latest.md, or handoff.json.")
    p.add_argument("--json", action="store_true", help="Print prompt data as JSON.")
    p.add_argument("--language", choices=["auto", "en", "zh"], default="auto", help="Prompt language. Defaults to auto-detecting from handoff metadata.")
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


def metadata_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(metadata_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(metadata_text(item) for item in value)
    return str(value or "")


def detect_language(metadata: dict[str, Any], requested: str = "auto") -> str:
    if requested in {"en", "zh"}:
        return requested

    explicit = str(metadata.get("conversation_language") or metadata.get("language") or "").strip().lower()
    if explicit in {"zh", "zh-cn", "cn", "chinese", "中文"}:
        return "zh"
    if explicit in {"en", "en-us", "english"}:
        return "en"

    text = metadata_text(
        {
            "objective": metadata.get("objective"),
            "original_objective": metadata.get("original_objective"),
            "goal_alignment": metadata.get("goal_alignment"),
            "current_state": metadata.get("current_state"),
            "next_steps": metadata.get("next_steps"),
            "resume_instructions": metadata.get("resume_instructions"),
            "user_constraints": metadata.get("user_constraints"),
        }
    )
    return "zh" if len(CJK_PATTERN.findall(text)) >= 4 else "en"


def build_prompt(latest_md: Path, metadata: dict[str, Any], include_next_steps: bool, language: str = "auto") -> str:
    prompt_language = detect_language(metadata, language)
    objective = str(metadata.get("objective") or "").strip()
    original_objective = str(metadata.get("original_objective") or "").strip()
    objective_source = str(metadata.get("objective_source") or "").strip()
    goal_alignment = str(metadata.get("goal_alignment") or "").strip()
    status = str(metadata.get("status") or "").strip()
    next_steps = as_lines(metadata.get("next_steps")) if include_next_steps else []

    if prompt_language == "zh":
        lines = [
            "使用 cc-continue-task 继续这个交接：",
            str(latest_md),
            "",
            "先按 Context Loading Plan 读取上下文。先读 Must Read，再做更大范围的项目探索。",
            "下次保存检查点时保留 Original Objective。",
            "继续前先报告目标漂移或过期状态。",
        ]
        labels = {
            "original_objective": "原始目标",
            "current_objective": "当前目标",
            "objective": "目标",
            "objective_source": "目标来源",
            "status": "状态",
            "goal_alignment": "目标对齐",
            "metadata_heading": "已知交接元数据：",
            "next_steps_heading": "后续步骤（来自 handoff.json）：",
        }
    else:
        lines = [
            "Use cc-continue-task to resume this handoff:",
            str(latest_md),
            "",
            "Follow the Context Loading Plan first. Read Must Read items before broader project exploration.",
            "Preserve the Original Objective when saving the next checkpoint.",
            "Report objective drift or stale state before continuing.",
        ]
        labels = {
            "original_objective": "Original objective",
            "current_objective": "Current objective",
            "objective": "Objective",
            "objective_source": "Objective source",
            "status": "Status",
            "goal_alignment": "Goal alignment",
            "metadata_heading": "Known handoff metadata:",
            "next_steps_heading": "Next steps from handoff.json:",
        }

    details: list[str] = []
    if original_objective:
        details.append(f"{labels['original_objective']}: {original_objective}")
    if objective and objective != original_objective:
        details.append(f"{labels['current_objective']}: {objective}")
    elif objective and not original_objective:
        details.append(f"{labels['objective']}: {objective}")
    if objective_source:
        details.append(f"{labels['objective_source']}: {objective_source}")
    if status:
        details.append(f"{labels['status']}: {status}")
    if goal_alignment:
        details.append(f"{labels['goal_alignment']}: {goal_alignment}")

    if details:
        lines.extend(["", labels["metadata_heading"], *[f"- {item}" for item in details]])

    if next_steps:
        lines.extend(["", labels["next_steps_heading"]])
        lines.extend(f"{index}. {step}" for index, step in enumerate(next_steps, start=1))

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parser().parse_args()
    latest_md, metadata_path = resolve_paths(args.handoff)
    metadata = read_metadata(metadata_path)
    prompt = build_prompt(latest_md, metadata, include_next_steps=not args.no_next_steps, language=args.language)

    if args.json:
        print(
            json.dumps(
                {
                    "latest_md": str(latest_md),
                    "metadata": str(metadata_path) if metadata_path else None,
                    "language": detect_language(metadata, args.language),
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
