---
forge:
  artifact: architecture
  schema: 1
change: CHG-0036
status: complete
---

# Architecture — CHG-0036 Merge Readiness Gate

## Solution Summary

Add a provider-independent `merge_readiness` package that evaluates an
explicit Git subject and returns structured checks and diagnostics. Keep the
CLI adapter thin: `forge change merge-check` resolves arguments, invokes the
engine, renders deterministic output, and maps the engine verdict to the
command-specific exit contract. `forge validate` remains unchanged.

## Architectural Goals

- Reuse `resolve_effective_flow`, existing validation helpers, Protocol
  policies, and canonical Change artifacts.
- Keep Change resolution, materiality policy, evidence evaluation, and
  diagnostics independently testable.
- Make the evaluator usable by CLI, CI, Doctor, and future Harness
  diagnostics without duplicating verdict logic.
- Fail closed whenever Git history, artifact identity, provenance, or
  authorization is ambiguous.
- Keep GitHub-specific behavior in workflow wiring, not Protocol Core.

## Components and interfaces

### `src/forge_cli/merge_readiness/models.py`

Define immutable result types:

- `MergeReadinessRequest(base_revision: str, head_revision: str)`;
- `MergeReadinessEvaluation(subject, affected_changes, checks, diagnostics,
  verdict)`;
- `ReadinessCheck(id, status, change_id, expected, actual, artifact)`;
- `ReadinessDiagnostic(code, severity, change_id, message, expected, actual,
  artifact, remediation)`.

Statuses and diagnostic ordering are language-invariant and deterministic.

### `change_resolution.py`

Resolve `BASE..HEAD` with Git name-status data and exact repository-relative
path handling. Include both rename endpoints, preserve deleted Change
identity from the base tree when possible, reject symlinks and malformed
Change directories, and return an operational failure when required history
cannot be inspected.

### `policy.py`

Load `protocol/policies/merge-readiness.yml` through a corresponding schema
and canonical Protocol resource resolver. The policy classifies
repository-relative paths/categories as material, permitted non-material, or
ambiguous. It must not define lifecycle stages or Flow requirements.
Ambiguous policy matches are blocking.

### `evaluator.py`

For every resolved Change, load its manifest and effective Flow, invoke the
existing validation boundary in-memory where possible, and evaluate:

1. structural validity;
2. Flow-required artifact and Gate evidence;
3. current C-077 Plan Decision and approved Plan digest;
4. TDD/Verification evidence bound to the effective subject;
5. Review iteration, finding, Resolution, and re-review chain;
6. Completion consistency; and
7. final subject/provenance equality with the merge subject.

The evaluator never runs tests or performs lifecycle mutations.

### Plan digest binding

The existing C-077 implementation provenance record remains the authority
record (`role: implementation`, `source.reference:
plan.md#approval-record`) and gains a `source.content_digest` object with
`algorithm: sha256`, `path: plan.md`, and a lowercase 64-hex `value`. The
digest covers the complete Plan file after removing only the two canonical
approval marker comments and normalizing UTF-8 and LF newlines. This keeps
human confirmation and provenance in the existing authority channel while
adding an explicit content binding. The v2 provenance schema and its
validator must require this object for prospective C-077 approval records;
Protocol 1 historical records remain accepted without it. Any missing,
malformed, mismatched, or historically unavailable digest is blocking for
prospective readiness.

### `diagnostics.py`

Map internal failures to stable `MR-xxx` codes, sort by Change ID then check
ID then artifact path, and render both human output and structured data.

### CLI and workflow

`src/forge_cli/change_cli.py` exposes `merge-check` with explicit `--base` and
`--head` options. Local invocation defaults only `head` to `HEAD`; base must
be explicit or deterministically inferred from a configured protected-branch
ref, otherwise the command fails closed. The workflow supplies immutable PR
base/head SHAs and runs with `fetch-depth: 0`.

## Data flow

`base/head arguments → Git subject inspection → changed paths → materiality
policy → affected Changes → effective Flow → evidence checks → deterministic
diagnostics → verdict/exit code`.

Every affected Change contributes a conjunctive result. Zero affected Changes
is permitted only for an explicitly permitted non-material diff.

## Security and assurance boundaries

The engine detects repository-observable tampering and missing evidence; it
does not provide cryptographic attestation. A recorded provenance source is
not upgraded to `verified`. CI required-check configuration and bypass rules
remain external GitHub controls and are documented, not simulated.

## Compatibility

Protocol 1 historical artifacts retain their original validity. The engine
uses a version-aware compatibility policy for current merge authorization and
never reconstructs absent Plan, Review, Verification, or historical subject
evidence.
