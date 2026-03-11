# Design: P042 — Fix Planning Docs CI Path Regression

## Problem

`tests/test_upstream_planning_analysis_docs.py::test_strategy_and_frontier_capture_upstream_planning_contract`
previously read BioMCP planning files from Ian-local absolute paths under
`/home/ian/workspace/planning/teams/biomcp/`. That path does not exist on
GitHub Actions runners, so the test failed with `FileNotFoundError` for the
wrong reason.

## Verified Repo State

Commit `a7db639` in this worktree already contains the implementation under
review. The current code does the following:

1. `tests/test_upstream_planning_analysis_docs.py` resolves `PLANNING_ROOT`
   from `BIOMCP_PLANNING_ROOT` and otherwise falls back to the repo-local path
   `REPO_ROOT / "tests" / "fixtures" / "planning" / "biomcp"`.
2. `_read_planning()` reads `strategy.md` and `frontier.md` from that resolved
   root with no skip/fallback branching beyond the explicit env override.
   If a caller points `BIOMCP_PLANNING_ROOT` at a bad location, the test still
   fails loudly with `FileNotFoundError`.
3. `tests/fixtures/planning/biomcp/strategy.md` and `frontier.md` exist in the
   repo and satisfy the current assertions. The strategy fixture is 49 lines,
   which preserves the `<= 80` line-count contract asserted by the test.
4. No hardcoded `/home/ian/workspace/...` path remains anywhere in
   `tests/test_upstream_planning_analysis_docs.py`.
5. No GitHub Actions workflow sets `BIOMCP_PLANNING_ROOT`. The relevant
   workflow path is `.github/workflows/release.yml`, whose `validate` job runs
   `uv run pytest tests/ -v --mcp-cmd "biomcp serve"` on a clean checkout, so
   GitHub Actions will exercise the repo-local fixture fallback. `.github/workflows/ci.yml`
   only runs Rust checks, and `.github/workflows/contracts.yml` runs the shell
   smoke script rather than pytest.

## Architecture Decision

**Chosen approach: explicit env override with repo-local vendored fallback**

This is the right choice for T051 because:

- local development can still point the test at live planning files with
  `BIOMCP_PLANNING_ROOT=/home/ian/workspace/planning/teams/biomcp`
- GitHub Actions and other clean runners use checked-in fixture snapshots
- the contract stays explicit rather than silently skipping when planning files
  are unavailable
- fixture drift remains visible because the assertions still run against real
  content

## File Disposition

| File | Action | Notes |
|------|--------|-------|
| `tests/test_upstream_planning_analysis_docs.py` | Modified | Uses `BIOMCP_PLANNING_ROOT` with repo-local fallback |
| `tests/fixtures/planning/biomcp/strategy.md` | Added | Repo-local planning snapshot satisfying strategy assertions |
| `tests/fixtures/planning/biomcp/frontier.md` | Added | Repo-local planning snapshot satisfying frontier assertions |
| `spec/` | No change | This ticket is covered by pytest docs-contract tests, not executable spec files |

## Acceptance Coverage

- [x] No test in `tests/test_upstream_planning_analysis_docs.py` requires an
  Ian-local absolute planning path.
- [x] The upstream planning contract remains explicit: the test still asserts
  required BioMCP strategy/frontier markers and does not skip when data is
  missing.
- [x] The CI-compatible source of truth is explicit and understandable:
  `BIOMCP_PLANNING_ROOT` is the override, and the repo fixture path is the
  default.
- [x] The affected test file passes locally with the default repo-local
  fallback.
- [x] Workflow inspection shows GitHub Actions does not inject
  `BIOMCP_PLANNING_ROOT`, so clean runners will exercise the fallback path.

The ticket-level acceptance item "the failing test passes in CI" should be
confirmed by the verify/CI step itself. This design review can support that
claim from code and workflow inspection, but it should not claim a green
GitHub Actions run without the actual run evidence.

## Local Test Run

```text
uv run pytest tests/test_upstream_planning_analysis_docs.py -v
# 4 passed, 1 warning in 0.01s
```

Observed warning:

- `PytestAssertRewriteWarning: Module already imported so cannot be rewritten; sitecustomize`

This warning is pre-existing and unrelated to the planning-path regression.

## Verify Plan

1. Run `uv run pytest tests/test_upstream_planning_analysis_docs.py -v` and
   confirm all 4 tests pass.
2. Confirm no `/home/ian/workspace` planning path appears in
   `tests/test_upstream_planning_analysis_docs.py`.
3. Confirm `.github/workflows/release.yml` does not set
   `BIOMCP_PLANNING_ROOT`, so GitHub Actions uses the repo-local fixtures.
4. Optionally run the focused test once with
   `BIOMCP_PLANNING_ROOT=/home/ian/workspace/planning/teams/biomcp` in local
   development to verify the override path still works against live planning
   files.
