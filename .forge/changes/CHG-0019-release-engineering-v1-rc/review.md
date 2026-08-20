---
forge:
  artifact: review
  schema: 1
change: CHG-0019
status: passed
---
# Strict Review — CHG-0019

## Verdict

**PASS (final, Iteration 2 — `kind: resolution_verification`).** No
blocking Findings remain outstanding.

- **Iteration 1** (`kind: initial_review`) — **PASS**: 0 BLOCKER/MAJOR, 2
  MINOR (R001, R002), 1 OBSERVATION (O001).
- **Iteration 2** (`kind: resolution_verification`) — **PASS**: R001,
  R002, and O001 all verified resolved against actual repository state,
  not accepted from `resolution-001`'s own claim; no Out-of-Scope
  Mutation; 0 new material findings; 1 new non-blocking OBSERVATION
  recorded (O002, an unrelated latent Core-validation finding, recorded
  per C-050, out of this Iteration's own bounded authority per C-047).

Everything below this Summary down to the end of the original `##
Conclusion` is Iteration 1's verbatim historical record, except the
Summary table immediately below, which is restated in Raised/Outstanding
form to account for R001/R002/O001's resolution. Iteration 2 is appended
at the end of this file.

`protocol/policies/review.yml` sets `blocking: [blocker, major]`; none of
R001, R002, O001, or O002 was ever blocking. Both Iterations pass, and
this Change may proceed toward Completion.

**PASS (Iteration 1, `kind: initial_review`), as originally recorded.** No
BLOCKER or MAJOR Finding. 2 MINOR, 1 OBSERVATION — none blocking per
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

Counting semantics, stated explicitly since the Protocol does not fix them:
**Raised** is cumulative — every Finding ever recorded in this Review, in
the Iteration that recorded it. **Outstanding** is the state *after* the
final Iteration, and is what `manifest.yml`'s
`review.blockers`/`majors`/`minors`/`observations` carry.

| Severity | Raised (It. 1) | Raised (It. 2) | Raised total | Outstanding | Blocking |
| --- | --- | --- | --- | --- | --- |
| BLOCKER | 0 | 0 | 0 | 0 | yes |
| MAJOR | 0 | 0 | 0 | 0 | yes |
| MINOR | 2 | 0 | 2 | 0 | no |
| OBSERVATION | 1 | 1 | 2 | 1 | no |

R001 and R002 (MINOR, Iteration 1) and O001 (OBSERVATION, Iteration 1) are
resolved by `resolution-001` and verified in Iteration 2 — no longer
outstanding. O002 (OBSERVATION, Iteration 2) is a new, unrelated latent
finding, not targeted by any Resolution, and remains outstanding.

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

## Iteration 2 — PASS (`kind: resolution_verification`)

### Iteration 2 scope and authority

This Iteration is a **Resolution Verification**, not a second Initial
Review. Per `protocol/contract/engineering.md` C-047 and
`protocol/versions/2/specification.md` §10, its authority is bounded to
exactly three things:

1. R001, R002, and O001 — the three Findings `resolution-001` targets;
2. defects within `resolution-001`'s own Resolution Delta;
3. Out-of-Scope Mutation.

It is deliberately **not** a re-audit of `implementation-001`. Nothing in
Iteration 1's "Checked and found sound" section — the migration engine's
read-only/write-only separation, the `delegated_task` exclusion, the
three schema-family exclusion claims, the schema catalog cross-check,
TDD-001's build reproduction, the workflow YAML review, C-075's dual-file
parity, `RELEASING.md`'s PEP 440 strings, the Flow classification, or
DEC-001's classification — was re-litigated here. Re-opening any of that
is precisely what C-047 forbids.

### Iteration 2 execution independence

Executed cold, from committed repository state, in an Execution and
Execution Context distinct from `implementation-001`/`resolution-001`
(both `implementation-exec-chg0019-20260820-01` /
`implementation-context-chg0019-20260820-01`) and from `review-001`
(`review-exec-chg0019-20260820-7ef99eba` /
`review-context-chg0019-20260820-f8b709bb`). This session has no memory of
any of them and read Iteration 1 of this file, `provenance.yml`,
`manifest.yml`, and `protocol/versions/2/specification.md` §10-§11
directly. No claim in `resolution-001`'s own `provenance.yml` statement or
its commit message was accepted without independent reproduction against
the actual diff, the actual current source, and the actual test suite.
See `provenance.yml` record `review-002` for this execution's own
self-recorded provenance.

Subject: `resolution-001`, frozen at
`b6b570613e379d6919474240bf5a4bd36320fb1a` (revision
`chg-0019-resolution-001`). `HEAD` at the start of this Iteration is
`aa61c13`, whose only difference from the subject is `provenance.yml` (the
`resolution-001` record itself) — Change-local review-control metadata,
which the §5 effective-workspace freeze permits. `git status --porcelain`
was otherwise clean throughout this Iteration; every scratch/adversarial
fixture used below was built in a disposable directory outside this
repository, never inside `.forge/changes/`.

### Resolution Delta, computed independently — no Out-of-Scope Mutation

Computed per §11 as the committed diff between the immutable revision of
the Iteration immediately preceding this one (`review-001`'s subject,
`443678bc0ec7dbd9423d1e306416ebecdc65bdf3`) and this Iteration's own
subject (`b6b570613e379d6919474240bf5a4bd36320fb1a`) — both already-frozen
historical commits, not the current workspace — minus this Change's exact
`manifest.yml`, `provenance.yml`, and `review.md` paths:

```
$ git diff --name-only 443678b..b6b5706
.forge/changes/CHG-0019-release-engineering-v1-rc/manifest.yml
.forge/changes/CHG-0019-release-engineering-v1-rc/provenance.yml
.forge/changes/CHG-0019-release-engineering-v1-rc/review.md
CHANGELOG.md
src/forge_cli/migration.py
tests/unit/test_migration.py
tests/unit/test_packaging_version.py
```

Subtracting the three Change-local paths leaves exactly four:

| # | Resolution Delta path | Covered by declared `scope` |
| --- | --- | --- |
| 1 | `CHANGELOG.md` | yes |
| 2 | `src/forge_cli/migration.py` | yes |
| 3 | `tests/unit/test_migration.py` | yes |
| 4 | `tests/unit/test_packaging_version.py` | yes |

`resolution-001` declares exactly these same four paths as `scope`. The
two sets are **exactly equal** in both directions — no Resolution Delta
path is uncovered, and no declared `scope` entry is broader than the
Delta actually taken. **Out-of-Scope Mutation: none.** Consequently
`full_review_required` is `false` and this Iteration is eligible to be
`status: passed`.

### R001, re-checked against actual repository state — resolved

Not accepted from `resolution-001`'s own claimed description. Read
`CHANGELOG.md` directly: `## Unreleased` now has a `### Release
Engineering & v1 Release Candidate (Infrastructure)` subsection
(`grep -n "^##\|^###" CHANGELOG.md`, line 13, immediately above CHG-0018's
own `### Second Harness Adapter (Claude Code)` entry at line 61) with
`Added:`/`Fixed:`/`Known limitation` sub-groups, matching the exact shape
of every prior entry (compared directly against the Claude Code entry's
own `Added:`/`Fixed (generic Adapter Core...)` structure). The entry
substantively names `forge migrate`/`forge migrate --check`, the new
`forge doctor` `migration_available` advisory, `C-075`, `publish.yml`
(OIDC trusted publishing, no stored token, triggers only on a published
Release), `RELEASING.md`, the `pyproject.toml` metadata/dynamic-version
additions, the `verification.yml` stale-branch fix, and the ROADMAP PEP
440 correction — not a token one-line stub. R001 is resolved.

### R002, re-checked against actual repository state — resolved

Not accepted from `resolution-001`'s own claimed test description. Read
`tests/unit/test_packaging_version.py` in full: it loads the real
`pyproject.toml` via `tomllib`, asserts `dynamic == ["version"]` and no
static `version` key, then extracts `[tool.hatch.version]`'s actual `path`
and `pattern`, applies that exact `pattern` via `re.search` against the
real, current `src/forge_cli/version.py` content, and asserts the
extracted group equals the imported `CLI_VERSION` — plus a third test
applying the same real pattern to a synthetic changed string
(`CLI_VERSION = "9.9.9-test-only"`) to confirm the regex is a live
extraction, not one that merely happens to match today's literal value.

Ran it myself: `pytest -q` (below) shows all pass. To confirm this is a
genuine regression guard and not cosmetic, I read `pyproject.toml`'s
actual pattern (`CLI_VERSION = ["'](?P<version>[^"']+)["']`) and reasoned
through, then verified in a standalone Python REPL (not touching the real
`version.py`), two plausible regressions:

```
>>> re.search(pattern, 'CLI_VERSION: str = "0.1.0"\n')   # added type annotation
None
>>> re.search(pattern, 'CLI_VERSION=0.1.0\n')              # quotes dropped
None
>>> re.search(pattern, 'CLI_VERSION = "0.1.0.dev0"\n').group("version")  # real, current
'0.1.0.dev0'
```

Both plausible regressions make `match` `None`, which trips
`test_hatch_version_pattern_extracts_the_real_cli_version`'s `assert match
is not None`. This test would genuinely fail on the class of regression
R002 was raised against, not merely on paper. R002 is resolved.

### O001, re-checked against actual repository state — resolved, verified with my own independent adversarial fixture

Not accepted from `resolution-001`'s own claim or from the existing new
test's own assertion. Read `src/forge_cli/migration.py`'s current
`apply_migrations` directly: the bare `original.replace(_SOURCE_SCHEMA,
_TARGET_SCHEMA, 1)` is gone, replaced by `_SCHEMA_LINE_PATTERN =
re.compile(r"^schema: " + re.escape(_SOURCE_SCHEMA) + r"$", re.MULTILINE)`
and `_SCHEMA_LINE_PATTERN.subn(..., count=1)` — anchored (`^...$` with
`re.MULTILINE`) to a whole line that is *exactly* `schema:
forge/execution-provenance@1`, not a bare substring match anywhere in the
file. A `count != 1` guard skips the write entirely rather than risk a
partial/ambiguous rewrite.

Built my own fixture, independent of `tests/unit/test_migration.py`'s own
new `test_apply_migrations_only_touches_the_schema_key_not_a_prose_mention`,
in a disposable scratch directory outside this repository. Deliberately
more adversarial than the existing test: I put the prose mention of the
literal string `forge/execution-provenance@1` in a `note:` field **before**
the real `schema:` key line in the raw file text (the exact scenario
Iteration 1's O001 described as the latent risk — "a hypothetical...
`source.statement` prose happens to quote it textually before the actual
`schema:` line"), plus a second mention in a `statement:` field after it.
Called `find_candidates`/`apply_migrations` directly against a copy:

```
--- (original)
+++ (after apply_migrations)
@@ -4,7 +4,7 @@
   whole file (the bug O001 warned about) or correctly targets only the
   actual schema: key line.
-schema: forge/execution-provenance@1
+schema: forge/execution-provenance@2
 change: CHG-9999
 records:
```

Only the actual `schema:` key line changed; both the `note:` prose mention
(textually first in the file) and the `statement:` prose mention
(textually after the key) are byte-for-byte untouched. This is the exact
adversarial case the OBSERVATION warned about, constructed independently,
and it now behaves correctly. O001 is resolved.

### Regression check — the six real historical candidates, unaffected

`forge migrate --check` against this actual repository still reports
exactly the same six candidates as `review-001` found:
`CHG-0008-reviewer-resolver-separation`,
`CHG-0011-review-convergence-boundary`,
`CHG-0012-freeze-check-exempts-complete-changes`,
`CHG-0013-unresolved-decision-management`,
`CHG-0014-golden-path-codex-onboarding`,
`CHG-0015-delegated-agent-authority-and-side-effect-boundaries`.
`git status --porcelain` was empty immediately before and immediately
after running `--check`. The applying form of `forge migrate` was never
run against this repository's real `.forge/changes/` directory by this
Iteration, per the assignment's own constraint. This confirms
`resolution-001`'s O001 fix (a change to the rewrite step only) did not
alter `find_candidates`'s candidate selection, which none of R001/R002/O001
touch.

### Full suite, reproduced independently

```
$ python -m pytest -q
524 passed in 40.33s
```

520 baseline (matching `review-001`'s own independently-reproduced figure)
plus 4 new: 1 in `tests/unit/test_migration.py`
(`test_apply_migrations_only_touches_the_schema_key_not_a_prose_mention`)
and 3 in the new `tests/unit/test_packaging_version.py` — matching
`resolution-001`'s claimed count exactly, reproduced independently rather
than accepted from its statement.

### New material findings: 0

No defect was found in `resolution-001`'s own Resolution Delta. All three
targeted Findings (R001, R002, O001) are genuinely resolved against actual
repository state, confirmed by independent reproduction and an adversarial
fixture built from scratch, not by trusting the Resolution's own
narrative. `new_material_findings: 0`.

### O002 — OBSERVATION — unrelated latent finding, recorded per C-050 — same pre-existing Core gap already documented in CHG-0018's Iteration 2 (R002 there)

**Not targeted by `resolution-001`, not inside the Resolution Delta, and
not counted toward this Iteration's `new_material_findings`** (C-047
scopes this Iteration's authority to R001/R002/O001, the Resolution Delta,
and Out-of-Scope Mutation; C-050 requires an unrelated Finding discovered
incidentally be recorded, not discarded, and not treated as license to
re-audit further). Recorded here because it is real, demonstrated, and
would otherwise go unrecorded for this Change specifically — even though
it is the *same* Core defect, not a new one.

**Problem:** `forge validate` currently exits 2 against this real
repository:

```
$ forge validate
C-026 [.forge/changes/CHG-0019-release-engineering-v1-rc/manifest.yml]
C-026 review subject changed after its immutable revision freeze; create
new subject provenance.
```

This is the identical root cause CHG-0018's own review.md Iteration 2
(R002 there) already documented and recorded independently for that
Change: `_validate_protocol2_review_provenance`
(`src/forge_cli/validation/__init__.py:349`) checks each bound Iteration
in `review.iterations` in isolation against its own frozen subject commit.
`review-001` (subject `implementation-001`, frozen at `443678b`, `status:
passed`) is only satisfied if nothing outside this Change's own
`manifest.yml`/`provenance.yml`/`review.md` changed since `443678b` — but
`resolution-001` (`b6b5706`) necessarily changed real code
(`CHANGELOG.md`, `migration.py`, two test files) after that freeze, which
is exactly what §10-§11's two-Iteration lifecycle (Iteration 1 passed on
non-blocking Findings, Resolution, `resolution_verification` Iteration 2
verifying it) legitimately permits. Core's per-Iteration freeze loop has
no notion of "this earlier Iteration's subject freeze is properly
superseded by a later, correctly-bound `resolution_verification`
Iteration" — an implementation gap in Core, not a Specification violation
by this Change's own artifacts.

**Evidence, reproduced independently:** isolated the variable with
`git checkout <ref> -- <path>` (restored cleanly afterward, confirmed via
`git status --porcelain`): resetting only this Change's directory to its
state at `abe8817` (immediately after `review-001` was recorded, `status:
passed`, no `resolution-001`/`review-002` yet) while `HEAD`'s real code
remained at its current, post-Resolution state reproduces the exact same
`C-026` exit 2 — confirming the finding already existed the moment
`resolution-001`'s code commit (`b6b5706`) landed, before `resolution-001`'s
own provenance record or this Iteration's `review-002` record were ever
written. Not caused by anything added by this Iteration.

**Impact:** Non-blocking (OBSERVATION only per this Iteration's own bounded
authority; `forge validate`'s C-026 failure is itself outside blocking
severity classes for a Resolution Verification's judgment here, and in any
case this is the same already-known, already-recorded Core gap, not a new
one requiring separate remediation tracking — CHG-0018's own R002 already
carries that responsibility for Core). Recorded for completeness per
C-050; not counted toward `new_material_findings` (unrelated to R001/R002/
O001, and not newly discovered — merely newly re-demonstrated for this
Change).

## Iteration 2 Conclusion

Zero BLOCKER/MAJOR Findings across both Iterations. R001, R002, and O001
are verified genuinely resolved against actual repository state — not
accepted from `resolution-001`'s own narrative — including an independent
adversarial fixture for O001 built from scratch that specifically
reconstructs the exact scenario the OBSERVATION warned about. The
Resolution Delta, computed independently, exactly matches
`resolution-001`'s declared `scope` in both directions: **no Out-of-Scope
Mutation**. `new_material_findings: 0`. One unrelated, non-blocking
OBSERVATION (O002) is recorded per C-050 — the same pre-existing Core
validation gap CHG-0018's own Iteration 2 already documented, not a defect
in this Resolution. This Change is **PASS (final)** and may proceed toward
Completion.
