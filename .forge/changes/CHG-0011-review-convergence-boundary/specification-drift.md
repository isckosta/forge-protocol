---
forge:
  artifact: specification_drift
  schema: 1
change: CHG-0011
status: complete
---
# Specification Drift — CHG-0011

Independent Strict Review Iteration 1 (`review.md`) found three implementation
defects that also invalidated parts of the original `specification.md`. This
Resolution corrects both the implementation and the Specification text itself
(not merely the code), per Contract C-006/C-007 (no silent Requirement
mutation; Specification precedes behavioral change).

- **CHG-0011-R001 (BLOCKER).** `review.convergence.decision` was a single
  manifest-wide field. FR-012/FR-014/FR-015 and Protocol 2 Specification §13
  are corrected to define `convergence_decision` as a field on the specific
  Iteration immediately following the point a Non-Convergence episode's limit
  was reached, checked independently at every such historical point. This is
  a genuine Requirement correction, not an implementation-only fix: the
  original FR-012/FR-015 text was itself insufficiently precise to prevent
  the bypass.
- **CHG-0011-R002 (MAJOR).** AC-009's original text ("appending a new
  `initial_review` Iteration with or without a decision record is legal")
  directly contradicted FR-012. It is retracted and replaced, not merely
  reworded — the contradiction reflected a real drafting error, not just an
  underspecified detail.
- **CHG-0011-R003 (MAJOR).** FR-003/FR-005 permitted `fnmatch`-style glob
  scope declarations. This is narrowed to exact-path-only declarations;
  `fnmatch` is removed from the implementation rather than hardened, since no
  degenerate-pattern heuristic was part of this Change's minimal-mechanism
  mandate.
- **CHG-0011-R004 (MINOR).** FR-013 and `architecture.md`'s validator-changes
  step 8 overstated what is mechanically enforced (implying `evidence_gap`/
  `finding_classes` content is checked). Reworded to state plainly that
  `new_material_findings` is a self-declared, evidence-*expected* value —
  the same trust boundary Protocol 2 already applies to blocker/major/minor/
  observation counts — rather than a mechanically cross-checked one. No code
  change: the Specification's claim was wrong, not the implementation.
- **CHG-0011-R005 (OBSERVATION).** Accepted as an intentional, already-honest
  scope narrowing (FR-011's rationale and `test-strategy.md` TDD-014 already
  disclosed it); not resolved by design. Recorded as a follow-up in the final
  report rather than expanded into this Change's scope.

No Requirement was weakened to reduce Resolution effort. R001's fix makes the
mechanism *more* restrictive (a decision now authorizes exactly one episode,
not every future one); R003's fix removes an entire bypass class rather than
attempting to patch around it.
