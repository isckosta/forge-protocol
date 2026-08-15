# Specification Drift — CHG-0008

Date: 2026-08-15
Status: accepted before Strict Review

## Trigger

The Laravel Forge stress test demonstrated that a single conversational context could implement a Change, switch its declared Role to Reviewer, issue findings, switch back to Resolver, and then switch again to Reviewer to approve its own remediation. The existing CHG-0008 design based on `actor_type` plus Harness-shaped `session_ref` values does not model the actual property at risk: context contamination.

## Corrected invariant

Strict Review independence is defined by **Execution** and **Execution Context**, not by a Role label and not by a Harness-specific session concept.

- An Execution is one concrete invocation performing Forge work.
- An Execution Context is the transient conversational/reasoning context available to that Execution.
- Changing Role inside the same Execution Context MUST NOT satisfy Strict Review independence.
- A Strict Review Execution MUST have both an `execution_id` and a `context_id` distinct from the Execution and Context that produced or resolved the revision under review.
- A Resolver MUST NOT resolve blocking findings in the Reviewer's Execution Context.
- After blocking findings are resolved, `review_passed` requires an independent re-review Execution whose Execution and Context are distinct from the Resolution Execution.
- The same Harness, provider, model, or agent implementation MAY perform both roles when the required execution/context boundaries are real and durably evidenced.
- Self-review remains allowed but MUST NOT satisfy Strict Review.

## Schema amendment

`forge/change@2` MUST replace Harness-shaped `session_ref` evidence with provider-independent execution/context evidence:

```yaml
reviewer_identity:
  actor_type: agent | human
  execution_id: <review execution>
  context_id: <review context>
  resolver_execution_id: <implementation-or-resolution execution>
  resolver_context_id: <implementation-or-resolution context>
```

The semantic validator MUST reject equality of either execution IDs or context IDs with C-026. Distinct execution IDs do not rescue a shared context; distinct context IDs do not rescue a shared execution.

## Impact on existing CHG-0008 work

The previous `agent_same_session | agent_isolated_session | human` hierarchy is superseded. `actor_type` is descriptive (`agent | human`); independence is proven by execution/context evidence rather than asserted by actor classification. Review Policy and Codex projection must express the same invariant. Existing `forge/change@1` compatibility remains unchanged.

This drift is recorded before the amended production implementation and before Strict Review.