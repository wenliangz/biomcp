# Code Log

## Commands run

- `checkpoint status`
- `cargo test optional_auth_get_reports_authenticated_429_as_error -- --exact` (after updating proof; failed to compile until `key_configured` was implemented)
- `cargo fmt`
- `cargo test health::tests`
- `cargo build --release --locked`
- `uv sync --extra dev`
- `XDG_CACHE_HOME="$(mktemp -d)" PATH="$PWD/target/release:$PATH" uv run --extra dev sh -c 'PATH="$PWD/target/release:$$PATH" pytest spec/01-overview.md --mustmatch-lang bash --mustmatch-timeout 60 -v'`
- `make check`
- `env -u NCI_API_KEY -u ONCOKB_TOKEN -u DISGENET_API_KEY -u ALPHAGENOME_API_KEY -u S2_API_KEY -u UMLS_API_KEY ./target/release/biomcp health --apis-only`
- `env -u NCI_API_KEY -u ONCOKB_TOKEN -u DISGENET_API_KEY -u ALPHAGENOME_API_KEY -u S2_API_KEY -u UMLS_API_KEY ./target/release/biomcp --json health --apis-only`
- `git status --short`
- `git add src/cli/health.rs spec/01-overview.md`
- `git add -f .march/code-log.md`
- `git diff --cached --stat`
- `git diff --cached --name-only`

## What changed

- Added `HealthRow.key_configured: Option<bool>` with `skip_serializing_if`, so JSON exposes structured key-state metadata without leaking any key material.
- Removed `masked_key_hint` and `decorated_status`; mandatory auth probes now store raw `ok` / `error` statuses and explicit `key_configured` values.
- Moved human-only `key configured` / `key not configured` decoration into `HealthReport::to_markdown()`, keeping JSON status strings raw.
- Preserved existing mandatory-auth missing-key `excluded (set ENV_VAR)` behavior and Semantic Scholar optional-auth wording while attaching `key_configured` metadata.
- Updated health unit tests and `spec/01-overview.md` to prove the no-secret markdown/JSON contract.

## Proof added or updated

- Rust unit tests in `src/cli/health.rs` now cover markdown decoration, raw JSON status serialization, excluded keyed rows, public rows omitting `key_configured`, and Semantic Scholar keyed/unkeyed paths.
- `spec/01-overview.md` now unsets auth env vars explicitly, asserts markdown never contains `(key:`, and checks JSON for `key_configured == false` on `OncoKB` plus omission on `MyGene`.

## Verification

- `cargo test health::tests` passed.
- `spec/01-overview.md` passed under `pytest`/`mustmatch`.
- `make check` passed.
- Direct CLI checks against `./target/release/biomcp` confirmed no `(key:` output and the expected JSON `key_configured` contract.

## Deviations from design

- None. The implementation follows the approved final design. The direct CLI checks were supplemental verification while the Python spec environment finished bootstrapping.
