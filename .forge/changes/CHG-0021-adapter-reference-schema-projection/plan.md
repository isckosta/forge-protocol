---
forge:
  artifact: plan
  schema: 1
change: CHG-0021
status: approved
---

# Plan — Adapter Reference Schema Projection

1. Add `render_decision_rules_reference() -> str` to
   `src/forge_cli/validation/__init__.py`, placed immediately after the
   `_DEC_*` constants and `_DEC_ID_RE` it documents (per `architecture.md`
   DEC-001).
2. Sharpen the `resolved_via` invalid-value error message inside
   `_validate_unresolved_decisions` (same file), per `architecture.md`
   "Error message change".
3. Add `decision_rules_content: str = ""` to `AdapterProjectionContext`
   in `src/forge_cli/adapters/driver.py`, alongside
   `artifact_structure_content`.
4. Wire `decision_rules_content=render_decision_rules_reference()` at
   both `AdapterProjectionContext` construction sites in
   `src/forge_cli/adapters/service.py` (the same two call sites that
   already compute `artifact_structure_content`).
5. Thread `context.decision_rules_content` through
   `src/forge_cli/adapters/claude_code/driver.py` and
   `src/forge_cli/adapters/codex/driver.py`.
6. Add the `decision_rules_content` field, `has_decision_rules` gate, the
   `skills/forge/references/decision-rules.md` resource, and its
   reference link to `src/forge_cli/adapters/claude_code/projection.py`,
   mirroring `artifact_structure_content`/`has_artifact_structure`
   exactly.
7. Add the equivalent plumbing (`references/decision-rules.md`) to
   `src/forge_cli/adapters/codex/projection.py`.
8. New test module `tests/unit/test_decision_rules_reference.py` for
   TDD-001 (renderer content against the live constants).
9. Extend `tests/unit/test_claude_code_projection_bundle.py` and
   `tests/unit/test_codex_projection_bundle.py` for TDD-002, TDD-003,
   TDD-005, TDD-006.
10. Extend `tests/unit/test_unresolved_decisions.py` for TDD-004.
11. Run the TDD-007 regression baseline (full `pytest -q`,
    `forge validate`, `forge doctor`) both immediately before starting
    step 1 and again after step 10, and record both in `verification.md`.
12. Assemble `tdd-evidence.yml`, `traceability.yml`, `verification.md`,
    and `manifest.yml` from the real evidence produced by steps 1–11 —
    never pre-filled before Implementation exists (Contract C-016/C-021).

## Implementation Boundary

Reaching `tasks_ready` is not authorization to begin Implementation.
Anything discovered during Implementation that this Plan did not
anticipate belongs in Verification, a new Decision record, or a
documented re-Plan — never as a silent edit to this already-approved
Plan's content.
