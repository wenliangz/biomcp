# Design: T070 — Minor code quality polish

This ticket remains three independent edits in the current codebase:

1. `src/entities/article.rs`: replace the hard-coded deep-fetch warning threshold with a named constant and clearer advisory copy.
2. `src/cli/mod.rs`: add a property-level parser test for `_meta.next_commands` emitted by entity JSON output.
3. `src/entities/article.rs`: split `INVALID_ARTICLE_ID_MSG` into two sentences without changing the supported/unsupported identifier contract.

The initial design was directionally correct but under-covered the JSON command surface. The current CLI emits `_meta.next_commands` from 11 get-JSON paths, not 8, and the new property test should validate the JSON-rendered commands rather than bypassing `_meta`.

---

## Verified Current Code

- `src/entities/article.rs:200-214` defines pagination constants plus `INVALID_ARTICLE_ID_MSG`.
- `src/entities/article.rs:890-895` emits the current Europe PMC deep-fetch warning on the 21st fetch with the literals `21` and `20`.
- `src/cli/mod.rs:6344-6445` already has a `next_commands_validity` module with static parser checks for 11 surfaces:
  gene, variant, article, trial, disease, pgx, drug, pathway, protein, adverse-event, device-event.
- Entity JSON output is rendered through `crate::render::json::to_entity_json(...)`, not by the markdown helpers alone. Current get-JSON call sites are in `src/cli/mod.rs` for:
  gene, article, disease, pgx, trial, variant, drug, pathway, protein, and adverse-event/device-event.
- `spec/06-article.md` already covers invalid article identifier rejection at the outside-in level.
- `spec/11-evidence-urls.md` already covers that get-JSON responses contain `_meta.next_commands`; it does not prove those commands are parseable.

---

## Architecture Decisions

### ARCH-02 / UX-02 — Name the deep-fetch advisory threshold

Add `const WARN_PAGE_THRESHOLD: usize = 20;` beside the other article pagination constants in `src/entities/article.rs`, immediately after `MAX_PAGE_FETCHES`.

Keep the warning one-shot by replacing:

```rust
if fetched_pages == 21
```

with:

```rust
if fetched_pages == WARN_PAGE_THRESHOLD + 1
```

That preserves the current behavior exactly: the warning still fires once, on the 21st fetch, which is the first fetch beyond the 20-page advisory threshold.

Use the clarified warning copy from ticket scope:

```rust
"article search is deep (>{WARN_PAGE_THRESHOLD} page fetches); continuing up to {MAX_PAGE_FETCHES} — consider narrowing your query"
```

This is advisory only. No paging behavior, fetch cap, or search result semantics change.

### ARCH-03 — Property-test the JSON `_meta.next_commands` surface

The new test should validate the same surface users get from `biomcp get <entity> --json`: JSON output with `_meta.next_commands`, followed by parser validation of each emitted command.

Do not call `execute()` or live network-backed `get`/`search` functions in unit tests. That would make `cargo test` network-dependent and non-deterministic. Instead:

1. Construct minimal valid entity fixtures in-process.
2. Render JSON with the same helpers the CLI uses today:
   `crate::render::json::to_entity_json(...)`
3. Parse the JSON string into `serde_json::Value`.
4. Extract `value["_meta"]["next_commands"]`.
5. For each command, run `shlex::split(...)` and `Cli::try_parse_from(...)`.

This is the closest CI-safe approximation of `get <entity> --json` because it exercises:

- the real `related_*` generator
- the real JSON metadata wrapper
- the real `_meta.next_commands` extraction path
- the real CLI parser

The property module should cover every current get-JSON surface that emits `_meta.next_commands`:

- gene
- article
- disease
- pgx
- trial
- variant
- drug
- pathway
- protein
- adverse-event (FAERS report)
- adverse-event (device report)

Notes:

- `variant` output may or may not include the optional `variant oncokb` command depending on `ONCOKB_TOKEN`. The test should not assert an exact command count, only that every emitted command parses.
- For the adverse-event branch, render the actual enum shapes used by the CLI (`AdverseEventReport::Faers` and `AdverseEventReport::Device`) so the JSON structure matches the shipped get-JSON path.
- `trial_locations_json(...)` already has dedicated coverage in `src/cli/mod.rs` proving `location_pagination` coexists with `_meta`; this ticket does not need a second property test for that special case.

### ARCH-05 / UX-06 — Split invalid article ID guidance into two sentences

Keep the content contract but rewrite `INVALID_ARTICLE_ID_MSG` into two sentences:

1. Sentence 1 lists supported types: PMID, PMCID, DOI.
2. Sentence 2 names publisher PIIs as unsupported because PubMed and Europe PMC do not index them.

The existing unit test in `src/entities/article.rs` only asserts for the presence of the supported-type labels and the PII/publisher limitation, so no test rewrite is required unless the implementation chooses to strengthen that assertion.

---

## File Disposition

| File | Change |
|---|---|
| `src/entities/article.rs` | Add `WARN_PAGE_THRESHOLD`, replace the hard-coded warning threshold check, update warning copy, split `INVALID_ARTICLE_ID_MSG` into two sentences |
| `src/cli/mod.rs` | Add a new `#[cfg(test)]` module that renders entity JSON, extracts `_meta.next_commands`, and validates every emitted command through `Cli::try_parse_from` |

