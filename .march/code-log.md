# Code Log

## Commands Run

```bash
checkpoint status
GIT_EDITOR=true git rebase main
git diff --stat main..HEAD | tail -1
sed -n '1,220p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,260p' .march/design-final.md
sed -n '1,220p' architecture/ux/cli-reference.md
sed -n '1,220p' architecture/functional/overview.md
sed -n '150,260p' architecture/technical/overview.md
sed -n '1,120p' .github/workflows/ci.yml
sed -n '1,140p' Cargo.toml
cargo test next_commands_validity -- --nocapture
XDG_CACHE_HOME="$PWD/.cache" PATH="$PWD/target/release:$PATH" uv run --extra dev sh -c 'PATH="$PWD/target/release:$PATH" pytest spec/01-overview.md --mustmatch-lang bash --mustmatch-timeout 60 -v'
XDG_CACHE_HOME="$PWD/.cache" PATH="$PWD/target/release:$PATH" uv run --extra dev sh -c 'PATH="$PWD/target/release:$PATH" pytest spec/11-evidence-urls.md --mustmatch-lang bash --mustmatch-timeout 60 -v'
XDG_CACHE_HOME="$PWD/.cache" PATH="$PWD/target/release:$PATH" uv run --extra dev sh -c 'PATH="$PWD/target/release:$PATH" pytest spec/21-cross-entity-see-also.md --mustmatch-lang bash --mustmatch-timeout 60 -v'
XDG_CACHE_HOME="$PWD/.cache" PATH="$PWD/target/release:$PATH" uv run --extra dev sh -c 'PATH="$PWD/target/release:$PATH" pytest spec/19-discover.md --mustmatch-lang bash --mustmatch-timeout 60 -v'
rg -n "See also|next_commands|discover <query>|BIOMCP_TAG|Post-tag public proof|make check-quality-ratchet|biomcp list" architecture src spec tests .github/workflows
sed -n '100,220p' tests/test_upstream_planning_analysis_docs.py
sed -n '150,240p' tests/test_docs_changelog_refresh.py
uv run pytest tests/test_upstream_planning_analysis_docs.py -k 'functional_overview_preserves_readme_surface_and_study_family or technical_and_ux_docs_match_current_cli_and_workflow_contracts' -q
uv run pytest tests/test_docs_changelog_refresh.py -k 'release_overview_uses_manifest_reference_for_current_version_and_release_files or release_overview_post_tag_public_proof_requires_all_markers' -q
make check < /dev/null > /tmp/biomcp-make-check-078.log 2>&1
git status --short
git diff --stat
git diff -- architecture/functional/overview.md architecture/ux/cli-reference.md architecture/technical/overview.md tests/test_upstream_planning_analysis_docs.py tests/test_docs_changelog_refresh.py
```

## What Changed

- Added `discover <query>` to the command grammar in `architecture/functional/overview.md`.
- Added `biomcp discover <query>` to the UX grammar in `architecture/ux/cli-reference.md`.
- Extended the UX architecture with a `See Also and Next Commands` section covering:
  `related_*()` rendering, `format_related_block()`, `_meta.next_commands`,
  zero-result `discover_try_line()` routing, and the executable-or-omit rule.
- Clarified the `biomcp list` boundary so the static list must cover top-level
  discoverability, but not runtime-generated per-record `next_commands`.
- Corrected the technical release pipeline docs so PR CI `check` matches
  `.github/workflows/ci.yml` and local `make check` remains the broader gate.
- Rewrote the post-tag public proof to use an explicit `BIOMCP_TAG` / `tag`
  / `version` flow instead of hardcoded `v0.8.18`.
- Updated repo tests that intentionally lock these documentation contracts.

## Proof Added or Updated

- Updated `tests/test_upstream_planning_analysis_docs.py` to assert:
  `discover` appears in both architecture grammar summaries, the new See-also
  contract exists, the `biomcp list` boundary is explicit, and the CI/post-tag
  wording matches the approved design.
- Updated `tests/test_docs_changelog_refresh.py` to assert the post-tag proof
  now uses `BIOMCP_TAG`, `tag`, and `version` instead of a hardcoded release.

## Verification Results

- `cargo test next_commands_validity -- --nocapture` passed.
- `spec/01-overview.md` passed.
- `spec/11-evidence-urls.md` passed with 2 skipped headings.
- `spec/21-cross-entity-see-also.md` passed.
- Focused doc-contract tests passed after the edits:
  `uv run pytest tests/test_upstream_planning_analysis_docs.py -k 'functional_overview_preserves_readme_surface_and_study_family or technical_and_ux_docs_match_current_cli_and_workflow_contracts' -q`
  and
  `uv run pytest tests/test_docs_changelog_refresh.py -k 'release_overview_uses_manifest_reference_for_current_version_and_release_files or release_overview_post_tag_public_proof_requires_all_markers' -q`.
- `make check` passed. Log: `/tmp/biomcp-make-check-078.log`.

## Deviations From Design

- No deviation in implementation scope.
- One pre-existing non-blocking baseline issue remains outside this ticket:
  `spec/19-discover.md::Ambiguous Query` failed before the doc edits because
  the runtime currently emits a bulleted `## Suggested Commands` list while the
  volatile spec expects numbered items.
