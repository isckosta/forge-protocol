---
forge:
  artifact: intent
  schema: 1
change: CHG-0028
status: complete
---
# Intent — Chat Cadence Guidance

## Problem

The two Adapter workflow templates currently explain Forge lifecycle
requirements but give no non-binding guidance about what progress belongs in
the human chat. Agents can narrate every command or tool call, producing a
noisy conversation even when the human asked for one concise outcome.

## Desired outcome

Add identical, explicitly non-binding guidance to both Adapter templates:
prefer concise narration at meaningful stage transitions—such as Discovery,
Implementation, Verification, and Review completion—over a status message
for every command or tool call. The repository-native artifacts remain the
authoritative detailed record.

## Scope

In scope: the two `resources/skills/workflow.md` source templates and this
Change's documentation evidence. Out of scope: CLI behavior, Flow/Gate
semantics, validation, adapter projection mechanics, artifact publication,
Reviewer-independence wording, and roadmap items #2–#7, #9, and #10.

## Success criteria

- Both templates receive byte-identical, non-binding cadence guidance.
- The text preserves the existing technical-enforcement disclaimer.
- No executable behavior or enforced Protocol rule changes.
