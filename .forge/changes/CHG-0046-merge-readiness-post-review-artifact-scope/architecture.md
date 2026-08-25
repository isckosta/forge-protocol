---
forge:
  artifact: architecture
  schema: 1
change: CHG-0046
status: complete
---

# Architecture — CHG-0046 Merge Readiness Post Review Artifact Scope

## Solution Summary

**Revised by Specification Drift** (`specification-drift.md`) after an
external, independent reviewer (Codex, PR #37) found the originally
selected design (below, DEC-001, now superseded) directly contradicted
`protocol/versions/2/specification.md` §5's literal text. No new module
or subsystem, still. Two localized, independent edits inside the existing
`src/forge_cli/merge_readiness/` package:

1. **`evaluator.py`'s MR-015 check** (`_check_change()`): the allowed set
   remains exactly the Protocol's literal
   `{manifest.yml, provenance.yml, review.md}` for tolerance *without*
   renewing subject provenance. Any other `change_root` path differing
   from the frozen subject is tolerated *only* when covered by the
   `scope` of an explicit, anchored `role: implementation`/`resolution`
   provenance record whose commit is an ancestor of (or equal to)
   `head_revision` — never by reading `manifest.state` at all.
2. **`protocol/policies/merge-readiness.yml`**: add path rules for the ten
   Agent Adapter–generated paths Discovery identified, resolving each to
   `material` or `non_material`. Unaffected by the Specification Drift.

## Architectural Goals

- Conform to Protocol 2 `specification.md` §5's literal text — the only
  unconditional post-freeze exception is the three named files; every
  other tolerance must be an explicit, individually anchored, auditable
  provenance record, never an implicit manifest-state flag (§14: "A
  manifest claim... is not sufficient authorization").
- Preserve, exactly, MR-015's existing behavior for any delta not covered
  by an anchored renewal record's declared `scope` — this Change adds a
  narrow, explicit escape hatch; it does not loosen the default.
- Resolve the ten ambiguous Adapter-generated paths as data (policy
  configuration), not by adding a fifth special case to `classify_path()`'s
  control flow — the function's fail-closed structure (explicit rules,
  then an unconditional `ambiguous` fallback) is already the mechanism
  CHG-0046 needs; it is missing rules, not missing logic.
- Reuse, not duplicate, the anchoring mechanism MR-021 already implements
  for subject records (`_first_committed_record`) — a renewal record's
  own immutability is checked the same way, not by a second, parallel
  anchoring implementation.

## Design

### MR-015: explicit, anchored, scoped renewal records

The `git diff` scope, ancestor check, and diagnostic wiring already in
`_check_change()` are unchanged. Only the tolerance test for uncovered
paths changes — from a literal three-file allowlist with no escape hatch,
to the same allowlist plus a per-path lookup against anchored renewal
records:

```python
allowed = {f"{change_root}/manifest.yml", f"{change_root}/provenance.yml", f"{change_root}/review.md"}
uncovered_paths = [item for item in delta.stdout.splitlines() if item and item not in allowed]
if delta.returncode != 0:
    diagnostics.append(ReadinessDiagnostic("MR-015", ...))
elif uncovered_paths:
    renewed_scope: set[str] = set()
    for item in records:
        if not (isinstance(item, dict) and item.get("role") in {"implementation", "resolution"}):
            continue
        renewal_commit = item.get("revision", {}).get("commit") or item.get("revision", {}).get("immutable_ref", {}).get("value")
        if not isinstance(renewal_commit, str) or len(renewal_commit) != 40:
            continue
        # Upper bound: the renewal must not postdate head_revision.
        if subprocess.run(["git", "merge-base", "--is-ancestor", renewal_commit, head_revision], ...).returncode != 0:
            continue
        # Lower bound (Review R005, Iteration 4, BLOCKER): the renewal must
        # postdate THIS evaluation's own subject_commit -- otherwise a
        # renewal anchored during an earlier freeze cycle would silently
        # cover tampering introduced after a later one, forever.
        if subprocess.run(["git", "merge-base", "--is-ancestor", subject_commit, renewal_commit], ...).returncode != 0:
            continue
        scope = item.get("scope")
        if not (isinstance(scope, list) and scope):
            continue
        anchored_renewal = _first_committed_record(root, provenance_relative, item.get("id", ""))
        if anchored_renewal is not None and anchored_renewal == item:
            renewed_scope.update(p for p in scope if isinstance(p, str))
    if any(item not in renewed_scope for item in uncovered_paths):
        diagnostics.append(ReadinessDiagnostic("MR-015", ...))
```

`records`/`record_index` are already loaded earlier in `_check_change()`
for the subject/reviewer lookup — no new read. `_first_committed_record`
is the exact function MR-021 already uses to anchor subject records;
reused verbatim, not reimplemented, for renewal records (Architectural
Goals). A renewal record's tolerance is scoped per-path (`scope`, mirroring
§11's existing `resolution` shape) — a record covering `knowledge-capture.md`
does not blanket-authorize an unrelated `specification.md` rewrite
committed alongside it (AC-007). Both bounds are required (AC-008): the
original implementation only checked the upper bound, which Review
Iteration 4 (R005) found let a stale, earlier-cycle renewal keep covering
every later freeze indefinitely. `manifest.state` is not read anywhere in
this block.

### MR-017: additive policy rules, no code change

`protocol/policies/merge-readiness.yml` gains a fourth prefix category
(or extends `material_prefixes`/adds a new `non_material_prefixes` list —
Tasks decides the exact key name against `policy.py:29-43`'s existing
`if/elif` chain, which already has a natural slot for one more prefix
list before the final `ambiguous` fallback). Resolution per path family,
consistent with what each family actually is:

- `.claude/skills/forge/**`, `.agents/skills/forge/**`,
  `.forge/adapters/*/installation.yml`: **material.** These are the
  Adapter's projected, digest-tracked normative surface — exactly the
  kind of generated-but-consequential output `material_prefixes` already
  covers for other generated artifacts (`protocol/` itself is generated
  into Adapter output, and is already `material`). A PR that changes what
  an installed Adapter tells an agent to do is a real, reviewable change.
- `.claude/CLAUDE.md`: **material**, for the same reason — it is the
  Adapter-generated pointer file CHG-0045's own Discovery documents
  (`_claude_md_pointer()`), not hand-authored prose.

No path in the ten is reclassified `non_material` — Discovery found no
path in the set that is inert/decorative; all ten are Adapter-projected
governance surface. `non_material` is named in FR-002 as an available
outcome for generality (Tasks may find a path where it applies), not
because any of the ten specific paths needs it.

## Alternatives Considered

**Per-Flow-stage artifact mapping (Specification's original FR-001
design).** Rejected by Specification Review (SR-001): `tasks.md` is a
continuously-updated checklist not attributable to one stage, and
`specification-drift.md` is documented (`protocol/artifact-structure.md:436-441`)
as having no Flow stage or code representation at all.

**A `state.current`-keyed temporal boundary (DEC-001, this Architecture's
own first design).** Selected by SR-001/SR-002, shipped, passed three
internal independent Strict Review iterations, then rejected after
external review (Codex, PR #37) found it directly contradicts Protocol §5
and §14's literal text — see `specification-drift.md`. Superseded by the
explicit-anchored-renewal-record design above (DEC-003). Kept here, not
deleted, as the record of what was tried and why it failed: the design
mirrored `forge validate`'s own pre-existing `state.current != "complete"`
carve-out for the identical invariant, which is itself now suspected of
the same non-conformance — a separate, pre-existing question this Change
does not resolve, flagged as follow-up work.

**Requiring the renewal record's commit to equal `head_revision` exactly,
rather than merely be its ancestor.** Rejected during implementation: the
established two-commit freeze convention this repository already uses
throughout (commit the substantive change, then commit `provenance.yml`
recording it as a second commit) means the commit where a renewal's
`scope` actually applies is typically the *parent* of `head_revision`, not
`head_revision` itself. An ancestor check accommodates that convention
without requiring a third, artificial "squash" commit merely to make the
renewal's commit and `head_revision` coincide.

**Trusting `state.current` with no corroboration.** Rejected outright, not
merely narrowed (Specification Drift) — `state.current` is not read by
the corrected design at all, so the question of whether it would have
been sufficiently corroborated by MR-005/MR-016 (Specification's original
CON-002) no longer applies.

## Decisions

### DEC-001 — Temporal (`state.current`) boundary over per-stage artifact derivation for MR-015
Class: architectural · Materiality: material · Authority: agent_with_review
Owning artifact: architecture · Discovered in: specification (Specification
Review SR-001) · Status: **superseded by DEC-003** (Specification Drift,
after Codex's PR #37 finding) · Resolved via: autonomous_decision

Selecting the `state.current == "complete"` boundary (mirroring `forge
validate`'s own precedent) over a per-Flow-stage artifact mapping is a
materially consequential choice about how a security/integrity-relevant
gate behaves. Resolved autonomously, consistent with SR-001/SR-002's
findings and `forge validate`'s existing, already-reviewed implementation
of the identical invariant; passed three internal independent Strict
Review iterations before an external reviewer found it directly
contradicts Protocol §5/§14's literal text. Kept as the historical record
of a decision made, shipped, reviewed, and later found wrong by evidence
none of the three internal Reviews happened to check (cross-referencing
the actual Protocol specification text against the diff) — not deleted,
per this repository's own append-only provenance discipline applied to
Architecture's own record-keeping.

### DEC-003 — Explicit, anchored, per-path-scoped renewal records over a manifest-state flag for MR-015
Class: architectural · Materiality: material · Authority: agent_with_review
Owning artifact: architecture · Discovered in: specification (Specification
Drift, Codex PR #37 finding) · Resolved via: autonomous_decision

Supersedes DEC-001. Selects the design in this Architecture's own
"Design" section: tolerance for a `change_root` path outside the
Protocol's literal three-file exception requires an explicit, anchored,
scoped provenance record — never a `manifest.state` read. This is not a
narrower version of DEC-001; it is a different mechanism entirely
(per-commit, per-path, auditable, immutable-once-anchored, matching
Protocol §5/§11's own vocabulary) chosen specifically because DEC-001's
mechanism (a single mutable flag governing every future commit once set)
is exactly what Protocol §5 names and forbids ("MUST NOT be inferred
from... membership in the Change directory generally") and what §14 names
as insufficient authorization on its own. Subject to this Change's own
fresh, independent Strict Review — the prior three Iterations reviewed
DEC-001's design, not this one.

## Risks

- **A renewal record's tolerance is granted on self-attested existence
  (`assurance: recorded`), the same bar every other subject/verification
  record in this Protocol already uses — it is not independent proof the
  *content* of whatever changed is itself correct.** Not eliminated, and
  not a new risk this Change introduces: matches how `implementation-
  subject-001`/`verification-001`-shaped records already work everywhere
  else in this Protocol (§4: `recorded` is "the minimum for
  review_passed"). Mitigated relative to DEC-001's rejected design by
  being explicit, per-path-scoped, and immutably anchored once committed
  — an auditable act per renewal, not a single mutable flag silently
  covering every future commit.
- **This Change does not close, and could be mistaken for closing, the
  separate and more severe pre-existing gap that MR-015 provides no
  protection at all — today, independent of this Change, in either
  direction — against a completed Change's implementation changing
  outside its own `change_root`** (Discovery; confirmed by direct
  reproduction). Not mitigated by this Change; recorded explicitly in
  Specification's Out of Scope rather than left implicit, precisely so it
  is not read as resolved by AC-002's narrower, corrected guarantee.
- **The additive `merge-readiness.yml` policy change could be read as
  loosening materiality classification generally.** Mitigated: FR-002/AC-005
  requires the fallback to stay `ambiguous` for every other path; only ten
  named paths move, and all ten move to `material` (the stricter outcome),
  not `non_material`.
