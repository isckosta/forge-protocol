---
forge:
  artifact: intent
  schema: 1
change: CHG-0052
status: active
---

# CHG-0052 · Investigate Capability

> **Change Intent**
>
> Define `investigate`, the first concrete Forge Capability, as a
> canonical, evidence-driven diagnostic competency under the Capability
> Architecture foundation (`CHG-0047`), proving that foundation can carry
> a real competency without becoming a framework.

## Overview
| | |
|---|---|
| **Change** | CHG-0052 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

`CHG-0047` established the Capability Architecture — the `capabilities/`
contract and the `forge_cli.capabilities` loader — but deliberately left
it empty: no concrete Capability exists yet, so the foundation has never
been exercised against a real definition. Separately, when an agent
(human-directed or autonomous) is asked to diagnose a bug, a regression,
a failing test, or unexpected behavior, the path of least resistance is
`symptom -> plausible guess -> code change`: the agent fixates on the
first plausible explanation and edits code to match it, without first
establishing what is actually true. That produces fixes aimed at the
wrong cause, silently discarded evidence, and conclusions presented with
more confidence than the evidence supports. Nothing in this repository
currently defines, canonically and Harness-independently, what a
disciplined, hypothesis-driven investigation competency requires.

## Goal

1. Introduce `capabilities/investigate/CAPABILITY.md` as the canonical
   definition of a diagnostic investigation competency, satisfying the
   contract in `capabilities/capability.md` exactly as written.
2. The definition must replace `symptom -> plausible guess -> code
   change` with `problem -> establish facts -> reproduce when possible
   -> gather evidence -> competing hypotheses -> test hypotheses ->
   isolate root cause -> conclusion`, and must allow root cause to remain
   explicitly unestablished when the evidence does not support a
   conclusion.
3. Prove, via the existing generic `forge_cli.capabilities` loader and
   its existing test suite shape, that the loader can load this
   definition without any `investigate`-specific handling anywhere in
   the loader, model, or foundation documents.

## Scope

- One new Capability definition (`investigate`) under `capabilities/`.
- Tests that prove the definition satisfies the existing Capability
  contract and loads through the existing, unmodified loader.

## Out of Scope

- Any change to `capabilities/README.md` or `capabilities/capability.md`
  (the foundation itself).
- `CapabilityRegistry`, `CapabilityExecutor`, discovery, a dependency
  graph, a composition runtime, Capability-owned state, a new lifecycle,
  a new Gate, or a new Protocol version.
- A `SKILL.md` or any other Harness-specific representation of
  `investigate` (Claude, Codex, Cursor, or otherwise), and any adapter
  wiring for one.
- Any change to Flow, Gate, Protocol, or Engineering Contract semantics.
- Any behavior that fixes, mitigates, or otherwise implements a
  correction for whatever a future investigation finds — `investigate`
  is diagnostic only.

## Success Criteria

- `capabilities/investigate/CAPABILITY.md` exists, carries the required
  frontmatter and all seven required `##` sections non-empty, and reads
  as a genuine diagnostic competency definition rather than placeholder
  prose.
- The existing `forge_cli.capabilities.loader.load_capability` function
  loads it successfully with no code change to the loader, the model, or
  `capabilities/capability.md`.
- The definition is evidence-driven and hypothesis-driven: it requires
  separating facts from hypotheses, forming competing hypotheses before
  settling on one, testing hypotheses against evidence, and permits an
  explicit "root cause not established" outcome.
- The definition stays diagnostic: it does not authorize `investigate`
  to fix the problem it investigates, approve a Change, select or
  redefine a Flow, create a Gate, control lifecycle, or claim any human
  authority.
