---
forge:
  artifact: test_design
  schema: 1
change: CHG-0031
status: complete
---

# Test Design — CHG-0031 Chat Cadence Guidance Revalidation

- Verify both workflow projections are byte-identical.
- Verify the guidance retains `non-binding`, stage-transition examples, and
  the technical-enforcement disclaimer.
- Verify no runtime or normative Forge files are changed.
- Run `forge validate`, `git diff --check`, and the focused Adapter projection
  tests.

TDD is not applicable because this is documentation-only revalidation.
