# BioASQ Benchmark Module

This directory is the BioASQ benchmark data-prep and operator-docs surface for
BioMCP. It does not replace the existing Rust benchmark CLI under
`src/cli/benchmark/`; it gives that future runner code a stable place to pull
public benchmark inputs from.

## What lives here

- `ingest_public.py` downloads pinned public BioASQ artifacts and normalizes
  them into one JSONL schema.
- `datasets/manifest.json` is the source of truth for bundle ids, source refs,
  provenance notes, and expected record counts.
- `datasets/raw/` and `datasets/normalized/` are operator-generated outputs.
  They are intentionally gitignored.
- `annotations/` holds the validity overlay contract used for future stale or
  invalid question review without mutating the raw corpus.

## Run the public ingester

```bash
uv run --script benchmarks/bioasq/ingest_public.py --bundle hf-public-pre2026
uv run --script benchmarks/bioasq/ingest_public.py --bundle mirage-yesno-2024
```

Add `--force` when you want to overwrite an existing raw or normalized output
path owned by this module.

The public ingester only handles manifest-defined public bundles. The official
participant download remains metadata-only in `datasets/manifest.json` because
registration and participant-area downloads are a separate lane.

## Output layout

- `datasets/raw/` stores the pinned public source payloads in source shape.
- `datasets/normalized/` stores the canonical JSONL bundles used for regression
  tracking or future runner inputs.
- `annotations/validity.jsonl` is the overlay scaffold for temporal review.

See `datasets/README.md` for provenance details and
`docs/reference/bioasq-benchmark.md` for the public-lane versus official-lane
runbook.
