# Code Log

## Commands run

```bash
checkpoint status
sed -n '1,220p' /home/ian/workspace/.agents/skills/checkpoint/SKILL.md
sed -n '1,220p' .march/ticket.md
sed -n '1,240p' .march/design-draft.md
sed -n '1,260p' .march/design-final.md
rg -n "gwas_unavailable_reason|add_gwas_section|variant_section_sources|GWAS Supporting PMIDs|SourceUnavailable|associations_by_rsid|associationByStudy" src templates spec docs/user-guide/variant.md
git status --short
git diff --cached -- src/entities/variant.rs src/sources/gwas.rs src/render/markdown.rs src/render/provenance.rs templates/variant.md.j2 docs/user-guide/variant.md spec/03-variant.md .march/code-log.md src/transform/variant.rs
sed -n '1,260p' src/sources/gwas.rs
sed -n '260,620p' src/sources/gwas.rs
sed -n '1,260p' src/entities/variant.rs
sed -n '1200,2050p' src/entities/variant.rs
sed -n '500,620p' src/render/provenance.rs
sed -n '1,260p' src/render/markdown.rs
sed -n '1,220p' templates/variant.md.j2
sed -n '1,220p' docs/user-guide/variant.md
sed -n '140,220p' spec/03-variant.md
sed -n '1,180p' src/error.rs
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/rust-standards/SKILL.md
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/testing-mindset/SKILL.md
cargo check --quiet
cargo fmt
cargo test associations_by_rsid_remaps_decode_failures_to_source_unavailable --quiet
cargo test associations_by_rsid_remaps_transient_http_failures_to_source_unavailable --quiet
cargo test gwas_only_request_returns_variant_when_gwas_is_unavailable --quiet
cargo test variant_markdown_renders_gwas_unavailable_message --quiet
cargo test variant_provenance_includes_gwas_when_requested_section_is_unavailable --quiet
git add src/render/markdown.rs src/render/provenance.rs src/sources/gwas.rs
checkpoint note "GWAS hardening follows final design: source remaps transient/decode failures to SourceUnavailable, variant output preserves truthful unavailable state via gwas_unavailable_reason and supporting_pmids=None."
cargo run --quiet --bin biomcp -- --json get variant rs7903146 gwas
cargo test --quiet
make spec-pr
git status --short
rm -rf .venv .pytest_cache .cache
git status --short
```

## What changed

- Added GWAS source error remapping in `src/sources/gwas.rs` so GWAS decode failures and transient upstream HTTP failures become `BioMcpError::SourceUnavailable`.
- Added `gwas_unavailable_reason` to `Variant` and initialized it in variant constructors.
- Hardened `add_gwas_section()` in `src/entities/variant.rs` to degrade only on `SourceUnavailable`, keeping `supporting_pmids` as `None` and setting a truthful unavailable message.
- Updated markdown rendering and provenance so unavailable GWAS requests still render honest output and keep `_meta.section_sources.gwas`.
- Updated `spec/03-variant.md` and `docs/user-guide/variant.md` to reflect the array-or-unavailable contract for GWAS.

## Proof added or updated

- `src/sources/gwas.rs`
  - decode failure remaps to `SourceUnavailable`
  - transient HTTP failure remaps to `SourceUnavailable`
- `src/entities/variant.rs`
  - GWAS-only request returns a variant with `gwas_unavailable_reason` instead of failing
- `src/render/markdown.rs`
  - unavailable GWAS renders the unavailable message instead of the empty-data text
- `src/render/provenance.rs`
  - unavailable GWAS still contributes a `gwas` section source
- `spec/03-variant.md`
  - GWAS supporting PMIDs heading now accepts either `supporting_pmids` array or `gwas_unavailable_reason` string

## Verification

- `cargo test --quiet` passed
- `cargo test associations_by_rsid_remaps_decode_failures_to_source_unavailable --quiet` passed
- `cargo test associations_by_rsid_remaps_transient_http_failures_to_source_unavailable --quiet` passed
- `cargo test gwas_only_request_returns_variant_when_gwas_is_unavailable --quiet` passed
- `cargo test variant_markdown_renders_gwas_unavailable_message --quiet` passed
- `cargo test variant_provenance_includes_gwas_when_requested_section_is_unavailable --quiet` passed
- `cargo run --quiet --bin biomcp -- --json get variant rs7903146 gwas` returned successful JSON with GWAS rows and `supporting_pmids`
- `make spec-pr` passed: `218 passed, 6 skipped, 36 deselected`

## Deviations from design

- No GWAS deserializer schema changes were needed. The live `rs7903146` endpoint decoded successfully during implementation, so the fix stayed at the approved source-remap plus entity/render/spec hardening layer.
