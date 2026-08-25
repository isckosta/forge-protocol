# Forge Capabilities

Status: Foundation (introduced by `CHG-0047`). No concrete Capability exists
yet — this document defines the abstraction so that the first real
Capability (`investigate`, in a later Change) has a place to live without
requiring the foundation to be redesigned.

## What a Forge Capability is

A Forge Capability is a specialized, reusable **agentic competency** —
a well-scoped thing an agent knows how to do (investigate an incident,
review a Change, verify provenance, challenge a claim) — defined once,
canonically, in a human-readable `CAPABILITY.md` file, independent of any
specific Harness (Claude, Codex, Cursor, or any future one).

A Capability answers *what a competency is and requires* — its Identity,
Purpose, Applicability, Inputs, Behavior, Outputs, and Evidence
Expectations (the full contract is defined in [`capability.md`](capability.md)).
It does not answer *when* it runs, *who* authorized it, or *how* a
particular Harness exposes it — those are the responsibilities of other
layers, described below.

## What a Forge Capability is not

- **Not a Harness Skill.** A Claude Skill (`SKILL.md`), a Codex
  representation, or a Cursor integration is a Harness-specific
  *adaptation* of a Capability, produced by a Harness Adapter. The
  Capability is the canonical source; the Skill is a derived
  representation. They are not interchangeable, and a Capability is never
  defined *as* a `SKILL.md`.
- **Not "Harness capability" (`src/forge_cli/adapters/capabilities.py`).**
  That existing, unrelated module answers a different question — "does
  this Harness declare support for feature X (e.g. subagents, hooks)?" —
  and reports a limitation when it doesn't. A Forge Capability is a
  competency a Capability defines and an agent performs; a Harness
  capability is an environment feature flag a Harness Adapter checks. The
  shared English word is coincidental; the concepts do not overlap.
- **Not a Flow stage, a Gate, or a lifecycle.** A Capability does not
  decide when it is needed, does not gate Completion, and does not carry
  approval semantics.
- **Not a registry, a plugin system, or an executor.** This foundation
  introduces no mechanism for discovering, composing, scoring, or running
  Capabilities. A Capability is loaded — deterministically, one
  definition at a time, given an explicit path — not resolved from a
  catalog.

## Responsibilities

A Forge Capability is responsible for describing, canonically and
Harness-independently:

- what competency it represents (Identity, Purpose);
- when it legitimately applies (Applicability);
- what it needs to operate (Inputs);
- what it actually does (Behavior);
- what it produces (Outputs);
- what evidence a run of it is expected to leave behind (Evidence
  Expectations).

It is not responsible for enforcing any of the above — enforcement, where
it exists, belongs to CLI, CI, hooks, or another deterministic mechanism,
per the architectural boundaries below.

## Architectural boundaries

A Capability MUST NOT possess or redefine:

- Protocol lifecycle;
- Flow selection or Flow stage sequencing;
- Change lifecycle (`intent` → ... → `completion`);
- mandatory Gates;
- approval semantics;
- human authority (a Capability cannot authorize its own execution, nor
  substitute for a required human Decision);
- Protocol compatibility;
- enforcement that properly belongs to CLI, CI, hooks, or another
  deterministic mechanism.

These boundaries exist so that adding a Capability is never mistaken for
extending the Protocol or the Engineering Contract. Registering a
Capability requires no change to either.

## Relation to Core, Flow, Harness Adapters, and evidence

```
Protocol / Engineering Contract   defines obligations and invariants
              |
        Forge Core / Flow         decides lifecycle and when a
              |                   competency is needed
        Forge Capability          provides the specialized competency
              |
        Harness Adapter           translates the Capability into a
              |                   concrete environment
   Claude Skill / Codex / Cursor  representation, distribution
```

Core and Flow remain the sole authority over *when* a competency is
exercised — a Capability never decides this for itself. A Harness Adapter
derives its environment-specific representation *from* a Capability; the
Capability remains canonical regardless of how many Harnesses adapt it,
or whether any Harness Adapter for it exists yet at all.

Repository-native evidence (Git-committed Change Artifacts, provenance
records) remains the durable memory for anything a Capability's execution
needs to survive past that execution. A Capability does not own storage,
does not persist state of its own, and does not become a second source of
truth alongside the repository.

## Adding a future Capability

A concrete Capability is introduced as a new directory under
`capabilities/`, containing a single canonical definition:

```
capabilities/
└── investigate/
    └── CAPABILITY.md
```

`CAPABILITY.md` is the canonical representation of that Capability in
Forge — it must conform to the minimal contract defined in
[`capability.md`](capability.md). A Harness Adapter may later produce an
adaptation of it (for example
`.claude/skills/forge-investigate/SKILL.md`), but that adaptation is
derived, not authoritative: if the two ever disagree, `CAPABILITY.md` is
correct and the Harness projection is stale.

Adding a Capability this way requires no change to the Protocol, the
Engineering Contract, `pyproject.toml`, or `src/forge_cli/capabilities/`
itself — the loader in that package already knows how to load any
definition conforming to the contract, given its path.
