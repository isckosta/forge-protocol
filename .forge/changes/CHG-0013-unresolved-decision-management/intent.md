---
forge:
  artifact: intent
  schema: 1
change: CHG-0013
status: complete
---

# Intent — Unresolved Decision Management

## Problem

Forge currently has no normative concept for "this Artifact or Gate cannot
yet be considered determined because a material question has no valid
answer." When an agent encounters ambiguity today, exactly two failure modes
are available, and both are already visible in this repository's own
history:

1. **Silent resolution.** The agent picks a plausible answer and it appears
   directly in Specification, Architecture, Plan, Tasks, or code, with no
   record that a choice was made, why, or that alternatives existed. This is
   Specification Drift's precondition (§13 of `protocol/specification.md`
   already names the failure — silently changing Requirement meaning to fit
   an Implementation — but nothing today stops the *first* silent choice from
   ever becoming a Requirement in the first place).
2. **Unstructured escalation.** The agent asks an open question ("what should
   happen when...?") without having investigated the repository, without
   alternatives, without trade-offs, and without a recommendation — pushing
   engineering work the agent could have done onto the human.

Neither failure mode is hypothetical. `review.convergence` (CHG-0011) had to
invent a narrow, purpose-built version of exactly this problem —
`convergence_decision` with a fixed option enum and a `reason` field — because
Non-Convergence is one specific case of "a question exists that Forge cannot
answer for itself and must not silently answer." CHG-0011's own Discovery
explicitly named this as future work: *"No general Decision Gate / Decision
Analysis framework... planned for a later Change."* This Change is that later
Change.

## Goal

Introduce **Unresolved Decision Management**: a disciplined way for Forge to
detect a material, unresolved question before it is silently propagated into
a downstream Artifact; investigate whether repository evidence already
answers it; produce alternatives and trade-offs when it does not; recommend
an answer when there is engineering basis to do so; distinguish that
Recommendation from an actual Decision; resolve autonomously only when
Decision Authority for that class of question permits it; and otherwise stop
and require an explicit human Decision — presented as a structured choice,
not an open-ended question.

Concretely, this Change must let Forge:

1. Detect and classify an Unresolved Decision.
2. Determine its materiality (most questions are not material and must not
   interrupt the workflow).
3. Determine who has authority to resolve it.
4. Investigate before escalating.
5. Produce alternatives and trade-offs when there is a real choice.
6. Recommend, with a Confidence level, when there is engineering basis.
7. Keep Recommendation and Decision distinct in the record.
8. Resolve autonomously when authority permits it.
9. Stop the workflow and request a human Decision when it does not.
10. Record the Decision and its rationale durably.
11. Prevent a Material Unresolved Decision from crossing a Gate.
12. Prevent a downstream Artifact from silently resolving an ambiguity owned
    by an upstream Artifact.
13. Trigger controlled backward invalidation when an owning Artifact's
    Decision changes, or is discovered, after downstream Artifacts already
    depended on the absence of that Decision.

## Non-goals

- This is not a general-purpose "ask the user" mechanism. A structured
  Decision record with investigation, alternatives, and a Recommendation is
  the default; a bare open question is the exception of last resort.
- This does not retrofit `review.convergence_decision` (CHG-0011) onto the
  new mechanism. `convergence_decision` is a valid, narrower, already-shipped
  instance of the same underlying pattern; unifying it is explicitly
  deferred (see `discovery.md`).
- This does not make Forge autonomous by removing human authority over
  product or contract questions. Confidence is not authorization.
- This does not introduce a new integer Protocol identifier. See
  `discovery.md` and `specification.md` §Compatibility for the evidence.
- This does not build a general assumption-tracking system beyond what is
  needed to stop a Material Assumption from substituting for a Decision
  record.
- This does not implement Implementation-stage behavior. This Change stops
  at the Forge-mandated boundary before Implementation (see the final
  message of this session).

## Flow

FULL. This Change adds a new Core Protocol concept (Unresolved Decision),
new Contract invariants, a new Specification section, a new canonical
Policy, additive Schema fields on `forge/change@1` and `forge/change@2`, and
a new `forge validate` mechanical boundary — the same class of cross-cutting
change as CHG-0008 and CHG-0011, both FULL. Per C-032, FULL requires
inspecting existing Architecture before introducing new abstractions; that
inspection is recorded in `discovery.md`.
