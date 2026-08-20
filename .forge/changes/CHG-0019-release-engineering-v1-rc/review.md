---
forge:
  artifact: review
  schema: 1
change: CHG-0019
status: passed
---
# Strict Review — CHG-0019

## Verdict

**PASS (Iteration 1, `kind: initial_review`).** No BLOCKER or MAJOR
Finding. 2 MINOR, 1 OBSERVATION — none blocking per
`protocol/policies/review.yml` (`blocking: [blocker, major]`).

The core, highest-stakes claim of this Change — a migration engine that
touches this repository's own real historical evidence — holds up under
direct, hands-on adversarial testing, not narrative acceptance. I built my
own fixtures independently of the existing test suite, ran the actual
`find_candidates`/`apply_migrations` functions myself against copies of
this repository's own real `provenance.yml` files, and confirmed by
line-by-line diff that only the `schema:` line ever changes. I reproduced
the version-sourcing claim (TDD-001) end to end myself — changed
`CLI_VERSION` to a throwaway value, built a real wheel, confirmed the
filename and `METADATA` tracked it, and confirmed `git diff` was clean
after reverting. Both of this Change's two most consequential, hardest-to-
fake claims are genuine.

Two non-blocking MINOR findings and one OBSERVATION, detailed below, none
of which concern correctness or safety of the migration engine itself —
they concern a documentation-completeness gap and a missing regression
test for a manual verification.

## Summary

| Severity | Count | Blocking |
| --- | --- | --- |
| BLOCKER | 0 | yes |
| MAJOR | 0 | yes |
| MINOR | 2 | no |
| OBSERVATION | 1 | no |

## Review Subject

Frozen Implementation subject `443678bc0ec7dbd9423d1e306416ebecdc65bdf3`
(`provenance.yml`, record `implementation-001`), reviewed against this
Change's own baseline `d489f1b` (`CHG-0018`'s own Completion commit). The
later commit `c0f3e8a` (this session's own provenance-recording commit,
touching only Change-local review-control metadata) is exempt from the
freeze per Protocol 2 §5 and was not treated as part of the reviewed diff.

## Review Execution Independence

Executed cold, from committed repository state alone, in an Execution and
Execution Context distinct from the Implementation session that produced
`implementation-001`, per Contract C-026 and Protocol 2 §2. No prior memory
of this Change beyond what the committed Artifacts and diff state. Every
commit in `d489f1b..443678b` was read directly (`git log --oneline`,
`git show <sha>` for each of the four commits); no claim in
`verification.md`, `tdd-evidence.yml`, `knowledge-capture.md`,
`specification-review.md`, or any commit message was accepted without
independent reproduction. See `provenance.yml` record `review-001` for
this execution's own self-recorded provenance and honest assurance
statement.

## Findings

### R001 — MINOR — `CHANGELOG.md` has no dedicated entry for this Change's own substantive additions

**Problem:** Every prior historical Change in this repository's
`CHANGELOG.md` — "Second Harness Adapter (Claude Code)," "Interaction
Language Resolution," "Canonical Artifact Structure," "Delegated Agent
Authority and Side-Effect Boundaries," and every earlier one back to
"Foundation" — has its own `###` subsection under `## Unreleased`
describing what it added. CHG-0019 adds a new user-facing CLI command
surface (`forge migrate`/`forge migrate --check`), a new CI workflow
(`publish.yml`), a new Contract rule (C-075), and `RELEASING.md`, none of
which get a `###` entry. The only `CHANGELOG.md` change is a four-line
convention note prepended above `## Unreleased` (`git diff
d489f1b..443678b -- CHANGELOG.md`). `verification.md` marks AC-010
("`CHANGELOG.md`/`ROADMAP.md` reflect this Change at Completion") **PASS**
without this gap being caught.

**Evidence:** `grep -n "^##" CHANGELOG.md` shows the `## Unreleased`
section's only subsection is still `### Second Harness Adapter (Claude
Code)` (CHG-0018's own entry) — CHG-0019 is invisible to a reader of the
file that states its own purpose as "All notable Forge changes will be
documented here."

**Impact:** Non-blocking (documentation-completeness only; no functional
or safety consequence — the actual code, tests, and workflow are correct
and independently verified regardless of this gap). But it is a real,
demonstrable inconsistency with this repository's own established
convention, and AC-010 is verified PASS despite it.

**Suggested Resolution (Resolver's judgment, C-025):** Add a `###
Release Engineering & v1 Release Candidate (Infrastructure)` subsection
under `## Unreleased` naming the new `forge migrate`/`--check` commands,
the `forge doctor` advisory, `publish.yml`, `C-075`, and `RELEASING.md`,
matching the shape of every prior entry.

