---
forge:
  artifact: specification_drift
  schema: 1
change: CHG-0046
status: complete
---

# Specification Drift — CHG-0046

## Root Cause

DEC-001 (Architecture) selected a temporal boundary for MR-015 —
tolerate any `change_root`-prefixed path differing from the frozen
subject once `manifest.yml: state.current == "complete"` — reasoning
that this mirrored `forge validate`'s own already-shipped
`state.current != "complete"` carve-out for the identical C-026
invariant (`validation/__init__.py:375`). That reasoning treated an
existing implementation's behavior as sufficient precedent without
independently checking it against Protocol 2's own normative text.

It is not sufficient. `protocol/versions/2/specification.md` §5 states,
without qualification: "The only post-freeze paths that MAY differ
without renewing subject provenance are the frozen Change's exact
repository-root-relative `manifest.yml`, `provenance.yml`, and
`review.md` paths. The exception MUST NOT be inferred from... membership
in the Change directory generally." §14 adds: "A manifest claim such as
`state.current: complete`... is not sufficient authorization." DEC-001's
design is exactly the inference §5 names and forbids — a
`state.current`-keyed blanket tolerance for every `change_root` path,
not the three named ones.

This was found by an external, independent reviewer (a GitHub Codex
review bot) on PR #37, reading `protocol/versions/2/specification.md`
directly against `evaluator.py`'s diff — after Architecture, adversarial
Specification Review (SR-001/SR-002), and three independent internal
Strict Review iterations had all reasoned about this design without
citing or re-checking it against Protocol 2's own text. Architecture's
own precedent-matching (`forge validate`'s carve-out) itself likely has
the identical defect — a separate, pre-existing conformance question
this Change does not resolve, flagged separately.

## Evidence

Codex's review comment (PR #37, thread on `evaluator.py:150`, P1):
"When `state.current` is `complete`, this filter skips every path
returned by the Change-local diff, so a commit can rewrite
`specification.md`, `verification.md`, `tdd-evidence.yml`, or other
reviewed evidence after the recorded subject commit and still avoid
MR-015... This violates the Protocol 2 freeze requirement in
`protocol/versions/2/specification.md:25-35`... retain that narrow
exception or require a new frozen subject and review for post-freeze
artifacts." Independently confirmed by reading §5/§8/§11/§14 directly
(quoted above) — the cited text says exactly what the comment claims.

§8 (Completion) reads: "Completion MUST NOT occur when... the frozen
reviewable workspace has changed **without renewed provenance**" — not
an unconditional prohibition on the workspace ever changing, but a
requirement that any change be accounted for by a new, explicit,
anchored provenance record. §11 defines exactly one renewal mechanism
today — `role: resolution` + `resolution_verification`, scoped by
declared `scope`/`targets` (Finding identifiers) — which is
Finding-specific (fixing a Review defect) and does not, by its own
`targets` field's definition, cover ordinary Flow-scheduled
Documentation Impact / Knowledge Capture bookkeeping that targets no
Finding at all. The Protocol does not name a second, lighter renewal
mechanism for that case; it also does not forbid one — §5's own text
("Appending a new provenance record... remains allowed when previously
anchored subject records and Iteration subject bindings remain
unchanged") permits exactly this: a new, self-attested, anchored
`role: implementation` provenance record binding to the later commit,
without redirecting or rewriting the original passed Review's own
binding (which stays immutable, per §5's anchoring rules).

## Final decision

FR-001 and DEC-001 are corrected (superseded, not deleted — see
Architecture's revised Decisions section) to: MR-015's post-freeze
allowed set remains exactly the Protocol's literal three files
(`manifest.yml`, `provenance.yml`, `review.md`); additionally, any
further `change_root`-prefixed delta is tolerated **only** when it is
itself covered by a subsequent, `_first_committed_record`-anchored
`role: implementation` (or `role: resolution`, for Finding-driven
Resolutions, unchanged) provenance record whose `revision.commit`
equals the exact commit at which that delta was introduced — i.e., the
delta must be *explained* by an explicit, auditable, anchored record
naming that later commit, not *tolerated* by an implicit manifest-state
flag. `state.current` is no longer read by MR-015 at all. This requires
CHG-0045 (and any Change whose PR predates this correction) to add one
more self-attested subject-provenance record for its own Documentation/
Knowledge-Capture-stage commit, exactly as it already did for MR-006 —
not a new independent Review, since no Review-relevant material changed,
only Change-local bookkeeping the Flow itself schedules after Review.
