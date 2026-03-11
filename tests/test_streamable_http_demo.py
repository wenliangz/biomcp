from __future__ import annotations

import importlib.util
import json
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


class _FakeHealthResponse:
    def __init__(self, payload: dict[str, str]) -> None:
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> _FakeHealthResponse:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return self.payload


def test_parse_args_defaults_to_local_server_and_default_scenario() -> None:
    module = _load_demo_module()

    args = module.parse_args([])

    assert args.base_url == module.DEFAULT_BASE_URL
    assert args.scenario == "braf-melanoma"


def test_parse_args_accepts_base_url_and_named_scenario() -> None:
    module = _load_demo_module()

    args = module.parse_args(["--scenario", "braf-melanoma", "http://demo.test:9000"])

    assert args.base_url == "http://demo.test:9000"
    assert args.scenario == "braf-melanoma"


def test_parse_args_rejects_unknown_scenario(capsys: pytest.CaptureFixture[str]) -> None:
    module = _load_demo_module()

    with pytest.raises(SystemExit, match="2"):
        module.parse_args(["--scenario", "missing"])

    assert "invalid choice: 'missing'" in capsys.readouterr().err


def test_steps_for_returns_configured_scenario() -> None:
    module = _load_demo_module()

    assert module.steps_for("braf-melanoma") == module.SCENARIOS["braf-melanoma"]


def test_check_health_reports_success(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_demo_module()

    def fake_urlopen(url: str, *, timeout: int):
        assert url == "http://127.0.0.1:8080/health"
        assert timeout == module.HEALTH_TIMEOUT_SECONDS
        return _FakeHealthResponse({"status": "ok"})

    monkeypatch.setattr(module.urllib.request, "urlopen", fake_urlopen)

    module.check_health("http://127.0.0.1:8080")

    assert "Health check passed: http://127.0.0.1:8080/health" in capsys.readouterr().out


def test_check_health_exits_with_startup_guidance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_demo_module()

    def fake_urlopen(url: str, *, timeout: int):
        assert timeout == module.HEALTH_TIMEOUT_SECONDS
        raise module.urllib.error.URLError("connection refused")

    monkeypatch.setattr(module.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(SystemExit) as exc_info:
        module.check_health("http://127.0.0.1:8080")

    message = str(exc_info.value)
    assert "http://127.0.0.1:8080/health" in message
    assert "Start the server first" in message
    assert "biomcp serve-http --host 127.0.0.1 --port 8080" in message


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
