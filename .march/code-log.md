# Code Log

## Commands run

```bash
checkpoint status
sed -n '1,220p' .march/ticket.md
sed -n '1,220p' .march/design-draft.md
sed -n '1,260p' .march/design-final.md
rg -n "to_entity_json|to_pretty\\(&results\\)|Commands::Batch|batch_gene_json|next_commands_json_property|evidence-urls" src spec Cargo.toml
sed -n '1,260p' src/render/json.rs
sed -n '4980,5285p' src/cli/mod.rs
sed -n '10120,10720p' src/cli/mod.rs
sed -n '1,260p' spec/11-evidence-urls.md
cargo test batch_gene_json_includes_meta_per_item
cargo test to_entity_json_value_adds_meta_and_flattens_entity
cargo test batch_protein_json_omits_requested_section_from_next_commands
cargo test batch_adverse_event_json_uses_variant_specific_meta
cargo test batch_gene_json_includes_meta_per_item
cargo fmt --all
./bin/lint
cargo test
python3 -m pytest spec/11-evidence-urls.md --mustmatch-lang bash --mustmatch-timeout 60 -v
uv run --extra dev sh -c 'PATH="$(pwd)/target/debug:$PATH" pytest spec/11-evidence-urls.md --mustmatch-lang bash --mustmatch-timeout 60 -v'
ps -ef | rg "pytest spec/11-evidence-urls|uv run --extra dev|mustmatch"
kill 1949837
git status --short
```

## What changed

- Added `to_entity_json_value` in `src/render/json.rs` and refactored
  `to_entity_json` to pretty-print that typed value so batch JSON can reuse the
  exact single-entity `_meta` contract without string round-trips.
- Added `render_batch_json` in `src/cli/mod.rs`.
- Updated every `Commands::Batch` JSON branch to wrap each item with the same
  evidence URL, next-command, and section-source helpers used by the matching
  `get` command.
- Preserved the array root shape for `batch --json`.
- Kept markdown batch rendering unchanged.
- Added focused Rust tests for:
  - typed entity JSON value rendering
  - end-to-end `batch gene --json` metadata contract
  - protein batch next-command filtering for requested sections
  - adverse-event batch variant-specific metadata
- Added a spec section to `spec/11-evidence-urls.md` covering the batch JSON
  metadata contract.

## Proof added or updated

- `render::json::tests::to_entity_json_value_adds_meta_and_flattens_entity`
- `cli::tests::batch_gene_json_includes_meta_per_item`
- `cli::next_commands_json_property::batch_protein_json_omits_requested_section_from_next_commands`
- `cli::next_commands_json_property::batch_adverse_event_json_uses_variant_specific_meta`
- `spec/11-evidence-urls.md` section `Batch JSON Metadata Contract`

## Verification

- `cargo test batch_gene_json_includes_meta_per_item`
  - initially failed before implementation because batch JSON emitted bare
    entity objects with no `_meta`
  - passes after the fix
- `cargo test to_entity_json_value_adds_meta_and_flattens_entity`
- `cargo test batch_protein_json_omits_requested_section_from_next_commands`
- `cargo test batch_adverse_event_json_uses_variant_specific_meta`
- `cargo fmt --all`
- `./bin/lint`
- `cargo test`

## Deviations / notes

- The design’s direct spec command used `.venv/bin/python`, but that virtualenv
  did not exist initially in this worktree.
- `python3 -m pytest ... --mustmatch-*` failed because the `mustmatch` plugin
  was not installed in the system interpreter.
- I retried using the repo’s supported `uv run --extra dev ... pytest ...`
  command from `Makefile`, which created `.venv` but then hung without producing
  observable test output in this session, so I terminated that process after the
  Rust verification had already passed.
