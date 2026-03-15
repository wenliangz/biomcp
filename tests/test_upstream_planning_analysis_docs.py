from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLANNING_ROOT = REPO_ROOT / "tests" / "fixtures" / "planning" / "biomcp"


def _read_repo(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _planning_root() -> Path:
    return Path(os.environ.get("BIOMCP_PLANNING_ROOT", DEFAULT_PLANNING_ROOT))


def _read_planning(path: str) -> str:
    return (_planning_root() / path).read_text(encoding="utf-8")


def _workflow_job_block(workflow: str, job_name: str) -> str:
    match = re.search(
        rf"^  {re.escape(job_name)}:\n(.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)",
        workflow,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, f"missing workflow job {job_name}"
    return match.group(1)


def _workflow_run_steps(job_block: str) -> list[str]:
    return re.findall(r"^\s+- run: (.+)$", job_block, flags=re.MULTILINE)


def test_planning_contract_uses_repo_fixture_fallback_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("BIOMCP_PLANNING_ROOT", raising=False)

    assert _planning_root() == DEFAULT_PLANNING_ROOT
    assert "# BioMCP Strategy" in _read_planning("strategy.md")


def test_planning_contract_reads_explicit_env_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("BIOMCP_PLANNING_ROOT", str(tmp_path))
    (tmp_path / "strategy.md").write_text("# override strategy\n", encoding="utf-8")

    assert _planning_root() == tmp_path
    assert _read_planning("strategy.md") == "# override strategy\n"


def test_planning_contract_bad_override_fails_loudly(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    missing_root = tmp_path / "missing-planning-root"
    monkeypatch.setenv("BIOMCP_PLANNING_ROOT", str(missing_root))

    with pytest.raises(FileNotFoundError):
        _read_planning("strategy.md")


def test_strategy_and_frontier_capture_upstream_planning_contract() -> None:
    strategy = _read_planning("strategy.md")
    frontier = _read_planning("frontier.md")

    assert "# BioMCP Strategy" in strategy
    assert "Rust core, Python packaging" in strategy
    assert "Rate limiting is process-local" in strategy
    assert "G002" in strategy
    assert "G003" in strategy
    assert len(strategy.splitlines()) <= 80

    assert "# BioMCP Frontier" in frontier
    assert "## G002" in frontier
    assert "## G003" in frontier
    assert "analysis/functional/overview.md" in frontier
    assert "analysis/technical/overview.md" in frontier
    assert "analysis/ux/cli-reference.md" in frontier
    assert "Harvest Guidance" in frontier


def test_functional_overview_preserves_readme_surface_and_study_family() -> None:
    functional = _read_repo("analysis/functional/overview.md")

    assert "# BioMCP Functional Overview" in functional
    assert "## Entity Surface" in functional
    for entity in (
        "| gene |",
        "| variant |",
        "| article |",
        "| trial |",
        "| drug |",
        "| disease |",
        "| pathway |",
        "| protein |",
        "| adverse-event |",
        "| pgx |",
        "| gwas |",
        "| phenotype |",
    ):
        assert entity in functional

    assert "## Study Command Family" in functional
    assert "`study` is a separate local analytics surface" in functional
    assert (
        "`biomcp study list|download|filter|query|co-occurrence|cohort|survival|compare`"
        in functional
    )
    assert "BioMCP ships an embedded agent guide" in functional
    assert "`biomcp skill` shows the BioMCP agent guide" in functional
    assert "`biomcp skill install <dir>` installs that guide" in functional
    assert "`biomcp skill list` is a legacy compatibility alias" in functional
    assert "`No skills found`" in functional
    assert "`biomcp skill 03` fail clearly" in functional
    assert "search all [slot filters]" in functional
    assert "biomcp search all --gene BRAF --disease melanoma" in functional
    assert "biomcp search all BRAF" in functional


def test_technical_and_ux_docs_match_current_cli_and_workflow_contracts() -> None:
    technical = _read_repo("analysis/technical/overview.md")
    ux = _read_repo("analysis/ux/cli-reference.md")

    assert "CI (`.github/workflows/ci.yml`) runs five parallel jobs" in technical
    assert "`check` (`cargo fmt --check`, `cargo clippy -- -D warnings`, `cargo test`)" in technical
    assert "`version-sync` (`bash scripts/check-version-sync.sh`)" in technical
    assert "`climb-hygiene` (`bash scripts/check-no-climb-tracked.sh`)" in technical
    assert '`contracts` (`uv sync --extra dev`, `uv run pytest tests/ -v --mcp-cmd "biomcp serve"`, `uv run mkdocs build --strict`)' in technical
    assert "`spec` (`cargo build --release --locked`, then `make spec`)" in technical
    assert "PR CI now runs `make spec` via the `spec` job in `.github/workflows/ci.yml`." in technical
    assert "Contract smoke checks run in `.github/workflows/contracts.yml`" in technical
    assert "release validation runs `pytest tests/` and `mkdocs build --strict`" in technical
    assert "Streamable HTTP" in technical
    assert "`/mcp`" in technical
    assert "`/health`" in technical
    assert "`/readyz`" in technical
    assert "connection line and `Command:` markers" in technical
    assert "through the remote" in technical
    assert "`biomcp` tool" in technical
    assert "remote `shell`" not in technical

    assert "`search all` Contract" in ux
    assert "typed slots first" in ux
    assert "biomcp search all --gene BRAF --disease melanoma" in ux
    assert 'biomcp search all --keyword "checkpoint inhibitor"' in ux
    assert "biomcp search all BRAF" in ux
    assert "positional alias" in ux
    assert "biomcp skill                  → show the embedded BioMCP agent guide" in ux
    assert "biomcp skill list             → legacy alias; currently reports no embedded catalog" in ux
    assert "Overview: `biomcp skill`" in ux
    assert "List: `biomcp skill list`" in ux
    assert "Legacy lookup: `biomcp skill 03` or `biomcp skill variant-to-treatment`" in ux
    assert "biomcp serve-http            → run the MCP Streamable HTTP server at `/mcp`" in ux
    assert "biomcp serve-sse             → removed compatibility command; use `biomcp serve-http`" in ux


def test_pull_request_contract_gate_matches_release_validation() -> None:
    ci = _read_repo(".github/workflows/ci.yml")
    release = _read_repo(".github/workflows/release.yml")
    contracts_smoke = _read_repo(".github/workflows/contracts.yml")
    expected_contract_runs = [
        "uv sync --extra dev",
        'uv run pytest tests/ -v --mcp-cmd "biomcp serve"',
        "uv run mkdocs build --strict",
    ]

    ci_contracts = _workflow_job_block(ci, "contracts")
    ci_spec = _workflow_job_block(ci, "spec")
    ci_version_sync = _workflow_job_block(ci, "version-sync")
    ci_climb_hygiene = _workflow_job_block(ci, "climb-hygiene")
    release_validate = _workflow_job_block(release, "validate")

    assert 'python-version: "3.12"' in ci_contracts
    assert 'python-version: "3.12"' in ci_spec
    assert 'python-version: "3.12"' in release_validate
    assert _workflow_run_steps(ci_contracts) == expected_contract_runs
    assert "- uses: actions/checkout@v4" in ci_spec
    assert "uses: arduino/setup-protoc@v3" in ci_spec
    assert "uses: dtolnay/rust-toolchain@stable" in ci_spec
    assert "uses: actions/setup-python@v5" in ci_spec
    assert "uses: astral-sh/setup-uv@v4" in ci_spec
    assert _workflow_run_steps(ci_spec) == [
        "cargo build --release --locked",
        "make spec",
    ]
    assert _workflow_run_steps(release_validate)[-3:] == expected_contract_runs
    assert "- uses: actions/checkout@v4" in ci_version_sync
    assert _workflow_run_steps(ci_version_sync) == [
        "bash scripts/check-version-sync.sh"
    ]
    for forbidden in (
        "setup-python",
        "setup-uv",
        "setup-protoc",
        "rust-toolchain",
        "cargo ",
        "uv sync",
        "python-version:",
    ):
        assert forbidden not in ci_version_sync
    assert "- uses: actions/checkout@v4" in ci_climb_hygiene
    assert _workflow_run_steps(ci_climb_hygiene) == [
        "bash scripts/check-no-climb-tracked.sh"
    ]
    for forbidden in (
        "setup-python",
        "setup-uv",
        "setup-protoc",
        "rust-toolchain",
        "cargo ",
        "uv sync",
        "python-version:",
    ):
        assert forbidden not in ci_climb_hygiene

    assert "name: Contract Smoke Tests" in contracts_smoke
    assert 'cron: "0 6 * * *"' in contracts_smoke
    assert "workflow_dispatch:" in contracts_smoke
    assert "continue-on-error: true" in contracts_smoke
    assert "- run: bash scripts/contract-smoke.sh" in contracts_smoke


def test_runtime_contract_docs_and_scripts_align_on_release_target() -> None:
    staging_demo = _read_repo("analysis/technical/staging-demo.md")
    runbook = _read_repo("RUN.md")
    technical = _read_repo("analysis/technical/overview.md")
    scripts_readme = _read_repo("scripts/README.md")
    source_contracts = _read_repo("scripts/source-contracts.md")
    contract_smoke = _read_repo("scripts/contract-smoke.sh")
    genegpt_demo = _read_repo("scripts/genegpt-demo.sh")
    geneagent_demo = _read_repo("scripts/geneagent-demo.sh")

    assert "# BioMCP Staging and Demo Contract" in staging_demo
    assert "./target/release/biomcp" in staging_demo
    assert "shared merged-main target" in staging_demo
    assert "BIOMCP_BIN=./target/release/biomcp ./scripts/genegpt-demo.sh" in staging_demo
    assert "BIOMCP_BIN=./target/release/biomcp ./scripts/geneagent-demo.sh" in staging_demo
    assert "./scripts/contract-smoke.sh --fast" in staging_demo
    assert 'uv run pytest tests/test_mcp_contract.py -v --mcp-cmd "./target/release/biomcp serve"' in staging_demo
    assert "ONCOKB_TOKEN" in staging_demo
    assert "./target/release/biomcp serve-http --host 127.0.0.1 --port 8080" in staging_demo
    assert "POST/GET /mcp" in staging_demo
    assert "GET /health" in staging_demo
    assert "GET /readyz" in staging_demo
    assert "GET /" in staging_demo
    assert "tests/test_mcp_http_transport.py" in staging_demo
    assert "S2_API_KEY" in staging_demo
    assert "article citations 22663011 --limit 3" in staging_demo

    assert "# BioMCP Runbook" in runbook
    assert "cargo build --release --locked" in runbook
    assert "./target/release/biomcp serve" in runbook
    assert "./target/release/biomcp serve-http --host 127.0.0.1 --port 8080" in runbook
    assert 'uv run pytest tests/test_mcp_contract.py -v --mcp-cmd "./target/release/biomcp serve"' in runbook
    assert "curl http://127.0.0.1:8080/health" in runbook
    assert "curl http://127.0.0.1:8080/readyz" in runbook
    assert "curl http://127.0.0.1:8080/" in runbook
    assert "tests/test_mcp_http_surface.py" in runbook
    assert "tests/test_mcp_http_transport.py" in runbook
    assert "make spec" in runbook
    assert "make test-contracts" in runbook
    assert "S2_API_KEY" in runbook
    assert "./target/release/biomcp article citations 22663011 --limit 3" in runbook
    assert "docs/user-guide/cli-reference.md" in runbook
    assert "docs/reference/mcp-server.md" in runbook

    assert "analysis/technical/staging-demo.md" in technical
    assert "RUN.md" in technical
    assert "S2_API_KEY" in technical
    assert "Semantic Scholar article enrichment/navigation" in technical
    assert "No `RUN.md` or staging-demo runbook exists" not in technical

    assert "current BioMCP operator command layer" in scripts_readme
    assert "source-facing contract probes" in scripts_readme
    assert "091 expansion scope" not in scripts_readme

    assert "# BioMCP Source Contract Probes" in source_contracts
    assert "source-facing API contract probes" in source_contracts
    assert "ONCOKB_TOKEN" in source_contracts
    assert "Semantic Scholar" in source_contracts
    assert "S2_API_KEY" in source_contracts
    assert "091 expansion scope" not in source_contracts

    assert "ONCOKB_TOKEN" in contract_smoke
    assert "ONCOKB_API_TOKEN" in contract_smoke
    assert "S2_API_KEY" in contract_smoke
    assert "Semantic Scholar" in contract_smoke
    assert "set ONCOKB_TOKEN to enable" in contract_smoke

    for demo_script in (genegpt_demo, geneagent_demo):
        assert 'BIN="${BIOMCP_BIN:-' in demo_script
        assert "$ROOT/target/release/biomcp" in demo_script
        assert "target/debug/biomcp" not in demo_script
        assert 'command -v biomcp >/dev/null 2>&1' in demo_script
