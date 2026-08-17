---
forge:
  artifact: verification
  schema: 1
change: CHG-0008
status: passed
---
# Verification — CHG-0008 Resolutions

Verification evidence is Resolver evidence only; it is not Strict Review acceptance.

## Historical Resolution 3 — R006
Resolution 3 established the effective reviewable workspace freeze: committed, staged, unstaged, deletion/rename, and Git-visible untracked state are combined from the Git repository root; exact Change-local `manifest.yml`, `provenance.yml`, and `review.md` are the only review-control path exceptions and must remain regular non-symlink files. Its causal GREEN was `eaa6c481e5ea9a08c3f4e234feb6d1cbf871ee99`, Tests run `31904623010`, with Distribution Verification run `31904622991`. Final Resolution 3 regressions passed at Tests run `31904809568` and Distribution Verification run `31904809691`. Strict Review Iteration 4 subsequently accepted R006 for its original dirty-workspace defect and found R007 instead.

## Historical Resolution 4 — R007
R007 established immutable subject provenance authority from Git history rather than the mutable current `provenance.yml`. Its causal RED was `73f865ff712647c24a0203c530703d69c2513ae8` / Tests run `31906413392`; GREEN was `80292e6acc54a59e15bf4c4919b9286cc2ba5dd6` / Tests run `31906638536`, with Distribution Verification `31906638462`. Strict Review Iteration 5 preserved that fix and found R008 in Review Iteration history enforcement.

## Resolution 5 — R008 root cause
`_validate_protocol2_review_provenance` resolved the first committed Review Iteration subject binding only when the **current** Iteration status was `pending` or `passed`. A historical `failed` Iteration therefore skipped the append-only history comparison and could retain its ID/status while redirecting `revision` or `subject_provenance`.

The defect was status coupling: historical subject identity belonged to the verdict branch instead of to the committed Review Iteration identity. A second adversarial probe showed that, after removing the status gate, replacing the committed Iteration ID with a new ID could still avoid per-ID lookup unless previously established identities were preserved explicitly.

## TDD-011 causal RED
Primary tests-only RED commit `1d70b1282b7c0dd2f5015439281fd493954ca87f`, Tests run `31917557112`, job `95091910991`:

- setup and dependency steps passed;
- failure occurred in `Run tests`;
- regressions exercise failed-Iteration `revision`, `subject_provenance`, simultaneous binding rewrites, status changes, legitimate lifecycle metadata updates, and addition of a genuinely new Iteration;
- vulnerable behavior was acceptance of historical failed subject redirection because history authority was not consulted for `failed` status.

Supplemental tests-only RED commit `410dc2efe32e1b3c96aaf8f9378d052f7566b68b`, Tests run `31917909131`, demonstrated the remaining Iteration-ID replacement bypass. Distribution Verification remained green for that tests-only commit.

## Implementation and authority boundary
Core now resolves committed Review Iteration subject authority for every bound Protocol 2 Iteration ID regardless of verdict. The first valid committed representation establishing `iteration.id + revision + subject_provenance` is the immutable subject identity for that historical Iteration. Current content must preserve the logical revision and subject provenance for the same ID, and every previously established bound Iteration ID must remain present; a replacement ID cannot silently reinterpret history.

Lifecycle/review metadata is intentionally not frozen wholesale. Legitimate transitions such as `pending -> failed`, evidence-gap updates, aggregate counters, and append of a genuinely new Iteration continue to work when subject identity is unchanged and the Protocol otherwise permits the transition. The existing effective workspace freeze remains lifecycle-aware so a failed Review can be followed by Resolver work for the next Resolution without mutating what the failed Review historically examined.

The authority comes from local Git history. A malformed YAML snapshot cannot establish a valid binding by itself; lookup may continue to a later valid committed representation for the requested Iteration. If complete history is unavailable or the required authority remains unsafe/ambiguous, validation fails closed. Duplicate identities, shallow history, Git failures, inaccessible state, and unresolved authority do not become successful validation.

No CHG-0008-specific, review-005-specific, resolution-004-specific, status-failed-only, or SHA-specific enforcement exists in the validator.

## GREEN and regression preservation
Final implementation GREEN before Resolution evidence updates: `66c88be244617864f9e8aea54f044e4bc6eaaa91`.

Tests run `31918012008`, job `95093064159`:

- `pytest -q`: `228 passed in 5.91s`;
- `forge validate`: `Forge project is valid`;
- `forge doctor`: PASS for Git availability/repository, Forge initialization, project configuration, Protocol 2 compatibility, FAST/STANDARD/FULL canonical Flows, and canonical Protocol 2 Engineering Contract.

Distribution Verification run `31918012004`: PASS.

The same suite retains R005 concrete immutable revision mismatch tests; R006 committed/staged/unstaged/deleted/rename/copy/Git-visible-untracked workspace regressions and exact metadata allowlist tests; R007 historical subject-provenance rewrite/removal/replacement/shallow-history regressions; Protocol 1 compatibility; Protocol 2 FAST/STANDARD/FULL validation paths; schema/contract tests; CLI validation and Doctor. No metadata exception was broadened by basename, substring, suffix, or directory.

## Normative impact
No Protocol/schema normative change was required for R008. Existing Protocol 2 authority already requires append-only Review/provenance history and stable revision binding. Resolution 5 corrects Core enforcement and records the clarified architectural distinction between immutable historical subject identity and mutable lifecycle metadata. Protocol 1 semantics remain unchanged.

## Assurance and freeze procedure
Resolution 5 uses repository-native `recorded` provenance only. No provider execution ID, external attestation, or `verified` assurance is claimed.

All implementation, tests, architecture, TDD evidence, verification and knowledge changes belong to the Resolution 5 reviewable subject and must be finalized before freeze. The final reviewable commit becomes `chg-0008-resolution-005`'s frozen subject. A later Change-local `provenance.yml` metadata commit will append `resolution-005` pointing back to that exact SHA. Historical `review-001` through `review-005` remain unchanged; no `review-006`, Strict Review PASS, Completion, approval, or merge is produced by this Resolver.
