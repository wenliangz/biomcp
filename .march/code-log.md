# Code Log

## Commands Run

```text
checkpoint status
git status --short --branch
GIT_EDITOR=true git rebase main
git diff --stat main..HEAD | tail -1
sed -n '1,220p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,260p' .march/design-final.md
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/rust-standards/SKILL.md
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/testing-mindset/SKILL.md
rg -n "hit_mentions_mechanism|build_mychem_query|mechanism_of_action|atc_classifications|StringOrVec|deoxycoformycin|--mechanism|--atc" src spec tests .
sed -n '1,260p' spec/05-drug.md
sed -n '150,280p' src/sources/mychem.rs
sed -n '400,840p' src/entities/drug.rs
sed -n '1980,2235p' src/entities/drug.rs
sed -n '1,120p' src/utils/serde.rs
sed -n '1,220p' Makefile
cargo test build_mychem_query -- --nocapture
cargo test mechanism_match_uses_mechanism_fields_not_drug_name -- --nocapture
./target/debug/biomcp search drug deoxycoformycin --limit 5
rg -n "cfg\\(test\\)|from_value|StringOrVec|MYCHEM_FIELDS_SEARCH|drug_mechanisms" src/sources/mychem.rs
pytest --collect-only -q spec/05-drug.md
cargo test atc_classifications_support_string_and_list -- --nocapture
cargo test build_mychem_query_includes_mechanism_of_action_field -- --nocapture
cargo test build_mychem_query_expands_purine_to_atc_codes -- --nocapture
cargo test hit_mentions_mechanism_matches_atc_purine_hits -- --nocapture
cargo test mechanism_atc_expansions_returns_purine_mapping -- --nocapture
cargo build --release --locked
uv run --extra dev sh -c 'PATH="$PWD/target/release:$PATH" pytest spec/05-drug.md --mustmatch-lang bash --collect-only -q'
uv run --extra dev sh -c 'PATH="$PWD/target/release:$PATH" pytest spec/05-drug.md --mustmatch-lang bash --mustmatch-timeout 60 -v -k "Deoxycoformycin or Leukemia or Purine"'
cargo fmt
git diff --stat
git diff -- src/entities/drug.rs src/sources/mychem.rs spec/05-drug.md
git add src/entities/drug.rs src/sources/mychem.rs spec/05-drug.md
git commit -m "Improve purine drug mechanism search coverage"
make check < /dev/null > /tmp/086-make-check.log 2>&1
tail -n 40 /tmp/086-make-check.log
git status --short --branch
git diff --stat HEAD~1..HEAD
```

## What Changed

- Added `chembl.atc_classifications` to MyChem search fields and parsed it on `MyChemChembl` with the existing `StringOrVec` pattern in `src/sources/mychem.rs`.
- Extended drug mechanism query construction in `src/entities/drug.rs` to search `chembl.drug_mechanisms.mechanism_of_action` alongside the existing action type and NDC pharm class fields.
- Added a narrow purine-only ATC expansion in `src/entities/drug.rs`:
  `L01BB*` for purine analogues and exact `L01XX08` for pentostatin.
- Kept query construction and local post-filtering aligned by reusing the same purine ATC expansion helper in both paths.
- Added Rust unit coverage for ATC parsing, `mechanism_of_action` query clauses, purine ATC expansion, and ATC-backed mechanism matching.
- Added executable spec coverage in `spec/05-drug.md` for:
  purine mechanism search,
  leukemia + purine combined search,
  and `deoxycoformycin -> pentostatin` alias resolution.

## Proof Added Or Updated

- `cargo test atc_classifications_support_string_and_list -- --nocapture`
- `cargo test build_mychem_query_includes_mechanism_of_action_field -- --nocapture`
- `cargo test build_mychem_query_expands_purine_to_atc_codes -- --nocapture`
- `cargo test hit_mentions_mechanism_matches_atc_purine_hits -- --nocapture`
- `cargo test mechanism_atc_expansions_returns_purine_mapping -- --nocapture`
- `uv run --extra dev sh -c 'PATH="$PWD/target/release:$PATH" pytest spec/05-drug.md --mustmatch-lang bash --mustmatch-timeout 60 -v -k "Deoxycoformycin or Leukemia or Purine"'`
- `make check < /dev/null > /tmp/086-make-check.log 2>&1`

## Results

- Red proof failed first because `MyChemChembl` did not yet expose `atc_classifications`.
- After implementation, the new unit tests passed.
- Live spec verification passed for the three new drug-search contracts.
- `make check` passed.

## Deviations From Design

- None.
