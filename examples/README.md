# BioMCP Examples

This folder contains runnable example surfaces for local experimentation. Most
subfolders are paper-style benchmark harnesses with `prompt.md`, `run.sh`, and
`score.sh`; `streamable-http/` is a standalone transport demo.

## Canonical Workflows

For day-to-day agent use, the canonical workflow interface is the embedded
skills, not this examples folder.

Use:

```bash
biomcp skill list
biomcp skill <number-or-slug>
```

## Mapping

| Example folder | Canonical skill |
|----------------|-----------------|
| `genegpt/` | `09-gene-function-lookup` |
| `geneagent/` | `10-gene-set-analysis` |
| `trialgpt/` | `03-trial-searching` (patient matching section) |
| `pubmed-beyond/` | `11-literature-synthesis` |

## Example Index

| Example folder | What it does |
|----------------|--------------|
| `geneagent/` | Replays a gene-set-analysis workflow with prompt, run, and scoring assets. |
| `genegpt/` | Reproduces a gene-function lookup workflow with captured benchmark harness files. |
| `pubmed-beyond/` | Replays a literature-synthesis workflow over BioMCP with benchmark assets. |
| `trialgpt/` | Reproduces a patient-matching and trial-search workflow with benchmark assets. |

## Standalone Examples

| Example folder | What it does |
|----------------|--------------|
| `streamable-http/` | Runs a Streamable HTTP client against `biomcp serve-http` and proves the remote `biomcp` MCP tool can complete a three-step BRAF workflow. |

## When to Use This Folder

Use the paper-style examples when you want a quick local benchmark harness with
captured outputs or metrics. Use `streamable-http/` when you want a runnable
remote-transport proof. Use embedded skills when you want the production
workflow instructions agents should follow.
