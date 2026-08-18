# Forge Core Protocol Specification

Protocol version: `1`

Status: Stable

## 1. Scope

This specification defines the Core concepts required to conduct Forge-governed software Changes.

## 2. Change

A Change is the fundamental Forge unit of engineering work. Every Forge-governed modification MUST belong to a Change.

A Change MUST have a stable identifier, title, kind, explicit Intent, assigned Flow, lifecycle state, TDD status, Verification status, Review status, and Documentation Impact status.

## 3. Change identifier

Canonical format: `CHG-NNNN`. Identifiers MUST remain stable after creation.
Planning documents MUST NOT reserve Change identifiers. Forge assigns the next
available stable identifier when the repository-native Change is created.

When a Change uses a dedicated Git branch, the branch SHOULD include the
lowercase Change identifier for repository traceability. The recommended form
is `<type>/chg-NNNN-<slug>`, for example
`feat/chg-0007-protocol-v1-contract-freeze`. Branch names are references, not
an alternate source of Change state.

## 4. Change kinds

Protocol version 1 recognizes `feature`, `bugfix`, `refactor`, `security`, `performance`, `migration`, `documentation`, `infrastructure`, and `chore`. Projects MAY introduce additional kinds. Additional kinds MUST NOT alter canonical Flow semantics.

## 5. Intent

Every Change MUST have explicit Intent before Implementation.

## 6. Classification

Every Change MUST be classified before Implementation. Classification MUST primarily consider semantic impact. Line count MUST NOT be the primary classifier.

## 7. Flows

Protocol version 1 defines FAST, STANDARD, and FULL. Projects MAY create stricter derived configurations. Projects MUST NOT weaken canonical minimum requirements.

## 8. FAST

Minimum lifecycle: Intent, Inspection, Test Design when behavioral, TDD Implementation when applicable, Verification, Strict Review, Documentation Impact, Completion. FAST MUST NOT bypass applicable TDD, Verification, or Review.

## 9. STANDARD

Minimum lifecycle: Intent, Discovery, Specification, Test Design when behavioral, Plan, TDD Implementation when applicable, Verification, Strict Review, Documentation, Completion.

## 10. FULL

Minimum lifecycle: Intent, Discovery, Specification, Adversarial Specification Review, Architecture, Test Strategy, Plan, Tasks, TDD Implementation when applicable, Verification, Strict Review, Documentation, Knowledge Capture, Completion.

## 11. Escalation

Supported escalation: FAST -> STANDARD, STANDARD -> FULL, FAST -> FULL. Escalation MUST preserve relevant Artifacts and record its reason. Automatic downgrade is forbidden.

## 12. Requirements

STANDARD and FULL Changes SHOULD identify material expected behavior through stable Requirements. FULL Changes MUST identify material Requirements when applicable. Prefixes: FR, NFR, SEC, INV, CON.

## 13. Specification Drift

Agents MUST NOT silently modify Requirement meaning to accommodate an Implementation. When implementation evidence invalidates the Specification, the Change MUST return to the appropriate specification stage and the Drift MUST be recorded.

## 14. TDD-first

Reasonably testable executable behavioral Changes MUST follow TDD. The canonical cycle is RED -> GREEN -> REFACTOR.

## 15. RED

A valid RED state requires expected behavior, an appropriate executable test existing before production Implementation, execution, failure, and failure because expected behavior is absent or incorrect. Syntax errors, invalid test setup, broken fixtures, environment failures, unrelated failures, and unrelated dependency failures MUST NOT count as valid RED evidence.

## 16. GREEN

After valid RED, Implementation SHOULD introduce the minimum production behavior required to satisfy the relevant test. The relevant test MUST pass before GREEN.

## 17. REFACTOR

Refactoring MAY occur after GREEN. Relevant tests MUST remain passing. New behavior requires a new TDD cycle.

## 18. Post-hoc tests

Tests written after production Implementation MAY contribute to Verification and regression protection. They MUST NOT be represented as TDD evidence.

## 19. TDD exceptions

TDD MAY be marked `not_applicable` or `exception` when it cannot reasonably provide value. The reason MUST be explicit. Verification and Strict Review remain mandatory.

