# Verification — CHG-0016

<!-- Dogfooding this Change's own recommendation (FR-004,
     protocol/artifact-structure.md §4 Verification): Result first. -->

## Result

# PASS

## Summary

| Acceptance Criterion | Result |
| --- | --- |
| AC-001 — `protocol/artifact-structure.md` exists, defines all 6 principles | PASS |
| AC-002 — structural guidance for all 14 real Artifact types, real names | PASS |
| AC-003 — `forge validate` behavior unchanged (SHOULD-only; DEC-001 = A) | PASS |
| AC-004 — Verification `## Result` / Review `## Verdict` recommended; iteration convention preserved | PASS |
| AC-005 — Plan gains canonical `## Implementation Boundary` guidance | PASS |
| AC-006 — Contract C-067–C-069 reference, do not restate, the guidance | PASS |
| AC-007 — `protocol/specification.md` §41 added | PASS |
| AC-008 — `protocol/compatibility.md` addendum added | PASS |
| AC-009 — Codex Adapter projects the guidance by reference | PASS |
| AC-010 — canonical examples added; no historical Change reformatted | PASS |
| AC-011 — `ARCHITECTURE.md`, `docs/adr/0014`, `CHANGELOG.md` updated; no RFC | PASS |
| AC-012 — no file under `protocol/schemas/` changed | PASS |
| AC-013 — `forge validate`/`forge doctor` baseline unchanged | PASS |

## Test Evidence

- `pytest -q` (full suite): **429 passed, 0 failed** — up from the
  pre-Implementation baseline of 423 (`test-strategy.md` TDD-003 recorded
  35 for `tests/contract` only; the full-suite pre-Implementation figure,
  423, matches `CHG-0015/plan.md`'s own contemporaneous baseline note for
  this same repository state). 6 new tests added by this Change:
  `test_projection_bundle_omits_artifact_structure_resource_when_not_provided`,
  `test_projection_bundle_includes_artifact_structure_when_provided`,
  `test_codex_projection_includes_artifact_structure_reference_when_present`,
  `test_resolves_effective_artifact_structure_from_canonical_root`,
  `test_resolves_effective_artifact_structure_falls_back_from_versioned_root`,
  `test_fails_when_canonical_artifact_structure_is_unavailable`.
- TDD-001 through TDD-003 (`tdd-evidence.yml`): all GREEN, RED validly
  observed for TDD-001 (`TypeError`/`AttributeError` for the expected,
  not-yet-implemented reason).
- One pre-existing integration test,
  `tests/integration/test_adapter_distribution.py::
  test_installed_wheel_runs_the_codex_adapter_golden_path_offline`,
  initially failed after Implementation because its hardcoded expected
  reference-links list did not yet include the new,
  intentionally-added `references/artifact-structure.md` link. Updated
  (`adapter_cli_wheel_probe.py`) to assert the new link and to verify its
  installed content byte-for-byte against `protocol/artifact-structure.md`
  in the built wheel — this is the one deliberate behavior change this
  Change makes to the installed Codex skill's content, confirmed present
  and correct in an actual offline-installed wheel, not only in unit
  tests. See `knowledge-capture.md` for the full account.

## Forge Evidence

- `forge validate` — **"Forge project is valid"** (exit 0), unchanged
  from the pre-Implementation baseline, including this Change's own
  manifest (`DEC-001` resolved before Implementation began, per
  `specification.md`).
- `forge doctor` — **7/7 checks PASS**, unchanged.

## Compatibility

No file under `protocol/schemas/` changed (AC-012, verified: `git status`
against `protocol/schemas/` shows no modification). No historical Change
(`CHG-0001`–`CHG-0015`) reports a new `forge validate` finding. No
existing test's assertions changed in a way that weakens what it checks —
the one test edit (above) strengthens the assertion (checks one more real
link) rather than loosening it. `AdapterProjectionContext` and
`CodexProjectionInput` both gained the new field as an additive default,
confirmed by every pre-existing caller/test continuing to pass unchanged.

## What Required Correction During Implementation Itself

Plan step 4 named only `src/forge_cli/adapters/codex/projection.py` as
the file to change for FR-009. Implementing it correctly (reusing the
existing pattern per NFR-003, rather than inventing a Codex-only
shortcut) required also extending the generic `AdapterProjectionContext`
(`src/forge_cli/adapters/driver.py`), both of `service.py`'s context
construction sites, and a new `resolve_effective_artifact_structure`
function in `protocol_resolution/__init__.py`. Recorded here and in
`knowledge-capture.md`, per this Change's own C-069 recommendation, not
by editing the already-approved Plan to make it look like it had said
this all along.

## Limitations

None material. `protocol/artifact-structure.md`'s guidance is, by design
(`DEC-001`), non-binding — its actual adoption by future agent sessions
cannot be verified by this Verification and is explicitly named as an
accepted, revisitable risk in `architecture.md`'s Risks section and
`docs/adr/0014`'s Consequences.

## Conclusion

All 13 Acceptance Criteria verified PASS. Zero regressions in the 423
pre-existing tests; 6 new tests added and passing. `forge validate` and
`forge doctor` unchanged. Ready for independent Strict Review.
