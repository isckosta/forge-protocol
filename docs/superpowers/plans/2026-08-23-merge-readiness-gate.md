# Merge Readiness Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a deterministic repository-native Merge Readiness evaluation for the effective Git revision without changing `forge validate` semantics.

**Architecture:** A reusable `merge_readiness` engine resolves an explicit Git subject, materiality policy, affected Changes, effective Flow requirements, and canonical evidence. A thin CLI command and GitHub workflow invoke the engine; branch protection and release provenance remain external/separate boundaries.

**Tech Stack:** Python 3.12+, Typer, PyYAML, JSON Schema resources, Git subprocesses, pytest, GitHub Actions.

**Spec:** `.forge/changes/CHG-0036-merge-readiness-gate/specification.md`

## Global Constraints

- `forge validate` remains structural/semantic validation, not merge readiness.
- Effective FAST/STANDARD/FULL requirements come from canonical Flow resolution.
- The accepted RFC-0006 decision requires immutable Plan content-digest binding.
- Ambiguous provenance, history, ownership, or authorization fails closed.
- Protocol 1 historical validity is preserved.
- Core remains local and provider-independent.
- Release provenance and external branch protection are not replaced.

### Task 1: Canonical Plan digest and materiality policy

**Files:**
- Modify: `protocol/contract/engineering.md`
- Modify: `protocol/versions/2/specification.md`
- Create: `protocol/policies/merge-readiness.yml`
- Create: `protocol/schemas/policy-merge-readiness.schema.json`
- Modify: `protocol/schemas/execution-provenance-v2.schema.json`
- Test: protocol contract and policy tests

- [ ] Write RED tests for digest mismatch, malformed digest, historical compatibility, and ambiguous materiality policy.
- [ ] Implement `source.content_digest` with `algorithm: sha256`, `path: plan.md`, lowercase 64-hex `value`, and the canonical marker/newline normalization rule defined in Architecture.
- [ ] Implement the centralized materiality policy loader without embedding Flow requirements.
- [ ] Run focused policy and contract tests; record expected GREEN evidence.

### Task 2: Git subject and Change resolution

**Files:**
- Create: `src/forge_cli/merge_readiness/change_resolution.py`
- Create: `src/forge_cli/merge_readiness/models.py`
- Test: `tests/unit/test_merge_readiness_change_resolution.py`

- [ ] Write RED tests for explicit base/head, additions, deletions, renames, malformed Change directories, contradictory IDs, missing history, shallow clones, and multiple Changes.
- [ ] Implement immutable subject inspection and deterministic affected-Change resolution.
- [ ] Ensure symlink and path traversal cases fail closed.
- [ ] Run focused resolution tests.

### Task 3: Evidence evaluator

**Files:**
- Create: `src/forge_cli/merge_readiness/evaluator.py`
- Create: `src/forge_cli/merge_readiness/policy.py`
- Create: `src/forge_cli/merge_readiness/diagnostics.py`
- Test: `tests/unit/test_merge_readiness_evaluator.py`

- [ ] Write RED fixtures for FAST, STANDARD, FULL, pending lifecycle stages, stale Plan approval, Verification, Review, Resolution, Completion, findings, and post-review subject changes.
- [ ] Implement conjunctive per-Change evaluation by composing effective Flow and existing validation authorities.
- [ ] Implement stable `MR-xxx` diagnostics and deterministic ordering.
- [ ] Run focused evaluator tests.

### Task 4: CLI contract

**Files:**
- Modify: `src/forge_cli/change_cli.py`
- Test: `tests/cli/test_merge_check.py`

- [ ] Write RED tests for ready, blocked, and operational outcomes and for human/structured output.
- [ ] Add `forge change merge-check --base BASE --head HEAD` with safe local defaults and fail-closed base resolution.
- [ ] Preserve existing `forge validate` output and exit codes.
- [ ] Run CLI contract tests.

### Task 5: CI and documentation

**Files:**
- Modify: `.github/workflows/tests.yml` or create the dedicated required-check workflow selected by Architecture
- Modify: `CONTRIBUTING.md`, `README.md`, and affected Harness workflow resources only
- Test: workflow/guidance/release provenance tests

- [ ] Write RED tests requiring full history, explicit PR subject selection, required-check naming, and honest branch-protection boundaries.
- [ ] Add CI invocation of validation and readiness without coupling to release provenance.
- [ ] Document external branch-protection configuration and Harness guidance limitations.
- [ ] Run workflow and release-provenance regression tests.

### Task 6: Verification and independent Review

**Files:**
- Modify: `.forge/changes/CHG-0036-merge-readiness-gate/tdd-evidence.yml`
- Modify: `.forge/changes/CHG-0036-merge-readiness-gate/verification.md`
- Modify: `.forge/changes/CHG-0036-merge-readiness-gate/review.md`
- Create/modify: `.forge/changes/CHG-0036-merge-readiness-gate/provenance.yml`

- [ ] Run focused and full test suites, `forge validate`, and `forge doctor`.
- [ ] Freeze the implementation subject and record immutable provenance.
- [ ] Conduct independent Strict Review with distinct Execution and Context.
- [ ] Resolve findings with Resolution Verification and re-review when required.
- [ ] Record Completion only after every applicable Flow Gate passes.
