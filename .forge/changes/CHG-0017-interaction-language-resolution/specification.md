# Specification — Interaction Language Resolution

## Summary

Add an optional, additive `interaction.language` field to `forge/project@1`;
four new binding Contract rules (`C-070`–`C-073`) governing what interaction
language may and may not affect; a new `protocol/specification.md` §42
defining a three-level precedence chain (explicit configuration →
Harness-observed chat hint → English fallback); and Codex Adapter
projection support surfacing the effective instruction to a Codex session
via one interpolated `SKILL.md` line, reusing the existing generic
`AdapterProjectionContext` → `CodexProjectionInput` pipeline with no new
Codex-specific concept.

## Classification

**Flow: FULL.** Touches a Protocol schema, the Contract (binding rules,
both `protocol/contract/engineering.md` and
`protocol/versions/2/contract/engineering.md`), the Specification, and
executable Adapter code with new tests — the same combination that
classified `CHG-0013`, `CHG-0015`, and `CHG-0016` as FULL. See
`discovery.md` "Flow Classification Finding."

## Functional Requirements

### FR-001 — `interaction.language` schema field

`protocol/schemas/project.schema.json` gains an optional `interaction`
object with a `language` string property, pattern
`^(auto|[a-z]{2,3}(-[A-Z]{2})?)$` (the sentinel `auto`, or a
BCP-47-shaped lowercase-language[-REGION] code — no enumerated language
allowlist). Absent `interaction` is valid and behaves identically to
`interaction: {language: auto}`.

### FR-002 — Contract rules C-070–C-073

`protocol/contract/engineering.md` (and the parallel
`protocol/versions/2/contract/engineering.md`) gain four new binding
rules:

- **C-070**: canonical identifiers (schema keys, Change/requirement IDs,
  Gate names, Contract rule IDs) MUST remain invariant regardless of
  configured interaction language — interaction language governs prose
  only.
- **C-071**: Gate semantics MUST NOT vary by interaction language — a
  Gate condition's satisfaction is identical regardless of the prose
  language it is expressed or evaluated in.
- **C-072**: deterministic project configuration
  (`interaction.language` set to a value other than `auto`) MUST take
  precedence over any Harness-observed or chat-inferred language signal.
- **C-073**: an Adapter projecting interaction-language guidance MUST NOT
  represent that projection as a guarantee of the Harness's actual output
  language — Core can project an instruction; it cannot verify Harness
  compliance with it (mirrors C-066's "harness honesty" shape for
  delegated-Execution authority claims).

Neither C-072 nor C-073 is validated by `forge validate`; both are
honesty and precedence obligations on the Harness/Adapter, not
mechanically checked Gate conditions, matching C-067's own disclaimer for
a different concern (found in Specification Review, SR-001).

### FR-003 — Specification §42

`protocol/specification.md` gains `## 42. Interaction Language
Resolution`, defining the concept, the three-level precedence chain, that
Core resolves only the deterministic (explicit-configuration) level and
projects an instruction for the Harness-hint level (Core cannot observe
live chat state — §2, §33), and an explicit statement that
repository/context heuristic detection is out of scope for this Change,
pointing at the ADR.

### FR-004 — Codex Adapter projects the effective instruction

The Codex Adapter's generated `SKILL.md` contains exactly one interpolated
interaction-language instruction line, reflecting the effective
configuration:

- explicit `interaction.language` value `X`: the line states the Harness
  MUST interact in `X`, citing C-072 (deterministic configuration takes
  precedence).
- absent or `auto`: the line states the Harness SHOULD use the active
  chat's observed language if there is one, otherwise English, citing
  C-070–C-073.

### FR-005 — Documentation Impact

`CHANGELOG.md`, the ADR (`docs/adr/0015-interaction-language-resolution.md`),
and `ROADMAP.md`'s own status line for this section are updated at
Completion, matching the precedent every prior FULL Change (`CHG-0013`,
`CHG-0015`, `CHG-0016`) already set.

## Non-functional Requirements

### NFR-001 — Backward compatibility

