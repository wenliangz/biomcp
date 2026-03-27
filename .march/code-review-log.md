# Code Review Log

## Review Scope

Reviewed the resumed worktree against `.march/design-final.md`, the ticket
checklist, the staged docs/spec/test diff, and the required proof matrix.

## Findings

1. `README.md`
   - The Claude Desktop note still used stale direct-bundle language.
   - Approved behavior: Anthropic Directory when available, JSON MCP config for
     local/manual setups.
   - Repair: updated the README wording to the approved stable phrasing.

2. `tests/test_documentation_consistency_audit_contract.py`
   - The new ticket-specific docs-contract suite did not lock the repaired
     README Claude Desktop wording.
   - Repair: added assertions for the README and matching
     `docs/getting-started/claude-desktop.md` guidance.

3. `tests/test_public_skill_docs_contract.py`
   - The staged change retargeted the chart-blog contract from
     `docs/blog/biomcp-kuva-charts.md` to `docs/blog/kuva-charting-guide.md`.
   - That weakened the approved "do not delete either chart blog" proof path.
   - Repair: restored the existing contract to keep asserting against
     `docs/blog/biomcp-kuva-charts.md`.

4. `docs/blog/biomcp-pubmed-articles.md`,
   `docs/blog/skillbench-biomcp-skills.md`
   - The staged intro rewrites were outside the approved scope. The final
     design explicitly said not to do a separate blog-opening rewrite pass.
   - Repair: reverted both intro rewrites.

5. `docs/user-guide/gene.md`
   - `## Error handling expectations` was placed after `## JSON mode`.
   - That drifted from the approved entity-guide structure, which keeps extra
     sections before `## JSON mode`.
   - Repair: moved the error-handling section above `## JSON mode`.

## Fix Plan

1. Repair the README Claude Desktop copy so it matches the approved stable
   install guidance.
2. Add docs-contract regression coverage for that README/Claude Desktop wording.
3. Restore the public-skill blog contract to the approved
   `docs/blog/biomcp-kuva-charts.md` surface.
4. Revert the out-of-scope blog intro rewrites.
5. Move the gene guide's extra error-handling section back before `## JSON mode`.

## Repair Status

All five implementation findings were fixed in the worktree before final
staging. A follow-up critique found one artifact defect in this log: the
verification section had collapsed the regular docs-contract pytest run and the
mustmatch spec run into one command that was not actually how verification was
executed. This log now records the commands separately.

## Verification

- `uv run --extra dev pytest tests/test_documentation_consistency_audit_contract.py tests/test_public_search_all_docs_contract.py tests/test_source_pages_docs_contract.py tests/test_source_licensing_docs_contract.py tests/test_directory_submission_contract.py tests/test_public_skill_docs_contract.py tests/test_docs_changelog_refresh.py -q`
  - passed: `50 passed`
- `PATH="$(pwd)/target/release:$PATH" uv run --extra dev pytest spec/17-cross-entity-pivots.md spec/17-guide-workflows.md --mustmatch-lang bash --mustmatch-timeout 60 -q`
  - passed: `23 passed, 1 skipped`
- `uv run mkdocs build --strict`
  - passed
- `make check`
  - passed

## Residual Concerns

- `uv run mkdocs build --strict` still prints the existing informational nav
  note for `docs/blog/biomcp-kuva-charts.md`, `docs/charts/scatter.md`, and
  `docs/charts/waterfall.md`, plus the upstream Material/MkDocs 2.0 advisory.
  The build passes, and nav work stayed out of scope by design.

## Out-of-Scope Observations

No additional out-of-scope follow-up issues were found for this ticket.
