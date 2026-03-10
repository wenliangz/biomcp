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


def test_installation_doc_covers_pypi_package_and_command_contract() -> None:
    installation = _read("docs/getting-started/installation.md")

    assert "## Option 1: PyPI package" in installation
    assert "## Option 2: Installer script" in installation
    assert "## Option 3: Source build" in installation
    assert installation.index("## Option 1: PyPI package") < installation.index(
        "## Option 2: Installer script"
    )

    pypi_block = _markdown_section_block(
        installation,
        "## Option 1: PyPI package",
        "\n## Option 2: Installer script",
    )
    assert "uv tool install biomcp-cli" in pypi_block
    assert "pip install biomcp-cli" in pypi_block
    assert "Install the `biomcp-cli` package, then use the `biomcp` command" in pypi_block
    assert "biomcp --version" in pypi_block


def test_docs_index_lists_pypi_install_before_binary_install() -> None:
    docs_index = _read("docs/index.md")

    assert "### PyPI tool install" in docs_index
    assert "### Binary install" in docs_index
    assert docs_index.index("### PyPI tool install") < docs_index.index(
        "### Binary install"
    )
    assert "uv tool install biomcp-cli" in docs_index
    assert "pip install biomcp-cli" in docs_index
    assert "Install the `biomcp-cli` package, then use `biomcp`" in docs_index
