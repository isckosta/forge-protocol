---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0011
status: approved
---

# Test Strategy — CHG-0011

## TDD-012 — legacy manifests are unaffected (regression baseline, RED first)
RED: assert `_validate_resolution_verification`-equivalent path returns no
findings for a fixture manifest with zero `kind`-classified iterations
(reuse `CHG-0008`'s and `CHG-0010`'s real manifests as fixtures, byte-for-
byte). This RED is causal: written against the not-yet-existing function name
before it exists, executed, and fails for `AttributeError`/`ImportError`
reasons — the expected "absent behavior" failure, not an environment
failure.

## TDD-013 — successful scoped convergence (golden path)
Initial Review → BLOCKER finding → Resolution declares `scope`/`targets`
covering exactly its real delta → `resolution_verification` Iteration,
independent Execution/Context, Resolution Delta ⊆ scope → PASS. Validates
clean.

## TDD-014 — unresolved original finding (class A)
Same as TDD-013 but the Resolution Delta does not actually fix the target
Finding (Reviewer records class A, `status: failed`,
`new_material_findings: 0` since the same known Finding recurring is not
independent new material). Validates clean as `failed`; a second such cycle
does not, by itself, trip the Convergence Limit (only B/C findings count) —
asserted explicitly, since this is the one case most likely to be
mis-implemented as "any failure increments the counter."

## TDD-015 — resolution regression (class B)
Resolution fixes the target Finding but the delta introduces a new defect
directly inside that delta. `new_material_findings: 1`,
`finding_classes: [resolution_regression]`. Validates clean as `failed`,
`full_review_required` absent/false (in-scope defects do not require Full
Review Escalation — they get another scoped Resolution Verification).

## TDD-016 — out-of-scope material mutation (class C) — the R3.4 case
Resolution's actual Git delta includes a path never listed in declared
`scope`. Assert:
- `status: passed` with the uncovered path present → validation fails
  (mechanical bypass attempt).
- `status: failed`, `full_review_required: true` → validates clean.
- The Iteration immediately after is `kind: resolution_verification` again
  (not `initial_review`) → validation fails (FR-010).
- The Iteration immediately after is `kind: initial_review` → validates
  clean, and Core does not require it to re-declare scope (Initial Review is
  unrestricted by definition).

## TDD-017 — trivial incidental mutation is still declared, not exempted
A Resolution touches `traceability.yml` as a mechanical side effect of an
in-scope change but does not list it in `scope`. Assert this still fails as
an uncovered path (Specification's Finding taxonomy explicitly rejects a
free "triviality" carve-out from the mechanical containment check — only
declared scope is exempt).

## TDD-018 — legitimate related new finding vs. review amplification
Two adjacent regression-chain fixtures modeled directly on CHG-0008's real
R004→R005 and R006→R007 chains (each new finding causally inside the prior
Resolution's own delta, `finding_classes: [resolution_regression]` both
times). Assert the derived convergence run does NOT reach the limit merely
because two consecutive Verifications failed — it only reaches the limit
because `new_material_findings > 0` two times *in a row*, which this
legitimate chain also technically satisfies at 2. This test exists to prove
the Specification's own claim (Discovery: "CHG-0008's chain would not have
been wrongly flagged") is bounded correctly: it asserts the mechanism
produces `review_convergence_failed` at exactly 2, and separately documents
(non-blocking OBSERVATION in `knowledge-capture.md`) that the counter cannot
distinguish "still-legitimate 2-deep hardening chain" from "amplification" —
that distinction is why FR-014 returns authority to the engineer instead of
Forge unilaterally aborting the Change. This is the intended design, not a
gap: the counter is a *rate limiter with mandatory check-in*, not a
correctness oracle.

## TDD-019 — latent unrelated finding (class D)
`finding_classes: [unrelated_latent_finding]`, `new_material_findings: 0`,
Finding recorded with class D in `review.md`, `status: failed` only because
of an unrelated class A finding also present in the same Iteration (D alone
never fails an Iteration by itself per FR-009 — assert a fixture with *only*
a MINOR class D finding and no A/B/C finding still validates as `status:
passed`, i.e., pure class D does not force `failed`).

## TDD-020 — provenance/shape adversarial matrix
`resolution_verification` first in `iterations` (rejected); subject role
`implementation` (rejected); subject missing `scope` (rejected); subject
missing `targets` (rejected); `new_material_findings` negative (rejected);
`accept_residual_risk` without `.forge/forge.yml` permission (rejected);
`accept_residual_risk` with permission present (accepted); declared
`convergence.state`/`consecutive_unconverged_verifications` disagreeing with
Core's derived value (rejected, proves INV-003 — the counter is not
self-declared truth).

## Verification
GREEN requires the complete `pytest -q` suite (existing suite unmodified in
behavior — TDD-012 is the explicit regression proof), `forge validate` and
`forge doctor` against this repository, and schema validation of both
modified `.schema.json` files against their own fixtures plus the existing
CHG-0008/CHG-0010 manifests. Passing Verification is Resolution evidence
only, not Strict Review acceptance.
