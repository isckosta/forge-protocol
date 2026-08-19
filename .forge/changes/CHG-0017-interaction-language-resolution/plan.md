---
forge:
  artifact: plan
  schema: 1
change: CHG-0017
status: approved
---
# Plan — CHG-0017

**Written for DEC-001 = Alternative A (three-level precedence, repository/
context heuristic deferred) and DEC-002 = Alternative A (interpolated
`SKILL.md` line, no new resource file). Both resolved before this Plan is
written — DEC-001 human, DEC-002 autonomous per `architecture.md`.**

1. Schema: `protocol/schemas/project.schema.json` — add the optional
   `interaction.language` object/property per `specification.md` FR-001.
2. Protocol docs: `protocol/contract/engineering.md` and
   `protocol/versions/2/contract/engineering.md` (append `C-070`–`C-073`,
   byte-identical modulo each file's own pre-existing wrapping
   convention, verified against the `specification-review.md` SR-002
   precedent check); `protocol/specification.md` (new `§42`, after §41).
3. ADR: `docs/adr/0015-interaction-language-resolution.md` (number
   re-verified against `docs/adr/` immediately before writing, matching
   `CHG-0016/plan.md` step 7's own stated practice, not assumed frozen at
   Planning time).
4. Codex Adapter: `src/forge_cli/adapters/driver.py`
   (`AdapterProjectionContext.interaction_language: str = ""`),
   `src/forge_cli/adapters/codex/projection.py`
   (`CodexProjectionInput.interaction_language`, `_skill_content(...)`
   interpolated line per `architecture.md`'s Content Shape), and
   `src/forge_cli/adapters/service.py` (populate the field from the
   already-loaded `configuration` dict at both existing
   `AdapterProjectionContext(...)` construction sites). No `adapter.yml`
   capability change; `validate_conformance` untouched (`architecture.md`
   Adapter/Harness Integration).
5. Tests: TDD-001 (projection carries and renders the field correctly,
   both branches) and TDD-002 (repository-wide `forge validate`/`forge
   doctor`/`pytest` baseline unchanged) per `test-strategy.md`, baseline
   captured before any Implementation edit lands.
6. Documentation/Knowledge Capture (deferred content, not authored now):
   `CHANGELOG.md` entry, `ROADMAP.md` status flip, `knowledge-capture.md`.
   `traceability.yml` and `tdd-evidence.yml` are **not** produced by this
   Plan — same reasoning `CHG-0015/plan.md` and `CHG-0016/plan.md` step 7
   already recorded: producing them before any test exists would be
   reconstructed evidence, forbidden by C-016/C-021.
7. Strict Review: adversarial, evaluating in particular INV-001 (no false
   compliance claim actually introduced, not just specified), C-070–C-073
   wording fidelity to what DEC-001/DEC-002 actually resolved, and
   whether the rendered `SKILL.md` output for both the explicit and
   `auto` cases actually matches `specification.md` FR-004 rather than
   merely claiming to.

## Validation Strategy

`pytest -q` (existing suite plus TDD-001/TDD-002), `forge validate`,
`forge doctor` — all three against the pre-Implementation baseline
captured in step 5, before Implementation begins.

## Compatibility Impact

None: additive schema field, additive dataclass fields, one new,
intentional `SKILL.md` line. No Schema other than `project.schema.json`
changes (CON-002). No historical Change invalidated. No new Protocol
integer.

## Implementation Boundary

Reaching `tasks_ready` (`full.yml`'s `before_implementation` Gate) is not,
by itself, authorization to begin Implementation. For this Change, that
explicit, separate human go-ahead was already given before Discovery
began — the human's approval of the full implementation plan (covering
Discovery through Completion, dogfooded as a real Change) via this
session's own plan-mode approval, distinct from DEC-001's resolution
above. `tasks.md` below has every task unchecked; none has been started
as of this Plan's own approval.
