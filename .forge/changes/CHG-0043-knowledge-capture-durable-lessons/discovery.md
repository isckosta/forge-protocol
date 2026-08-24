---
forge:
  artifact: discovery
  schema: 1
change: CHG-0043
status: complete
---

# Discovery — CHG-0043 Knowledge Capture Durable Lessons

## Executive Summary

Unlike Specification Drift (`CHG-0042`, no scaffold at all), Knowledge
Capture has a real, working scaffold entry — but it exists only for
Flow FULL, is required there, and gates Completion
(`required_knowledge_capture_complete`). 25 real examples show two
legitimate, real structural modes: short prose per section for a
single dominant lesson, and a flat bullet list of independent lessons
when several exist (`CHG-0016`, the origin Change itself, is the
richest real precedent for the latter). Prior guidance explicitly
recommended "no material change" — this Discovery evaluates whether
that still holds and where elaboration is genuinely warranted without
overriding that judgment lightly.

## Investigation

### Protocol, Schema, Flow

Unchanged since `CHG-0042`: Protocol `2`; Change Schema
`forge/change@2`; project default Flow `standard`.
`protocol/specification.md`'s §? minimum-lifecycle list (line 55)
names "Knowledge Capture" as part of the FULL Flow's minimum
lifecycle, confirming it is FULL-only, not conditional the way the
prompt's framing suggested — `protocol/flows/full.yml` lists it as
`required: true` (not `required_when:`), and neither `fast.yml` nor
`standard.yml` has any `knowledge_capture` stage at all.

### Scaffold — real and behavioral

`src/forge_cli/change_scaffolding.py`:
- `_STAGE_FILES["knowledge_capture"] = ("knowledge-capture.md", "knowledge_capture")`.
- `_markdown()`'s `sections` dict, `"knowledge_capture"` entry (line
  345): `"## What Changed\n\nRecord the durable change.\n\n## Durable
  Knowledge\n\n## Consequences for Future Changes\n\n## References\n\n"`
  — a bare 4-heading skeleton, no guidance prose inside any section.
- `_frontmatter()` has no special-case heading for `artifact ==
  "knowledge_capture"` — it falls through to the generic
  `f"# {artifact.replace('_', ' ').title()} — {change_id} {title}"`
  form (`# Knowledge Capture — CHG-XXXX <Title>`), the same
  pre-`CHG-0037` pattern every other redesigned Artifact this session
  already moved away from.

This confirms the Change is properly BEHAVIORAL (a real renderer to
change, real tests to add) — same shape as `CHG-0037`–`41`, not
`CHG-0042`'s documentation-only shape.

### Gate semantics

`protocol/flows/full.yml`: `knowledge_capture` stage `required: true`;
`before_completion.require` includes `required_knowledge_capture_complete`.
`merge_readiness/evaluator.py`'s `_check_change` (confirmed during
`CHG-0041`'s own Discovery this session) checks this exact requirement
key against `artifacts.get("knowledge_capture") not in {"complete",
"approved", "passed"}` — a presence/status check only, never content
inspection. No validator anywhere parses `knowledge-capture.md`
content (grep across `src/forge_cli/validation/__init__.py` and
`src/forge_cli/adapters/*.py` for "knowledge" returns nothing) —
consistent with C-067.

### 25 real examples — two legitimate real structural modes

- **Short prose per section** (`CHG-0033`, `CHG-0035`, `CHG-0036`, and
  most others): one to three sentences under each of the four
  headings, no sub-items, no IDs. This is the dominant real pattern
  for a Change with one primary durable lesson.
- **Flat bullet list of independent lessons** (`CHG-0016`, seven
  distinct bolded-title-plus-explanation items with no structural
  headings at all — no `## What Changed`, straight into the list).
  This is real precedent for the multi-lesson case the prompt's
  `### K-001 · <title>` proposal targets, though `CHG-0016` uses no
  formal ID, no `#### Observation`/`Why It Matters`/`Scope`/`Guidance`
  subheadings — just a bold title sentence followed by prose. No other
  Change reaches this density; this remains the sole real example.

No `K-xxx` id has ever been used anywhere in this repository's
`knowledge-capture.md` history (confirmed by grep across all 25
files) — introducing it as a formal, mandatory namespace would have no
real precedent and no known consumer (§36 of the originating
guidance). It is adopted here strictly as *optional* structure,
consistent with `CHG-0016`'s own real bullet-list precedent, not
mandated.

### Distinction from adjacent artifacts (mostly already understood this session, extended here)

- **Decision** (`manifest.yml: decisions[]`, `DEC-xxx`) answers "which
  option was chosen." Knowledge Capture answers "what should be
  remembered afterward." A Decision can motivate a Knowledge Capture
  entry (the consequence of having chosen it), but the entry is not a
  restatement of the Decision record.
