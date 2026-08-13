---
forge:
  artifact: strict_review
  schema: 1
change: CHG-0001
iteration: 2
status: passed
---

# Strict Review — CHG-0001

## Iteration 1

Result: FAILED

Findings:

- BLOCKER: 0
- MAJOR: 3
- MINOR: 2
- OBSERVATION: 1

Project policy makes MAJOR findings blocking.

### REV-001 — Unsafe YAML generation for project name

Severity: MAJOR

Status: RESOLVED

The initial implementation interpolated the repository directory name directly into YAML. Regression TDD proved that a repository named `null` became YAML null. The configuration generator now uses `yaml.safe_dump`, preserving project names as strings. TDD-010 records RED and GREEN evidence.

### REV-002 — Workspace path validation was not cross-platform safe

Severity: MAJOR

Status: RESOLVED

Workspace plan paths are now explicitly defined as canonical POSIX-relative inputs. Backslash ambiguity and NUL bytes are rejected before native filesystem materialization. Regression coverage proves that `..\\outside.txt` is rejected. TDD-011 records evidence.

### REV-003 — No-overwrite guarantee contained a cross-process race

Severity: MAJOR

Status: RESOLVED

Forge initialization now acquires `.forge.init.lock` through exclusive filesystem creation before staging and holds ownership through publication. A competing Forge initialization cannot enter the publication section. Lock ownership is explicit so a process never removes a lock it did not create. TDD-011 records both the original RED and an intermediate failed GREEN that exposed the ownership bug.

The guarantee is scoped to cooperating Forge initialization processes and normal filesystem semantics; Forge does not claim protection against an arbitrary external actor mutating repository files concurrently.

### REV-004 — Missing Git executable used inconsistent exit semantics

Severity: MINOR

Status: RESOLVED

The Git boundary now raises `GitUnavailableError`. `forge init` and `forge validate` map it to `E_FORGE_GIT_UNAVAILABLE` and exit code `3`, consistent with the environment-failure contract. TDD-012 records evidence.

### REV-005 — Protocol identity and display version were implicit

Severity: MINOR

Status: RESOLVED

Runtime version metadata is centralized in `forge_cli.version`:

- Protocol compatibility identifier: `1`;
- human-readable maturity label: `1-draft`;
- CLI version: `0.1.0.dev0`.

Generated project configuration stores the compatibility identifier while `forge version` reports the display label. README documents the distinction.

### REV-006 — Initialization is not crash-atomic

Severity: OBSERVATION

Status: ACCEPTED

A hard process kill or machine failure may leave `.forge.tmp-*` or `.forge.init.lock` behind. Such state does not appear as a successfully initialized `.forge/` workspace, so it does not violate FR-008, but a stale lock may require manual inspection/removal before a later initialization.

This is intentionally not auto-recovered in CHG-0001 because blindly breaking a lock cannot reliably prove that another initialization process is dead, especially across PID reuse, containers, or shared filesystems. A future Doctor enhancement should detect and report stale initialization artifacts rather than silently delete them.

## Iteration 2 — Adversarial Re-review

Result: PASSED

Re-review examined:

- generated configuration and YAML scalar safety;
- workspace path confinement;
- concurrent initialization behavior and lock ownership;
- Git environment error classification;
- Protocol resource packaging;
- Protocol version identity;
- public CLI boundary;
- exit-code contract;
- isolated installed-wheel behavior;
- offline runtime behavior;
- regression TDD evidence.

No unresolved BLOCKER or MAJOR findings remain.

Fresh evidence after the behavioral review fixes:

- Tests workflow run `31671363071`, job `94356481812`: SUCCESS;
- Distribution Verification run `31671363034`, job `94356481901`: SUCCESS;
- isolated wheel build/install: SUCCESS;
- installed `forge version`: SUCCESS;
- installed `forge init -> validate -> doctor` with unreachable proxies: SUCCESS;
- runtime dependency audit: SUCCESS.

## Review gate

PASSED.

Remaining accepted risk: REV-006 only.
