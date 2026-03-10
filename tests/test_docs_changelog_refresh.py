from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _markdown_section_block(text: str, heading: str) -> str:
    start = text.index(heading)
    remainder = text[start + len(heading) :]
    next_heading = remainder.find("\n## ")
    if next_heading == -1:
        return remainder
    return remainder[:next_heading]


def test_changelog_has_backfilled_releases_and_release_header() -> None:
    changelog = _read("CHANGELOG.md")

    assert "## [Unreleased]" not in changelog
    assert "## 0.8.14 — 2026-03-10" in changelog
    assert "## 0.9.0" not in changelog

    expected_releases = [
        ("0.8.14", "2026-03-10"),
        ("0.8.13", "2026-03-09"),
        ("0.8.12", "2026-03-07"),
        ("0.8.11", "2026-03-06"),
        ("0.8.10", "2026-03-04"),
        ("0.8.9", "2026-03-03"),
        ("0.8.8", "2026-03-02"),
        ("0.8.7", "2026-02-27"),
        ("0.8.6", "2026-02-27"),
        ("0.8.5", "2026-02-26"),
    ]
    for version, date in expected_releases:
        header = f"## {version} — {date}"
        assert header in changelog
        assert "\n- " in _markdown_section_block(changelog, header)


def test_remote_http_docs_are_promoted_for_newcomers() -> None:
    readme = _read("README.md")
    docs_index = _read("docs/index.md")
    mkdocs = _read("mkdocs.yml")
    remote_http = _read("docs/getting-started/remote-http.md")

    assert "### Remote HTTP server" in readme
    assert "biomcp serve-http --host 127.0.0.1 --port 8080" in readme
    assert "http://127.0.0.1:8080/mcp" in readme
    assert "demo/streamable_http_client.py" in readme
    assert "https://biomcp.org/getting-started/remote-http/" in readme
    assert readme.index("### Remote HTTP server") < readme.index(
        "## Multi-worker deployment"
    )

    assert "### Remote HTTP server" in docs_index
    assert "biomcp serve-http --host 127.0.0.1 --port 8080" in docs_index
    assert "http://127.0.0.1:8080/mcp" in docs_index
    assert "`/health`, `/readyz`, and `/`" in docs_index
    assert "getting-started/remote-http.md" in docs_index
    assert "demo/streamable_http_client.py" in docs_index

    assert "Remote HTTP Server: getting-started/remote-http.md" in mkdocs

    assert "# Remote Streamable HTTP Server" in remote_http
    assert "Use `biomcp serve-http` when you need one shared MCP server" in remote_http
    assert "Use `biomcp serve` when a single local client" in remote_http
    assert "biomcp serve-http --host 127.0.0.1 --port 8080" in remote_http
    assert "`/mcp`" in remote_http
    assert "`/health`" in remote_http
    assert "`/readyz`" in remote_http
    assert "streamable_http_client" in remote_http
    assert "terminate_on_close=False" in remote_http
    assert "demo/streamable_http_client.py" in remote_http


def test_streamable_http_demo_script_is_runnable_repo_artifact() -> None:
    demo_script = _read("demo/streamable_http_client.py")

    assert demo_script.startswith("#!/usr/bin/env -S uv run --script")
    assert '# requires-python = ">=3.11"' in demo_script
    assert '"mcp>=' in demo_script
    assert "biomcp serve-http --host 127.0.0.1 --port 8080" in demo_script
    assert "uv run --script demo/streamable_http_client.py" in demo_script
    assert 'DEFAULT_BASE_URL = "http://127.0.0.1:8080"' in demo_script
    assert 'mcp_url = f"{base_url.rstrip(\'/\')}/mcp"' in demo_script
    assert "terminate_on_close=False" in demo_script
    assert '"shell"' in demo_script
    assert '"biomcp version"' in demo_script


def test_release_overview_mentions_v0_8_14_streamable_http_release() -> None:
    overview = _read("analysis/technical/overview.md")

    assert "**Current version:** 0.8.14 (as of 2026-03-10)" in overview


