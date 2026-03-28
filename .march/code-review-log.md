# Code Review Log

## Review Scope

Reviewed `.march/ticket.md`, `.march/design-draft.md`, `.march/design-final.md`,
`.march/code-log.md`, the staged implementation in `src/cli/mod.rs`,
`src/cli/chart.rs`, `src/entities/discover.rs`, and `src/render/json.rs`, plus
the staged spec changes in `spec/04-trial.md`, `spec/06-article.md`,
`spec/13-study.md`, and `spec/19-discover.md`.

Re-ran the relevant local gates and direct help/JSON surfaces:

- `cargo test help_`
- `cargo test article_date_help_advertises_shared_accepted_formats`
- `cargo test trial_phase_help_explains_canonical_numeric_forms_and_aliases`
- `cargo test chart_help_lists_descriptions_for_all_chart_topics`
- `cargo test to_discover_json_adds_discover_meta_aliases`
- `cargo run --bin biomcp -- search article --help`
- `cargo run --bin biomcp -- search trial --help`
- `cargo run --bin biomcp -- chart --help`
- `cargo run --bin biomcp -- --json discover Keytruda`

## Design Completeness Audit

Every final-design item marked as requiring change has a matching staged code or
spec change:

- Visible article date aliases:
  implemented in `src/cli/mod.rs` by changing `search article` date flags to
  `visible_alias = "since"` and `visible_alias = "until"`.
- Discover JSON de-duplication:
  implemented in `src/entities/discover.rs` with `#[serde(skip)]` on
  `DiscoverResult.next_commands`, while `src/render/json.rs` keeps
  `_meta.next_commands` populated.
- Chart help descriptions:
  implemented in `src/cli/chart.rs` by adding one-line clap doc comments to all
  chart subcommands.
- Trial phase canonical note:
  implemented in `src/cli/mod.rs` by explicitly documenting canonical numeric
  forms and accepted `PHASE*` aliases.

Documentation and contract updates were checked separately:

- `spec/06-article.md` now proves the visible `--since` / `--until` help
  aliases.
- `spec/19-discover.md` now proves `._meta.next_commands` exists and root
  `.next_commands` is absent.
- `spec/13-study.md` now proves representative chart help descriptions.
- `spec/04-trial.md` now proves the canonical numeric phase note and alias note.

I did not find a final-design implementation item with no corresponding code or
spec change.

## Test-Design Traceability

Each proof-matrix entry has a matching test surface and the assertions now check
the intended behavior:

- `search article --help` visible aliases:
  `cli::tests::article_date_help_advertises_shared_accepted_formats` plus the
  executable assertions in `spec/06-article.md`.
- `discover --json` root de-duplication:
  `render::json::tests::to_discover_json_adds_discover_meta_aliases` plus the
  structural `jq` assertions in `spec/19-discover.md`.
- `chart --help` chart purposes:
  `cli::tests::chart_help_lists_descriptions_for_all_chart_topics` plus the
  representative assertions in `spec/13-study.md`.
- `search trial --help` canonical phase note:
  `cli::tests::trial_phase_help_explains_canonical_numeric_forms_and_aliases`
  plus the executable assertions in `spec/04-trial.md`.

The unit tests and direct `cargo run` help output agree with the staged
implementation. I did not find a missing proof-matrix test or a weak assertion
in the staged Rust/spec changes.

## Issues Found During Critique

1. The existing `.march/code-review-log.md` in the worktree was stale and
   documented an unrelated earlier ticket, so this step did not yet have the
   required review artifact for ticket 068.

No implementation defect was found in the staged Rust or spec changes after
re-running the ticket's relevant help and JSON surfaces.

## Fix Plan

- Replace the stale `.march/code-review-log.md` with a current review log for
  ticket 068.
- Re-run the repo gate after writing the artifact.

## Repair

Applied the following fix:

- Replaced `.march/code-review-log.md` with this ticket-specific review log.

No Rust or spec changes were required beyond the already-staged implementation,
because the re-run outputs matched the final design and proof matrix.

## Post-Fix Collateral Scan

Checked the touched review artifact and surrounding step state after replacing
the file:

- No dead code or unused imports were introduced.
- No cleanup logic or resource handling changed.
- No stale error messages or variable shadowing were introduced.

## Verification

- `cargo test help_` passed.
- `cargo test article_date_help_advertises_shared_accepted_formats` passed.
- `cargo test trial_phase_help_explains_canonical_numeric_forms_and_aliases`
  passed.
- `cargo test chart_help_lists_descriptions_for_all_chart_topics` passed.
- `cargo test to_discover_json_adds_discover_meta_aliases` passed.
- `cargo run --bin biomcp -- search article --help` showed
  `[aliases: --since]` and `[aliases: --until]`.
- `cargo run --bin biomcp -- search trial --help` showed the canonical numeric
  phase note and accepted alias note.
- `cargo run --bin biomcp -- chart --help` showed one-line descriptions for all
  chart subcommands.
- `cargo run --bin biomcp -- --json discover Keytruda` emitted
  `_meta.next_commands` and no root `next_commands`.

`make check` still needed at the time this log was written and was run
afterward as the final gate for the step.

## Residual Concerns

No residual implementation concerns were found. Verify should only confirm that
`make check` stays green in this worktree.

## Out-of-Scope Observations

No out-of-scope follow-up issue was needed from this review.

## Defect Register

| # | Category | Lintable | Description |
|---|----------|----------|-------------|
| 1 | stale-doc | no | The existing `.march/code-review-log.md` was stale from an unrelated earlier ticket and could not serve as the required review artifact for ticket 068 |
