# Design: T069 — Add protein entity spec coverage (spec/16-protein.md)

## Summary

Create `spec/16-protein.md` with four spec sections covering `search protein`,
`get protein`, and `get protein --json`. The spec uses stable structural markers
per team learnings — no literal upstream values beyond stable identity anchors.
Review confirmed the live CLI contract: positional search is supported, the markdown
protein card includes both a `More:` helper and a `See also:` block, and JSON output
includes `_meta.evidence_urls` plus `_meta.next_commands`. The spec was corrected to
cover the required `More:` hint and passes `make spec`.

---

## Architecture Decisions

**Spec-only ticket — no product code changes.**
The protein entity is fully shipped and working per P001 QA. This ticket changes
only executable documentation in `spec/16-protein.md` plus this design artifact;
no `src/` or runtime behavior is modified.

**Use positional argument, not `-q`, in the spec proof.**
`src/cli/mod.rs` defines protein search with both `query: Option<String>` and
`positional_query: Option<String>`, so both forms are valid at runtime. The ticket
explicitly requires the positional form be exercised, so the spec uses
`biomcp search protein BRAF` without `-q` even though help text still shows `-q`
examples.

**Search heading proof must allow the default reviewed scope suffix.**
`src/cli/mod.rs` builds the visible heading from
`crate::entities::protein::search_query_summary(...)`, and the shipped default
human-only search scope currently appends `reviewed=true`. The live heading for the
target case is therefore `# Proteins: BRAF, reviewed=true`, so the spec correctly
asserts the stable `# Proteins: BRAF` prefix instead of the entire line.

**Assert structural markers only.**
Per team learnings (P002/spec-suite): use stable table headers, section headings,
and fixed identifiers like accession numbers, not volatile upstream text fields.
`Gene: BRAF` and `Accession: P15056` are stable identity anchors for the canonical
UniProt record. The protein name and full function text are intentionally not
asserted because they can drift upstream.

**Markdown detail proof must cover both helper surfaces.**
`templates/protein.md.j2` renders the visible protein card, while
`src/render/markdown.rs` injects the `More:` command block via
`format_sections_block(...)` and the `See also:` block via `format_related_block(...)`.
The ticket specifically requires the `More:` hint, so the detail-card section asserts
`More:` in addition to `See also:`.

**JSON `next_commands` assertion stays structural.**
`src/render/markdown.rs::related_protein` currently emits `biomcp get protein
P15056 structures` and `biomcp get gene BRAF`. The spec asserts the `_meta` keys and
a stable `biomcp get protein P15056` substring rather than an exact array payload, to
avoid overfitting if additional next commands are added later.

**Spec proof must run through the release binary path.**
`Makefile` prepends `target/release` to `PATH` before invoking `pytest spec/`.
That matters in this repo because `uv run` can otherwise pick up a stale
`.venv/bin/biomcp`. Targeted proof should therefore use either `make spec` or the
equivalent `uv run --extra dev` invocation with `PATH="$(pwd)/target/release:$PATH"`.

---

## File Disposition

| File | Change |
|---|---|
| `.climb/design.md` | Update — corrected review notes to match the live protein CLI contract |
| `spec/16-protein.md` | Create/update — 4 sections covering positional search, table structure, detail card, and JSON metadata |

No product/runtime files are created or modified.

---

## Spec Sections

### 1. Positional Search Query
Command: `biomcp search protein BRAF --limit 3`
Asserts: heading starts with `# Proteins: BRAF` (allowing the current
`, reviewed=true` suffix), result count present.

### 2. Search Table Structure
Command: `biomcp search protein BRAF --limit 3`
Asserts: table columns `| Accession | Name | Gene | Species |`, `P15056` row, usage hint.

### 3. Getting Protein Details
Command: `biomcp get protein P15056`
Asserts: `Accession: P15056`, `Gene: BRAF`, `## Function` section, `More:` helper,
`See also:` block, `[UniProt](` link.

### 4. JSON Metadata Contract
Command: `biomcp get protein P15056 --json`
Asserts: `_meta`, `evidence_urls`, `"label": "UniProt"`, `next_commands`,
`biomcp get protein P15056`.

---

## Acceptance Criteria

1. `spec/16-protein.md` exists in the worktree.
2. All four spec sections pass via `make spec`.
3. Positional arg (`search protein BRAF` without `-q`) is tested.
4. Search table confirms `| Accession | Name | Gene | Species |` columns.
5. Detail card confirms `Accession:`, `Gene:`, `## Function`, `More:`, and `[UniProt](` markers.
6. JSON `--json` confirms `_meta.evidence_urls` and `_meta.next_commands` present and non-empty.
7. Total spec gate remains green (no regressions).

---

## Success Checklist Coverage

| Item | Covered by |
|---|---|
| `spec/16-protein.md` exists and passes via `make spec` | File created; `make spec` = 103 passed, 5 skipped |
| `search protein BRAF` returns results with accession column | Section 2: asserts `| Accession |` and `P15056` |
| `get protein P15056` renders card with Gene, Function, UniProt link | Section 3: asserts `Gene:`, `## Function`, `More:`, and `[UniProt](` |
| JSON `_meta.evidence_urls` and `_meta.next_commands` are present | Section 4: all four `_meta` assertions |
| Positional argument works (no flag prefix required) | Section 1: `biomcp search protein BRAF` (no `-q`) |

All five checklist items fully covered.

---

## Proof Matrix

| Layer | Proof |
|---|---|
| Spec | `make spec` — 103 passed, 5 skipped; `spec/16-protein.md` contributes 4 passing protein cases |
| Test | Existing `src/cli/mod.rs::protein_next_commands_parse` keeps generated protein helper commands parser-valid; positional search itself is covered by the executable spec and live CLI smoke rather than a new unit test on this ticket |
| Dev smoke | Live CLI checks: `cargo run --quiet --bin biomcp -- search protein BRAF --limit 3`, `get protein P15056`, and `get protein P15056 --json` |
| Regression | Baseline was 99 passed, 5 skipped before `spec/16-protein.md`; current total 103 passed, 5 skipped confirms no spec regressions |

---

## Dev Verification Plan

```bash
cd /home/ian/workspace/worktrees/T069-biomcp
cargo run --quiet --bin biomcp -- search protein BRAF --limit 3
cargo run --quiet --bin biomcp -- get protein P15056
cargo run --quiet --bin biomcp -- get protein P15056 --json
XDG_CACHE_HOME="$PWD/.cache" PATH="$PWD/target/release:$PATH" \
  uv run --extra dev sh -c 'PATH="$PWD/target/release:$PATH" pytest spec/16-protein.md --mustmatch-lang bash --mustmatch-timeout 60 -v'
make spec
# Expect: spec/16-protein.md::* PASSED x4, 103 passed, 5 skipped total
```
