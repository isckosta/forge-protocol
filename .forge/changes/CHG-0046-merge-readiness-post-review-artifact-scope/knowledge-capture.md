---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0046
status: complete
---

# CHG-0046 · Knowledge Capture

> **Durable Knowledge**
>
> Records knowledge produced by this Change that should remain useful for future development, maintenance, and decisions — not a summary of the Change itself.

## What Changed

`forge-merge-readiness`'s MR-015 check now tolerates any Change-local path
changing after a Review subject freezes, once the Change reaches
`state.current: complete` — replacing a hardcoded three-file allowlist
that blocked a real, already-passed-Review Change (CHG-0045's PR #36).
MR-017's materiality policy gained explicit rules for ten Agent
Adapter–generated paths that previously fell through to `ambiguous`. Two
Strict Review iterations found and required fixing real defects in the
first implementation before a third passed.

## Durable Knowledge

Two independent implementations of the same Contract invariant can
silently diverge. `forge validate`'s local C-026 check
(`validation/__init__.py`) and `forge-merge-readiness`'s CI-only MR-015
check (`merge_readiness/evaluator.py`) both exist to detect "the Review
subject changed after freeze," but were built at different times with
different scoping choices (whole-repo vs. `change_root`-only) and,
crucially, only one of them had the `state.current != "complete"`
carve-out. Nothing compared them to each other; CI's own two steps on the
same commit — "Validate Forge repository" (passing) and "Evaluate Forge
Merge Readiness" (failing) — quietly disagreed until a real blocked PR
forced the comparison. When two checks share a name or a stated purpose,
verify they share behavior too, rather than assuming a shipped precedent
in one automatically extends to the other.

A Specification's Acceptance Criteria can overclaim by omission, not just
by explicit falsehood. AC-002's original wording ("MR-015 still fires for
`change_root`-external changes") sounded like a regression guard but
described a protection that never existed — discovered only when
Architecture traced the actual code, not when Specification Review read
the prose. Tracing a claimed *existing* behavior against the real code,
not just the *proposed* behavior against the Specification's prose, is a
distinct check worth doing deliberately — Specification Review's own
adversarial pass caught two other real defects (SR-001, SR-002) but not
this one, because both were about the *design being proposed*, not about
verifying a claim of *already-true* behavior.

Provenance records that satisfy a mechanical schema check (`scope`/
`targets` on a `resolution_verification`'s subject) are easy to omit when
writing a Resolution record for the first time, because nothing forces
them into existence at that moment — the gap only surfaces later, at the
next Resolution Verification. This is the same class of gap CHG-0045's own
R007 hit (`resolution-001-scope`, an append-only corrective record, not a
rewrite) — now confirmed to recur across at least two Changes. A future
Change could usefully add this to the Plan/Tasks template for any
`resolution-001`-shaped record, so it stops being rediscovered per-Change.

## Consequences for Future Changes

- **`forge-merge-readiness` (CLI):** MR-015's tolerance is bounded by
  `state.current: complete`, not by which Flow stage an artifact belongs
  to — a future Change adding a new post-`strict_review` Flow stage does
  not need to touch `evaluator.py` at all; the temporal boundary already
  covers it.
- **`forge-merge-readiness` (CLI), out of scope here:** MR-015 still
  provides no protection against a *completed* Change's implementation
  changing outside its own directory (Discovery; Specification Out of
  Scope). A future Change closing this needs to resolve the same
  repo-wide-vs-per-Change false-positive tension CHG-0036 already fought
  once, for the completed state specifically.
- **`forge validate` (CLI), out of scope here:** a real, reproducible,
  pre-existing crash exists at `validation/__init__.py:321`
  (`st=m.get("state")or{}`, the identical unguarded-string-state shape
  R001 fixed one file over) — flagged separately, not fixed by this
  Change.
- **Review workflow:** when writing a `resolution-NNN` provenance record
  for the first time, include `scope`/`targets` immediately rather than
  waiting for a Resolution Verification to demand it as a follow-up
  `-scope` record.

### K-001 · Three independent internal Strict Reviews all missed the same thing an external reviewer caught by reading the Protocol text directly

The `state.current`-keyed design (DEC-001) passed Specification Review
(SR-001/SR-002) and three independent internal Strict Review Iterations
(R001–R004, all real, all correctly caught and fixed) before an external
reviewer — a GitHub Codex bot on the opened PR, with no special access,
following the same public repository — found it directly contradicted
`protocol/versions/2/specification.md` §5/§14's own literal text. None of
the internal passes had cross-referenced the design against Protocol 2's
own normative specification document; they reasoned from an internal
precedent (`forge validate`'s own carve-out) and from the code's internal
consistency, both real and useful checks, but neither is a substitute for
checking a design against the actual governing specification text when
one exists and is directly on point. **Durable lesson:** when a Change
modifies mechanical enforcement of a named Protocol invariant (here,
C-026 / Sec 5's freeze rule), at least one Review pass — internal or
external — must explicitly re-read the relevant Protocol section's literal
text against the diff, not just check the diff's internal logic and test
coverage. Three rounds of "does this code do what it says" review did not
substitute for one round of "does this design match what the Protocol
actually requires."

## References

- Decisions: DEC-001 (superseded — temporal `state.current` boundary),
  DEC-002 (Plan Decision, C-077), DEC-003 (the corrected, shipped design —
  explicit anchored scoped renewal records).
- `docs/adr/0018-merge-readiness-post-review-artifact-scope.md` (DEC-003,
  the material architectural decision, and its correction history).
- `specification-drift.md` for the full Root Cause / Evidence / Final
  decision record of the correction.
- `review.md` for every Iteration's full findings and Resolution
  evidence, across both the original and corrected designs.
- Discovery's "A more severe, orthogonal, pre-existing gap..." and
  "Addendum (post-Review)..." sections for the two out-of-scope findings.
