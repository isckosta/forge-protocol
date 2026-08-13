# Discovery — Codex Harness Adapter

## Confirmed from current official OpenAI documentation

- Codex supports reusable workflows as skills.
- Codex is documented for engineering workflows including understanding large codebases and reviewing GitHub pull requests.
- OpenAI documents Codex as usable for durable workflow-oriented engineering tasks.

Official sources consulted on 2026-08-13:
- https://developers.openai.com/codex/use-cases
- https://developers.openai.com/

## Not yet proven

The Change must not assume support for hooks, agent-role primitives, a specific repository instruction filename, or a stable command registration mechanism until each is confirmed by an authoritative current Codex document.

## Adapter implications

The first specification should model only capabilities proven during Discovery. Unsupported or unverified Forge requirements must become explicit Adapter limitations rather than false enforcement claims.

Codex-specific projections must remain outside the generic Adapter Core. The generic planner, ownership model, installation record, drift detection, conformance validator, and safe publisher remain the implementation boundary established by CHG-0002.

## Flow classification

FULL. This is the first concrete Harness integration and may reveal abstraction leaks that affect future adapters. Any required change to the generic Adapter contract must be handled explicitly through Architecture/ADR rather than hidden inside Codex-specific code.
