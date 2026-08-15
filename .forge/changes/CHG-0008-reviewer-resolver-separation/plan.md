# Plan — CHG-0008

## Preserved historical plan
1. Preserve Strict Review findings and verdicts as normative input rather than rewriting history.
2. Keep Protocol 1 semantics frozen and place stronger review-independence semantics under integer Protocol 2.
3. Maintain repository-native provenance with explicit assurance and logical/concrete revision binding.
4. Preserve FAST/STANDARD/FULL quality invariants and provider-independent local operation.

## Resolution 3 — Strict Review Iteration 3
1. Confirm PR/branch/HEAD, `resolution-002`, `review-003`, frozen Resolution 2 subject, and workflow state.
2. Record Specification Drift for R006 before finalizing the new behavior.
3. Add a dedicated TDD cycle whose causal RED proves the pre-fix validator accepts a dirty reviewable workspace.
4. Model a single effective reviewable workspace delta from committed, staged, unstaged, deletion/rename, and Git-visible untracked Git state.
5. Keep the review-control exception exact and Change-local; adversarially test rename, symlink, lookalike, directory, and same-basename paths.
6. Preserve Protocol 1 and R001-R005 regressions plus Protocol 2 FAST/STANDARD/FULL behavior.
7. Diagnose the independent `Tests` CI regression without weakening tests or workflows and correct its root cause.
8. Update Protocol 2 Specification, Engineering Contract, Review Policy, ADR-0008, Architecture, Codex projection, traceability, TDD evidence, Verification, CHANGELOG, and knowledge capture.
9. Run full Tests and Distribution Verification, including wheel build, isolated install, offline init/validate/doctor, Adapter loading, and dependency audit.
10. Finalize all reviewable Resolution 3 material, create a new immutable Git subject, and record it prospectively as `resolution-003` with `recorded` assurance.
11. After the freeze, change only exact review-control metadata, prepare `review-004` pending without Reviewer provenance, and dogfood the dirty-subject validator plus final CI.
12. Stop at the Resolver boundary. Do not perform, approve, merge, or certify Strict Review Iteration 4.
