# Design: P043 — Release v0.8.15 Asset Catch-up

## Problem

`v0.8.14` was published on 2026-03-10, but its GitHub release page has no
platform assets because `.github/workflows/release.yml` failed in `validate`
before any packaging jobs ran. Current `main` is commit `6dcfec5` (merge of
PR #191) and already includes:

- PR #190 (`align-search-all-public-docs`): teaches `search all` as the unified
  discovery entry point in `README.md` and `docs/index.md`
- PR #191 (`fix-planning-docs-ci-path`): makes the planning-docs contract test
  use repo-local fixtures by default, with `BIOMCP_PLANNING_ROOT` as an
  explicit override

The catch-up release should ship current `main` as `v0.8.15` and prove that
the public GitHub release page now contains the expected downloadable assets.

## Verified Repo State

1. `tests/test_upstream_planning_analysis_docs.py` now resolves planning files
   from `tests/fixtures/planning/biomcp/` by default, so the
   `FileNotFoundError` that broke `v0.8.14` on GitHub Actions is fixed on
   current `main`.
2. `.github/workflows/release.yml` runs:
   - `validate`: `cargo fmt --check`, `cargo clippy -- -D warnings`,
     `cargo test`, `uv sync --extra dev`,
     `uv run pytest tests/ -v --mcp-cmd "biomcp serve"`,
     `uv run mkdocs build --strict`
   - `build`: 5 binary packaging targets, each uploaded to the GitHub release
     page with a matching `.sha256`
   - `pypi-build` / `pypi-publish`: 4 wheel targets published to PyPI
   - `deploy-docs`: GitHub Pages deploy
3. The GitHub release page asset contract is binary archives plus checksum
   files only. Wheels are built for PyPI, but they are not uploaded to the
   GitHub release page by this workflow.
4. The repo still declares `0.8.14` in all version-sensitive metadata:
   `pyproject.toml`, `Cargo.toml`, `uv.lock`, and `Cargo.lock`.
5. The repo also has release-version assertions outside the version manifests:
   - `CHANGELOG.md` currently starts with `## 0.8.14 — 2026-03-10`
   - `analysis/technical/overview.md` says
     `**Current version:** 0.8.14 (as of 2026-03-10)`
   - `tests/test_docs_changelog_refresh.py` hardcodes both of those
     expectations

## Root Cause of v0.8.14 Release Failure

`v0.8.14` tagged commit `bd15482` predates PR #191. At that tag,
`tests/test_upstream_planning_analysis_docs.py` read BioMCP planning files from
Ian-local absolute paths under `/home/ian/workspace/planning/teams/biomcp/`.
That path does not exist on GitHub Actions runners, so release validation
failed in `pytest tests/ -v` and all downstream packaging jobs were skipped.

Because `build` never ran, the GitHub release page did not receive any of the
five platform archives or their checksum files.

## Design Decisions

1. **Cut the release from current `main` with no cherry-picks.**
   `main` already points at `6dcfec5`, which includes both PR #190 and PR #191.
   The release branch should start from that state.

2. **This is a release-metadata/docs/test refresh, not a runtime feature
   change.**
   No Rust or Python behavior should change for P043. The required edits are
   version bumps, lockfile refreshes, changelog text, and the repo docs/test
   files that intentionally pin the current public release.

3. **Update both lockfiles after the version bump.**
   - `uv.lock` should be refreshed via `uv sync --extra dev`
   - `Cargo.lock` should be refreshed by running a Cargo command after the
     `Cargo.toml` version bump so the checked-in root package entry matches
     `0.8.15`

4. **Keep the release-overview docs contract aligned in the same PR.**
   Because `tests/test_docs_changelog_refresh.py` asserts the current release
   header and the current-version line verbatim, the release PR must update
   `analysis/technical/overview.md` and that test alongside `CHANGELOG.md`.

5. **Verify the GitHub release page by asset names, not just workflow
   existence.**
   The user-facing proof for this ticket is a published `v0.8.15` release with
   non-empty downloadable assets on the release page. A merged PR alone is not
   enough.

6. **If the release workflow stalls, retry the release workflow itself.**
   Closing or reopening the release PR will not retrigger
   `.github/workflows/release.yml`, because that workflow is driven by
   `release: types: [published]` or manual `workflow_dispatch`. Use `gh run rerun`
   or `gh workflow run release.yml -f tag=v0.8.15` instead, and document the
   exact stuck run/job if a follow-up ticket is needed.

## File Disposition

| File | Action | Notes |
|------|--------|-------|
| `pyproject.toml` | Modify | Bump `version = "0.8.14"` to `0.8.15` |
| `Cargo.toml` | Modify | Bump `version = "0.8.14"` to `0.8.15` |
| `uv.lock` | Modify | Refresh after `uv sync --extra dev` so root package version is `0.8.15` |
| `Cargo.lock` | Modify | Refresh after a Cargo command so the root package entry is `0.8.15` |
| `CHANGELOG.md` | Modify | Prepend `0.8.15` entry dated `2026-03-11` |
| `analysis/technical/overview.md` | Modify | Update the current-version line from `0.8.14 / 2026-03-10` to `0.8.15 / 2026-03-11` |
| `tests/test_docs_changelog_refresh.py` | Modify | Update the hardcoded release/date expectations to `0.8.15` and `2026-03-11` |
| `spec/` | No change | No outside-in CLI behavior changes are introduced by this release cut |

## CHANGELOG Entry

Prepend this block immediately below `# Changelog`:

```markdown
## 0.8.15 — 2026-03-11

- Fixed the planning-docs CI path regression so release validation uses the
  repo-local planning fixtures by default instead of an Ian-local absolute
  path. This is the fix from PR #191 that unblocks release packaging on
  GitHub Actions.
- Refreshed the public discovery docs so `search all` is taught as the unified
  cross-entity entry point in the README and docs index. This is the docs
  alignment from PR #190.
```

## Spec Impact

No `spec/` change is required. This repo is spec-capable, but P043 does not
change CLI behavior, output grammar, or outside-in command contracts. Per the
`architect/spec-writing` review guidance, this remains a docs-contract and
release-artifact ticket, not a new executable-spec ticket.

## Acceptance Criteria

- [ ] `pyproject.toml` and `Cargo.toml` both declare `0.8.15`
- [ ] `uv.lock` and `Cargo.lock` both reflect the root package version
  `0.8.15`
- [ ] `CHANGELOG.md` has a new top entry `## 0.8.15 — 2026-03-11`
- [ ] `analysis/technical/overview.md` says
  `**Current version:** 0.8.15 (as of 2026-03-11)`
- [ ] `tests/test_docs_changelog_refresh.py` expects `0.8.15 / 2026-03-11`
  instead of `0.8.14 / 2026-03-10`
- [ ] `./scripts/check-version-sync.sh` passes after the version bump
- [ ] Release-branch validation passes cleanly
- [ ] GitHub Release `v0.8.15` exists and is published
- [ ] `gh release view v0.8.15 --json assets` returns a non-empty asset array
  containing the 5 platform archives and 5 `.sha256` files:
  `biomcp-linux-x86_64.tar.gz`, `biomcp-linux-arm64.tar.gz`,
  `biomcp-darwin-x86_64.tar.gz`, `biomcp-darwin-arm64.tar.gz`,
  `biomcp-windows-x86_64.zip`, plus checksum counterparts
- [ ] `gh run view <release-run-id>` reports `status=completed` and
  `conclusion=success` for the `Release` workflow on `v0.8.15`
- [ ] `git merge-base --is-ancestor 6dcfec5 v0.8.15` exits `0`, proving the
  PR #191 merge commit is included in the release tag
- [ ] If the release workflow stalls again, the exact stuck run/job is
  documented and a follow-up ticket is created before P043 closes

## Verify Plan

```bash
# 1. Refresh release metadata and lockfiles
uv sync --extra dev
cargo check

# 2. Confirm version sync in checked-in files
./scripts/check-version-sync.sh
rg -n '0\.8\.15|2026-03-11' \
  pyproject.toml Cargo.toml uv.lock Cargo.lock CHANGELOG.md \
  analysis/technical/overview.md tests/test_docs_changelog_refresh.py

# 3. Run the same core gates that release validation runs
cargo fmt --check
cargo clippy -- -D warnings
cargo test
uv run pytest tests/ -v --mcp-cmd "biomcp serve"
uv run mkdocs build --strict

# 4. Confirm the release tag contains PR #191
git merge-base --is-ancestor 6dcfec5 v0.8.15 && echo "PR #191 included"

# 5. Confirm the release workflow completed successfully
gh run list --workflow=release.yml --limit 5
gh run view <release-run-id> --json status,conclusion,displayTitle

# 6. Confirm the GitHub release page has the expected downloadable assets
gh release view v0.8.15 --json assets --jq '.assets[].name'
```

## Stall Contingency

If the `Release` workflow remains `in_progress` instead of finishing:

1. Record the exact run ID and the stuck job name from `gh run view`.
2. Retry the release workflow itself with either:
   - `gh run rerun <release-run-id>`
   - `gh workflow run release.yml -f tag=v0.8.15`
3. Re-check `gh release view v0.8.15 --json assets` after the retry.
4. If the retry still stalls or fails for a new reason, open a follow-up ticket
   naming the run ID, job, and failure/stall mode before closing P043.
