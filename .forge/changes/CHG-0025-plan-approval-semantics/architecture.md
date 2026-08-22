---
forge:
  artifact: architecture
  schema: 1
change: CHG-0025
status: complete
---

# Architecture — Plan Approval Semantics

## Solution Summary

Extend the existing Protocol-2 unresolved-Decision validation path with a
small Plan-specific authority check. The check reads the already canonical
manifest fields (`state`, `artifacts.plan`, and `decisions[]`) and emits a
normal validation finding. No new state store, CLI command, Schema property,
or Adapter-specific authority channel is introduced.

## Boundary and compatibility

The check is active only for Change identifiers allocated from CHG-0025
onward, when the Change is not already `complete` and its manifest asserts
`artifacts.plan: approved`. This is the repository-native prospective
boundary: historical Changes are not rewritten, while a new active Change
cannot cross the boundary without the new evidence.

The matching Decision is identified structurally, not by a magic ID:
`class: technical`, `materiality: material`, `owning_artifact: plan`,
`authority: human`, `status: resolved`, and
`resolved_via: human_decision`. The Plan and provenance record the explicit
confirmation using the same repository-native convention established by
CHG-0014. A Decision with
the same ownership but an open status is reported as missing valid
authorization; the existing C-051 Gate dependency also blocks it. A
human-authority Decision resolved via `autonomous_decision` is reported by
existing C-055 validation.

## Data flow

1. Change author declares the Plan artifact approved.
2. The user explicitly confirms the Plan/Implementation transition.
3. Change author records the human act in the Plan's approval boundary and
   provenance, and records the matching `decisions[]` entry.
4. `forge validate` validates the Decision shape and C-055 semantics.
5. The Plan authority check requires one structurally matching resolved
   human Decision for active Changes.
6. The existing Gate dependency treats an approved Plan as a dependency of
   `before_implementation`, preventing a material open Plan Decision from
   being asserted as passed.

## Failure behavior

Missing, malformed, conflicting, or autonomous authorization is invalid. The
validator must not infer approval from
Recommendation Confidence, provenance of the agent execution, Adapter
projection, or chat text. More than one valid matching approval is invalid
unless one is explicitly superseded and the active Decision remains unique.
Completed Changes are compatibility exceptions only because their lifecycle
has already ended; they are not evidence that the new rule is optional for
active Changes.

## Decision record

The new requirement reuses `decisions[]` and existing Protocol-1/2 Schema
enums; no Schema shape change is necessary. Existing optional evidence fields
remain available for other provenance uses, but are not used as C-077 proof.
The Contract and versioned
Contract receive identical C-077 wording, as RFC-0003 established for the
active Protocol representation.
