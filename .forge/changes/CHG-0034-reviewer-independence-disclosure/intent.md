---
forge:
  artifact: intent
  schema: 1
change: CHG-0034
status: active
---

# Intent — CHG-0034 Reviewer Independence Disclosure

## Summary

Clarify the real scope of Forge's Reviewer independence guarantee and correct
the stale remediation-roadmap sequencing note.

## Problem

The Contract requires Reviewer/Resolver separation and provider independence,
but does not explicitly distinguish execution independence from
vendor/model independence. The roadmap's sequencing note also still claims
that item #2 is next even though items #2 through #9 are complete.

## Desired Outcome

Contributors and maintainers can accurately understand what Protocol 2
Reviewer independence proves today, without changing the existing
Reviewer/Resolver or provider-independence requirements. The remediation
roadmap identifies item #10 as the active next item and the real next Change
identifier.

## Scope

- Update the canonical Contract with a non-normative disclosure of the
  execution/context boundary and its vendor/model limitation.
- Evaluate whether the clarification is material under the RFC policy.
- Update the projected Harness-facing Contract guidance if required.
- Correct stale status/sequencing metadata in `ROADMAP-REMEDIATION.md`.
- Preserve evidence from prior independent reviews as supporting context.

## Out of Scope

- No change to C-026 or C-037's normative requirements.
- No new Review gate, vendor/model selection rule, or cryptographic
  attestation mechanism.
- No implementation of hint-free review mode unless the Specification proves
  it is necessary for this Change; otherwise record it as future work.
- No work from remediation items #2 through #9.

## Success Criteria

- The Contract explicitly states the guarantee and limitation without
  weakening existing invariants.
- The RFC-required-or-not decision is evidenced in Discovery and the
  Specification.
- The roadmap marks item #10 as active and points to CHG-0034; stale claims
  about the next identifier are corrected.
- `forge validate` passes and an independent Strict Review evaluates the
  frozen Change subject before Completion.
