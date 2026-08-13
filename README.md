# Forge

> Build with agents. Engineer with discipline.

Forge is an open-source engineering protocol for AI-assisted software development.

AI can generate code quickly. That is no longer the difficult part. The difficult part is establishing what should be built, proving expected behavior before implementation, verifying the resulting system, and reviewing the Change rigorously enough to discover why it might still be wrong.

Forge governs that process.

It combines Spec-Driven Development, Test-Driven Development, explicit engineering policies, proportional development Flows, Verification, adversarial Strict Review, and repository-native engineering knowledge.

**Your chat is the runtime. Your repository is the durable memory. Forge is the protocol.**

## Status

Forge is in its Foundation phase. The project is intentionally Protocol-first. The official CLI has not been implemented yet.

## Core engineering loop

For behavioral Changes:

`Specification -> Test Design -> RED -> GREEN -> REFACTOR -> Verification -> Strict Review`

Specification defines what should exist. TDD drives how behavior is implemented. Verification determines whether sufficient evidence supports the resulting system. Strict Review attempts to falsify the Implementation.

## Core properties

- **Repository-native:** durable engineering state belongs to the repository.
- **Chat-executed:** development workflows happen inside supported coding-agent conversations.
- **Harness-agnostic:** canonical semantics do not depend on Cursor, Claude Code, Codex, Gemini CLI, Copilot, or another Harness.
- **TDD-first:** reasonably testable behavioral Changes establish valid RED before production behavior.
- **Protocol-first:** the Protocol defines semantics; implementations consume them.
- **Local-first:** canonical operation requires no Forge-hosted backend.

## Change as the fundamental unit

Forge organizes engineering around a `Change`, not only around features. A Change may represent a feature, bugfix, refactor, security correction, performance improvement, migration, documentation, infrastructure, or maintenance.

Every Change has Intent, classification, a Flow, Verification, Review, and Documentation Impact. Behavioral Changes are TDD-first unless an explicit justified exception applies.

## Flows

Forge defines three canonical Flows:

- **FAST** — low-semantic-impact work with minimal ceremony, never reduced quality.
- **STANDARD** — ordinary behavioral Changes and small-to-medium features.
- **FULL** — architecture, security, authorization, integrations, persistence, public contracts, major domain behavior, and other high-impact work.

Flows may escalate `FAST -> STANDARD -> FULL`. Automatic downgrade is forbidden.

## CLI boundary

The Forge CLI exists for infrastructure concerns such as installation, initialization, configuration, validation, migration, diagnostics, version reporting, and Adapter management.

The CLI is **not** the development workflow runtime. Specification, implementation, Verification, Review, and Resolution happen in the chat runtime under the Protocol.

## Repository layout

- `protocol/` — canonical Forge Protocol.
- `.forge/` — Forge's own dogfooding workspace.
- `docs/adr/` — Architecture Decision Records.
- `docs/rfcs/` — Protocol evolution proposals.
- `examples/` — reference Forge Changes.

## Dogfooding

Forge develops Forge using Forge. The `.forge/` directory is active engineering state, not an example.

The first Forge Change is `CHG-0001 — Bootstrap Forge CLI`.

## License

Apache License 2.0.
