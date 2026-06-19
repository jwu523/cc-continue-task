#!/usr/bin/env python3
"""List AI coding-agent task handoffs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="List AI coding-agent task handoffs.")
    p.add_argument("--workspace", default=".", help="Workspace root. Defaults to current directory.")
    p.add_argument("--handoff-root", default=".codex/handoffs", help="Handoff root relative to workspace unless absolute.")
    p.add_argument("--format", choices=["text", "json"], default="text")
    return p


def load_handoffs(root: Path) -> list[dict]:
    items: list[dict] = []
    for metadata_path in sorted(root.glob("*/handoff.json")):
        try:
            data = json.loads(metadata_path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        data.setdefault("task_id", metadata_path.parent.name)
        data.setdefault("title", metadata_path.parent.name)
        data.setdefault("updated", "")
        data.setdefault("status", "")
        data["_path"] = str(metadata_path.parent / "latest.md")
        items.append(data)

    known = {item["task_id"] for item in items}
    for latest_path in sorted(root.glob("*/latest.md")):
        if latest_path.parent.name in known:
            continue
        items.append(
            {
                "task_id": latest_path.parent.name,
                "title": latest_path.parent.name,
                "updated": "",
                "status": "",
                "_path": str(latest_path),
            }
        )

    return sorted(items, key=lambda item: item.get("updated") or "", reverse=True)


def main() -> int:
    args = parser().parse_args()
    workspace = Path(args.workspace).resolve()
    root = Path(args.handoff_root)
    if not root.is_absolute():
        root = workspace / root

    if not root.exists():
        if args.format == "json":
            print("[]")
        else:
            print(f"No handoffs found at {root}")
        return 0

    items = load_handoffs(root)
    if args.format == "json":
        print(json.dumps(items, indent=2, ensure_ascii=False))
        return 0

    if not items:
        print(f"No handoffs found at {root}")
        return 0

    for item in items:
        print(f"{item['task_id']} | {item.get('status', '')} | {item.get('updated', '')}")
        print(f"  title: {item.get('title', '')}")
        print(f"  path: {item.get('_path', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
