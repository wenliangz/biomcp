# Code Log

## Commands Run

```bash
checkpoint status
sed -n '1,220p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,260p' .march/design-final.md
git status --short
sed -n '1,260p' tests/test_docs_changelog_refresh.py
sed -n '1,260p' tests/test_version_sync_script.py
sed -n '1,260p' tests/test_bioasq_benchmark_contract.py
sed -n '1,180p' tests/test_citation_contract.py
sed -n '1,260p' CHANGELOG.md
sed -n '1,260p' design/technical/overview.md
sed -n '1,200p' CITATION.cff
rg -n '0\.8\.17|0\.8\.18' .
uv run --no-project --with pytest --with mcp python -m pytest tests/test_docs_changelog_refresh.py -k 'changelog_has_backfilled_releases_and_release_header or release_overview_mentions_v0_8_18_current_version_and_release_files' -v
cargo check
uv sync --extra dev
bash scripts/check-version-sync.sh
uv run pytest tests/test_version_sync_script.py tests/test_docs_changelog_refresh.py tests/test_bioasq_benchmark_contract.py tests/test_citation_contract.py -v
uv run mkdocs build --strict
cargo build --release --locked
./target/release/biomcp version | head -n 1
git status --short
git diff --stat
```

## What Changed

- Added the `0.8.18 — 2026-03-25` changelog entry, scoped to the shipped
  release surface: EMA regional drug workflows, the BioASQ benchmark module
  and docs route, and Semantic Scholar optional authentication.
- Bumped the tracked release metadata to `0.8.18` in `Cargo.toml`,
  `Cargo.lock`, `pyproject.toml`, `manifest.json`, and the generated
  editable-root entry in `uv.lock`.
- Updated `design/technical/overview.md` to reflect `0.8.18` as current,
  expanded the release checklist to the repo's actual tracked metadata files,
  and added explicit post-tag verification commands for release/devops handoff.
- Updated `tests/test_docs_changelog_refresh.py` in place so the existing
  docs/version contract proves the new release header, changelog themes, and
  verify-step command handoff.
- Refreshed `CITATION.cff` release version/date so the existing citation
  contract stays aligned with the release metadata surfaces.

## Tests And Proof

- Proof-first failure before implementation:
  `uv run --no-project --with pytest --with mcp python -m pytest tests/test_docs_changelog_refresh.py -k 'changelog_has_backfilled_releases_and_release_header or release_overview_mentions_v0_8_18_current_version_and_release_files' -v`
- Rust metadata refresh:
  `cargo check`
- Python/docs environment and lock refresh:
  `uv sync --extra dev`
- Version-sync contract:
  `bash scripts/check-version-sync.sh`
- Docs/version/BioASQ/citation contracts:
  `uv run pytest tests/test_version_sync_script.py tests/test_docs_changelog_refresh.py tests/test_bioasq_benchmark_contract.py tests/test_citation_contract.py -v`
- Repo docs build proof:
  `uv run mkdocs build --strict`
- Release build proof:
  `cargo build --release --locked`
- Built binary version proof:
  `./target/release/biomcp version | head -n 1`

## Deviations

- The approved design file list did not mention `CITATION.cff`, but I updated
  it because `tests/test_citation_contract.py` already enforces version/date
  parity between the citation metadata, manifest versions, and latest
  changelog release header.
- I repaired `.march/checkpoint.json` after an early parallel checkpoint write
  corrupted the file; this only affected the workflow artifact, not repo or
  runtime behavior.
