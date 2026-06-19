from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CREATE_HANDOFF = REPO_ROOT / "scripts" / "create_handoff.py"
MAKE_RESUME_PROMPT = REPO_ROOT / "scripts" / "make_resume_prompt.py"
VALIDATE_HANDOFF = REPO_ROOT / "scripts" / "validate_handoff.py"
SANITIZE_HANDOFF = REPO_ROOT / "scripts" / "sanitize_handoff.py"


def run_script(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd or REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


class HandoffScriptTests(unittest.TestCase):
    def test_create_and_validate_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            result = run_script(
                str(CREATE_HANDOFF),
                "--workspace",
                str(workspace),
                "--title",
                "Demo Task",
                "--objective",
                "Finish the demo task and verify the result.",
                "--objective-source",
                "user_specified",
                "--goal-alignment",
                "The state is aligned with the objective.",
                "--current-state",
                "A test handoff is being generated.",
                "--completed",
                "Created test input.",
                "--next-step",
                "Validate generated handoff.",
                "--must-read",
                "latest.md",
                "--preserve",
                "Objective and verified facts.",
                "--drop",
                "Transcript detail.",
                "--revalidate",
                "Current git status.",
                "--resume-instruction",
                "Run the validator.",
            )

            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("Saved objective (user_specified): Finish the demo task and verify the result.", result.stdout)
            self.assertIn("Resume prompt:", result.stdout)
            self.assertIn("Use cc-continue-task to resume this handoff:", result.stdout)
            handoff_dir = workspace / ".codex" / "handoffs" / "demo-task"
            self.assertTrue((handoff_dir / "latest.md").exists())
            self.assertTrue((handoff_dir / "handoff.json").exists())

            validate = run_script(str(VALIDATE_HANDOFF), str(handoff_dir))
            self.assertEqual(validate.returncode, 0, validate.stdout)

            prompt = run_script(str(MAKE_RESUME_PROMPT), str(handoff_dir))
            self.assertEqual(prompt.returncode, 0, prompt.stdout)
            self.assertIn("Use cc-continue-task to resume this handoff:", prompt.stdout)
            self.assertIn("Original objective: Finish the demo task and verify the result.", prompt.stdout)
            self.assertIn("Objective source: user_specified", prompt.stdout)
            self.assertIn("1. Validate generated handoff.", prompt.stdout)

    def test_validate_rejects_missing_required_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            handoff_dir = Path(tmp) / "broken"
            handoff_dir.mkdir()
            (handoff_dir / "latest.md").write_text("# Broken\n\n## Objective\n\nMissing most sections.\n", encoding="utf-8")

            result = run_script(str(VALIDATE_HANDOFF), str(handoff_dir))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing section: Goal Alignment", result.stdout)

    def test_sanitize_detects_and_redacts_sensitive_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "handoff.md"
            credential_line = "pass" + "word = super-secret-value"
            user_path_line = "path: " + "C:" + "\\Users\\alice\\demo\\file.txt"
            private_ip_line = "host: " + "192." + "168." + "1.20"
            source.write_text(
                "\n".join(
                    [
                        "# Demo",
                        credential_line,
                        user_path_line,
                        private_ip_line,
                    ]
                ),
                encoding="utf-8",
            )
            redacted_dir = root / "redacted"

            result = run_script(
                str(SANITIZE_HANDOFF),
                str(source),
                "--json",
                "--redact-to",
                str(redacted_dir),
            )

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["finding_count"], 3)
            rendered = json.dumps(payload)
            self.assertNotIn("super-secret-value", rendered)
            self.assertIn("REDACTED_CREDENTIAL", rendered)

            redacted_text = (redacted_dir / "handoff.md").read_text(encoding="utf-8")
            self.assertNotIn("super-secret-value", redacted_text)
            self.assertIn("REDACTED_CREDENTIAL", redacted_text)

    def test_examples_have_required_sections(self) -> None:
        for latest_md in (REPO_ROOT / "examples").glob("*/latest.md"):
            with self.subTest(example=latest_md):
                result = run_script(str(VALIDATE_HANDOFF), str(latest_md))
                self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
