---
forge:
  artifact: discovery
  schema: 1
change: CHG-0013
status: complete
---

# Discovery — CHG-0013

## Repository truth audit

Established directly from `protocol/`, `.forge/`, and `src/forge_cli/` (not
from prior session memory), 2026-08-18:

- No existing vocabulary for "ambiguity," "clarification," "unresolved
  decision," or "decision gate" exists anywhere in `protocol/`, `ROADMAP.md`,
  `ARCHITECTURE.md`, or `docs/adr/`. This is new vocabulary, not a rename —
  confirmed by grep across all normative and design documents.
- `security.yml` has the only existing "assumption" concept in the Protocol:
  `assumptions.must_be_explicit_when_material: true`, scoped to security
  only. This is direct precedent for generalizing "material assumption must
  be explicit" Protocol-wide, and for how a Material Assumption and an
  Unresolved Decision must relate (§Interaction with Assumptions below).
- `review.yml` (`resolution_verification` block) and
  `protocol/versions/2/specification.md` §10–§13 (CHG-0011) already contain
  one concrete, narrower instance of this exact pattern:
  `convergence_decision` is a human decision record (`option` enum +
  `reason`) that Forge requires when it reaches a state it cannot resolve
  for itself (Non-Convergence). CHG-0011's own `intent.md` explicitly
  deferred the general form: *"No general Decision Gate / Decision Analysis
  framework... planned for a later Change."* This Change is that Change.
  `convergence_decision` is not retrofitted onto the new mechanism (see
  Non-goals in `intent.md`); it remains valid prior art demonstrating the
  pattern already works in this Protocol.
- `architecture.yml` already has an adjacent but distinct concept:
  `adr.required_when` lists trigger conditions
  (`long_lived_cross_cutting_decision`, `architectural_pattern_change`,
  `major_dependency_direction_change`, `significant_technology_choice`,
  `irreversible_or_expensive_to_reverse_decision`) for when an *already-made*
  architectural decision must be durably recorded as an ADR. This is a
  **documentation** obligation for a decision already resolved, not a gate
  that stops the workflow while the decision is open. The two concepts are
  complementary, not overlapping: an ARCHITECTURAL-class Unresolved Decision
  that matches one of these triggers still gets its own Decision record
  while open, and — once resolved — the ADR obligation from `architecture.yml`
  applies to the resolved outcome. Reused, not duplicated.
