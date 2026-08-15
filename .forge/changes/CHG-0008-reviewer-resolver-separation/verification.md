---
forge:
  artifact: verification
  schema: 1
change: CHG-0008
status: passed
---
# Verification — Strict Review Iteration 3 Resolution

Resolution implementation and Verification are passed; this is not Strict Review acceptance.

## Scope
This Resolution addresses CHG-0008-R006 and the unrelated `Tests` workflow regression observed after Strict Review Iteration 3. R001-R005 and all historical REQUEST CHANGES verdicts remain preserved.

## R006 root cause
The pre-Resolution freeze helper inspected only `git diff <frozen>..HEAD`. Consequently a frozen subject could diverge in the effective workspace without a new commit: staged, unstaged, deleted/renamed, and Git-visible untracked reviewable paths were invisible to C-026 validation.

## CI `Tests` root cause
The Iteration 3 review-control commit wrote the R006 description as a plain YAML scalar containing `MAJOR:`. PyYAML rejected the canonical `manifest.yml` with `ScannerError: mapping values are not allowed here`. The sole failing test in the diagnostic run was `test_canonical_yaml_instances_satisfy_their_declared_schemas`. The artifact was repaired with a block scalar; the contract test and workflow were not weakened, skipped, or removed.

## TDD-009 causal RED
The first R006 test was authored before the production fix, but that initial CI run was contaminated by the malformed historical manifest and is not counted as causal RED. After the manifest was repaired, the validator alone was temporarily restored to the pre-R006 commit-only implementation while the R006 tests remained unchanged.

RED commit `d845f0a270648f10e7106184db4a6970bad8132b`, Tests run `31904557628`, job `95060254120`:

- command: `pytest -q`;
- result: `9 failed, 201 passed in 3.93s`;
- causal failures: unstaged tracked mutation, staged tracked mutation, untracked reviewable file, tracked deletion, tracked rename, same-Change reviewable artifact, rename-to-allowlisted path, metadata lookalike, and symlink substitution;
- causal reason: each mutation was accepted with validator exit code `0` when C-026 expected exit code `2`.

## Implementation
Core now computes one `reviewable workspace delta since frozen subject` from the Git repository root. It unions machine-readable NUL-delimited results for:

- committed `<subject>..HEAD` delta;
- staged/index delta;
- unstaged working-tree delta;
- Git-visible untracked paths via `git ls-files --others --exclude-standard`.

Rename/copy parsing keeps both source and destination paths; tracked deletions remain visible. `.gitignore` is respected for untracked paths. The only excluded paths are the exact repository-root-relative `manifest.yml`, `provenance.yml`, and `review.md` of the Change whose subject is frozen, and only while those paths remain regular non-symlink files. Metadata in another Change, same-directory reviewable artifacts, lookalikes, rename targets, directory substitutions, same basenames outside the Change, and symlink substitutions remain reviewable.

The invariant is enforced by `forge validate`, not delegated to Doctor. Protocol 1 behavior is unchanged. Protocol 2 FAST, STANDARD, and FULL use the same rule.

## Causal GREEN
GREEN commit `eaa6c481e5ea9a08c3f4e234feb6d1cbf871ee99`:

- Tests run `31904623010`, job `95060410846`: PASS, `210 passed in 4.95s`;
- Distribution Verification run `31904622991`, job `95060410904`: PASS;
- wheel build: PASS;
- isolated wheel install: PASS;
- offline `forge init`: PASS;
- offline `forge validate`: PASS (`Forge project is valid`);
- offline `forge doctor`: PASS for Git availability/repository, Forge initialization, project schema, Protocol 2 compatibility, canonical FAST/STANDARD/FULL Flows, and canonical Contract;
- Adapter schema/loading probe: PASS;
- runtime dependency audit: PASS.

## Final pre-freeze regression checkpoint
After adding the two remaining explicit path-bypass regressions (`review.md/` directory and a same-basename `review.md` outside the Change), the complete reviewable Resolution 3 state was verified again:

- Tests run `31904809568`, job `95060859894`: PASS, `212 passed in 4.24s`;
- Distribution Verification run `31904809691`: PASS;
- the suite preserves committed post-freeze failure, wrong immutable ref, wrong logical revision, forged provenance, same Execution, same Context, Protocol 1 compatibility, and FAST/STANDARD/FULL Protocol 2 regressions.

## Frozen subject and provenance boundary
All remaining reviewable Resolution 3 artifacts are finalized before the final freeze. The exact immutable freeze SHA cannot truthfully be embedded into this reviewable file because that would create commit self-reference. The final subject is therefore the commit containing this evidence and all other reviewable Resolution 3 material; its exact Git SHA is subsequently recorded authoritatively by `resolution-003` in `provenance.yml`.

After that freeze, only Change-local review-control metadata may change. The final metadata state must be dogfooded with `forge validate`, `forge doctor`, the test suite, and final CI. `review-004` remains pending and receives no Reviewer provenance from this Resolver.
