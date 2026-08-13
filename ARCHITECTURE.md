# Forge Architecture

## Status

Foundation Architecture. Material changes require an RFC and, when applicable, an ADR.

## 1. Purpose

Forge is an open-source, repository-native, chat-executed engineering Protocol for AI-assisted software development.

Forge governs a Change from Intent through Specification, TDD, Implementation, Verification, adversarial Review, Documentation, and durable engineering knowledge.

## 2. Architectural thesis

Forge is primarily a Protocol, not an executable application.

The Protocol must remain useful independently of the official CLI, CLI implementation language, coding agent, LLM, editor, Git provider, or Forge-hosted backend.

## 3. Core principles

Forge is repository-native, chat-executed, Harness-agnostic, Policy-governed, Protocol-first, TDD-first, local-first, human-readable, and machine-validatable where practical.

## 4. Major components

### Forge Protocol
Canonical engineering semantics.

### Forge CLI
Installation, initialization, configuration, validation, migration, diagnostics, version reporting, and Adapter management.

### Harness Adapters
Translation between canonical Forge concepts and Harness-specific primitives.

## 5. Canonical Protocol

The canonical Protocol lives in `protocol/` and contains the Engineering Contract, Flow definitions, Policies, Schemas, Artifact semantics, Gate semantics, and Role semantics.

## 6. Project workspace

A Forge-enabled project contains `.forge/`.

- `protocol/` defines Forge.
- `.forge/` configures Forge for a repository.

## 7. Configuration resolution

```text
Canonical Protocol
       ↓
Protocol Defaults
       ↓
Project Configuration
       ↓
Project Policies
       ↓
Project Contract Extensions
       ↓
Effective Forge Configuration
       ↓
Harness Adapter Representation
```

Later layers may specialize behavior only where the Protocol permits it. They may not weaken canonical Contract invariants.

Project Flow files reference canonical Flows by stable identifiers. They do not contain authoritative private copies of canonical Flow definitions.

The Effective Engineering Contract is the canonical Engineering Contract plus project Contract extensions. Project rules may strengthen canonical rules; they may not weaken them.

## 8. Change model

The fundamental unit of work is `Change`. Every Change has an identifier, title, kind, Intent, Flow, lifecycle state, Artifacts, Requirements when applicable, TDD state when applicable, Verification state, Review state, and Documentation Impact.

## 9. Flow classification

Flow selection is based on semantic impact, not line count. Relevant signals include domain rules, Architecture, persistence, security, authorization, public contracts, integrations, cross-module behavior, migrations, compatibility, and operational risk.

## 10. Canonical Flows

FAST: Intent -> Inspection -> Test Design -> TDD Implementation -> Verification -> Strict Review -> Documentation Impact -> Completion.

STANDARD: Intent -> Discovery -> Specification -> Test Design -> Plan -> TDD Implementation -> Verification -> Strict Review -> Documentation -> Completion.

FULL: Intent -> Discovery -> Specification -> Adversarial Specification Review -> Architecture -> Test Strategy -> Plan -> Tasks -> TDD Implementation -> Verification -> Strict Review -> Documentation -> Knowledge Capture -> Completion.

## 11. TDD execution model

A valid TDD cycle contains RED, GREEN, and REFACTOR.

RED requires expected behavior, an appropriate executable test created before production behavior, execution, and failure for the expected behavioral reason.

GREEN introduces the minimum relevant production behavior required to satisfy the failing test.

REFACTOR may improve design while relevant tests remain GREEN. New behavior requires a new cycle.

## 12. TDD applicability

TDD is required for reasonably testable executable behavioral Changes. Explicit exceptions do not disable Verification or Strict Review.

## 13. Bugfix model

Reasonably reproducible bugfixes follow Observed Behavior -> Regression Test -> RED -> Root Cause -> Fix -> GREEN -> REFACTOR -> Verification.

## 14. Verification versus TDD

TDD drives Implementation. Verification evaluates the resulting Change as a whole and may include automated tests, integration tests, contract tests, static analysis, type checking, linting, build validation, manual reproduction, security analysis, performance analysis, and compatibility analysis.

## 15. Strict Review

Every Change requires adversarial Strict Review. Review evaluates Requirements, TDD compliance, correctness, tests, edge cases, Architecture, domain Invariants, authorization, security, persistence, concurrency, transactions, performance, maintainability, compatibility, and Documentation when applicable.

## 16. Findings and Roles

Initial severities are BLOCKER, MAJOR, MINOR, and OBSERVATION. BLOCKER always blocks Completion. Reviewer and Resolver are separate conceptual Roles and blocking Findings require re-review after Resolution.

## 17. Gates

Initial conceptual Gates include Classification, Specification, Architecture, RED, Verification, Review, Documentation, and Completion. A Gate may be PASSED, FAILED, WARNING, or SKIPPED; SKIPPED requires an explicit reason.

## 18. Documentation and Knowledge

Every Change evaluates Documentation Impact. FULL Changes capture material durable knowledge when system reality changes.

## 19. Persistence

The initial source of truth is the filesystem using Markdown, YAML, and JSON Schema. Future indexes or databases may exist only as derived state unless a future RFC changes this decision.

## 20. CLI boundary

The official CLI may perform installation, initialization, configuration, validation, migration, upgrades, Adapter installation, diagnostics, and version reporting. It must not become the canonical interface for Specification, Test Design, Implementation, Verification, Review, Resolution, or Completion.

## 21. AI and Harness boundary

Forge Core contains no dependency on an AI provider SDK. AI execution belongs to the coding Harness. Adapters translate Forge semantics but may not redefine them.

## 22. Protocol versioning

CLI, Protocol, Schemas, and Adapters may be versioned independently.

## 23. Security boundary

Forge defines engineering expectations. Actual process isolation and filesystem, network, and shell enforcement depend on the underlying Harness.

## 24. Non-goals

Forge is not intended to become an IDE, issue tracker, Git hosting platform, CI platform, LLM gateway, general AI assistant, or mandatory cloud service.

## 25. Core responsibility

Forge's core architectural responsibility is **Engineering Change Governance**.

## 26. Dogfooding

Forge develops Forge using Forge. If Forge cannot govern its own development without unreasonable ceremony, the Protocol should be reconsidered.
