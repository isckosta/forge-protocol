# ADR-0003 — Filesystem is the Initial Source of Truth

Status: Accepted

## Context

Forge requires persistence for configuration and engineering Artifacts.

## Decision

The initial canonical persistence mechanism is the filesystem. Tracked state uses Markdown, YAML, and JSON Schema.

## Consequences

Artifacts remain readable, diffable, and Git-native. Schema migration becomes an explicit responsibility. Future indexes may improve performance but remain derived state.
