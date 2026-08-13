---
forge:
  artifact: specification
  schema: 1
change: CHG-0008
status: approved
review:
  iterations: 1
---

# Specification — Adapter CLI and Codex Installation UX

## Public command contract

### FR-001 — Adapter command group

Forge MUST expose `adapter list`, `configure`, `plan`, `install`, `validate`,
`doctor`, and `update` as infrastructure commands. It MUST NOT add lifecycle
execution commands.

### FR-002 — Packaged discovery

`adapter list` MUST discover Adapters from the installed Forge distribution,
operate without network access, and report stable Adapter id, version, Harness,
Protocol interval, compatibility, and repository installation state.

### FR-003 — Adapter selection

Every Adapter-specific command MUST reject an unknown Adapter with
`E_FORGE_ADAPTER_UNKNOWN` and MUST NOT mutate repository state.

### FR-004 — Project prerequisite

Commands other than `adapter list` MUST resolve the Git repository root and
require a valid initialized Forge project before Adapter-specific evaluation or
mutation.

## Configuration and target resolution

### FR-005 — Adapter configuration

`adapter configure <adapter>` MUST validate and atomically write the user-owned
`.forge/adapters/<adapter-id>/config.yml`. Codex configuration MUST support a
repository-relative publication `target` and MUST reject unsafe paths.

### FR-006 — Target precedence

Codex target resolution MUST use, in order: an explicit command option, the
Adapter configuration file, then packaged evidence. The packaged Codex default
MUST be `.agents/skills/forge`.

### FR-007 — Repository scope

Default Adapter operations MUST remain inside the resolved Git repository and
MUST NOT write to `.codex/`, a home directory, or another global location.

## Planning and representation

### FR-008 — Effective Forge input

Codex planning MUST derive its representation from the validated project
configuration, enabled canonical project Flows, effective Engineering Contract,
packaged Codex descriptor/evidence, installation record, and observed
repository state.

### FR-009 — Valid Codex skill

The Codex projection MUST produce a valid repository skill rooted at the
resolved target. It MUST include `SKILL.md` with stable name/description and
Forge workflow instructions plus deterministic references for the effective
Engineering Contract and enabled canonical Flows.

### FR-010 — Authority preservation

Every projection MUST state that repository-native Forge sources remain
authoritative. Removing all generated Adapter artifacts MUST NOT remove or
alter canonical Forge state.

### FR-011 — Visible deterministic plan

`adapter plan` MUST be read-only and print stably ordered operations, ownership,
limitations, and conflicts. `install` and `update` MUST compute and emit the
same plan before attempting publication. `install --dry-run` MUST not mutate
and MUST be operationally equivalent to planning an installation.

### FR-012 — Protocol compatibility

Planning, installation, validation, and update MUST check the project's
Protocol against the Adapter's half-open compatibility interval before any
mutation.

## Installation, idempotence, and ownership

### FR-013 — Safe first installation

Given no installation record and no target collision, `adapter install` MUST
publish the complete projection through the generic safe publisher and
atomically write its installation record.

### FR-014 — No silent adoption

An existing target artifact without matching Forge ownership evidence MUST be
a collision even when its bytes equal the desired projection. Forge MUST NOT
silently adopt or overwrite it.

### FR-015 — Idempotent installation

Repeating `adapter install` for the installed Adapter version with identical
configuration, desired projection, and intact generated state MUST succeed as a
true no-op and MUST NOT rewrite generated files or the installation record.

### FR-016 — Installation version boundary

`install` MUST reject a different installed Adapter version with
`E_FORGE_ADAPTER_ALREADY_INSTALLED` and direct the user to `update`. Update MUST
require a valid existing installation record.

### FR-017 — Ownership-aware update

`adapter update` MAY replace a Forge-owned artifact only when its observed
digest matches the prior installation record. User-owned artifacts MUST be
preserved and unsupported shared merges MUST remain conflicts.

### FR-018 — Safe obsolete-artifact removal

Update MUST delete an obsolete generated artifact only when its current digest
matches the prior installation record. A modified obsolete artifact MUST be
preserved and reported as drift/conflict. Create, update, delete, and record
publication MUST roll back as one operation on failure.

### FR-019 — Installation record completeness

After successful publication, the installation record MUST describe every
currently generated Forge-owned artifact, its desired digest, Adapter identity
and version, Protocol interval, Harness, and sorted limitations. Obsolete paths
MUST not remain in the new record.

## Validation and diagnostics

### FR-020 — Adapter validation

