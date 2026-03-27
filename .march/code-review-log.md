# Code Review Log

## Review Scope

Reviewed `.march/ticket.md`, `.march/design-draft.md`, `.march/design-final.md`,
`.march/code-log.md`, and the staged changes in `src/mcp/shell.rs`, `build.rs`,
`tests/test_mcp_contract.py`, `docs/reference/mcp-server.md`, and
`spec/15-mcp-runtime.md`.

Re-ran the relevant local gates instead of relying on the existing code log:

- `cargo test mcp_allowlist_blocks_mutating_commands`
- `cargo build --quiet --bin biomcp`
- `uv sync --extra dev --no-install-project`
- `.venv/bin/python -m pytest tests/test_mcp_contract.py -q --mcp-cmd "./target/debug/biomcp serve" -k "description_matches_list_contract or mutating_study_download or charted_study_call_returns_text_then_svg_image"`
- `PATH="$PWD/target/debug:$PATH" .venv/bin/python -m pytest spec/15-mcp-runtime.md --mustmatch-lang bash --mustmatch-timeout 60 -v`
- `make check`

## Design Completeness Audit

Every required design item has a corresponding implementation change:

- Explicit `study` allowlist with exact `study download --list` handling:
  implemented in `src/mcp/shell.rs::is_allowed_mcp_command()`.
- Blanket `study` access removed; mutating or malformed `study download` forms
  denied:
  implemented in `src/mcp/shell.rs::is_allowed_mcp_command()`.
- MCP description sanitized to advertise only MCP-safe study forms:
  implemented in `build.rs` via targeted study-line rewriting.
- MCP description contract updated:
  implemented in `tests/test_mcp_contract.py::test_biomcp_description_matches_list_contract`.
- End-to-end MCP rejection of `study download <study_id>`:
  implemented in `tests/test_mcp_contract.py::test_mutating_study_download_is_rejected_in_mcp_mode`.
- Reference docs updated with catalog-only exception and CLI-only install
  guidance:
  implemented in `docs/reference/mcp-server.md`.
- Executable runtime spec for rejection path:
  implemented in `spec/15-mcp-runtime.md`.

Documentation and contract updates were present alongside code changes; I did
not find a design item with no matching code or doc change.

## Test-Design Traceability

The design proof matrix and acceptance criteria map to the following tests and
spec coverage:

- Deny `study download <study_id>`:
  `src/mcp/shell.rs::mcp_allowlist_blocks_mutating_commands` and
  `tests/test_mcp_contract.py::test_mutating_study_download_is_rejected_in_mcp_mode`.
- Allow exact `study download --list`:
  `src/mcp/shell.rs::mcp_allowlist_blocks_mutating_commands`.
- Keep read-only study commands available through the MCP gate:
  `src/mcp/shell.rs::mcp_allowlist_blocks_mutating_commands` plus the existing
  positive integration coverage in
  `tests/test_mcp_contract.py::test_charted_study_call_returns_text_then_svg_image`.
- Hide install syntax from MCP `tools/list` while keeping `study download --list`:
  `tests/test_mcp_contract.py::test_biomcp_description_matches_list_contract`.
- Document and prove runtime rejection outside-in:
  `spec/15-mcp-runtime.md`.

### Issues Found During Traceability

1. The unit proof initially covered `study list`, `study download --list`, and
   one representative `study query`, but it did not cover every read-only
   study subcommand enumerated in the final design acceptance criteria
   (`filter`, `cohort`, `survival`, `compare`, `co-occurrence`).
2. The MCP rejection message still mentioned `study` generically, which was
   stale after narrowing the allowlist to specific MCP-safe study forms.

Both issues were fixed in this review.

## Fix Plan

- Expand the allowlist unit proof in `src/mcp/shell.rs` to cover every
  read-only study subcommand named in the design and one additional malformed
  `study download` shape.
- Update the MCP rejection message in `src/mcp/shell.rs` so it accurately
  describes the allowed study surface after the security fix.

## Repair

Applied the following fixes in `src/mcp/shell.rs`:

- Added positive allowlist assertions for:
  `study filter`, `study cohort`, `study survival`, `study compare`,
  and `study co-occurrence`.
- Added a negative assertion for incomplete `study download`.
- Updated the read-only rejection text to list the exact MCP-safe study
  commands instead of implying that the entire `study` family is allowed.

## Post-Fix Collateral Scan

Checked the touched area after the fix:

- No dead branches were introduced.
- No unused imports or variables remained.
- No resource cleanup paths changed.
- The updated error message now matches the narrowed allowlist behavior.
- No variable shadowing was introduced.

## Verification

- `cargo test mcp_allowlist_blocks_mutating_commands` passed.
- Focused MCP contract tests passed.
- `spec/15-mcp-runtime.md` passed under mustmatch.
- `make check` passed.

## Residual Concerns

- The description rewrite in `build.rs` still depends on exact list-reference
  line shapes. Current tests cover the emitted MCP description contract, so the
  behavior is guarded, but future CLI reference edits should keep that coupling
  in mind.

## Out-of-Scope Observations

No out-of-scope follow-up issue was needed from this review.

## Defect Register

| # | Category | Lintable | Description |
|---|----------|----------|-------------|
| 1 | missing-test | no | Final design acceptance criteria required coverage for every read-only study subcommand, but the unit proof initially covered only `list`, `download --list`, and `query` |
| 2 | stale-doc | no | The MCP rejection message still implied broad `study` access after the allowlist had been narrowed to specific MCP-safe study commands |