Every existing `.forge/forge.yml` (this repository's own and any external
project's) continues to validate unchanged; every existing
`AdapterProjectionContext`/`CodexProjectionInput` construction call site
that does not pass the new field keeps producing byte-identical output
except for the one new, intentional `SKILL.md` line.

### NFR-002 — Harness independence

No Codex-specific, Claude-specific, or other single-provider concept is
introduced into `AdapterProjectionContext` (the generic Adapter Core) or
into the Contract/Specification text. The new field and rules are
Harness-agnostic; only `codex/projection.py`'s `SKILL.md` interpolation is
Codex-specific, matching where `artifact_structure_content`'s own
Codex-specific rendering already lives.

### NFR-003 — Projection follows the existing additive-field pattern

`interaction_language` on `AdapterProjectionContext`/`CodexProjectionInput`
uses the same `str = ""` additive-default shape as
`artifact_structure_content`, `contract_content`, and every other existing
field on those dataclasses — no new construction pattern is invented.

## Constraints

### CON-001 — No semantic regression

No Flow, lifecycle stage, Finding severity, Review convergence rule, or
Unresolved Decision Management mechanic is added, removed, or altered.

### CON-002 — Schema stability elsewhere

No schema other than `project.schema.json` is modified by this Change.

### CON-003 — Namespace separation

The Decision this Change resolves (DEC-001, below) is recorded once, in
the ADR and this Specification's Unresolved Decisions section — not
restated or duplicated inside Contract or Specification prose (mirrors
INV-001's reference-not-restate discipline, applied to Decision records
too).

### CON-004 — Historical validity

Every historical Change (`CHG-0001`–`CHG-0016`) remains `complete` and
valid; `forge validate`/`forge doctor` report no new finding against any
of them after this Change lands.

### INV-001 — No false compliance claim

No Artifact produced by this Change (Contract text, Specification text,
Codex projection output, or this Change's own Artifacts) may state or
imply that Core has verified, or can verify, what language a Harness
actually produced in a live chat session. Only the instruction is
verifiable; compliance is not (C-073).

## Acceptance Criteria

- **AC-001**: `protocol/schemas/project.schema.json` validates a
  `.forge/forge.yml` with an explicit `interaction: {language: "pt-BR"}`,
  with `interaction: {language: "auto"}`, and with `interaction` entirely
  absent — all three valid.
- **AC-002**: The same schema rejects a malformed `interaction.language`
  value (e.g. `"Portuguese"`, `"PT_BR"`, empty string) with
  `InvalidProjectConfigurationError`.
- **AC-003**: `protocol/contract/engineering.md` and
  `protocol/versions/2/contract/engineering.md` both contain C-070
  through C-073, worded identically (or with only the Protocol-1-vs-2
  framing differences the file's own header already establishes for
  inherited rules).
- **AC-004**: `protocol/specification.md` contains `## 42. Interaction
  Language Resolution` after §41, defining the three-level precedence
  chain and citing C-070–C-073.
- **AC-005**: A generated Codex `SKILL.md` for a project with
  `interaction.language: pt-BR` contains a line instructing interaction
  in `pt-BR`, citing C-072.
- **AC-006**: A generated Codex `SKILL.md` for a project with no
  `interaction` configuration (or `auto`) contains the auto/fallback
  instruction line instead, citing C-070–C-073.
- **AC-007**: Every existing Codex projection test that does not pass
  `interaction_language` continues to pass unchanged except for the one
  new, intentional line difference.
- **AC-008**: `forge validate` and `forge doctor` report no new finding
  against this repository's own historical Changes after this Change
  lands.
- **AC-009**: `docs/adr/0015-interaction-language-resolution.md` exists
  and records DEC-001 (Alternative A vs. B, human Decision, Alternative A
  selected).
- **AC-010**: `CHANGELOG.md` and `ROADMAP.md` reflect this Change at
  Completion.

## Unresolved Decisions

### DEC-001 — Precedence chain scope (three levels vs. four)

**Class**: `product` (affects the shape of a Requirement this
Specification states — non-negotiable `human` Authority floor per
`protocol/policies/decision.yml`, matching `contract`'s own floor).

**Question**: Does this Change implement the ROADMAP's full four-level
precedence chain (explicit config → repository/context language →
active chat language → English fallback), or a reduced three-level chain
that defers the repository/context heuristic level?

**Alternatives**:

- **A — Three levels (recommended)**: explicit project configuration →
  Harness-observed chat hint (Harness-resolved, Core only instructs the
  Harness to look for one) → English fallback. The repository/context
  heuristic level is explicitly deferred as a documented, known
  limitation.
- **B — Four levels**: additionally implement a repository-content
  language-detection heuristic inside Core (e.g. inspecting README or
  comment language).

**Trade-offs**: Alternative A ships a smaller, fully deterministic,
fully testable mechanism, consistent with this repository's stated
discipline against speculative machinery (top-level engineering
guidance: no abstraction or mechanism beyond what a task demonstrably
requires). It leaves a real ROADMAP-named level unimplemented, recorded
honestly as a limitation rather than silently dropped. Alternative B is
more literally faithful to the ROADMAP's original four-level sketch, but
there is no single correct, deterministic algorithm for "this
repository's language" — any heuristic would need its own Specification,
failure-mode analysis, and test suite disproportionate to a Change the
ROADMAP itself calls "the smallest of the remaining items," and a wrong
guess is a worse outcome (silently interacting in the wrong language)
than no guess at all (falling through to the next, honest level).

**Recommendation**: Alternative A.

**Resolved via**: `human_decision`. **Decision**: Alternative A.
**Authority**: `human`. **Owning Artifact**: this Specification (per
`protocol/policies/decision.yml` `ownership.owning_artifact_by_class.product:
specification`). Full record: `docs/adr/0015-interaction-language-resolution.md`.

## Out of Scope

- Repository/context-language heuristic detection (deferred by DEC-001).
- Translating any canonical Protocol document, schema, or this
  repository's own English-language Artifacts.
- Any new Flow, lifecycle stage, Finding severity, Review convergence
  rule, or Unresolved Decision Management semantic change.
- A second Harness Adapter.
- `forge validate`/`forge doctor` mechanical enforcement of *which*
  language a Harness actually produced (impossible for Core to observe;
  see INV-001/C-073).

## Traceability

Populated in `traceability.yml` at Plan/Tasks stage onward, per this
repository's own established practice (`CHG-0016/test-strategy.md`
"Traceability (informal)").
