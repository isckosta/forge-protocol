# Knowledge Capture — CHG-0008

The key architectural correction is that **Protocol compatibility is a semantic boundary, not a schema-filename boundary**. Protocol 1 keeps the original conceptual Reviewer/Resolver Role separation. The stronger requirement for independent Execution, independent Execution Context, and revision-bound provenance begins at integer Protocol 2.

Protocol 2 separates Review state from execution evidence. `forge/change@2` records Review Iterations; `forge/execution-provenance@1` records the Implementation, Resolution, and Review executions that produce or evaluate revisions. A re-review therefore compares against the provenance that actually produced the resolved revision instead of a stale global Resolver identifier.

Evidence assurance is intentionally explicit. `claimed` is only a declaration. `recorded` means the execution is durably represented in repository-native provenance and is the minimum for `review_passed`. `verified` adds observation by a Harness, Adapter, operator, attestation mechanism, or equivalent source. Forge Core can verify linkage and consistency of repository records; it must not advertise self-recorded values as cryptographic proof that an external execution really occurred.

FAST, STANDARD, and FULL share the Protocol 2 independence requirement. FAST reduces ceremony, not quality. The validator first resolves the project Protocol, then applies the invariant, so Protocol 1 is not retroactively strengthened.

Historical evidence gaps remain gaps. CHG-0008's original Implementation and Strict Review Iteration 1 did not capture suitable provenance, and no identifiers are fabricated for them. This Resolution is the first CHG-0008 execution recorded prospectively as `resolution-001`. Its source assurance is `recorded`, not `verified`, because no provider-native execution/context reference was available to the repository adapter.

Strict Review Iteration 1 remains historical REQUEST CHANGES evidence. Review Iteration 2 is pending and must be performed independently from `resolution-001`; this Resolver execution cannot certify its own Resolution.
