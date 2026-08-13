---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0002
status: complete
---

# Knowledge Capture — Harness Adapter Foundation

## Durable decisions confirmed by implementation

### Adapters are projection boundaries, never semantic authorities

Harness Adapters consume already-resolved Effective Forge Configuration and translate it into Harness-native representation. They do not redefine canonical Flows, Gates, TDD requirements, Strict Review, Change state, or the Engineering Contract.

Adapter installation records are derived repository state and deliberately reject lifecycle fields. Harness representation may describe or enforce Forge semantics, but canonical repository-native Forge state remains authoritative.

### Protocol compatibility is a half-open integer interval

Adapter compatibility uses `min <= project_protocol < max_exclusive`. Protocol v1 intentionally avoids package-manager range grammars so independent Adapter implementations cannot reinterpret compatibility syntax.

### Capabilities describe representation primitives, not Forge semantics

The canonical capability vocabulary is `persistent_instructions`, `commands`, `skills`, `hooks`, `agent_roles`, and `generated_files`.

Unsupported Forge-required representation must become an explicit `enforced: false` limitation. A limitation may report missing enforcement; it may not authorize removal or weakening of the canonical requirement.

### Planning is pure and precedes mutation

Adapter planning consumes manifest data, Effective Forge Configuration, projections, and already-observed repository state. It produces an immutable deterministic plan before mutation.

Equivalent inputs must yield semantically equivalent plans. Shared-file updates require explicit deterministic merge provenance rather than an implicit merge strategy.

### Ownership and drift control mutation authority

`user_owned` existing files are preserved. `forge_owned` updates require recorded expected generated state matching current state. Divergent or missing generated state becomes drift/conflict rather than implicit replacement. `shared` state requires an explicit merge result before update classification.

Generated ownership is therefore evidence-based, not path-based.

### Publication has a narrow safe-mutation boundary

The Foundation publisher validates path confinement, Adapter identity, plan conflicts, installation-record consistency, and repository preconditions before mutation. UPDATE digests are revalidated immediately before write.

CREATE targets are reserved with exclusive filesystem creation before replacement. This closes the preflight-to-write no-overwrite race discovered by Strict Review: a file appearing after planning/preflight is preserved and publication fails as a conflict.

Publication records the Adapter installation state last and rolls back already-applied files on ordinary publication failure. This prevents a normal failure from being represented as a successful installation.

The Foundation does not claim crash-atomic multi-file transactions across hard process termination or machine/filesystem failure. Absence of the final installation record remains the success-boundary signal.

### Safe deletion is intentionally deferred

The plan vocabulary includes `delete_generated`, but the Foundation publisher rejects that intent. Generated deletion requires its own ownership, drift, rollback, and TDD treatment before mutation support is introduced.

### Adapter Protocol resources are distributable and offline-capable

The wheel carries `adapter.schema.json` and `adapter-installation.schema.json` with the bundled canonical Protocol resources. Manifest and installation-record loaders work from an isolated installed wheel without source-tree access or network connectivity.

### The CLI remains infrastructure-only

CHG-0002 did not add lifecycle execution commands or an independent activation-state machine. The public CLI boundary continues to exclude Specification, Implementation, Verification, Review, Resolution, and Completion execution.
