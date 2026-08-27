---
forge:
  artifact: test_design
  schema: 1
change: CHG-0049
status: complete
---

# CHG-0049 · Test Design

> Verification Design

## Overview

| | |
|---|---|
| **Change** | CHG-0049 |
| **Flow** | STANDARD |
| **Status** | Complete |

## Test Strategy

Demonstrate the fix bottom-up through the pipeline it touches, then
end-to-end through the two public entry points (`forge adapter doctor`,
`forge adapter update`) and `forge doctor`. All scenarios are automated
and POSIX-gated where they assert executable-bit behaviour.

| Layer | Scope | Method |
|---|---|---|
| A · Publication | `publish_adapter_plan` applies mode | Automated (Integration, temp repo) |
| B · Planning | snapshot observes mode; `plan_adapter` / `classify_artifact` repair mode-only discrepancy | Automated (Unit) |
| C · Projection | Claude Code bundle marks the hook executable | Automated (Unit) |
| D · Diagnostics | `AdapterService.doctor` + `forge doctor` + `forge adapter doctor` CLI | Automated (Integration + CLI) |
| E · Service | `forge adapter update` repairs an installed non-executable hook, idempotently | Automated (Integration) |
| F · Repository | tracked git mode of the hook | Automated (Unit) |

## Coverage Map

| Requirement | Scenario | Method |
|---|---|---|
| FR-001 | TD-001, TD-002, TD-003 | Automated |
| FR-002 | TD-004 | Automated |
| FR-003 | TD-005 | Automated |
| FR-004 | TD-006, TD-007 | Automated |
| FR-005 | TD-008 | Automated |
| FR-006 | TD-009, TD-010, TD-011 | Automated |
| FR-007 | TD-012 | Automated |

## Layer A · Publication

### TD-001 · `create` of an executable artifact lands executable
Requirements: FR-001
Type: Integration

#### Purpose
Proves the publisher applies the owner-executable bit for a projected
executable artifact on first materialization — the property a fresh
`forge adapter install` on a POSIX system depends on. A wrong
Implementation (no chmod, or chmod after replace with a visible window)
leaves the hook non-executable and the `PreToolUse` guard inoperative.

#### Preconditions
POSIX platform (`os.name == "posix"`); otherwise skip.

#### Scenario
Given an `AdapterPlan` with a `create` operation for a Forge-owned artifact carrying `executable=True`
When `publish_adapter_plan` runs against a temp repository
Then the file exists, its content equals the operation content, and `stat().st_mode & 0o100` is set

#### Evidence
`pathlib.Path.stat()` mode bits of the published file; test assertion result.

#### Failure Condition
File written non-executable; or the executable bit is set on a
non-executable sibling artifact in the same plan (over-application); or
the test passes only because it never ran the POSIX branch.

### TD-002 · `update` re-applies the executable bit
Requirements: FR-001
Type: Integration

#### Purpose
Proves a content-identical `update` operation (the intent FR-004 produces
for a mode-only discrepancy) results in an executable file. Without this,
`forge adapter update` would rewrite the bytes but leave the mode wrong.

#### Scenario
Given an existing executable-projected artifact on disk that is currently non-executable, and a plan with an `update` operation for it whose `expected_current_digest` matches
When `publish_adapter_plan` runs on POSIX
Then the file is executable afterward and its content is unchanged

#### Evidence
Mode bits before/after; content digest equality.

#### Failure Condition
Mode unchanged after `update`; content altered; precondition digest
check bypassed.

### TD-003 · non-POSIX publish does not fail and does not chmod
Requirements: FR-001
Type: Integration

#### Purpose
Proves CON-003 at the publication layer: on a platform without meaningful
executable bits the publish still succeeds and writes correct content.

#### Scenario
Given the same executable `create` plan, with `os.name` forced to `"nt"` (monkeypatch)
When `publish_adapter_plan` runs
Then it completes without error and the file content is correct (no assertion on mode)

#### Evidence
No exception; file content equals operation content.

#### Failure Condition
Publish raises; content wrong; test asserts a mode bit that the platform
branch never guarantees.

## Layer B · Planning

### TD-005 · repository snapshot reports the executable bit
Requirements: FR-003
Type: Unit

