from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

OVERVIEW_FILE = "index.md"

SOURCE_PAGE_SPECS = {
    "pubmed.md": {
        "title": "PubMed MCP Tool for AI Agents | BioMCP",
        "description": "Search PubMed in BioMCP with PubTator3 annotations, article summaries, and PMC full-text handoff so AI agents can review literature faster.",
        "api_access": "Optional `NCBI_API_KEY` for higher NCBI throughput.",
        "provider_key_url": "https://www.ncbi.nlm.nih.gov/account/settings/",
        "official_url": "https://pubmed.ncbi.nlm.nih.gov/",
        "required_intro_phrases": [
            '"PubMed" is an umbrella label',
            "PubTator3",
            "Europe PMC",
            "PMC OA",
            "NCBI ID Converter",
            "Semantic Scholar",
        ],
        "exposes": [
            "search article",
            "get article <id>",
            "get article <id> annotations",
            "get article <id> fulltext",
            "article entities <pmid>",
        ],
        "example_commands": [
            "biomcp search article -g BRAF --limit 3",
            "biomcp get article 22663011",
            "biomcp get article 22663011 annotations",
            "biomcp article entities 22663011",
            "biomcp get article 27083046 fulltext",
        ],
    },
    "clinicaltrials-gov.md": {
        "title": "ClinicalTrials.gov MCP Tool for AI Agents | BioMCP",
        "description": "Search ClinicalTrials.gov from BioMCP for recruiting studies, eligibility criteria, locations, and trial details without learning the native API.",
        "api_access": "No BioMCP API key required.",
        "official_url": "https://clinicaltrials.gov/",
        "required_intro_phrases": [
            "default trial backend",
            "`--source nci`",
        ],
        "exposes": [
            "search trial",
            "get trial <nct_id>",
            "get trial <nct_id> eligibility",
            "get trial <nct_id> locations",
            "get trial <nct_id> outcomes",
            "get trial <nct_id> arms",
            "get trial <nct_id> references",
        ],
        "example_commands": [
            'biomcp search trial -c melanoma --status recruiting --limit 3',
            'biomcp search trial -c melanoma --mutation "BRAF V600E" --limit 3',
            "biomcp get trial NCT02576665",
            "biomcp get trial NCT02576665 eligibility",
            "biomcp get trial NCT02576665 locations --limit 3",
        ],
    },
    "clinvar.md": {
        "title": "ClinVar MCP Tool for Variant Interpretation | BioMCP",
        "description": "Use BioMCP to pull ClinVar clinical significance, review status, and disease context for human variants through one variant lookup workflow.",
        "api_access": "No standalone BioMCP key path; ClinVar content is surfaced indirectly via MyVariant.info.",
        "official_url": "https://www.ncbi.nlm.nih.gov/clinvar/",
        "required_intro_phrases": [
            "indirect-only",
            "MyVariant.info",
            "does not act as a direct ClinVar API client",
        ],
        "exposes": [
            "get variant <id>",
            "get variant <id> clinvar",
            "search variant -g <gene> --significance <value>",
        ],
        "example_commands": [
            "biomcp get variant rs113488022",
            "biomcp get variant rs113488022 clinvar",
            'biomcp get variant "BRAF V600E" clinvar',
            "biomcp search variant -g BRCA1 --significance pathogenic --limit 5",
        ],
    },
    "openfda.md": {
        "title": "OpenFDA MCP Tool for Drug Safety Workflows | BioMCP",
        "description": "Use BioMCP to query OpenFDA adverse events, recalls, device reports, labels, and approval context for drug safety and surveillance workflows.",
        "api_access": "Optional `OPENFDA_API_KEY` for higher quota headroom.",
        "provider_key_url": "https://open.fda.gov/apis/authentication/",
        "official_url": "https://open.fda.gov/",
        "required_intro_phrases": [
            "FAERS",
            "MAUDE",
            "shortages",
            "Drugs@FDA-derived",
        ],
        "exposes": [
            "search adverse-event --drug <name>",
            "search adverse-event --type recall --drug <name>",
            "search adverse-event --type device --device <name>",
            "get adverse-event <report_id>",
            "get drug <name> label",
            "get drug <name> shortage",
            "get drug <name> approvals",
            "get drug <name> interactions",
            "get drug <name> safety --region us",
        ],
        "example_commands": [
            "biomcp search adverse-event --drug pembrolizumab --limit 3",
            "biomcp search adverse-event --type recall --drug metformin --limit 3",
            'biomcp search adverse-event --type device --device "insulin pump" --limit 3',
            "biomcp get drug vemurafenib label",
            "biomcp get drug dabrafenib approvals",
        ],
    },
    "uniprot.md": {
        "title": "UniProt MCP Tool for Protein Data | BioMCP",
        "description": "Use BioMCP to search UniProt proteins, fetch canonical protein cards, and surface structure-linked context for AI agents and research workflows.",
        "api_access": "No BioMCP API key required.",
        "official_url": "https://www.uniprot.org/",
        "required_intro_phrases": [
            "gene `protein` section",
            "Domains, interactions, and complexes are separate provider sections",
            "PDB",
            "AlphaFold",
        ],
        "exposes": [
            "search protein",
            "get protein <accession_or_symbol>",
            "get gene <symbol> protein",
            "get protein <accession> structures",
        ],
        "example_commands": [
            "biomcp search protein BRAF --limit 3",
            "biomcp get protein P15056",
            "biomcp get gene BRAF protein",
            "biomcp get protein P15056 structures",
        ],
    },
    "gnomad.md": {
        "title": "gnomAD MCP Tool for Variant Frequency Analysis | BioMCP",
        "description": "Use BioMCP to pull gnomAD population frequencies and gene constraint metrics for variant interpretation, rarity checks, and gene-level context.",
        "api_access": "No BioMCP API key required.",
        "official_url": "https://gnomad.broadinstitute.org/",
        "required_intro_phrases": [
            "gene constraint comes from the gnomAD source path directly",
            "MyVariant.info payloads",
        ],
        "exposes": [
            "get gene <symbol> constraint",
            "get variant <id> population",
            "search variant -g <gene> --max-frequency <value>",
        ],
        "example_commands": [
            "biomcp get gene BRAF constraint",
            "biomcp get variant rs113488022 population",
            'biomcp get variant "chr7:g.140453136A>T" population',
            "biomcp search variant -g BRCA1 --max-frequency 0.01 --limit 5",
        ],
    },
    "reactome.md": {
        "title": "Reactome MCP Tool for Pathway Analysis | BioMCP",
        "description": "Use BioMCP to search Reactome pathways, inspect pathway genes and events, and connect pathway context to downstream trial and article workflows.",
        "api_access": "No BioMCP API key required.",
        "official_url": "https://reactome.org/",
        "required_intro_phrases": [
            "multi-source across Reactome, KEGG, and WikiPathways",
            "Top-level `biomcp enrich` is a g:Profiler workflow",
            "Reactome-gated enrichment",
        ],
        "exposes": [
            "search pathway",
            "get pathway <id>",
            "get pathway <id> genes",
            "get pathway <id> events",
            "get pathway <id> enrichment",
            "get gene <symbol> pathways",
        ],
        "example_commands": [
            'biomcp search pathway "MAPK signaling" --limit 5',
            "biomcp get pathway R-HSA-5673001",
            "biomcp get pathway R-HSA-5673001 genes",
            "biomcp get pathway R-HSA-5673001 events",
            "biomcp get gene BRAF pathways",
        ],
    },
    "semantic-scholar.md": {
        "title": "Semantic Scholar MCP Tool for Citation Graphs | BioMCP",
        "description": "Use BioMCP to add Semantic Scholar TLDRs, citations, references, and recommendations to literature-review workflows for AI agents.",
        "api_access": "Optional `S2_API_KEY` for dedicated quota and higher reliability.",
        "provider_key_url": "https://www.semanticscholar.org/product/api",
        "official_url": "https://www.semanticscholar.org/",
        "required_intro_phrases": [
            "`search article` does not expose `--source semantic-scholar`",
            "automatic optional search leg",
            "article citations",
            "article references",
            "article recommendations",
        ],
        "exposes": [
            "search article",
            "get article <id> tldr",
            "article citations <id>",
            "article references <id>",
            "article recommendations <id>",
        ],
        "example_commands": [
            "biomcp get article 22663011 tldr",
            "biomcp article citations 22663011 --limit 3",
            "biomcp article references 22663011 --limit 3",
            "biomcp article recommendations 22663011 --limit 3",
        ],
    },
}

