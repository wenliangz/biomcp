# Code Log

## Commands Run

```bash
checkpoint status
GIT_EDITOR=true git rebase main
git diff --stat main..HEAD | tail -1
sed -n '1,240p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,520p' .march/design-final.md
sed -n '1,260p' tests/test_quality_ratchet_contract.py
sed -n '1,220p' tests/test_version_sync_script.py
sed -n '1,220p' tests/test_citation_contract.py
sed -n '1,220p' tests/test_docs_changelog_refresh.py
sed -n '1,320p' tools/check-quality-ratchet.sh
sed -n '1,260p' tools/check-mcp-allowlist.py
sed -n '1,260p' tools/check-source-registry.py
git log --oneline v0.8.19..HEAD
uv --version
python3 --version
bash tools/check-quality-ratchet.sh
uv run pytest tests/test_quality_ratchet_contract.py tests/test_version_sync_script.py tests/test_citation_contract.py tests/test_docs_changelog_refresh.py -v
uvx --from mustmatch==0.0.4 python -m mustmatch lint <fixture> --min-like-len 10 --json
uv lock --upgrade-package mustmatch
cargo update -w
python3 -m py_compile tools/check-quality-ratchet.py tools/check-mcp-allowlist.py tools/check-source-registry.py
.venv/bin/pytest tests/test_quality_ratchet_contract.py tests/test_version_sync_script.py tests/test_citation_contract.py tests/test_docs_changelog_refresh.py -v
bash scripts/check-version-sync.sh
.venv/bin/python tools/check-quality-ratchet.py --root-dir . --output-dir .march/reality-check --spec-glob 'spec/*.md' --cli-file src/cli/mod.rs --shell-file src/mcp/shell.rs --build-file build.rs --sources-dir src/sources --sources-mod src/sources/mod.rs --health-file src/cli/health.rs
uvx --from mustmatch==0.0.4 python -m mustmatch verify-matrix .march/design-final.md --repo-root . --json
git add tests/test_quality_ratchet_contract.py tests/test_version_sync_script.py tests/test_citation_contract.py tests/test_docs_changelog_refresh.py
git commit -m "test: prove v0.8.20 release prep"
make check < /dev/null > .march/make-check.log 2>&1
git add CHANGELOG.md CITATION.cff Cargo.lock Cargo.toml architecture/technical/overview.md manifest.json pyproject.toml tools/check-quality-ratchet.sh tools/check-quality-ratchet.py uv.lock
git commit -m "build: prepare v0.8.20 release"
git status --short
git log --oneline --decorate -2
```

## What Changed

- Added proof-first contract coverage for the approved release state:
  `0.8.20` version metadata, the `0.8.20` changelog block, and a thin
  `tools/check-quality-ratchet.sh` wrapper that delegates to a committed
  Python tool.
- Moved the quality-ratchet implementation out of the shell heredoc into
  `tools/check-quality-ratchet.py`, preserving the existing artifact schema
  and audit orchestration.
- Switched spec linting to packaged `mustmatch lint` and kept the repo's
  compatibility delta for `invalid-mustmatch-mode` and `short-like-pattern`,
  because upstream `mustmatch 0.0.4` does not report those begin-of-line
  fenced cases the same way the existing contract requires.
- Updated release metadata to `0.8.20` across `Cargo.toml`, `Cargo.lock`,
  `pyproject.toml`, `uv.lock`, `manifest.json`, and `CITATION.cff`, and bumped
  the dev dependency floor to `mustmatch>=0.0.4`.
- Added the `0.8.20 — 2026-03-30` changelog entry covering the shipped delta
  from `v0.8.19..HEAD`.
- Updated `architecture/technical/overview.md` so the post-tag public proof
  example uses the current release tag (`v0.8.20`).

## Proof Added

- Contract: `test_wrapper_is_thin_shell_around_committed_python_tool`
- Contract: repo metadata tests now require `0.8.20`
- Contract: changelog refresh test now requires the `0.8.20` release block

## Verification Results

- Baseline before edits:
  `uv run pytest tests/test_quality_ratchet_contract.py tests/test_version_sync_script.py tests/test_citation_contract.py tests/test_docs_changelog_refresh.py -v`
  passed with the pre-change repo state.
- Red proof after test updates:
  the same focused suite failed on the missing committed ratchet tool and the
  stale `0.8.19` release surfaces.
- Focused green verification after implementation:
  `.venv/bin/pytest tests/test_quality_ratchet_contract.py tests/test_version_sync_script.py tests/test_citation_contract.py tests/test_docs_changelog_refresh.py -v`
  passed.
- Version sync:
  `bash scripts/check-version-sync.sh`
  passed with `Versions in sync: 0.8.20`.
- Ratchet tool:
  `.venv/bin/python tools/check-quality-ratchet.py ...`
  passed and rewrote the reality-check JSON artifacts.
- Design proof matrix:
  `uvx --from mustmatch==0.0.4 python -m mustmatch verify-matrix .march/design-final.md --repo-root . --json`
  returned `status: "pass"`.
- Full repo gate:
  `make check < /dev/null > .march/make-check.log 2>&1`
  passed.

## Commits

- `7043a52` `test: prove v0.8.20 release prep`
- `e8dcc55` `build: prepare v0.8.20 release`

## Deviations From Design

- The draft design expected the packaged `mustmatch lint` output to be fully
  contract-identical. The final implementation follows the approved final
  design instead: it uses packaged `mustmatch lint` as the primary linter and
  preserves only the narrow repo compatibility layer needed for the existing
  ratchet contract.
- Tagging `v0.8.20`, pushing the tag, and publishing the release were not done
  in the code-change step. That remains the explicit post-merge operational
  handoff described in the final design.
