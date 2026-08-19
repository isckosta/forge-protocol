---
forge:
  artifact: plan
  schema: 1
change: CHG-0016
status: approved
---
# Plan — CHG-0016

**Written for DEC-001 = Alternative A (Specification's recommendation:
SHOULD-only guidance, no Gate change, no new Protocol integer).
DEC-001 is resolved (human, 2026-08-19): Alternative A confirmed. The
Alternative-B contingency notes below (step 4, step 2) describe what was
**not** chosen and are retained only as the recorded rationale for why
this Plan takes the shape it does — they are not open branches.

1. Canonical guidance: new `protocol/artifact-structure.md` — Principles
   (FR-001), per-Artifact-type structural guidance for all fourteen real
   types (FR-002), written per `architecture.md`'s Content Shape section,
   citing this repository's own real precedent rather than inventing new
   convention where a real one already exists (`architecture.md`'s
   itemized list per type is the authoring outline).
2. Protocol docs: `protocol/contract/engineering.md` (append `C-067`
   onward — exact count depends on how many distinct guidance-reference
   rules are needed; expected 2-3: one for the guidance's existence/
   non-binding status, one for the outcome-first recommendation, one for
   the Plan-boundary/no-silent-mutation recommendation); `protocol/
   specification.md` (new `§41`, brief pointer, matching `§39`/`§40`
   style); `protocol/compatibility.md` (new addendum, "Canonical Artifact
   Structure (CHG-0016)", same "optional artifact, no Protocol bump"
   template as the three prior addenda).
3. Repository docs: one added sentence to `ARCHITECTURE.md` §5 (per
   `architecture.md`; matches CHG-0015's own "one added sentence"
   precedent for its own `ARCHITECTURE.md` touch).
4. Codex Adapter: `src/forge_cli/adapters/codex/projection.py` — add
   `artifact_structure_content` (name TBD at Implementation) to
   `CodexProjectionInput`/`CodexProjectionBundle`, loaded via the existing
   `_resource()` mechanism from the new `protocol/artifact-structure.md`.
   No `adapter.yml` capability change. *(DEC-001 = B only: add a narrow
   validation function in `src/forge_cli/validation/__init__.py` checking
   for `## Result`/`## Verdict` heading presence in Verification/Review,
   wired the same way `_validate_unresolved_decisions` is wired per
   `CHG-0015/plan.md`'s own precedent for adding a new always-on check —
   not built under Alternative A.)*
5. Tests: TDD-001 through TDD-003 per `test-strategy.md`, plus the
   `forge validate`/`forge doctor` baseline capture (TDD-003) against
   every real historical Change directory, recorded before any
   Implementation edit lands, matching `CHG-0013`'s and `CHG-0015`'s own
   stated Plan practice.
6. Canonical examples: new `examples/canonical-artifacts/` directory with
   one example `verification.md` and one example `review.md`, each
   annotated (HTML comments) with which principle each section
   demonstrates, per `architecture.md`'s Canonical Examples section.
   `examples/golden-path-standard/` is left untouched (Discovery: it is a
   code-fixture directory, not a Markdown-artifact showcase — mixing
   would violate Artifact Responsibility).
7. Documentation/Knowledge Capture (deferred content, not authored now):
   `docs/adr/0014-canonical-artifact-structure.md` (per `architecture.md`'s
   ADR determination, F-008) — the exact number is re-verified against
   `docs/adr/` immediately before this step, not assumed frozen at
   Planning time (Specification Review's own finding on this point);
   `CHANGELOG.md` entry; `knowledge-capture.md`. No RFC (F-008's
   RFC threshold is "Material Protocol Changes"; this Change's own
   Specification FR-011 already made this determination — Documentation
   stage confirms, does not re-litigate it, since Discovery/Specification
   already did the comparative-precedent analysis F-008 requires).
   `traceability.yml` and `tdd-evidence.yml` are **not** produced by this
   Plan — same reasoning `CHG-0015/plan.md` step 7 already recorded for
   itself: producing them before any test exists would be reconstructed
   evidence, forbidden by C-016/C-021.
8. Strict Review: adversarial, evaluating in particular INV-001 (no
   duplicated normative authority actually introduced, not just
   specified), the DEC-001-contingent wording throughout Contract/
   compatibility text, and whether the canonical examples actually
   demonstrate outcome-first structure or merely claim to.

## Validation Strategy

`pytest -q` (existing suite plus TDD-001/002/003), `forge validate`,
`forge doctor` — all three against the TDD-003 baseline captured in step
5, before Implementation begins.

## Compatibility Impact

None under DEC-001 = Alternative A: no Schema change (CON-002/AC-012), no
Gate change, no historical Change invalidated, no new Protocol integer.
Under Alternative B: one new integer Protocol, prospective-only, plus one
new narrow Core validation function — explicitly called out at step 4 and
in `architecture.md`'s Compatibility section, not silently absorbed if
selected.

## Implementation Boundary

This Plan and the following Tasks are the last planning artifacts
produced in this session, and are themselves the first live demonstration
of FR-005/AC-005 (a canonically named, always-last boundary section
rather than ad-hoc "Explicit boundary" prose — this section replaces what
two prior Changes each wrote from scratch).

Reaching `tasks_ready` (`full.yml`'s `before_implementation` Gate) is not
authorization to begin Implementation. Steps 1-7 above, as actual
production Markdown/YAML/Python content (not the design already recorded
in `architecture.md`/`test-strategy.md`), require an explicit, separate
human go-ahead in a later message — distinct from, and in addition to,
DEC-001's resolution above. DEC-001 being resolved unblocked the
`specification_review_passed` Gate mechanically (`forge validate` — see
`test-strategy.md` TDD-003 baseline); it did not, by itself, authorize
Implementation. `tasks.md` below has every task unchecked; none has been
started.
