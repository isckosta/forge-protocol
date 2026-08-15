# ADR-0008 — Verifiable Review Independence

Status: Proposed pending CHG-0008 Strict Review

## Context

C-026 and Protocol Specification §25 originally described Reviewer and Resolver as distinct conceptual Roles. The first CHG-0008 implementation strengthened that to Harness-shaped session evidence, but a Laravel stress test exposed a deeper flaw: one conversational context could implement, switch its declared Role to Reviewer, issue findings, switch back to Resolver, and then switch again to Reviewer to approve its own remediation.

The actual risk is context contamination, not the label attached to a Role or session.

## Decision

Forge defines two provider-independent concepts for review independence:

- **Execution** — one concrete invocation performing Forge work;
- **Execution Context** — the transient conversational, reasoning, or equivalent non-repository context available to that Execution.

Strict Review MUST execute with both a distinct Execution and a distinct Execution Context from the Implementation or Resolution being reviewed. Changing Role inside one Execution or shared transient context is self-review and MUST NOT satisfy Strict Review.

`review.reviewer_identity` records:

- `actor_type`: `human | agent`;
- `execution_id` and `context_id` for the Reviewer;
- `resolver_execution_id` and `resolver_context_id` for the implementation/resolution being reviewed.

Equality of either Execution IDs or Context IDs is a C-026 violation. Different execution IDs cannot rescue a shared context; different context IDs cannot rescue a shared execution.

After blocking Findings are resolved, acceptance requires an independent re-review Execution whose Execution and Context are distinct from the Resolution Execution. The original Reviewer actor may perform that re-review if it runs in a compliant independent context.

The same Harness, provider, model, or agent implementation may perform multiple Roles. Forge is not requiring different vendors or models; it is requiring a real context boundary. A human reviewer is preferred for FULL where available, but human identity does not replace execution/context evidence.

## Information boundary

Independent Review may receive repository-native source, specification, requirements, architecture, tests, TDD/Verification evidence, previous Findings, and explicit review inputs. It should not require the Resolver's transient conversation or reasoning history. This approximates the human PR model: the reviewer sees the work product and durable engineering evidence rather than sharing the author's internal implementation context.

## Schema and validation

`forge/change@2` carries mandatory FULL review identity evidence. `forge/change@1` remains backward compatible and does not require the new field.

JSON Schema owns the closed evidence shape and non-empty identifiers. `forge validate` owns semantic C-026 equality checks. Harness Adapters map Forge `execution_id`/`context_id` to native run/thread/session/conversation/workspace concepts without redefining the invariant.

## Limits

Execution-context separation reduces confirmation bias and context contamination; it does not prove epistemic independence. Two isolated executions of the same model can still share correlated blind spots. Different-model review may be added later as a stronger project policy, but it is not required by the Core invariant.

## Consequences

Strict Review can no longer be satisfied by prompt-level Role switching in one session. Resolver self-review remains useful but non-authoritative. Resolution and re-review gain explicit context boundaries. The invariant becomes provider-independent and machine-checkable wherever a Harness can supply durable execution/context references.
