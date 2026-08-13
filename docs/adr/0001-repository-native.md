# ADR-0001 — Forge is Repository-Native

Status: Accepted

## Context

Forge requires durable engineering state including Specifications, Requirements, TDD evidence, Review Findings, Policies, and Change state. Chat sessions are transient.

## Decision

Durable Forge state lives primarily in repository-versioned files. Initial formats are Markdown, YAML, and JSON Schema.

## Consequences

Forge state travels with branches and code. Ordinary Git tooling can review Forge Artifacts. No Forge-hosted service is required. Concurrent Changes may create Git conflicts. Future indexes must remain derivable from repository state.
