---
forge:
  artifact: architecture
  schema: 1
change: CHG-0021
status: complete
---

# Architecture — Adapter Reference Schema Projection

## Solution Summary

A new pure function, `render_decision_rules_reference()`, renders
Markdown directly from the Decision structural-rule constants already
in `src/forge_cli/validation/__init__.py`. Both Adapters thread its
output through the exact `AdapterProjectionContext` pattern `CHG-0016`
established for `artifact_structure_content`: resolved once in
`adapters/service.py`, carried through each Driver, and conditionally
included as `references/decision-rules.md` (Codex) /
`skills/forge/references/decision-rules.md` (Claude Code), with a
matching conditional reference link. `forge validate`'s `resolved_via`
error message is sharpened to state the expected values.

## Architectural Goals

- one Python source of truth for every Decision structural rule this
  Change documents — no second, hand-maintained copy;
- reuse `CHG-0016`'s already-shipped wiring pattern exactly, introducing
  no new projection concept;
- no new import cycle;
- byte-identical rendered content across both Adapters.

## DEC-001 — Where does the renderer live: `protocol_resolution` or `validation`?

- **Class:** architectural
- **Materiality:** material
- **Authority:** agent_with_review
- **Owning Artifact:** architecture
- **Status:** resolved

**Question:** `protocol_resolution/__init__.py` already holds every other
`resolve_effective_*` function used to build Adapter projection input
(`resolve_effective_contract`, `resolve_effective_flow`,
`resolve_effective_artifact_structure`) — naming and precedent both point
there. But the content this Change renders is not a file `protocol_resolution`
resolves; it is Python data that already lives in `validation/__init__.py`.

**Evidence:** `validation/__init__.py:10` imports from
`forge_cli.protocol_resolution`
(`discovery.md` "A real constraint: import direction"; confirmed
independently in `specification-review.md`'s "Checked and found sound").
`protocol_resolution/__init__.py` imports nothing from `forge_cli.validation`.
A renderer placed in `protocol_resolution` that imports `_DEC_*` from
`validation` would create `validation → protocol_resolution → validation`
— an import cycle Python cannot resolve at module-load time.

**Decision:** place `render_decision_rules_reference() -> str` in
`src/forge_cli/validation/__init__.py`, exported alongside the constants
it documents. `adapters/service.py` imports it directly from
`forge_cli.validation` — a new one-directional edge
(`adapters → validation`), not a new architectural layer:
`adapters/service.py` already imports `resolve_effective_artifact_structure`
from `protocol_resolution`, so this adds a second, symmetrical import
from a sibling low-level module, not a new dependency shape.

**Resolution path:** `autonomous_decision` — `architectural` class
carries `agent_with_review` default authority
(`protocol/policies/decision.yml`), and this is a mechanical consequence
of the existing import graph (Discovery already found the constraint;
there is no second reasonable placement given it), not a preference
call.

**Confidence:** high.

## Resource naming and placement

`decision-rules.md`, matching `artifact-structure.md`'s existing
kebab-case, singular-concept naming. Claude Code:
`skills/forge/references/decision-rules.md`. Codex:
`references/decision-rules.md`. Both under each Adapter's existing
`references/` convention — no new top-level directory.

## Content shape

The rendered Markdown opens with one sentence stating plainly that it is
generated from `forge validate`'s own enforcement code, not hand-
maintained prose — the same honest-mechanism disclosure `CHG-0018`
already established for the illustrative `PreToolUse` hook (Contract
C-073). It then documents, from the named constants only:

- `_DEC_CLASSES`, `_DEC_MATERIALITY`, `_DEC_STATUSES`, `_DEC_AUTHORITIES`,
  `_DEC_RESOLVED_VIA` — the flat enum for each `decisions[]` field;
- `_DEC_OWNING_BY_CLASS` — which `owning_artifact` values are valid for
  each `class`;
- `_DEC_AUTHORITY_FLOOR` — which `class` values have a non-negotiable
  minimum `authority`.

## Wiring (mirrors `CHG-0016` exactly)

1. `adapters/driver.py` — add `decision_rules_content: str = ""` to
   `AdapterProjectionContext`, alongside `artifact_structure_content`.
2. `adapters/service.py` — at both existing construction sites (the same
   two call sites currently computing `artifact_structure_content=
   resolve_effective_artifact_structure(...)`), add
   `decision_rules_content=render_decision_rules_reference()`. No
   `protocol_root` or versioned-root argument is needed — unlike
   `resolve_effective_artifact_structure`, this function reads only
   in-process constants.
3. `adapters/claude_code/driver.py` and `adapters/codex/driver.py` — pass
   `context.decision_rules_content` into each Adapter's projection input
   construction, alongside `context.artifact_structure_content`.
4. `adapters/claude_code/projection.py` and `adapters/codex/projection.py`
   — add a `decision_rules_content: str = ""` field to each projection-
   input dataclass; `has_decision_rules = bool(decision_rules_content)`
   gates both the resource and its reference link, exactly mirroring
   `has_artifact_structure`.

## Error message change

`validation/__init__.py`, `_validate_unresolved_decisions`'s
`resolved_via` check: append
`f" (expected one of {sorted(_DEC_RESOLVED_VIA)}, or omit while unresolved)"`
to the existing message, matching the `owning_artifact` message's
parenthetical convention at the same function.

## What This Change Deliberately Does Not Build

- No promotion of `_DEC_OWNING_BY_CLASS`/`_DEC_AUTHORITY_FLOOR` into
  `protocol/schemas/change-v2.schema.json` (`discovery.md` Candidate A;
  CON-001).
- No sweep of the `class`/`materiality`/`status`/`authority` invalid-
  value messages for the same "expected one of" treatment — only
  `resolved_via`, per Intent's Out of Scope.
- No `forge change new` scaffolding.

## Risks

`render_decision_rules_reference()` explicitly names each of the seven
constants it documents rather than introspecting every module-level
`_DEC_*` name generically (deliberately, to avoid accidentally exposing
an unrelated future internal constant). This means NFR-001's guarantee
is narrower than it might sound: *these seven constants cannot drift
from what the reference renders*, not *every future Decision-rule
constant is automatically documented*. A future Change that adds an
entirely new `_DEC_*` category will need to update the renderer
explicitly — disclosed here rather than overclaimed.
