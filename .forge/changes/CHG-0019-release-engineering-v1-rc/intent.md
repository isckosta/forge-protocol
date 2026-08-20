# Intent — Release Engineering & v1 Release Candidate (Infrastructure)

## Summary

Forge has never been packaged for real distribution: no PyPI publish
mechanism, no migration tooling, no release documentation, and the CLI's
own version string is duplicated in two places with no enforcement. This
Change builds the infrastructure ROADMAP.md's "Release Engineering & v1
Release Candidate" milestone requires — versioning consistency, a real
`forge migrate` mechanism with one genuine, safe migration case, a PyPI
publish workflow, release documentation, and package metadata — without
actually cutting a release. Publishing to PyPI, tagging a version, or
creating a GitHub Release is a public, shared-state, hard-to-reverse
action that requires its own separate, explicit authorization later, not
something a Change like this one performs on its own.

## Problem

Two Explore agents mapped the exact gaps (Discovery records the full
findings): `pyproject.toml`'s `version` field and `version.py`'s
`CLI_VERSION` are two independently hardcoded strings with zero
enforcement; no migration mechanism exists anywhere, despite six real
historical Changes in this repository still declaring the superseded
`forge/execution-provenance@1` schema for data that could safely (and,
per `compatibility.md`'s own text, losslessly) move to `@2`; no PyPI
publish workflow, OIDC config, or token reference exists anywhere; no
`RELEASING.md` or release runbook exists; `CHANGELOG.md` has never had a
released-version heading; and `ROADMAP.md`'s own release-progression
version strings (`0.1.0-alpha.1`) are not valid PEP 440.

## Desired Outcome

A human can, later, with full confidence: bump one version string in one
place, run `forge migrate --check`/`forge migrate` against any project
that needs it, follow `RELEASING.md`'s checklist, tag a release, and have
`publish.yml` build and publish it — all already built, tested, and
proven safe by this Change, before that human action is ever taken.

## Scope

- Single source of truth for `CLI_VERSION` (`pyproject.toml` reads it via
  `hatch.version` dynamic sourcing).
- `forge migrate` / `forge migrate --check`, covering the one real, safe,
  mechanically-verifiable migration case
  (`forge/execution-provenance@1` → `@2`), plus a `forge doctor` advisory.
- New Contract rule `C-075` (migration honesty — generalizing `CHG-0007`'s
  own truth-preserving migration precedent into a durable rule).
- `.github/workflows/publish.yml` (PyPI, OIDC trusted publishing, wheel +
  sdist) — written, never triggered.
- `verification.yml` cleanup (stale branch triggers removed, sdist
  coverage added).
- `RELEASING.md`, `pyproject.toml` metadata (`authors`/`urls`/
  `classifiers`/`keywords`), a `CHANGELOG.md` released-heading convention
  note.
- `ROADMAP.md`'s release-progression version strings corrected to PEP 440.

## Out of Scope

- Actually publishing anything to PyPI, GitHub Releases, or cutting a
  version tag.
- Migrating `forge/change@1` (explicitly forbidden by `compatibility.md`)
  or `forge/adapter-installation@1` (needs non-derivable external input).
- Registering a PyPI trusted publisher (a manual, out-of-band action on
  PyPI's own side).
- The ROADMAP's "End-to-End Examples & External Validation" milestone.

## Success Criteria

See `specification.md` for concrete Acceptance Criteria. At Intent stage,
success means: version consistency is enforced by construction, not
convention; a real, safe migration case works end to end against this
repository's own historical data (verified on a disposable copy, never
mutating genuine historical evidence); the publish workflow is complete
and correct but inert; and a human has everything needed to cut v1's
first real prerelease with no further engineering work.
