# Trial Queries

Trial search in BioMCP supports condition-first exploration with clinical filters for status, phase, and mutation-centric discovery. This file validates search cards plus sectioned trial retrieval for one known NCT record. Assertions remain structural so they are resilient to changing trial inventories.

| Section | Command focus | Why it matters |
|---|---|---|
| Condition search | `search trial -c melanoma` | Confirms baseline trial retrieval |
| Status filter | `search trial ... -s recruiting` | Confirms recruitment filtering |
| Phase filter | `search trial ... -p 3` | Confirms phase filtering |
| Mutation search | `search trial ... --mutation G12D` | Confirms mutation search query echo and table shape |
| Trial detail | `get trial NCT02576665` | Confirms trial card structure |
| Eligibility section | `get trial ... eligibility` | Confirms criteria expansion |
| Locations section | `get trial ... locations` | Confirms site listing expansion |

## Searching by Condition

Condition-based search is the default entrypoint for clinical trial discovery. The output should include trial table columns and the condition query echo.

```bash
out="$(biomcp search trial -c melanoma --limit 3)"
echo "$out" | mustmatch like "|NCT ID|Title|Status|Phase|Conditions|"
echo "$out" | mustmatch like "condition=melanoma"
```

## Filtering by Status

Recruitment status is often the first triage filter for study feasibility. We assert on explicit status echo and unchanged table schema.

```bash
out="$(biomcp search trial -c melanoma -s recruiting --limit 3)"
echo "$out" | mustmatch like "status=recruiting"
echo "$out" | mustmatch like "|NCT ID|Title|Status|Phase|Conditions|"
```

## Age Filter Count Stability

Age-only count-only search must stay on the cheap CTGov total path regardless
of display limit. This guards the regression where age was incorrectly grouped
with expensive detail-verified post-filters and `Total:` changed with `--limit`.

```bash
t10="$("$(git rev-parse --show-toplevel)/target/release/biomcp" search trial -c melanoma -s recruiting --age 51 --limit 10 --count-only | sed -n 's/^Total: \([0-9]*\).*/\1/p')"
t20="$("$(git rev-parse --show-toplevel)/target/release/biomcp" search trial -c melanoma -s recruiting --age 51 --limit 20 --count-only | sed -n 's/^Total: \([0-9]*\).*/\1/p')"
t50="$("$(git rev-parse --show-toplevel)/target/release/biomcp" search trial -c melanoma -s recruiting --age 51 --limit 50 --count-only | sed -n 's/^Total: \([0-9]*\).*/\1/p')"
test -n "$t10"
test "$t10" = "$t20"
test "$t20" = "$t50"
```

## Age-Only Count Approximation Signal

When age is the only non-API filter, `--count-only` must signal that the total
comes from the upstream CTGov fast-count path and is only approximate after
BioMCP's client-side age post-filter.

```bash timeout=180
out="$("$(git rev-parse --show-toplevel)/target/release/biomcp" search trial -c melanoma -s recruiting --age 51 --count-only)"
echo "$out" | mustmatch like "Total: "
echo "$out" | mustmatch like "(approximate, age post-filtered)"

json_out="$("$(git rev-parse --show-toplevel)/target/release/biomcp" search trial -c melanoma -s recruiting --age 51 --count-only --json)"
echo "$json_out" | mustmatch like "\"total\":"
echo "$json_out" | mustmatch like "\"approximate\": true"
```

## Expensive Count Traversal Cap

When facility or eligibility verification forces the expensive detail-fetch
path, `--count-only` must stop at the traversal cap and report an unknown total
instead of a misleading lower bound.

Contract note:
Text output is `Total: unknown (traversal limit reached)` and JSON output is
`{"total": null}` when the traversal cap is hit. This is regression-covered in
`src/entities/trial.rs` unit tests because a real live-spec query broad enough
to exhaust the cap would require large-scale per-study detail fetches and is
not stable enough for the executable spec suite.

## Fractional Age Filter

