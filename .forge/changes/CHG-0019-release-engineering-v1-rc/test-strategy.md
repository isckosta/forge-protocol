# Test Strategy — CHG-0019

## Objective

This Change is a mix of executable code (`migration.py`, CLI commands,
the doctor advisory) and infrastructure/policy prose (Contract rule,
workflow YAML, `RELEASING.md`). TDD applies fully to the executable
parts; Protocol §19 marks the prose deliverables `not_applicable`.

## Strategy

Four TDD cases:

## TDD-001 — Dynamic version sourcing

**Covers:** FR-001, AC-001.

**RED:** `python -m build` against the unmodified `pyproject.toml`
produces `0.1.0.dev0` regardless of `CLI_VERSION`'s value (they're
independent today) — change `CLI_VERSION` first to observe this,
confirming the drift risk is real, not hypothetical.

**GREEN:** After `dynamic = ["version"]` + `[tool.hatch.version]`, a
changed `CLI_VERSION` is reflected in the built wheel/sdist filename and
`METADATA` without touching `pyproject.toml`.

## TDD-002 — Migration engine (the real, safe case)

**Covers:** FR-002, FR-003, NFR-001, AC-002–AC-004, CON-004.

**RED:** `find_candidates`/`apply_migrations` don't exist; a test
asserting a fixture with `schema: forge/execution-provenance@1` (no
`delegated_task` role) is detected and, on apply, has only its `schema:`
line changed, fails (`ModuleNotFoundError`).

**GREEN:** Implement both functions. Assert: a `delegated_task` fixture
is never touched; a `forge/change@1`/`adapter-installation@1` file is
never scanned at all (wrong schema family, ignored by construction); the
rewritten file's content is byte-identical to the original except the
one `schema:` line (verified with a line-by-line diff, not just
schema-validity).

**Fixture discipline (CON-004):** tests copy this repository's own six
real `CHG-0008`/`CHG-0011`–`0015` `provenance.yml` files into a `tmp_path`
fixture first; `find_candidates`/`apply_migrations` run only against the
copies. The real files under `.forge/changes/` are read once (to build
the fixture) and never written by any test.

## TDD-003 — `forge doctor` migration advisory

**Covers:** FR-004, AC-005.

**RED:** `forge doctor` against a project with a migration candidate
present shows no advisory line today (the check doesn't exist) — fails
the assertion that it should.

**GREEN:** The new `DoctorCheck` (`status="warning"`) appears only when
`find_candidates` returns non-empty; `DoctorResult.passed` is unaffected
either way (`status != "failed"`).

## TDD-004 — Repository-wide baseline unchanged

**Covers:** CON-003, AC-010.

**RED:** Baseline capture, not a failing assertion (matches every prior
Change's own TDD-00x precedent).

**GREEN:** `forge validate`/`forge doctor`/`pytest -q` report the
identical overall status against every historical Change after
Implementation, plus `forge migrate --check` against this repository
itself correctly reports exactly six real candidates (read-only; not
applied to this repository's own files by the test suite or by any
Implementation step — a human decides separately whether/when to run
`forge migrate` for real against this repository).

**Baseline recorded before Implementation** (HEAD `d489f1b`, working tree
otherwise clean except this Change's own new, untracked planning
directory): `forge validate` reports **"Forge project is valid"** (exit
0); `forge doctor` reports all 7 checks `PASS`; `pytest -q` (full suite)
reports **504 passed**. Real candidate count confirmed by direct grep:
exactly six files (`CHG-0008`, `CHG-0011`–`CHG-0015`) declare `schema:
forge/execution-provenance@1`, and none of the six contains a
`delegated_task` role (checked line by line). Any regression against
these exact figures during Implementation is investigated before
Verification proceeds.

## Non-mechanical Validation

- `C-075`'s wording against FR-005 and against CHG-0007's own real
  precedent (not merely plausible-sounding, actually the same principle).
- `publish.yml`'s YAML validity and that it triggers only on
  `release: published` — reviewed, not merely asserted, since no test
  can safely simulate a real publish.
- `RELEASING.md` against INV-001 (references, doesn't restate,
  `compatibility.md`) and PEP 440 correctness of every version string in
  it and in the corrected `ROADMAP.md` sketch.

## Completion Criteria

All of AC-001 through AC-010 satisfied; TDD-001–004 GREEN; Non-mechanical
Validation items reviewed and accepted at Strict Review; `tdd-evidence.yml`/
`traceability.yml` produced from real Implementation evidence.
