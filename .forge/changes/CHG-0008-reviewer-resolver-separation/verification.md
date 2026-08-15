---
forge:
  artifact: verification
  schema: 1
change: CHG-0008
status: active
---

# Verification — Strict Review Iteration 1 Resolution

## Scope

Verification covers R001-R004: integer Protocol versioning, Protocol 1 preservation, Protocol 2 provenance and assurance semantics, revision-aware Review Iterations, all-Flow C-026 enforcement, forged-evidence rejection, downgrade resistance, Protocol-aware Contract/Doctor resolution, and Protocol-aware Codex projection.

## RED evidence

TDD-006 test-only commit `d71435f9b2fca5c5829121ff45e0059e67526d84` produced GitHub Actions Tests run `31900774999`, job `95051092652`: **FAIL** at `Run tests`. Checkout, Python setup, pip upgrade, and test dependency installation all passed, so the failure is a valid behavioral RED rather than environment/setup failure. Distribution Verification run `31900775010` passed on the same test-only revision, further isolating the RED to the new expectations.

TDD-007 test-only commit `bb43fae06670e90f5ed07a63f154ec0f541c854d` adds the Protocol-aware Adapter projection boundary before production support for `protocol_id` exists.

## Resolution implementation

Production revisions:

- `c25125ffc4bdf3ed9f6bf0f4bade5424ddc3c762` — Protocol 2, provenance ledger, revision-aware Review, validation and Adapter boundary;
- `5806346ab38e0f7b624c67e17981724bf2e90b44` — Doctor resolves the configured Protocol Contract.

## Finding resolution evidence

- **R001:** Protocol 1 canonical Contract/Specification/Review Policy and `forge/change@1` are restored to historical semantics; Protocol 2 lives under `protocol/versions/2/`, CLI supports integer Protocols 1 and 2, and compatibility documentation states the breaking boundary explicitly.
- **R002:** `forge/execution-provenance@1` provides durable provider-independent execution records. CHG-0008 does not backfill historical Implementation/Review identifiers; this Resolution prospectively records `resolution-001`.
- **R003:** Protocol 2 C-026 enforcement is selected after project Protocol resolution and applies to FAST, STANDARD, and FULL. Active Protocol 2 schema downgrade is rejected; completed Protocol 1 history is preserved.
- **R004:** arbitrary unequal strings no longer satisfy the Gate. Passed Review Iterations resolve subject/Reviewer references against `provenance.yml`, require at least `recorded` assurance, require correct Roles and revision binding, and reject shared Execution/Context. Documentation explicitly limits Core claims: self-recorded provenance is durable consistency evidence, not cryptographic/external proof; `verified` is the stronger observer-backed level.

## Final execution

Final `pytest -q`, `forge validate`, `forge doctor`, and Distribution Verification results are populated after this artifact set is committed and the final Resolution HEAD executes.

## Strict Review boundary

Verification success, when obtained, will only establish that the Resolution implementation and distribution checks are green. It will not constitute Strict Re-review. Review Iteration 2 remains `pending` and must be executed in a Reviewer Execution/Context independent from `resolution-001`.