`adapter validate` MUST read only and fail on invalid configuration,
incompatibility, missing or invalid installation state, generated drift, unsafe
recorded paths, or broken Adapter conformance. It MUST distinguish an Adapter
that is not installed from an invalid installation.

### FR-021 — Adapter doctor

`adapter doctor` MUST read only and emit deterministic checks with PASS, FAIL,
or WARN status plus actionable remediation for configuration, compatibility,
installation state, drift, target safety, conformance, and enforcement
limitations.

### FR-022 — Limitations

Evidence-backed enforcement limitations MUST remain visible in plans,
installation records, validation, and diagnostics. A limitation MAY warn but
MUST NOT be represented as technical enforcement.

## Errors and distribution

### FR-023 — Stable failures and exit codes

Expected Adapter failures MUST use stable `E_FORGE_*` codes, including unknown,
not configured where configuration is required, already/not installed,
Protocol incompatibility, collision, drift, stale state, and invalid
configuration. Domain/validation failures MUST exit `2`, Git/environment
failures `3`, unexpected internal failures `70`, and success `0`.

### FR-024 — Installed-wheel and offline operation

The complete clean-repository flow from `forge init` through Codex install,
idempotence, validate, doctor, drift detection, restoration, and safe update
MUST work from an isolated installed wheel. Vendor discovery MUST not occur at
runtime.

## Non-functional requirements

### NFR-001 — Determinism

Identical installed package, effective Forge inputs, configuration, record, and
repository bytes MUST produce semantically identical plans and diagnostics.

### NFR-002 — Atomicity

Adapter mutation MUST either publish the complete planned state and matching
record or restore the exact pre-publication filesystem state.

### NFR-003 — Harness isolation

Generic registry, service, planning, ownership, state, and publication modules
MUST not depend on Codex-specific types or policy. Codex behavior MUST enter
through an Adapter driver boundary.

### NFR-004 — Human reviewability

Plan and diagnostic output MUST make operation intent, path, ownership,
limitations, conflicts, and the next safe action understandable without
inspecting Python internals.

## Invariants

### INV-001

Protocol and repository-native Forge state remain authoritative; Adapter
configuration, records, and projections are subordinate representations.

### INV-002

Content equality without a matching installation record is not ownership.

### INV-003

Planning and diagnostics are read-only; only explicit `configure`, `install`,
and `update` operations may mutate Adapter state.

### INV-004

No update, cleanup, or recovery path silently overwrites user changes.

### INV-005

Runtime output depends on packaged evidence, never on live vendor content.

## Acceptance scenarios

### AC-001 — Golden path

Given an empty Git repository and an isolated wheel, `forge init` followed by
`forge adapter install codex` creates a valid Forge skill under
`.agents/skills/forge` with no manual prompt copying.

### AC-002 — Discovery

Given an initialized compatible project, `forge adapter list` reports Codex as
packaged, compatible, and either installed or not installed without network
access.

### AC-003 — Plan parity

Given the same project state, `plan codex` and `install codex --dry-run` report
the same ordered operations and neither changes filesystem bytes.

### AC-004 — Collision

Given an unrecorded user file at any desired generated path, plan reports a
collision and install leaves all files and Adapter state unchanged.

### AC-005 — Idempotent reinstall

Given an intact current Codex installation, a repeated install succeeds with
only unchanged operations and preserves file and record timestamps and bytes.

### AC-006 — Safe update

Given an intact older installation and a changed packaged projection, update
creates, replaces, and removes only recorded Forge-owned artifacts, then writes
the complete new record.

### AC-007 — Drift protection

Given a modified or missing recorded artifact, validate and doctor identify its
path and drift kind, while install/update perform no mutation.

### AC-008 — Atomic rollback

Given a publication failure after a mixture of create, update, and delete
operations, every affected artifact and the prior installation record are
restored byte-for-byte.

### AC-009 — Configuration precedence

Given packaged evidence, a configured target, and an explicit target option,
planning selects the explicit option; without it selects configuration; without
configuration selects `.agents/skills/forge`.

### AC-010 — Limitations remain truthful

Given a Forge invariant represented through Codex skill text without a proven
technical primitive, plan, record, validate, and doctor report it as a
limitation rather than enforced behavior.

### AC-011 — Invalid or stale state

Given malformed configuration, an incompatible Protocol, a malformed record,
or a record for an unexpected Adapter identity/version, commands return the
appropriate stable failure and do not mutate.

### AC-012 — Canonical survival

Given removal of the generated `.agents/skills/forge` tree, canonical Forge
project, Flow, Contract, and Change state remain intact and independently
validatable.
