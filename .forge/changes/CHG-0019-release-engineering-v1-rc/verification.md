---
forge:
  artifact: verification
  schema: 1
change: CHG-0019
status: passed
---
# Verification — CHG-0019

## Result

**PASS.**

## Summary

| Acceptance Criterion | Result |
| --- | --- |
| AC-001 — changed `CLI_VERSION` reflected in built wheel/sdist, no `pyproject.toml` edit needed | PASS |
| AC-002 — `forge migrate --check` reports exactly the six real candidates | PASS |
| AC-003 — `forge migrate` rewrites only the six `schema:` lines, `forge validate` still passes | PASS |
| AC-004 — a `delegated_task` fixture is never touched | PASS |
| AC-005 — `forge doctor` advisory only when a candidate exists; exit code unaffected | PASS |
| AC-006 — `C-075` byte-identical (modulo wrapping) in both Contract files | PASS |
| AC-007 — `publish.yml` valid, inert, OIDC-only (no stored token) | PASS |
| AC-008 — `pyproject.toml` metadata present in built wheel `METADATA` | PASS |
| AC-009 — `RELEASING.md` exists, references (not restates) `compatibility.md`, valid PEP 440 | PASS |
| AC-010 — `CHANGELOG.md`/`ROADMAP.md` reflect this Change; no historical Change invalidated | PASS |

## Test Evidence

- `pytest -q` (full suite): **520 passed, 0 failed** — up from the
  pre-Implementation baseline of 504. 16 new tests: 8 in
  `test_migration.py` (including the real-historical-fixture round trip),
  6 in `test_migrate.py` (CLI), 2 new in `test_doctor.py`.
- TDD-001 through TDD-004 (`tdd-evidence.yml`): all GREEN, genuine RED
  observed for TDD-001, TDD-002, TDD-003.

## Forge Evidence

- `forge validate` — **"Forge project is valid"** (exit 0), unchanged.
- `forge doctor` — **7/7 checks PASS**, plus one new, expected,
  non-blocking `WARN migration_available: 6 migration candidate(s)
  found...` — exit code still 0.
- `forge migrate --check` against this repository itself reports exactly
  the six real candidates Discovery identified
  (`CHG-0008`, `CHG-0011`–`CHG-0015`). **Deliberately not applied for
  real against this repository's own files** — `git status` after every
  local verification step confirms zero files under `.forge/changes/`
  were ever written by anything in this Change; running the real
  migration against this repository's own historical evidence is left as
  a distinct, later, human decision (`plan.md`'s Implementation Boundary).

## Distribution Verification (local reproduction, not a live CI run)

- `python -m build` (wheel + sdist) succeeds against the unmodified
  repository.
- Installed the built sdist into a fresh, isolated venv and ran `forge
  version` offline — matches the wheel-only check `verification.yml`
  already had, now proven for the sdist path too before trusting CI to
  repeat it.
- `publish.yml` verified by direct reading (correct trigger —
  `release: {types: [published]}`, `permissions: id-token: write`, no
  `secrets.PYPI_API_TOKEN` reference anywhere) and by YAML-parsing all
  three workflow files successfully. **Not** verified by an actual CI
  run or a real publish — no GitHub Release exists to trigger it, and
  none is created by this Change (NFR-002).

## Compatibility

No file under `protocol/schemas/` changed (CON-002). No historical
Change (`CHG-0001`–`CHG-0018`) reports a new `forge validate` finding.
`forge/execution-provenance@1` files this Change does not apply
migration to (this repository's own six, left untouched) remain valid,
matching `compatibility.md`'s own "not deprecated" statement.

## What Required Correction During Implementation Itself

Two real corrections, both caught before any freeze, both recorded in
`knowledge-capture.md`: RED for TDD-001 had to be captured by temporarily
reverting the already-written fix (not narrated retroactively); a fourth
schema-version pair (`forge/policy/review@1`/`@2`) was found at
Specification Review and required a third, distinct exclusion reason.

## Limitations

`publish.yml`'s actual PyPI-publishing behavior cannot be verified end to
end without a real GitHub Release and a real PyPI trusted-publisher
registration, neither of which this Change performs. This is a stated,
accepted limitation (Verification's own scope), not a defect — the
workflow's correctness is established by direct reading and by locally
reproducing every step it performs that *can* be reproduced locally
(build, install, smoke-test), not by claiming an untestable step was
tested.

## Conclusion

All 10 Acceptance Criteria verified PASS. Zero regressions in the 504
pre-existing tests; 16 new tests added and passing. `forge validate` and
`forge doctor` clean (one new, expected, non-blocking advisory). No
release, tag, or publication was created by this Change. Ready for
independent Strict Review.
