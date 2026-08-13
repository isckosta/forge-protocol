---
forge:
  artifact: architecture
  schema: 1
change: CHG-0004
status: approved
---

# Architecture — Codex Harness Adapter

## Objective
Implement the first concrete Harness Adapter without weakening the harness-agnostic Core established by CHG-0002.

## Boundaries
Codex-specific code lives under `src/forge_cli/adapters/codex/` and may own descriptor loading, packaged capability evidence, projection rendering, invariant assessment, and optional publication-target resolution. Generic compatibility, planning, ownership, installation state, drift, path safety, publication, and conformance remain in `src/forge_cli/adapters/`.

## Runtime flow

```text
Canonical Forge semantics + Effective Forge Configuration
    -> Codex projection renderer
    -> CodexProjectionBundle
    -> optional publication target resolution
    -> generic ProposedArtifact inputs
    -> generic plan_adapter
    -> generic AdapterPlan
    -> generic Safe Publisher
```

The Codex layer never mutates files directly.

## Package layout

```text
src/forge_cli/adapters/codex/
  __init__.py
  descriptor.py
  evidence.py
  projection.py
  assessment.py
  targets.py
  resources/
    adapter.yml
    capabilities.yml
    skills/
```

## Descriptor
`descriptor.py` loads a packaged immutable Codex Adapter descriptor into the generic `AdapterManifest`. It declares stable Adapter id/version, target `codex`, Protocol interval, and only evidence-backed generic capabilities. No network discovery occurs at runtime.

## Capability evidence
`evidence.py` owns Codex-specific evidence metadata. Each advertised capability records capability id, support status, authoritative source identifier/URL, and observation date. Evidence ships with the Adapter release and is not fetched live during planning.

## Projection bundle
`projection.py` produces deterministic logical resources. A projection resource contains logical name, media type, content, and digest. Logical resources do not imply a filesystem destination. The initial projection focuses on workflow skill content because `skills` is the only confirmed workflow capability in CHG-0004 Discovery.

## Invariant assessment
`assessment.py` classifies relevant Forge invariants as `enforced`, `represented`, or `unsupported`. This classification is separate from CHG-0002 generic capability declarations. A textual skill representation cannot be promoted to `enforced` without a proven enforcement primitive.

## Publication targets
`targets.py` may resolve a destination only from an evidence-backed Codex convention packaged with the Adapter or explicit validated project/user configuration. If neither exists, projection generation succeeds with no publication plan. Forge must not invent an undocumented default path.

## Generic planner integration
After a target is resolved, Codex projection resources are converted to generic proposed artifacts. Ownership, collision classification, expected digests, merge provenance, operation intent, installation records, drift, and safe publication remain generic Core responsibilities.

## State and limitations
Published artifacts use the existing `.forge/adapters/<adapter-id>/installation.yml`. Codex limitations use the existing generic limitation mechanisms. A generated but unpublished projection bundle does not create an installation record.

## Determinism
Runtime behavior depends only on installed Adapter version/resources, Effective Forge Configuration, repository state, and explicit target configuration. Live vendor documentation is maintainer Discovery input, never runtime input.

## Distribution
The wheel must contain the Codex resources tree. Isolated-wheel Verification must load descriptor/evidence and execute projection/conformance without source-tree or network access.

## Security
Codex-specific code never writes directly. Any published path passes through generic path safety and safe publisher protections.

## Non-goals
No invented Codex path, no live Codex session/API requirement, no Codex/OpenAI SDK dependency in generic Core, no premature generic evidence abstraction, and no unproven capability support.