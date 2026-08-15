# Knowledge Capture — CHG-0008

Durable knowledge is captured in ADR-0008, canonical C-026, Protocol Specification §§22/25/27, Review Policy, Change schemas, CLI validation, Codex projection, tests, and this Change record.

The central lesson from the Laravel stress test is that **Role separation is not context independence**. An agent that implements a revision and then changes its declared Role to Reviewer inside the same conversation still carries the Resolver's assumptions, intent, anchors, and blind spots. Forge therefore models Strict Review independence with provider-independent **Execution** and **Execution Context** boundaries.

A valid Strict Review must use both an Execution and an Execution Context distinct from the implementation or resolution being reviewed. Self-review remains useful but cannot satisfy the Strict Review Gate. After blocking Findings are resolved, acceptance requires a re-review independent from the Resolution Execution/Context.

The same Harness, provider, model, or agent implementation may perform multiple Roles if real execution/context boundaries exist. This improves operational independence and reduces context contamination; it does not guarantee epistemic independence or eliminate correlated model errors.

Repository-native source, Specification, Requirements, tests, Verification evidence, and Review Findings may cross the boundary. Transient Resolver conversation/reasoning is not authoritative review input and should not be required by the independent Reviewer.

Evidence truthfulness remains non-negotiable. Execution/context references must describe real executions and must not be invented to satisfy schema validation. This Resolver execution intentionally leaves `review.md` absent and `review.status: pending` until a genuinely independent Strict Review occurs.

Compatibility is handled through schema versioning: `forge/change@1` remains backward compatible, while `forge/change@2` carries the mandatory FULL review-independence evidence shape. Historical completed Changes are not rewritten and receive no fabricated reviewer evidence.
