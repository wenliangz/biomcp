# Drug and Safety Queries

Drug commands connect mechanism and target context with trial and adverse-event pivots. This file checks both core drug retrieval and OpenFDA-backed safety summaries. Assertions use durable headings and table columns instead of volatile report content.

| Section | Command focus | Why it matters |
|---|---|---|
| EMA health readiness | `biomcp health` | Confirms the local EMA batch is surfaced as an operator-readable readiness row |
| Drug search | `search drug pembrolizumab --region us` | Confirms stable U.S. name-based lookup |
| Drug detail | `get drug pembrolizumab` | Confirms mechanism/target card |
| Targets section | `get drug ... targets` | Confirms progressive disclosure |
| Trial helper | `drug trials pembrolizumab` | Confirms intervention-based trial pivot |
| Adverse-event helper | `drug adverse-events pembrolizumab` | Confirms safety signal pivot |
| Adverse-event search | `search adverse-event -d ibuprofen` | Confirms direct safety search |

## EMA Health Readiness

Full `biomcp health` should expose local EMA readiness separately from the API-only inventory so operators can confirm EU drug prerequisites before debugging query output.

```bash
bash fixtures/setup-ema-spec-fixture.sh "$PWD"
. "$PWD/.cache/spec-ema-env"
out="$(biomcp health)"
echo "$out" | mustmatch like "EMA local data ($BIOMCP_EMA_DIR)"
echo "$out" | mustmatch like "| EMA local data ($BIOMCP_EMA_DIR) | configured |"
```

## Searching by Name

Name-first search is the stable PR-gate coverage for generic U.S. lookup
without the EMA local-data dependency. This section runs with
`BIOMCP_EMA_DIR` unset and fresh XDG roots so a regression back to EMA
auto-sync is visible immediately. The later EMA-seeded sections cover the
default U.S.+EU no-flag path and the explicit EU/all-region variants.

```bash
tmp_data="$(mktemp -d)"
tmp_cache="$(mktemp -d)"
err="$(mktemp)"
out="$(env -u BIOMCP_EMA_DIR XDG_DATA_HOME="$tmp_data" XDG_CACHE_HOME="$tmp_cache" biomcp search drug pembrolizumab --region us --limit 3 2>"$err")"
echo "$out" | mustmatch like "# Drugs: pembrolizumab"
echo "$out" | mustmatch like "|Name|Mechanism|Target|"
cat "$err" | mustmatch not like "Downloading EMA data"
test ! -d "$tmp_data/biomcp/ema"
```

## Search Help Shows Region Defaults

The inline help should advertise the no-flag cross-region default while keeping
the structured-filter exception explicit.

```bash
out="$(biomcp search drug --help)"
echo "$out" | mustmatch '/\[default: all\]/'
echo "$out" | mustmatch like "Omitting --region on a plain name/alias search checks both U.S. and EU data."
echo "$out" | mustmatch like "If you omit --region while using structured filters such as --target or --indication, BioMCP stays on the U.S. MyChem path."
```

## Getting Drug Details

`get drug` expands mechanism, targets, indications, and key metadata. We assert on the normalized heading and a stable metadata/section marker.

```bash
out="$(biomcp get drug pembrolizumab)"
echo "$out" | mustmatch like "# pembrolizumab"
echo "$out" | mustmatch like "DrugBank ID: DB09037"
echo "$out" | mustmatch like "## Targets"
```

## Drug Indications

Indications are sourced from OpenTargets and should render user-facing stage labels instead of leaking GraphQL failures or raw field names. This checks the repaired indication path without binding the spec to a particular disease row.

```bash
out="$(biomcp get drug pembrolizumab indications)"
echo "$out" | mustmatch like "## Indications (Open Targets)"
echo "$out" | mustmatch not like "Cannot query field"
echo "$out" | mustmatch '/\((Approved|Phase [0-9](\/[0-9])?|Early Phase 1)\)/'
```

## Get Drug Help Surfaces Supported Sections

The inline help should agree with `biomcp list drug` and the implementation for
supported typed sections, including the regional EMA additions.

```bash
out="$(biomcp get drug --help)"
echo "$out" | mustmatch like "approvals"
echo "$out" | mustmatch like "civic"
echo "$out" | mustmatch like "label"
echo "$out" | mustmatch like "regulatory"
echo "$out" | mustmatch like "safety"
echo "$out" | mustmatch like "--region <REGION>"
echo "$out" | mustmatch like "biomcp get drug pembrolizumab approvals"
echo "$out" | mustmatch like "biomcp get drug Keytruda regulatory --region eu"
```

