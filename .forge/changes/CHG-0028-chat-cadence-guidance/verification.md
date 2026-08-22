---
forge:
  artifact: verification
  schema: 1
change: CHG-0028
status: pending
---
# Verification — CHG-0028

## Planned evidence

- Confirm both workflow templates contain the same cadence paragraph and
  remain byte-identical.
- Confirm the paragraph is explicitly non-binding and preserves the existing
  technical-enforcement disclaimer.
- Confirm the diff changes only the two workflow templates, this Change's
  artifacts, and the roadmap item #8.
- Run `forge validate` and `git diff --check`.

TDD is not applicable: this Change adds no executable behavior.
