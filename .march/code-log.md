# Code Log

## Commands run

```bash
checkpoint status
GIT_EDITOR=true git rebase main
git diff --stat main..HEAD | tail -1
sed -n '1,220p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,260p' .march/design-final.md
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/rust-standards/SKILL.md
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/testing-mindset/SKILL.md
rg -n "struct Drug|target_family|drug_targets\(|drug_sections\(|Targets \(ChEMBL / Open Targets\)|pembrolizumab|olaparib|imatinib|target_chembl_id|approvedName|approved_name" src templates spec
sed -n '1,110p' Makefile
cargo test drug_targets_requests_mechanism_endpoint --quiet
cargo test drug_sections --quiet
cargo test drug_markdown --quiet
cargo test target_summary_returns_pref_name_and_target_type --quiet
cargo test drug_markdown_shows_target_family_and_members_when_present --quiet
cargo test strict_target_family_label --quiet
cargo test derive_target_family_name --quiet
cargo test json_render_drug_entity --quiet
cargo test family_target_chembl_id_requires_single_matching_target_id --quiet
cargo test family_target_chembl_id --quiet
cargo test parse_sections_default_card_includes_targets_enrichment --quiet
cargo run --quiet --bin biomcp -- get drug olaparib targets
cargo run --quiet --bin biomcp -- --json get drug olaparib
cargo run --quiet --bin biomcp -- get drug pembrolizumab targets
cargo run --quiet --bin biomcp -- get drug imatinib targets
curl -s 'https://www.ebi.ac.uk/chembl/api/data/mechanism.json?molecule_chembl_id=CHEMBL521686&limit=15' | jq '{count: (.mechanisms|length), rows: [.mechanisms[] | {target_pref_name, target_chembl_id, action_type, mechanism_of_action}]}'
curl -s 'https://www.ebi.ac.uk/chembl/api/data/target/CHEMBL3390820.json' | jq '{pref_name, target_type}'
cargo build --bin biomcp
XDG_CACHE_HOME="$PWD/.cache" uv run --extra dev sh -c 'PATH="$PWD/target/debug:$PATH" pytest --mustmatch-lang bash --mustmatch-timeout 60 -v "spec/05-drug.md::Drug Target Family (line 170) [bash]" "spec/05-drug.md::Drug Target Family JSON (line 181) [bash]"'
cargo fmt
make check < /dev/null 2>&1
git status --short
git ls-files --others --exclude-standard
git diff --stat
git add spec/05-drug.md src/cli/mod.rs src/entities/drug.rs src/render/json.rs src/render/markdown.rs src/sources/chembl.rs src/sources/opentargets.rs src/transform/drug.rs templates/drug.md.j2
git diff --cached --stat
git commit -m "Show drug target family alongside targets"
```

## What changed

- Added additive `Drug.target_family` and `Drug.target_family_name` fields.
- Extended ChEMBL mechanism parsing to retain `target_chembl_id`, and added `ChemblClient::target_summary()`.
- Extended Open Targets drug target parsing to retain `approvedName`.
- Implemented target-family resolution in `enrich_targets()`:
  - gate on a single ChEMBL family target id
  - require `target_type == "PROTEIN FAMILY"`
  - derive the concise family label from strict numeric-suffix symbol prefixes
  - derive the expanded family name from shared Open Targets approved-name stems
- Enabled target enrichment for the default drug card / JSON path so additive family fields are computed outside section-only requests too.
- Updated markdown rendering to show:
  - `Family: ...`
  - `Members: ...`
- Updated JSON and Rust fixtures for the new additive fields.
- Added end-to-end spec coverage in `spec/05-drug.md`.

## Proof added or updated

- `src/sources/chembl.rs`
  - mechanism rows preserve `target_chembl_id`
  - target summary parses `pref_name` and `target_type`
- `src/sources/opentargets.rs`
  - drug target parsing preserves `approvedName`
- `src/entities/drug.rs`
  - strict family-symbol detection
  - mechanism-only ChEMBL family row handling
  - family-name derivation and incomplete-name rejection
  - default section parsing includes target enrichment
- `src/render/markdown.rs`
  - target family + members render path
- `src/render/json.rs`
  - additive JSON serialization for family fields
- `spec/05-drug.md`
  - olaparib family markdown output
  - olaparib additive JSON contract

## Verification results

- `make check < /dev/null 2>&1`: passed
- `cargo run --quiet --bin biomcp -- get drug olaparib targets`: showed `Family: PARP (poly(ADP-ribose) polymerase)` and `Members: PARP1, PARP2, PARP3`
- `cargo run --quiet --bin biomcp -- --json get drug olaparib`: included `target_family` and `target_family_name`
- `cargo run --quiet --bin biomcp -- get drug pembrolizumab targets`: remained plain `PDCD1`
- `cargo run --quiet --bin biomcp -- get drug imatinib targets`: remained plain mixed targets with no family line
- Targeted spec run for:
  - `Drug Target Family`
  - `Drug Target Family JSON`
  passed when `PATH` was forced inside the `uv run` shell to prefer `target/debug/biomcp` over the venv shim.

## Deviations from design

- None in the implementation itself.
- For local spec verification, the command needed to set `PATH="$PWD/target/debug:$PATH"` inside the `uv run ... sh -c` shell because `.venv/bin/biomcp` otherwise shadowed the freshly built local binary.
