---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0021
status: complete
---

# Knowledge Capture — Adapter Reference Schema Projection

## What Changed

Both Harness Adapters now project a `decision-rules.md` reference,
rendered directly from `forge_cli.validation`'s own enum/mapping
constants rather than hand-duplicated as prose, closing the gap that
caused two real `forge validate` rejections during CHG-0001's external
validation. The `resolved_via` invalid-value error message now states
the expected values.

## Durable Knowledge

**Undocumented validation rules split into two structurally different
gaps, and both needed the same fix.** `resolved_via`'s enum was already
in `change-v2.schema.json` — the gap was that the schema file itself was
never projected or referenced by either Adapter. `class` -> valid
`owning_artifact` and `class` -> authority floor existed **only** as
Python constants, with no JSON Schema representation at all — a deeper
gap. Both were closed the same way: generate a Markdown reference from
the single real source of truth (the Python constants `forge validate`
actually reads) and project it, rather than treating the two gaps as
needing different fixes. Future work discovering an "undocumented
validation rule" should check both places (JSON Schema, Python-only
logic) before assuming which kind of gap it is.

**Generate documentation from enforcement code; do not hand-duplicate
it.** A hand-written Markdown table mirroring `_DEC_OWNING_BY_CLASS`
would have reintroduced exactly the class of defect this Change exists
to prevent — the moment the table and the code disagree, one of them is
silently wrong. `render_decision_rules_reference()` reads the constants
directly; its own tests assert against the imported constants, not a
second hand-typed expectation. This generalizes: any future reference
document describing validation behavior should prefer rendering from the
real enforcement code over a parallel prose description, wherever the
enforcement code already exists as accessible, structured data.

**`forge_cli.validation` already imports from `forge_cli.protocol_resolution`
— a real, durable constraint on where new `resolve_effective_*`-style
functions can live.** A function needing both "the
`resolve_effective_*` naming convention's natural home" and "validation's
constants" cannot have both; `protocol_resolution` importing from
`validation` would cycle. This Change resolved it by placing the
renderer in `validation` and having `adapters/service.py` import from
both siblings directly. Any future Change adding a new projected
reference derived from `validation`-owned data should expect the same
constraint, not rediscover it from a failed import.

**A "final" regression baseline needs to run after evidence-assembly
artifacts are written, not only after code/test-writing tasks.** This
Change's own Strict Review Iteration 1 (R001, BLOCKER) caught a real
regression: the TDD-007 baseline was genuinely green when checked after
T-010 (per `plan.md`'s own step 11), but `T-012` — writing
`traceability.yml` — then introduced a schema violation
(`tasks: []` against `traceability.schema.json`'s `minItems: 1`) that
was never re-verified before the Implementation commit was frozen.
`verification.md`/`tdd-evidence.yml` both asserted "535 passed, 0
failed" for a commit where that was never true. The general lesson:
Plan's regression-baseline step should be sequenced strictly last, after
every artifact the Implementation itself writes (`traceability.yml`,
`tdd-evidence.yml`, `manifest.yml`), not positioned before the final
evidence-assembly task on the assumption that assembling evidence cannot
itself introduce a regression. It can, and did.

**Independent, cold, hint-free sub-agent review found three real,
distinct issues across three separate passes in this same Change** —
Specification Review (4 MINOR, citation/completeness gaps), Strict
Review (1 real BLOCKER, the regression above), Resolution Verification
(confirmed the fix and found nothing new). None were seeded with a hint
about where to look. This is itself further evidence for the finding
that motivated this Change in the first place: adversarial independent
review, run genuinely cold, catches real defects self-review does not
— including, this time, defects in the Change whose entire purpose was
improving Forge's own review-supporting tooling.

## Consequences for Future Changes

- A future Change adding another `_DEC_*`-style constant category should
  update `render_decision_rules_reference()` explicitly — it names each
  constant it documents rather than introspecting all module-level
  `_DEC_*` names generically (`architecture.md` "Risks").
- `discovery.md`'s deferred "Candidate A" (promoting
  `_DEC_OWNING_BY_CLASS`/`_DEC_AUTHORITY_FLOOR` into
  `change-v2.schema.json` directly) remains open and undecided — a
  legitimate future direction, not rejected on its merits, only deferred
  as materially larger than this Change's scope.
- `specification-review.md`'s SR-005 (the external `crud-produtos`
  validation report that motivated this Change is unarchived anywhere in
  this repository) remains an open observation. A future Change curating
  that report as real, in-repo evidence — the way `CHG-0020` curated
  `CHG-0016`/`CHG-0018` — would let `ROADMAP.md`'s "External validation
  matrix" be flipped for Laravel/PHP on real evidence, and would resolve
  the traceability gap SR-005 identified.

## References

- `specification-review.md`, `review.md` (both Iterations) for the full
  independent-review evidence trail.
- `CHG-0016` (`canonical-artifact-structure`), the direct precedent this
  Change's Adapter-wiring pattern reuses exactly.
