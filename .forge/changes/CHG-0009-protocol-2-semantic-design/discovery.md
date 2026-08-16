---
forge:
  artifact: discovery
  schema: 1
change: CHG-0009
status: complete
---

# Discovery — CHG-0009

## Repository reality

The analysis base is `70841bd77bd0128c48deda73b24708c3e5e3c461` on `main`. Repository-native Changes currently occupy CHG-0001 through CHG-0008; CHG-0009 was unallocated when this Change was created.

Protocol 1 remains Stable and frozen by C-045/C-046. `forge/change@1` does not require a `protocol` field and retains historical conceptual Reviewer/Resolver separation.

Protocol 2 already exists. `protocol/compatibility.md` states that Protocol 2 strengthens Strict Review from conceptual Role separation to revision-bound independent Execution and Execution Context provenance. Active Protocol 2 Changes use `forge/change@2`, declare `protocol: 2`, and may coexist with completed historical Protocol 1 Changes.

The schema catalog already includes `forge/change@2`, `forge/execution-provenance@1`, and `forge/policy/review@2`. Protocol 2 canonical resources exist under `protocol/versions/2/`.

## Compatibility boundary already established

C-045 requires an integer Protocol identifier to preserve the meaning and minimum obligations of existing valid instances. C-046 requires a new integer identifier when a Change removes or weakens an invariant, changes an existing required field or Gate meaning, or invalidates a previously valid conforming instance.

`protocol/compatibility.md` additionally identifies as breaking: making optional evidence mandatory, changing stage/Gate semantics, changing Adapter interval semantics, and allowing quality obligations to be bypassed. Schema suffixes cannot conceal a Core semantic break.

Therefore adding a new `MUST` is not automatically compatible. The decisive question is whether the obligation was already unavoidable for every conforming instance under the current integer Protocol. If a valid historical instance could lack the newly required state or evidence, the stronger rule is not compatible maintenance.

## Evidence and provenance already present

Protocol 1 already uses evidence in bounded contexts: valid RED requires observed execution evidence; BLOCKER/MAJOR findings require sufficient evidence; passing tests alone are insufficient for Verification; Manifest state must reflect repository reality. However Protocol 1 does not define a universal claim/evidence model and expressly does not retroactively require independent Execution IDs, Context IDs, revision-bound provenance, or a provenance ledger.

Protocol 2 introduces an execution provenance artifact and revision-bound Strict Review provenance, but its published scope is review independence rather than a universal evidence ontology for every lifecycle claim.

## Gate semantics

FULL currently requires `specification_review_passed` before Architecture, and requires Verification and Strict Review before Completion. Protocol 1 does not generically define every Gate PASS as bound to an immutable revision or automatically invalidated after later mutation.

Protocol 2 has stronger revision binding for Strict Review. Generalizing that behavior to Specification Review, Verification, Completion readiness, or arbitrary downstream Gates would add semantics beyond Protocol 2's currently published review-independence boundary.

## Authority

Protocol 1 already establishes several precedence rules: canonical Protocol definitions are authoritative; project extensions may strengthen but not weaken them; Harness Adapters consume rather than redefine effective configuration; Harness conventions cannot replace Protocol semantics. This supports a compatible authority-model clarification, but same-level conflict resolution and prompt/chat precedence remain under-specified.

## Scope, assumptions, and confidence

Existing invariants constrain silent Requirement mutation, escalation, repository truth, false Completion, explicit trade-offs, and durable knowledge. They do not currently require universal assumption inventories, explicit scope-expansion records for every material discovery, rollback analysis for every irreversible operation, or a machine-readable engineering-confidence score.

## Design consequence

CHG-0009 must analyze three boundaries, not two:

1. compatible Protocol 1 maintenance;
2. semantics already established by Protocol 2;
3. new mandatory semantics that would invalidate valid Protocol 1 or Protocol 2 instances and therefore require a future integer Protocol identifier.

For clarity, this Change refers to that hypothetical next breaking boundary as **Future Protocol**. It does not reserve or assign integer Protocol `3`; that identifier may only be established by a later Change that actually creates the new Protocol contract.
