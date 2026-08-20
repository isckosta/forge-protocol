# Specification — Release Engineering & v1 Release Candidate (Infrastructure)

## Summary

Single source of truth for `CLI_VERSION`; a real `forge migrate`/`forge
migrate --check` mechanism covering the one safe migration case
(`forge/execution-provenance@1` → `@2`); a new Contract rule (`C-075`,
migration honesty); a PyPI publish workflow (written, inert);
`verification.yml` cleanup; `RELEASING.md`; `pyproject.toml` metadata;
`CHANGELOG.md` convention note; `ROADMAP.md` version-string correction.
No real release is cut.

## Classification

**Flow: FULL.** See `discovery.md` "Flow Classification Finding".

## Functional Requirements

### FR-001 — Single source of truth for CLI version

`pyproject.toml` declares `dynamic = ["version"]` and
`[tool.hatch.version]` reads `CLI_VERSION` out of
`src/forge_cli/version.py` via a regex pattern. `forge version`'s output
and `python -m build`'s produced artifact version are identical for any
value of `CLI_VERSION`, verified by changing it and rebuilding.

### FR-002 — `forge migrate --check`

Scans `.forge/changes/*/provenance.yml` for `schema:
forge/execution-provenance@1` whose `records[].role` never includes
`delegated_task`. Reports each candidate by Change id and path, or "no
migration available" if none. Exit 0 in both cases (informational, not a
validation failure).

### FR-003 — `forge migrate`

Applies the same scan, then rewrites exactly the `schema:` field to
`forge/execution-provenance@2` for each candidate — no other byte in the
file changes. Idempotent: a second run reports/changes nothing.
Explicitly refuses (does not silently skip, does not attempt) any
`provenance.yml` containing a `delegated_task` record, and never touches
`forge/change@*`, `forge/adapter-installation@*`, or `forge/policy/
review@*` files at all — this Change's `forge migrate` recognizes
exactly one schema family. `forge/policy/review@1`/`@2` (found in
Specification Review, see `specification-review.md` SR-001) is not a
per-project user-data instance at all — it is a canonical,
Protocol-version-selected resource (mirroring how Contract/Flow text is
already resolved per declared `protocol` integer), and no code in this
repository reads or validates a project's own `.forge/policies/review.yml`
against either schema today — there is no live consumer to migrate
*for*.

### FR-004 — `forge doctor` migration advisory

If any `forge migrate --check` candidate exists in the current project,
`forge doctor` prints one additional informational line naming `forge
migrate --check` as the next step. Non-blocking; does not change
`forge doctor`'s exit code.

### FR-005 — Contract `C-075`

A migration MUST NOT fabricate, infer, or reconstruct data absent from
the instance being migrated; a transformation requiring invented
information MUST be refused, not approximated. Added to both
`protocol/contract/engineering.md` and
`protocol/versions/2/contract/engineering.md`.

### FR-006 — PyPI publish workflow

`.github/workflows/publish.yml`: triggers only on `release: {types:
[published]}`; builds wheel and sdist; re-runs an offline smoke check
against both; publishes via OIDC trusted publishing
(`pypa/gh-action-pypi-publish`, `permissions: id-token: write`), no
stored token. This Change does not create a Release, so this workflow
never runs as a side effect of this Change landing.

### FR-007 — `verification.yml` cleanup

Stale branch triggers (`chore/chg-0001-verification`,
`feat/chg-0002-harness-adapter-foundation` — both branches no longer
exist) removed. sdist build + `pip install`-from-sdist smoke check added
alongside the existing wheel-only check.

### FR-008 — `RELEASING.md`