## Drug List Documents Region Grammar

`biomcp list drug` is the concise grammar contract for region-aware drug
sections and the MCP help mirror. The list output should continue to document
the same regional section grammar that `get drug --help` exposes.

```bash
out="$(biomcp list drug)"
echo "$out" | mustmatch like "get drug <name> regulatory [--region <us|eu|all>]"
echo "$out" | mustmatch like "get drug <name> safety [--region <us|eu|all>]"
echo "$out" | mustmatch like "get drug <name> shortage [--region <us|eu|all>]"
```

## Compact Approval Fields

Drug JSON should expose additive approval aliases and a compact summary so approval questions do not require parsing the base card prose.

```bash
out="$(biomcp --json get drug pembrolizumab)"
echo "$out" | jq -e '.approval_date | type == "string"' > /dev/null
echo "$out" | jq -e '.approval_date_raw | type == "string"' > /dev/null
echo "$out" | jq -e '.approval_date == .approval_date_raw' > /dev/null
echo "$out" | jq -e '.approval_date_display | type == "string"' > /dev/null
echo "$out" | jq -e '.approval_summary | type == "string"' > /dev/null
```

## Human-Friendly Approval Date

The drug card should render the human-friendly display date in the base header instead of only the raw ISO string.

```bash
out="$(biomcp get drug pembrolizumab)"
echo "$out" | mustmatch '/FDA Approved.*[A-Z][a-z]+ [0-9]{1,2}, [0-9]{4}/'
```

## Drug Targets

Target-only expansion is useful when the workflow is gene-centric. This check ensures the section heading and expected target token are present.

```bash
out="$(biomcp get drug pembrolizumab targets)"
echo "$out" | mustmatch like "## Targets"
echo "$out" | mustmatch like "PDCD1"
```

## Drug Interactions With Public Label Text

The public MyChem payload does not reliably expose structured DrugBank interaction rows, so BioMCP should render OpenFDA label text when it exists instead of claiming no interactions are known.

```bash
out="$(biomcp get drug Warfarin interactions)"
echo "$out" | mustmatch like "## Interactions"
echo "$out" | mustmatch like "DRUG INTERACTIONS"
echo "$out" | mustmatch not like "No known drug-drug interactions found."
```

## Drug Interactions Truthful Fallback

When public label text is also unavailable, the interactions section must say so explicitly rather than implying the drug has no interactions.

```bash
out="$(biomcp get drug pembrolizumab interactions)"
echo "$out" | mustmatch like "## Interactions"
echo "$out" | mustmatch like "Interaction details not available from public sources."
echo "$out" | mustmatch not like "No known drug-drug interactions found."
```

## Drug to Trials

Intervention-based helper search should return the shared trial table layout. We also assert query echo to confirm the pivot preserved the drug token.

```bash
out="$(biomcp drug trials pembrolizumab --limit 3)"
echo "$out" | mustmatch like "|NCT ID|Title|Status|Phase|Conditions|"
echo "$out" | mustmatch like "intervention=pembrolizumab"
```

## Drug to Adverse Events

This helper links a therapy directly to adverse-event reporting data. Assertions target the adverse-event heading and report table columns.

```bash
out="$(biomcp drug adverse-events pembrolizumab --limit 3)"
echo "$out" | mustmatch like "# Adverse Events: drug=pembrolizumab"
echo "$out" | mustmatch like "|Report ID|Drug|Reactions|Serious|"
```

## Adverse Event Search

Direct adverse-event search is useful for safety reconnaissance independent of drug metadata. We verify the heading and stable summary marker.

```bash
out="$(biomcp search adverse-event -d ibuprofen --limit 3)"
echo "$out" | mustmatch like "# Adverse Events: drug=ibuprofen"
echo "$out" | mustmatch like "Total reports (OpenFDA)"
```

## Brand Name Search Uses Exact Match Ranking

Brand-only MyChem hits should still render search rows with a usable canonical
name. The OpenFDA rescue path should prefer the exact Keytruda label over the
newer KEYTRUDA QLEX combo label and respect the requested limit/total text.

