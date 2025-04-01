# Trials CLI Documentation

The Trials CLI module provides commands for searching and retrieving clinical trial information from ClinicalTrials.gov.

> **API Documentation**: For details about the underlying API, see the [ClinicalTrials.gov API Documentation](../apis/clinicaltrials_gov.md).

## Search Command

Search for clinical trials based on various filters and criteria.

### Usage

```bash
biomcp trial search [OPTIONS]
```

### Options

#### Basic Search Filters

- `-c, --condition [CONDITION]`: Medical condition to search for (can specify multiple times)
- `-i, --intervention [INTERVENTION]`: Treatment or intervention to search for (can specify multiple times)
- `-t, --term [TERM]`: General search terms (can specify multiple times)
- `-n, --nct-id [NCT_ID]`: Clinical trial NCT ID to lookup (can specify multiple times)

#### Study Characteristics

- `-s, --status [STATUS]`: Recruiting status (Recruiting, Completed, Active, Enrolling, Terminated, Withdrawn, Unknown)
- `--type [TYPE]`: Study type (Interventional, Observational, Expanded_Access)
- `-p, --phase [PHASE]`: Trial phase (Early_Phase_1, Phase_1, Phase_2, Phase_3, Phase_4, Not_Applicable)
- `--purpose`: Primary purpose (Treatment, Prevention, Diagnostic, Supportive_Care, Screening, Health_Services_Research, Basic_Science, Other)
- `-a, --age-group [AGE_GROUP]`: Age group filter (Child, Adult, Older_Adult)

#### Advanced Filters

- `--min-date [MIN_DATE]`: Minimum date for filtering (YYYY-MM-DD format)
- `--max-date [MAX_DATE]`: Maximum date for filtering (YYYY-MM-DD format)
- `--date-field [DATE_FIELD]`: Date field to filter on (Start_Date, Completion_Date, Primary_Completion_Date, Results_First_Posted, Last_Update_Posted)
- `--intervention-type [TYPE]`: Intervention type filter (Drug, Device, Biological, Procedure, Radiation, Behavioral, Dietary_Supplement, Genetic, Combination_Product, Diagnostic_Test, Other)
- `--sponsor-type [TYPE]`: Sponsor type filter (Industry, NIH, U.S.\_Fed, Other_Gov, Network, Individual, Other)
- `--study-design [DESIGN]`: Study design filter (Single_Group, Parallel, Crossover, Factorial, Sequential, Other)

#### Location-based Search

- `--lat [LATITUDE]`: Latitude for location-based search
- `--lon [LONGITUDE]`: Longitude for location-based search
- `-d, --distance [DISTANCE]`: Distance in miles for location-based search

#### Results Management

- `--sort [SORT]`: Sort order for results (Relevance, Acronym, Brief_Title, Start_Date, Primary_Completion_Date, Last_Update_Posted)
- `--next-page [HASH]`: Next page hash for pagination
- `--help`: Show help message and exit

### Examples

Search for clinical trials about melanoma:

```bash
biomcp trial search --condition "Melanoma"
```

Search for clinical trials involving a specific drug:

```bash
biomcp trial search --intervention "Vemurafenib"
```

Search for recently started Phase 3 trials for cancer:

```bash
biomcp trial search --condition "Cancer" --phase Phase_3 --sort Start_Date
```

Search for recruiting trials in a specific location:

```bash
biomcp trial search --condition "Diabetes" --status Recruiting --lat 40.7128 --lon -74.0060 --distance 50
```

Search for trials with multiple filters:

```bash
biomcp trial search --condition "Breast Cancer" --intervention "Immunotherapy" --phase Phase_2 --status Recruiting
```

## Get Command

Retrieve detailed information about a specific clinical trial by its NCT ID.

### Usage

```bash
biomcp trial get NCT_ID [MODULE]
```

### Arguments

- `NCT_ID`: The NCT identifier for the clinical trial (required)
- `MODULE`: Module to retrieve (optional, defaults to Protocol)
  - Valid modules: Protocol, Locations, References, Outcomes

### Examples

Get basic protocol information for a trial:

```bash
biomcp trial get NCT04267848
```

Get location information for a trial:

```bash
biomcp trial get NCT04267848 Locations
```

Get references and publications for a trial:

```bash
biomcp trial get NCT04267848 References
```

Get outcomes data for a trial:

```bash
biomcp trial get NCT04267848 Outcomes
```
