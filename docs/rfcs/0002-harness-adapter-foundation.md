# RFC-0002 — Harness Adapter Foundation

Status: Accepted

## Summary

This RFC defines the canonical boundary between Forge semantics and Harness-specific representation.

A Harness Adapter is a projection layer. It consumes Effective Forge Configuration and produces a deterministic, reviewable plan for Harness-native representation. It does not become a new semantic authority.

## Motivation

Forge is Harness-agnostic, but Harnesses expose different primitives such as instruction files, commands, skills, hooks, agents, and generated configuration. Without a canonical Adapter contract, each integration could reinterpret Forge Flows and invariants differently.

## Decision

Forge will define a Harness Adapter model with:

- stable Adapter identity and independent versioning;
- explicit target Harness;
- explicit integer Protocol compatibility interval;
- canonical capability vocabulary;
- deterministic planning before mutation;
- artifact ownership modes;
- repository-native installation records;
- digest-based generated drift detection;
- explicit unsupported-capability limitations;
- conformance checks preserving canonical Contract, Flow, TDD, and Strict Review semantics.

## Protocol compatibility

Adapter manifests use a half-open integer interval:

```yaml
protocol:
  min: 1
  max_exclusive: 2
```

Compatibility is `min <= project_protocol < max_exclusive`.

This deliberately avoids importing a package-manager version-range grammar into Protocol v1.

## Capability vocabulary

Initial capabilities are:

- `persistent_instructions`;
- `commands`;
- `skills`;
- `hooks`;
- `agent_roles`;
- `generated_files`.

Capabilities describe Harness representation primitives. They do not define Forge semantics.

## Planning model

Adapters produce an `AdapterPlan` before mutation. Planned operations are deterministic and reviewable.

Ownership modes:

- `forge_owned`;
- `user_owned`;
- `shared`.

Operation intents:

- `create`;
- `update`;
- `preserve`;
- `conflict`;
- `delete_generated`.

## Repository authority

Generated Harness artifacts and Adapter installation records are derived representation. Canonical repository-native Forge state remains authoritative.

## Conformance

Adapters must preserve effective Flow and Contract semantics. In particular, they cannot represent TDD-applicable work as authorizing production behavior before valid RED, and they cannot bypass required Strict Review.

If a Harness cannot enforce an invariant, the Adapter must expose that limitation and must not claim enforcement.

## CLI boundary

The Forge CLI may validate, plan, install, update, and diagnose Adapter infrastructure. It remains prohibited from executing the software-development lifecycle itself.

## Alternatives rejected

### First Harness first
Rejected because it would allow one Harness's primitives to shape Core semantics prematurely.

### Free-form Protocol version ranges
Rejected because independent implementations could interpret them differently.

### Path-only generated ownership
Rejected because a user modification to a generated path would be silently destroyed. Ownership evidence requires expected generated content state.

### Harness files as source of truth
Rejected because this would violate repository-native and Harness-agnostic architecture.

## Consequences

Positive:
- Harness integrations share one semantic contract;
- drift and ownership are explicit;
- unsupported capabilities become visible;
- first-party and third-party Adapters can target the same foundation.

Negative:
- Adapter implementation requires planning and installation metadata;
- shared files require explicit merge strategies;
- some Harnesses may be unable to claim full Forge conformance.

## Future work

A separate Change will implement the first real Harness Adapter and validate this abstraction against an actual Harness.
