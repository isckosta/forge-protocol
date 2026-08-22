---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0025
status: complete
---

# Knowledge Capture — Plan Approval Semantics

The repository already had a `plan_complete` Gate and a human-authority
Decision rule for Decisions, but no equivalent recorded boundary for an
approved Plan. The adopted pattern is the repository-native convention used
by CHG-0014: ask for the explicit human confirmation at the Plan/Implementation
boundary, then preserve that confirmation in the Plan and provenance.

This is intentionally a recorded-evidence mechanism, not a claim that Core
can cryptographically prove who typed the confirmation. `forge validate`
checks the Decision shape and the required durable record structure. Adapter
guidance may remind the agent of the checkpoint, but it is not authority.

`specification_gate_passed` remains technical. Extending human-authority
semantics to another Gate requires a separate Change with evidence that the
Gate represents a human act.
