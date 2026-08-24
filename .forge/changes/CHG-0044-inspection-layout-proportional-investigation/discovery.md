---
forge:
  artifact: discovery
  schema: 1
change: CHG-0044
status: complete
---

# Discovery — CHG-0044 Inspection Layout Proportional Investigation

## Executive Summary

Inspection is the last of `protocol/artifact-structure.md`'s fourteen
Artifact types not yet elaborated by the `CHG-0037`–`CHG-0043` series. It
already carries the *correct* normative content (§2.5 Proportionality,
directly quoting its own `CHG-0005`/`CHG-0012` precedent), so this Change
is not a correction the way `CHG-0043` partly was — it is a genuine
elaboration: adding an optional, recommended structural vocabulary and a
better scaffold, without touching the one property (proportionality) that
makes Inspection correct for FAST. One inaccuracy was found and must be
fixed while elaborating: the existing text calls `CHG-0005/inspection.md`
"a four-line file (title only)" — it is not title-only; it has two
sentences of real context.

## Investigation

### Protocol, Schema, Flow — unchanged

Protocol `2`; Change Schema `forge/change@2`; project default Flow
`standard` (`.forge/forge.yml`). Consistent with the entire
`CHG-0037`–`CHG-0043` series, all of which used `flow.initial: standard`,
`kind: feature`, regardless of the target Artifact's own Flow (FAST for
Inspection itself, FULL for Knowledge Capture) — the elaboration Change is
classified by its own semantic impact (canonical guidance + scaffold
code), not by which Flow the *target* Artifact belongs to.

### Where Inspection lives in the Flow model

`protocol/flows/fast.yml`: `inspection` stage `required: true` — the only
Flow where it exists. Neither `standard.yml` nor `full.yml` has an
`inspection` stage; those Flows have `discovery` + `specification` +
`plan` instead. `protocol/specification.md` §8 confirms textually: "FAST
minimum lifecycle: Intent, Inspection, Test Design when behavioral, TDD
Implementation when applicable, Verification, Strict Review, Documentation
Impact, Completion." No Contract rule (`protocol/contract/engineering.md`,
grepped in full) mentions Inspection by name — its only normative anchor
is this one Protocol §8 lifecycle line and `artifact-structure.md` §4
itself (guidance, not Contract, per C-067).

### Scaffold — real, behavioral, and currently redundant

`src/forge_cli/change_scaffolding.py`:
- `_STAGE_FILES["inspection"] = ("inspection.md", "inspection")` (line 20).
- `_markdown()`'s `sections` dict, `"inspection"` entry (line 135):
  `"## Inspection\n\nRecord the relevant inspection findings.\n"` — a
  single heading plus one generic sentence, no guidance on
  proportionality, symptom/cause separation, or Fix Boundary.
- `_frontmatter()` (lines 72-99) has no special case for `artifact ==
  "inspection"` — it falls through to the generic fallback
  `f"# {artifact.replace('_', ' ').title()} — {change_id} {title}"`
  (line 88), producing `# Inspection — CHG-XXXX <Title>`. This is the
  same pre-elaboration shape every other redesigned Artifact
  (`specification`, `test_design`, `tasks`, `verification`, `review`,
  `knowledge_capture`) explicitly moved away from, toward
  `# {change_id} · {Type}` (confirmed by reading each of their
  `_frontmatter` branches directly).
- The scaffold's own emitted body currently produces a real defect: a
  file whose title is `# Inspection — CHG-XXXX <Title>` followed
  immediately by a redundant `## Inspection` sub-heading restating the
  same word — no other Artifact scaffold does this.

This confirms the Change is properly BEHAVIORAL: a real renderer to
change (`_markdown`, `_frontmatter`), real tests to add — same shape as
`CHG-0037`–`CHG-0041`, not `CHG-0042`'s documentation-only shape.

### Gate and validator semantics — presence/status only, never content

`merge_readiness/evaluator.py:231` checks `"inspection"` only for
presence and status membership in `{"complete", "approved", "passed"}` —
confirmed identical mechanism already used for every other Artifact key
(`intent`, `discovery`, `specification`, …). No validator anywhere parses
`inspection.md` content or its headings (grep across
`src/forge_cli/validation/__init__.py` and `src/forge_cli/adapters/*.py`
for "inspection" returns only the scaffold and merge-readiness references
already covered above). This confirms §39 of the elaboration prompt (no
new semantic validation) is not a self-imposed restriction but already
the real, existing boundary — there is no content-aware Inspection
validator to avoid strengthening.

### Six real `inspection.md` examples — genuinely proportional, genuinely inconsistent headings

