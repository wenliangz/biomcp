# Skills

BioMCP ships one embedded guide plus supporting reference files for agent
workflows. The current workflow is:

```bash
biomcp skill
biomcp skill install ~/.claude
```

## Read the guide

`biomcp skill` prints the embedded `skills/SKILL.md` overview. Start there if
you want the current BioMCP workflow guidance without installing anything into
an agent directory.

## Install into an agent directory

Install the embedded `skills/` tree into your agent directory:

```bash
biomcp skill install ~/.claude
```

Force replacement of an existing install:

```bash
biomcp skill install ~/.claude --force
```

The `dir` argument can point at an agent root such as `~/.claude`, an existing
`skills/` directory, or a `skills/biomcp/` directory. When you omit `dir`,
BioMCP attempts supported agent-directory detection in your home directory and
the current working tree, then prompts before installing when stdin is a TTY.

## Install payload

Current builds install the full embedded reference tree into
`<agent>/skills/biomcp/`, including:

- `SKILL.md`
- `jq-examples.md`
- `examples/`
- `schemas/`

## Legacy compatibility note

`biomcp skill list` remains as a legacy compatibility alias and currently prints
`No skills found`.

Numeric and slug lookups are also legacy compatibility paths. Commands such as
`biomcp skill 03` and `biomcp skill variant-to-treatment` currently fail with a
clear not-found message and suggest `biomcp skill`.
