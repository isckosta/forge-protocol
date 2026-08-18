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
- `CHG-0008`'s own completed manifest currently fails `forge validate` with
  a C-026 freeze finding, confirmed present on a clean `main` checkout with
  none of this Change's edits. It is not caused by CHG-0011 and is out of
  this Change's declared scope; recorded as a follow-up (see final report).
