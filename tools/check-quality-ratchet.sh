#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${QUALITY_RATCHET_OUTPUT_DIR:-$ROOT_DIR/.march/reality-check}"
SPEC_GLOB="${QUALITY_RATCHET_SPEC_GLOB:-$ROOT_DIR/spec/*.md}"
CLI_FILE="${QUALITY_RATCHET_CLI_FILE:-$ROOT_DIR/src/cli/mod.rs}"
SHELL_FILE="${QUALITY_RATCHET_SHELL_FILE:-$ROOT_DIR/src/mcp/shell.rs}"
BUILD_FILE="${QUALITY_RATCHET_BUILD_FILE:-$ROOT_DIR/build.rs}"
SOURCES_DIR="${QUALITY_RATCHET_SOURCES_DIR:-$ROOT_DIR/src/sources}"
SOURCES_MOD="${QUALITY_RATCHET_SOURCES_MOD:-$ROOT_DIR/src/sources/mod.rs}"
HEALTH_FILE="${QUALITY_RATCHET_HEALTH_FILE:-$ROOT_DIR/src/cli/health.rs}"

mkdir -p "$OUTPUT_DIR"

python3 - <<'PY' \
  "$ROOT_DIR" \
  "$OUTPUT_DIR" \
  "$SPEC_GLOB" \
  "$CLI_FILE" \
  "$SHELL_FILE" \
  "$BUILD_FILE" \
  "$SOURCES_DIR" \
  "$SOURCES_MOD" \
  "$HEALTH_FILE"
from __future__ import annotations

import glob
import json
import re
import subprocess
import sys
from pathlib import Path

MUSTMATCH_JSON_RE = re.compile(r"\|\s*mustmatch\s+json\b")
SHORT_LIKE_RE = re.compile(r'\|\s*mustmatch\s+like\s+("([^"]*)"|\'([^\']*)\')')
FENCE_RE = re.compile(r"^```(?P<info>.*)$")


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_json_command(command: list[str], *, allowed_exit_codes: set[int]) -> dict[str, object]:
    proc = subprocess.run(command, capture_output=True, text=True, check=False)
    if proc.returncode not in allowed_exit_codes:
        return {
            "status": "error",
            "command": command,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "errors": [f"unexpected exit code {proc.returncode}"],
        }
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "command": command,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "errors": [f"invalid JSON output: {exc}"],
        }
    payload["exit_code"] = proc.returncode
    if proc.stderr:
        payload["stderr"] = proc.stderr
    return payload


def collect_shell_blocks(text: str) -> list[tuple[int, str, str]]:
    blocks: list[tuple[int, str, str]] = []
    current_lang: str | None = None
    current_start: int | None = None
    current_lines: list[str] = []

    for lineno, line in enumerate(text.splitlines(), start=1):
        if current_lang is None:
            match = FENCE_RE.match(line)
            if match is None:
                continue
            info = match.group("info").strip()
            current_lang = info.split(maxsplit=1)[0].lower() if info else ""
            current_start = lineno + 1
            current_lines = []
            continue

        if line.strip() == "```":
            blocks.append((current_start or lineno, current_lang, "\n".join(current_lines)))
            current_lang = None
            current_start = None
            current_lines = []
            continue

        current_lines.append(line)

    return blocks


