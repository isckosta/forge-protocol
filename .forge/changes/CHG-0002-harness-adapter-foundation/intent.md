---
forge:
  artifact: intent
  schema: 1
change: CHG-0002
status: approved
---

# Intent — Harness Adapter Foundation

## Problem

Forge is intentionally Harness-agnostic, but the Protocol does not yet define a formal boundary between canonical Forge semantics and Harness-specific representation.

Without that boundary, each integration could invent its own interpretation of Flows, Policies, Roles, Gates, and Change state. That would make Forge behavior dependent on the chosen coding Harness and undermine Protocol interoperability.

## Desired outcome

Define a canonical Harness Adapter model that allows Forge semantics to be translated into Harness-specific files, commands, skills, rules, prompts, hooks, or configuration without allowing the Adapter to redefine Forge.

## Success criteria

The Foundation must define:

- a stable Adapter identity and manifest;
- Protocol compatibility declaration;
- supported capabilities;
- deterministic input from Effective Forge Configuration;
- deterministic generated representation where the Harness permits it;
- ownership boundaries for generated artifacts;
- conformance invariants;
- explicit unsupported-capability reporting;
- safe install/update behavior;
- a path toward a future Adapter Conformance Suite.

## Constraints

- No first-party Cursor, Codex, Claude, ChatGPT, Gemini, or Copilot Adapter is implemented in CHG-0002.
- Canonical Forge semantics remain independent from Adapter implementations.
- Adapters MUST NOT weaken the Effective Engineering Contract.
- Adapters MUST NOT become an alternate source of Change truth.
- The repository remains the durable source of Forge engineering state.
- The CLI may install/configure Adapter infrastructure but does not execute development lifecycle stages.

## Out of scope

- Adapter marketplace;
- remote Adapter registry;
- auto-discovery from the internet;
- execution of LLM inference;
- first-party Harness-specific workflows;
- Adapter sandboxing beyond capabilities provided by the underlying Harness;
- Protocol conformance certification for third parties.
