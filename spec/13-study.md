# Study-Native Queries

This spec validates the local cBioPortal study command family. Assertions stay anchored on stable headings, column names, and group labels rather than volatile dataset counts.

| Section | Command focus | Why it matters |
|---|---|---|
| Environment setup | `BIOMCP_STUDY_DIR` | Makes the local dataset dependency explicit |
| Study listing | `study list` | Confirms study discovery and list table schema |
| Mutation frequency | `study query --type mutations` | Confirms mutation query headings and metrics |
| CNA distribution | `study query --type cna` | Confirms CNA bucket rows |
| Expression distribution | `study query --type expression` | Confirms expression summary metrics |
| Cohort split | `study cohort` | Confirms mutation-based cohort partitioning |
| Survival aggregates | `study survival` | Confirms per-group event/follow-up summary output |
| Expression comparison | `study compare --type expression` | Confirms per-group expression summary tables |
| Mutation rate comparison | `study compare --type mutations` | Confirms per-group mutation-rate summary tables |
| Co-occurrence | `study co-occurrence` | Confirms pairwise table schema |
| Missing data handling | missing expression or survival inputs | Confirms actionable source-unavailable messages |
| Unknown study handling | invalid `--study` | Confirms actionable not-found message |

## Environment Setup

These commands require local study files. This spec provisions a minimal local fixture dataset, then exports `BIOMCP_STUDY_DIR` from a cached env file that later sections can source.

```bash
bash fixtures/setup-study-spec-fixture.sh "$PWD"
. "$PWD/.cache/spec-study-env"
test -n "${BIOMCP_STUDY_DIR:-}"
test -d "$BIOMCP_STUDY_DIR"
echo "$BIOMCP_STUDY_DIR" | mustmatch like "datasets"
```

## Study Listing

Listing should return a stable heading and table columns with at least one known starter study ID.

```bash
. "$PWD/.cache/spec-study-env"
out="$(biomcp study list)"
echo "$out" | mustmatch like "# Study Datasets"
echo "$out" | mustmatch like "| Study ID | Name | Cancer Type | Samples | Available Data |"
echo "$out" | mustmatch like "msk_impact_2017"
```

## Mutation Frequency Query

Mutation query should render the expected heading, metric table, and detail sections.

```bash
. "$PWD/.cache/spec-study-env"
out="$(biomcp study query --study msk_impact_2017 --gene TP53 --type mutations)"
echo "$out" | mustmatch like "# Study Mutation Frequency: TP53 (msk_impact_2017)"
echo "$out" | mustmatch like "| Metric | Value |"
echo "$out" | mustmatch like "## Top Variant Classes"
echo "$out" | mustmatch like "## Top Protein Changes"
```

## CNA Distribution Query

CNA query should render canonical CNA buckets and total sample line.

```bash
. "$PWD/.cache/spec-study-env"
out="$(biomcp study query --study brca_tcga_pan_can_atlas_2018 --gene ERBB2 --type cna)"
echo "$out" | mustmatch like "# Study CNA Distribution: ERBB2 (brca_tcga_pan_can_atlas_2018)"
echo "$out" | mustmatch like "| Bucket | Count |"
echo "$out" | mustmatch like "| Deep deletion (-2) |"
echo "$out" | mustmatch like "| Total samples |"
```

## Expression Distribution Query

Expression query should show summary statistics fields and source file label.

```bash
. "$PWD/.cache/spec-study-env"
out="$(biomcp study query --study paad_qcmg_uq_2016 --gene KRAS --type expression)"
echo "$out" | mustmatch like "# Study Expression Distribution: KRAS (paad_qcmg_uq_2016)"
echo "$out" | mustmatch like "| File |"
echo "$out" | mustmatch like "| Sample count |"
echo "$out" | mustmatch like "| Mean |"
```

## Cohort Split

The cohort command should partition the study into mutation-defined groups. The output should keep both group labels and the total row stable even when counts drift upstream.