No `spec/` file changes are required for this ticket.

Why no spec change:

- The warning-string change is internal logging, not a documented CLI contract.
- The invalid-ID change tightens prose but preserves the outside-in contract already covered by `spec/06-article.md`.
- The new parser property is an internal quality gate on `_meta.next_commands`; `spec/11-evidence-urls.md` already covers presence of `_meta.next_commands`, and the new unit test adds parser-validity proof without changing user-visible flow shape.

This matches the `spec-writing` skill guidance: keep representative outside-in behavior in `spec/`, and add exhaustive/internal contract checks in Rust tests.

---

## Implementation Notes

### Article warning constant

Target the existing constant block in `src/entities/article.rs:200-214`.

Add:

```rust
const WARN_PAGE_THRESHOLD: usize = 20;
```

and update the warning block in `src/entities/article.rs:890-895` to:

```rust
if fetched_pages == WARN_PAGE_THRESHOLD + 1 {
    tracing::warn!(
        "article search is deep (>{WARN_PAGE_THRESHOLD} page fetches); continuing up to {MAX_PAGE_FETCHES} — consider narrowing your query"
    );
}
```

### Invalid article identifier copy

Rewrite `INVALID_ARTICLE_ID_MSG` so it remains a single Rust string constant but reads as two sentences. The message should still include:

- `PMID`
- `PMCID`
- `DOI`
- `PII` or `publisher`

### JSON next-command property helper

Add a helper in the new `src/cli/mod.rs` test module along these lines:

```rust
fn assert_json_next_commands_parse(label: &str, json: &str) {
    let value: serde_json::Value = serde_json::from_str(json)
        .unwrap_or_else(|e| panic!("{label}: invalid json: {e}"));
    let cmds = value["_meta"]["next_commands"]
        .as_array()
        .unwrap_or_else(|| panic!("{label}: missing _meta.next_commands"));
    assert!(!cmds.is_empty(), "{label}: expected at least one next_command");
    for cmd in cmds {
        let cmd = cmd
            .as_str()
            .unwrap_or_else(|| panic!("{label}: next_command was not a string"));
        let argv = shlex::split(cmd)
            .unwrap_or_else(|| panic!("{label}: shlex failed on: {cmd}"));
        Cli::try_parse_from(argv)
            .unwrap_or_else(|e| panic!("{label}: failed to parse '{cmd}': {e}"));
    }
}
```

Each test should then:

1. Build a minimal valid fixture for one entity surface.
2. Render JSON with `to_entity_json(...)` plus the matching `*_evidence_urls(...)` and `related_* (...)` helpers already used in production code.
3. Pass the JSON string to `assert_json_next_commands_parse(...)`.

Fixture guidance:

- Prefer explicit Rust literals where the structs are already used that way in nearby tests.
- Prefer `serde_json::from_value(...)` for larger or more volatile structs where a minimal deserializable shape is easier to maintain.
- Reuse nearby test fixture patterns from `src/render/markdown.rs` and `src/cli/mod.rs` instead of inventing new exhaustive struct literals.

---

## Acceptance Criteria

1. `src/entities/article.rs` defines `WARN_PAGE_THRESHOLD` with value `20`.
2. The Europe PMC warning check uses `WARN_PAGE_THRESHOLD + 1`, preserving the current one-time warning on the 21st fetch.
3. The warning message reads as an advisory, includes the advisory threshold and `MAX_PAGE_FETCHES`, and tells users to narrow the query.
4. `INVALID_ARTICLE_ID_MSG` is two sentences: supported identifier types first, unsupported publisher PIIs second.
5. A new property-level test module in `src/cli/mod.rs` renders JSON and parses `_meta.next_commands`, rather than validating hard-coded strings only.
6. That module covers all current get-JSON next-command emitters:
   gene, article, disease, pgx, trial, variant, drug, pathway, protein, adverse-event/faers, adverse-event/device.
7. Every emitted command extracted from `_meta.next_commands` is validated with `shlex::split` plus `Cli::try_parse_from`.
8. Existing article identifier contract checks still pass.
9. `cargo test` passes.
10. `make spec` passes.

---

## Proof Matrix

| Layer | Proof |
|---|---|
| Spec proof | `spec/06-article.md::Invalid Identifier Rejection` stays green; `spec/11-evidence-urls.md::JSON Metadata Contract` stays green |
| Test proof | New `src/cli/mod.rs` JSON `_meta.next_commands` property tests for all current get-JSON emitters |
| Test proof | Existing `src/entities/article.rs` invalid-identifier unit test remains green |
| Dev proof | `cargo test` |
| Dev proof | `make spec` |

No browser proof, shared-runtime smoke proof, or merged-main artifact proof applies to this ticket.

---

## Dev Verification Plan

Run from `/home/ian/workspace/worktrees/T070-biomcp`:

```bash
cargo test
make spec
```

Spot-check during development:

- `cargo test next_commands_validity`
- `cargo test next_commands`
- `cargo test invalid_article_id_error_names_supported_types_and_publisher_limit`

Expected outcomes:

- the new JSON property tests pass across all covered entity surfaces
- the invalid article ID tests still find the supported types and publisher/PII limitation
- specs remain unchanged and green
