# Plan — CHG-0008 Resolution of Strict Review Iteration 1

1. Preserve Strict Review Iteration 1 as normative REQUEST CHANGES input.
2. Record Specification Drift before Resolution implementation: Protocol 2 boundary, provenance ledger, assurance levels, iteration-aware Review.
3. Add test-first regressions for R001-R004, including all Flows, forged evidence, revision mismatch, re-review contamination, and downgrade resistance.
4. Restore Protocol 1 historical semantics and schemas; introduce versioned Protocol 2 canonical resources.
5. Add repository-native execution provenance and revision-bound Review Iterations.
6. Make validation, Doctor, and Codex projection resolve the selected Protocol before applying version-specific semantics.
7. Record this Resolution execution prospectively without fabricating historical Implementation/Review provenance.
8. Run full tests, `forge validate`, `forge doctor`, and Distribution Verification on the final Resolution HEAD.
9. Return CHG-0008 to `strict_review` with Review Iteration 2 pending. Do not perform or certify re-review in this Resolver execution.