Version scheme (PEP 440, per `discovery.md`'s correctness argument), a
pointer (not a restatement — INV-001) to `compatibility.md`'s 4-axis
policy, and the actual manual release checklist, explicitly marked as
a human-executed process this Change enables but does not run.

### FR-009 — `pyproject.toml` metadata

`authors`, `[project.urls]` (`Homepage`/`Repository`/`Issues`/
`Changelog`, pointing at the real `github.com/isckosta/forge-protocol`
remote), `classifiers` (`Development Status :: 3 - Alpha`, supported
Python versions, License, Intended Audience, Topic), `keywords`.

### FR-010 — `CHANGELOG.md` convention note

One line documenting the released-version heading shape
(`## [0.1.0a1] - YYYY-MM-DD`) directly under the existing header prose.
No version section is actually added.

### FR-011 — `ROADMAP.md` version-string correction

`0.1.0-alpha.1`/`0.1.0-beta.1`/`1.0.0-rc.1` corrected to `0.1.0a1`/
`0.1.0b1`/`1.0.0rc1` in the Release progression sketch.

## Non-functional Requirements

### NFR-001 — Migration honesty in practice, not only in Contract text

`forge migrate`'s own implementation is checked against C-075 directly:
no code path defaults, infers, or synthesizes a value for any field the
source instance lacks.

### NFR-002 — No accidental publish

Nothing in this Change's own commits, CI config, or Change lifecycle
creates a git tag, a GitHub Release, or triggers `publish.yml`.

### NFR-003 — Backward compatibility

Every existing historical Change (`CHG-0001`–`CHG-0018`) remains valid.
`forge/execution-provenance@1` files this Change does not touch (this
repository's own, until a human runs `forge migrate`) remain valid,
matching `compatibility.md`'s own "not deprecated" statement for `@1`.

## Constraints

### CON-001 — No new Protocol integer

Nothing here weakens or redefines an existing Protocol invariant.

### CON-002 — No schema change

No file under `protocol/schemas/` changes. `forge migrate` targets
existing schemas' own already-published compatibility, not a new one.

### CON-003 — Historical validity

`forge validate`/`forge doctor` report no new finding against any
historical Change.

### CON-004 — Never mutate genuine historical evidence

Any test exercising migration against this repository's own real
`CHG-0008`/`0011`–`0015` `provenance.yml` files operates read-only or
against a copied fixture; none is rewritten in place as a side effect of
testing.

### INV-001 — No duplicated normative authority

`RELEASING.md` references `compatibility.md`'s versioning policy; it
does not restate it.

## Acceptance Criteria

- **AC-001**: changing `CLI_VERSION` in `version.py` and running `python
  -m build` produces a wheel/sdist whose filename and internal metadata
  both reflect the new value, with no edit to `pyproject.toml` itself.
- **AC-002**: `forge migrate --check` run against this repository reports
  exactly the six real `@1` provenance files as candidates.
- **AC-003**: `forge migrate` run against a disposable copy of this
  repository rewrites exactly those six `schema:` lines to `@2`, changes
  no other byte in any of the six files, and `forge validate` still
  passes afterward.
- **AC-004**: `forge migrate --check`/`forge migrate` run against a
  fixture containing a `delegated_task` record leaves that file
  untouched and does not list it as a candidate.
- **AC-005**: `forge doctor` prints the migration advisory only when a
  candidate exists, and its exit code is unaffected either way.
- **AC-006**: `C-075` present, byte-identical (modulo wrapping) in both
  Contract files.
- **AC-007**: `publish.yml` is valid workflow YAML, never executes as a
  side effect of any commit in this Change, and its OIDC/trusted-
  publishing configuration is present with no stored token.
- **AC-008**: `pyproject.toml`'s new metadata fields are present and
  valid (`python -m build` succeeds; the built wheel's `METADATA` file
  contains the new fields).
- **AC-009**: `RELEASING.md` exists, references `compatibility.md`
  rather than restating it, and its version strings are valid PEP 440.
- **AC-010**: `CHANGELOG.md`/`ROADMAP.md` reflect this Change at
  Completion; no historical Change is invalidated.

## Unresolved Decisions

None `product`/`contract` class. One `architectural` question
(`forge doctor` advisory shape) resolved at Architecture — see
`discovery.md`.

## Out of Scope

- Actually cutting a release, tag, or PyPI/GitHub publication.
- Migrating `forge/change@1` or `forge/adapter-installation@1`.
- PyPI trusted-publisher registration.
- The ROADMAP's "End-to-End Examples & External Validation" milestone.

## Traceability

Populated in `traceability.yml` at Plan/Tasks stage onward.