#### Purpose
Proves `snapshot_repository_artifacts` observes mode, the input
`plan_adapter` needs to detect a mode-only discrepancy.

#### Scenario
Given two existing regular files, one `chmod 0o755` and one `0o644`, on POSIX
When the Adapter repository snapshot reads them
Then the first is reported executable and the second is not

#### Evidence
`RepositoryArtifactState.executable` (or equivalent field) per path.

#### Failure Condition
Both reported the same; symlink/non-regular handling regressed; field
absent.

### TD-006 · mode-only discrepancy classifies as `update`
Requirements: FR-004
Type: Unit

#### Purpose
The core repair mechanism: a projected-executable artifact whose content
is byte-current but whose mode is wrong must produce an `update`
operation, not `unchanged`, or `forge adapter update` short-circuits and
never repairs it.

#### Scenario
Given a `ProjectedArtifact(executable=True)`, a `RepositoryArtifactState` that exists with `current_digest == expected_digest == digest(projection.content)` and `executable=False`, on POSIX
When `plan_adapter` builds the plan
Then that artifact's `AdapterOperation.intent is OperationIntent.UPDATE`

#### Evidence
Operation intent in the returned `AdapterPlan`.

#### Failure Condition
Intent is `UNCHANGED`; or a genuinely-unchanged non-executable artifact
is now spuriously `UPDATE` (checked by TD-007); `CONFLICT` produced.

### TD-007 · matching mode stays `unchanged`; non-executable unaffected
Requirements: FR-004
Type: Unit

#### Purpose
Proves the mode check narrows exactly to the failure case: an
already-executable projected artifact, and any non-executable artifact,
remain `unchanged` when content matches. Also covers CON-003 (mode
ignored when `os.name != "posix"`).

#### Scenario
Given (a) a projected-executable artifact already executable on disk with matching content, and (b) a projected non-executable artifact with matching content, on POSIX; and (c) case (a)-shaped inputs but non-executable on disk with `os.name` forced to `"nt"`
When `plan_adapter` builds the plan
Then every one of these operations is `UNCHANGED`

#### Evidence
Operation intents.

#### Failure Condition
Any of the three becomes `UPDATE`/`CONFLICT`.

## Layer C · Projection

### TD-004 · only the hook resource is executable
Requirements: FR-002
Type: Unit

#### Purpose
Proves the Claude Code projection is the source of truth for
executability and marks exactly the right resource — the wiring that
carries the fix into every install without repository-specific knowledge
(SC6).

#### Scenario
Given the Claude Code projection bundle for a representative protocol + flow set
When its resources are enumerated
Then the resource whose name ends `skills/forge/hooks/check-manifest-edit.sh` is executable and every other resource is not

#### Evidence
`executable` attribute on each `ClaudeCodeProjectionResource` (or on the
`ProjectedArtifact` produced by the driver).

#### Failure Condition
Hook not marked; a markdown/yaml resource marked; attribute absent.

## Layer D · Diagnostics

### TD-009 · doctor fails on a non-executable installed hook
Requirements: FR-006
Type: Integration

#### Purpose
Proves the gap is surfaced (CON-004) — a declared protection that is not
executable is reported, not silently accepted.

#### Scenario
Given a temp repo with the Claude Code Adapter installed, then the hook file `chmod 0o644`, on POSIX
When `AdapterService.doctor` runs
Then a check has status `failed`, its message names the hook path, and its remediation contains `forge adapter update claude-code`

#### Evidence
`AdapterDoctorResult.checks` entries; `AdapterDoctorResult.passed is False`.

#### Failure Condition
No failed check; check present but no remediation (would also violate the
`AdapterCheck` invariant); passes on non-POSIX where it should be inert
and instead errors.

### TD-010 · doctor passes when the hook is executable
Requirements: FR-006
Type: Integration

#### Purpose
Guards against a check that always fails / always fires regardless of
state.

#### Scenario
Given a freshly installed Claude Code Adapter (hook executable) on POSIX
When `AdapterService.doctor` runs
Then the executable-artifact check has status `passed`

#### Evidence
Named check status.

#### Failure Condition
Check failed or absent on a healthy install.

