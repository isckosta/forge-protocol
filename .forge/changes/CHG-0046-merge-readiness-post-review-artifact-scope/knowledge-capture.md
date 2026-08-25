---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0046
status: pending
---

# CHG-0046 · Knowledge Capture

> **Durable Knowledge**
>
> Records knowledge produced by this Change that should remain useful for future development, maintenance, and decisions — not a summary of the Change itself.

## What Changed

State the durable change in a few sentences — context for the knowledge below, not a file-by-file account. That belongs to Plan, Tasks, or the diff.

## Durable Knowledge

Record only what will still be true and useful after this Change is forgotten. Ask: will this still be valid, and could another Change decide better by knowing it? Do not duplicate Decision, Architecture, Specification, Review, or Specification Drift — reference them, extract the reusable lesson they revealed. Use short prose for a single dominant lesson. Use `### K-xxx · <title>` items when there are several genuinely independent lessons — ids are optional structure, not required, since no consumer depends on them today. If no additional knowledge beyond this Change was identified, say so plainly — that is a valid, complete answer, not a gap to fill.

## Consequences for Future Changes

State concrete implications for future work, only when they exist. Give each conclusion a scope (Forge Core, Harness Adapter, CLI, review workflow, …) rather than implying it applies to the whole system.

## References

Reference Specification, Architecture, Decision, Review, or Specification Drift by id — do not duplicate their content. When this work is materially architectural or Protocol-level, reference the `docs/adr/`/`docs/rfcs/` entry already produced for it, rather than restating it here. This is distinct from the Forge Experience Report (`docs/experience-reporting.md`): FER is opt-in and records what happened during a real execution; this document records what should remain known afterward.