def test_gene_guide_includes_new_sections_and_positional_search() -> None:
    gene_guide = _read("docs/user-guide/gene.md")

    assert "biomcp search gene BRAF --limit 5" in gene_guide
    assert "biomcp get gene BRAF expression" in gene_guide
    assert "biomcp get gene BRAF druggability" in gene_guide
    assert "biomcp get gene BRAF clingen" in gene_guide


def test_article_guide_documents_federated_search_and_source_flag() -> None:
    article_guide = _read("docs/user-guide/article.md")

    assert "PubTator3 and Europe PMC" in article_guide
    assert "deduplicated by PMID" in article_guide
    assert "--source pubtator" in article_guide
    assert "--source europepmc" in article_guide


def test_data_sources_reference_covers_new_gene_and_article_sources() -> None:
    data_sources = _read("docs/reference/data-sources.md")

    assert "UniProt, QuickGO, STRING, GTEx, DGIdb, ClinGen" in data_sources
    assert "https://gtexportal.org/api/v2" in data_sources
    assert "https://dgidb.org/api/graphql" in data_sources
    assert "https://search.clinicalgenome.org" in data_sources
    assert "| Article search & metadata | PubTator3 + Europe PMC |" in data_sources
    assert "PubTator3 + Europe PMC for federated search" in data_sources


def test_cli_and_quick_reference_cover_search_all_and_gene_sections() -> None:
    cli_reference = _read("docs/user-guide/cli-reference.md")
    quick_reference = _read("docs/reference/quick-reference.md")

    assert "### All (cross-entity)" in cli_reference
    assert "biomcp search all --gene BRAF --disease melanoma" in cli_reference
    assert "biomcp get gene BRAF pathways ontology diseases protein" in cli_reference
    assert (
        "biomcp get gene BRAF go interactions civic expression druggability clingen"
        in cli_reference
    )
    assert "biomcp get gene BRAF all" in cli_reference
    assert "_meta.evidence_urls" in cli_reference
    assert "Ensembl, OMIM, NCBI Gene, and UniProt URLs." in cli_reference

    assert "biomcp search gene BRAF --limit 5" in quick_reference
    assert "biomcp search all --gene BRAF --disease melanoma" in quick_reference
    assert "biomcp search all --keyword resistance --counts-only" in quick_reference


def test_public_docs_surface_local_study_analytics() -> None:
    readme = _read("README.md")
    quick_reference = _read("docs/reference/quick-reference.md")
    cli_reference = _read("docs/user-guide/cli-reference.md")
    study_commands = [
        "biomcp study list",
        "biomcp study download [--list] [<study_id>]",
        "biomcp study filter --study <id> [--mutated <symbol>] [--amplified <symbol>] [--deleted <symbol>] [--expression-above <gene:threshold>] [--expression-below <gene:threshold>] [--cancer-type <type>]",
        "biomcp study query --study <id> --gene <symbol> --type <mutations|cna|expression>",
        "biomcp study cohort --study <id> --gene <symbol>",
        "biomcp study survival --study <id> --gene <symbol> [--endpoint <os|dfs|pfs|dss>]",
        "biomcp study compare --study <id> --gene <symbol> --type <expression|mutations> --target <symbol>",
        "biomcp study co-occurrence --study <id> --genes <g1,g2,...>",
    ]

    assert "plus local study analytics" in readme
    assert "## Local study analytics" in readme
    assert "12 remote entity commands" in readme
    assert "study download" in readme

    assert "## Study commands" in quick_reference
    assert "local downloaded cBioPortal-style datasets" in quick_reference
    assert "BIOMCP_STUDY_DIR" in quick_reference
    for command in study_commands:
        assert command in quick_reference

    assert "## Local study analytics" in cli_reference
    assert "BIOMCP_STUDY_DIR" in cli_reference
    assert "local cBioPortal analytics family for downloaded" in cli_reference
    assert "cBioPortal-style datasets" in cli_reference
    assert "12 remote entity commands" in cli_reference
    assert "data_mutations.txt" in cli_reference
    assert "data_clinical_patient.txt" in cli_reference
    for command in study_commands:
        assert command in cli_reference
