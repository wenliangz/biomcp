# Study-Native Queries

This spec validates the study-native local cBioPortal command family. Assertions target stable command surfaces, table headings, and query labels rather than volatile upstream counts.

| Section | Command focus | Why it matters |
|---|---|---|
| Environment setup | `BIOMCP_STUDY_DIR` | Makes local dataset dependency explicit |
| Study listing | `study list` | Confirms study discovery and list table schema |
| Mutation frequency | `study query --type mutations` | Confirms mutation query headings and metrics |
| CNA distribution | `study query --type cna` | Confirms CNA bucket rows |
| Expression distribution | `study query --type expression` | Confirms expression summary metrics |
| Co-occurrence | `study co-occurrence` | Confirms pairwise table schema |
| Missing data handling | expression on `msk_impact_2017` | Confirms actionable source-unavailable message |
| Unknown study handling | invalid `--study` | Confirms actionable not-found message |

## Environment Setup

These commands require local study files. Set `BIOMCP_STUDY_DIR` to your dataset root before running this spec.

```bash
test -n "${BIOMCP_STUDY_DIR:-}"
test -d "$BIOMCP_STUDY_DIR"
echo "$BIOMCP_STUDY_DIR" | mustmatch like "datasets"
```

## Study Listing

Listing should return a stable heading and table columns with at least one known starter study ID.

```bash
out="$(biomcp study list)"
echo "$out" | mustmatch like "# Study Datasets"
echo "$out" | mustmatch like "| Study ID | Name | Cancer Type | Samples | Available Data |"
echo "$out" | mustmatch like "msk_impact_2017"
```

## Mutation Frequency Query

Mutation query should render the expected heading, metric table, and detail sections.

```bash
out="$(biomcp study query --study msk_impact_2017 --gene TP53 --type mutations)"
echo "$out" | mustmatch like "# Study Mutation Frequency: TP53 (msk_impact_2017)"
echo "$out" | mustmatch like "| Metric | Value |"
echo "$out" | mustmatch like "## Top Variant Classes"
echo "$out" | mustmatch like "## Top Protein Changes"
```

## CNA Distribution Query

CNA query should render canonical CNA buckets and total sample line.

```bash
out="$(biomcp study query --study brca_tcga_pan_can_atlas_2018 --gene ERBB2 --type cna)"
echo "$out" | mustmatch like "# Study CNA Distribution: ERBB2 (brca_tcga_pan_can_atlas_2018)"
echo "$out" | mustmatch like "| Bucket | Count |"
echo "$out" | mustmatch like "| Deep deletion (-2) |"
echo "$out" | mustmatch like "| Total samples |"
```

## Expression Distribution Query

Expression query should show summary statistics fields and source file label.

```bash
out="$(biomcp study query --study paad_qcmg_uq_2016 --gene KRAS --type expression)"
echo "$out" | mustmatch like "# Study Expression Distribution: KRAS (paad_qcmg_uq_2016)"
echo "$out" | mustmatch like "| File |"
echo "$out" | mustmatch like "| Sample count |"
echo "$out" | mustmatch like "| Mean |"
```

## Co-occurrence Query

Co-occurrence query should return the expected pairwise table headings.

```bash
out="$(biomcp study co-occurrence --study msk_impact_2017 --genes TP53,KRAS)"
echo "$out" | mustmatch like "# Study Co-occurrence: msk_impact_2017"
echo "$out" | mustmatch like "Genes: TP53, KRAS"
echo "$out" | mustmatch like "Sample universe: clinical sample file"
echo "$out" | mustmatch like "| Gene A | Gene B | Both | A only | B only | Neither | Log Odds Ratio | p-value |"
```

## Missing Data Handling

Requesting expression for a study without expression matrices should fail with a clear source-unavailable message.

```bash
out="$(biomcp study query --study msk_impact_2017 --gene TP53 --type expression 2>&1 || true)"
echo "$out" | mustmatch like "Source unavailable: cbioportal-study"
echo "$out" | mustmatch like "No supported expression matrix found"
```

## Unknown Study Handling

Unknown study IDs should produce a not-found message with a direct next step.

```bash
out="$(biomcp study query --study missing_study --gene TP53 --type mutations 2>&1 || true)"
echo "$out" | mustmatch like "study 'missing_study' not found"
echo "$out" | mustmatch like "biomcp study list"
```
