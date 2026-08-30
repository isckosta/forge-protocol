---
forge:
  artifact: plan
  schema: 1
change: CHG-0050
status: approved
---

# Plan — CHG-0050 Review Experience Modes

1. Extract `compute_review_profile_floor(effective)` out of
   `_validate_review_profile_floor`'s existing inline logic
   (`src/forge_cli/validation/__init__.py:774-780`); refactor that
   validator to call it. RED: adapt/extend
   `tests/unit/test_validation_review_profile.py` to call the new
   function directly before it exists (TDD-001), confirm existing
   floor-validator tests still pass unchanged after the refactor.

2. Add `resolve_effective_review_profile(floor: str, mode: str) ->
   str` to `src/forge_cli/protocol_resolution/__init__.py`, built on
   `_PROFILE_RANK` (imported from `validation`, or a shared constant —
   decide placement to avoid a circular import at Implementation time).
   RED: new `tests/unit/test_protocol_resolution_review_mode.py`
   (TDD-002, TDD-003).

3. Add `review.mode` (enum `recommended|fast|thorough`) and
   `review.current_phase` (enum `scanning|findings_recorded|resolving|
   re_reviewing|converged|stopped`) to `protocol/schemas/change-v2.schema.json`'s
   `properties.review` object, both optional. RED: new fixture cases in
   `tests/contract/test_review_profile_schemas.py` (TDD-004, TDD-008).

4. Add `_validate_review_current_phase(manifest) ->
   list[ValidationFinding]` to `src/forge_cli/validation/__init__.py`,
   wired into `validate_project`'s existing per-Change-manifest loop.
   Implements: no finding for `converged`+`passed` or absent-phase+empty-
   iterations; exactly one finding for `converged` with a non-`passed`
   status. RED: new `tests/unit/test_review_current_phase_validation.py`
   (TDD-006, TDD-007).

5. Add `review.preferred_mode` (same enum) to
   `protocol/schemas/project.schema.json`'s `properties.review` object,
   as a sibling of the existing locked `strict` — `strict` itself is
   untouched. RED: schema fixture case alongside item 3's tests.

6. Add a `review_mode: str = "recommended"` parameter to `_manifest()`
   (`src/forge_cli/change_scaffolding.py:373-406`), setting
   `manifest["review"]["mode"]`. Thread it through `render_scaffold`'s
   signature and its one caller. RED: extend existing
   `change_scaffolding` tests to assert the new field's presence/value
   without breaking the byte-identical-scaffold assertion for the
   default case (TDD-010's non-behavioral half).

7. Update `_active_flow`/`new_change` in `src/forge_cli/change_cli.py`
   to read `configuration.get("review", {}).get("preferred_mode",
   "recommended")` from `load_project_configuration`'s already-loaded
   dict and pass it to `render_scaffold`. RED: new `tests/cli/`
   integration cases (TDD-009, TDD-010, TDD-011).

8. Create `src/forge_cli/adapters/review_experience.py`: mode/profile
   instruction text (parallel structure to
   `review_independence.py`'s `REVIEW_PROFILE_INSTRUCTION`) and a
   phase-to-human-label mapping (`scanning` → "Discovery",
   `findings_recorded` → "Findings", `resolving` → "Resolution",
   `re_reviewing` → "Re-review", `converged` → "Converged", `stopped` →
   "Stopped"). No RED of its own (pure data/prose module); covered
   indirectly by item 9's tests.

9. Update `_gate_instructions` in
   `src/forge_cli/adapters/claude_code/projection.py:92-122` and
   `codex/projection.py:71-101` to read `manifest.review.mode`/
   `current_phase`, call `resolve_effective_review_profile`, and append
   `review_experience.py`'s text — keeping the existing
   `review_independence.py` import/usage unchanged and unconditional.
   RED: extend `tests/unit/test_claude_code_projection_gates.py` and
   `test_codex_projection_gates.py` (TDD-012), including the
   byte-identical-independence-block assertion across mode values.

10. Add `forge change review-status {slug}` to
    `src/forge_cli/change_cli.py`: reads the named Change's
    `manifest.yml`, resolves mode/profile/phase, counts Findings by
    severity from `review.blockers/majors/minors/observations`, and
    prints a next-step hint per DEC-002 (no `merge_readiness` call).
    RED: new `tests/cli/test_change_review_status.py` (TDD-013,
    TDD-014).

11. Update `protocol/compatibility.md` with a `### CHG-0050` entry
    (mirroring the existing `### CHG-0048` entry's structure) and add
    an `Unreleased` entry to `CHANGELOG.md`. No `docs/adr/` entry is
    needed beyond RFC-0008 itself (F-008 already satisfied by the
    accepted RFC, same reasoning CHG-0048 recorded for RFC-0007).

## Implementation Boundary

Reaching `plan_complete`/`tasks_ready` is not authorization to begin
Implementation. Per C-077, this Change's manifest MUST record a
material technical Decision owned by `plan`, `authority: human`,
`status: resolved`, `resolved_via: human_decision`, with the Plan and
provenance recording the explicit human confirmation, before crossing
this boundary. An Implementation-time discovery that diverges from
this Plan belongs in Verification, a new Decision record, or a
documented re-Plan — never a silent edit to the items above.

<a id="forge-plan-approval-confirmation"></a>
## Plan Approval Confirmation

<a id="forge-plan-approval-record"></a>
**Approved.** The human maintainer (operator, this repository's Git
user) explicitly approved this Plan for Implementation in the active
chat session on 2026-08-30, via `AskUserQuestion`, after reviewing the
11 items above, DEC-001 (Flow escalation to FULL), and DEC-002
(`review-status`'s direct-manifest-read mechanism), selecting "Aprovar
e prosseguir". This confirmation is recorded per C-077 as `DEC-003` in
`manifest.yml` (`class: technical`, `owning_artifact: plan`,
`authority: human`, `status: resolved`, `resolved_via:
human_decision`) and in `provenance.yml`'s `plan-approval-001` record.
