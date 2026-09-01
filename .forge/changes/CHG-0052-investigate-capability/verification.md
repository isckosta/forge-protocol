---
forge:
  artifact: verification
  schema: 1
change: CHG-0052
status: pending
---

# CHG-0052 · Verification

## Result

**PENDING**

## Summary

State how many Acceptance Criteria were verified, how many passed, how many failed, and whether Manual Evidence or Limitations apply. When Result is SKIPPED or NOT APPLICABLE, state the rationale here, proportional to the Change — a skipped or inapplicable Verification is itself a claim that needs a reason.

## Acceptance Coverage

Reference each AC-xxx by id; do not reproduce its full text here.

| Acceptance | Requirement | Result | Evidence |
|---|---|---|---|
| AC-001 | FR-001 | PENDING | <evidence> |

## Requirement Coverage

Omit this section when Acceptance Coverage already expresses per-Requirement coverage; include it only when it adds information Acceptance Coverage does not.

## Test Evidence

Record commands, exit status, and a short summary — not full logs. When `tdd-evidence.yml` already records RED and GREEN for a TDD-xxx cycle, reference it by id instead of renarrating the sequence.

## Forge Evidence

Record only what the command actually guarantees.

## Manual Evidence

Include this section only when a real manual verification occurred; keep it distinct from Test Evidence and Forge Evidence.

## Compatibility and Limitations

Record confirmed compatibility impact and any real limitation. Do not pad this section when neither applies.

## Conclusion

State the outcome for the implemented scope. Do not imply Completion when Result is FAIL or SKIPPED, or when Review remains pending.
