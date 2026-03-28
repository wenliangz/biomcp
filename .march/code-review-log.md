# Code Review Log

## Scope Reviewed

- `.march/design-draft.md`
- `.march/design-final.md`
- `.march/code-log.md`
- `design/technical/overview.md`
- `tests/test_docs_changelog_refresh.py`
- `tests/test_upstream_planning_analysis_docs.py`
- Relevant implementation surfaces referenced by the new architecture text:
  `src/cli/chart.rs`, `src/cli/mod.rs`, `src/render/chart.rs`,
  `scripts/check-version-sync.sh`, and `spec/13-study.md`

## Critique

### Design Completeness Audit

- Current-version drift fix: implemented in `design/technical/overview.md`.
  The overview now points to `Cargo.toml` and names the actual version-sync
  manifests enforced by `scripts/check-version-sync.sh`.
- New `## Chart Rendering` section: implemented in
  `design/technical/overview.md`.
- `biomcp chart` described as embedded documentation, not the renderer:
  implemented and consistent with `src/cli/chart.rs`.
- Study rendering ownership documented for `study query`,
  `study co-occurrence`, `study compare`, and `study survival`:
  implemented and consistent with `ChartArgs` in `src/cli/mod.rs`.
- Actual 12 chart types and command compatibility matrix: implemented and
  consistent with `ChartType` plus validation in `src/render/chart.rs`.
- Output targets and flag boundaries: implemented and consistent with
  `output_target()` and `rewrite_mcp_chart_args()`.
- MCP rewrite behavior: implemented and consistent with the real rewrite layer.
  The overview does not mention a nonexistent `--png` flag and does not imply
  MCP file output.
- Link to `docs/charts/index.md`: implemented.
- Docs-contract updates required by the final design:
  `tests/test_docs_changelog_refresh.py` and
  `tests/test_upstream_planning_analysis_docs.py` were both updated.

Result: no design item from `design-final.md` was skipped.

### Test-Design Traceability

- Proof matrix item "Current-version line is drift-proof":
  covered by the overview text itself and by
  `test_release_overview_uses_manifest_reference_for_current_version_and_release_files`.
- Proof matrix item "Overview docs contract accepts the new version wording":
  covered by `tests/test_docs_changelog_refresh.py`.
- Proof matrix item "Chart architecture section exists and uses the real repo model":
  covered by `test_chart_rendering_architecture_doc_matches_repo_contract`.
- Proof matrix item "Study chart behavior referenced by the architecture doc still matches shipped behavior":
  covered by existing chart scenarios in `spec/13-study.md`.
- Proof matrix item "Full repo contracts stay green after the doc and test updates":
  covered by `make test-contracts`.

Result: the required tests/specs existed, but the implementation step did not
replay the full proof matrix. `.march/code-log.md` showed targeted docs pytest
and `make check`, but it omitted `make spec-pr` and `make test-contracts`,
which `design-final.md` explicitly called out as verification surfaces.

### Quality Checks

- Implementation quality: the touched docs and pytest files follow adjacent repo
  conventions. No unnecessary abstractions were introduced.
- Test quality: the new pytest coverage checks contract text, not incidental
  formatting trivia. Existing `spec/13-study.md` remains the outside-in proof
  for chart behavior.
- Performance: not applicable; docs-only change.
- Data completeness: the chart section documents all contractually required
  surfaces named in the final design.
- Security: no new untrusted-input flow introduced.

## Fix Plan

- Repair the verification gap by running the proof-matrix gates that were not
  replayed during implementation: `make spec-pr` and `make test-contracts`.
- Re-run `make check` after the verification repair, per the review-step
  instructions.
- Record the issue and the repaired verification state in this review log.

## Repair

- Ran `make spec-pr`: passed (`218 passed, 6 skipped, 36 deselected`).
- Ran `make test-contracts`: passed (`125 passed` and `mkdocs build --strict`).
- Re-ran `make check`: passed.

No source changes were required. The implementation itself was complete and
accurate; the only defect was incomplete verification against the final design.

## Residual Concerns

- The final design intentionally leaves a spec gap for architecture-doc prose.
  The overview contract is enforced through docs-contract pytest, not a
  dedicated `spec/*.md` file. Verify should continue treating those pytest
  files as the enforcement surface for future overview edits.
- `mkdocs build --strict` emitted the existing upstream Material/MkDocs 2.0
  warning, but the build succeeded and this review did not change that surface.

## Defect Register

| # | Category | Lintable | Description |
|---|----------|----------|-------------|
| 1 | verification-gap | no | `design-final.md` required `make spec-pr` and `make test-contracts`, but the implementation replay only covered targeted docs pytest and `make check`; review ran the missing gates and confirmed they pass. |