- **Architecture** (`architecture.md`, `## DEC-xxx` embedded records,
  confirmed real convention this session's earlier Discoveries)
  records the *design*. Knowledge Capture may record a durable
  *consequence* of that design that future Changes must respect — not
  a copy of the design itself.
- **Specification** defines the Change's own obligation (`FR-xxx`).
  Knowledge Capture is not a reworded Requirement; it exists only when
  a broader, reusable conclusion follows from having implemented it.
- **Review** (`review.md`, `Rxxx` findings, redesigned `CHG-0041` this
  session) records problems found in the reviewed subject. A finding
  may *reveal* a durable lesson (`CHG-0016`'s own real example: a
  Reviewer catching a specified-but-never-executed Non-mechanical
  Validation item became a general lesson about specification vs.
  execution) — Knowledge Capture preserves the generalized lesson, not
  the finding transcript.
- **Specification Drift** (`specification-drift.md`, redesigned
  `CHG-0042` this session) records *how* a contract had to change.
  Knowledge Capture may record what should be *remembered* from that
  change having been necessary — a distinct downstream artifact, not a
  duplicate.
- **Forge Experience Report (FER)** — a real, active, distinct
  mechanism (`docs/experience-reporting.md`; `dogfooding/reports/FER-####.{yml,md}`;
  `src/forge_cli/experience/`). FER is opt-in, local-first, records
  *what happened during a real execution* (expected/observed/evidence/
  impact/workaround/follow_up), explicitly "not telemetry, logging,
  Strict Review, a bug tracker, a Change, Protocol state, a
  Requirement, or a Gate" (`docs/experience-reporting.md` verbatim).
  It lives in a wholly separate location
  (`dogfooding/reports/`, not `.forge/changes/<CHG>/`) and is not tied
  to a single Change. Knowledge Capture is Change-scoped, always
  present when the Flow requires it (not opt-in), and records
  distilled, durable *knowledge*, not raw observation records. No
  existing `knowledge-capture.md` references FER or vice versa — this
  relationship has never been documented before.

### Promotion to permanent documentation — no real mechanical precedent; a real but different relationship exists

No `knowledge-capture.md` uses a "Promoted to:" marker or any
equivalent (grep across all 25 files for "Promoted to" returns
nothing). The real relationship is different from what the prompt's
"Knowledge Lifecycle" framing suggests: Contract `F-008` ("Public
architectural decisions" — confirmed present in
`.forge/contract/engineering.md`, the project's materialized effective
Contract, and cited already by `protocol/artifact-structure.md`'s own
"Architecture" entry) already requires that *materially* architectural
work produce a `docs/adr/NNNN-slug.md` ADR directly, as part of
Architecture — not as a later "promotion" derived from Knowledge
Capture. Real References sections already point to these
(`CHG-0013`, `CHG-0015`, `CHG-0016` all reference `docs/adr/00NN-...`;
`CHG-0036` references `docs/rfcs/0006-merge-readiness-gate.md`). The
correct guidance is therefore: reference the ADR/RFC that F-008 already
produced, when one exists, rather than inventing a new post-hoc
promotion workflow with no real precedent or mechanism.

### Empty Knowledge Capture

No real example says "no knowledge to record" the way
`CHG-0013/specification-drift.md` did for Drift — all 25 examples have
substantive content, consistent with FULL Flow being reserved for
"high-impact work" (`full.yml`'s own description) where durable
learning is more likely. Still, nothing in Protocol or the gate
definition requires fabricated content — `required_knowledge_capture_complete`
checks `artifacts.knowledge_capture` status, not content richness. The
guidance should state explicitly that a short, honest "no additional
knowledge beyond this Change was identified" is a valid, complete
answer, matching the pattern already established for `## Checked and
found sound` sections and Specification Drift's own real "No Drift to
record" precedent (`CHG-0013`) — proportionality (§2.5), not padding.

### Harness Adapters

No reference to Knowledge Capture, "What Changed," "Durable
Knowledge," or any related heading in `src/forge_cli/adapters/*.py`
(confirmed by grep). No Adapter impact.

### Tests

No existing test in `tests/unit/test_change_scaffolding.py` asserts on
`knowledge_capture` template content (confirmed by grep for
`test_render_scaffold_knowledge`) — only its presence in the FULL-flow
file set, via the existing parametrized
`test_render_scaffold_uses_only_the_selected_flow_stages`.

## Compatibility Finding

Nenhum impacto retroativo: os 25 `knowledge-capture.md` reais não são
reescritos; nenhuma mudança de Protocol integer, Change Schema,
Decision/Architecture/Specification/Review/Specification-Drift/FER
semantics, ou `forge validate` semantics.
