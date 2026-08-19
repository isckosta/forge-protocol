---
forge:
  artifact: plan
  schema: 1
change: CHG-0015
status: approved
---
# Plan — CHG-0015

1. Schemas: new `protocol/schemas/execution-provenance-v2.schema.json`
   (`forge/execution-provenance@2` — `role` enum gains `delegated_task`;
   new `execution.delegated_by`; new `baseline` object; `scope`'s
   `minItems` relaxed to `0`). Register in `catalog.yml`. `@1` untouched.
2. Protocol docs: `protocol/contract/engineering.md` (append C-060–C-066);
   `protocol/versions/2/contract/engineering.md` (append the identical
   C-060–C-066, per the CHG-0011/CHG-0013 dual-file precedent
   `architecture.md` already cites); `protocol/specification.md` (new §40,
   "Delegated Execution Authority"); `protocol/compatibility.md` (new
   subsection, same "additive, prospective-only" argument as the CHG-0011/
   CHG-0013 subsections).
3. Repository docs: one added sentence to `ARCHITECTURE.md` §27 (per
   `architecture.md`); no other section touched.
4. Core validator: two new functions in
   `src/forge_cli/validation/__init__.py` —
   `_delegated_execution_effect(root, baseline, close_revision)` and
   `_validate_delegated_authority(root, mpath, manifest)` — wired into
   `validate_project` for every Protocol id (not gated to `protocol == 2`,
   matching how `_validate_unresolved_decisions` is wired, per
   `architecture.md`).
5. Tests: TDD-001 through TDD-016 per `test-strategy.md`, both levels
   (shape/logic `tmp_path` fixtures; fixture-repo tests with real
   `git init`/`git commit`/working-tree mutations), plus the
   compatibility regression baseline against every real `provenance.yml`
   under `.forge/changes/CHG-0001`–`CHG-0015` (TDD-001).
6. Verification: `pytest -q`, `forge validate`, `forge doctor`. Baseline
   recorded now, before Implementation, matching `CHG-0013`'s own Plan
   practice: `forge validate` currently reports **"Forge project is
   valid"** (confirmed at the end of the Test Strategy commit, `f41f45e`)
   — any regression introduced during Implementation must be visible
   against this exact baseline, not a vaguer "it passed before."
7. Documentation/Knowledge Capture (deferred content, not authored now):
   `docs/adr/0013-delegated-execution-authority-boundaries.md` (per
   `architecture.md`'s ADR determination); `knowledge-capture.md`. RFC
   requirement evaluated at Documentation time against
   `.forge/contract/engineering.md` F-008 ("Material Protocol Changes
   require RFC") — this Change proposes new Contract invariants and a new
   schema, which plausibly qualifies; the actual determination is
   Documentation-stage work this Plan does not preempt, exactly as
   `CHG-0013`'s own Plan deferred the identical question for itself.
   `traceability.yml` and `tdd-evidence.yml` are **not** produced by this
   Plan either, for a stronger reason than scheduling convenience: both
   artifacts assert real test names and real TDD-cycle evidence: producing
   them before any test exists would be exactly the "reconstructed
   evidence" C-016/C-021 forbid. They are produced during Implementation,
   from what actually happens, not planned in advance.
8. Freeze Implementation subject; record `role: implementation`
   provenance (`assurance: recorded`) once Implementation actually
   completes — this Change's first Review Iteration will be
   `kind: initial_review`, not `resolution_verification`.
9. Independent Strict Review: separate Execution and Execution Context
   from Implementation (Protocol 2 §2/C-026) — executed by a fresh agent
   instance, not this session, which cannot satisfy that independence
   requirement for itself by construction (the same reasoning `CHG-0014`'s
   and `CHG-0013`'s own Intents already recorded for themselves).

## Explicit boundary

This Plan and the following Tasks are the last planning artifacts produced
in this session. Reaching `tasks_ready` (`full.yml`'s `before_
implementation` Gate) is not authorization to begin Implementation — it is
authorization to *stop having planned* and ask. Steps 4–9 above, as actual
code, Contract text, schema files, and provenance records (not the design
already recorded in `architecture.md`/`test-strategy.md`), require an
explicit, separate human go-ahead in a later message, distinct from the
go-ahead that reached Plan/Tasks. `tasks.md` below therefore has every task
unchecked; none has been started.