## 20. Bugfixes

Reasonably automatable bugfixes MUST first establish a regression test reproducing the defect and reaching valid RED before the fix. Bugfixes SHOULD address root cause.

## 21. Verification

Every Change MUST undergo Verification. Passing tests alone MUST NOT automatically satisfy Verification.

## 22. Strict Review

Every Change MUST undergo adversarial Strict Review. Reviewer MUST attempt to identify plausible reasons the Implementation should not be accepted.

When a pull request or equivalent external review surface is part of the Change, Review MUST reconcile all unresolved threads that contain BLOCKER findings, MAJOR findings when project policy makes MAJOR blocking, or any other finding explicitly classified as blocking. `review_passed` MUST NOT be asserted while such a thread remains unresolved. If no external review surface exists, this condition is satisfied trivially.

## 23. TDD Review

Where TDD applies, Review SHOULD evaluate test-before-production ordering, RED validity, behavioral relevance, GREEN scope, refactoring safety, missing behavioral tests, and false TDD evidence.

## 24. Findings

Initial severities are BLOCKER, MAJOR, MINOR, and OBSERVATION. BLOCKER MUST prevent Completion. Projects MAY make MAJOR blocking. Material Findings MUST contain sufficient evidence.

## 25. Reviewer and Resolver

Reviewer and Resolver are separate conceptual Roles. Blocking Findings SHOULD be re-reviewed after Resolution.

## 26. Documentation Impact

Every Change MUST explicitly evaluate Documentation Impact.

## 27. Completion

A Change MUST NOT complete when required stages remain incomplete; a blocking Gate has failed; unresolved BLOCKER Findings exist; required Verification is incomplete; required TDD evidence is missing without an explicit exception; Documentation Impact has not been evaluated; Manifest state contradicts repository reality; or blocking review threads on an active external review surface remain unresolved.

## 28. Repository-native state

Essential Forge engineering state MUST NOT exist only in transient chat history.

## 29. Configuration resolution

Canonical Protocol definitions are authoritative. Project configuration references canonical concepts by stable identifiers and MAY strengthen or specialize behavior only where the Protocol permits it. The Effective Engineering Contract is the canonical Contract plus project Contract extensions. Project extensions MUST NOT weaken canonical invariants. Harness Adapters consume the effective Forge configuration; they MUST NOT redefine it.

## 30. Harness execution

Different coding Harnesses MAY execute Forge workflows. Harness differences MUST NOT redefine Core Protocol semantics.

## 31. CLI boundary

The official Forge CLI MAY install, initialize, configure, validate, migrate, diagnose, report versions, and manage Adapters. It MUST NOT be required for normal lifecycle execution.

## 32. Provider independence

Forge Protocol MUST remain independent from specific AI providers.

## 33. Local operation

Canonical Forge operation MUST NOT require a Forge-hosted backend.

## 34. Harness Adapter contract

A Harness Adapter is a projection layer from resolved Effective Forge Configuration to Harness-native representation. It MUST NOT redefine canonical Contract, Flow, Policy, Change, TDD, Verification, Review, or Documentation semantics.

Every Adapter manifest MUST declare stable identity, independent Adapter version, target Harness, a half-open integer Protocol interval (`min <= protocol < max_exclusive`), and declared capabilities. Protocol v1 capabilities are `persistent_instructions`, `commands`, `skills`, `hooks`, `agent_roles`, and `generated_files`.

Adapters MUST plan before mutation. Plans MUST be deterministic for identical inputs and declare artifact path, ownership, operation intent, resulting content or digest, limitations, and conflicts. Initial ownership modes are `forge_owned`, `user_owned`, and `shared`; initial operation intents are `create`, `update`, `preserve`, `conflict`, and `delete_generated`.

User-owned artifacts MUST NOT be silently overwritten. Forge-owned updates require proven expected generated state. Shared updates require an Adapter-defined deterministic merge strategy; otherwise they MUST conflict.

## 35. Adapter installation state and drift

A configured Adapter MUST retain repository-native installation metadata at `.forge/adapters/<adapter-id>/installation.yml` containing Adapter identity/version, target Harness, Protocol interval, generated Forge-owned artifacts with expected digests, and explicit limitations.

