---
forge:
  artifact: verification
  schema: 1
change: CHG-0052
status: complete
---

# CHG-0052 · Verification

## Result

**PASS**

## Summary

All six Functional Requirements (FR-001–FR-006) and NFR-001 verified.
`tests/capabilities/test_investigate_capability.py` (20 scenarios,
covering TD-001–TD-006) passes against the real
`capabilities/investigate/CAPABILITY.md`; the full repository suite and
`forge validate` pass with no other change to the codebase. TD-007
(Manual Acceptance — qualitative reading) remains for the independent
Reviewer, per its own Boundary in `test-design.md`.

## Acceptance Coverage

| Acceptance | Requirement | Result | Evidence |
|---|---|---|---|
| AC-001 | FR-001 | PASS | `test_investigate_capability_loads_via_existing_loader` — id/schema/all seven sections non-empty; `git diff --stat` confirms `loader.py`/`model.py`/`capabilities/capability.md` untouched |
| AC-002 | FR-002 | PASS | `test_evidence_driven_sequence_key_terms_are_named`, `test_plausible_guess_antipattern_is_named` — hypothesis/reproduction/evidence/root-cause terms and `plausible guess` present in Behavior; manual reading confirms the eight-step sequence is spelled out as an enumerated list |
| AC-003 | FR-003 | PASS | `test_root_cause_conclusion_markers_are_literal`, `test_evidence_classification_is_declared` — literal `ROOT CAUSE CONFIRMED`/`ROOT CAUSE NOT ESTABLISHED` and `CONFIRMED`/`INFERRED`/`UNKNOWN` present |
| AC-004 | FR-004 | PASS | `test_boundary_denial_fragments_are_present` (approv/flow/gate/lifecycle/decis) — Behavior's dedicated boundary paragraph denies every prohibited authority by name |
| AC-005 | FR-005 | PASS (structural) / pending TD-007 for qualitative completeness | `test_investigate_capability_loads_via_existing_loader` confirms Applicability is non-empty; full category coverage is TD-007's responsibility |
| AC-006 | FR-006 | PASS | `test_no_harness_or_forbidden_mechanism_vocabulary` (claude/codex/cursor/CapabilityRegistry/CapabilityExecutor//investigate/SKILL.md) — none found in `CAPABILITY.md`; `git diff --stat` confirms `capabilities/README.md`, `capabilities/capability.md` untouched |

## Test Evidence

`tdd-evidence.yml` TDD-001 records RED (20 errors, `CapabilityDefinitionError` — file not found) and GREEN (20 passed) for `tests/capabilities/test_investigate_capability.py`.

`python -m pytest tests/capabilities/ tests/unit/test_adapter_capabilities.py -q` → **53 passed**.

Full suite: `python -m pytest -q` → **882 passed**, 2 pre-existing unrelated warnings (`test_experience_capture.py`, unaffected by this Change).

## Forge Evidence

`forge validate` → **Forge project is valid**.

## Compatibility and Limitations

No code change to `src/forge_cli/capabilities/{loader.py,model.py}`, `capabilities/README.md`, or `capabilities/capability.md` — confirmed via `git diff --stat` returning empty for those four paths. AC-005's qualitative-completeness claim (does Applicability's category list read as genuinely sufficient, not merely present) is deferred to TD-007, a Manual Acceptance scenario by design (`test-design.md` — testing prose completeness mechanically risks freezing prose instead of behavior).

## Conclusion

Implementation scope (FR-001–FR-006, NFR-001) is verified against the real `capabilities/investigate/CAPABILITY.md` and the real, unmodified loader — not a synthetic fixture. Ready for Strict Review, including TD-007's manual reading.
