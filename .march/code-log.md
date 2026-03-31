# Code Log

## Execution Order
1. Baseline the current proof surface for ticket 092 (`cargo test` and targeted specs), confirm external preconditions, then lock the red proof additions to the approved design. — status: done
2. Add failing proof for unique `get drug` fallback, compact/raw label contract, and scoped trial zero-result hint; run the targeted proofs to capture red. — status: done
3. Implement the drug entity and CLI contract changes: unique fallback inside `resolve_drug_base()`, compact/raw label data model, `--raw` validation, and operator-facing help/list updates; compile and run targeted tests. — status: done
4. Implement the scoped trial zero-result hint render path and supporting tests/specs; run targeted Rust/spec proof until green. — status: done
5. Run formatting and full verification (`make check`), review/stage the intended diff, and write the final code log with deviations/proof results. — status: done

## Resume State
- Last completed batch: 5
- Files edited so far: .march/code-log.md, spec/05-drug.md, spec/04-trial.md, src/cli/mod.rs, src/cli/list.rs, src/render/markdown.rs, src/entities/drug.rs, templates/drug.md.j2, templates/trial_search.md.j2
- Existing partial edits: replace stale prior-ticket code log only; preserve repo source as-is
- Tests passing: yes — focused Rust tests passed, the edited markdown nodes passed against `./target/release/biomcp`, `./tools/check-quality-ratchet.sh` passed after the spec-lint fix, and `make check < /dev/null 2>&1` passed on the second full run
- Next concrete action: none
- Current blocker: none

## Out of Scope
- Adding a `--no-fallback` switch for `get drug`
- Inventing per-indication approval dates or pivotal trials when current sources do not support a confident mapping
- Broadening the trial nickname hint beyond positional ClinicalTrials.gov zero-result searches
- Changing the existing general `indications` section contract beyond preserving it

