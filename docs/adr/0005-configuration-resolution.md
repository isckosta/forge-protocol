# ADR-0005 — Canonical Protocol and Project Configuration are Resolved Explicitly

Status: Accepted

## Context

Forge needs project-specific configuration without copying canonical Protocol definitions into every repository or allowing projects to weaken canonical invariants.

Implicit file inheritance would create ambiguous precedence and allow Harnesses to interpret the same project differently.

## Decision

Forge resolves effective configuration conceptually as:

Canonical Protocol -> Protocol Defaults -> Project Configuration -> Project Policies -> Project Contract Extensions -> Effective Forge Configuration -> Harness Adapter Representation.

Project Flow configuration references canonical Flows by stable identifier rather than duplicating their authoritative definitions.

The Effective Engineering Contract is the canonical Contract plus project Contract extensions. Project extensions may strengthen but may not weaken canonical invariants.

Harness Adapters translate effective configuration and do not participate in semantic resolution.

## Consequences

Canonical semantics remain centralized, project customization remains explicit, and Adapters have a stable semantic input. The CLI must eventually validate configuration resolution and reject attempts to weaken non-overridable invariants.
