---
forge:
  artifact: architecture
  schema: 1
change: CHG-0046
status: complete
---

# Architecture — CHG-0046 Merge Readiness Post Review Artifact Scope

## Solution Summary

No new module or subsystem. Two localized, independent edits inside the
existing `src/forge_cli/merge_readiness/` package:

1. **`evaluator.py`'s MR-015 check** (`_check_change()`, currently
   `evaluator.py:132-146`): replace the fixed
   `{manifest.yml, provenance.yml, review.md}` allowed-set literal with a
   state-conditioned check — while `state.current != "complete"` at
   `head_revision`, behavior is unchanged (only the three-file literal is
   tolerated, exactly as today); once `state.current == "complete"`, any
   Change-local path (i.e. any path under
   `{change_root}/`) is tolerated, and only paths outside `change_root`
   remain subject to the existing ancestor/diff staleness check.
2. **`protocol/policies/merge-readiness.yml`**: add path rules for the ten
   Agent Adapter–generated paths Discovery identified, resolving each to
   `material` or `non_material`.

## Architectural Goals

- Make MR-015 agree with `forge validate`'s own already-shipped
  implementation of the identical C-026 invariant
  (`validation/__init__.py:375`) instead of contradicting it on the same
  repository state — one invariant, one behavior, checked in two places.
- Preserve, exactly, MR-015's existing behavior for every Change that has
  not yet reached `state.current: complete` — this Change changes *when*
  the check stops applying, not how it behaves before that point.
- Resolve the ten ambiguous Adapter-generated paths as data (policy
  configuration), not by adding a fifth special case to `classify_path()`'s
  control flow — the function's fail-closed structure (explicit rules,
  then an unconditional `ambiguous` fallback) is already the mechanism
  CHG-0046 needs; it is missing rules, not missing logic.
- Change nothing about how `state.current` reaches `complete` — MR-005 and
  MR-016 already gate that transition on independently-verifiable evidence
  existing at `head_revision`; this Change consumes that existing gate, it
  does not touch it.

## Design

### MR-015: state-conditioned allowed set

Current (`evaluator.py:132-146`, abbreviated):

```python
change_root = path.parent.relative_to(root).as_posix()
delta = subprocess.run(["git", "diff", "--name-only", subject_commit, head_revision, "--", change_root], ...)
allowed = {f"{change_root}/manifest.yml", f"{change_root}/provenance.yml", f"{change_root}/review.md"}
if delta.returncode != 0 or any(item and item not in allowed for item in delta.stdout.splitlines()):
    diagnostics.append(ReadinessDiagnostic("MR-015", "REVIEW SUBJECT STALE", ...))
```

Revised shape (the `git diff` scope, subject/ancestor checks, and
diagnostic wiring above and below this block are unchanged — only the
tolerance test changes):

```python
change_root = path.parent.relative_to(root).as_posix()
delta = subprocess.run(["git", "diff", "--name-only", subject_commit, head_revision, "--", change_root], ...)
is_complete = manifest.get("state", {}).get("current") == "complete"
allowed = {f"{change_root}/manifest.yml", f"{change_root}/provenance.yml", f"{change_root}/review.md"}
stale = delta.returncode != 0 or any(
    item and item not in allowed
    for item in delta.stdout.splitlines()
    if not (is_complete and item.startswith(f"{change_root}/"))
)
if stale:
    diagnostics.append(ReadinessDiagnostic("MR-015", "REVIEW SUBJECT STALE", ...))
```

`manifest` is already loaded and parsed earlier in `_check_change()` (used
for `review`, `state`, `artifacts`, `tdd`, `decisions` throughout the same
function) — no new read. The `-- change_root` pathspec on the `git diff`
already scopes this specific check's delta to the Change's own directory
(AC-002's outside-`change_root` protection is structural: this check
never sees paths outside `change_root` at all, and needs no new code for
AC-002 — it already only inspects `change_root`-scoped delta). `is_complete`
is evaluated fresh at `head_revision`'s manifest for every call, so a
Change that has *not yet* reached `complete` (AC-003) gets exactly today's
behavior — the temporal boundary is `state.current` at the commit under
evaluation, not some earlier or cached value.

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
as having no Flow stage or code representation at all. No stage-derived
allowed set can cover both without becoming, in effect, "anything in
`change_root`" — which is exactly the temporal-boundary design, arrived
at more directly.

**Deriving the allowed set from a real Git diff of `change_root` between
the frozen commit and a hypothetical "Completion commit," rather than
gating on `state.current`.** Rejected: there is no dedicated "Completion
commit" concept anywhere in this repository's Git history model — the
final commit satisfying MR-005/MR-016 is just whatever HEAD happens to be
when those checks pass, indistinguishable in Git terms from any other
commit. `state.current` is the only existing, already-load-bearing signal
for "this Change now considers itself finished," and MR-005/MR-016 already
corroborate it independently (Specification CON-002).

**Trusting `state.current` with no corroboration, i.e. relying on this
Change's edit alone without MR-005/MR-016's existing evidence
requirements.** Not applicable — MR-005 and MR-016 already exist and
already run in the same `_check_change()` pass; this Change adds no new
dependency, it relies on checks that are already unconditionally present
for every Change evaluated.

## Decisions

### DEC-001 — Temporal (`state.current`) boundary over per-stage artifact derivation for MR-015
Class: architectural · Materiality: material · Authority: agent_with_review
Owning artifact: architecture · Discovered in: specification (Specification
Review SR-001) · Resolved via: autonomous_decision

Selecting the `state.current == "complete"` boundary (mirroring `forge
validate`'s own precedent) over a per-Flow-stage artifact mapping is a
materially consequential choice about how a security/integrity-relevant
gate behaves — it changes what "the reviewed subject is protected" means
operationally (protected until Completion, not protected-per-artifact
forever). Resolved autonomously, consistent with SR-001/SR-002's findings
and `forge validate`'s existing, already-reviewed implementation of the
identical invariant; subject to this Change's own Strict Review like any
other Implementation decision.

## Risks

- **A Change could reach `state.current: complete` prematurely (mislabeled
  status, per [[project-merge-readiness-scoping-bug]] finding 6) and then
  edit Change-local files without MR-015 catching it.** Mitigated, not
  eliminated: MR-005/MR-016 require `verification.md`/`review.md`/
  `provenance.yml` to exist at `head_revision` before `complete` is
  accepted at all, and MR-006/MR-007/MR-012/MR-018/MR-021 independently
  cross-check that recorded Review/Verification evidence is internally
  consistent and provenance-backed — a Change cannot manufacture a
  corroborated `complete` state from nothing.
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
