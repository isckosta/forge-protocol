---
forge:
  artifact: specification_review
  schema: 1
change: CHG-0046
status: pending
---

# Specification Review — CHG-0046 Merge Readiness Post Review Artifact Scope

## Verdict

**PASS (two findings, both resolved in the same authoring session).**

Per `protocol/flows/full.yml`'s `specification_review` Gate (`mode:
adversarial`), this Review actively searched for requirements that look
verifiable but do not actually cover the real artifact-usage patterns
Discovery evidenced, rather than re-reading the Specification for style.
Per `protocol/versions/2/specification.md`, Protocol 2's independent-
Execution/Context requirement (C-026) binds Strict Review only, not
Specification Review, so running this Review in the same
session/Execution/Context that authored the Specification is conforming.

## Findings

### SR-001 (MAJOR) — FR-001's stage-to-artifact derivation cannot cover two of Discovery's own four observed post-freeze artifacts
**Found:** FR-001 as originally written required deriving the post-freeze
allowed-file set from "which canonical Flow stages are scheduled after
`strict_review`" (a per-artifact, per-stage mapping). Re-checking
Discovery's own reproduction against that model breaks it on two of the
four Change-local paths CHG-0045 actually changed post-freeze:
`tasks.md` is not a post-Review-stage artifact at all in the canonical
scaffold mapping (`_STAGE_FILES["tasks"]` maps to the pre-Review `tasks`
stage) — CHG-0045 amended it post-freeze as a continuously-updated
checklist recording Review Iteration 3's outcome and Completion
bookkeeping (T-022–T-025), not as new "tasks" stage output.
`specification-drift.md` is stronger still: `protocol/artifact-structure.md:436-441`
states explicitly it "has no scaffold, no Flow stage, and no code
representation anywhere in the repository... created by hand, only when
Protocol §13 actually applies" — which can be during or after Resolution,
with no stage id to derive from at all. A strict stage→artifact mapping
would still incorrectly flag both as stale, defeating FR-001's own
purpose, and AC-003 as originally written compounded this by naming
`tasks.md`-shaped artifacts as things that "must still" trigger MR-015 —
which Discovery's own evidence shows is wrong.
**Resolution:** FR-001 rewritten to specify a temporal boundary — any
Change-local artifact may change without triggering MR-015 once the
Change has reached `state.current: complete` — instead of a per-stage
derivation that cannot cover every artifact real Changes legitimately
touch post-freeze. This is not a new invention: it is exactly the
carve-out `forge validate`'s own C-026 check already uses
(`validation/__init__.py:375`, `st.get("current")!="complete"`), which
Discovery already cited as the working precedent MR-015 disagrees with.
AC-001 and AC-003 revised accordingly; AC-002 (implementation changes
outside the Change directory) is untouched and remains the primary
regression guard. Applied directly to `specification.md`.

### SR-002 (MAJOR) — CON-002 ruled out the only design SR-001's resolution actually needs
**Found:** CON-002 as originally written prohibited MR-015's outcome from
depending on a Change's self-reported `manifest.yml` state "as sufficient
evidence on its own." SR-001's resolution gates tolerance on exactly
`state.current == "complete"` — a self-reported manifest field — which
CON-002, read literally, forbids. This is not accidental: it would rule
out the one design this Specification now selects, in favor of a
stage-mapping design SR-001 just showed does not work. The actual
question is not "may MR-015 ever consult `state.current`" — `forge
validate`'s own already-shipped implementation of the identical invariant
already does — it is whether `state.current` is the *only* thing standing
between a dishonestly-early completion claim and unlimited post-freeze
tolerance. It is not: `state.current: complete` is independently
cross-checked by MR-005 (`COMPLETION NOT READY` unless
`state.current == complete` and, separately, MR-016 requires
`verification.md`/`review.md`/`provenance.yml` to actually exist as
committed files at HEAD before a completion claim is accepted at all), so
a Change cannot reach the tolerated state without those files existing —
it can misrepresent *when* work happened, not manufacture non-existent
Verification/Review evidence out of nothing.
**Resolution:** CON-002 rewritten to state precisely what must not happen
(MR-015 becoming defeatable by `state.current` alone, with no other
completion-gating check corroborating it) rather than forbidding
`state.current` as an input outright. Applied directly to
`specification.md`.

## Checked and found sound

- FR-002/AC-004/AC-005 (materiality policy) do not depend on any Flow-stage
  or Change-state reasoning at all — they are pure path-classification
  rules, unaffected by SR-001/SR-002 and confirmed independently correct
  against Discovery's ten-path list.
- CON-001 (no Contract-meaning change) and CON-003 (fix applies uniformly
  across `fast`/`standard`/`full`) remain sound under the revised FR-001:
  the temporal (`state.current`) boundary is Flow-agnostic by construction
  — it does not reference any Flow's stage list at all, which if anything
  makes CON-003 easier to satisfy than the original stage-derivation
  design would have.
- AC-002 is untouched by SR-001/SR-002. **Correction, found during
  Architecture, after this Review's original pass:** AC-002's original
  wording claimed MR-015 "still fires" for `change_root`-external changes
  as an existing protection this Change must not regress. Architecture's
  own trace of `evaluator.py:134`'s `-- change_root` `git diff` pathspec,
  confirmed by direct reproduction, found MR-015 structurally never
  inspects any path outside `change_root`, independent of `state.current`
  and independent of this Change — there is no such existing protection to
  regress. AC-002 was revised in `specification.md` to bound this Change's
  blast radius rather than assert a protection that does not exist; the
  finding itself is recorded in Discovery ("A more severe, orthogonal,
  pre-existing gap...") and named explicitly in Out of Scope. Corrected
  directly in `specification.md`, not re-litigated as a new SR-numbered
  finding, since it does not change either FR's substance — only AC-002's
  own wording was inaccurate.
- Out of Scope's exclusion of MR-006/MR-008 remains correct: neither
  finding here touches provenance-record completeness, only the temporal
  window in which Change-local *files* may differ from the frozen subject.

## Conclusion

Two defects found and resolved before Architecture. Both concern the same
underlying correction: the allowed-file model for post-freeze changes must
be temporal (bounded by `state.current: complete`, corroborated by MR-005/
MR-016's independent evidence requirements), not a per-Flow-stage artifact
map that Discovery's own evidence (`tasks.md`, `specification-drift.md`)
already contradicts. No finding required an Unresolved Decision escalation.
Proceeds to Architecture, which selects the concrete implementation shape
for this now-corrected temporal-boundary requirement.
