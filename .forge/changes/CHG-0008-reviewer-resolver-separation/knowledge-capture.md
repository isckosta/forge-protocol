# Knowledge Capture — CHG-0008

Durable knowledge is captured in ADR-0008, canonical C-026, Protocol Specification §25, Review Policy, schemas, tests, and this Change record.

The independence hierarchy is operational, not epistemic: isolated sessions of the same underlying model reduce Resolver-context contamination and confirmation bias but do not remove correlated model errors. `agent_different_model` remains future work.

Evidence truthfulness is non-negotiable. A Resolver must not invent Reviewer identity merely to satisfy structural validation, and this Change intentionally leaves `review.md` absent until a separate Reviewer executes Strict Review.

The revised requirement that every FULL `forge/change@1` manifest contain reviewer identity creates a durable compatibility conflict with C-045/C-046 and historical FULL manifests that this Change is forbidden to rewrite. That conflict needs an explicit schema/Protocol versioning or migration decision; weakening canonical validation or fabricating historical evidence is not an acceptable workaround.
