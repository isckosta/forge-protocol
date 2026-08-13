---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0007
status: approved
---

# Test Strategy — Protocol v1 Contract Freeze

## Objective

Prove stable identity, schema/catalog closure, canonical instance validity,
Flow quality invariants, historical migration integrity, and installed-wheel
availability.

## TDD cycles

### Cycle 1 — Schema catalog and schema validity

RED: contract test fails because the catalog does not exist.

GREEN: catalog and missing Flow, Policy, and TDD-evidence schemas exist; every
entry resolves and each schema is valid with matching identity.

### Cycle 2 — Canonical repository instances

RED: instance audit exposes obsolete manifest fields and the old CHG-0004
traceability shape.

GREEN: mechanical migrations make all selected instances valid without
changing historical facts.

### Cycle 3 — Stable version label

RED: CLI test expects stable `1` but observes `1-draft`.

GREEN: display metadata changes to `1` while compatibility remains integer 1.

### Cycle 4 — Defects discovered during review

Each automatable behavioral defect receives its own valid RED before a fix.

## Contract test dimensions

- catalog schema and uniqueness;
- Draft 2020-12 meta-schema validity;
- catalog/file closure and identity agreement;
- canonical YAML validation by declared schema;
- invalid Adapter interval rejection through schema plus semantic validation;
- common Flow completion and behavioral RED Gates;
- preservation of CHG-0004 task/acceptance facts.

## Documentation review

Human adversarial review checks normative consistency across Specification,
Contract, Flows, Policies, compatibility policy, Architecture, README,
Changelog, Roadmap, and RFC-0001. Prose is not tested by source-text matching.

## Distribution verification

Build a wheel, install it in an isolated temporary environment, verify
`forge version`, locate the packaged schema catalog and all cataloged files,
and perform validation without the source tree or network access.
