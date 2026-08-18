---
forge:
  artifact: inspection
  schema: 1
change: CHG-0012
status: complete
---
# Inspection — CHG-0012

## Root cause

`src/forge_cli/validation/__init__.py:348` (before fix):

```python
elif status in{"pending","passed"} and _changed(r,mpath,sim[1]):out.append(...)
```

`_changed` computes the effective reviewable workspace delta between the
Iteration's frozen subject commit and current `HEAD`, excluding only that
Change's own three review-control-metadata paths. Once any other Change's
commits touch any file outside those three paths — inevitable and expected
on a shared `main` branch — this fires for every passed Iteration of every
*completed* Change, forever, because nothing exempted a Change whose
`state.current` is already `complete`.

Confirmed on GitHub Actions run `32091880352` (workflow "Tests", step
"Validate Forge repository"): exit code 2, two findings, one each for
`CHG-0008` and `CHG-0011` — both already `state.current: complete`, both
last-passed by an independent Reviewer, both immediately broken by the very
next commit that touched an unrelated file (the other Change's own merge).

## Precedent for the fix

The same function already exempts `complete` Changes from a different
check, two branches earlier in the same `for mpath in ...` loop
(`src/forge_cli/validation/__init__.py:296`):

```python
if m.get("schema")=="forge/change@1":
    if not isinstance(st,dict)or st.get("current")!="complete":out.append(...)
```

The freeze-drift check lacked the equivalent `state.current == "complete"`
exemption. This Change adds it, following the existing pattern rather than
introducing a new one.

## Classification

FAST. `localized_validation_correction`: a single boolean condition added to
one existing check in one function, with a directly parallel precedent
already in the same function. No new Contract rule, schema field, or
Protocol concept. No architectural, security-model, or cross-module change.

## Scope verified not to include

- Any other C-026 invariant (provenance authority, Execution/Context
  independence, Iteration identity history, immutable subject/record
  rewriting) — unaffected; `test_active_change_still_detects_freeze_drift`
  proves the freeze remains exactly as strict for a non-complete Change.
- CHG-0008/CHG-0011's own historical manifests — unmodified by this Change.

## Correction after Strict Review Iteration 1, and the final decision (see `specification-drift.md`)

The first implementation attempt exempted `state.current == "complete"`
unconditionally from the drift check. Independent Strict Review Iteration 1
found this a BLOCKER (CHG-0012-R001): it also silently disabled detection of
the Change's *own* reviewed files being tampered with, not only unrelated
repository activity — reproduced directly against `validate_project`.

Two further attempts tried to precisely bound that protection by reasoning
about *when* `state.current`'s mutable history became trustworthy
(`_first_commit_where_state_complete`, added then removed across this
Change's history); each closed one gap and opened another
(CHG-0012-R002, R003), reaching CHG-0011's Convergence Limit. A fourth,
structurally different attempt (scope the comparison to the paths the
implementation itself touched, checked permanently against `HEAD`) closed
all three but reintroduced real CI friction on shared files, and was not
adopted.

**`_first_commit_where_state_complete` does not exist in the shipped code.**
The final, engineer-approved code reverts to this section's original
unconditional `state.current == "complete"` exemption — the same shape as
CHG-0012-R001 — this time with that finding's residual risk explicitly
accepted and documented rather than silently reintroduced. See
`specification-drift.md`'s "Final decision" section for the complete
four-attempt history and the accepted trade-off.