EXPECTED_SOURCE_FILES = [OVERVIEW_FILE, *SOURCE_PAGE_SPECS]

EXPECTED_NAV_BLOCK = """  - Sources:
      - Overview: sources/index.md
      - PubMed: sources/pubmed.md
      - ClinicalTrials.gov: sources/clinicaltrials-gov.md
      - ClinVar: sources/clinvar.md
      - OpenFDA: sources/openfda.md
      - UniProt: sources/uniprot.md
      - gnomAD: sources/gnomad.md
      - Reactome: sources/reactome.md
      - Semantic Scholar: sources/semantic-scholar.md
"""


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _read_source_page(filename: str) -> str:
    return _read(f"docs/sources/{filename}")


def _front_matter_value(text: str, field: str) -> str:
    match = re.search(rf"(?ms)\A---\n.*?^{field}: \"([^\"]+)\"\n.*?^---\n", text)
    assert match, f"missing front matter field {field!r}"
    return match.group(1)


def _markdown_section_block(text: str, heading: str, next_heading: str) -> str:
    start = text.index(heading)
    remainder = text[start + len(heading) :]
    end = remainder.find(next_heading)
    if end == -1:
        return remainder
    return remainder[:end]


def _source_intro_block(text: str) -> str:
    title_end = text.index("\n", text.index("\n# ") + 1)
    return text[title_end + 1 : text.index("\n## What BioMCP exposes")]


