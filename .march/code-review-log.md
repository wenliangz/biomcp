# Code Review Log

## Review Scope

Reviewed `.march/ticket.md`, `.march/design-draft.md`, `.march/design-final.md`,
`.march/code-log.md`, the implementation changes in `src/render/json.rs` and
`src/cli/mod.rs`, and the executable spec update in `spec/11-evidence-urls.md`.

Re-ran the relevant local gates:

- `cargo test to_entity_json_value_adds_meta_and_flattens_entity`
- `cargo test batch_gene_json_includes_meta_per_item`
- `cargo test batch_protein_json_omits_requested_section_from_next_commands`
- `cargo test batch_adverse_event_json_uses_variant_specific_meta`
- `PATH="$PWD/target/debug:$PATH" .venv/bin/python -m pytest spec/11-evidence-urls.md --mustmatch-lang bash --mustmatch-timeout 60 -v`
- `make check`

## Design Completeness Audit

Every final-design implementation item has a matching code or spec change:

- Keep the batch root as an array:
  implemented by `render_batch_json()` in `src/cli/mod.rs`, which serializes a
  `Vec<serde_json::Value>` directly.
- Reuse the existing entity JSON contract in typed form:
  implemented by `to_entity_json_value()` in `src/render/json.rs`, with
  `to_entity_json()` refactored to call it.
- Add batch orchestration in `src/cli/mod.rs`:
  implemented by `render_batch_json()` and the per-entity wrapping closures in
  every `Commands::Batch` JSON branch.
- Match `get` behavior branch-by-branch for all in-scope entities:
  implemented across the `gene`, `variant`, `article`, `trial`, `drug`,
  `disease`, `pgx`, `pathway`, `protein`, and `adverse-event` batch branches.
- Preserve protein requested-section filtering:
  implemented in the `protein` batch branch by passing `&batch_sections` to
  `related_protein(item, &batch_sections)`.
- Preserve adverse-event variant-specific metadata:
  implemented in the `adverse-event` batch branch by matching
  `AdverseEventReport::{Faers, Device}` and using the variant-specific helpers.
- Keep markdown batch output unchanged:
  preserved; only JSON branches changed.
- Leave `article batch ...` unchanged:
  preserved; the design-scoped `Commands::Article` path was not modified.
- Add the required Rust proofs:
  implemented by `to_entity_json_value_adds_meta_and_flattens_entity`,
  `batch_gene_json_includes_meta_per_item`,
  `batch_protein_json_omits_requested_section_from_next_commands`, and
  `batch_adverse_event_json_uses_variant_specific_meta`.
- Add the required executable spec proof:
  implemented by the `Batch JSON Metadata Contract` section in
  `spec/11-evidence-urls.md`.

Documentation and contract updates were also checked separately:

- The repo-level contract text in `README.md` already states that
  `batch ... --json` returns the same metadata shape as `get --json`; no
  further doc repair was needed for this ticket.
- The executable contract in `spec/11-evidence-urls.md` now matches the final
  design by checking batch-array shape plus per-item metadata.

I did not find a final-design item with no matching implementation change.

## Test-Design Traceability

Proof-matrix coverage after repair:

- `to_entity_json_value_adds_meta_and_flattens_entity` exists in
  `src/render/json.rs` and proves the typed helper preserves the single-entity
  `_meta` contract without string round-trips.
- `batch_gene_json_includes_meta_per_item` exists in `src/cli/mod.rs` and now
  proves:
  root remains an array, top-level entity fields remain flat, each item has
  non-empty `_meta.evidence_urls`, each item has non-empty
  `_meta.next_commands`, and at least one item has non-empty
  `_meta.section_sources`.
- `batch_protein_json_omits_requested_section_from_next_commands` exists in
  `src/cli/mod.rs` and proves requested protein sections are not re-suggested.
- `batch_adverse_event_json_uses_variant_specific_meta` exists in
  `src/cli/mod.rs` and proves FAERS/device batch items keep variant-specific
  evidence URLs and follow-up metadata.
- The existing `next_commands_json_property` tests still cover the parseability
  of `_meta.next_commands` across entity families used by batch.
- The spec section `Batch JSON Metadata Contract` exists in
  `spec/11-evidence-urls.md` and now proves the user-visible contract:
  array root, stable item ordering for the fixture call, per-item
  `_meta.evidence_urls`, per-item `_meta.next_commands`, and non-empty
  `_meta.section_sources` on at least one item.

### Issues Found During Traceability

1. `batch_gene_json_includes_meta_per_item` originally asserted only
   `_meta.next_commands`, so it would not have caught regressions that dropped
   `evidence_urls` or `section_sources` from the batch contract.
2. The spec assertion for `section_sources` originally accepted any array,
   including an empty one, which was too weak to prove real provenance data.

Both issues were fixed in this review.

## Fix Plan

- Strengthen `batch_gene_json_includes_meta_per_item` so it asserts the full
  per-item `_meta` contract required by the final design.
- Strengthen the `Batch JSON Metadata Contract` spec section so it requires
  non-empty batch `evidence_urls` and real `section_sources` data instead of
  only checking array types.

## Repair

Applied the following fixes:

- Updated `src/cli/mod.rs::batch_gene_json_includes_meta_per_item` to assert:
  non-empty `_meta.evidence_urls` for each item and non-empty
  `_meta.section_sources` on at least one item, in addition to the existing
  `next_commands` checks.
- Updated `spec/11-evidence-urls.md` so the batch JSON proof now asserts:
  every item has non-empty `_meta.evidence_urls`, every item has non-empty
  `_meta.next_commands`, and at least one item has non-empty
  `_meta.section_sources`.

## Post-Fix Collateral Scan

Checked the touched areas after each fix:

- No dead code or unreachable branches were introduced.
- No imports or variables became unused.
- No resource cleanup logic changed.
- Error messages were unaffected by the proof-only changes.
- No variable shadowing was introduced.

## Verification

- `cargo test to_entity_json_value_adds_meta_and_flattens_entity` passed.
- `cargo test batch_gene_json_includes_meta_per_item` passed after the stronger
  assertions were added.
- `cargo test batch_protein_json_omits_requested_section_from_next_commands`
  passed.
- `cargo test batch_adverse_event_json_uses_variant_specific_meta` passed.
- `PATH="$PWD/target/debug:$PATH" .venv/bin/python -m pytest spec/11-evidence-urls.md --mustmatch-lang bash --mustmatch-timeout 60 -v`
  passed with `4 passed, 2 skipped`.
- `make check` passed.

## Residual Concerns

- The outside-in spec exercises live upstream-backed commands, so timing and
  availability remain partially dependent on external services. The contract is
  now stronger, but verify should still watch for upstream instability rather
  than treating any intermittent spec failure as a deterministic regression.

## Out-of-Scope Observations

No out-of-scope follow-up issue was needed from this review.

## Defect Register

| # | Category | Lintable | Description |
|---|----------|----------|-------------|
| 1 | missing-test | no | `batch_gene_json_includes_meta_per_item` originally verified only `_meta.next_commands`, leaving the batch `evidence_urls` and `section_sources` contract unguarded |
| 2 | weak-assertion | no | The batch executable spec originally accepted empty `section_sources` arrays, so it did not prove real provenance data was present |
