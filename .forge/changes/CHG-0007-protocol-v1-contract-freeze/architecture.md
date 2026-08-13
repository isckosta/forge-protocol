---
forge:
  artifact: architecture
  schema: 1
change: CHG-0007
status: approved
---

# Architecture — Protocol v1 Contract Freeze

## Architectural objective

Make the stable Protocol contract independently readable and mechanically
auditable without creating a second lifecycle runtime or coupling validity to
network services.

## Version axes

```text
Protocol integer 1 ── compatibility semantics
Schema suffix @1   ── individual artifact shape
CLI SemVer         ── distribution behavior
Adapter SemVer     ── projection implementation
```

The axes are explicit and independent. Adapter compatibility remains the
half-open interval `min <= protocol < max_exclusive`.

## Schema catalog

`protocol/schemas/catalog.yml` is the portable index. Each entry maps one
schema identifier to one file relative to the catalog directory. The catalog
includes itself and is validated by `schema-catalog.schema.json`.

```yaml
schema: forge/schema-catalog@1
protocol: 1
schemas:
  - id: forge/project@1
    file: project.schema.json
```

Contract tests enforce:

1. catalog shape and unique identifiers/files;
2. every JSON Schema is valid Draft 2020-12;
3. catalog ID equals the schema's root `schema.const`;
4. every supported schema file is cataloged;
5. canonical YAML instances validate by their declared identifier.

## Validation boundary

The validator lives in contract tests because this Change establishes a
release/conformance Gate, not a new user-facing lifecycle command. It uses the
same packaged Protocol resources and existing PyYAML/jsonschema dependencies.
No network resolver is permitted.

## Flow consistency boundary

Contract tests validate all Flow documents and assert common completion Gates
and valid behavioral RED preconditions. Normative prose documents why FAST may
omit formal Requirement identification while retaining test-before-code.

## Historical migration

Migration is limited to:

- deleting the obsolete, redundant `documentation.status` field;
- wrapping existing CHG-0004 traceability arrays in requirement objects;
- retaining acceptance mappings as additional requirement metadata.

No evidence value or lifecycle outcome changes.

## Stable documentation

`protocol/compatibility.md` owns compatibility and deprecation rules.
`protocol/specification.md` remains the normative Core definition. README,
Architecture, Changelog, and RFC status point to these authorities rather than
restate incompatible variations.

## Security and operations

Validation reads repository and bundled resources only. Schema references are
local; remote `$ref` resolution is not introduced. The CLI remains outside
normal lifecycle execution.
