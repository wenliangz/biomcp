# Code Log

## Summary

Implemented chart sizing and DPI controls, added `waterfall` and `scatter`
chart modes, preserved the existing study markdown/JSON contracts, updated
embedded/public chart docs plus the study spec fixture and spec coverage, and
finished the step with a repo-wide clippy cleanup so `make check` can pass.

## Commands Run

- `checkpoint status`
- `checkpoint done 1`
- `checkpoint done 2`
- `checkpoint note "..."`
- `sed -n '1,220p' .march/ticket.md`
- `sed -n '1,260p' .march/design-draft.md`
- `sed -n '1,420p' .march/design-final.md`
- `sed -n '1,240p' /home/ian/workspace/.agents/skills/checkpoint/SKILL.md`
- `sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/rust-standards/SKILL.md`
- `sed -n '1,240p' /home/ian/workspace/planning/flows/build/skills/testing-mindset/SKILL.md`
- `sed -n '1,240p' /home/ian/workspace/planning/flows/build/skills/cli-design/SKILL.md`
- `rg -n "ChartArgs|ChartRenderOptions|ChartType|..." src spec docs -S`
- `cargo test mutation_counts_by_sample_returns_sorted_counts`
- `cargo test terminal_chart_respects_custom_cols_and_rows`
- `cargo test inline_svg_output_respects_custom_dimensions`
- `cargo test chart_dimension_flags_validate_positive_values`
- `cargo test expression_pairs_by_sample_round_trips_source_result`
- `cargo test expression_scatter_renders_inline_svg_and_rejects_empty_points`
- `cargo test rewrite_mcp_chart_args_rejects_terminal_and_png_only_flags`
- `cargo test study_compare_expression_invalid_chart_lists_scatter`
- `cargo test study_query_parses_waterfall_chart_flag`
- `cargo test study_compare_expression_parses_scatter_chart_with_file_dimensions`
- `cargo test rewrite_mcp_chart_args_preserves_svg_sizing_flags`
- `cargo build`
- `bash spec/fixtures/setup-study-spec-fixture.sh .`
- direct shell verification with `target/debug/biomcp` covering the new study spec cases
- `cargo fmt`
- `cargo fmt --check`
- `git diff -- src/cli/mod.rs src/render/chart.rs`
- `sed -n '60,200p' src/render/chart.rs`
- `sed -n '4680,4775p' src/cli/mod.rs`
- `sed -n '4920,4995p' src/cli/mod.rs`
- `sed -n '3988,4006p' src/entities/article.rs`
- `cargo clippy --all-targets --all-features -- -D warnings`
- `cargo test`
- `git status --short`

## Changes Made

- Updated `src/cli/mod.rs`:
  - added `ChartType::Waterfall` and `ChartType::Scatter`
  - extended `ChartArgs` with optional `--cols`, `--rows`, `--width`,
    `--height`, and `--scale`
  - added parser-level validation for positive numeric values
  - rewired chart dispatch so:
    - `study query --type mutations --chart waterfall` uses per-sample mutation counts
    - `study compare --type expression --chart scatter` uses paired expression values
  - updated MCP chart-argument rewriting to preserve `--width/--height` and reject
    `--cols/--rows/--scale`
- Updated `src/render/chart.rs`:
  - extended `ChartRenderOptions` with optional size/scale fields
  - kept render-layer defaults (`100x32`, `2.0x`) while validating flags against
    the resolved output target
  - applied `--width/--height` to all scene-based charts, including co-occurrence heatmaps
  - added `render_mutation_waterfall_chart()` and `render_expression_scatter_chart()`
  - updated PNG rendering to use `PngBackend::with_scale(scale)`
  - collapsed chart render option construction into `From<&ChartArgs>` so the
    shared sizing/DPI plumbing stays clippy-clean
- Updated `src/sources/cbioportal_study.rs`:
  - added `mutation_counts_by_sample()`
  - added single-pass `expression_pairs_by_sample()`
- Updated `src/entities/study.rs`:
  - added async wrappers for the new chart-only helpers
- Updated `src/entities/article.rs`:
  - replaced a manual `iter().any()` assertion with `.contains()` to clear a
    repo-wide clippy warning surfaced during final verification
- Updated embedded/public docs:
  - `src/cli/chart.rs`
  - `docs/charts/index.md`
  - new `docs/charts/waterfall.md`
  - new `docs/charts/scatter.md`
  - refreshed chart inventory/flag references in the affected docs/blog pages
- Updated spec assets:
  - added `TP53` expression data to the BRCA study spec fixture
  - added study spec coverage for terminal sizing, SVG dimensions, waterfall,
    scatter, and the updated invalid chart/help surfaces

## Proof / Tests Added

- Added/updated Rust proof in:
  - `src/cli/chart.rs`
  - `src/cli/mod.rs`
  - `src/entities/study.rs`
  - `src/render/chart.rs`
  - `src/sources/cbioportal_study.rs`
- Added spec coverage in `spec/13-study.md`
- Extended `spec/fixtures/setup-study-spec-fixture.sh` for scatter data

## Verification

- `cargo fmt --check` passed
- `cargo clippy --all-targets --all-features -- -D warnings` passed
- `cargo test` passed
  - 949 unit tests
  - 16 integration/doc tests
- Direct shell verification passed against the local study fixture using
  `target/debug/biomcp` for:
  - custom terminal dimensions
  - custom SVG dimensions
  - `waterfall` terminal output
  - `scatter` terminal output
  - updated invalid chart error surfaces
  - `biomcp chart waterfall`
  - `biomcp chart scatter`

## Deviations

- No product/design deviations.
- Operational deviation: the `uv run --extra dev pytest spec/13-study.md ...`
  path stalled in package release-build setup, so I validated the new study spec
  cases directly with the local fixture and `target/debug/biomcp` instead.
- Operational deviation: an earlier parallel `checkpoint` write corrupted
  `.march/checkpoint.json`, so I repaired that local March state file to keep
  the required checkpoint workflow usable.
