# ADR-0002 — Forge Workflows are Chat-Executed

Status: Accepted

## Context

Developers increasingly perform software work through conversational coding Harnesses. Creating a separate Forge execution environment would duplicate capabilities already provided by those Harnesses.

## Decision

Forge development workflows execute inside supported coding-agent chats. The Forge CLI is restricted to infrastructure concerns.

## Consequences

Forge does not require model inference infrastructure. Harness Adapters become important. The repository remains durable state.