Fractional year input matters because ClinicalTrials.gov eligibility often uses
months for pediatric studies. This regression guards the truncation bug that
rejected `--age 0.5`.

```bash timeout=180
out="$("$(git rev-parse --show-toplevel)/target/release/biomcp" search trial --age 0.5 --count-only)"
echo "$out" | mustmatch like "Total: "
echo "$out" | grep -qE "^Total: [0-9]+"
```

## Filtering by Phase

Trial phase helps separate exploratory from confirmatory evidence. The phase-specific query marker should be present with the standard trial table.

```bash
out="$(biomcp search trial -c melanoma -p 3 --limit 3)"
echo "$out" | mustmatch like "phase=3"
echo "$out" | mustmatch like "|NCT ID|Title|Status|Phase|Conditions|"
```

## Combined Phase 1 and 2 Search

The `1/2` shorthand should preserve the raw query echo while broadening to the combined ClinicalTrials.gov phase bucket. This regression guards the overly narrow early-phase mapping bug.

```bash
out="$("$(git rev-parse --show-toplevel)/target/release/biomcp" search trial -c melanoma --phase 1/2 --limit 3)"
echo "$out" | mustmatch like "phase=1/2"
echo "$out" | mustmatch like "|NCT ID|Title|Status|Phase|Conditions|"
```

## Mutation Search

Mutation-centric search must surface trials where the mutation term appears in title, summary, or keywords, not only in eligibility criteria text. This regression guards against the G12D undercounting bug.

```bash
out="$(biomcp search trial -c "pancreatic cancer" --mutation "G12D" --phase 3)"
echo "$out" | mustmatch like "mutation=G12D"
echo "$out" | mustmatch like "|NCT ID|Title|Status|Phase|Conditions|"
```

## Intervention Code Punctuation Normalization

Intervention code searches should normalize the confirmed space-delimited drug-code pattern before dispatch. The CLI should still echo the user query while returning the standard trial table.

```bash
out="$("$(git rev-parse --show-toplevel)/target/release/biomcp" search trial -c "pancreatic cancer" --intervention "HRS 4642" --limit 1)"
echo "$out" | mustmatch like "intervention=HRS 4642"
echo "$out" | mustmatch like "|NCT ID|Title|Status|Phase|Conditions|"
```

## Getting Trial Details

`get trial` provides protocol identity and key metadata in a compact card. We assert on stable NCT heading and status field marker.

```bash
out="$(biomcp get trial NCT02576665)"
echo "$out" | mustmatch like "# NCT02576665"
echo "$out" | mustmatch like "Status:"
```

## Eligibility Section

Eligibility content captures inclusion and exclusion criteria needed for screening workflows. The test targets the section heading and a canonical inclusion label.

```bash
out="$(biomcp get trial NCT02576665 eligibility)"
echo "$out" | mustmatch like "## Eligibility"
echo "$out" | mustmatch like "Inclusion Criteria"
```

## Locations Section

Site listings support geographic feasibility checks and referral planning. The output should include the locations heading and a stable column schema.

```bash
out="$(biomcp get trial NCT02576665 locations --limit 3)"
echo "$out" | mustmatch like "## Locations"
echo "$out" | mustmatch like "| Facility | City | Country | Status | Contact |"
```

## Trial Help Explains Special Filter Semantics

The trial help output should explain the three non-obvious filter behaviors that
otherwise surprise operators: facility text-search versus geo-verify cost,
ClinicalTrials.gov's combined `1/2` phase label, and `--sex all` meaning no sex
restriction.

```bash
out="$(biomcp search trial --help)"
echo "$out" | mustmatch like "text-search mode"
echo "$out" | mustmatch like "geo-verify mode"
echo "$out" | mustmatch like "materially more expensive"
echo "$out" | mustmatch like "combined Phase 1/Phase 2 label"
echo "$out" | mustmatch like "not Phase 1 OR Phase 2"
echo "$out" | mustmatch like "no sex restriction"
echo "$out" | tr '\n' ' ' | mustmatch like "age-only CTGov searches report an approximate upstream total"
```
