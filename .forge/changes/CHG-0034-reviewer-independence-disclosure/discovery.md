---
forge:
  artifact: discovery
  schema: 1
change: CHG-0034
status: pending
---

# Discovery — CHG-0034 Reviewer Independence Disclosure

## Executive Summary

The remediation table has only item #10 open. The sequencing note and the
last-assigned-Change paragraph are stale: they still point to item #2 and
CHG-0024, while the repository has already reached CHG-0033 and this Change
has been scaffolded as CHG-0034. The next remediation item is therefore
`reviewer-independence-disclosure`.

The Contract gap is real but narrow. C-026 requires conceptual
Reviewer/Resolver separation, and C-037 prohibits dependence on a specific AI
provider; neither states that the verifiable independence boundary is a
distinct Execution and Execution Context rather than a distinct vendor or
model. Existing CHG-0021 review provenance demonstrates that independent
reviews can run with the same underlying provider/model as Implementation.
The evidence supports an explicit limitation disclosure, not a claim that
execution independence is ineffective.

## Investigation

- `protocol/contract/engineering.md:82-83` defines C-026 as
  Reviewer/Resolver separation between conceptual Roles.
- `protocol/contract/engineering.md:115-116` defines C-037 as provider
  independence for the Protocol itself. Neither rule states the distinction
  between execution/context independence and vendor/model independence.
- `protocol/specification.md` defines Strict Review as an adversarial stage
  and the Contract requires it, but does not add a vendor/model boundary.
- `CHG-0021`'s `provenance.yml` and `review.md` provide concrete evidence of
  distinct Reviewer execution/context records while the review history does
  not establish vendor/model diversity. This is self-recorded repository
  evidence, not cryptographic or external attestation.
- The Adapter projection already communicates the Execution/Execution
  Context independence requirement. The canonical Contract is the missing
  durable authority for its actual scope.
- `CONTRIBUTING.md:35-37` requires an RFC before materially changing the
  Engineering Contract. This Change proposes no new obligation, removes no
  obligation, changes no Gate, and does not invalidate Protocol 1 instances;
  it makes an existing guarantee's evidence boundary explicit. On that
  basis, the clarification is non-material and an RFC is not required. If
  Specification authoring would add a vendor/model requirement or alter
  review semantics, the Change must stop and escalate to an RFC instead.
- The requested optional hint-free mode is not necessary to disclose the
  current guarantee and would introduce new review semantics. It is deferred
  as future work.

## Recommendation

Proceed as a STANDARD, non-behavioral Contract/documentation clarification.
Keep TDD not applicable because the planned change has no executable behavior;
record that exception explicitly. Update the Contract, Adapter-facing
projection only if its wording is inconsistent with the clarification, and
correct the roadmap metadata. Do not begin those implementation edits until
the Plan receives human approval.
