---
forge:
  artifact: verification
  schema: 1
change: CHG-0046
status: complete
---

# CHG-0046 · Verification

## Result

**PASS**

## Summary

All Acceptance Criteria (AC-001 through AC-007) verified and passing
against the **corrected, Protocol-conformant design** (Specification
Drift, after Codex's PR #37 finding that the original `state.current`-keyed
design directly contradicted `protocol/versions/2/specification.md` §5/§14).
11 total TDD cycles: TDD-001/TDD-002 are the original design's cycles,
kept and marked superseded (not deleted — an honest record of what was
tried and passed three internal independent Strict Review iterations
before external review found it non-conformant); TDD-008 through TDD-011
are the corrected replacement cycles (explicit, anchored,
per-path-scoped renewal records); TDD-003/TDD-005 (characterization/
fail-closed guards) and TDD-004/TDD-006/TDD-007 (MR-017 and the R001/R002
Resolution fixes) are unaffected by the Specification Drift and remain
valid as originally recorded.

## Acceptance Coverage

| Acceptance | Requirement | Result | Evidence |
|---|---|---|---|
| AC-001 | FR-001 | PASS | TDD-008 (`test_merge_check_tolerates_change_local_artifact_with_anchored_renewal_record`) |
| AC-002 | FR-001 (bounded, not claimed) | PASS | TDD-003 (`test_merge_check_does_not_detect_external_drift_after_completion`) — characterization, confirms this Change's blast radius stays inside `change_root` |
| AC-003 | FR-001 | PASS | TDD-009 (`test_merge_check_still_flags_change_local_edit_without_renewal_record`) |
| AC-004 | FR-002 | PASS | TDD-004 (`test_agent_adapter_generated_paths_resolve_to_a_definite_classification`, 10 parametrized cases) |
| AC-005 | FR-002 | PASS | TDD-005 (`test_unrelated_unclassified_path_still_falls_back_to_ambiguous`) plus pre-existing `test_ambiguous_unclassified_diff_is_blocked` |
| AC-006 | FR-001 | PASS | TDD-010 (`test_merge_check_ignores_unanchored_renewal_record`) |
| AC-007 | FR-001 | PASS | TDD-011 (`test_merge_check_scopes_renewal_tolerance_to_the_declared_paths`) |

## Test Evidence

- TDD-001/TDD-002: superseded — see `tdd-evidence.yml` for the historical RED/GREEN record of the original design, and TDD-008/TDD-009 for the corrected replacements below.
- TDD-003: passes unmodified before and after the Specification Drift (characterization test of the pre-existing, Out-of-Scope gap). Unaffected — this check never depended on the renewal-record mechanism.
- TDD-004/TDD-005: unaffected by the Specification Drift (MR-017 is a separate, unrelated fix). Still passing.
- TDD-006/TDD-007: unaffected — R001/R002's Resolution fixes are independent of MR-015's tolerance mechanism.
- TDD-008: RED confirmed (no renewal-record lookup existed pre-Drift) — GREEN after adding the anchored, scoped renewal-record check to `evaluator.py`, reusing `_first_committed_record` from MR-021.
- TDD-009: MR-015 fires with no renewal record present, regardless of `state.current`'s value — confirms tolerance requires an explicit record.
- TDD-010: an unanchored (later-rewritten) renewal record provides no tolerance — confirms the anchoring check is load-bearing, not decorative.
- TDD-011: a renewal record's tolerance is scoped to exactly its declared paths — confirms a record covering `knowledge-capture.md` cannot be abused to blanket-tolerate an unrelated `specification.md` rewrite in the same commit.
- Full suite: `.venv/bin/python -m pytest -q` → `706 passed, 2 warnings` (both warnings pre-existing, `tests/unit/test_experience_capture.py`, unrelated to this Change).
- `tests/cli/test_merge_check.py` alone: `14 passed`.
- `tests/unit/test_merge_readiness_policy.py`: `12 passed`.

## Forge Evidence

- `forge validate` → `Forge project is valid`.
- `forge doctor` → all `PASS` except the same two pre-existing, unrelated `WARN`s as before (`adapter:installation_missing`, `migration_available`).
- **Specification-level acceptance check, re-run after the Specification Drift**, against CHG-0045's actual PR #36 commits: because CHG-0045's own branch was never given an explicit renewal provenance record for its Documentation/Knowledge-Capture delta (it relied on the now-superseded `state.current` tolerance, which never actually shipped to `main` — CHG-0045's own commits predate this Change entirely), reproducing the check against CHG-0045's real commits **now correctly reports `MR-015` again**, in addition to the unrelated `MR-006`/`MR-008` gaps already documented as Out of Scope. This is not a regression in this Change — it is the corrected design accurately declining to grant tolerance CHG-0045 never explicitly requested. Closing it requires CHG-0045's own branch to add one renewal provenance record (`role: implementation`, `scope` naming its actual Documentation/Knowledge-Capture delta paths, `revision.commit` an ancestor of its head) after this Change merges — recorded as necessary follow-up work, not performed by this Change (Out of Scope: this Change does not modify CHG-0045's branch).

## Compatibility and Limitations

No Protocol version change; no artifact schema change — this Change's
corrected design uses only fields (`role`, `revision`, `scope`) already
defined and used elsewhere in `forge/execution-provenance@2` for
`resolution` records; it does not introduce a new schema shape. No other
code in `src/` reads `merge_readiness/evaluator.py` or
`protocol/policies/merge-readiness.yml` outside the `merge_readiness`
package itself and its CLI wiring. This Change does not, and does not
claim to, close the separate pre-existing gap TDD-003 characterizes (no
protection against a completed Change's implementation changing outside
its own `change_root`) — Out of Scope, flagged separately. TDD-006's
Resolution work also surfaced a second, unrelated, pre-existing bug in
`src/forge_cli/validation/__init__.py:321` — flagged separately, not
fixed here.

## Conclusion

FR-001 (corrected) and FR-002 fully implemented and verified against
their Specification Acceptance Criteria. No regression in the existing
test suite. `forge validate`/`forge doctor` clean. This Change no longer
claims CHG-0045's PR #36 is unblocked by this fix alone — the corrected,
Protocol-conformant design requires CHG-0045 to take one further,
explicit action (a renewal provenance record) that the superseded design
did not. Ready for a fresh independent Strict Review of the corrected
design.
