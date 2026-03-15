from __future__ import annotations

import os

import pytest

OPENFDA_SPEC_NODEIDS = {
    "spec/05-drug.md::Drug to Adverse Events",
    "spec/05-drug.md::Adverse Event Search",
    "spec/17-cross-entity-pivots.md::Drug to Adverse Events",
    "spec/11-evidence-urls.md::Markdown Evidence Links",
    "spec/11-evidence-urls.md::JSON Metadata Contract",
    "spec/12-search-positionals.md::Adverse-event Positional Query",
}


def _has_openfda_api_key() -> bool:
    return bool(os.environ.get("OPENFDA_API_KEY", "").strip())


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    del config

    openfda_skip = None
    if not _has_openfda_api_key():
        openfda_skip = pytest.mark.skip(
            reason=(
                "requires OPENFDA_API_KEY for stable live-spec quota against OpenFDA"
            )
        )

    for item in items:
        if openfda_skip and any(
            item.nodeid.startswith(nodeid) for nodeid in OPENFDA_SPEC_NODEIDS
        ):
            item.add_marker(openfda_skip)
