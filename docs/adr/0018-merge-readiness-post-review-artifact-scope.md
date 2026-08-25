# ADR-0018 — Merge Readiness Post-Review Artifact Scope (Anchored Renewal Records)

Status: Accepted for CHG-0046, independent Strict Review passed.

## Decision

`forge-merge-readiness`'s MR-015 check (`REVIEW SUBJECT STALE`) now
tolerates a specific Change-local path (inside a Change's own
`.forge/changes/CHG-xxxx-*/` directory) differing from its frozen Review
subject, when — and only when — an explicit provenance record exists
(`role: implementation` or `role: resolution`) whose commit is an
ancestor of (or equal to) the commit under evaluation, whose first
committed representation is unchanged (anchored, reusing the same
`_first_committed_record` check MR-021 already applies to subject
records), and whose declared `scope` (an exact list of repository-relative
paths, mirroring the `scope` shape Protocol 2 §11 already defines for
`resolution` records) includes that specific path. Before this Change,
MR-015 hardcoded a fixed three-file allowlist (`manifest.yml`,
`provenance.yml`, `review.md`) with no escape hatch at all, which blocked
any Change from merging if its Documentation Impact or Knowledge Capture
bookkeeping — legitimately scheduled *after* `strict_review` in every
canonical Flow's own `stages` list — touched any other Change-local file
after the freeze. This was not hypothetical: it was actively blocking
CHG-0045's PR #36, a Change that had genuinely passed Strict Review.

**This design is the result of a correction.** The first design
considered and rejected was a per-Flow-stage artifact mapping
(Specification Review SR-001: rejected because `tasks.md`, a
continuously-updated checklist, and `specification-drift.md`, which
`protocol/artifact-structure.md` documents as having no Flow stage
representation at all, cannot be derived from a stage map). The second
design — selected, implemented, and passed through three internal
independent Strict Review iterations — tolerated *any* Change-local path
once `manifest.yml: state.current` reached `complete`, deliberately
mirroring an already-shipped precedent (`forge validate`'s own
`state.current != "complete"` carve-out for the identical C-026
invariant). An external, independent reviewer (a GitHub Codex review bot,
on PR #37) then found that design directly contradicts Protocol 2's own
normative text: `protocol/versions/2/specification.md` §5 states "The
only post-freeze paths that MAY differ without renewing subject
provenance are" the three literal files, and "The exception MUST NOT be
inferred from... membership in the Change directory generally"; §14
adds "A manifest claim such as `state.current: complete`... is not
sufficient authorization." Recorded as Specification Drift
(`.forge/changes/CHG-0046-.../specification-drift.md`) — none of
Architecture, adversarial Specification Review, or three internal
independent Strict Review iterations had cross-checked the design against
Protocol 2's own text before shipping it; an external reviewer, reading
the Protocol directly, did. The design in this ADR is the third,
corrected attempt: instead of a single mutable manifest field granting
blanket tolerance, every renewal is an individually anchored, per-path
auditable record — the mechanism Protocol §5's own text explicitly
permits ("Appending a new provenance record... remains allowed") and
implicitly requires (§8: "Completion MUST NOT occur when... the frozen
reviewable workspace has changed without renewed provenance").

One practical consequence: because CHG-0045's own branch predates this
correction, its Documentation/Knowledge-Capture delta has no such renewal
record. Reproducing `forge change merge-check` against its real PR #36
commits after this correction again reports `MR-015` (verified directly,
`verification.md`) until that branch adds one — a real, expected, and
disclosed follow-up, not a regression in this Change.

Separately, the materiality policy (`protocol/policies/merge-readiness.yml`)
gained explicit classification for ten Agent Adapter–generated paths
(`.claude/CLAUDE.md`, `.claude/skills/forge/**`, `.agents/skills/forge/**`,
`.forge/adapters/*/installation.yml`) that previously fell through to
`ambiguous` (MR-017) — real, digest-tracked Adapter output the same PR
also needed to touch, blocking it a second, independent way. This part of
the design is unaffected by the Specification Drift above. Both fixes
together were subject to independent Strict Review, which found and
required correction of two implementation defects before first passing:
an unguarded manifest-state read that could crash the CLI (R001), and a
materiality prefix broader than this Change's own declared design (R002)
— see `review.md` for the full record across every iteration.

A related, more severe, and unrelated gap was found and deliberately
**not** fixed by this Change: MR-015 provides no protection at all, in
either direction, against a *completed* Change's actual implementation
changing outside its own `change_root` — a pre-existing limitation of
MR-015's `-- change_root` diff scope, independent of this Change.
Recorded explicitly (Discovery, Specification Out of Scope) rather than
left an implicit, false assumption; closing it is a materially larger,
separate undertaking left for a future Change.
