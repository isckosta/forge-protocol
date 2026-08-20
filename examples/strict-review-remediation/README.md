# Example — Strict Review Remediation

This is not a fabricated scenario. It is a guided tour of a real Strict
Review cycle already recorded in this repository's own history:
**`CHG-0016`** ("Canonical Artifact Structure"), whose independent
Strict Review genuinely returned `REQUEST CHANGES` on its first pass —
not a token non-blocking note, a real blocking verdict — and was then
genuinely remediated to a passing second Iteration.

Full primary source: `.forge/changes/CHG-0016-canonical-artifact-structure/`
(`review.md`, `provenance.yml`, `manifest.yml`, `knowledge-capture.md`).
This README is a map into that record, not a replacement for it.

## The commit sequence

```text
bf69393  docs(chg-0016): T-001..T-005 -- canonical guidance, Contract/Specification/Compatibility/Architecture wiring
70478ae  feat(chg-0016): T-006..T-010 -- RED/GREEN for Adapter projection of Canonical Artifact Structure
e50d3c5  docs(chg-0016): T-011..T-012 -- planning artifacts, canonical examples, ADR, knowledge capture, traceability, TDD evidence, verification
f7829d9  docs(chg-0016): T-013 -- freeze Implementation subject, record provenance
6d6e2c7  review(chg-0016): Iteration 1 -- Independent Strict Review, REQUEST CHANGES
848adc9  fix(chg-0016): resolve Strict Review Iteration 1 findings (R001-R012)
67766d3  docs(chg-0016): record role: resolution provenance (Resolution Scope/targets)
856e6a4  review(chg-0016): Iteration 2 -- Resolution Verification, PASS
85c8ce0  docs(chg-0016): T-016 -- Completion
```

`e50d3c5` froze the Implementation subject. `6d6e2c7` is a genuinely
independent Strict Review Execution — a distinct Execution and Execution
Context from the Implementation session, per Protocol 2 (`protocol/versions/2/specification.md`
§2, Contract C-026) — evaluating that frozen subject cold.

## What Iteration 1 actually found

`review.md`'s own Summary table (quoted verbatim):

| Severity | Count |
| --- | --- |
| BLOCKER | 1 |
| MAJOR | 2 |
| MINOR | 6 |
| OBSERVATION | 3 |

`protocol/policies/review.yml` sets `blocking: [blocker, major]` — the
BLOCKER and both MAJORs were genuinely blocking, not decorative.

### R012 — BLOCKER

`src/forge_cli/validation/__init__.py`'s C-026 check accepted only
`schema: forge/execution-provenance@1` — but `CHG-0015` had already
introduced `forge/execution-provenance@2`, and `CHG-0016`'s own
provenance ledger used it. The moment `CHG-0016`'s own Review Iteration
tried to bind to its `@2` ledger, `forge validate` failed. This is a
Change's own Strict Review catching a real, pre-existing latent defect
by triggering it on itself — not a hypothetical example.

### R001 — MAJOR

`traceability.yml` recorded evidence *asserting* that NFR-002 (Harness
independence — no Codex-specific content in the new canonical guidance)
held. The shipped guidance file actually violated it. A Finding here
isn't just "the code has a bug" — it's "the Change's own evidence
misrepresented reality," a materially more serious class of problem.

### R002 — MAJOR

The new guidance omitted this repository's own most consistent real
Artifact convention (the `forge:` frontmatter block present in every
real Artifact since `CHG-0006`) — reproducing, inside the very guidance
meant to prevent structural drift, the exact kind of omission-by-drift
it existed to fix.

*(Six further MINOR and three OBSERVATION findings exist — see `review.md`
directly for the full record; this README surfaces the three most
consequential, not all twelve.)*

## The remediation

`848adc9` resolved R001 through R012 in one commit, with the Resolution's
own `provenance.yml` record declaring its exact scope and the Findings it
targeted (Protocol 2's Resolution Scope/Resolution Delta mechanism,
`protocol/versions/2/specification.md` §11) — not a vague "fixed some
stuff" commit. `67766d3` recorded that Resolution's provenance.
`856e6a4` is a second, independently-executed Review — a distinct
Execution/Context again, this time verifying the Resolution Delta and
checking for Out-of-Scope Mutation — which returned **PASS**, with two
new non-blocking OBSERVATIONs (`R013`, `R014`) recorded, not silently
dropped.

## What this demonstrates

- A Strict Review verdict can genuinely block Completion — this is not
  theater.
- A Reviewer Execution independent from Implementation is what caught a
  defect the Implementation's own extensive self-testing did not.
- Resolution has a declared scope and targets, checkable against the
  actual diff (`git diff --name-only 6d6e2c7-subject..848adc9`, minus
  this Change's own `manifest.yml`/`provenance.yml`/`review.md`).
- Resolution Verification is a second, independent, narrower Review pass
  — not a rubber stamp, and not a full re-audit of already-reviewed
  content either.

See `.forge/changes/CHG-0016-canonical-artifact-structure/review.md` for
the complete record, including all twelve Iteration 1 Findings and the
full Iteration 2 verification.
