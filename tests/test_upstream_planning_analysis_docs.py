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
