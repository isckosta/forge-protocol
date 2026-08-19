# Architecture — Interaction Language Resolution

## Solution Summary

Reuse the exact generic projection pipeline `CHG-0016` established:
`AdapterProjectionContext` (Harness-independent) → `CodexProjectionInput`
(Codex-specific) → `generate_codex_skill_bundle`. Add one additive-default
field, `interaction_language: str = ""`, at each layer. `service.py`
populates it from the already-loaded, schema-validated project
configuration dict at both existing `AdapterProjectionContext(...)`
construction sites. Unlike `CHG-0016`'s `artifact_structure_content`
(a whole static document, projected as a separate `references/*.md`
resource), this value is a single small, project-specific datum — so it
is rendered as one interpolated instruction line directly inside
`SKILL.md`'s existing instruction body, never a new resource file.

## Architectural Goals

1. No new concept enters the generic Adapter Core
   (`AdapterProjectionContext`) beyond a plain string field, matching
   NFR-002.
2. Zero new plumbing for Contract enforcement: C-070–C-073 reach a Codex
   session automatically the moment they exist, because
   `references/engineering-contract.md` already projects the entire
   effective Contract text verbatim (`contract_content`, unchanged by
   this Change).
3. The degenerate case (`auto`, or no configuration at all) and the
   explicit case are both always-present, differently-worded output —
   not an "included/omitted" branch. This avoids the one accepted rough
   edge `CHG-0016` left behind (Strict Review R010 there: the
   omit-branch its own field enabled was, in fact, unreachable from any
   shipped production path, because both call sites resolve the
   canonical file unconditionally). This Change has no equivalent
   unreachable branch to begin with, because there is no "absent" case —
   `auto` is always a valid, meaningful value.

## DEC-002 — Interpolated line vs. new reference-file resource

**Class**: `architectural`. **Authority**: `agent_with_review` (default
for `architectural` per `protocol/policies/decision.yml`).

**Question**: Should `interaction_language` be projected as a new
`references/interaction-language.md` resource file (mirroring
`artifact_structure_content` exactly), or as one interpolated line inside
the existing `SKILL.md`?

**Alternatives**:

- **A — Interpolated `SKILL.md` line (selected)**: no new resource file;
  `_skill_content(...)` gains one more parameter and renders one more
  line. Proportional to the content size (a handful of words), keeps the
  file count from growing for a per-project scalar value, and avoids
  inventing an "omitted when empty" branch this field will never actually
  need (the value is always meaningful — `auto` is not absence).
- **B — New `references/interaction-language.md` resource**: structurally
  identical to `artifact_structure_content`'s pattern. Rejected: the
  content would be one sentence in an otherwise-empty file, which is the
  kind of disproportionate structure `protocol/artifact-structure.md`'s
  own Proportionality principle (introduced by `CHG-0016` itself) argues
  against, and it would resurrect exactly the "always non-empty, so the
  omitted branch is dead code" shape Strict Review flagged as an
  OBSERVATION on `CHG-0016` (R010).

**Resolution**: Alternative A. **Resolved via**: `autonomous_decision`.
Recommendation confidence: high (the size/proportionality argument is
decisive and Strict Review will independently verify both the rendered
`SKILL.md` output and that no dead branch was introduced).

## Content Shape (design, not production text)

`_skill_content(...)` (`src/forge_cli/adapters/codex/projection.py`)
gains an `interaction_language: str` parameter. Rendering logic:

```text
effective = interaction_language or "auto"
if effective == "auto":
    line = (
        "Interaction language: auto -- use the active chat's observed "
        "language if there is one, otherwise English (C-070-C-073)."
    )
else:
    line = (
        f"Interaction language: {effective} (project configuration "
        "takes precedence -- C-072)."
    )
```

Rendered as one line in the existing instruction body (near the other
per-project directives already interpolated there, e.g. the Flow list) —
not a new heading, not a new `references/` link.

## Contract and Specification Placement

`C-070`–`C-073` appended to `protocol/contract/engineering.md` (wrapped
prose, matching the file's existing convention) and to
`protocol/versions/2/contract/engineering.md` (single-line-per-rule,
matching that file's existing convention) — verified byte-identical
content modulo wrapping against the C-067–C-069 precedent during
Specification Review (SR-002). `protocol/specification.md` §42 placed
after §41, matching sequential numbering; it is not added to
`protocol/versions/2/specification.md`, which is scoped exclusively to
Protocol-2-specific review/provenance semantics (confirmed in Discovery)
and has no equivalent placement for §41 either.

## Adapter/Harness Integration

- `src/forge_cli/adapters/driver.py`: `AdapterProjectionContext` gains
  `interaction_language: str = ""`.
- `src/forge_cli/adapters/codex/projection.py`: `CodexProjectionInput`
  gains the same field; `generate_codex_projection_bundle` passes it to
  `generate_codex_skill_bundle`, which passes it to `_skill_content`.
- `src/forge_cli/adapters/codex/driver.py`: `CodexDriver.project` already
  passes every `AdapterProjectionContext` field through to
  `generate_codex_skill_bundle` positionally/by keyword (the same call
  site that already forwards `artifact_structure_content`) — gains the
  new keyword, no structural change.
- `src/forge_cli/adapters/service.py`: both existing
  `AdapterProjectionContext(...)` construction sites (conformance/doctor
  path, `_prepare`/publish path) gain
  `interaction_language=configuration.get("interaction", {}).get("language", "auto")`.
  `configuration` (the schema-validated project dict) is already in local
  scope at both sites — no new loading code, no new failure mode.
- `validate_conformance` (`src/forge_cli/adapters/validation.py`):
  unchanged. It diffs stage/gate/invariant *names* and two booleans; a
  purely informational `SKILL.md` line is invisible to it, matching
  `CHG-0016`'s own reasoning for leaving it alone.

## Compatibility

Purely additive at every layer (schema, dataclasses, generated output).
No Protocol version bump. No existing `.forge/forge.yml`, test, or
historical Change's `forge validate`/`forge doctor` result changes.

## Risks

- **A future second Harness Adapter must reuse
  `interaction_language`, not reinvent a parallel field.** Mitigated by
  keeping the field on the generic `AdapterProjectionContext`, not on
  `CodexProjectionInput` alone (NFR-002 already requires this).
- **A translation feature, if ever built, could be tempted to also
  translate schema keys or IDs.** Mitigated by C-070 existing now, before
  any translation mechanism exists, so the invariant is in place ahead of
  the risk rather than retrofitted after an incident (the same
  "invariant before the mechanism that could violate it" pattern
  `CHG-0015`'s Contract additions used for delegated-Execution authority).

## What This Change Deliberately Does Not Build

- Any actual translation of Forge-generated prose (there is no
  translation engine in this Change — only an instruction for the
  Harness to interact in a given language).
- Repository/context-language heuristic detection (DEC-001, deferred).
- Any `forge validate` check for C-070–C-073 (SR-001; both are
  Harness/Adapter honesty and precedence obligations, not mechanically
  checkable Gate conditions).
- Any change to `validate_conformance`, `adapter.yml` capability
  declarations, or the Adapter installation/drift/ownership machinery.
