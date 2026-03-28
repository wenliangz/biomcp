# Code Review Log

## Review Scope

Reviewed:

- `.march/ticket.md`
- `.march/design-draft.md`
- `.march/design-final.md`
- `.march/code-log.md`
- staged implementation in:
  - `src/sources/gwas.rs`
  - `src/entities/variant.rs`
  - `src/transform/variant.rs`
  - `src/render/markdown.rs`
  - `src/render/provenance.rs`
  - `templates/variant.md.j2`
  - `docs/user-guide/variant.md`
  - `spec/03-variant.md`

Re-ran the relevant local gates:

- `cargo test --quiet`
- `make spec-pr`
- `make check`

## Design Completeness Audit

I checked every "Needs change" item, acceptance criterion, and proof-matrix row
from `.march/design-final.md` against the staged code and spec changes.

### Design items mapped to code

- GWAS source error remap:
  implemented in `src/sources/gwas.rs` via `remap_gwas_error()` and applied to
  all public GWAS fetch methods.
- Truthful unavailable state on variants:
  implemented in `src/entities/variant.rs` by adding
  `gwas_unavailable_reason: Option<String>` and updating `add_gwas_section()`
  to degrade only on `BioMcpError::SourceUnavailable`.
- Variant initialization updates:
  implemented in `src/transform/variant.rs::from_myvariant_hit()` and
  `src/entities/variant.rs::gwas_only_variant_stub()`.
- Truthful markdown rendering:
  implemented in `templates/variant.md.j2` and wired through
  `src/render/markdown.rs`.
- Honest provenance when GWAS is unavailable:
  implemented in `src/render/provenance.rs::variant_section_sources()`.
- JSON/doc contract update:
  implemented in `docs/user-guide/variant.md`.
- Live spec gate update:
  implemented in `spec/03-variant.md::GWAS Supporting PMIDs`.

### Acceptance criteria check

- `biomcp --json get variant rs7903146 gwas` no longer hard-fails on
  GWAS decode/transient failures:
  covered by source remap plus entity-layer degradation.
- Requested-but-unavailable GWAS remains truthful:
  `gwas` stays empty, `gwas_unavailable_reason` is set,
  `supporting_pmids` stays `None`.
- Successful GWAS loads preserve current behavior:
  success path still populates `gwas` and `supporting_pmids`, and clears the
  unavailable marker before loading.
- Markdown renders an unavailable message rather than a false empty-state:
  implemented in the GWAS template branch.
- `_meta.section_sources` still reports GWAS when unavailable:
  implemented in provenance.
- PR spec gate is green:
  verified by `make spec-pr`.

### Documentation / contract audit

- The JSON contract doc now distinguishes:
  - `supporting_pmids: null` when not loaded or temporarily unavailable
  - `gwas_unavailable_reason` when requested but unavailable
  - `supporting_pmids: []` only for a successful load with no PMIDs
- The executable spec now matches the intended contract by accepting either:
  - array-valued `supporting_pmids`, or
  - string-valued `gwas_unavailable_reason`

I did not find a design item with no matching code or contract change.

## Test-Design Traceability

Each proof-matrix item in `.march/design-final.md` has matching proof:

- GWAS decode failure remaps to source unavailability:
  `src/sources/gwas.rs::associations_by_rsid_remaps_decode_failures_to_source_unavailable`
- Transient GWAS HTTP failure remaps to source unavailability:
  `src/sources/gwas.rs::associations_by_rsid_remaps_transient_http_failures_to_source_unavailable`
- GWAS-only variant request degrades instead of failing:
  `src/entities/variant.rs::gwas_only_request_returns_variant_when_gwas_is_unavailable`
- Markdown tells the truth for unavailable GWAS:
  `src/render/markdown.rs::variant_markdown_renders_gwas_unavailable_message`
- Provenance keeps GWAS visible when unavailable:
  `src/render/provenance.rs::variant_provenance_includes_gwas_when_requested_section_is_unavailable`
- Live GWAS contract stays green:
  `spec/03-variant.md::GWAS Supporting PMIDs`
- Rust regressions are not introduced:
  `cargo test --quiet`

I also checked the assertions themselves:

- The source tests assert `BioMcpError::SourceUnavailable`, not just any error.
- The entity test asserts the returned variant exists and carries the truthful
  unavailable fields.
- The markdown test asserts the unavailable message is present and the false
  empty-state copy is absent.
- The provenance test asserts the `gwas` section key remains present.
- The spec heading asserts the user-visible contract rather than the exact
  current implementation shape.

I did not find a missing proof-matrix test or a weak assertion that should
block this review.

## Critique Findings

No additional implementation defects were found in the reviewed change set.

The source remap is scoped correctly, the entity degradation is narrow enough
to avoid swallowing internal bugs, the rendering and provenance changes preserve
truthfulness, and the docs/spec updates match the new contract.

## Fix Plan

No implementation fixes were needed beyond replacing the stale review artifact
with this ticket-specific log.

## Repair

Applied:

- Replaced the stale `.march/code-review-log.md` with a review log for ticket
  `071-bug-fix-harden-gwas-variant-section-for-live-decode-failures`.

No Rust, template, doc, or spec changes were required during review because the
reviewed implementation already matched the final design and passed the gates.

## Post-Fix Collateral Scan

After replacing the review artifact:

- No dead code was introduced.
- No unused imports or variables were introduced.
- No resource cleanup paths changed.
- No stale error messages were introduced.
- No variable shadowing was introduced.

## Verification

- `cargo test --quiet` passed.
- `make spec-pr` passed: `218 passed, 6 skipped, 36 deselected`.
- `make check` passed.

## Residual Concerns

No residual concerns from this review.

## Out-of-Scope Observations

None.

## Defect Register

| # | Category | Lintable | Description |
|---|----------|----------|-------------|
| 1 | None found | no | No additional defects found during code review beyond the implementation already present in the worktree |
