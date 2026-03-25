# Drug

Use drug commands for medication lookup, target-oriented search, and U.S./EU regulatory context.

## Search drugs

Text query:

```bash
biomcp search drug -q "kinase inhibitor" --limit 5
biomcp search drug Keytruda --limit 5
```

EU or comparison search:

```bash
biomcp search drug Keytruda --region eu --limit 5
biomcp search drug Keytruda --region all --limit 5
```

Target-oriented search:

```bash
biomcp search drug --target BRAF --limit 5
```

Indication-oriented search:

```bash
biomcp search drug --indication melanoma --limit 5
```

`search drug --interactions <drug>` is currently unavailable because the public data sources BioMCP uses do not expose partner-indexed interaction rows.

Omitting `--region` on a plain name/alias search checks both U.S. and EU data.
If you omit `--region` while using structured filters such as `--target` or
`--indication`, BioMCP stays on the U.S. MyChem path. Explicit `--region eu`
or `--region all` with structured filters still errors.

## Get a drug record

```bash
biomcp get drug pembrolizumab
```

Default output provides concise identity and mechanism context. Approval-bearing
JSON now includes additive `approval_date_raw`, `approval_date_display`, and
`approval_summary` fields, while markdown renders the human-friendly display
date in the base card.

## Request drug sections

Supported sections: `label`, `regulatory`, `safety`, `shortage`, `targets`,
`indications`, `interactions`, `civic`, `approvals`, `all`.

FDA label section:

```bash
biomcp get drug vemurafenib label
```

Shortage section:

```bash
biomcp get drug carboplatin shortage
```

Regional regulatory and safety sections:

```bash
biomcp get drug Keytruda regulatory --region eu
biomcp get drug Keytruda regulatory --region all
biomcp get drug Ozempic safety --region eu
biomcp get drug Ozempic shortage --region eu
```

Targets and indications sections:

```bash
biomcp get drug pembrolizumab targets
biomcp get drug pembrolizumab indications
```

Interactions (OpenFDA label text when public interaction details are available; otherwise a truthful fallback):

```bash
biomcp get drug warfarin interactions
```

CIViC evidence and Drugs@FDA approvals:

```bash
biomcp get drug vemurafenib civic
biomcp get drug dabrafenib approvals
```

`approvals` remains a legacy U.S.-only section. Use `regulatory` for the region-aware regulatory view.

## EMA local data setup

EU regional commands read the EMA human-medicines JSON batch from `BIOMCP_EMA_DIR` first, then the platform data directory (`~/.local/share/biomcp/ema` on typical Linux systems).

Download the current batch from:

- <https://www.ema.europa.eu/en/about-us/about-website/download-website-data-json-data-format>

Expected files:

- `medicines.json`
- `post_authorisation.json`
- `referrals.json`
- `psusas.json`
- `dhpcs.json`
- `shortages.json`

## Cross-entity helpers

Trial pivot:

```bash
biomcp drug trials pembrolizumab --limit 5
```

Safety pivot:

```bash
biomcp drug adverse-events pembrolizumab --limit 5
```

## JSON mode

```bash
biomcp --json get drug pembrolizumab
```

## Practical tips

- Start with base `get` before requesting heavy sections.
- Use target filters to narrow crowded drug classes.
- Use `regulatory`, `safety`, or `shortage` with `--region eu|all` when you need EMA context.
- Pair drug lookups with trial filters for protocol matching workflows.

## Related guides

- [Adverse event](adverse-event.md)
- [Trial](trial.md)
- [Data sources](../reference/data-sources.md)
