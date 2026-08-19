# Discovery — Interaction Language Resolution

## Executive Summary

`ROADMAP.md` names Interaction Language Resolution as the next unstarted
item in the recommended v1 execution order (after Protocol v1 Contract
Freeze and Adapter CLI & Codex Installation UX, both complete). It is the
smallest of the four remaining items. The mechanism this Change needs is
architecturally a near-exact structural twin of `CHG-0016` (Canonical
Artifact Structure): a new Contract-governed concept threaded through the
existing generic `AdapterProjectionContext` → `CodexProjectionInput` →
`generate_codex_skill_bundle` pipeline as one more additive field. The
ROADMAP itself flags one unresolved question it deliberately does not
answer — which precedence signals are deterministic configuration versus
Harness-only hints — and that question is escalated to a human Decision
in this Change rather than assumed (see "Open Questions").

## Repository State at Investigation Time

- HEAD: `85c8ce0` (`docs(chg-0016): T-016 -- Completion`), working tree
  otherwise clean except this Change's own new, untracked
  `.forge/changes/CHG-0017-interaction-language-resolution/` directory.
- Sixteen prior Changes exist (`CHG-0001`–`CHG-0016`), all `complete`.
  `CHG-0016` is the most recently completed and the closest structural
  precedent.
- `forge/project@1` (`protocol/schemas/project.schema.json`) has no
  `interaction` key today; `additionalProperties: false` at the top level
  means an unrecognized key would fail schema validation outright — this
  Change's field must be added to the schema, not merely documented.
- `protocol/contract/engineering.md` ends at `C-069`; the next free rule
  number is `C-070`. `protocol/versions/2/contract/engineering.md` is a
  parallel, not-generated copy (confirmed via CHG-0013's changelog entry,
  which backfilled it independently) that needs the same rules added.
- `protocol/specification.md` ends at `## 41. Canonical Artifact
  Structure`; the next free section number is `42`.
- `protocol/versions/2/specification.md` is scoped exclusively to Protocol
  2's distinguishing review/provenance semantics (Execution provenance,
  Assurance, Review subject freeze, Resolution Verification, Convergence,
  etc. — 13 sections, none about interaction or presentation language).
  Interaction Language Resolution applies independently of Protocol
  version, matching how §41 (Canonical Artifact Structure) is scoped —
  it does not belong in this file.

## Existing Normative Layers (what already governs this Change)