## Commands and Changes
- `checkpoint status`
- `GIT_EDITOR=true git rebase main`
- `git diff --stat main..HEAD | tail -1`
- `sed -n '1,220p' .march/ticket.md`
- `sed -n '1,260p' .march/design-final.md`
- `sed -n '1,260p' .march/design-draft.md`
- `sed -n '1,260p' .march/investigation-notes.md`
- `sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/rust-standards/SKILL.md`
- `sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/python-standards/SKILL.md`
- `sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/testing-mindset/SKILL.md`
- `rg -n "resolve_drug_base|extract_inline_label|DrugLabel|indication_summary|trial_search_markdown_with_footer|GetEntity::Drug|search_results_from_openfda_label_response|DrugSearchFilters" src templates spec`
- `sed -n '90,140p' src/entities/drug.rs`
- `sed -n '610,740p' src/entities/drug.rs`
- `sed -n '960,1045p' src/entities/drug.rs`
- `sed -n '1920,2045p' src/entities/drug.rs`
- `sed -n '1335,1385p' src/cli/mod.rs`
- `sed -n '5940,6035p' src/cli/mod.rs`
- `sed -n '1,180p' templates/drug.md.j2`
- `sed -n '1,180p' templates/trial_search.md.j2`
- `sed -n '2398,2465p' src/render/markdown.rs`
- `sed -n '10520,10610p' src/cli/mod.rs`
- `sed -n '80,180p' spec/05-drug.md`
- `sed -n '160,220p' spec/04-trial.md`
- `cargo test get_drug_ -- --nocapture`
- `cargo test search_drug_help_mentions_default_all_and_structured_filter_note -- --nocapture`
- `cargo test drug_alias_fallback_returns_exit_1_markdown_suggestion -- --nocapture`
- `cargo test list_drug_describes_omitted_region_behavior -- --nocapture`
- `uv run --extra dev pytest spec/05-drug.md spec/04-trial.md --collect-only -q`
- `uv run --extra dev pytest 'spec/05-drug.md::Get Drug Help Surfaces Supported Sections (line 112) [bash]' 'spec/05-drug.md::Drug List Documents Region Grammar (line 127) [bash]' 'spec/04-trial.md::Trial Help Explains Special Filter Semantics (line 168) [bash]' --mustmatch-lang bash --mustmatch-timeout 60 -v`
- `rg -n "mount_drug_lookup_|label_search|BIOMCP_OPENFDA_BASE|MockServer|trial_search_markdown_with_footer\(|No trials found matching the filters|GetEntity::Drug \{|raw:" src/cli/mod.rs src/entities/drug.rs src/render/markdown.rs`
- `sed -n '6920,7065p' src/cli/mod.rs`
- `sed -n '4240,4315p' src/render/markdown.rs`
- `sed -n '1,120p' spec/05-drug.md`
- `sed -n '1,175p' spec/04-trial.md`
- `cargo test get_drug_help_mentions_raw_label_mode -- --nocapture`
- `uv run --extra dev pytest spec/05-drug.md spec/04-trial.md --collect-only -q`
- `uv run --extra dev pytest 'spec/05-drug.md::Brand Name Get Fallback (line 53) [bash]' 'spec/05-drug.md::Compact FDA Label Summary (line 124) [bash]' 'spec/05-drug.md::Raw FDA Label Output (line 139) [bash]' 'spec/05-drug.md::Get Drug Help Surfaces Supported Sections (line 152) [bash]' 'spec/05-drug.md::Drug List Documents Region Grammar (line 169) [bash]' 'spec/04-trial.md::Zero-Result Positional Hint (line 137) [bash]' --mustmatch-lang bash --mustmatch-timeout 120 -v`
- `stat -c '%y %n' target/debug/biomcp`
- `PATH="$(pwd)/target/debug:$PATH" biomcp --version`
- `PATH="$(pwd)/target/debug:$PATH" biomcp get drug --help`
- `PATH="$(pwd)/target/debug:$PATH" biomcp list drug`
- `PATH="$(pwd)/target/debug:$PATH" biomcp get drug XIPERE`
- `PATH="$(pwd)/target/debug:$PATH" biomcp get drug pembrolizumab label`
- `PATH="$(pwd)/target/debug:$PATH" biomcp get drug pembrolizumab label --raw`
- `PATH="$(pwd)/target/debug:$PATH" biomcp search trial "CodeBreaK 300"`
- `rg -n '^spec-pr:|PATH=\"\\$\\(CURDIR\\)/target/release:\\$\\(PATH\\)\"|target/release/biomcp' Makefile tests/test_upstream_planning_analysis_docs.py -S`
- `sed -n '1,260p' Makefile`
- `sed -n '560,640p' tests/test_upstream_planning_analysis_docs.py`
- `cargo build --release --locked`
- `BIOMCP_BIN="$(pwd)/target/release/biomcp" XDG_CACHE_HOME="$(pwd)/.cache" uv run --extra dev pytest 'spec/05-drug.md::Brand Name Get Fallback (line 53) [bash]' 'spec/05-drug.md::Compact FDA Label Summary (line 125) [bash]' 'spec/05-drug.md::Raw FDA Label Output (line 141) [bash]' 'spec/05-drug.md::Get Drug Help Surfaces Supported Sections (line 155) [bash]' 'spec/05-drug.md::Drug List Documents Region Grammar (line 173) [bash]' 'spec/04-trial.md::Zero-Result Positional Hint (line 137) [bash]' --mustmatch-lang bash --mustmatch-timeout 120 -v`
- `checkpoint note "Batch 4 complete: release-binary CLI checks and targeted spec nodes are green; moving into Rust recheck, commit, and full verification."`
- `checkpoint status`
- `cargo test extract_inline_label_ -- --nocapture`
- `cargo test trial_search_markdown_with_footer_ -- --nocapture`
- `cargo test list_drug_documents_raw_label_mode -- --nocapture`
- `cargo fmt`
- `git add spec/04-trial.md spec/05-drug.md src/cli/list.rs src/cli/mod.rs src/entities/drug.rs src/render/markdown.rs templates/drug.md.j2 templates/trial_search.md.j2`
- `git commit -m "Improve drug resolution and raw label fallback"` (`84fc261`)
- `make check < /dev/null > /tmp/092-make-check.log 2>&1` (first run: lint/tests passed; failed in `check-quality-ratchet`)
- `find .march/reality-check -maxdepth 2 -type f | sort`
- `sed -n '1,220p' .march/reality-check/quality-ratchet-lint.json`
- `BIOMCP_BIN="$(pwd)/target/release/biomcp" XDG_CACHE_HOME="$(pwd)/.cache" uv run --extra dev pytest 'spec/05-drug.md::Get Drug Help Surfaces Supported Sections (line 155) [bash]' --mustmatch-lang bash --mustmatch-timeout 120 -v`
- `./tools/check-quality-ratchet.sh`
- `make check < /dev/null > /tmp/092-make-check-2.log 2>&1` (second run: pass)
- `git add spec/05-drug.md`
- `git commit -m "Fix drug spec quality-ratchet assertion"` (`7aa9635`)
- `git status --short`
- `git diff --cached --stat`
- `git log --oneline main..HEAD`

- Changes:
- Added a unique brand-name fallback in `resolve_drug_base()` that reuses existing drug search data only when it resolves to one canonical match, preserving the existing not-found guidance for ambiguous misses.
- Split FDA label rendering into a compact default summary (`indication_summary`) and explicit `--raw` mode, including CLI parsing/validation, Markdown rendering, and JSON support.
- Updated `get drug --help`, `list drug`, and the drug/trial Markdown templates to document the raw-label mode and the scoped zero-result nickname hint.
- Updated executable specs to cover the new behavior and to honor `BIOMCP_BIN` for the touched live-network blocks so targeted proof can pin the release artifact deterministically.

## Deviations from Design
- The markdown spec collector in this repo still skips some later bash blocks in `spec/05-drug.md` (for example the newly added compact/raw label JSON sections, mirroring the existing skipped `Compact Approval Fields` block). I kept the operator-facing spec text on disk, but the machine-enforced proof for the compact JSON contract will need to live in Rust tests unless the collector behavior changes.
