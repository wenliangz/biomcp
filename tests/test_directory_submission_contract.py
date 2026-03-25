from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EXAMPLE_MARKERS = (
    "**User prompt:**",
    "**Expected tool call:**",
    "**Expected behavior:**",
    "**Expected output:**",
)


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _read_json(path: str) -> dict[str, object]:
    return json.loads(_read(path))


def _markdown_section_block(text: str, heading: str, next_heading: str) -> str:
    start = text.index(heading)
    remainder = text[start + len(heading) :]
    end = remainder.find(next_heading)
    if end == -1:
        return remainder
    return remainder[:end]


def test_manifest_matches_directory_bundle_contract() -> None:
    manifest = _read_json("manifest.json")
    cargo = tomllib.loads(_read("Cargo.toml"))
    pyproject = tomllib.loads(_read("pyproject.toml"))

    assert manifest["manifest_version"] == "0.3"
    assert manifest["name"] == "biomcp"
    assert manifest["display_name"] == "BioMCP"
    assert manifest["version"] == cargo["package"]["version"]
    assert manifest["version"] == pyproject["project"]["version"]
    assert manifest["privacy_policies"] == ["https://biomcp.org/policies/"]
    assert "tools_generated" not in manifest

    server = manifest["server"]
    assert isinstance(server, dict)
    assert server["type"] == "binary"
    assert server["entry_point"] == "server/biomcp"

    mcp_config = server["mcp_config"]
    assert isinstance(mcp_config, dict)
    assert mcp_config["command"] == "server/biomcp"
    assert mcp_config["args"] == ["serve"]
    assert mcp_config["env"] == {
        "ONCOKB_TOKEN": "${user_config.oncokb_token}",
        "DISGENET_API_KEY": "${user_config.disgenet_api_key}",
        "S2_API_KEY": "${user_config.s2_api_key}",
    }

    tools = manifest["tools"]
    assert isinstance(tools, list)
    assert len(tools) == 1
    assert tools[0]["name"] == "biomcp"
    assert "read-only" in str(tools[0]["description"]).lower()
    assert "ONCOKB_API_KEY" not in json.dumps(manifest)

    compatibility = manifest["compatibility"]
    assert isinstance(compatibility, dict)
    assert sorted(compatibility["platforms"]) == ["darwin", "win32"]


def test_packaging_workspace_is_ignored_and_bundle_payload_is_filtered() -> None:
    mcpbignore = _read(".mcpbignore")

    for entry in (
        ".git/",
        ".march/",
        "src/",
        "tests/",
        "docs/",
        "spec/",
        "target/",
        "dist/",
        "*.md",
    ):
        assert entry in mcpbignore

    gitignore = _read(".gitignore")
    assert "/server/" in gitignore


def test_readme_is_directory_review_complete() -> None:
    readme = _read("README.md")

    required_sections = [
        "## Description",
        "## Features",
        "## Installation",
        "## Configuration",
        "## Usage Examples",
        "## Privacy Policy",
        "## Support",
        "## Documentation",
        "## Citation",
        "## Data Sources and Licensing",
        "## License",
    ]
    positions = [readme.index(section) for section in required_sections]
    assert positions == sorted(positions)

    installation = _markdown_section_block(readme, "## Installation", "\n## Quick start")
    assert "### Claude Desktop extension (.mcpb)" in installation
    assert "Anthropic Directory" in installation

    configuration = _markdown_section_block(
        readme,
        "## Configuration",
        "\n## Usage Examples",
    )
    assert "### Claude Desktop extension settings" in configuration
    for label, env_var in (
        ("OncoKB Token", "ONCOKB_TOKEN"),
        ("DisGeNET API Key", "DISGENET_API_KEY"),
        ("Semantic Scholar API Key", "S2_API_KEY"),
    ):
        assert label in configuration
        assert env_var in configuration
    assert "first directory build exposes only those three optional settings" in (
        configuration.lower()
    )

    examples = _markdown_section_block(readme, "## Usage Examples", "\n## Privacy Policy")
    assert examples.count("**User prompt:**") >= 4
    assert examples.count("**Expected tool call:**") >= 4
    assert examples.count("**Expected behavior:**") >= 4
    assert examples.count("**Expected output:**") >= 4
    for prompt, call in (
        (
            "Give me a low-noise overview of BRAF in melanoma.",
            "biomcp search all --gene BRAF --disease melanoma --counts-only",
        ),
        (
            "Summarize ClinVar significance and population frequency for BRAF V600E.",
            'biomcp get variant "BRAF V600E" clinvar population',
        ),
        (
            "Show OncoKB therapy evidence for BRAF V600E.",
            'biomcp variant oncokb "BRAF V600E"',
        ),
        (
            "Show scored DisGeNET associations for TP53.",
            "biomcp get gene TP53 disgenet",
        ),
    ):
        assert prompt in examples
        assert call in examples

    example_blocks = [
        block.strip()
        for block in re.split(r"(?m)^### ", examples)
        if block.strip()
    ]
    complete_examples = [
        block
        for block in example_blocks
        if all(marker in block for marker in REQUIRED_EXAMPLE_MARKERS)
    ]
    assert len(complete_examples) >= 4

    privacy = _markdown_section_block(readme, "## Privacy Policy", "\n## Support")
    assert "https://biomcp.org/policies/" in privacy

    support = _markdown_section_block(readme, "## Support", "\n## Documentation")
    assert "github.com/genomoncology/biomcp/issues" in support
    assert "docs/troubleshooting.md" in support


def test_policies_page_covers_directory_privacy_requirements() -> None:
    policies = _read("docs/policies.md")
    lowered = policies.lower()

    assert "# privacy policy" in lowered
    assert "telemetry" in lowered
    assert "anthropic" in lowered
    assert "claude" in lowered
    assert "upstream providers" in lowered or "third-party providers" in lowered
    assert "retention" in lowered
    assert "api keys" in lowered
    assert "read-only" in lowered
    assert "privacy@" in lowered or "contact" in lowered
    assert "source licensing reference" in lowered
    assert "clinical" in lowered


def test_release_workflow_updates_manifest_version_for_release_builds() -> None:
    release = _read(".github/workflows/release.yml")

    assert "Sync Cargo.toml and manifest.json version from release tag" in release
    assert (
        "Sync Cargo.toml, pyproject.toml, and manifest.json version from release tag"
        in release
    )
    assert release.count("manifest.json") >= 4
