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

## Filtering by Phase

Trial phase helps separate exploratory from confirmatory evidence. The phase-specific query marker should be present with the standard trial table.

```bash
out="$(biomcp search trial -c melanoma -p 3 --limit 3)"
echo "$out" | mustmatch like "phase=3"
echo "$out" | mustmatch like "|NCT ID|Title|Status|Phase|Conditions|"
```

## Mutation Search

Mutation-centric search must surface trials where the mutation term appears in title, summary, or keywords, not only in eligibility criteria text. This regression guards against the G12D undercounting bug.

```bash
out="$(biomcp search trial -c "pancreatic cancer" --mutation "G12D" --phase 3)"
echo "$out" | mustmatch like "mutation=G12D"
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
