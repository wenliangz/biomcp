# Code Review Log

## Review Scope

Reviewed `.march/ticket.md`, `.march/design-draft.md`, `.march/design-final.md`,
`.march/code-log.md`, the staged implementation in
`src/cli/health.rs`, and the spec updates in `spec/01-overview.md`.

Re-ran the relevant gates and direct CLI checks instead of relying on the
existing code log.

## Design Completeness Audit

All final-design items marked as required were matched to the current code:

- `HealthRow.status` remains the serialized JSON contract and markdown-only
  decoration moved to `markdown_status()` used by
  `HealthReport::to_markdown()`.
- `HealthRow.key_configured: Option<bool>` exists with
  `skip_serializing_if = "Option::is_none"`.
- `health_row(...)` accepts `key_configured` and all helper call sites were
  updated.
- `masked_key_hint` and `decorated_status` were removed.
- `excluded_outcome(...)` now emits `key_configured: Some(false)` for
  env-gated excluded rows.
- `send_request(...)` now carries raw `"ok"` / `"error"` statuses plus
  `key_configured`.
- Mandatory auth probes use `Some(true)` when configured and keep
  `excluded (set ENV_VAR)` when missing.
- `check_auth_query_param(...)` invalid-URL error path builds raw `"error"`
  with `key_configured: Some(true)`.
- Optional-auth Semantic Scholar behavior preserves its special authenticated
  and unauthenticated success/rate-limit strings while using raw `"error"`
  statuses for non-special failures.
- Markdown decoration is narrow and explicit: only `"ok"` / `"error"` rows are
  decorated from `key_configured`.
- Contract/spec updates were made in `spec/01-overview.md` for JSON health
  output and no-secret assertions.

No design item was missing a corresponding code or spec change.

## Test-Design Traceability

Every proof item and required test from the final design has matching coverage:

- Remove masked-key test:
  `key_gated_source_masks_present_key` is gone.
- Auth-backed rows carry `key_configured`:
  covered by `key_gated_source_is_excluded_when_env_missing`,
  `empty_key_is_treated_as_missing`,
  `optional_auth_get_reports_authed_semantic_scholar_as_configured`,
  `optional_auth_get_reports_authenticated_429_as_error`,
  `optional_auth_get_reports_unauthenticated_non_429_as_error`,
  `optional_auth_get_reports_unauthenticated_429_as_unavailable`.
- Markdown keyed error rendering:
  `markdown_decorates_keyed_error_rows_without_changing_status`.
- Markdown keyed success rendering:
  `markdown_decorates_keyed_success_rows_without_changing_status`.
- Excluded keyed-row JSON serialization:
  `excluded_key_gated_row_serializes_key_configured_false`.
- Public-row JSON omission:
  `public_row_omits_key_configured_in_json`.
- Raw keyed JSON status with boolean metadata:
  `keyed_row_serializes_raw_status_with_key_configured_true`.
- Semantic Scholar unauthenticated wording preserved with
  `key_configured == Some(false)`:
  `optional_auth_get_reports_unauthed_semantic_scholar_as_healthy`,
  `optional_auth_get_reports_unauthenticated_429_as_unavailable`.
- Outside-in spec coverage for `biomcp health --apis-only` and
  `biomcp --json health --apis-only`:
  `spec/01-overview.md`.

I did not find any proof-matrix item without a matching test or spec assertion.

## Findings

No additional implementation defects were found in this review.

The only artifact problem was that `.march/code-review-log.md` contained stale
content from a different ticket. That artifact defect is corrected here.

## Fix Plan

- No source-code fixes were required.
- Replace the stale review artifact with a log for ticket 066.

## Repair

- Rewrote `.march/code-review-log.md` for this ticket.
- No changes were needed in `src/cli/health.rs` or `spec/01-overview.md`
  beyond the implementation already under review.

## Verification

- `checkpoint status`
- `cargo test health::tests`
  - passed: `27 passed`
- `uv sync --extra dev`
  - passed
- `XDG_CACHE_HOME="$(mktemp -d)" PATH="$PWD/target/release:$PATH" uv run --extra dev sh -c 'PATH="$PWD/target/release:$PATH" pytest spec/01-overview.md --mustmatch-lang bash --mustmatch-timeout 60 -v'`
  - passed: `4 passed`
- `make check`
  - passed
- `cargo build --release --locked`
  - passed
- `env -u NCI_API_KEY -u ONCOKB_TOKEN -u DISGENET_API_KEY -u ALPHAGENOME_API_KEY -u S2_API_KEY -u UMLS_API_KEY ./target/release/biomcp health --apis-only`
  - passed; output contained no key material
- `env -u NCI_API_KEY -u ONCOKB_TOKEN -u DISGENET_API_KEY -u ALPHAGENOME_API_KEY -u S2_API_KEY -u UMLS_API_KEY ./target/release/biomcp --json health --apis-only`
  - passed; JSON status strings contained no key material and excluded auth
    rows emitted `key_configured: false`
- `env -u NCI_API_KEY -u ONCOKB_TOKEN -u DISGENET_API_KEY -u ALPHAGENOME_API_KEY -u S2_API_KEY -u UMLS_API_KEY ./target/release/biomcp health`
  - passed; full markdown output contained no key material

## Residual Concerns

- Live upstream health probes are network-dependent. Exact ok/error counts can
  vary between runs, so verify should compare the no-secret contract and
  `key_configured` semantics rather than expecting stable live counts.

## Out-of-Scope Observations

No out-of-scope follow-up issue was needed from this review.

## Defect Register

| # | Category | Lintable | Description |
|---|----------|----------|-------------|
| 1 | stale-doc | no | `.march/code-review-log.md` contained stale review content from a different ticket and was replaced with the correct ticket-066 review log |
