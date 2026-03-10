from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PLANNING_ROOT = Path("/home/ian/workspace/planning/teams/biomcp")


def _read_repo(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _read_planning(path: str) -> str:
    return (PLANNING_ROOT / path).read_text(encoding="utf-8")


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

    assert "CI (`.github/workflows/ci.yml`) runs `cargo fmt --check`, `cargo clippy -- -D warnings`, and `cargo test`." in technical
    assert "The spec suite is repo-local executable documentation; no GitHub workflow currently runs `make spec`." in technical
    assert "Contract smoke checks run in `.github/workflows/contracts.yml`" in technical
    assert "release validation runs `pytest tests/` and `mkdocs build --strict`" in technical
    assert "Streamable HTTP" in technical
    assert "`/mcp`" in technical
    assert "`/health`" in technical
    assert "`/readyz`" in technical

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
    assert "docs/user-guide/cli-reference.md" in runbook
    assert "docs/reference/mcp-server.md" in runbook

    assert "analysis/technical/staging-demo.md" in technical
    assert "RUN.md" in technical
    assert "No `RUN.md` or staging-demo runbook exists" not in technical

    assert "current BioMCP operator command layer" in scripts_readme
    assert "source-facing contract probes" in scripts_readme
    assert "091 expansion scope" not in scripts_readme

    assert "# BioMCP Source Contract Probes" in source_contracts
    assert "source-facing API contract probes" in source_contracts
    assert "ONCOKB_TOKEN" in source_contracts
    assert "091 expansion scope" not in source_contracts

    assert "ONCOKB_TOKEN" in contract_smoke
    assert "ONCOKB_API_TOKEN" in contract_smoke
    assert "set ONCOKB_TOKEN to enable" in contract_smoke

    for demo_script in (genegpt_demo, geneagent_demo):
        assert 'BIN="${BIOMCP_BIN:-' in demo_script
        assert "$ROOT/target/release/biomcp" in demo_script
        assert "target/debug/biomcp" not in demo_script
        assert 'command -v biomcp >/dev/null 2>&1' in demo_script
