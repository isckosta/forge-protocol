---
forge:
  artifact: specification
  schema: 1
change: CHG-0049
status: complete
---

# CHG-0049 · Specification

> **Change Contract**
>
> This Specification defines the behaviors, constraints, and verifiable
> conditions that the Change must satisfy.

## Overview

| | |
|---|---|
| **Change** | CHG-0049 |
| **Flow** | STANDARD |
| **Status** | Complete |

## Summary

Give the Harness Adapter materialization pipeline enough file-mode
fidelity to materialize a generated artifact as executable when its
Adapter projection declares it so. Apply this to the Claude Code
Adapter's `check-manifest-edit.sh` hook, which Claude Code executes
directly and which is currently materialized (and committed)
non-executable, rendering a Forge-declared `PreToolUse` protection
inoperative. Make Forge diagnostics report an installed hook that should
be executable but is not, and make `forge adapter update` repair such an
installation. The contract boundary is: **Forge-owned generated
artifacts that their Adapter projection marks executable**, on **POSIX**
platforms. Non-executable artifacts, user-owned/shared artifacts, the
Codex Adapter, and non-POSIX permission emulation are unchanged.

## Classification

STANDARD. This is a behavioral Change to the CLI's Adapter pipeline
(projection → planning → publication → diagnostics) with a repository
side effect (the tracked hook mode). It is not a localized single-file
bugfix (FAST is disqualified by `significant_cross_module_change`: it
touches projection, planner, ownership classification, repository
snapshot, publisher, and diagnostics). It introduces no new domain
invariant, no Protocol change, no schema change, and no
authorization-model change (the hook is explicitly *not* a security
boundary — C-073), so FULL is not warranted.

## Functional Requirements

### FR-001 · Executable artifacts materialize with the executable bit (POSIX)
Origin: discovery.md "Where mode is lost"

#### Requirement
When an Adapter projection declares a Forge-owned generated artifact as
executable, `publish_adapter_plan` MUST materialize that artifact with an
owner-executable file mode on POSIX platforms, for both a `create` and an
`update` operation. On non-POSIX platforms the publisher MUST NOT fail
and MUST write the artifact content unchanged.

#### Expected Behavior
The executable bit is applied atomically with the content write (the file
is never observable as present-but-non-executable during a successful
publish). A non-executable artifact's mode handling is unchanged from
current behavior.

#### Acceptance
AC-001
Given a plan containing a `create` operation for a Forge-owned artifact marked executable
When `publish_adapter_plan` runs on a POSIX system
Then the materialized file exists with mode bits including `0o100` (owner-executable) and its content matches the projection

AC-002
Given an installed executable artifact whose on-disk content later matches a new plan's `update` operation for it
When `publish_adapter_plan` applies that operation on a POSIX system
Then the file is executable afterward

### FR-002 · Claude Code projection marks the hook executable
Origin: discovery.md "The hook and how it is invoked"

#### Requirement
The Claude Code Adapter projection MUST mark
`<target>/skills/forge/hooks/check-manifest-edit.sh` as executable and
MUST mark every other projected resource (SKILL.md, CLAUDE.md, the
references, the flow files) as non-executable.

#### Acceptance
AC-003
Given the Claude Code projection bundle for any supported protocol and flow set
When its resources are enumerated
Then exactly the `check-manifest-edit.sh` resource is executable and all others are not

### FR-003 · The repository snapshot observes the executable bit
Origin: discovery.md "Why `adapter update` will not currently repair"

#### Requirement
The read-only repository artifact snapshot used for Adapter planning MUST
record, per existing regular file, whether it is executable on POSIX. On
non-POSIX platforms this observation MUST be reported such that it never
causes a mode-driven plan difference (see FR-004 Boundary).

#### Acceptance
AC-004
Given an existing regular file with an owner-executable mode on a POSIX system
When the Adapter repository snapshot reads it
Then the snapshot reports that artifact as executable, and reports a non-executable sibling as not executable

### FR-004 · Planning repairs a mode-only discrepancy
Origin: discovery.md "Why `adapter update` will not currently repair"

#### Requirement
When an Adapter projection marks an artifact executable, the artifact
already exists, its on-disk content digest equals both the recorded
generated digest and the projected content digest, but its observed mode
is not executable (POSIX), `plan_adapter` MUST classify the operation as
`update` (a content-identical re-materialization that will re-apply
mode), not `unchanged`. When the observed mode already matches, the
operation MUST remain `unchanged`.

#### Boundary
On non-POSIX platforms, or for a non-executable projected artifact, mode
MUST NOT influence classification — a content-identical artifact stays
`unchanged`.

#### Acceptance
AC-005
Given a projected executable artifact, an intact recorded digest, matching on-disk content, and a non-executable on-disk mode on POSIX
When `plan_adapter` produces the plan
Then that artifact's operation intent is `update`

AC-006
Given the same inputs but an already-executable on-disk mode
When `plan_adapter` produces the plan
Then that artifact's operation intent is `unchanged`

### FR-005 · `forge adapter update` repairs an installed non-executable hook
Stories: —
Origin: intent.md Goal 4, Success Criteria 4