```bash
. "$PWD/.cache/spec-study-env"
out="$(biomcp study cohort --study brca_tcga_pan_can_atlas_2018 --gene TP53)"
echo "$out" | mustmatch like "# Study Cohort: TP53"
echo "$out" | mustmatch like "| Group | Samples | Patients |"
echo "$out" | mustmatch like "TP53-mutant"
echo "$out" | mustmatch like "TP53-wildtype"
echo "$out" | mustmatch like "| Total |"
```

## Survival Aggregates

The survival command should return aggregate-only group summaries rather than record-level data. The stable contract is the endpoint label plus the event/censor/follow-up columns.

```bash
. "$PWD/.cache/spec-study-env"
out="$(biomcp study survival --study brca_tcga_pan_can_atlas_2018 --gene TP53)"
echo "$out" | mustmatch like "# Study Survival: TP53"
echo "$out" | mustmatch like "Endpoint: Overall Survival"
echo "$out" | mustmatch like "| Group | N | Events | Censored | Event Rate | Median Months |"
echo "$out" | mustmatch like "TP53-mutant"
echo "$out" | mustmatch like "TP53-wildtype"
```

## Expression Comparison

Expression comparison should summarize the target gene distribution across mutation-defined groups. The spec asserts the structural columns, not numeric values.

```bash
. "$PWD/.cache/spec-study-env"
out="$(biomcp study compare --study brca_tcga_pan_can_atlas_2018 --gene TP53 --type expression --target ERBB2)"
echo "$out" | mustmatch like "# Study Group Comparison: Expression"
echo "$out" | mustmatch like "| Group | N | Mean | Median |"
echo "$out" | mustmatch like "TP53-mutant"
echo "$out" | mustmatch like "TP53-wildtype"
```

## Mutation Rate Comparison

Mutation-rate comparison should summarize the target gene mutation rate in each cohort. This keeps the group names and table schema stable while actual study counts vary.

```bash
. "$PWD/.cache/spec-study-env"
out="$(biomcp study compare --study brca_tcga_pan_can_atlas_2018 --gene TP53 --type mutations --target PIK3CA)"
echo "$out" | mustmatch like "# Study Group Comparison: Mutation Rate"
echo "$out" | mustmatch like "| Group | N | Mutated | Mutation Rate |"
echo "$out" | mustmatch like "TP53-mutant"
echo "$out" | mustmatch like "TP53-wildtype"
```

## Co-occurrence Query

Co-occurrence query should return the expected pairwise table headings.

```bash
. "$PWD/.cache/spec-study-env"
out="$(biomcp study co-occurrence --study msk_impact_2017 --genes TP53,KRAS)"
echo "$out" | mustmatch like "# Study Co-occurrence: msk_impact_2017"
echo "$out" | mustmatch like "Genes: TP53, KRAS"
echo "$out" | mustmatch like "Sample universe: clinical sample file"
echo "$out" | mustmatch like "| Gene A | Gene B | Both | A only | B only | Neither | Log Odds Ratio | p-value |"
```

## Missing Expression Data

Requesting expression for a study without expression matrices should fail with a clear source-unavailable message.

```bash
. "$PWD/.cache/spec-study-env"
out="$(biomcp study query --study msk_impact_2017 --gene TP53 --type expression 2>&1 || true)"
echo "$out" | mustmatch like "Source unavailable: cbioportal-study"
echo "$out" | mustmatch like "No supported expression matrix found"
```

## Missing Survival Data

Studies without canonical survival inputs should fail clearly instead of inferring unsupported behavior. The error should point at the required patient clinical file and missing columns.

```bash
. "$PWD/.cache/spec-study-env"
out="$(biomcp study survival --study paad_qcmg_uq_2016 --gene KRAS 2>&1 || true)"
echo "$out" | mustmatch like "Source unavailable: cbioportal-study"
echo "$out" | mustmatch like "Missing required column"
echo "$out" | mustmatch like "data_clinical_patient.txt"
```

## Unknown Study Handling

Unknown study IDs should produce a not-found message with a direct next step.

```bash
. "$PWD/.cache/spec-study-env"
out="$(biomcp study query --study missing_study --gene TP53 --type mutations 2>&1 || true)"
echo "$out" | mustmatch like "study 'missing_study' not found"
echo "$out" | mustmatch like "biomcp study list"
```