- `protocol/specification.md` §2 ("The chat remains the runtime... The
  repository remains durable memory... Forge remains the protocol") and
  §33 (Local operation: normal Forge operation must not require a hosted
  backend) together establish that Core cannot observe live chat state —
  it configures and projects; a Harness executes. Any precedence level
  requiring live chat-session awareness is necessarily a Harness
  responsibility, not something Core resolves itself.
- `protocol/specification.md` §29 (Configuration resolution): "Project
  configuration references canonical concepts by stable identifiers and
  MAY strengthen or specialize behavior only where the Protocol permits
  it... Project extensions MUST NOT weaken canonical invariants." This is
  the existing authority for adding `interaction.language` as project
  configuration rather than as a new Protocol-version-gated concept.
- `protocol/contract/engineering.md` C-067 establishes the precedent that
  new canonical guidance can be non-binding (a "SHOULD", not a Gate
  condition) when that is the correct strength — relevant because this
  Change's invariants (C-070–C-073, drafted in Specification) are
  deliberately **binding** MUSTs, not guidance, since they protect
  machine-readable interoperability rather than human presentation
  preference.
- `protocol/policies/decision.yml`: `product` and `contract` Decision
  Classes have a non-negotiable `human` Authority floor
  (`authority_floor: {product: human, contract: human}`). The ROADMAP's
  own deferred question ("which signals are deterministic configuration
  vs. Harness hints") is exactly this class of question.

## Comparative Mechanism Analysis: CHG-0016's Projection Pattern

`CHG-0016` added `protocol/artifact-structure.md`, a static canonical
guidance document, and projected it into the Codex Adapter's output as a
new conditionally-included `references/artifact-structure.md` resource
file, gated on non-empty content (`has_artifact_structure = bool(...)`).
Traced concretely for reuse:

- `AdapterProjectionContext` (`src/forge_cli/adapters/driver.py`) —
  generic, Harness-independent dataclass — gained
  `artifact_structure_content: str = ""` as an additive-default field.
- `CodexProjectionInput` (`src/forge_cli/adapters/codex/projection.py`)
  gained the same field, passed straight through
  `generate_codex_projection_bundle` into `generate_codex_skill_bundle`,
  which conditionally added a `references/artifact-structure.md` resource
  and a matching link line in `_reference_links` only when the content was
  non-empty.
- `src/forge_cli/adapters/service.py` populated the field at both existing
  `AdapterProjectionContext(...)` construction sites (the conformance/
  doctor path and the `_prepare`/publish path) by resolving the canonical
  file via `resolve_effective_artifact_structure`
  (`src/forge_cli/protocol_resolution/__init__.py`), a small new resolver
  function mirroring the existing `resolve_effective_contract` shape.
- `validate_conformance` (`src/forge_cli/adapters/validation.py`) was
  **not** touched — it diffs stage/gate/invariant *names* and two
  booleans, and has no awareness of reference-file content. A purely
  informational addition does not need to touch it.
- Tests followed a consistent four-layer shape: a resolver-level unit test
  (existence/fallback/missing), a projection-bundle-level pair
  (omitted-when-absent / included-when-provided), a driver-level
  end-to-end test, and a wheel-probe integration update for the new
  reference link.

**This Change's one structural departure**: artifact-structure content is
a large, static, canonical document, so a separate `references/*.md` file
made sense. Interaction-language content is a single small,
**project-specific** value (a configured code like `pt-BR`, or the
sentinel `auto`) — not a document. Projecting it as a whole extra resource
file would be disproportionate; it belongs as one interpolated instruction
line inside `SKILL.md` itself. The Contract rules governing interaction
language (C-070–C-073, drafted below) require no new plumbing to reach a
Codex session at all — `references/engineering-contract.md` already
projects the entire effective Contract text verbatim, so new Contract
rules are automatically visible the moment they exist.

## Flow Classification Finding

This Change touches: a Protocol schema (`project.schema.json`), the
Contract (`engineering.md`, both copies), the Specification
(`specification.md` §42), a new ADR recording a `product`/`contract`-class
Decision, and executable Adapter projection code with new tests. Per
`protocol/contract/engineering.md` C-003 (semantic classification) and
matching every prior Change that touched Contract + Specification +
executable Adapter code (`CHG-0013`, `CHG-0015`, `CHG-0016`, all `full`),
this Change is classified **FULL**. No FAST/STANDARD candidate signal is
present — the schema and Contract surface are both binding, not purely
additive-and-inert.

## Compatibility Finding

The schema addition is purely additive (`interaction` is optional, no
existing `required` entry touches it) — every existing `.forge/forge.yml`
across every historical Change and any external project continues to
validate unchanged. `AdapterProjectionContext`/`CodexProjectionInput`
field additions use the same additive-default pattern CHG-0015 and
CHG-0016 both already established as safe (every existing caller that
does not pass the new field keeps working identically). No Protocol
version bump is warranted — this mirrors CHG-0016's own DEC-002
conclusion (Alternative A: additive Contract/Specification content, no new
integer) for the same underlying reason: nothing here weakens or
redefines an existing invariant, per §29's own compatibility test.

## Documentation Impact Signal (preliminary)

Expected updates: `CHANGELOG.md` (new "Unreleased" subsection), `ROADMAP.md`
(flip this section's status once complete, matching the Golden Path
section's own inline completion marker), `docs/adr/0015-*.md` (new ADR),
and `docs/getting-started.md` only if it enumerates `.forge/forge.yml`
fields (confirmed absent — `docs/getting-started.md` does not currently
mention `interaction`, `language`, or enumerate the project schema
field-by-field, so no edit is required there). Final Documentation Impact
evaluation is recorded at Completion.

## Open Questions Requiring Human Decision

**DEC-001 (`product`/`contract` class, `human` authority per the
non-negotiable floor)**: The ROADMAP proposes a four-level precedence
chain (explicit config → repository/context language → active chat
language → English fallback). The third level is genuinely a Harness
runtime concern Core cannot resolve. The second level — repository/context
language — would require Core to run some content-based heuristic
(reading README/comments/commit-message language) with no single correct,
deterministic answer, which is exactly the kind of speculative mechanism
this repository's own engineering discipline avoids building without
demonstrated need.

- **Alternative A (recommended)**: Reduce to a three-level precedence for
  this Change — explicit project configuration → Harness/chat-observed
  language hint (resolved by the Harness at runtime, Core only projects
  the instruction to look for one) → English fallback. The
  repository/context heuristic level is explicitly deferred, recorded as
  a documented limitation, not silently dropped.
- **Alternative B**: Implement a real repository-content heuristic inside
  Core now. Rejected in Discovery as premature: no deterministic algorithm
  for "this repository's language" exists that would not itself need its
  own Specification, testing, and failure-mode analysis disproportionate
  to this Change's stated scope (ROADMAP: "the smallest of the remaining
  items").

**Resolved**: Human Decision selected Alternative A (recorded in
`docs/adr/0015-interaction-language-resolution.md` and
`specification.md`'s Unresolved Decisions section). This Discovery
document is not amended retroactively; the resolution is the Specification
stage's and the ADR's record to own, per `protocol/policies/decision.yml`
`ownership.owning_artifact_by_class.product: specification`.
