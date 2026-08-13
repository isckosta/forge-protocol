---
forge:
  artifact: plan
  schema: 1
change: CHG-0002
status: approved
---

# Plan — Harness Adapter Foundation

## Goal

Implement the Harness-agnostic Adapter Core as deterministic, repository-native infrastructure without adding a real Harness Adapter.

## Architecture

Core Adapter code will live under `src/forge_cli/adapters/` and model manifest validation, capabilities, planning, ownership, installation state, drift, conformance, and safe publication as separate focused boundaries. Canonical Adapter schema will live under `protocol/schemas/` and be bundled in the wheel through the existing Protocol resource packaging path.

## Global constraints

- Python 3.12+.
- TDD-first for all behavioral implementation.
- No Harness SDK dependency.
- No network requirement for validation/planning.
- No lifecycle execution commands.
- Repository-native Forge state remains authoritative.
- User-owned files are never silently overwritten.

## Phase 1 — Manifest schema and model

Create `protocol/schemas/adapter.schema.json`, Adapter manifest model, parser, and deterministic validation. Drive identity, version, Harness, compatibility bounds, and capability vocabulary through RED -> GREEN -> REFACTOR.

## Phase 2 — Protocol compatibility

Implement the exact half-open integer compatibility rule `min <= protocol < max_exclusive`. Invalid intervals (`min >= max_exclusive`) fail manifest validation.

## Phase 3 — Capability requirements and limitations

Model declared Harness capabilities separately from Forge-required representation requirements. Produce explicit limitations for required invariants that cannot be represented; never silently mark them supported.

## Phase 4 — Adapter plan

Introduce immutable plan/operation models with stable operation ordering, ownership modes, intents, content digest, and limitation/conflict collections. Planning remains mutation-free.

## Phase 5 — Repository state and collision classification

Represent existing target paths, ownership evidence, expected digests, and safe classification into create/update/preserve/conflict/delete-generated intents.

## Phase 6 — Installation record

Define `.forge/adapters/<adapter-id>/installation.yml` schema/model and deterministic serialization. Store Adapter identity/version, Harness, Protocol interval, generated Forge-owned paths/digests, and limitations only.

## Phase 7 — Drift detection

Compare recorded expected digest to current repository content. Modified generated artifacts become conflict and are never silently replaced.

## Phase 8 — Conformance checks

Implement Harness-agnostic checks for canonical invariant preservation, Flow-stage/Gate preservation, TDD RED preservation, Strict Review preservation, explicit unsupported limitations, and repository-authority preservation.

## Phase 9 — Safe publisher

Only after plan/conflict behavior is proven, implement repository-confined publication for conflict-free plans. Reuse hardened workspace/path-safety principles where appropriate, but do not couple Adapter planning to workspace initialization internals.

## Phase 10 — Verification

Run full tests, isolated wheel build/install, bundled Adapter schema resolution, offline validation/planning, deterministic repeated planning, path escape/symlink cases, dependency audit, and installation-record roundtrip.

## Phase 11 — Strict Review

Adversarially review semantic authority boundaries, overwrite safety, Protocol compatibility, determinism, path security, installation state, false conformance claims, TDD evidence, and documentation. Resolve blocking Findings and re-review.

## Phase 12 — Documentation and Knowledge

Accept RFC-0002 only if Implementation matches the proposed semantics. Update Protocol Specification, Architecture, README, CHANGELOG, and durable knowledge with final Adapter boundaries.
