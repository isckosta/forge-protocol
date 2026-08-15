---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0008
status: approved
---

# Test Strategy — CHG-0008

## Historical cycles
TDD-001 through TDD-008 remain preserved. TDD-006 covers the Protocol 1/2 provenance boundary, TDD-007 covers Protocol-aware Codex projection, and TDD-008 covers R004/R005 concrete immutable revision binding and committed post-freeze mutation.

## TDD-009 — R006 effective reviewable workspace freeze
R006 requires a dedicated behavioral cycle. The causal RED uses a valid Protocol 2 fixture with valid subject provenance and a frozen Git commit, mutates only reviewable working-tree material, and expects `forge validate` to reject C-026. Environment, dependency, schema, and fixture failures do not count as RED.

The minimum causal case is an unstaged tracked modification. The expanded adversarial matrix covers:

- clean frozen workspace → PASS;
- committed reviewable mutation → FAIL;
- unstaged tracked mutation → FAIL;
- staged tracked mutation → FAIL;
- Git-visible untracked reviewable file → FAIL;
- tracked deletion → FAIL;
- tracked rename → FAIL;
- exact Change-local `manifest.yml`, `provenance.yml`, and `review.md` metadata mutation → PASS;
- reviewable artifact inside the same Change → FAIL;
- metadata belonging to another Change → FAIL;
- Git-ignored temp/cache file → PASS;
- rename of reviewable material to an allowlisted basename/path → FAIL;
- lookalike metadata path such as `review.md.bak` → FAIL;
- symlink substitution at a review-control path → FAIL.

The suite also preserves Protocol 1 compatibility; Protocol 2 FAST/STANDARD/FULL behavior; wrong immutable ref; wrong logical revision; forged provenance; shared Execution; shared Context; and R004/R005 regressions.

## CI regression diagnosis
The Iteration 3 `Tests` failure is investigated independently from R006. A failing canonical-YAML contract test must be fixed at the artifact that violates YAML/schema semantics; the test or workflow must not be weakened or skipped.

## GREEN and verification
GREEN requires the complete `pytest -q` suite plus Distribution Verification. Distribution Verification must continue to exercise wheel build, isolated install, offline init/validate/doctor, Adapter schema/loading, and dependency audit. Final review-control metadata must then be dogfooded by the same validator so the exact metadata allowlist does not invalidate the newly frozen subject.

Passing Verification is Resolution evidence only. It is not Strict Review acceptance.
