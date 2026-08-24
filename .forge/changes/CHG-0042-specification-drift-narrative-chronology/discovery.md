---
forge:
  artifact: discovery
  schema: 1
change: CHG-0042
status: complete
---

# Discovery — CHG-0042 Specification Drift Narrative Chronology

## Executive Summary

"Specification Drift" is Protocol §13's minimal, two-sentence normative
rule ("Agents MUST NOT silently modify Requirement meaning to
accommodate an Implementation... the Drift MUST be recorded"), given a
correspondingly minimal, three-section guidance in
`protocol/artifact-structure.md` since `CHG-0016`. Unlike every other
Artifact redesigned this session (Specification, Test Design, Tasks,
Verification, Review), Specification Drift has **no scaffold, no Flow
stage, and no code representation anywhere in `src/`** — it is created
by hand, only when a real drift occurs, which real history shows is
rare (4 occurrences in 42 Changes, all early: `CHG-0008`, `CHG-0011`,
`CHG-0012`, `CHG-0013`). The four real examples diverge structurally
from each other and from any single template, confirming the guidance
gap. This Change elaborates the guidance text only; it introduces no
scaffold, since inventing deterministic generation for an artifact
that is conditional by nature would misrepresent it as another
per-Change stage.

## Investigation

### Protocol authority

`protocol/specification.md` §13, in full: "Agents MUST NOT silently
modify Requirement meaning to accommodate an Implementation. When
implementation evidence invalidates the Specification, the Change MUST
return to the appropriate specification stage and the Drift MUST be
recorded." No filename, no structure, and no schema are mandated by
Protocol — `specification-drift.md` and its shape are entirely real
practice plus non-binding guidance (C-067), same status as every other
Artifact's structure.

### No scaffold, no Flow stage, no schema

- `src/forge_cli/change_scaffolding.py`'s `_STAGE_FILES` has no
  `specification_drift` entry; `_markdown()` has no corresponding
  case. `render_scaffold()` only emits files for stages present in the
  selected Flow's YAML.
- `protocol/flows/{fast,standard,full}.yml` have no `specification_drift`
  stage — confirmed by reading all three stage lists.
- `manifest.yml`'s `artifacts` property is schema-unconstrained
  (`{"type": "object"}` in `change-v2.schema.json`, confirmed during
  `CHG-0040`'s own Discovery) — no `specification_drift` key is
  expected or validated there.
- No validator in `src/forge_cli/validation/__init__.py` references
  `specification_drift`, `specification-drift`, or "drift" at all
  (broad grep across `src/`, `protocol/*.yml`, `protocol/*.json`
  returned nothing).
- No Harness Adapter (`src/forge_cli/adapters/*.py`) references it
  either.

This means: unlike Verification/Review/Tasks (redesigned earlier this
session), there is no renderer to fix, no `_markdown()` template to
rewrite, and therefore no TDD-testable surface. This Change is
correctly non-behavioral.

### Real examples (only four exist)

- **`CHG-0008/specification-drift.md`** — no `forge:` front matter at
  all (the sole real gap in this repository's otherwise-consistent
  front-matter convention, beyond the `CHG-0003`/`CHG-0005` exceptions
  `artifact-structure.md` already names). Two flat sections
  ("Strict Review Iteration N drift" / "Normative correction before
  Resolution N implementation"), no `Root Cause`/`Evidence`/`Final
  decision` headings at all — predates that convention.
- **`CHG-0011/specification-drift.md`** — has front matter; heading `#
  Specification Drift — CHG-0011` (old style, not the `# CHG-XXXX ·
  <Type>` convention `CHG-0037` onward established); prose intro plus a
  flat bullet list, one per finding, using the old change-scoped
  `CHG-0011-Rxxx` finding-id convention (pre-`CHG-0016`, per this
  session's own `CHG-0041` Discovery).
- **`CHG-0012/specification-drift.md`** — the example
  `artifact-structure.md` already cites as the good precedent for
  "Final decision last." Heading-per-attempt narrative (`## Attempt 1`
  … `## Attempt 4`), each explaining what was tried, what Review found,
  and why it failed, ending in `## Final decision — <title>` (note:
  lowercase "decision" — real, current casing, not "Final Decision").
  This Change's drift is really a **Non-Convergence / engineering
  Decision record**, not a "Specification wording was ambiguous" case
  — a materially different flavor of drift than the prompt's own
  running example (FR-006 fallback semantics), and real evidence that
  the artifact's responsibility is broader than one narrow shape.
- **`CHG-0013/specification-drift.md`** — "No Drift to record at this
  stage," with an explicit, important clarification: the corrections
  made to `CHG-0013`'s own `specification.md` during *Adversarial
  Specification Review* (before Architecture, against no Implementation
  evidence) are **Specification Review** iteration, not Drift.
  Materiality boundary, confirmed by real precedent: Drift requires
  Implementation evidence invalidating the Specification; a
  pre-Implementation Specification correction is ordinary
  `specification-review.md` iteration, covered by that artifact's own
  Verdict/Findings/Conclusion structure, not this one.

### Distinction from adjacent concepts (already partly documented, confirmed real)

- **Specification Review** (`specification-review.md`, `SR-xxx`) —
  pre-Implementation correction of Specification defects found by
  adversarial review of the Specification itself. Confirmed distinct
  from Drift by `CHG-0013`'s own explicit statement.
  `protocol/artifact-structure.md`'s "Specification Review" entry
  (§4, already elaborated) is unaffected by this Change.
- **Resolution** — a `role: resolution` provenance record (per
  `execution-provenance-v2.schema.json`'s role enum:
  `implementation, resolution, review, delegated_task`, confirmed
  during `CHG-0041`'s own Discovery) produced in response to a Review
  Finding. Resolution is *work*; Specification Drift is the *record*
  of a normative correction that Resolution's work may have required.
  Not every Resolution involves Drift (most findings are pure
  implementation/test fixes); not every Drift comes from a single
  Resolution (`CHG-0012` shows four).
- **Decision** (`manifest.yml: decisions[]`, `DEC-xxx`) — the escalation
  mechanism for a genuine normative trade-off with more than one valid
  answer (C-051 through C-059, confirmed during `CHG-0041`'s own
  Discovery this session). `CHG-0012`'s specification-drift.md itself
  demonstrates the real relationship: the drift was discovered across
  three Resolution attempts, Review Convergence's Non-Convergence
  mechanism (`CHG-0011`) triggered, and the engineer's resulting
  Decision (documented, not a Decision-record entity by that Change's
  era, but conceptually identical to what `manifest.yml: decisions[]`
  formalizes today) is what `## Final decision` records. Specification
  Drift documents that a decision became necessary and what it
  produced; it does not itself supply Authority the way a `DEC-xxx`
  Decision record does when a real trade-off exists (C-054:
  "Recommendation is not Decision").
- **Review Finding (`Rxxx`)** — the trigger, not the drift itself. A
  finding may reveal implementation-only defects (most common), or may
  reveal that the Specification itself was insufficient (drift). Only
  the latter warrants a `specification-drift.md` entry.

### Frozen subject interaction (already governed elsewhere, not by this artifact)

Confirmed via `CHG-0041`'s own Discovery this session:
`protocol/policies/review.yml`'s `reviewer_resolver_separation`
(`review_subject_freeze_required`,
`post_freeze_subject_mutation_invalidates_binding`) and
`re_review.required_after_blocking_resolution` already govern what
happens mechanically after a Resolution changes reviewable content —
including a Resolution that also corrects `specification.md` because
of a documented Drift. Specification Drift does not need, and this
Change does not introduce, a parallel freeze mechanism — the existing
one already applies uniformly to any post-freeze reviewable mutation,
Drift-driven or not.

### Compatibility Impact convention already real

`CHG-0008`'s own specification-drift.md already demonstrates careful,
material compatibility scoping in practice: "This correction completes
the original Protocol 2 promise... it does not strengthen Protocol 1
and does not claim cryptographic proof." This is real precedent for
the guidance's "assess materially, do not default to breaking change"
principle — already practiced, worth stating explicitly in the
elaborated guidance rather than left implicit.

### Harness Adapters

Confirmed via broad grep (`src/forge_cli/adapters/*.py`): no reference
to Specification Drift, drift, or any related heading. No Adapter
impact.

### Tests

No test surface exists or is warranted — no renderer, no validator, no
CLI behavior touches this artifact. Consistent with this Change being
correctly classified non-behavioral.

## Compatibility Finding

Nenhum impacto retroativo: os quatro `specification-drift.md` reais
não são reescritos; nenhuma mudança de Protocol integer, Change
Schema, Decision mechanics, ou frozen subject semantics.
`specification-review.md`/`SR-xxx` inalterados.
