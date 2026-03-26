# Code Log

## Summary

Rewrote the landing copy in `README.md` and `docs/index.md` to match the
approved marketing voice while preserving the shipped docs contract, command
examples, section order, and downstream public-doc assertions.

## Commands Run

- `checkpoint status`
- `checkpoint done 1`
- `checkpoint note "..."`
- `checkpoint done 2`
- `checkpoint done 3`
- `rg --files .march`
- `ls -la`
- `sed -n '1,220p' /home/ian/workspace/.agents/skills/checkpoint/SKILL.md`
- `sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/testing-mindset/SKILL.md`
- `sed -n '1,240p' .march/ticket.md`
- `sed -n '1,380p' .march/design-draft.md`
- `sed -n '1,380p' .march/design-final.md`
- `sed -n '1,260p' README.md`
- `sed -n '1,260p' docs/index.md`
- `sed -n '1,240p' tests/test_public_install_docs_contract.py`
- `sed -n '1,240p' tests/test_public_search_all_docs_contract.py`
- `sed -n '1,240p' tests/test_public_skill_docs_contract.py`
- `sed -n '1,240p' tests/test_docs_changelog_refresh.py`
- `sed -n '1,220p' /home/ian/workspace/marketing/.agents/product-marketing-context.md`
- `sed -n '1,240p' /home/ian/workspace/marketing/biomcp/presentations/biomcp-introduction/biomcp-introduction.md`
- `python3 - <<'PY' ...`
  - ran the approved structural landing-copy proof from
    `.march/design-final.md` before and after the rewrite
- `uv run --no-project --with pytest python -m pytest tests/test_public_install_docs_contract.py tests/test_public_search_all_docs_contract.py tests/test_public_skill_docs_contract.py tests/test_citation_contract.py tests/test_source_licensing_docs_contract.py tests/test_directory_submission_contract.py tests/test_bioasq_benchmark_contract.py tests/test_docs_changelog_refresh.py -q --noconftest`
- `uv run --no-project --with mkdocs-material --with pymdown-extensions mkdocs build --strict`
- `make check`
- `git status --short`
- `git add README.md docs/index.md`
- `git add -f .march/code-log.md`
- `git diff --cached --stat`
- `git diff --cached -- README.md docs/index.md .march/code-log.md`
- `git check-ignore -v .march/code-log.md .march/checkpoint.json`
- `git ls-files .march/code-log.md .march/checkpoint.json`

## Changes Made

- Updated `README.md`:
  - added a one-paragraph hero between `# BioMCP` and `## Description`
  - rewrote the `## Description` block in the approved product-marketing voice
  - rewrote the five `## Features` bullets as scannable capability copy
  - left installation, quick start, command grammar, and later sections intact
- Updated `docs/index.md`:
  - replaced the opening intro block before `## Install`
  - added a one-line lead sentence above the existing quick-start code block
  - rewrote the six `## Feature highlights` bullets to mirror the README voice
  - left install content, quick-start commands, command grammar, and later
    sections intact

## Proof / Tests Added

- No committed test files changed.
- Used the approved structural landing-copy Python check from
  `.march/design-final.md` as the proof-first gate.
  - It failed before the rewrite because the README lacked the required hero
    paragraph.
  - It passed after the rewrite once the README description preserved the exact
    `plus local study analytics` contract phrase.

## Verification

- Approved structural landing-copy proof: passed
- Targeted public docs contract suite: passed
  - 49 tests passed
- `uv run --no-project --with mkdocs-material --with pymdown-extensions mkdocs build --strict`
  - passed
- `make check`
  - passed
  - includes `./bin/lint`, `cargo fmt --check`, `cargo clippy -- -D warnings`,
    and `cargo test` (927 unit tests plus integration/doc tests)

## Deviations

- No design deviations.
- Operational note: concurrent `checkpoint` commands corrupted the ignored
  `.march/checkpoint.json` state file, so I repaired that local step-tracking
  file to continue the required checkpoint workflow. It is ignored by Git and
  not part of the ticket diff.
