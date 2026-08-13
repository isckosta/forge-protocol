---
forge:
  artifact: discovery
  schema: 1
change: CHG-0007
status: complete
---

# Discovery — Protocol v1 Contract Freeze

## Current version model

- Project and Adapter compatibility use integer Protocol `1`.
- Schema identifiers independently use suffix `@1`.
- Human-facing CLI and Specification still use `1-draft`.
- CLI package version remains `0.1.0.dev0` and is independent.

The least disruptive stable promotion is therefore to retain integer `1` and
replace only the human maturity label with `1`.

## Canonical surfaces inspected

- `protocol/specification.md`;
- `protocol/contract/engineering.md`;
- FULL, STANDARD, and FAST Flow YAML;
- all canonical policy YAML;
- all JSON Schemas;
- Architecture, README, Changelog, Roadmap, and RFC-0001;
- CLI version metadata and tests;
- repository-native manifests, traceability, and TDD evidence;
- Adapter descriptor and installation-record boundaries.

## Schema inventory findings

Existing schemas cover project configuration, project Flow configuration,
Change manifests, traceability, Adapter descriptors, and Adapter installation
records. Canonical Flow, Policy, and TDD-evidence identifiers have no
corresponding cataloged schema. There is no portable registry relating a
supported identifier to its schema file.

All existing JSON Schemas are Draft 2020-12 documents. Adapter interval
ordering is enforced by Python parsing but not by the schema alone. Draft
2020-12 has no portable keyword for comparing two arbitrary instance fields,
so stable validation keeps this deliberate schema-plus-semantic split.

## Repository drift findings

Read-only validation found:

- CHG-0001 through CHG-0005 manifests contain obsolete
  `documentation.status`, prohibited by `forge/change@1`;
- CHG-0004 traceability uses requirement arrays and a top-level `acceptance`
  map from an earlier shape, prohibited by `forge/traceability@1`;
- one CHG-0002 evidence note contains an unquoted colon and therefore parses as
  a YAML map rather than the intended text;
- CHG-0005 declares TDD compliance but its durable evidence retains only a
  cycle title, so it cannot substantiate Requirements, RED, or GREEN;
- CHG-0006 already uses the current manifest and traceability shapes.

These are structural discrepancies. Removing the obsolete status property and
wrapping existing task mappings in the current requirement object shape does
not change any historical outcome. The stable traceability schema can add an
optional top-level acceptance map and retain those mappings exactly.

CHG-0005 is not a mechanical shape issue. Its absent TDD detail cannot be
reconstructed, so the truthful stable migration is an explicit exception with
the historical behavior retained as Verification evidence.

## Flow consistency findings

All three Flows preserve Verification, Strict Review, blocking external-review
thread reconciliation, Documentation Impact, and applicable TDD. FAST omits a
formal Requirement identifier from its behavioral precondition because FAST
does not require formal Requirements. FULL adds its required Architecture,
Specification Review, Knowledge Capture, and related Gates.

The stable Gate vocabulary must be documented so future compatible additions
cannot silently rename or weaken these completion conditions.

## Preliminary roadmap correction

Commit `b767fa4` removed reserved Change IDs from future roadmap headings after
CHG-0006 demonstrated that planned identifiers collide with intervening work.
The user supplied explicit Intent before that documentation-only correction.
CHG-0007 records the durable rule: roadmap stages do not allocate IDs; Forge
allocates the next stable ID when a repository-native Change begins.
