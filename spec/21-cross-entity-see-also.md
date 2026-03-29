# Cross-Entity See Also

This spec locks the approved cross-entity next-step hints that should teach the
typed BioMCP surfaces directly from normal output. Agents learn the right next
call from output context, not from proactively reading help — so every card and
empty-state must surface the structured path directly.

| Section | Command focus | Why it matters |
|---|---|---|
| Drug to PGx | `get drug warfarin` | Teaches the structured PGx surface from a drug card |
| Gene to PGx | `get gene TP53` | Teaches the PGx card from a gene card |
| Gene More ordering | `get gene NANOG` | Keeps `ontology` at equal prominence in follow-up sections |
| Oncology study local match | `get disease "breast cancer" genes` | Prefers executable `study top-mutated` when a local study exists |
| Oncology study fallback | `get disease melanoma genes` | Falls back to `study download --list` when no local study can be chosen |
| Disease zero-result discover | `search disease definitelynotarealdisease` | Teaches `discover` when disease search is empty |
| Drug zero-result discover | `search drug definitelynotarealdrugname --region us` | Teaches `discover` when drug search is empty |

## Drug to PGx

Drug cards should advertise the typed PGx search directly in normal markdown
output so agents can pivot without guessing the command shape.

```bash
out="$(biomcp get drug warfarin)"
echo "$out" | mustmatch like "biomcp search pgx -d warfarin"
echo "$out" | mustmatch like "pharmacogenomics interactions"
```

The JSON contract should expose the same next command in `_meta.next_commands`.

```bash
out="$(biomcp --json get drug warfarin)"
echo "$out" | jq -e '._meta.next_commands | index("biomcp search pgx -d warfarin") != null' > /dev/null
```

## Gene to PGx

Gene cards should point to the PGx card in both markdown and JSON because the
same hint powers agentic follow-up planning across renderers.

```bash
out="$(biomcp get gene TP53)"
echo "$out" | mustmatch like "biomcp get pgx TP53"
echo "$out" | mustmatch like "pharmacogenomics card"
```

```bash
out="$(biomcp --json get gene TP53)"
echo "$out" | jq -e '._meta.next_commands | index("biomcp get pgx TP53") != null' > /dev/null
```

## Gene More Ordering

This ticket should not demote `ontology`; the default gene card still needs the
top follow-up trio to stay `pathways`, `ontology`, and `diseases`.

```bash
out="$(biomcp get gene NANOG)"
echo "$out" | mustmatch like $'More:\n  biomcp get gene NANOG pathways'
echo "$out" | mustmatch like "biomcp get gene NANOG pathways"
echo "$out" | mustmatch like "biomcp get gene NANOG ontology"
echo "$out" | mustmatch like "biomcp get gene NANOG diseases"
```

## Oncology Study Local Match

When oncology context and a matching local study are both present, the disease
card should suggest the executable `study top-mutated` command.

```bash
bash fixtures/setup-study-spec-fixture.sh "$PWD"
. "$PWD/.cache/spec-study-env"
out="$(biomcp get disease "breast cancer" genes)"
echo "$out" | mustmatch like "biomcp study top-mutated --study brca_tcga_pan_can_atlas_2018"
echo "$out" | mustmatch like "mutation frequency ranking"
```

## Oncology Study Fallback

When there is no usable local study match, the disease card should still teach
the next structured step by falling back to the study catalog.

```bash
empty_root="$(mktemp -d)"
out="$(BIOMCP_STUDY_DIR="$empty_root" biomcp get disease melanoma genes)"
echo "$out" | mustmatch like "biomcp study download --list"
echo "$out" | mustmatch like "browse downloadable cancer genomics studies"
rm -rf "$empty_root"
```

## Disease Zero-Result Discover

Empty disease searches should redirect users to `discover` with the original
query preserved in the suggested command.

```bash
out="$(biomcp search disease definitelynotarealdisease --limit 3)"
echo "$out" | mustmatch like "Try: biomcp discover definitelynotarealdisease"
echo "$out" | mustmatch like "resolve abbreviations and synonyms"
```

## Drug Zero-Result Discover

Empty drug searches should do the same, nudging users toward `discover` when a
trial code or alias is more likely than a canonical drug name match.

```bash
out="$(biomcp search drug definitelynotarealdrugname --region us --limit 3)"
echo "$out" | mustmatch like "Try: biomcp discover definitelynotarealdrugname"
echo "$out" | mustmatch like "resolve drug trial codes and aliases"
```