### R002 — MINOR — No automated regression test guards `pyproject.toml`'s dynamic version sourcing

**Problem:** TDD-001 (dynamic `CLI_VERSION` sourcing, FR-001/AC-001) was
verified exclusively by a one-time manual build reproduction during
Implementation (`tdd-evidence.yml`: "built a wheel... reverted `CLI_
VERSION`..."), not captured as a repeatable `pytest` test.
`traceability.yml`'s `FR-001` entry has `tests: []`. I confirmed this
directly: `grep -rln "hatch.version\|CLI_VERSION" tests/` returns nothing.

**Evidence:** No file under `tests/` references `CLI_VERSION` or
`hatch.version`. A future accidental regression — e.g. someone
reintroducing a static `version = "..."` field in `pyproject.toml`
alongside `dynamic = ["version"]` (which `hatchling` would likely reject
or silently prefer one over the other), or editing the regex pattern
incorrectly — would not be caught by `pytest -q`, only by a human manually
rebuilding and checking the wheel again.

**Impact:** Non-blocking. This is a coverage gap for a fix that is
otherwise genuinely verified today (I reproduced it myself independently,
see below), not a defect in the fix itself.

**Suggested Resolution (Resolver's judgment, C-025):** A cheap, fast unit
test reading `pyproject.toml` (e.g. via `tomllib`) asserting `dynamic ==
["version"]`, no static `version` key present, and `[tool.hatch.version]`
present with the expected `path`/`pattern`, would catch a future regression
without requiring a real build in CI.

## Observations

### O001 — OBSERVATION — `apply_migrations`'s exact string replacement targets the first textual occurrence of the schema string, not specifically the `schema:` key

**Problem:** `apply_migrations` (`src/forge_cli/migration.py:87`) does
`original.replace(_SOURCE_SCHEMA, _TARGET_SCHEMA, 1)` — a plain substring
replace of the first occurrence of the literal string
`"forge/execution-provenance@1"` anywhere in the file, not a replacement
scoped to the `schema:` key specifically. This is safe today: I confirmed
by direct grep that each of the six real candidate files contains exactly
one occurrence of that string (the `schema:` line itself, always the
file's first line). But the safety of this design rests on that empirical
fact about today's six files, not on a structural guarantee — a
hypothetical future `provenance.yml` whose `source.statement` prose
happens to quote `"forge/execution-provenance@1"` textually before the
actual `schema:` line would have the wrong occurrence rewritten (or,
depending on ordering, the prose rewritten instead of the schema field).
`_is_safe_v1_provenance`'s own YAML-structured check (`data.get("schema")
== _SOURCE_SCHEMA`) already correctly gates *candidacy* structurally; only
the rewrite step itself is a flat string operation.

**Impact:** None against any file this repository holds today (verified:
exactly one occurrence each in all six real candidates, confirmed by
direct grep). A latent fragility for a hypothetical future case, not a
present defect. Not blocking.

## Checked and found sound

- **Migration engine, the highest-stakes claim, verified by direct
  inspection and my own independent fixtures — not the existing test
  suite's.** Read `migration.py` in full: `find_candidates` is read-only
  by construction (only `Path.read_text`/`yaml.safe_load`, no write calls
  anywhere in its call graph); `apply_migrations` writes only when
  explicitly invoked (the CLI's `--check` branch returns before
  `apply_migrations` is ever called — confirmed by reading `app.py`'s
  `migrate` command). Built my own scratch fixture (copies of the real
  `CHG-0008` and `CHG-0011` `provenance.yml` files, independent of
  `tests/unit/test_migration.py`'s own fixture list) and ran the actual
  `find_candidates`/`apply_migrations` functions against the copies
  myself: both detected, both rewritten, `diff` against the originals
  shows only `schema: forge/execution-provenance@1` → `@2` on line 1 in
  each, nothing else differs. Confirmed via `git status --porcelain`
  before and after that the real files under `.forge/changes/` were never
  touched by this.
- **`forge migrate --check` against this actual repository, reproduced
  myself.** Reports exactly six real candidates (`CHG-0008`, `CHG-0011`
  through `CHG-0015`) — cross-checked independently against
  `grep -rl "schema: forge/execution-provenance@1" .forge/changes/*/
  provenance.yml`, which returns exactly these same six paths, none
  containing a `delegated_task` role. `git status --porcelain` was empty
  both before and after running `--check`. The applying form of `forge
  migrate` was never run against this repository's real `.forge/changes/`
  directory by this Review, per the assignment's own constraint.
- **`delegated_task` exclusion, verified with my own constructed
  fixture.** Built a fixture `provenance.yml` with one `implementation`
  and one `delegated_task` record; `find_candidates` returned `()`, and
  the file was byte-for-byte unchanged after calling `apply_migrations`
  with that empty result.
- **The three exclusion claims, each verified directly.**
  `forge/change@1` is structurally impossible for `find_candidates` to
  scan: it only ever reads files literally named `provenance.yml` under
  `.forge/changes/*/`, and `forge/change@1` lives in `manifest.yml`, a
  different file — confirmed by reading `find_candidates`'s file-selection
  loop. `compatibility.md` (lines 22, 30) is explicit: "`forge/change@1`
  preserves its historical shape and meaning" and a Protocol 2 repository
  "MAY retain completed historical `forge/change@1` Changes without
  retroactive migration." `forge/policy/review@1`/`@2`: `grep -rn
  "policy/review\|policies/review" src/forge_cli/` returns only
  `migration.py`'s own doc comment — no reader/validator of
  `.forge/policies/review.yml` exists anywhere in `src/`, confirming the
  "no live consumer" claim; independently confirmed this repository's own
  `.forge/policies/review.yml` still declares `schema: forge/policy/
  review@1` under `protocol: 2` today, exactly as `specification-
  review.md` describes.
- **Schema catalog cross-check.** `protocol/schemas/catalog.yml` lists
  exactly four schema families with more than one version —
  `adapter-installation`, `change`, `execution-provenance`, `policy/
  review` — matching Discovery's "four families" claim exactly, and the
  `policy-review.schema.json` vs. `policy-review-v2.schema.json` diff
  confirms a real, non-trivial content difference (nine new
  `reviewer_resolver_separation`/`re_review`-shaped sub-keys), not a
  cosmetic one.
- **TDD-001, reproduced end to end myself, not accepted from
  `tdd-evidence.yml`'s prose.** Changed `CLI_VERSION` to a throwaway
  `0.1.0.dev999`, ran `python -m build --wheel`: produced
  `forge_protocol-0.1.0.dev999-py3-none-any.whl`, whose `METADATA`
  correctly showed `Version: 0.1.0.dev999` along with `Author: Israel
  Costa`, all four `Project-URL` entries, `Keywords`, and every
  `Classifier` FR-009 requires. Reverted `version.py` to `0.1.0.dev0`
  afterward; `git status`/`git diff` confirmed clean, no stray change.
  `pyproject.toml` correctly declares `dynamic = ["version"]` with no
  leftover static `version = "..."` field (would conflict/be ambiguous
  with `hatchling` otherwise) — read directly.
- **`git log --all -p -- src/forge_cli/version.py pyproject.toml | grep
  "0\.1\.0\.dev1"` returns zero hits** — independently confirms
  `knowledge-capture.md`'s claim that no commit ever recorded
  Implementation's own temporary RED-capture test value.
- **Full test suite, reproduced independently.** `python -m pytest -q` →
  **520 passed**, matching `verification.md`'s claimed figure exactly (up
  from the stated 504 baseline). `forge validate` → "Forge project is
  valid" (exit 0). `forge doctor` → 7/7 PASS plus the one new, expected,
  non-blocking `WARN migration_available: 6 migration candidate(s)
  found...` — exit code still 0, exactly as FR-004/AC-005 require.
- **Workflow YAML, all three parsed successfully.** `publish.yml`,
  `verification.yml`, and `tests.yml` all load cleanly via
  `yaml.safe_load`. `publish.yml` triggers only on `release: {types:
  [published]}`; no `secrets.PYPI_API_TOKEN` or any `secrets.*` reference
  appears in any of the three workflow files (`grep -rn "secrets\."`
  returns nothing). `verification.yml`'s trigger is now `push: branches:
  [main]` + `pull_request` — the two stale branch names
  (`chore/chg-0001-verification`, `feat/chg-0002-harness-adapter-
  foundation`) are gone, and `git branch -a`/`git ls-remote --heads
  origin` confirm neither branch exists locally or on the remote (`main`
  is the only branch either place).
- **`C-075`, byte-identical (modulo wrapping) in both Contract files** —
  read both directly (`protocol/contract/engineering.md:307-311`,
  `protocol/versions/2/contract/engineering.md:245-246`), matching the
  `C-070`-`C-074` dual-file precedent exactly.
- **`RELEASING.md`'s version strings are valid PEP 440** — `0.1.0a1`,
  `0.1.0b1`, `1.0.0rc1`, `1.0.0`, no hyphens before any pre-release
  segment. It references `compatibility.md`'s 4-axis policy ("See
  `protocol/compatibility.md` for the authoritative definition of each —
  this document does not restate it") rather than restating it (INV-001).
  `ROADMAP.md`'s corrected release-progression sketch (`0.1.0a1`/
  `0.1.0b1`/`1.0.0rc1`) is likewise valid PEP 440.
- **`pyproject.toml` metadata**, confirmed present in the actual built
  wheel's `METADATA` (see TDD-001 reproduction above): `authors`,
  `[project.urls]` (all four), `keywords`, and every listed `classifier`.
- **Flow classification (FULL) is correctly justified** — this Change
  touches both Contract files, packaging configuration, a new executable
  CLI surface with new tests, and new CI workflow files, the same
  combination `discovery.md` cites as already classifying `CHG-0013`/
  `0015`/`0016`/`0017`/`0018` as FULL.
- **DEC-001's classification is defensible.** `architectural` class,
  `agent_with_review` authority: an implementation-shape choice
  (structured `DoctorCheck` vs. unstructured info line) within an already-
  approved Specification, with no `product`/`contract` Materiality
  trigger. The resolution correctly observes that `DoctorCheck`'s existing
  `warning`-status shape needed zero new plumbing — confirmed by reading
  `doctor.py`'s `_migration_advisory_checks` (18 lines, reuses `_check`
  and the existing `DoctorResult.passed` semantics unchanged).
  `DoctorResult.passed` (`all(check.status != "failed" for check in
  checks)`) confirms a `"warning"` status is genuinely non-blocking by
  construction, not merely by convention.
- **No schema file changed** (CON-002) — `git diff d489f1b..443678b
  --stat -- protocol/schemas/` and `-- protocol/specification.md` are both
  empty, confirmed directly.
- **Documentation Impact evaluation is accurate about its own stated
  scope** — `manifest.yml`'s `documentation.reason` names exactly
  `CHANGELOG.md` (PEP 440 correction, convention note),
  `ROADMAP.md` (version-string correction), the new ADR, `RELEASING.md`,
  and `CONTRIBUTING.md`'s one-line pointer — and each of those five is
  confirmed present in the diff. (R001 above is that this accurate
  self-description of a narrower scope than every prior Change's
  `CHANGELOG.md` treatment is itself the gap, not that the description
  misrepresents what was done.)
- **F-008 (RFC threshold) reasoning holds** — "Material Protocol Changes
  require RFC" (`.forge/contract/engineering.md`); this Change adds one
  additive Contract rule and CLI/CI tooling, not a Protocol semantic
  redefinition, matching the same no-RFC-needed precedent CHG-0015/0016/
  0018 already established for their own new Contract rules.
- **No historical Change invalidated.** `forge validate` reports no new
  finding against any of `CHG-0001`-`CHG-0018`; the six real `@1`
  provenance files remain valid and untouched, matching
  `compatibility.md`'s own "not deprecated" statement for `@1`.
- **No accidental publish (NFR-002).** Nothing in this Change's own
  commits creates a git tag, GitHub Release, or triggers `publish.yml` —
  confirmed no such action was taken (`git tag` unchanged, no Release
  exists to trigger it).

## Conclusion

Zero BLOCKER/MAJOR Findings. Two non-blocking MINOR Findings (a
`CHANGELOG.md` documentation-completeness gap, and a missing cheap
regression test for the version-sourcing fix) and one OBSERVATION (a
latent, currently-harmless fragility in the migration engine's exact
string-replace design). The Change's two highest-stakes claims — the
migration engine's genuine safety against this repository's own real
historical data, and the version-sourcing fix's genuine effect on a real
build — both hold under independent, hands-on adversarial verification,
not narrative acceptance. This Change is **PASS** and may proceed toward
Completion.