def _source_table_block(text: str) -> str:
    return _markdown_section_block(
        text,
        "## What BioMCP exposes\n",
        "\n## Example commands",
    )


def test_docs_sources_directory_has_expected_file_set() -> None:
    actual = sorted(path.name for path in (REPO_ROOT / "docs" / "sources").glob("*.md"))
    assert actual == sorted(EXPECTED_SOURCE_FILES)


def test_mkdocs_nav_contains_sources_section_between_user_guide_and_how_to() -> None:
    mkdocs = _read("mkdocs.yml")
    section = _markdown_section_block(
        mkdocs,
        "  - User Guide:\n",
        "  - How-To:\n",
    )

    assert EXPECTED_NAV_BLOCK in mkdocs
    assert "  - Sources:\n" in section


def test_sources_overview_page_has_required_metadata_and_links() -> None:
    overview = _read_source_page(OVERVIEW_FILE)

    assert (
        _front_matter_value(overview, "title")
        == "Biomedical Data Sources for AI Agents | BioMCP"
    )
    assert (
        _front_matter_value(overview, "description")
        == "Explore BioMCP source guides for PubMed, ClinicalTrials.gov, ClinVar, OpenFDA, UniProt, gnomAD, Reactome, and Semantic Scholar."
    )

    assert "# Biomedical Data Sources for AI Agents" in overview
    assert "User Guide" in overview
    assert "Sources" in overview
    assert "[Data Sources](../reference/data-sources.md)" in overview
    assert "[Source Licensing and Terms](../reference/source-licensing.md)" in overview
    assert "[API Keys](../getting-started/api-keys.md)" in overview
    assert "## Example commands" not in overview
    assert "```bash" not in overview

    for filename in SOURCE_PAGE_SPECS:
        assert f"]({filename})" in overview


def test_each_source_page_has_required_front_matter_headings_intro_and_examples() -> None:
    for filename, spec in SOURCE_PAGE_SPECS.items():
        page = _read_source_page(filename)

        assert _front_matter_value(page, "title") == spec["title"]
        assert _front_matter_value(page, "description") == spec["description"]

        for heading in (
            "## What BioMCP exposes",
            "## Example commands",
            "## API access",
            "## Official source",
            "## Related docs",
        ):
            assert heading in page, f"{filename} missing heading {heading!r}"

        intro = _source_intro_block(page)
        for phrase in spec["required_intro_phrases"]:
            assert phrase in intro, f"{filename} missing intro phrase {phrase!r}"

        examples = _markdown_section_block(page, "## Example commands\n", "\n## API access")
        command_count = len(re.findall(r"(?m)^biomcp ", examples))
        assert command_count == len(spec["example_commands"])
        assert 3 <= command_count <= 5, f"{filename} has {command_count} example commands"

        for command in spec["example_commands"]:
            assert command in examples, f"{filename} missing example {command!r}"


def test_each_source_page_includes_expected_surface_auth_and_official_link() -> None:
    for filename, spec in SOURCE_PAGE_SPECS.items():
        page = _read_source_page(filename)
        source_table = _source_table_block(page)

        assert spec["api_access"] in page
        assert spec["official_url"] in page

        for command in spec["exposes"]:
            assert command in source_table, f"{filename} missing source surface {command!r}"


def test_optional_key_pages_link_api_keys_guide() -> None:
    for filename in ("pubmed.md", "openfda.md", "semantic-scholar.md"):
        page = _read_source_page(filename)
        assert "[API Keys](../getting-started/api-keys.md)" in page


def test_optional_key_pages_link_their_provider_key_pages() -> None:
    for filename, spec in SOURCE_PAGE_SPECS.items():
        provider_key_url = spec.get("provider_key_url")
        if provider_key_url is None:
            continue

        page = _read_source_page(filename)
        assert provider_key_url in page
