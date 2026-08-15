---
forge:
  artifact: tasks
  schema: 1
change: CHG-0008
status: active
---

# Tasks — Verifiable Reviewer/Resolver Separation

- [x] T-001 Inspect canonical FULL flow, Review Policy, Change schema, Contract, Specification, validator, Codex projection, and CHG-0007 structure.
- [x] T-002 Create/use the exact structurally valid FULL same-session fixture and RED CLI test.
- [x] T-003 Observe valid RED for the missing C-026 semantic behavior.
- [x] T-004 Add semantic regression for claimed isolation with identical session references and observe RED before implementation.
- [x] T-005 Implement C-026 semantic CLI validation for same-session and inconsistent identical-reference evidence.
- [x] T-006 Make FULL `reviewer_identity` structurally mandatory and preserve all three required inner fields.
- [x] T-007 Update Review Policy minimums and supporting policy schema.
- [x] T-008 Rewrite C-026 and align Protocol Specification §25 semantics.
- [x] T-009 Update Codex STANDARD/FULL projection to require isolated execution and distinct session references.
- [x] T-010 Add/update ADR and CHANGELOG with operational-independence limits and breaking-change disclosure.
- [x] T-011 Preserve completed historical Change files without retroactive reviewer evidence.
- [ ] T-012 Resolve the incompatibility between the new mandatory FULL field and Protocol 1 C-045/C-046/canonical historical manifests without weakening tests or fabricating evidence.
- [ ] T-013 Restore full-suite and repository `forge validate` success after T-012 is resolved.
- [ ] T-014 Obtain independent Strict Review; only that execution may create `review.md` and record compliant reviewer identity evidence.
- [ ] T-015 Resolve any blocking findings and complete the Change only after compliant re-review.
