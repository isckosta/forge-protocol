---
forge:
  artifact: tasks
  schema: 1
change: CHG-0036
status: complete
---

# Tasks — CHG-0036 Merge Readiness Gate

- Implement the reusable Merge Readiness evaluator and deterministic CLI.
- Add centralized materiality policy, revision/change resolution, and
  repository-native evidence binding.
- Add regression tests for lifecycle, provenance, revision, and exit-code
  behavior.
- Integrate the evaluator into full-history GitHub Actions and document the
  external branch-protection boundary.
