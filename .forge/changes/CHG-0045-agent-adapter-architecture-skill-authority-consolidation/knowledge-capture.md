---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0045
status: complete
---
# Knowledge Capture — CHG-0045

## What Changed

The Claude Code and Codex Adapters' Reviewer/Resolver-independence (C-026)
projection text moved from two independently hand-maintained copies (one
per Adapter, the Claude Code copy additionally re-emitted once per
effective Flow) to a single shared source,
`src/forge_cli/adapters/review_independence.py`. The generated
`PreToolUse` guard's tool coverage widened from `Bash`-only to
`Bash`+`Edit`+`Write`. A Bootstrap-section instruction now directs an
operating agent to check the Adapter's existing digest-based drift record
before trusting `references/*`, and a structured boundary-reporting
format was added for human-authority/blocked/missing-evidence Gates.
`.forge/adapters/*/installation.yml` — previously untracked in this
repository's entire history — is now committed.

## Durable Knowledge

- **Any commit touching a non-review-control-metadata path after a
  Change's Review subject freezes invalidates that Review's mechanical
  C-026 check, even if the net content change is semantically inert or
  is itself later reverted to identical content.** After Strict Review
  Iteration 3 passed, an unrelated housekeeping commit (tracking a
  pre-existing, already-byte-identical `.claude/CLAUDE.md`) immediately
  broke `forge validate` with `"C-026 review subject changed after its
  immutable revision freeze"` — Core compares committed paths against the
  frozen subject commit, not commit *content* against reviewed content,
  and cannot know a new commit's change is a no-op relative to what was
  already reviewed. Reverting the commit (net diff back to empty for
  those paths) fixed it immediately. **Consequence for future Changes:**
  once a Change's Review subject is frozen — and especially once it has
  `passed` — do *not* commit anything on that Change's branch beyond the
  three exempt review-control paths (`manifest.yml`, `provenance.yml`,
  `review.md`), even for unrelated, obviously-safe repository housekeeping
  discovered along the way. Do that housekeeping on a separate branch, or
  after the Change merges.
- **`forge adapter update`/`forge adapter install` do not offer a
  supported recovery path when an Adapter's `installation.yml` predates
  real, accumulated canonical `protocol/` drift** — both refuse outright
  via `AdapterService`'s own `_reject_drift`/`_reject_conflicts` guards
  (and `publish_adapter_plan`'s own internal conflict check refuses too),
  even after independently confirming, via `git diff`/`git log`, that no
  genuine hand-customization exists to protect. The only path forward
  found was a one-time, human-authorized direct write using the same
  production `driver.project()` code path plus a hand-rebuilt
  `installation.yml` from real on-disk digests. This is disclosed in
  `specification-drift.md` and is real follow-up work for a future
  Change (a `forge adapter update --acknowledge-stale-baseline`-shaped
  command, or equivalent), not built here.
- **A repository-wide, path-based "has anything changed since freeze"
  check cannot distinguish Change-relevant untracked files from
  unrelated ones.** `_reviewable_workspace_delta()`
  (`src/forge_cli/validation/__init__.py`) unions committed, staged,
  unstaged, *and* untracked paths across the *entire* repository, not
  just paths plausibly relevant to the Change being checked — so any
  stray untracked file anywhere (a browser-tool cache directory, an old
  session report from a different Change) can spuriously fail a
  completely unrelated Change's `forge validate` once that Change's
  Review reaches `passed`. Recorded as this Change's own Strict Review
  R008 (non-blocking, Out of Scope — a Core validation-logic gap, not
  something CHG-0045 fixes). Worked around here by moving the offending
  pre-existing files out of the working tree (not deleting, not
  committing them on this branch) — reversible, and unblocks `forge
  validate` without touching the frozen Review subject.
- **`forge validate`'s C-026 rewrite-protection genuinely fires on an
  in-place edit of an already-committed provenance record, including
  inside `provenance.yml` itself** (one of the three review-control-
  metadata-exempt paths) — the exemption covers *which files* may differ
  post-freeze, not *rewriting an existing record's own prior content*
  within them. Confirmed by direct reproduction: adding `scope`/`targets`
  fields to an already-committed `resolution-001` record in place
  produced `"C-026 immutable subject provenance differs from its first
  committed record; frozen subject authority cannot be rewritten"`. The
  correct fix was a new, additional record (`resolution-001-scope`)
  referencing the same, unchanged commit, with the Review Iteration's
  `subject_provenance` repointed at it — the original record left
  byte-for-byte untouched.
- **An independent Strict Review subagent, given no access to the
  Implementation conversation and instructed to reproduce every claim
  against real repository state rather than trust artifact prose,
  reliably finds real defects a self-reviewing Implementer misses** — in
  this Change's own case, a genuine test failure (`traceability.yml`
  schema violation) that had been asserted as passing in both
  `verification.md` and `provenance.yml`. This is the mechanism working
  as designed, not friction to route around.

## Consequences for Future Changes

- A future Contract wording change to C-026, or a third Harness Adapter,
  touches `review_independence.py` once, not once per Adapter.
- A future Change that discovers unrelated, safe repository housekeeping
  mid-Implementation (an untracked file worth tracking, a `.gitignore`
  gap) should land it *before* freezing that Change's own Review subject,
  or on a separate branch entirely — never after that Change's Review has
  already passed.
- The Adapter-republish recovery-command gap (specification-drift.md)
  and the repository-wide untracked-file `forge validate` gap (R008) are
  both real, disclosed, and unaddressed. Either is a reasonable, scoped
  follow-up Change.

## References

- `.forge/changes/CHG-0045-agent-adapter-architecture-skill-authority-consolidation/specification-drift.md`
- `.forge/changes/CHG-0045-agent-adapter-architecture-skill-authority-consolidation/review.md` (R006, R007, R008)
- `docs/adr/0018-agent-adapter-skill-authority-consolidation.md`
- `src/forge_cli/adapters/review_independence.py`
