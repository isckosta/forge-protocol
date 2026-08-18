---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0011
status: complete
---
# Knowledge Capture — CHG-0011

- Resolution Verification scope is anchored entirely through fields already
  covered by the existing Git-history-anchoring machinery
  (`_first_committed_provenance_record`): `scope`/`targets` are ordinary
  fields on a `resolution`-role provenance record, so they inherit
  immutability-once-committed for free. No new anchoring mechanism was
  needed — extend, don't parallel-build.
- Resolution Delta and the Protocol 2 §5 effective-workspace freeze look
  similar (both diff "since a frozen commit") but solve different problems:
  the freeze compares a frozen commit against the *current* workspace
  (staged/unstaged/untracked matter); Resolution Delta compares two
  *already-frozen historical commits* (only the committed diff applies).
  Conflating them was an early Specification mistake, caught and corrected
  during Architecture before any code was written — cheaper to catch there
  than in Implementation.
- A convergence/loop counter recomputed only as a *trailing* run is not
  enough to guarantee "decision required once the limit is reached" stays
  enforced — a later unrelated Iteration (e.g. a fresh, unrestricted
  `initial_review`) resets the trailing run and can silently un-trigger a
  check that depended on it. The general lesson: a state derived from
  history for anti-manipulation purposes needs a full-history scan for any
  "was this limit *ever* reached without being handled" check, not just a
  "is it currently true" check. This is the second time this kind of
  historical-vs-current distinction has mattered in this Protocol
  (`CHG-0008`'s R008 made the same distinction for Review Iteration subject
  binding authority independent of current verdict status).
- `forge validate` does not JSON-Schema-validate `manifest.yml`/
  `provenance.yml` today; `change-v2.schema.json` and
  `execution-provenance.schema.json` are normative machine-readable
  documents, but the actual mechanical Gate is hand-written Python in
  `src/forge_cli/validation/__init__.py`. This was true before CHG-0011 and
  remains true after; noted here so a future Change does not assume schema
  validation is happening where it is not.
- A shared "authorization" field that is checked only for *existence*, not
  for binding to the specific thing it authorizes, is a reusable-bypass
  pattern independent of this Protocol — the same shape as a stale approval
  token, a cached permission grant, or (closer to home) the exact
  self-declared-counter risk this Change's own Discovery phase flagged and
  fixed for the *counter*. Independent Strict Review Iteration 1 found the
  same shape had silently reappeared one field over, in the *decision*
  record, which received no equivalent binding. General lesson for this
  Protocol going forward: when a Change introduces a field whose presence is
  meant to authorize a specific past event, ask explicitly whether the field
  is bound to *that instance* of the event or merely to *the field's own
  existence* — the latter is bypassable by construction once more than one
  instance of the event can occur.
- Permitting a general-purpose pattern language (glob/wildcard matching) for
  a containment check is a broader attack surface than the containment
  check's own author usually accounts for at design time — a scope narrowly
  intended to mean "these specific files" can always be widened by a pattern
  general enough to mean "everything." Preferring exact enumeration over
  patterns, even at some ergonomic cost, is the safer default for this class
  of allowlist.
- **Pre-existing risk, not introduced here, surfaced by this Change's own
  self-check:** `_first_committed_review_iteration`'s historical-authority
  check (CHG-0008) only compares `revision`/`subject_provenance` between the
  current and first-committed representation of an Iteration; `status` and
  other lifecycle fields are documented as "independently mutable" by
  CHG-0008's own architecture. That means a committed Iteration's `status`
  could in principle be edited from `failed` to `passed` (or a
  `convergence_decision` added retroactively) without a genuinely new review
  execution, and today's mechanism would not catch it — the same gap applies
  to `kind`, `full_review_required`, and `convergence_decision` introduced
  here, since they inherit the same "lifecycle field" treatment. This is not
  a regression CHG-0011 introduces; it is an existing boundary of what
  Protocol 2's provenance-authority mechanism protects, worth flagging for a
  future Change rather than silently discovering it again later. See final
  report's Remaining Risks.
- `CHG-0008`'s own completed manifest currently fails `forge validate` with
  a C-026 freeze finding, confirmed present on a clean `main` checkout with
  none of this Change's edits. It is not caused by CHG-0011 and is out of
  this Change's declared scope; recorded as a follow-up (see final report).
