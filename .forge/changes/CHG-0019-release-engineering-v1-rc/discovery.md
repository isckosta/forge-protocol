# Discovery — Release Engineering & v1 Release Candidate (Infrastructure)

## Executive Summary

Two Explore agents mapped the entire distribution/versioning/migration
surface. Findings are summarized in `intent.md`'s Problem section and the
originating plan's Context; this document adds the exact evidence and
resolves the one real open question (PEP 440 vs. hyphenated version
strings) with a correctness argument, not a preference.

## Repository State at Investigation Time

HEAD: `d489f1b` (`docs(chg-0018): Completion`). `docs/adr/` highest number
`0016`; next free is `0017`. `protocol/contract/engineering.md` ends at
`C-074`; next free is `C-075`.

## Version duplication, confirmed structurally

`git log --all --oneline | grep -iE "version|release"` shows exactly two
relevant commits (`7a72e58`, `0439080`): the first created
`src/forge_cli/version.py` with `CLI_VERSION`/`PROTOCOL_ID`/
`PROTOCOL_DISPLAY_VERSION`/`SUPPORTED_PROTOCOL_IDS`; the second made
`app.py` import from it instead of a local literal. Neither ever touched
`pyproject.toml`'s own `version = "0.1.0.dev0"` field — confirmed by
`tomllib.load` showing it as a fully independent, static string, with no
`dynamic` declaration anywhere in the file.

## Migration: the real candidate, and the two real non-candidates

Full schema-pair diff (four families have more than one version:
`forge/change`, `forge/adapter-installation`, `forge/execution-provenance`,
`forge/policy/review`):

- **`forge/execution-provenance@1` → `@2`**: a strict superset for every
  record whose `role` is not `delegated_task` — `compatibility.md`'s own
  CHG-0015 entry states "`@1` itself is unchanged and remains valid."
  Real, live instances exist today: `CHG-0008`, `CHG-0011` through
  `CHG-0015`'s `provenance.yml` files all still declare `@1`. This is
  the one case where "old data + a trivial default = valid new data" is
  actually true, verified by direct schema-file comparison, not assumed.
- **`forge/change@1` → `@2`**: **not** a migration candidate.
  `compatibility.md` is explicit: "Previously valid conforming Protocol 1
  projects and completed Change instances MUST remain valid... `forge/
  change@1` preserves its historical shape and meaning," and "MAY retain
  completed historical `forge/change@1` Changes without retroactive
  migration or fabricated provenance." `forge validate` already gates
  this correctly today (an *active* `@1` Change under `protocol: 2` is
  rejected; a *completed* one is left alone) — `forge migrate` must not
  duplicate or second-guess that gate.
- **`forge/adapter-installation@1` → `@2`**: schema-superset-safe in
  principle (the only new field is `publication.root`) but has no
  derivable default — no live installation record exists in this
  repository to even drive a design against. Deferred; would need a
  `--publication-root` flag or a re-run of installation, not a pure
  rewrite, and building it now would be speculative.
- **`forge/policy/review@1` → `@2`**: **not a migration case at all**,
  found while checking whether a fourth schema pair had been missed
  (Specification Review SR-001). Unlike the three pairs above, this one
  is not a per-project mutable data instance — `protocol/policies/
  review.yml` (`@1`) and `protocol/versions/2/policies/review.yml`
  (`@2`) are canonical, Protocol-version-selected resources, the same
  pattern already used for Contract/Flow text. Confirmed by grep that
  **no code anywhere in `src/forge_cli/` reads or validates a project's
  own `.forge/policies/review.yml` against either schema** — the file
  this repository's own `forge init` copied is inert, unconsulted by any
  Core logic, so there is no live consumer a migration would even serve.
  Out of scope for a different reason than the other two: not "needs
  external input," but "there is nothing here to migrate."

No code anywhere today performs an actual rewrite between schema
versions — `state.py` and `validation/__init__.py` both only branch on
whichever schema string is already present. The one real historical
precedent for a mechanical migration is `CHG-0007`'s own one-off cleanup
of pre-catalog `CHG-0001`–`CHG-0005` manifests into `forge/change@1`
conformance (never fabricating missing data — CHG-0005's missing TDD
detail was recorded as an explicit exception, not invented). This
Change's `forge migrate` generalizes that same discipline into a
reusable mechanism, not a new philosophy.

## PEP 440 vs. hyphenated version strings — resolved, not a preference

`ROADMAP.md`'s release-progression sketch uses `0.1.0-alpha.1` /
`0.1.0-beta.1` / `1.0.0-rc.1`. PEP 440 (the version-string standard `pip`/
`build`/`hatchling` all parse against) does not use a hyphen before a
pre-release segment; its normalized spellings are `0.1.0a1`, `0.1.0b1`,
`1.0.0rc1`. `pip`/`packaging` will *normalize* a hyphenated form on
input in many cases, but `pyproject.toml`'s own `version` field (and this
Change's `hatch.version` dynamic sourcing from `version.py`) must contain
a string `packaging.version.Version` parses cleanly, and PyPI's own
display/sort behavior depends on canonical form. This is a factual
correction, resolved in Specification, not an Unresolved Decision — no
Requirement, public contract, or invariant is actually in tension; the
ROADMAP's original prose simply predates checking the exact grammar
against the tooling that will consume it.

## No existing Release Engineering ADR/RFC

`docs/adr/` (16 entries) and `docs/rfcs/` (2 entries) contain nothing on
versioning, release process, or migration. `protocol/compatibility.md` is
the closest adjacent normative document (4-axis versioning, deprecation
policy) and needs no change — this Change's new ADR sits beside it, not
inside it.

## Flow Classification Finding

Touches the Contract (new `C-075`, both files), packaging configuration,
new executable CLI surface (`forge migrate`) with new tests, and new CI
workflow files. Same combination class that classified
`CHG-0013`/`0015`/`0016`/`0017`/`0018` as **FULL**.

## Documentation Impact Signal (preliminary)

Expected: `CHANGELOG.md`, `ROADMAP.md` (status flip + version-string
correction), new ADR-0017, new `RELEASING.md`. `CONTRIBUTING.md` may gain
a one-line pointer to `RELEASING.md` — confirmed at Documentation Impact
evaluation.

## Open Questions Requiring Decision

None `product`/`contract` class. One `architectural` question, resolved
at Architecture (not here): whether `forge doctor`'s migration advisory
should be a new named check (`AdapterCheck`-shaped) or a lighter,
unstructured info line — Architecture owns this, informed by reading
`doctor.py`'s actual result-aggregation shape first.