Installation metadata is derived representation state and MUST NOT duplicate canonical Change lifecycle state. Divergence between recorded and observed generated content MUST be reported as drift/conflict before replacement.

Adapter publication SHOULD avoid leaving state that appears successfully installed after partial failure. Repository-bound paths MUST reject traversal, ambiguous cross-platform paths, and symlink escapes.

## 36. Adapter conformance and CLI boundary

Harness representation MUST preserve required canonical stages, Gates, Contract invariants, TDD RED semantics, Strict Review semantics, and repository semantic authority. If the Harness cannot enforce an invariant, the limitation MUST be explicit; a limitation MUST NOT excuse removing the canonical requirement.

Adapter-related CLI behavior is infrastructure-only. It MAY install, configure, validate, update, plan, and diagnose Adapter infrastructure, but MUST NOT execute Specification, TDD Implementation, Verification, Review, Resolution, or Completion stages. Protocol v1 introduces no separate Adapter activation lifecycle state.

## 37. Adapter schemas and locality

Forge MUST provide deterministic machine-readable Schemas for Adapter manifests and installation records. Core Adapter validation and planning MUST NOT require network access or a Harness-specific SDK. Official distributions MUST package the canonical Protocol resources required to resolve these Schemas outside a source checkout.

## 38. Compatibility and evolution

Protocol, Schema, CLI, and Adapter versions are independent. Protocol 1
compatibility, breaking-change boundaries, deprecation, stable lifecycle
vocabulary, and schema catalog rules are defined in `compatibility.md`.

A Protocol 1 revision MUST NOT weaken canonical invariants, change the meaning
of existing required fields or Gates, or invalidate previously valid conforming
instances. Such changes require a new integer Protocol identifier.

## 39. Unresolved Decision Management

An Unresolved Decision is a material decision required for an Artifact or
Gate to be considered sufficiently determined, whose answer does not yet
have valid normative authority. Detection MUST NOT be followed by silent
resolution: an agent MUST NOT choose an answer to a material question and
represent it as settled fact in any Artifact.

Every Unresolved Decision MUST be classified into exactly one Decision
Class — `product`, `contract`, `architectural`, or `technical` — which
determines its owning Artifact and its default Decision Authority
(`human`, `agent`, or `agent_with_review`) per `protocol/policies/decision.yml`.
A question MUST first be assessed for Materiality; a question that would not
change a Requirement, Acceptance Criterion, public Contract, Schema,
Compatibility boundary, Security posture, domain Invariant, ownership
boundary, failure semantics, state transition, Architecture, Verification
Strategy, or operational behavior is Non-material and requires no Decision
record, no escalation, and no workflow interruption.

Before escalating a Material Unresolved Decision, Forge MUST attempt
Evidence Resolution: citing an already-existing source of normative
authority that determines the answer. When Decision Authority permits
autonomous resolution, Forge MUST perform Analysis and produce a
Recommendation before resolving the Decision itself. When Decision
Authority is `human`, Forge MUST perform Analysis, produce Alternatives and
Trade-offs, and produce a Recommendation, then stop and require an explicit
human Decision; a Recommendation, regardless of Confidence, MUST NOT be
treated as a Decision the agent is authorized to enact.

A Gate MUST NOT be asserted passed while a dependent Artifact has a Material
Unresolved Decision it owns in an Open-blocking Lifecycle state (`open`,
`analyzing`, `awaiting_decision`). A downstream Artifact MUST NOT resolve a
Decision owned by an upstream Artifact; when a downstream stage discovers
one, the owning Artifact MUST be revisited and any Gate it already passed
MUST be re-satisfied. A Decision's resolution that changes an
already-complete upstream Artifact MUST explicitly declare which downstream
Artifacts it invalidates.

Full normative detail — Decision Lifecycle states, record shape, the
Class taxonomy rationale, and Gate-integration mechanics — is defined by
`protocol/policies/decision.yml` and enforced, to the extent deterministically
checkable from repository-native Change state, by Core validation. This
section applies independently of declared Protocol version; a Change that
records no Decision makes no claim this section speaks to and is
unaffected by it.