- `forge validate` (`src/forge_cli/validation/__init__.py::validate_project`)
  is small and almost entirely mechanical/deterministic. It checks
  `.forge/forge.yml` shape, resolves the effective Flow and Contract
  (existence only — it does not semantically validate Contract prose against
  a manifest), and — only for `protocol: 2` — runs
  `_validate_protocol2_review_provenance`, which is hand-written Python
  logic, not a generic policy interpreter. **Flow-file `gates.*.require`
  lists (e.g. `specification_review_passed`, `tasks_ready`) are not
  mechanically parsed or enforced by the CLI at all** — they are read and
  followed by the agent, and checked adversarially by Strict Review. Every
  `protocol/policies/*.yml` file is likewise agent-consumed prose/YAML that
  `validate_project` never loads (confirmed by the same absence in
  CHG-0011's own Discovery). This means: (a) any new Gate-blocking language
  I add to flow YAML is enforced exactly the way every existing Gate is
  enforced — by the agent and by Strict Review, not by the CLI; and (b) the
  only new *mechanical* enforcement this Change can honestly claim is the
  same narrow, deterministic slice CHG-0011 added — a Core-derived check
  against `manifest.yml` shape, analogous to
  `_validate_resolution_verification`. Overclaiming mechanical guarantees
  here would repeat exactly the kind of error CHG-0011's own Strict Review
  caught in its first iteration (evidence_gap on `CHG-0011-R004`, a
  Specification overstating actual enforcement).
- `forge/change@2` (`change-v2.schema.json`) and `forge/change@1`
  (`change.schema.json`) both use `additionalProperties: false` at the top
  level and inside `artifacts`/`review`/etc. A new top-level `decisions`
  field is additive to both without weakening either. `artifacts` is
  `{"type": "object"}` with no enum on its values anywhere in either schema
  — Change authors already write free-form status strings there
  (`complete`, `approved`, `active`, `pending` are conventions, not
  schema-enforced enums). Introducing `invalidated`/`revised` as additional
  conventional values requires no schema change to `artifacts` itself, only
  documentation of the convention plus new Core validation logic that reads
  it.
- No CLI subcommand creates a Change (`forge --help` lists only `version`,
  `init`, `validate`, `doctor`, `adapter`). Per ADR-0002, Changes are
  chat-executed and repository-native: this Change was created by an agent
  writing `.forge/changes/CHG-0013-unresolved-decision-management/`
  directly, exactly like every prior Change in this repository's history
  (`CHG-0001` through `CHG-0012`, `CHG-0009` never having been created is
  consistent with "Planning documents MUST NOT reserve Change identifiers" —
  §3 of `specification.md`).

## Critical finding: Protocol 2's canonical Contract is missing C-047–C-050

`src/forge_cli/protocol_resolution/__init__.py::_versioned_protocol_root`
resolves the canonical Contract for a project declaring `protocol: 2`
(this repository's own `.forge/forge.yml` declares exactly that) to
**`protocol/versions/2/contract/engineering.md`** — a *separate, complete*
file, not a delta over the root file — whenever that directory exists. It
does exist (confirmed: `protocol/versions/2/contract/engineering.md`,
`Status: Canonical Protocol 2 Contract`, with a strengthened C-026, ending
at C-046).

CHG-0011 added C-047–C-050 (Resolution Verification, Convergence,
Non-Convergence) only to the **root** `protocol/contract/engineering.md`
(`Status: Canonical Protocol 1 Contract`). CHG-0011's own `discovery.md`
states as justification: *"[`protocol/versions/2/contract/engineering.md`]
does not exist for Protocol 2, so the Contract file is shared."* That
statement was incorrect at the time CHG-0011 was authored, or the file was
created concurrently without CHG-0011 noticing — either way, the file exists
now, `resolve_effective_contract(..., protocol_id=2)` reads only it, and it
does not contain C-047–C-050.

Practical consequence: this very repository (`protocol: 2`) has an
*effective canonical Contract* that omits the four rules its own
`review.convergence` mechanism is built on, even though `forge validate`'s
Python enforcement (`_validate_resolution_verification`) is hardcoded and
works correctly regardless — the gap is in the **documented normative text**
a Protocol 2 project actually resolves, not in mechanical enforcement. This
is a latent specification-consistency defect in the shipped CHG-0011, not
something this Change's own scope created.

**Decision made (technical, not requiring escalation):** this Change adds
its own new Contract rules (C-051 onward, see `specification.md`) to
`protocol/contract/engineering.md`, and — because leaving the sync gap in
place would mean this Change repeats CHG-0011's exact mistake and would
mean *this very project's own effective Contract* never sees the rules it
needs to dogfood itself (C-044) — this Change **also backfills C-047–C-050
and the new C-051+ rules into `protocol/versions/2/contract/engineering.md`**
as a minimal, directly-necessitated, evidence-driven correction. This is not
a general refactor of CHG-0011 (its Specification, policy, schema, and
validator changes are untouched); it is copying already-normative,
already-shipped rule text into the one place its own declared protocol
version requires it to be, so that this Change's own new rules land in the
same place consistently. This is recorded here as a Discovery finding with
its rationale, per this Change's own principle of not silently resolving a
material gap — it is technical/compatibility in nature (no product
behavior, no Requirement, no Gate meaning changes), so it does not require
human escalation, but it is disclosed rather than fixed invisibly.

## Compatibility finding

A new optional top-level `decisions` array on `forge/change@1` and
`forge/change@2`, and new conventional (non-schema-enforced) `artifacts.*`
status values, do not remove or weaken an existing invariant, do not change
the meaning of an existing required field or Gate, and do not invalidate any
previously valid conforming instance — every existing manifest in this
repository (`CHG-0001` through `CHG-0012`) has no `decisions` field and
continues to validate and mean exactly what it always meant. This is the
same "optional artifacts whose absence preserves existing meaning" category
`protocol/compatibility.md` already recognizes for CHG-0011. No new integer
Protocol identifier and no new schema suffix is required. Detailed in
`specification.md` §Compatibility.

## Adversarial self-check risk noted for Specification/Architecture

The single greatest risk in this design is **overclaiming mechanical
enforcement**. Because `forge validate` does not parse Markdown or evaluate
whether a Specification is materially complete, Core can only mechanically
detect a Material Unresolved Decision that an agent *already chose to
record*. It cannot detect the case where an agent should have recorded one
and silently did not. The actual guarantee against silent resolution is
process-level (Contract invariants + Specification Review's adversarial
obligation + Strict Review dimension), identical in kind to how Forge
already relies on Strict Review — not `forge validate` — to catch a missing
Requirement. Specification and Architecture must state this limitation
explicitly rather than imply Core can detect an *absent* Decision record.
