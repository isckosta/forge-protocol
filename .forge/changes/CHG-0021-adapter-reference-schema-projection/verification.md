---
forge:
  artifact: verification
  schema: 1
change: CHG-0021
status: passed
---

# Verification — Adapter Reference Schema Projection

## Result

**PASS**

## Summary

| AC | Description | Result |
| --- | --- | --- |
| AC-001 | Renderer content matches live constants | PASS |
| AC-002 | Claude Code includes resource + link when provided | PASS |
| AC-003 | Codex includes resource + link when provided | PASS |
| AC-004 | `resolved_via` message states expected values | PASS |
| AC-005 | Additive-only, both Adapters | PASS |
| AC-006 | Cross-Adapter byte-identical content parity | PASS |
| AC-007 | Regression baseline unchanged | PASS |

## Test Evidence

`pytest -q` (full suite): **535 passed, 0 failed** — the pre-Implementation
Baseline (524) plus 11 deliberate, additive new tests.

**Correction (post-Review):** at the `implementation-001` commit this
figure was not yet true. Strict Review Iteration 1 (`review.md` R001,
BLOCKER) independently reproduced **534 passed, 1 failed** against that
exact frozen commit — `traceability.yml`'s `CON-001`/`CON-002` entries
declared `tasks: []`, which `protocol/schemas/traceability.schema.json`'s
`minItems: 1` rejects, failing
`tests/contract/test_protocol_contract.py::test_canonical_yaml_instances_satisfy_their_declared_schemas`.
Resolved by naming the real tasks in both entries (`traceability.yml`);
re-verified independently, `pytest -q` now genuinely reports 535 passed,
0 failed. See `tdd-evidence.yml` `TDD-008` for the Resolution's own
RED/GREEN evidence.

- `tests/unit/test_decision_rules_reference.py` — 6 new tests (AC-001,
  AC-006).
- `tests/unit/test_claude_code_projection_bundle.py` — 2 new tests
  (AC-002, AC-005).
- `tests/unit/test_codex_projection_bundle.py` — 2 new tests (AC-003,
  AC-005).
- `tests/unit/test_unresolved_decisions.py` — 1 new test (AC-004).

`tests/integration/test_adapter_distribution.py`'s installed-wheel golden
path (`test_installed_wheel_runs_the_codex_adapter_golden_path_offline`)
passes, including its updated `_effective_reference_links` expectation
and new `decision-rules.md` content-marker assertions in
`adapter_cli_wheel_probe.py` — see `tdd-evidence.yml` notes for the
mid-Implementation discovery this required.

## Forge Evidence

`forge validate` → `Forge project is valid` (exit 0), unchanged from the
pre-Implementation Baseline. `forge doctor` → 7/7 checks PASS, with the
same single, pre-existing, non-blocking `migration_available` WARN
recorded in `discovery.md`'s Baseline — no new finding.

## Compatibility

Additive only, confirmed by test: `test_projection_bundle_omits_decision_rules_resource_when_not_provided`
(both Adapters) shows a caller that does not pass
`decision_rules_content` gets the exact pre-Change resource set, matching
FR-005's compatibility contract and `CHG-0016`'s own precedent for
`artifact_structure_content`.

## What Required Correction During Implementation Itself

`tests/integration/adapter_cli_wheel_probe.py`'s `_effective_reference_links`
carried a hardcoded expected reference-link list that predated this
Change; it needed `references/decision-rules.md` added in its correct
position, plus new content-marker assertions (no byte-exact `protocol/`
source file exists for this generated resource, unlike
`artifact-structure.md`). This is not a defect in the Plan — it is the
same class of Implementation-time discovery `CHG-0016`'s own
`tdd-evidence.yml` recorded for the identical script, for the identical
reason (a second, independent consumer of the reference-link shape that
`specification.md`/`plan.md` did not name individually).

## Limitations

This Verification was performed by the same Execution/Execution Context
that did Implementation — it confirms the stated evidence is real and
reproducible, but it is not the independent Strict Review Protocol 2
requires before Completion. That Review follows separately, in a
distinct, cold Execution Context.

## Conclusion

All seven Acceptance Criteria pass. The full suite, `forge validate`, and
`forge doctor` are unchanged in overall status from the pre-Implementation
Baseline, with only the deliberate, additive new tests changing the
count. Proceeds to Strict Review.
