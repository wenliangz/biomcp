# Code Log

## Commands Run

```bash
checkpoint status
sed -n '1,220p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,260p' .march/design-final.md
sed -n '1,260p' src/cli/health.rs
sed -n '1,280p' src/sources/ema.rs
sed -n '1,220p' spec/01-overview.md
sed -n '1,280p' spec/05-drug.md
sed -n '1,260p' docs/troubleshooting.md
sed -n '1,260p' docs/user-guide/drug.md
sed -n '120,220p' docs/reference/data-sources.md
rg -n "biomcp health|health" tests src docs spec .
cargo fmt --all
cargo test -q ema_local_data_ -- --nocapture
cargo test -q health_inventory_includes_all_expected_sources -- --nocapture
BIOMCP_EMA_DIR="$(pwd)/spec/fixtures/ema-human" cargo run --quiet --bin biomcp -- health
BIOMCP_EMA_DIR="$(pwd)/spec/fixtures/ema-human" cargo run --quiet --bin biomcp -- health --apis-only
XDG_CACHE_HOME="$(pwd)/.cache" PATH="$(pwd)/target/debug:$PATH" uv run --no-project --with pytest --with mustmatch pytest spec/05-drug.md -k 'EMA and Health and Readiness' --mustmatch-lang bash --mustmatch-timeout 60 -v
XDG_CACHE_HOME="$(pwd)/.cache" PATH="$(pwd)/target/debug:$PATH" uv run --no-project --with pytest --with mustmatch pytest spec/01-overview.md -k 'Health and Check' --mustmatch-lang bash --mustmatch-timeout 60 -v
XDG_CACHE_HOME="$(pwd)/.cache" uv run --no-project --with mkdocs-material --with pymdown-extensions mkdocs build --strict
git status --short
git status --short --ignored
checkpoint done 1
checkpoint done 2
checkpoint done 3
checkpoint note "EMA local readiness is a full-health-only row..."
```

## What Changed

- Added a full `biomcp health` EMA local-data readiness row in `src/cli/health.rs`.
- Kept `biomcp health --apis-only` API-only by leaving `HEALTH_SOURCES` unchanged.
- Reused the EMA source contract by exporting `EMA_REQUIRED_FILES` and `ema_missing_files()` from `src/sources/ema.rs`.
- Added five Rust unit tests covering empty default root, partial default root, broken env-configured root, complete default root, and complete env-configured root.
- Updated operator-facing specs and docs to distinguish API-only health from full health and to explain EMA readiness states.

## Tests And Specs Added/Updated

- `src/cli/health.rs`
  - `ema_local_data_not_configured_when_default_root_is_empty`
  - `ema_local_data_errors_when_default_root_is_partial`
  - `ema_local_data_errors_when_env_root_is_missing_files`
  - `ema_local_data_reports_available_when_default_root_is_complete`
  - `ema_local_data_reports_configured_when_env_root_is_complete`
- `spec/05-drug.md`
  - Added `EMA Health Readiness`
- `spec/01-overview.md`
  - Clarified API-only vs full-health contract

## Deviations

- No product-behavior deviations from `.march/design-final.md`.
- For spec verification, I used `uv run --no-project --with ...` plus `target/debug/biomcp` to avoid rebuilding the Rust CLI as a Python package; this kept the verification focused on the shipped CLI contract.
