# Forge Protocol Compatibility

Status: Stable

This document defines the compatibility boundary between integer Forge Protocol versions. Protocol version and artifact schema version are independent axes.

## Independent versions

Forge has four independent version axes:

- **Protocol version** — integer Core semantic compatibility contract used by projects and Adapters.
- **Schema version** — suffix in an artifact identifier such as `forge/change@1` or `forge/change@2`; it versions that artifact shape, not the entire Protocol.
- **CLI version** — Semantic Versioning of the installable implementation.
- **Adapter version** — Adapter-specific Semantic Versioning, with an explicit half-open Protocol interval.

A schema suffix MUST NOT be used to conceal a breaking Core semantic change that belongs at the integer Protocol boundary.

## Protocol 1 — frozen semantic meaning

Protocol 1 remains valid and preserves its published meaning. In particular, C-026 means that Reviewer and Resolver are distinct conceptual Roles. Protocol 1 does not retroactively require independent Execution identifiers, independent Execution Context identifiers, revision-bound provenance, or a provenance ledger.

Previously valid conforming Protocol 1 projects and completed Change instances MUST remain valid merely because Protocol 2 exists. `forge/change@1` preserves its historical shape and meaning.

Compatible Protocol 1 maintenance may still include editorial corrections, implementation fixes that enforce already-published semantics, optional artifacts whose absence preserves existing meaning, and independently versioned schema additions that do not invalidate Protocol 1 instances.

## Protocol 2 — review-independence boundary

Protocol 2 intentionally strengthens Strict Review from conceptual Role separation to revision-bound independent Execution and Execution Context provenance. Because this invalidates states that were valid under Protocol 1, the stronger obligation is identified as integer Protocol `2` rather than being relabeled as a compatible Protocol 1 revision.

Protocol 2 active Changes use `forge/change@2` and declare `protocol: 2`. A Protocol 2 repository MAY retain completed historical `forge/change@1` Changes without retroactive migration or fabricated provenance. An active Protocol 2 Change MUST NOT downgrade to `forge/change@1` to bypass the Protocol 2 Strict Review Gate.

The `forge/execution-provenance@1` artifact is the repository-native ledger for Protocol 2 execution records. Its schema version is independent from Protocol 2; a future compatible provenance shape could receive another schema suffix without necessarily creating Protocol 3.

## Breaking Protocol evolution

A new integer Protocol identifier is required to:

- remove or weaken a Contract invariant;
- remove a previously supported required capability or artifact;
- make a previously optional field or evidence source mandatory for existing instances;
- change the meaning of an existing required field, stage, Gate, severity, or ownership mode;
- invalidate a previously valid conforming instance;
- change Adapter compatibility interval semantics;
- authorize a Flow to bypass applicable TDD/RED, Verification, Strict Review, blocking external-review reconciliation, Documentation Impact, or truthful Completion.

If an artifact-shape change also changes Core semantic obligations, both the relevant schema version and integer Protocol version must be selected correctly.

## Deprecation

A deprecation record must state the affected construct, replacement or migration path, first release or Protocol revision marking it deprecated, compatibility period, and earliest removal boundary. Deprecation does not authorize early removal.

## Stable lifecycle vocabulary

Protocol 1 and Protocol 2 both retain FAST, STANDARD, and FULL and the common quality obligations: applicable TDD, Verification beyond passing tests, adversarial Strict Review, blocking-thread reconciliation on active external review surfaces, Documentation Impact evaluation, and truthful Completion.

Protocol 2 adds the same review-provenance quality invariant to FAST, STANDARD, and FULL. FAST reduces ceremony, not quality.

## Schema catalog

`schemas/catalog.yml` is the portable list of schemas shipped by the distribution. Catalog presence does not imply that every schema is normative for every Protocol version. Applicability is defined by the selected Protocol contract and the artifact's own identifier. Cross-field semantic constraints that JSON Schema cannot express remain deterministic Core validation responsibilities.
