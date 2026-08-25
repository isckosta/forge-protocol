---
forge:
  artifact: verification
  schema: 1
change: CHG-0048
status: complete
---

# Verification — CHG-0048 Proportional Review Profiles

## Result

**PASS**

## Summary

Three canonical Review Profiles (`focused`/FAST, `standard`/STANDARD,
`strict`/FULL) are implemented across Contract (C-022/C-023 revised,
C-031 clarified), the three Flow definitions, the canonical Protocol 2
review policy, four Schemas (three additive, one narrowing — the
direct encoding of the already-resolved Contract decision), a new
profile-floor validation function wired into the existing
`resolve_effective_flow` call site, and profile-aware Adapter
projections sharing one instruction source. `MR-004`'s label is
profile-neutral. All 13 Functional Requirements (FR-001–FR-013) map to
concrete evidence below. Protocol 1 (Contract, `policy-review.schema.json`)
is untouched; `review_independence.py`'s independence block is
byte-unchanged.

## Test Evidence

| AC | Requirement | Evidence |
|---|---|---|
| AC-001 | FR-001 | `test_canonical_flow_files_declare_the_expected_profile` |
| AC-002 | FR-002 | `test_projection_renders_focused_profile_instruction_for_fast` |
| AC-003 | FR-003 | `test_projection_renders_standard_profile_instruction_for_standard` |
| AC-004 | FR-004 | `test_projection_renders_unchanged_strict_instruction_for_full` (both Adapters) |
| AC-005 | FR-005 | Manual Acceptance (Contract text reading below) + `protocol/versions/2/contract/engineering.md` diff |
| AC-006 | FR-006 | Manual Acceptance + C-031 diff |
| AC-007 | FR-007 | `git diff` confirms C-024/025/026/027/047-050/059/067-068 byte-identical; `validation/__init__.py` diff confirms no new `flow`/`profile` conditioning in `_validate_resolution_verification`/`_validate_protocol2_review_provenance` |
| AC-008 | FR-008 | `tests/contract/test_review_profile_schemas.py` (18 tests) |
| AC-009 | FR-009 | `test_projection_reviewer_resolver_independence_block_is_unaffected_by_profile`, `test_projection_matches_claude_code_profile_instruction_text` |
| AC-010 | FR-010 | `tests/unit/test_validation_review_profile.py` (3 tests) |
| AC-011 | FR-011 | `test_no_historical_change_is_invalidated_by_the_review_profile_change` |
| AC-012 | FR-012 | `test_projection_review_profile_is_derived_fresh_not_cached` |
| AC-013 | FR-013 | `test_merge_check_mr_004_label_is_profile_neutral` |

- `.venv/bin/python -m pytest -q`: **784 passed, 2 warnings** (warnings
  pre-exist this Change — deliberate failure injection in
  `tests/unit/test_experience_capture.py`, unrelated).
- `.venv/bin/python -m pytest tests/contract/ -q`: **52 passed** (34
  pre-existing + 18 new schema round-trip tests).
- TDD-001 through TDD-004: see `tdd-evidence.yml`. TDD-001 and TDD-004
  have live, pre-GREEN RED evidence. TDD-002 and TDD-003 have
  retroactively-reconstructed RED evidence (the Schema/Flow and
  Adapter edits were made before their respective tests, an
  implementation-sequencing discovery documented honestly in
  `tdd-evidence.yml` per C-017/C-069, not concealed) — in both cases
  the pre-edit file content was loaded and mechanically re-validated
  against the exact same fixture documents the real tests use,
  reproducing genuine rejection/wrong-output before the fix, not
  merely asserting it would have failed.

## Forge Evidence

- `forge validate`: **PASS** ("Forge project is valid").
- `git diff --stat main..HEAD`: 33 files changed, matching Plan/Architecture
  scope exactly — Contract (1), Flows (3), canonical review policy (1),
  Schemas (4), validation (1), Adapters (3), merge_readiness (1), tests
  (6), documentation (2), and this Change's own 12 Artifacts.
- `grep -rn "ReviewProfileEngine\|ReviewProfileRegistry\|ReviewProfilePipeline"` across
  `src/`, `protocol/`, `tests/`: **no matches**.
- `protocol/contract/engineering.md` (Protocol 1), `protocol/schemas/policy-review.schema.json`
  (Protocol 1), `.claude/skills/forge/references/engineering-contract.md`:
  confirmed byte-identical to the pre-Change baseline (`git diff --stat 7495615..HEAD` for
  each path: no output).
- `_validate_resolution_verification` and `_validate_protocol2_review_provenance`
  (`src/forge_cli/validation/__init__.py`): confirmed via diff to carry no
  new branch conditioned on `flow` or `profile` (FR-007).

## Compatibility/Limitations

`src/forge_cli/adapters/review_independence.py` **was** touched — Plan
item 6 and Architecture's Component Design §6 stated it would not be.
This is a disclosed, deliberate implementation-time refinement, not a
silent Plan deviation (C-069): the new `REVIEW_PROFILE_INSTRUCTION` map
was added to this existing shared-text module (rather than duplicated
in both `projection.py` files, or introduced as a new module) because
it is the established CHG-0045 precedent for exactly this kind of
cross-Adapter shared text. The independence block itself
(`REVIEWER_RESOLVER_INDEPENDENCE_LINES`, `_POINTER`, and the render
function) is byte-unchanged — confirmed by diff — which is the
substantive guarantee the Plan's original constraint was protecting.

Two Schema changes are not purely additive, disclosed explicitly
rather than smoothed over: `flow.schema.json`'s `strict`/`adversarial`
`const: true` became plain booleans (a narrowing of a previously
unconditional, machine-checked guarantee — Architecture DEC-001-adjacent,
Specification FR-008), and `change-v2.schema.json`'s new `profile`
field lives on `review.iterations[]` items (per-Iteration historical
evidence) rather than a top-level `review.profile`, deliberately, so
no cached/stale profile value can exist to contradict FR-012's
"derived fresh" requirement.

`docs/rfcs/0005-review-cost-proportionality.md` is marked `Status:
Superseded by RFC-0007` — its own content is preserved unmodified as
historical record, not deleted.

No concrete change to `src/forge_cli/configuration/__init__.py` or
`.forge/forge.yml`'s `project.schema.json`-validated `review.strict`
field was made — DEC-001 established this is not the right
integration point (confirmed unread by any CLI code).

Independent Strict Review (`strict` profile, since this Change is
itself FULL Flow) remains pending.

## Conclusion

Verification passes for the implemented scope. The Change is not
marked complete until independent Strict Review is performed.
