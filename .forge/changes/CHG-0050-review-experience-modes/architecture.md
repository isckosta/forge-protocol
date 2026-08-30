---
forge:
  artifact: architecture
  schema: 1
change: CHG-0050
status: complete
---

# Architecture — CHG-0050 Review Experience Modes

## Solution Summary

Extract the review-profile-floor computation that already exists,
inline, inside `_validate_review_profile_floor`
(`src/forge_cli/validation/__init__.py:773-786`) into a small,
reusable, pure function, and build the mode-to-profile resolution
(FR-002) directly on top of it — no new floor logic, only a new
consumer of the one that already exists. Add three additive schema
fields (`review.mode`, `review.current_phase` on `manifest.yml`;
`review.preferred_mode` on `.forge/forge.yml`). Add one Core validator
for phase/status consistency (FR-004). Add one shared Adapter-facing
module for mode/phase instruction prose, imported by both existing
Adapters exactly the way `review_independence.py` already is. Add one
read-only CLI command. No existing function's behavior changes for a
manifest that sets none of the three new fields (NFR-001).

## Component Map

| FR | Component | File | Change |
|---|---|---|---|
| FR-002 | `compute_review_profile_floor` | `src/forge_cli/validation/__init__.py` | New function; extracts existing inline logic from `_validate_review_profile_floor` (lines 774-780), used by both the validator (refactored to call it) and FR-002's resolver |
| FR-002 | `resolve_effective_review_profile` | `src/forge_cli/protocol_resolution/__init__.py` | New function, alongside `resolve_effective_flow` |
| FR-001 | `manifest.yml` `review.mode` field | `protocol/schemas/change-v2.schema.json` | New optional enum property under `properties.review` |
| FR-004 | `manifest.yml` `review.current_phase` field | `protocol/schemas/change-v2.schema.json` | New optional enum property under `properties.review` |
| FR-004 | `_validate_review_current_phase` | `src/forge_cli/validation/__init__.py` | New function, called from `validate_project` per Change manifest, alongside existing per-manifest checks |
| FR-003 | `.forge/forge.yml` `review.preferred_mode` field | `protocol/schemas/project.schema.json` | New optional enum property under `properties.review` (sibling of the existing locked `strict`) |
| FR-001, FR-003 | `_manifest()` | `src/forge_cli/change_scaffolding.py:373-406` | New `review_mode: str = "recommended"` parameter; sets `manifest["review"]["mode"]` |
| FR-003 | `new_change()` / `_active_flow()` | `src/forge_cli/change_cli.py:54-150` | Read `configuration.get("review", {}).get("preferred_mode", "recommended")` and pass it through to `render_scaffold`/`_manifest` |
| FR-005 | `review_experience.py` (new module) | `src/forge_cli/adapters/review_experience.py` | Per-Flow mode-resolution line + one shared phase-vocabulary section, imported by both Adapters — sibling of the existing `review_independence.py` |
| FR-005 | `_gate_instructions` | `src/forge_cli/adapters/claude_code/projection.py:92-122`, `codex/projection.py:71-101` | Per Flow, append `review_experience.render_mode_resolution_line(floor)`; once after the loop, append `render_review_experience_section()` (see DEC-004 — corrected from the original per-Change framing) |
| FR-006 | `review_status()` | `src/forge_cli/change_cli.py` (new command) | New read-only subcommand |

## Data Flow

```
manifest.yml (review.mode, review.current_phase)
        |
        v
resolve_effective_review_profile(floor, mode)      <- compute_review_profile_floor(effective_flow)
        |                                                        ^
        |                                                        |
        v                                                resolve_effective_flow (unchanged)
   effective profile ---------------------+
        |                                 |
        v                                 v
Adapter _gate_instructions          `forge change review-status`
(claude_code, codex)                 (reads manifest directly, no git diff)
```

