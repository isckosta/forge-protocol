# Changelog

All notable Forge changes will be documented here.

CLI releases will follow Semantic Versioning when releases begin. Protocol versions are tracked independently.

## Unreleased

### Freeze check exempts complete Changes

Fixed:

- `forge validate`'s Protocol 2 review-subject freeze-drift check no longer
  fires for a passed Review Iteration once its Change's `state.current` is
  `complete`; unrelated, expected commits from other Changes continuing
  development on the same branch no longer resurrect a closed, already
  independently-reviewed Change as a validation failure.

Known limitation (accepted, documented trade-off — see CHG-0012's
`specification-drift.md`):

- once a Change's `state.current` reaches `complete`, the freeze-drift check
  no longer inspects further activity on that Change's own previously
  reviewed files, including a hand-edited `state.current` that was never
  genuinely earned through Completion. This mirrors Protocol 2's existing
  `assurance: recorded` (self-declared) trust model rather than closing a
  gap no other layer of `forge validate` defends against either.

### Adapter CLI and Codex Installation UX

Added:

- an Adapter CLI command group — `forge adapter list`, `configure`, `plan`,
  `install`, `validate`, `doctor`, `update` — completing the documented
  `forge init` → `forge adapter install codex` v1 onboarding path;
- deterministic plan-before-mutation, ownership-aware publication, collision
  and stale-state protection, drift diagnostics, and safe/idempotent updates
  for Adapter installation through the generic Adapter Core;
- stable `E_FORGE_*` exit codes for publication conflicts, unsafe paths, and
  stale on-disk installation records, replacing internal-error fallthrough
  for expected, well-understood domain/validation failures.

Fixed:

- a class of TOCTOU (time-of-check/time-of-use) defects in adapter
  publication where a path resolved once and reused across preflight,
  authorization, mutation, and rollback allowed a directory-to-symlink swap
  to redirect installation-record reads/writes, or a rollback restore,
  outside the repository root, including cases that could forge the
  authorization used for a publication or exfiltrate original file content
  during rollback. Closed through six independent Strict Review iterations
  (`.forge/changes/CHG-0010-adapter-cli-codex-ux/review.md`) that each
  re-resolve the affected path immediately before use rather than reusing a
  path captured earlier in the operation.

### Protocol 2 — Verifiable Review Independence

Added:

- integer **Protocol 2** as the compatibility boundary for mandatory independent Strict Review Execution and Execution Context;
- version-specific Protocol 2 Contract, Specification, and Review Policy resources under `protocol/versions/2/`;
- `forge/execution-provenance@1`, a provider-independent repository-native ledger for Implementation, Resolution, and Review execution provenance;
- explicit provenance assurance levels: `claimed`, `recorded`, and `verified`, with at least `recorded` required for Protocol 2 `review_passed`;
- iteration-aware Protocol 2 Review state in `forge/change@2`, linking each passed Review to subject and Reviewer provenance for the revision under review;
- FAST, STANDARD, and FULL Protocol 2 validation for missing/forged provenance, wrong revision binding, shared Execution, shared Context, partial evidence, contaminated re-review, active schema downgrade, and dirty frozen review subjects;
- effective Git review-subject freeze validation across committed, staged, unstaged, deleted/renamed, and Git-visible untracked reviewable paths while respecting Git ignore rules;
- exact Change-local review-control metadata exception for `manifest.yml`, `provenance.yml`, and `review.md`, with rename/lookalike/symlink bypass protection;
- Protocol-aware canonical Contract resolution in validation and Doctor;
- Protocol-aware Codex projection so Protocol 2 provenance/freeze semantics are projected for FAST/STANDARD/FULL without leaking into Protocol 1.

Changed:

- restored Protocol 1 C-026, Specification §25, Review Policy, and `forge/change@1` to their historical pre-CHG-0008 semantics instead of retroactively strengthening Protocol 1;
- Protocol 2 review-subject binding now describes the effective reviewable workspace, not only committed `<subject>..HEAD` history;
- Codex Adapter compatibility interval covers integer Protocols 1 and 2 and now instructs Protocol 2 harnesses to finish reviewable material, ensure the effective workspace is clean, freeze, record provenance, and re-check the freeze before independent Review;
- compatibility documentation explicitly distinguishes Protocol version from artifact schema version and documents the Protocol 1 → 2 breaking boundary.

Security/trust boundary:

- pairwise-distinct execution/context strings are no longer treated as sufficient evidence of independence;
- post-freeze staged, unstaged, untracked, deletion, rename, and path-based metadata bypasses cannot silently alter the Protocol 2 subject presented for Review;
- Forge Core verifies durable provenance linkage and consistency but does not claim self-recorded provenance is cryptographic/external proof; `verified` provenance is reserved for observer-backed evidence.

Migration:

- completed historical Protocol 1 Changes remain unchanged and require no fabricated provenance;
- active Protocol 2 Changes use `forge/change@2` and may not downgrade to `forge/change@1` to bypass the Strict Review Gate.

### Protocol 1 Contract Freeze

Changed:

- stabilized the human-readable Protocol label as `1` while preserving integer Protocol compatibility;
- published Protocol 1 compatibility, breaking-change, and deprecation rules;
- added a portable schema catalog and offline contract coverage for canonical schemas and repository-native artifacts;
- migrated historical artifact structures to their canonical schemas without changing recorded engineering outcomes.

### Foundation

Added:

- Forge Manifesto and Core Architecture;
- Forge Core Protocol, Engineering Contract, FAST/STANDARD/FULL Flows, TDD-first development model, RED → GREEN → REFACTOR lifecycle, Verification, adversarial Strict Review, and canonical Policies/Schemas;
- official Python CLI with `version`, `init`, `validate`, and `doctor`;
- repository-native Change lifecycle, configuration resolution, offline packaged Protocol resources, Distribution Verification, Harness Adapter architecture, Codex Adapter, and deterministic Adapter planning/publication/drift detection.
