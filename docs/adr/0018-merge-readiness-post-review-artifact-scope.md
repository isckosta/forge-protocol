# ADR-0018 — Merge Readiness Post-Review Artifact Scope (Temporal Boundary)

Status: Accepted for CHG-0046, independent Strict Review passed (Iteration 3).

## Decision

`forge-merge-readiness`'s MR-015 check (`REVIEW SUBJECT STALE`) now
tolerates any path inside a Change's own `.forge/changes/CHG-xxxx-*/`
directory changing after that Change's Review subject is frozen, but only
once `manifest.yml: state.current` has reached `complete` at the commit
under evaluation. Before this Change, MR-015 hardcoded a fixed
three-file allowlist (`manifest.yml`, `provenance.yml`, `review.md`),
which blocked any Change from merging if its Documentation Impact,
Knowledge Capture, or Completion-stage bookkeeping — legitimately
scheduled *after* `strict_review` in every canonical Flow's own `stages`
list — touched any other Change-local file after the freeze. This was not
hypothetical: it was actively blocking CHG-0045's PR #36, a Change that
had genuinely passed Strict Review.

Two designs were considered for the allowed set (Specification Review
SR-001/SR-002 in `.forge/changes/CHG-0046-.../specification-review.md`):
deriving it from which canonical Flow stages run after `strict_review`
(per-artifact, per-stage mapping), or a temporal boundary keyed on
`state.current`. The stage-mapping design was rejected — Discovery's own
evidence showed two of the four Change-local artifacts CHG-0045's PR
actually touched post-freeze (`tasks.md`, a continuously-updated checklist
not attributable to one stage; `specification-drift.md`, documented in
`protocol/artifact-structure.md` as having no Flow stage or code
representation at all) cannot be derived from a stage map. The temporal
design was selected instead, deliberately mirroring an already-shipped
precedent for the identical invariant: `forge validate`'s own local C-026
check (`validation/__init__.py`) already stops enforcing this exact
staleness condition once `state.current == "complete"`. `state.current`
is not a bare, uncorroborated self-attestation here — reaching it requires
MR-005 and MR-016 to independently confirm `verification.md`/`review.md`/
`provenance.yml` actually exist as committed evidence first.

Separately, the materiality policy (`protocol/policies/merge-readiness.yml`)
gained explicit classification for ten Agent Adapter–generated paths
(`.claude/CLAUDE.md`, `.claude/skills/forge/**`, `.agents/skills/forge/**`,
`.forge/adapters/*/installation.yml`) that previously fell through to
`ambiguous` (MR-017) — real, digest-tracked Adapter output the same PR
also needed to touch, blocking it a second, independent way. Both fixes
were themselves subject to an independent Strict Review, which found and
required correction of two implementation defects before passing: an
unguarded manifest-state read that could crash the CLI (R001), and a
materiality prefix broader than this Change's own declared design,
silently sweeping in adapter-directory files never intended to be
reclassified (R002) — see `review.md` Iterations 1–3 for the full record.

A related, more severe, and unrelated gap was found and deliberately
**not** fixed by this Change: MR-015 provides no protection at all, in
either direction, against a *completed* Change's actual implementation
changing outside its own `change_root` — a pre-existing limitation of
MR-015's `-- change_root` diff scope, independent of `state.current` and
independent of this Change. Recorded explicitly (Discovery, Specification
Out of Scope) rather than left an implicit, false assumption; closing it
is a materially larger, separate undertaking (the same repo-wide-vs-per-
Change tension CHG-0036 already resolved once, now for the completed
state specifically) left for a future Change.
