#!/usr/bin/env python3
"""Scan handoff files for secrets and environment-specific data."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


TEXT_EXTENSIONS = {
    ".json",
    ".log",
    ".md",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
}


@dataclass(frozen=True)
class Rule:
    name: str
    severity: str
    pattern: re.Pattern[str]
    replacement: str
    description: str


@dataclass
class Finding:
    path: str
    line: int
    rule: str
    severity: str
    excerpt: str


RULES = [
    Rule(
        name="private_key",
        severity="high",
        pattern=re.compile(r"BEGIN (?:RSA |OPENSSH |DSA |EC |PGP )?PRIVATE KEY"),
        replacement="[REDACTED_PRIVATE_KEY]",
        description="Private key material marker.",
    ),
    Rule(
        name="github_token",
        severity="high",
        pattern=re.compile(
            r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b|"
            r"github" r"_pat_[A-Za-z0-9_]{20,}"
        ),
        replacement="[REDACTED_GITHUB_TOKEN]",
        description="GitHub token-like value.",
    ),
    Rule(
        name="openai_api_key",
        severity="high",
        pattern=re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
        replacement="[REDACTED_API_KEY]",
        description="OpenAI-style API key.",
    ),
    Rule(
        name="aws_access_key",
        severity="high",
        pattern=re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        replacement="[REDACTED_AWS_KEY]",
        description="AWS access key id.",
    ),
    Rule(
        name="credential_assignment",
        severity="high",
        pattern=re.compile(
            r"(?i)\b(password|passwd|pwd|token|secret|api[_-]?key)\b\s*[:=]\s*(['\"]?)[^'\"\s,;}]+"
        ),
        replacement=r"\1=[REDACTED_CREDENTIAL]",
        description="Credential-looking assignment.",
    ),
    Rule(
        name="windows_user_path",
        severity="medium",
        pattern=re.compile(r"\b[A-Za-z]:\\Users\\[^\\\s]+(?:\\[^\s`'\"<>]*)?"),
        replacement="[REDACTED_WINDOWS_USER_PATH]",
        description="Windows user profile path.",
    ),
    Rule(
        name="unix_home_path",
        severity="medium",
        pattern=re.compile(r"(?<!\w)/(?:Users|home)/[^/\s]+(?:/[^\s`'\"<>]*)?"),
        replacement="[REDACTED_UNIX_HOME_PATH]",
        description="Unix user home path.",
    ),
    Rule(
        name="private_ipv4",
        severity="medium",
        pattern=re.compile(
            r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})\b"
        ),
        replacement="[REDACTED_PRIVATE_IP]",
        description="Private IPv4 address.",
    ),
]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Scan handoff files for secrets and environment-specific data.")
    p.add_argument("targets", nargs="+", help="Files or directories to scan.")
    p.add_argument("--json", action="store_true", help="Print findings as JSON.")
    p.add_argument("--redact-to", help="Write redacted copies under this directory.")
    p.add_argument("--include-all", action="store_true", help="Scan all decodable files, not only known text extensions.")
    p.add_argument("--max-bytes", type=int, default=1_000_000, help="Skip files larger than this size. Defaults to 1 MB.")
    return p


def iter_files(targets: Iterable[Path], include_all: bool, max_bytes: int) -> Iterable[Path]:
    for target in targets:
        if not target.exists():
            continue
        if target.is_file():
            candidates = [target]
        else:
            candidates = [path for path in target.rglob("*") if path.is_file()]
        for path in candidates:
            if path.name.startswith(".") and path.suffix == "":
                continue
            if not include_all and path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            try:
                if path.stat().st_size > max_bytes:
                    continue
            except OSError:
                continue
            yield path


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    except OSError:
        return None


def redacted_line(line: str) -> str:
    redacted = line.rstrip("\n")
    for rule in RULES:
        redacted = rule.pattern.sub(rule.replacement, redacted)
    return redacted.strip()


def scan_text(path: Path, text: str, display_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for rule in RULES:
            if rule.pattern.search(line):
                findings.append(
                    Finding(
                        path=str(display_path),
                        line=line_number,
                        rule=rule.name,
                        severity=rule.severity,
                        excerpt=redacted_line(line),
                    )
                )
    return findings


def redact_text(text: str) -> str:
    redacted = text
    for rule in RULES:
        redacted = rule.pattern.sub(rule.replacement, redacted)
    return redacted


def common_root(paths: list[Path]) -> Path:
    resolved = [path.resolve() for path in paths if path.exists()]
    if not resolved:
        return Path.cwd()
    if len(resolved) == 1:
        return resolved[0].parent if resolved[0].is_file() else resolved[0]
    return Path(os.path.commonpath([str(path) for path in resolved]))


def relative_display(path: Path, root: Path) -> Path:
    try:
        return path.resolve().relative_to(root.resolve())
    except ValueError:
        return path


def write_redacted_copy(path: Path, text: str, destination_root: Path, source_root: Path) -> None:
    relative = relative_display(path, source_root)
    destination = destination_root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(redact_text(text), encoding="utf-8", newline="\n")


def main() -> int:
    args = parser().parse_args()
    targets = [Path(value) for value in args.targets]
    source_root = common_root(targets)
    redact_root = Path(args.redact_to) if args.redact_to else None
    findings: list[Finding] = []
    scanned = 0

    for path in iter_files(targets, args.include_all, args.max_bytes):
        text = read_text(path)
        if text is None:
            continue
        scanned += 1
        display_path = relative_display(path, source_root)
        findings.extend(scan_text(path, text, display_path))
        if redact_root:
            write_redacted_copy(path, text, redact_root, source_root)

    payload = {
        "scanned_files": scanned,
        "finding_count": len(findings),
        "findings": [asdict(finding) for finding in findings],
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Scanned files: {scanned}")
        print(f"Findings: {len(findings)}")
        for finding in findings:
            print(
                f"{finding.severity.upper()} {finding.path}:{finding.line} "
                f"{finding.rule}: {finding.excerpt}"
            )

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
