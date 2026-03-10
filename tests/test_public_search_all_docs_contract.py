from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _markdown_section_block(text: str, heading: str, next_heading: str) -> str:
    start = text.index(heading)
    remainder = text[start + len(heading) :]
    end = remainder.find(next_heading)
    if end == -1:
        return remainder
    return remainder[:end]


def test_readme_teaches_search_all_as_unified_entry_point() -> None:
    readme = _read("README.md")
    quick_start = _markdown_section_block(
        readme,
        "## Quick start",
        "\n## Command grammar",
    )
    grammar = _markdown_section_block(
        readme,
        "## Command grammar",
        "\n## Entities and sources",
    )

    assert "biomcp list gene" in quick_start
    assert (
        "biomcp search all --gene BRAF --disease melanoma  "
        "# unified cross-entity discovery"
    ) in quick_start
    assert quick_start.index("biomcp list gene") < quick_start.index(
        "biomcp search all --gene BRAF --disease melanoma"
    )

    assert "batch <entity> <id1,id2,...> → parallel gets" in grammar
    assert "search all [slot filters]    → unified fan-out across all entities" in grammar
    assert grammar.index("batch <entity> <id1,id2,...> → parallel gets") < grammar.index(
        "search all [slot filters]    → unified fan-out across all entities"
    )


def test_docs_index_teaches_search_all_as_unified_entry_point() -> None:
    docs_index = _read("docs/index.md")
    quick_start = _markdown_section_block(
        docs_index,
        "## Quick start",
        "\n## Command grammar",
    )
    grammar = _markdown_section_block(
        docs_index,
        "## Command grammar",
        "\n## Entities and sources",
    )

    assert "biomcp list gene" in quick_start
    assert (
        "biomcp search all --gene BRAF --disease melanoma  "
        "# unified cross-entity discovery"
    ) in quick_start
    assert quick_start.index("biomcp list gene") < quick_start.index(
        "biomcp search all --gene BRAF --disease melanoma"
    )

    assert "batch <entity> <id1,id2,...> → parallel gets" in grammar
    assert "search all [slot filters]    → unified fan-out across all entities" in grammar
    assert grammar.index("batch <entity> <id1,id2,...> → parallel gets") < grammar.index(
        "search all [slot filters]    → unified fan-out across all entities"
    )