#### Requirement
Running `forge adapter update claude-code` against a project whose
installed `check-manifest-edit.sh` is byte-current but non-executable
MUST make the hook executable on POSIX, MUST leave the installation
record valid, and MUST be idempotent (a second `update` reports no
change).

#### Acceptance
AC-007
Given an installed Claude Code Adapter whose hook file has been made non-executable
When `forge adapter update claude-code` runs on a POSIX system
Then the command succeeds, the hook file is executable, and an immediately repeated `update` reports no mutation

### FR-006 · Forge diagnostics detect a non-executable hook
Origin: intent.md Goal 3, Success Criteria 3

#### Requirement
`forge adapter doctor claude-code` (and therefore `forge doctor` via
adapter-readiness fan-out) MUST report a `failed` check, with remediation
text naming `forge adapter update claude-code`, when an installed
artifact that the projection marks executable exists on disk without an
executable bit on POSIX. When all such artifacts are executable (or the
platform is non-POSIX) the check MUST pass.

#### Acceptance
AC-008
Given an installed Claude Code Adapter whose hook file is not executable on a POSIX system
When `forge adapter doctor claude-code` runs
Then a check fails, identifies the hook path, and its remediation names `forge adapter update claude-code`

AC-009
Given an installed Claude Code Adapter whose hook file is executable
When `forge adapter doctor claude-code` runs
Then the executable-artifact check passes

AC-010
Given the same non-executable-hook project
When `forge doctor` runs
Then a check of the form `adapter:claude-code:<id>` is reported failed

### FR-007 · The hook is versioned executable in this repository
Origin: intent.md Goal 2, Success Criteria 1/2

#### Requirement
`.claude/skills/forge/hooks/check-manifest-edit.sh` MUST be tracked in
git with an executable mode (`100755`), and an automated test MUST assert
this so a regression is caught.

#### Acceptance
AC-011
Given the repository working tree
When the tracked mode of the hook file is inspected
Then it is `100755`, and a test asserting this passes

## Non-functional Requirements

### NFR-001 · No new runtime dependency
The solution uses only the Python standard library (`os`, `stat`) for
mode handling. No package is added.

### NFR-002 · No installation-record schema change
The installation record's `path → digest` contract is unchanged. The
Adapter projection remains the single source of truth for which paths are
executable (see DEC-001 in the Plan). `adapter-installation` schemas are
not modified.

## Constraints

### CON-001
The `SKILL.md` hook registration MUST continue to invoke the script by
path (`type: command`). It MUST NOT be changed to `sh <path>` to work
around a missing permission bit.

### CON-002
The hook mechanism MUST NOT be broadened: no new matcher, hook type, or
enforced path beyond what exists today.

### CON-003
A Windows / non-POSIX checkout MUST NOT be reported as drifted or failed
on account of an executable bit the platform does not model.

### CON-004
A failed hook installation MUST NOT be treated as a satisfied protection:
diagnostics reporting the gap is required, not optional.

## Traceability Matrix

| Requirement | Discovery finding | Acceptance |
|---|---|---|
| FR-001 | Publisher writes without chmod | AC-001, AC-002 |
| FR-002 | Hook resource has identical shape to markdown resources | AC-003 |
| FR-003 | Snapshot reads `read_text()` only | AC-004 |
| FR-004 | `update` early-returns on all-`unchanged` plan | AC-005, AC-006 |
| FR-005 | `service.update()` + publisher skip unchanged ops | AC-007 |
| FR-006 | `doctor()` has a live projection; `forge doctor` fans out | AC-008, AC-009, AC-010 |
| FR-007 | `git ls-files -s` → `100644` | AC-011 |

## Compatibility Statement

- **Protocol:** unaffected. No Contract, Flow, policy, or schema change.
- **Installation record:** format unchanged (NFR-002).
- **Existing installs:** after this Change the packaged Claude Code
  Adapter version is bumped, so `forge adapter doctor` will report
  existing installations as stale and `forge adapter update` will
  re-materialize; on POSIX this also repairs the hook mode via FR-004.
  This is the normal, intended consequence of an Adapter change.
- **Non-POSIX:** behavior is unchanged (CON-003).
- **Codex Adapter:** untouched (ships no hook).

## Specification Gate

- Every Discovery finding maps to a Requirement (Traceability Matrix).
- Requirements are independently verifiable; each has ≥1 Acceptance
  Criterion phrased Given/When/Then.
- The one material technical decision (record executability vs.
  projection-as-source-of-truth) is escalated to the Plan as DEC-001,
  per Discovery's Open Questions.
- No Protocol/schema/Contract impact; Compatibility Statement records
  why.
- Out-of-scope boundary is explicit and matches Intent.

## Out of Scope

- Codex Adapter.
- `SKILL.md` invoking the script via `sh` (CON-001).
- New hook matchers / types / enforced paths (CON-002).
- A general permission model for user-owned or shared artifacts.
- Recording per-artifact mode in the installation record / a schema bump
  (NFR-002, DEC-001).
- Non-POSIX executable-bit emulation (CON-003).