| Change | Lines | Headings used |
|---|---|---|
| `CHG-0005` | 5 (2 sentences, no frontmatter, no heading beyond title) | none |
| `CHG-0012` | 87 (frontmatter present) | Root cause, Precedent for the fix, Classification, Scope verified not to include, Correction after Strict Review Iteration 1... |
| `CHG-0024` | 57 | Root Cause, Existing Pattern, Evidence, Classification, Documentation Impact |
| `CHG-0026` | 62 | Finding, Flow Classification, Decision, Documentation Impact |
| `CHG-0028` | 44 | Current state, Flow classification, Parallel-work check, Process decision |
| `CHG-0029` | 50 | Evidence, Flow Classification, Recommendation, TDD Applicability |

Every example is genuinely proportional to its own fix — no padding, no
empty section, confirming §2.5's own framing is accurate in spirit. But no
two examples share a consistent heading vocabulary for the same concept:
"Classification" / "Flow Classification" / "Flow classification" all mean
the same FAST-eligibility judgment; "Root Cause" / "Root cause" / "Finding"
all mean the same confirmed-cause concept. This is the real, concrete gap
this Change closes: not a lack of structure, but a lack of a shared,
optional vocabulary for the structure authors already reach for
organically.

**Correction to existing guidance:** `artifact-structure.md`'s current
text calls `CHG-0005/inspection.md` "a four-line file (title only)". Its
real content is `# Inspection — CHG-0005` followed by two substantive
sentences of context (a real lifecycle gap and a stray misleading test
name) — not title-only. The file is five lines counting the blank
separator, closer to four non-blank lines, but it is not devoid of
content the way "title only" implies. This Change corrects the
description without changing the citation's point (it remains the
repository's real minimal-Inspection precedent).

### Distinction from adjacent artifacts

- **Discovery** (STANDARD/FULL only) is broad, pre-Specification
  understanding-building; Inspection (FAST only) is a narrow,
  fix-scoped investigation. The two never coexist in one Change — no
  Flow has both stages.
- **Specification** defines `FR-xxx` contract obligations for
  STANDARD/FULL; Inspection has no requirement-numbering convention and
  none of the six real examples invents one.
- **Plan** (STANDARD/FULL) records approved work; Inspection's optional
  `Fix Boundary` concept is narrower — it states what must *not* change,
  not a list of approved work items, and FAST has no separate `plan.md`
  at all.
- **Verification** records what was checked *after* the fix, with a
  Result-first (§2.3) convention; Inspection records what was found
  *before* it, with no such convention — presenting a fix as already
  verified inside `inspection.md` would misattribute Verification's own
  responsibility (§2.2).
- **Forge Experience Report** (`docs/experience-reporting.md`, opt-in,
  local, `dogfooding/reports/`) records what happened during execution of
  the work itself (tooling friction, unexpected behavior); Inspection
  records technical understanding of the defect being fixed. A `/investigate`
  command or equivalent does not exist anywhere in this repository (grep
  across `src/forge_cli`, `.claude/skills`, `protocol`, `docs` for
  "investigate" returns nothing) — there is no parallel semantics to
  reconcile.

### Flow escalation — already real, already independent of Inspection's shape

`fast.yml`'s `escalation.enabled: true` / `automatic_downgrade: false`,
together with `protocol/specification.md` §11 ("Escalation: FAST ->
STANDARD, STANDARD -> FULL, FAST -> FULL... Automatic downgrade is
forbidden") already provide the real mechanism for a FAST Change whose
Inspection reveals STANDARD/FULL-level complexity. Nothing in Inspection's
current or elaborated guidance needs to invent a new escalation path —
this Discovery confirms the existing mechanism is sufficient and only
needs to be named in the elaborated prose (per the originating prompt's
§17), not built.

### Harness Adapters

No reference to Inspection, its headings, or its scaffold body in
`src/forge_cli/adapters/*.py` (confirmed by grep across both `codex` and
`claude-code` adapter sources). Adapters project Flow/Contract/Protocol
content by reference (`artifact-structure.md` §5); they do not re-render
per-Artifact Markdown bodies. No Adapter impact.

### Tests

No existing test in `tests/unit/test_change_scaffolding.py` asserts on
`inspection` template content (confirmed by grep for
`test_render_scaffold.*inspection` and for the literal current string
"Record the relevant inspection findings" — both return nothing) — only
its presence in the FAST file set, via the existing parametrized
`test_render_scaffold_uses_only_the_selected_flow_stages`. Changing the
scaffold body and heading is safe with respect to every currently passing
test.

## Compatibility Finding

No retroactive impact: none of the six real `inspection.md` files are
rewritten; no Protocol integer, Change Schema, Flow stage list, gate
requirement, or `forge validate`/merge-readiness semantics change. The
scaffold change only affects `inspection.md` files created after this
Change ships.
