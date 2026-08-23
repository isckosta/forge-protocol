---
forge:
  artifact: review
  schema: 1
change: CHG-0030
status: active
---

# Review — CHG-0030 Forge Experience Reporting

## Verdict

**PENDING — Resolution Verification is required for the provenance migration.**

## Iteration 1 — FAIL

The independent review of frozen subject `258f62bc26cc5d4c807e2ba09139eff5c1377011` found two BLOCKERs and
three MAJORs: unsupported manifest metadata and incomplete TDD schema
evidence; privacy input was not guarded; malformed reports could crash
recording; verification/documentation metadata was inaccurate. The findings
were recorded and addressed in `resolution-001` at frozen subject `e03a8b2e48e4b89214ca32f73b7e36d288ffc6f7`.

## Iteration 2 — FAIL

The independent Resolution Verification of frozen subject `e03a8b2e48e4b89214ca32f73b7e36d288ffc6f7` confirmed
the prior fixes but found three remaining MAJORs: evidence-item sanitization,
symlinked `dogfooding` ancestor containment, and deep follow-up candidate
validation. These are addressed in `resolution-002` at frozen subject
`358bf848bc45c25406931091e16cc4c0adf9beea`.

## Iteration 3 — PASS

Review the exact `b5507b6e57523b1353f1072d078f174b80f0a3eb` subject independently.
The reviewer must verify the
resolution scope and re-run the focused/contract tests, with special attention
to default-off configuration, symlink/path safety, deep report validation,
sensitive-input rejection, TDD schema conformance, and Documentation Impact.

The independent cold review passed against the exact frozen subject
`b5507b6e57523b1353f1072d078f174b80f0a3eb`. It verified clean isolation,
`forge validate`, `forge experience validate`, schema/contract/CLI,
golden-path, Adapter, privacy, malformed-input, and symlink containment
checks. No material finding remains.

**PASS (final).**

## Iteration 4 — PENDING

The resolution subject adds a fail-closed migration path for historical
abbreviated Git subject SHAs. Verify that matching full SHAs are accepted,
non-matching or malformed historical values remain rejected, and the focused
regression suite plus `forge validate` pass against the frozen subject.

## Iteration 5 — PENDING

The follow-up subject isolates the validator change that prevents unrelated
commits merged between frozen subjects from entering a Resolution Delta.
Review the exact frozen subject recorded as `resolution-004`.
