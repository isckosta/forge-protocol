# Forge Protocol 1 Compatibility

Status: Stable

This document defines how Forge Protocol 1 evolves. The normative Core
semantics remain in `specification.md`; this policy determines whether a
change may retain integer Protocol identifier `1`.

## Independent versions

Forge has four independent version axes:

- **Protocol version** — integer compatibility contract used by projects and
  Adapters. The stable current identifier and human label are both `1`.
- **Schema version** — suffix in an artifact identifier such as
  `forge/change@1`. It versions that artifact shape, not the entire Protocol.
- **CLI version** — Semantic Versioning of the installable implementation.
- **Adapter version** — Adapter-specific Semantic Versioning, with an explicit
  half-open Protocol interval `min <= protocol < max_exclusive`.

A release may change one axis without changing the others when their respective
contracts remain compatible.

## Compatible Protocol 1 evolution

Protocol 1 may retain identifier `1` for:

- optional fields or artifacts whose absence preserves existing meaning;
- new independently versioned schemas that do not invalidate existing valid
  instances;
- stronger validation diagnostics for states already invalid under the
  published contract;
- editorial clarification that does not alter normative meaning;
- additional Harness representations or enforcement mechanisms that preserve
  canonical semantics;
- implementation fixes that make behavior conform to existing requirements.

Compatible additions must not make a previously valid conforming Protocol 1
project, Change, Flow, or Adapter invalid merely because it does not use the
addition.

## Breaking Protocol evolution

A new integer Protocol identifier is required to:

- remove or weaken a Contract invariant;
- remove a previously supported required capability or artifact;
- make a previously optional field required for existing instances;
- change the meaning of an existing required field, stage, Gate, severity, or
  ownership mode;
- invalidate a previously valid conforming Protocol 1 instance;
- change the Adapter compatibility interval semantics;
- authorize a Flow to bypass applicable TDD/RED, Verification, Strict Review,
  blocking external-review thread reconciliation, Documentation Impact, or
  truthful Completion.

An individual artifact shape may instead require a new schema suffix when the
break is limited to that artifact. If the shape change also changes Core
semantic obligations, both the schema and integer Protocol version must change.

## Deprecation

A deprecation record must state:

1. the affected construct;
2. its replacement or migration path;
3. the first CLI release or Protocol revision that marks it deprecated;
4. the compatibility period during which it remains supported;
5. the earliest removal boundary.

Deprecation does not authorize early removal. Removal that meets a breaking
condition above requires the next integer Protocol identifier. Security or data
integrity emergencies may shorten a CLI support window, but they do not permit
the implementation to mislabel a breaking Protocol contract as compatible.

## Stable lifecycle vocabulary

Protocol 1 freezes the canonical Flow names `FAST`, `STANDARD`, and `FULL` and
the common quality obligations:

- applicable TDD with observed valid RED before production behavior;
- Verification beyond merely passing tests;
- adversarial Strict Review;
- reconciliation of blocking threads on an active external review surface;
- explicit Documentation Impact evaluation;
- Completion only when manifest state agrees with repository reality.

Flows may differ in planning ceremony and may add stricter Gates. FAST does not
require a formal Requirement identifier, but it retains the applicable
test-before-implementation and completion quality Gates.

## Schema catalog

`schemas/catalog.yml` is the portable list of supported schemas. Cataloged
schemas use JSON Schema Draft 2020-12 and must agree with the identifier in the
instance's top-level `schema` field. Cross-field semantic constraints that
standard JSON Schema cannot express remain part of canonical deterministic
validation; Adapter interval ordering is one such constraint.
