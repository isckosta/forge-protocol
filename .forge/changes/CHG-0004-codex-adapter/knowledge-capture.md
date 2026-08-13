---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0004
status: complete
---

# Knowledge Capture — Codex Harness Adapter

## Durable decisions confirmed by implementation

### Packaged Adapter metadata is runtime authority

The installed Codex Adapter loads identity, version, Protocol compatibility, and generic capability declarations from packaged `resources/adapter.yml`. It loads dated capability evidence from packaged `resources/capabilities.yml`.

Python modules expose typed loaders and a compatibility facade; they do not maintain a second hard-coded copy of release metadata. Evidence changes therefore require a deliberate Adapter resource/version change rather than live runtime discovery.

### Stable framing and canonical workflow semantics have separate sources

The packaged `resources/skills/workflow.md` supplies stable Codex workflow framing. Required stages, RED conditions, Verification, Strict Review, and Completion statements remain derived from canonical Flow input during projection.

The template is not a lifecycle authority. Generated instructions explicitly represent Forge requirements without claiming technical enforcement, and repository-native Forge state remains canonical.

### Projection does not imply publication

The Codex Adapter can produce an immutable deterministic logical bundle containing `forge-flow.md` and `forge-contract.md` without selecting a filesystem destination.

Publication occurs only when the project/user supplies an explicit validated root or the Adapter release contains evidence for a target. Forge does not invent an undocumented Codex path. Logical resource names may be nested beneath that root, while generic publication safety retains repository confinement and traversal/symlink protection.

### Capabilities and invariant enforcement remain distinct

Generic capability booleans describe available representation primitives. Codex-specific invariant assessment separately classifies a Forge invariant as `enforced`, `represented`, or `unsupported`.

A skill that communicates an invariant is only `represented` unless a technical enforcement primitive is proven. Missing enforcement is persisted through generic Adapter limitations rather than hidden or converted into a false capability claim.

Already-assessed invariant limitations enter Codex planning separately from generic capability requirements. The generic planner combines both limitation sources, and installation records preserve the combined, human-reviewable evidence. A supported representation primitive therefore cannot erase the fact that an invariant lacks technical enforcement.

### Codex integration reuses the generic Adapter Core

Codex-specific code owns descriptor/evidence loading, projection rendering, invariant assessment, and publication-target resolution. Compatibility, deterministic planning, ownership classification, collision protection, installation records, drift detection, path safety, and mutation remain generic Core responsibilities.

This boundary keeps Codex concepts and policy out of reusable Core models and avoids a parallel Adapter lifecycle.

### Runtime behavior is release-stable and offline

Descriptor loading, evidence loading, projection, planning, installation-record construction, and drift detection depend only on installed release resources and repository inputs. They do not contact live OpenAI/Codex services.

The installed wheel contains all required Codex resources, and the generic Core has no Codex/OpenAI SDK dependency. Vendor documentation is maintainership evidence for future releases, not an implicit runtime input.