### TD-011 · `forge doctor` and `forge adapter doctor` surface it
Requirements: FR-006
Type: CLI

#### Purpose
Proves the operator-facing commands report the condition — `forge doctor`
via adapter-readiness fan-out and `forge adapter doctor` directly.

#### Scenario
Given the non-executable-hook temp repo on POSIX
When `forge adapter doctor claude-code` and `forge doctor` are invoked via the CLI runner
Then `forge adapter doctor` exits non-zero with a line identifying the hook, and `forge doctor` output contains a failed `adapter:claude-code:` check

#### Evidence
CLI exit code and stdout.

#### Failure Condition
Exit zero; condition absent from output.

## Layer E · Service

### TD-008 · `adapter update` repairs a non-executable hook, idempotently
Requirements: FR-005
Type: Integration

#### Purpose
The end-to-end repair path an existing project runs (SC4): after
`update`, the hook is executable; a second `update` is a no-op.

#### Scenario
Given a temp repo with the Claude Code Adapter installed and the hook then made non-executable, on POSIX
When `AdapterService.update` runs once
Then it reports a mutation, the hook is executable, and the installation record still validates
And when `AdapterService.update` runs again
Then it reports no mutation and the hook remains executable

#### Evidence
`AdapterMutationResult.mutated`; hook mode; `forge adapter validate`
result / record parse.

#### Failure Condition
First `update` no-ops (mode-only discrepancy not detected); record
invalid after; second `update` still mutates (non-idempotent); content of
any other projected file changed.

## Layer F · Repository

### TD-012 · the hook is tracked executable in git
Requirements: FR-007
Type: Unit

#### Purpose
Proves SC1/SC2 for this repository and any fresh clone of it, and guards
the regression permanently.

#### Scenario
Given the repository
When `git ls-files -s .claude/skills/forge/hooks/check-manifest-edit.sh` is read
Then the mode field is `100755`

#### Evidence
`git ls-files -s` output parsed in the test.

#### Failure Condition
Mode `100644`; test skipped when git is unavailable without being marked
as such.

## Manual Acceptance

None. Success Criterion 2 ("Claude Code can run the `PreToolUse` hook
without `Permission denied`") is a property of the file mode plus the
shell's `execve`; TD-001 (executable bit present) plus an in-test
execution of the materialized script with a crafted stdin payload
asserting `exit 0` and the `deny` JSON fully covers it without a live
Harness. This execution assertion is folded into TD-001's Evidence.

## Valid RED

RED for each scenario must fail because the mode is not applied / not
observed / not classified / not reported — not because of an import
error, a missing `executable` kwarg raising `TypeError` at collection
time (add the field first as inert, then assert behaviour), or an
unrelated fixture problem. The publisher and planner tests must actually
execute their POSIX branch (guard: skip on non-POSIX, and CI is POSIX).

## Requirement Coverage

| Requirement | Automated | Manual | Status |
|---|---|---|---|
| FR-001 | TD-001, TD-002, TD-003 | — | Covered |
| FR-002 | TD-004 | — | Covered |
| FR-003 | TD-005 | — | Covered |
| FR-004 | TD-006, TD-007 | — | Covered |
| FR-005 | TD-008 | — | Covered |
| FR-006 | TD-009, TD-010, TD-011 | — | Covered |
| FR-007 | TD-012 | — | Covered |

## Coverage Gaps

None. Every Functional Requirement has at least one automated scenario.
Non-POSIX behaviour (CON-003) is covered by TD-003 and TD-007's third
case via `os.name` monkeypatching rather than a real Windows runner,
which is the honest limit of this suite and sufficient for the
requirement (do-nothing on non-POSIX).

## Test Design Gate

- Every mandatory Requirement has an automated verification strategy
  (Requirement Coverage table, no gaps).
- Critical scenarios (TD-001, TD-006, TD-008) state the consequence a
  wrong Implementation causes, not just the mechanism.
- Failure Conditions are defined for every scenario, including
  false-positive modes (over-application, always-failing check,
  never-executed POSIX branch).
- All scenarios are automated; Manual Acceptance is explicitly "None"
  with justification.
- Valid RED is defined and distinguishes behavioural failure from
  collection-time `TypeError`.
- No Requirement is left without known coverage.
