# Architecture — Release Engineering & v1 Release Candidate (Infrastructure)

## Solution Summary

Six independent, mostly-decoupled pieces: (1) a hatch dynamic-version
source; (2) a new `migration.py` module + `forge migrate`/`forge migrate
--check` CLI commands; (3) one new `DoctorCheck` (warning-status,
non-blocking); (4) Contract `C-075`; (5) `publish.yml` + `verification.yml`
cleanup; (6) `RELEASING.md`/`pyproject.toml` metadata/doc corrections.
None touches Protocol schemas or existing Gate semantics.

## DEC-001 — `forge doctor`'s migration advisory shape

**Class**: `architectural`. **Authority**: `agent_with_review`.

**Question**: a new structured `DoctorCheck`, or an unstructured info
line?

**Resolution**: a new `DoctorCheck` with `status="warning"`. `DoctorCheck`
already has exactly this shape (`id`, `status`, `message`), `DoctorResult.
passed` already treats anything other than `"failed"` as non-blocking,
and `app.py`'s existing label map already renders `"warning"` as `WARN`
— the advisory needs zero new plumbing, only one more check appended by
`diagnose()`. Building a separate, unstructured "info line" mechanism
would duplicate machinery that already exists and already does exactly
this job (adapter capability-limitation checks are `WARN` today for the
same reason: real, non-blocking, worth surfacing). **Resolved via**:
`autonomous_decision`, confidence high — decisive once `doctor.py`'s
actual shape was read, not assumed.

## Content Shape

### `pyproject.toml`

```toml
[project]
dynamic = ["version"]
# version = "..." removed

[tool.hatch.version]
path = "src/forge_cli/version.py"
pattern = "CLI_VERSION = [\"'](?P<version>[^\"']+)[\"']"

[project.urls]
Homepage = "https://github.com/isckosta/forge-protocol"
Repository = "https://github.com/isckosta/forge-protocol"
Issues = "https://github.com/isckosta/forge-protocol/issues"
Changelog = "https://github.com/isckosta/forge-protocol/blob/main/CHANGELOG.md"

[[project.authors]]
name = "Israel Costa"
```

`classifiers`/`keywords` added per FR-009. No existing field removed
except the static `version` (replaced by `dynamic`).

### `src/forge_cli/migration.py`

Mirrors `doctor.py`'s shape: a `MigrationCandidate` dataclass
(`change_id`, `path`), a pure `find_candidates(project_root) ->
tuple[MigrationCandidate, ...]` (reads every `.forge/changes/*/
provenance.yml`, parses YAML directly — no need to route through the
generic `execution-provenance` loader, since this is deliberately a
narrow, single-purpose scan, not a general provenance-loading path;
loading through the full loader would require it to already be schema-
valid, whereas a `--check` scan must also tolerate finding nothing to do
without asserting the file is otherwise perfect), and `apply_migrations
(project_root, candidates) -> tuple[MigrationResult, ...]` performing the
one-line `schema:` rewrite via exact string replacement of the declared
value (not a full YAML re-serialization, to guarantee no other byte
changes — re-serializing through `yaml.safe_dump` could reorder keys or
change quoting style, which would violate "no other byte in the file
changes").

### `forge migrate` / `forge migrate --check` (new `app.py` commands)

Same `_project_root()`/`_internal_error()` helpers `validate`/`doctor`
already use. `--check` prints one line per candidate or "No migration
available."; the bare command applies and prints one line per file
changed, or "Nothing to migrate." Both exit 0 — this is advisory
tooling, not a Gate.

### `.github/workflows/publish.yml`

```yaml
on:
  release:
    types: [published]
permissions:
  id-token: write
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: python -m pip install --upgrade pip build
      - run: python -m build   # wheel + sdist
      - name: Smoke-test both artifacts offline
        run: |
          # mirrors verification.yml's existing isolated-venv pattern,
          # against dist/*.whl AND dist/*.tar.gz
      - uses: pypa/gh-action-pypi-publish@release/v1
```

Triggers only on an actual published GitHub Release — inert until one
exists, which this Change does not create.

## Contract and Specification Placement

`C-075` appended to both `protocol/contract/engineering.md` and
`protocol/versions/2/contract/engineering.md` (next free number after
`C-074`, dual-file convention already established). No
`protocol/specification.md` change — migration is CLI/Core tooling
behavior, not a Protocol semantic; §34-38-style Adapter-contract
sections don't apply here, and no existing section speaks to migration
at all (confirmed absent in Discovery).

## Compatibility

Purely additive. `pyproject.toml`'s `dynamic` version sourcing produces
the identical string `CLI_VERSION` already holds — zero behavior change
for `forge version` today. No schema change. No historical Change
invalidated; the six real `@1` provenance files remain valid until a
human explicitly runs `forge migrate` against them (not run by this
Change).

## Risks

- **A future third schema-version pair might not fit this narrow,
  single-family `migration.py` design.** Not mitigated preemptively —
  the same "wait for a second real, safe case" discipline already used
  elsewhere in this repository (e.g. `CHG-0018`'s DEC-003) applies: this
  Change builds exactly one real, justified case, not a speculative
  general migration framework.
- **`publish.yml` could theoretically be accidentally triggered** if
  someone publishes a GitHub Release before PyPI trusted-publishing is
  registered, causing a harmless failed run (OIDC exchange fails, no
  package is published, no damage) rather than a silent success — this
  is the safe failure mode, not swallowed or auto-retried.

## What This Change Deliberately Does Not Build

- Migration for `forge/change@1`, `forge/adapter-installation@1`, or
  `forge/policy/review@1` (Discovery/Specification Review explain why
  each is excluded, for three different reasons).
- Any actual PyPI publication, GitHub Release, or version tag.
- PyPI trusted-publisher registration (out-of-band, PyPI-side).
- A general-purpose, extensible migration framework beyond the one real
  case this Change has evidence for.
