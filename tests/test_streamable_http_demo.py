from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_PATH = REPO_ROOT / "demo/streamable_http_client.py"


def _load_demo_module():
    spec = importlib.util.spec_from_file_location("streamable_http_client_demo", DEMO_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_selected_steps_returns_configured_scenario() -> None:
    module = _load_demo_module()

    assert module.selected_steps() == module.SCENARIOS["braf-melanoma"]


def test_selected_steps_rejects_unknown_scenario(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_demo_module()
    monkeypatch.setattr(module, "SCENARIO", "missing")

    with pytest.raises(
        SystemExit,
        match="Unknown demo scenario 'missing'. Available scenarios: braf-melanoma",
    ):
        module.selected_steps()


def test_demo_python_floor_matches_syntax() -> None:
    source = DEMO_PATH.read_text()

    meta_match = re.search(r'requires-python\s*=\s*"([^"]+)"', source)
    assert meta_match, "requires-python not found in demo inline metadata"
    spec_str = meta_match.group(1)

    version_match = re.search(r">=(\d+)\.(\d+)", spec_str)
    assert version_match, f"Unrecognised requires-python spec: {spec_str!r}"
    min_version = (int(version_match.group(1)), int(version_match.group(2)))

    pep695 = re.compile(r"^\s*type\s+[A-Za-z_]\w*\s*=", re.MULTILINE)
    hits = pep695.findall(source)
    if min_version < (3, 12):
        assert not hits, (
            f"Demo declares requires-python={spec_str!r} (floor < 3.12) "
            f"but contains PEP 695 'type' statement(s): {hits}"
        )
