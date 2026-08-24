---
forge:
  artifact: specification_drift
  schema: 1
change: CHG-0045
status: complete
---

# Specification Drift — CHG-0045

## Root Cause

Specification's original Compatibility Statement asserted, unqualified,
that "a `forge adapter update` after this Change's Implementation will
show `UPDATE` (not `CONFLICT`) for the affected generated paths, resolving
Discovery's live drift as an ordinary consequence of republishing, not a
special-cased patch." This was written during Specification, before
Implementation had actually attempted the republish, and rested on an
untested assumption: that `AdapterService`'s ownership/drift guards would
treat "canonical `protocol/` content moved since the last recorded
install" the same way they treat "content is simply new" — as an ordinary
`UPDATE`.

That assumption was wrong. Discovery had already found the *symptom*
(`forge adapter plan claude-code` reporting `CONFLICT`) but had not yet
attempted the actual remediation, so Architecture and Specification both
reasoned from the symptom rather than the mechanism. Architecture's Risks
section came closer — "`forge adapter update` will surface real `UPDATE`s
beyond this Change's own diff" — but still assumed `update` would *run*,
only that its output would be noisier than expected, not that it would
refuse outright.

## Evidence

`tasks.md` T-016 and `verification.md`'s "Adapter Republish — how it was
actually done" section record what actually happened: `forge adapter
update claude-code`/`codex` and `forge adapter install claude-code`/`codex`
were both attempted, in that order, against this repository's real
pre-existing state, and both refused for both Adapters —
`AdapterService._reject_drift()` (comparing on-disk digests against
`installation.yml`'s stale recorded digests) and, separately,
`_reject_conflicts()`/`publish_adapter_plan`'s own internal conflict check
(comparing on-disk content against freshly-computed content) each
independently blocked the operation. Neither guard is wrong to exist —
both are doing exactly the job they were built for: refusing to silently
overwrite a `forge_owned` path whose on-disk state doesn't match what
Forge last recorded installing. The gap is that neither guard, nor any
CLI flag, offers a supported path forward once an operator has manually
confirmed (as this Change's Discovery and Verification both did, via
`git diff`/`git log` and digest inspection) that the mismatch is pure
staleness, not a customization worth preserving.

The independent Strict Review (Iteration 1, `review-001`) confirmed this
by reproducing the same refusal path directly against `src/forge_cli/
adapters/service.py`, `ownership.py`, and `planner.py`, and found this
Change's own Specification had not been corrected to reflect what
Implementation actually discovered — the "ordinary consequence" framing
stood, unrevised, alongside a Verification section that itself, honestly,
described an extraordinary one-time bypass.

## Final decision

The Compatibility Statement is corrected (this commit) to state plainly
that the republish required a one-time, human-authorized bypass, not an
ordinary `forge adapter update`, and that the same refusal is latent in
every other Forge-governed repository with this Adapter installed under
similarly stale conditions. Building a supported recovery command (e.g.
`forge adapter update --acknowledge-stale-baseline`) is explicitly **not**
undertaken by this Change — it is new Adapter-CLI surface (F-005 scope),
untested against the variety of staleness conditions a real second
repository might exhibit, and not something Architecture evaluated
alternatives for. It is recorded as follow-up work in
`knowledge-capture.md` instead of being silently absorbed into this
Change's already-approved Plan (C-069) or invented under Review pressure
without its own Architecture-level consideration.
