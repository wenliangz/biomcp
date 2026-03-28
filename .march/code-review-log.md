# Code Review Log

## Scope Reviewed

- `.march/design-draft.md`
- `.march/design-final.md`
- `.march/code-log.md`
- Full `git diff main..HEAD`
- Changed runtime, spec, doc, and contract files for the help-architecture overhaul

## Critique

### Design Completeness Audit

I mapped the acceptance criteria and proof matrix to the changed code and tests.
The implementation covered the required help surfaces, discover routing, layered
skill catalog, HATEOAS guidance, template copy, docs updates, and MCP resource
contract.

Gaps found during review:

1. `src/cli/list_reference.md` shipped two `## When to Use What` tables.
   The required routing table existed, but the duplicate block made the top-level
   help noisy and contradicted the design goal of clearer orientation.
2. `src/cli/list.rs` repeated `## When to use this surface` blocks in the
   `drug`, `disease`, `batch`, and `enrich` pages. The content was valid, but
   the duplicate sections reduced clarity.
3. `tests/test_mcp_http_transport.py` had no resource-list/read coverage for the
   new embedded worked-example catalog. The direct MCP contract tests covered the
   new behavior, but the Streamable HTTP path from the proof matrix was not
   updated.

### Test-Design Traceability

Proof-matrix coverage I verified:

- `spec/01-overview.md` covers the top-level routing table and article routing help.
- `spec/02-gene.md` covers alias guidance and HPA tissue detail.
- `spec/05-drug.md` covers sparse-card guidance and informative structured miss wording.
- `spec/06-article.md` covers annotation guidance.
- `spec/07-disease.md` covers phenotype completeness wording.
- `spec/10-workflows.md` covers layered skill overview, `skill list`, and `skill <name>`.
- `spec/19-discover.md` covers treatment, symptom, and gene+disease discover routing.
- Rust unit tests cover HATEOAS descriptions and help-text markers.
- `tests/test_mcp_contract.py` covers MCP resource inventory and reads.

Missing test found:

- The Streamable HTTP transport contract did not verify `list_resources()` and
  `read_resource()` for `biomcp://help` plus `biomcp://skill/<slug>` resources.
  This was a blocking traceability gap and was fixed.

### Additional Defect Found While Re-running Gates

- `cargo test discover:: --lib` exposed a real routing bug:
  `discover "what does OPA1 do"` was classified as `GeneDiseaseOrientation`
  instead of `GeneFunction`.
- Root cause: the fallback `gene_disease_focus()` heuristic treated any
  uppercase-compatible first token as a gene symbol. That was too loose for
  sentence-style queries.

## Fix Plan

1. Remove the duplicated routing/help blocks from `list_reference.md` and `list.rs`.
2. Strengthen the affected list tests so duplicate headings fail in the future.
3. Add Streamable HTTP resource inventory/read tests for the worked-example catalog.
4. Tighten discover gene+disease fallback detection so sentence-style gene-function
   queries do not misclassify.

## Repair

Applied fixes:

- Removed the duplicate `## When to Use What` table from
  `src/cli/list_reference.md`.
- Removed duplicate `## When to use this surface` blocks from the `drug`,
  `disease`, `batch`, and `enrich` list pages in `src/cli/list.rs`.
- Strengthened `src/cli/list.rs` tests to assert those headings appear exactly once.
- Added `test_streamable_http_lists_and_reads_help_and_skill_resources` to
  `tests/test_mcp_http_transport.py`.
- Tightened `gene_disease_focus()` in `src/entities/discover.rs` to require a
  stricter gene-token fallback before treating free text as gene+disease orientation.

### Post-Fix Collateral Scan

After each fix, I checked the touched code for:

- dead code or unreachable branches: none introduced
- unused imports or variables: none introduced
- stale error/help text: none introduced
- shadowed variables: none introduced
- resource-cleanup conflicts: none introduced

## Verification

- `checkpoint status`
- `GIT_EDITOR=true git rebase main`
- `cargo test list:: --lib`
- `cargo test skill:: --lib`
- `cargo test discover:: --lib`
- `cargo test markdown:: --lib`
- `cargo build --release --bin biomcp`
- `XDG_CACHE_HOME="$(pwd)/.cache" PATH="$(pwd)/target/release:$PATH" uv run --extra dev sh -c 'PATH="$(pwd)/target/release:$PATH" pytest spec/01-overview.md spec/02-gene.md spec/05-drug.md spec/06-article.md spec/07-disease.md spec/10-workflows.md spec/19-discover.md --mustmatch-lang bash --mustmatch-timeout 60 -v'`
- `uv run pytest tests/test_public_skill_docs_contract.py tests/test_upstream_planning_analysis_docs.py tests/test_mcp_contract.py tests/test_mcp_http_transport.py -v`
- `make check`

Results:

- Specs: `97 passed, 2 skipped`
- Python contract tests: `25 passed`
- `make check`: passed

## Residual Concerns

- No open defects remain in scope for this ticket.

## Defect Register

| # | Category | Lintable | Description |
|---|----------|----------|-------------|
| 1 | weak-assertion | yes | List-page tests only checked for heading presence, so duplicate help blocks shipped unnoticed. |
| 2 | missing-test | yes | Design required MCP resource coverage for the worked-example catalog on the Streamable HTTP path; no matching transport test existed. |
| 3 | validation-gap | yes | `gene_disease_focus()` accepted overly broad first-token input and misclassified `discover "what does OPA1 do"` as gene+disease orientation. |
