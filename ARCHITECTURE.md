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

When an external review surface is active, Review reconciles its blocking threads with repository-native findings before `review_passed` may be asserted. External thread state is process evidence rather than a second source of canonical Change state; when no such surface exists, this condition is satisfied trivially.

## 16. Findings and Roles

Initial severities are BLOCKER, MAJOR, MINOR, and OBSERVATION. BLOCKER always blocks Completion. Project policy may classify other findings as blocking. Reviewer and Resolver are separate conceptual Roles, blocking Findings require re-review after Resolution, and unresolved blocking threads on an active external review surface prevent Completion.

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

## 22. Harness Adapter architecture

Harness Adapters are deterministic projection components, not workflow engines. They consume resolved Effective Forge Configuration, an Adapter manifest, Harness capability state, Adapter projections, and observed repository state. The Core planner returns an immutable `AdapterPlan`; only the publisher owns repository mutation.

The Adapter package is split by responsibility:

- `manifest.py` — manifest loading, Schema validation, and Protocol compatibility;
- `capabilities.py` — Forge representation requirements and explicit limitations;
- `plan.py` — immutable plan and operation models;
- `ownership.py` — collision, ownership, and drift classification;
- `state.py` — repository-native installation metadata;
- `validation.py` — Harness-agnostic conformance checks;
- `planner.py` — deterministic composition without filesystem or Harness SDK access;
- `publisher.py` — safe repository-bound application with preflight, stale-state checks, and rollback.

Generated Harness artifacts are derived state. Canonical Contract, Flow, Policy, Change, TDD, Verification, and Review state remain repository-native Forge authority.

## 23. Adapter publication boundary

Plans distinguish `forge_owned`, `user_owned`, and `shared` artifacts. User-owned state is preserved. Forge-owned updates require recorded expected state. Shared updates require deterministic merge provenance.

Publication validates every destination before mutation, rejects traversal and symlink escapes, revalidates update digests immediately before write, and writes `.forge/adapters/<id>/installation.yml` last as the successful-installation marker. Failed publication must not leave an installation record that implies success.

## 24. Adapter compatibility and conformance

Adapters use explicit independent versions and a half-open integer Protocol compatibility interval. Unsupported representation capabilities become explicit limitations rather than silent semantic loss.

Conformance validates preservation of canonical stages, Gates, invariants, TDD RED, Strict Review, and repository semantic authority. A Harness limitation may explain lack of technical enforcement; it cannot remove the canonical requirement.

## 25. Codex Harness Adapter

The first concrete Harness Adapter lives under `src/forge_cli/adapters/codex/`. Its packaged descriptor and capability-evidence resources are immutable release inputs and runtime authority; runtime planning does not fetch live vendor documentation.

The Adapter generates deterministic logical workflow and Contract resources from canonical Forge input. Packaged workflow material supplies stable framing, while stage order and Gate statements remain derived from the effective canonical Flow. These instructions represent Forge requirements and do not claim technical enforcement.

Projection and publication are separate. A projection bundle may exist without a filesystem destination. Publication requires an explicit or evidence-backed target and then delegates planning, ownership, collision handling, installation state, drift control, path safety, and mutation to the generic Adapter Core.

Codex-specific invariant assessment distinguishes `enforced`, `represented`, and `unsupported` without redefining generic capability booleans. Unsupported enforcement remains visible through generic limitations. The integration adds no Codex/OpenAI SDK dependency to the Core and supports deterministic offline loading, projection, and planning from the installed distribution.

## 26. Protocol versioning

CLI, Protocol, Schemas, and Adapters may be versioned independently.

Protocol `1` is the stable integer compatibility contract. Schema suffixes such
as `forge/change@1` version individual artifact shapes; they are not CLI or
Protocol release numbers. Adapters declare independent versions and half-open
integer compatibility intervals. The canonical compatible-versus-breaking and
deprecation rules live in `protocol/compatibility.md`.

`protocol/schemas/catalog.yml` is the portable registry of supported artifact
schemas. Contract tests validate the catalog, each Draft 2020-12 schema,
canonical Flow/Policy resources, and repository-native instances without a
network dependency.

## 27. Security boundary

Forge defines engineering expectations. Actual process isolation and filesystem, network, and shell enforcement depend on the underlying Harness. Adapter publication still owns repository path confinement and must reject unsafe repository escapes.

## 28. Non-goals

Forge is not intended to become an IDE, issue tracker, Git hosting platform, CI platform, LLM gateway, general AI assistant, or mandatory cloud service. Harness Adapters are not a second lifecycle runtime and do not introduce Adapter activation state in Protocol v1.

## 29. Core responsibility

Forge's core architectural responsibility is **Engineering Change Governance**.

## 30. Dogfooding

Forge develops Forge using Forge. If Forge cannot govern its own development without unreasonable ceremony, the Protocol should be reconsidered.