```bash
out="$("$(git rev-parse --show-toplevel)/target/release/biomcp" search drug Keytruda --region us --limit 1)"
echo "$out" | mustmatch like "# Drugs: Keytruda"
echo "$out" | mustmatch like "Found 1 drug"
echo "$out" | mustmatch like "|Name|Mechanism|Target|"
echo "$out" | mustmatch like "pembrolizumab"
echo "$out" | mustmatch not like "pembrolizumab and berahyaluronidase alfa-pmph"
```

## EMA Search Region

The EMA human-medicine fixture should support EU-only search rows with the EMA
product number and authorization status while still honoring existing drug
normalization.

```bash
bash fixtures/setup-ema-spec-fixture.sh "$PWD"
. "$PWD/.cache/spec-ema-env"
out="$(biomcp search drug Keytruda --region eu --limit 5)"
echo "$out" | mustmatch like "# Drugs: Keytruda"
echo "$out" | mustmatch like "|Name|Active Substance|EMA Number|Status|"
echo "$out" | mustmatch like "Keytruda"
echo "$out" | mustmatch like "pembrolizumab"
echo "$out" | mustmatch like "EMEA/H/C/003820"
echo "$out" | mustmatch like "Authorised"
```

## Default Drug Search Covers US and EU

Omitting `--region` on a plain name query should render the same split U.S./EU
layout as the explicit all-regions mode.

```bash
bash fixtures/setup-ema-spec-fixture.sh "$PWD"
. "$PWD/.cache/spec-ema-env"
out="$(biomcp search drug Keytruda --limit 5)"
echo "$out" | mustmatch like "# Drugs: Keytruda"
echo "$out" | mustmatch like "## US (MyChem.info / OpenFDA)"
echo "$out" | mustmatch like "## EU (EMA)"
echo "$out" | mustmatch like "EMEA/H/C/003820"
```

## EMA Search All Regions

`--region all` should render separate labeled U.S. and EU result blocks instead
of flattening them into one unlabeled table.

```bash
bash fixtures/setup-ema-spec-fixture.sh "$PWD"
. "$PWD/.cache/spec-ema-env"
out="$(biomcp search drug Keytruda --region all --limit 5)"
echo "$out" | mustmatch like "# Drugs: Keytruda"
echo "$out" | mustmatch like "## US (MyChem.info / OpenFDA)"
echo "$out" | mustmatch like "## EU (EMA)"
echo "$out" | mustmatch like "EMEA/H/C/003820"
```

## EMA Regulatory Section

The EU regulatory section should anchor on the EMA medicine row and show recent
post-authorisation activity.

```bash
bash fixtures/setup-ema-spec-fixture.sh "$PWD"
. "$PWD/.cache/spec-ema-env"
out="$(biomcp get drug Keytruda regulatory --region eu)"
echo "$out" | mustmatch like "## Regulatory (EU"
echo "$out" | mustmatch like "EMEA/H/C/003820"
echo "$out" | mustmatch like "Authorised"
echo "$out" | mustmatch like "27/02/2026"
```

## EMA Safety Truthful Empty Sections

The EU safety surface should render DHPC matches and keep referrals/PSUSAs
truthful when the EMA batch has no matching rows.

```bash
bash fixtures/setup-ema-spec-fixture.sh "$PWD"
. "$PWD/.cache/spec-ema-env"
out="$(biomcp get drug Ozempic safety --region eu)"
echo "$out" | mustmatch like "## Safety (EU"
echo "$out" | mustmatch like "### DHPCs"
echo "$out" | mustmatch like "Medicine shortage"
echo "$out" | mustmatch like "### Referrals"
echo "$out" | mustmatch like "No data found (EMA)"
echo "$out" | mustmatch like "### PSUSAs"
echo "$out" | mustmatch like "No data found (EMA)"
```

## EMA Shortage Section

EU shortage output should expose the EMA shortage status, alternatives flag,
and update date from the local batch.

```bash
bash fixtures/setup-ema-spec-fixture.sh "$PWD"
. "$PWD/.cache/spec-ema-env"
out="$(biomcp get drug Ozempic shortage --region eu)"
echo "$out" | mustmatch like "## Shortage (EU"
echo "$out" | mustmatch like "Resolved"
echo "$out" | mustmatch like "Yes"
echo "$out" | mustmatch like "13/01/2026"
```
