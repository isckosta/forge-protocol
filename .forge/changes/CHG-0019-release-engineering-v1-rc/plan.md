---
forge:
  artifact: plan
  schema: 1
change: CHG-0019
status: approved
---
# Plan — CHG-0019

**Written for DEC-001 resolved (architectural, autonomous, per
`architecture.md`).**

1. `pyproject.toml`: `dynamic = ["version"]` + `[tool.hatch.version]`
   pattern sourcing from `version.py`; add `authors`/`urls`/
   `classifiers`/`keywords`.
2. `src/forge_cli/migration.py`: `MigrationCandidate`, `MigrationResult`,
   `find_candidates`, `apply_migrations`.
3. `app.py`: `forge migrate --check` / `forge migrate` commands.
4. `doctor.py`: one new advisory `DoctorCheck` (`status="warning"`) when
   a candidate exists.
5. Protocol docs: `C-075` in both Contract files.
6. `.github/workflows/publish.yml` (new); `verification.yml` (remove
   stale branch triggers, add sdist smoke check).
7. `RELEASING.md` (new); `CHANGELOG.md` convention line; `ROADMAP.md`
   version-string correction.
8. Tests: TDD-001 (version sourcing), TDD-002 (migration engine, against
   copied fixtures built from this repo's own six real `@1` files, never
   mutating the originals), TDD-003 (doctor advisory), TDD-004
   (repository-wide baseline unchanged).
9. Documentation: `docs/adr/0017-*.md`, `knowledge-capture.md`,
   `traceability.yml`, `tdd-evidence.yml`.
10. Strict Review: adversarial, evaluating in particular NFR-001
    (migration honesty in the actual code, not just C-075's text), that
    `publish.yml` is genuinely inert, and that no historical Change's
    real `provenance.yml` was touched by this Change's own tests.

## Validation Strategy

`pytest -q`, `forge validate`, `forge doctor`, `forge migrate --check`
(against this repo itself — real six-candidate report, no mutation),
`python -m build` (wheel + sdist, locally) — against the pre-
Implementation baseline, before Implementation begins.

## Compatibility Impact

None: additive CLI surface, additive Contract rule, additive CI
workflow, dynamic-but-identical version string. No historical Change
invalidated. No real release cut.

## Implementation Boundary

Reaching `tasks_ready` is not, by itself, authorization to begin
Implementation. For this Change, that explicit go-ahead was already
given via this session's plan-mode approval. Separately, and
independent of that approval: nothing in this Change creates a git tag,
a GitHub Release, or triggers `publish.yml` — that remains a distinct,
later, explicitly-authorized human action, not bundled into this
Change's own Completion. `tasks.md` below has every task unchecked; none
has been started as of this Plan's own approval.