`forge validate`'s `_validate_review_current_phase` reads the same
manifest independently, checking only enum membership and
phase/status consistency — it does not call
`resolve_effective_review_profile` (phase and profile are orthogonal
concerns; FR-004's Acceptance Criteria never reference profile).

## DEC-002

**Decision**: `forge change review-status`'s next-step hint (FR-006)
is computed directly from `manifest.review.current_phase` and
`manifest.review.iterations[]`/severity counts, not by invoking
`evaluate_merge_readiness` (`src/forge_cli/merge_readiness/evaluator.py`).

**Reasoning**: `evaluate_merge_readiness` is designed around a
committed two-commit diff range (`--base`/`--head`) and answers "is
this commit range mergeable." `review-status` targets a Change's
*currently declared* state directly from its manifest — including a
Change with uncommitted `manifest.yml` edits, which
`evaluate_merge_readiness`'s `git show`-based reads cannot see.
Reusing it would either force `review-status` to require two Git refs
(contradicting FR-006's Given/When/Then, which take only `{slug}`) or
silently read stale committed state. A next-step hint of comparable
information content is fully derivable from data `review-status`
already reads for its other fields (phase, Finding counts by
severity), so no duplication of `merge_readiness`'s own diagnostics is
needed.

**Class**: technical, owned by `plan` per the Decision Rules
(`technical -> plan, tasks`), recorded as `DEC-002` in `manifest.yml`
with `discovered_in: architecture`. **Authority**: agent
(`resolved_via: evidence`) — this is an implementation-strategy choice
within Specification's own stated boundary (FR-006's Acceptance
Criteria constrain behavior, not mechanism), not a reduction of any
Contract or product-facing guarantee.

## DEC-004

**Decision**: `_gate_instructions` (both Adapters) does not, and
cannot, read a specific Change's `manifest.review.mode`/
`current_phase` — it runs once per canonical Flow at `forge adapter
install` time, before any specific Change exists. Corrected design:
per-Flow, project a mode-to-profile resolution line computed purely
from that Flow's own floor (`resolve_effective_review_profile(floor,
"thorough")`); once, after the per-Flow loop, project one shared,
Flow-invariant section explaining the `review.mode`/`current_phase`
vocabulary and pointing at `forge change review-status <slug>` for any
specific Change's live value.

**Reasoning**: discovered while implementing FR-005 (Plan item 9) —
the original Architecture text assumed `_gate_instructions` had a
Change in scope, mirroring how `REVIEW_PROFILE_INSTRUCTION` already
works today; it does not, because `review.profile` is Flow-static
(known at install time) while `review.mode`/`current_phase` are
per-Change (unknown at install time). This is a non-material
correction to FR-005's mechanism, not its outcome: the Harness still
learns the mode vocabulary, the resolved-profile consequence, and the
phase vocabulary from Adapter-projected text, and still gets a
per-Change live view — through `forge change review-status` (FR-006)
instead of through the static projection.

**Class**: technical, owned by `plan` (Decision Rules). **Materiality**:
non_material (mechanism-only; RFC-0008's guarantees and Specification's
Acceptance Criteria are updated to match, not weakened). **Authority**:
agent (`resolved_via: evidence`).

## Schema Changes (concrete)

`protocol/schemas/change-v2.schema.json`, under the existing
`properties.review` object, add:

```json
"mode": {
  "enum": ["recommended", "fast", "thorough"],
  "description": "Developer-facing Review Experience Mode. Absent is interpreted as 'recommended'."
},
"current_phase": {
  "enum": ["scanning", "findings_recorded", "resolving", "re_reviewing", "converged", "stopped"],
  "description": "Schema-tracked Review phase (RFC-0008 SS4). Absent before any Review Iteration is recorded."
}
```

`protocol/schemas/project.schema.json`, under the existing
`properties.review` object (sibling of the locked `strict`), add:

```json
"preferred_mode": {
  "enum": ["recommended", "fast", "thorough"],
  "description": "Default review.mode seeded into new Change scaffolds by `forge change new`. Never overrides an already-set per-Change value."
}
```

Both additions are optional properties on objects that already declare
`additionalProperties: false` with other required siblings unchanged —
no existing required-field set changes, satisfying NFR-001/C-045.

## Adherence to Existing Architecture (C-032)

This design was checked against, and reuses without modification:
`resolve_effective_flow` (`protocol_resolution/__init__.py`), the
existing `_PROFILE_RANK` ordering, `_validate_resolution_verification`'s
FR-010 targeted-re-review escalation, the Convergence Limit counter,
and `review_independence.py`'s existing shared-Adapter-text pattern
(`review_experience.py` is a deliberate sibling of it, not a
competing pattern — C-033). No new architectural pattern is
introduced; this Change composes four existing patterns (floor
computation, project-config additive fields, shared Adapter prose
modules, read-only CLI commands) rather than inventing a fifth.
