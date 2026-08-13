# RFC-0001 — Forge Core Protocol

Status: Accepted for Protocol 1

## Summary

This RFC establishes the initial Forge Core Protocol.

Forge is a repository-native, chat-executed, harness-agnostic engineering Protocol combining Spec-Driven Development, TDD-first implementation, proportional engineering Flows, explicit Verification, adversarial Strict Review, and durable engineering knowledge.

## Motivation

AI agents have dramatically reduced the cost of generating code. They have not reduced the importance of determining what should be built, whether expected behavior is understood correctly, whether implementation satisfies it, whether tests prove what they claim, whether architecture remains coherent, and whether the resulting Change should be accepted.

Forge addresses this through explicit Engineering Change Governance.

## Decision

Forge uses `Change` as its fundamental unit. Changes are classified into FAST, STANDARD, or FULL.

All Changes require Intent, appropriate engineering context, TDD when applicable, Verification, Strict Review, and Documentation Impact evaluation.

## TDD

Executable behavioral Changes are TDD-first. Canonical cycle: RED -> GREEN -> REFACTOR.

RED must be observed before the relevant production behavior. Tests written after Implementation do not count as TDD evidence.

## FAST

FAST minimizes ceremony for low-semantic-impact Changes while preserving applicable TDD, Verification, Review, and Documentation Impact evaluation.

## STANDARD

STANDARD is the default workflow for ordinary behavioral development.

## FULL

FULL adds adversarial Specification Review, Architecture, Test Strategy, explicit Tasks, and Knowledge Capture for high-impact work.

## Verification

Verification is separate from TDD. TDD drives Implementation. Verification evaluates whether sufficient evidence supports the completed Change.

## Strict Review

Review is adversarial. Reviewers attempt to falsify the Implementation. Passing tests do not terminate Review reasoning.

## Repository-native state

Durable Forge state lives in the repository. Chat history is not authoritative durable storage.

## Chat execution

Development workflows execute through coding-agent conversations. The CLI supports Forge infrastructure; it does not execute the daily software lifecycle.

## Harness independence

Adapters translate Forge semantics into Harness-specific capabilities. Adapters do not define Forge.

## Configuration resolution

Canonical Protocol definitions remain authoritative. Projects reference canonical concepts and may strengthen or specialize behavior only where the Protocol permits it. Project configuration cannot weaken canonical Contract invariants.

## Alternatives rejected

- Test-after development as the default.
- CLI-executed SDD lifecycle.
- Feature-only abstraction.
- A single mandatory Flow.
- FAST without TDD or Review.
- Database-first persistence.
- Provider-specific orchestration in Forge Core.

## Future work

Later Changes established formal TDD evidence, traceability, Adapter drift and
conformance, and the Protocol 1 compatibility contract. Future RFCs may define
custom Flow extension and cross-implementation Protocol interoperability.
