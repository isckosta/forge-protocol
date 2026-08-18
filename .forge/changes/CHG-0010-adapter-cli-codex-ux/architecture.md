---
forge:
  artifact: architecture
  schema: 1
change: CHG-0010
status: approved
---

# Architecture — Adapter CLI and Codex Installation UX

## Architectural objective

Expose the existing Adapter Core as a complete, safe product workflow without
placing Harness policy in CLI handlers or allowing generated Codex files to
become semantic authority.

## Runtime composition

```text
Typer adapter commands
        ↓
packaged registry composition
        ↓
generic AdapterService ─────→ configuration / installation state / snapshots
        ↓
HarnessDriver protocol
        ↓
CodexDriver ────────────────→ effective Forge inputs / projection / limitations
        ↓
generic planner
        ↓
human-readable AdapterPlan
        ↓ explicit install or update only
generic safe publisher
```

The CLI translates domain results and errors into text and exit codes. It does
not calculate ownership, drift, compatibility, target precedence, or Harness
projection content.

## Package boundaries

```text
src/forge_cli/
  adapter_cli.py                 # Typer command group and error translation
  adapters/
    registry.py                  # generic immutable driver registry
    configuration.py             # generic schema-backed user configuration
    repository.py                # read-only record/artifact snapshots
    service.py                   # generic use-case orchestration
    diagnostics.py               # generic findings/check result models
    formatting.py                # deterministic human-readable output
    plan.py                      # operation vocabulary, including UNCHANGED
    planner.py                   # ownership-aware desired/current decisions
    publisher.py                 # atomic create/update/delete/record boundary
    codex/
      driver.py                  # Codex implementation of HarnessDriver
      projection.py              # valid skill resources
      targets.py                 # explicit/config/evidence resolution
      resources/
        adapter.yml
        capabilities.yml
        skills/workflow.md
```

Generic modules may depend on a structural `HarnessDriver` protocol but cannot
import Codex types. The application composition root registers `CodexDriver`.

## Registry and driver interface

`AdapterRegistry` is built from installed drivers and rejects duplicate ids.
It returns stable id ordering and an exact-id lookup. Runtime discovery is
package-local and performs no entry-point, filesystem, or network scan in v1.

Conceptual driver surface:

```python
class HarnessDriver(Protocol):
    manifest: AdapterManifest
    default_target: str | None

    def project(self, inputs: EffectiveAdapterInputs) -> ProjectionResult: ...
```

`ProjectionResult` contains generic `ProjectedArtifact` values, sorted
limitations, and an `AdapterRepresentation` for conformance. Codex-specific
assessment occurs before conversion to these generic values.

## Configuration

Adapter configuration is a user-owned input:

```yaml
schema: forge/adapter-configuration@1
adapter: codex
target: .agents/skills/forge
```

It lives at `.forge/adapters/<id>/config.yml`, has a bundled JSON Schema, and is
written atomically only by an explicit `configure` command. The target is
repository-relative and passes the same cross-platform path rules as generated
artifacts. Unknown keys are rejected.

Target precedence is explicit CLI option, configuration, then the driver's
packaged evidence-backed default. No resolved target is a domain failure for
operations that require publication.

## Effective Forge inputs

The service validates `.forge/forge.yml`, reads its Protocol id, resolves every
enabled project Flow against the packaged canonical Flow, and composes the
canonical Engineering Contract with the optional project extension. Inputs are
read once per operation and normalized into stable id order.

Codex renders:

```text
.agents/skills/forge/
  SKILL.md
  references/
    engineering-contract.md
    flows/
      fast.yml
      full.yml
      standard.yml
```

Only enabled project Flows are emitted. `SKILL.md` has valid frontmatter and
instructs Codex to classify work, resolve the effective Flow, preserve TDD and
review Gates, and treat Forge repository sources as authoritative.

## Snapshot and planning model

The repository reader loads the optional installation record and observes all
desired plus previously recorded paths. It records existence and content
digests but performs no mutation.

`OperationIntent.UNCHANGED` distinguishes an intact Forge-owned desired file
from `PRESERVE`, which retains a user-owned artifact without ownership proof.
For a recorded desired path:

```text
observed == recorded == desired  -> UNCHANGED
observed == recorded != desired  -> UPDATE
observed != recorded             -> CONFLICT / drift
```

For an unrecorded desired path, absence produces `CREATE`; presence produces
`CONFLICT`, even when bytes equal desired output. Previously recorded paths no
longer desired produce `DELETE_GENERATED` only when observed equals recorded.

Plans remain immutable and sorted by path, ownership, and intent. Plans include
all desired generated artifacts when building the next installation record,
including `UNCHANGED` files.

## Install and update state machines

Install has three allowed outcomes:

```text
no record + conflict-free CREATE plan -> publish and record
current record + entirely UNCHANGED   -> successful no-op
other record/state                    -> typed domain failure
```

Update requires a valid existing record. A record for the same Adapter with an
older version is valid update input; incompatible identity, unsafe path, or
unreadable state is stale state. Drift blocks the complete update.

Publisher preflight validates every operation before the first mutation.
Applied create/update/delete operations retain rollback material. The new
installation record is atomically replaced only after artifacts succeed. Any
failure restores artifacts and the record byte-for-byte. Empty directories are
not an ownership unit and need not be removed.

## Validation and diagnostics

The service returns domain results rather than printing. Validation converts
invalid configuration, compatibility, installation, path, drift, and
conformance conditions into deterministic failures. Doctor evaluates the same
boundaries as ordered PASS/FAIL/WARN checks and adds actionable remediation.
Limitations are WARN and never become enforcement claims.

`plan`, `validate`, and `doctor` call only read-side service methods.
`--dry-run` routes to planning and never reaches the publisher.

## Error boundary

Expected failures are typed domain exceptions with stable codes. The Adapter
CLI maps domain failures to exit `2`, reuses Git/environment exit `3`, and
delegates unexpected exceptions to the existing exit `70` boundary. Error text
includes the safe next action but does not expose tracebacks by default.

## Distribution and offline behavior

The wheel contains Adapter descriptors, capability evidence, skill templates,
Protocol schemas, Flows, and Contract sources. Registry creation and all
service operations use `importlib.resources` and repository files only. Vendor
URLs are release evidence, not runtime dependencies.

## Security

- all target and generated paths are normalized repository-relative POSIX paths;
- absolute, traversal, backslash, colon-ambiguous, NUL, and symlink-traversing
  paths are rejected;
- content equality without a matching record never grants ownership;
- preflight completes before mutation;
- drift blocks the whole operation;
- deletion requires exact prior digest proof;
- no default resolves outside `.agents/skills/forge` in the project repository.
