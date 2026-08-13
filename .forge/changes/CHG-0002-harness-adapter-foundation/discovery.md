---
forge:
  artifact: discovery
  schema: 1
change: CHG-0002
status: approved
---

# Discovery — Harness Adapter Foundation

## Current state

Forge already defines:

- canonical Protocol resources;
- Effective Configuration composition;
- repository-native Change state;
- CLI infrastructure boundaries;
- TDD-first development;
- Strict Review;
- a future Adapter layer in Architecture.

No Adapter manifest, capability model, ownership model, installation contract, or conformance contract exists yet.

## Architectural risk

The main risk is semantic drift. If a Harness-specific integration becomes authoritative, two Forge-enabled repositories could behave differently even with identical Protocol and project configuration.

The Adapter therefore needs to be a projection layer, not a semantic layer.

## Required boundary

Conceptually:

```text
Canonical Protocol
      +
Project Configuration
      +
Project Policies / Contract
      ↓
Effective Forge Configuration
      ↓
Harness Adapter
      ↓
Harness Representation
```

The Adapter consumes resolved Forge semantics and emits or configures Harness-native representation.

## Capability differences

Harnesses differ materially. One may support persistent instruction files, another skills, commands, hooks, subagents, or no equivalent primitive at all.

The Foundation therefore needs an explicit capability declaration rather than pretending every Harness supports the same primitives.

## Ownership risk

Generated Harness files may collide with existing user-managed files. Adapter installation must distinguish:

- Forge-owned generated artifacts;
- user-owned artifacts;
- shared/mergeable artifacts.

Silent overwrite is unacceptable.

## State risk

Harness-native files are derived representation. They must not become the only copy of Contract, Flow, Policy, Change, Review, or TDD state.

## Compatibility risk

Adapter version and Protocol version are independent. An Adapter must explicitly declare which Protocol range it supports.

## Security boundary

An Adapter may configure hooks or commands only within capabilities supported by the Harness. Forge cannot claim enforcement or sandbox guarantees beyond the Harness.

## Conclusion

CHG-0002 should define a small, deterministic Adapter contract and schema before any Harness-specific Adapter is implemented. The first real Adapter should be a separate Change that validates the abstraction rather than shaping it prematurely.
