---
forge:
  artifact: inspection
  schema: 1
change: CHG-0028
status: complete
---
# Inspection — Chat Cadence Guidance

## Current state

`src/forge_cli/adapters/claude_code/resources/skills/workflow.md` and
`src/forge_cli/adapters/codex/resources/skills/workflow.md` are currently
byte-identical: both have SHA-256
`f69f4985c8bf021e700fd63311c01a6720f7389cd2453c5e8634f0bf9292297d` and
23 lines. Both contain the same classification, gate-preservation, Plan
approval, first-commit baseline, skill-discovery limitation, and explicit
“not technical enforcement” disclaimer. Neither contains chat-cadence
guidance.

## Flow classification

This Change is **FAST**. `protocol/flows/fast.yml` explicitly includes
copy corrections and low-risk maintenance, while its disqualifiers are
architectural, security, authorization, new-invariant, integration,
significant-cross-module, and major-public-contract changes. This addition
is symmetric prose in two Adapter source templates, changes no Adapter
mechanism or canonical semantic rule, and introduces no executable behavior.
The fact that the templates project to consumer skill files increases the
need for parity verification but does not create a semantic disqualifier.

## Parallel-work check

No local branch or working-tree diff for item #9 was visible when this
Change started. The templates already contain the merged #5/#6 guidance;
the new cadence paragraph will be additive and positioned alongside that
guidance without altering it.

## Process decision

The FAST stages are Intent, Inspection, Verification, Strict Review,
Documentation Impact, and Completion. TDD is not applicable because this
Change is prose-only and changes no executable behavior; the manifest will
record the reason explicitly.