def lint_spec_file(spec_path: Path, *, min_like_len: int = 10) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    text = spec_path.read_text(encoding="utf-8")

    for lineno, line in enumerate(text.splitlines(), start=1):
        if MUSTMATCH_JSON_RE.search(line):
            findings.append(
                {
                    "line": lineno,
                    "rule": "invalid-mustmatch-mode",
                    "message": "uses unsupported `mustmatch json` syntax",
                    "text": line.strip(),
                }
            )
        match = SHORT_LIKE_RE.search(line)
        if match:
            literal = match.group(2) if match.group(2) is not None else match.group(3)
            if literal is not None and len(literal) < min_like_len:
                findings.append(
                    {
                        "line": lineno,
                        "rule": "short-like-pattern",
                        "message": f'uses short `mustmatch like` literal "{literal}" ({len(literal)} chars)',
                        "text": line.strip(),
                    }
                )

    for start_line, language, block in collect_shell_blocks(text):
        if language not in {"bash", "sh", "shell", "zsh"}:
            continue
        result = subprocess.run(
            ["bash", "-n"],
            input=block,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            findings.append(
                {
                    "line": start_line,
                    "rule": "invalid-shell-syntax",
                    "message": result.stderr.strip() or "bash -n failed",
                    "text": block.splitlines()[0] if block.splitlines() else "",
                }
            )

    return {
        "spec": str(spec_path),
        "finding_count": len(findings),
        "status": "fail" if findings else "pass",
        "findings": findings,
    }


root_dir = Path(sys.argv[1])
output_dir = Path(sys.argv[2])
spec_glob = sys.argv[3]
cli_file = Path(sys.argv[4])
shell_file = Path(sys.argv[5])
build_file = Path(sys.argv[6])
sources_dir = Path(sys.argv[7])
sources_mod = Path(sys.argv[8])
health_file = Path(sys.argv[9])

lint_out = output_dir / "quality-ratchet-lint.json"
mcp_out = output_dir / "quality-ratchet-mcp-allowlist.json"
source_out = output_dir / "quality-ratchet-source-registry.json"
summary_out = output_dir / "quality-ratchet-summary.json"

spec_paths = sorted(Path(path) for path in glob.glob(spec_glob))
lint_results: list[dict[str, object]] = []
lint_errors: list[str] = []

for spec_path in spec_paths:
    try:
        lint_results.append(lint_spec_file(spec_path.resolve()))
    except Exception as exc:  # noqa: BLE001
        lint_errors.append(f"{spec_path}: {exc}")

finding_count = sum(
    payload.get("finding_count", 0)
    for payload in lint_results
    if isinstance(payload.get("finding_count"), int)
)

if not spec_paths:
    lint_status = "error"
    lint_errors.append(f"no spec files matched {spec_glob!r}")
elif lint_errors:
    lint_status = "error"
elif finding_count:
    lint_status = "fail"
else:
    lint_status = "pass"

lint_payload = {
    "status": lint_status,
    "baseline_count": 0,
    "finding_count": finding_count,
    "files_checked": len(spec_paths),
    "results": lint_results,
    "errors": lint_errors,
}
write_json(lint_out, lint_payload)

mcp_payload = run_json_command(
    [
        "uv",
        "run",
        "--extra",
        "dev",
        "python",
        str(root_dir / "tools" / "check-mcp-allowlist.py"),
        "--cli-file",
        str(cli_file),
        "--shell-file",
        str(shell_file),
        "--build-file",
        str(build_file),
        "--json",
    ],
    allowed_exit_codes={0, 1},
)
write_json(mcp_out, mcp_payload)

source_payload = run_json_command(
    [
        "uv",
        "run",
        "--extra",
        "dev",
        "python",
        str(root_dir / "tools" / "check-source-registry.py"),
        "--sources-dir",
        str(sources_dir),
        "--sources-mod",
        str(sources_mod),
        "--health-file",
        str(health_file),
        "--json",
    ],
    allowed_exit_codes={0, 1},
)
write_json(source_out, source_payload)

statuses = [lint_payload["status"], mcp_payload.get("status"), source_payload.get("status")]
if "error" in statuses:
    summary_status = "error"
elif all(status == "pass" for status in statuses):
    summary_status = "pass"
else:
    summary_status = "fail"

summary_payload = {
    "status": summary_status,
    "lint": lint_payload,
    "mcp_allowlist": {"status": mcp_payload.get("status")},
    "source_registry": {"status": source_payload.get("status")},
}
write_json(summary_out, summary_payload)

raise SystemExit(0 if summary_status == "pass" else 1)
PY
