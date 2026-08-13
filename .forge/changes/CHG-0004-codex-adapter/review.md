---
forge:
  artifact: strict_review
  schema: 1
change: CHG-0004
iteration: 1
status: failed
---

# Strict Review — CHG-0004

## Iteration 1

Result: FAILED

Findings:

- BLOCKER: 0
- MAJOR: 2
- MINOR: 1
- OBSERVATION: 1

Project policy treats MAJOR findings as blocking.

### REV-001 — Packaged descriptor/evidence are not runtime authority

Severity: MAJOR

Status: OPEN

Architecture requires `descriptor.py` to load the packaged immutable Codex descriptor and `evidence.py` to own packaged evidence metadata. The implemented runtime loader instead constructs the manifest and evidence from hard-coded Python constants in `codex/__init__.py`; `resources/adapter.yml` and `resources/capabilities.yml` are only checked for partial consistency. This creates two independently editable release authorities and allows packaged evidence to diverge from runtime behavior without necessarily failing the existing tests.

Strict Review regression probe: commit `f3d256b2adb8e80298f33d699e74f6be0a7c82d1`, workflow run `31713000903` — the stronger full-field consistency checks passed. That means current values happen to agree; it does not resolve the architectural duplication. Resolution requires either making packaged resources the runtime source or revising the approved architecture through an explicit decision. Do not fabricate a RED for a pure refactor.

### REV-002 — Packaged workflow skill resource is disconnected from projection rendering

Severity: MAJOR

Status: OPEN

Architecture says `projection.py` produces workflow skill content from canonical Forge semantics and the wheel must contain the projection resources required for planning. `resources/skills/workflow.md` currently contains only a three-line static statement, while the actual workflow representation is independently authored in `_instructions()` inside `projection.py`. The resource is packaged and asserted to exist, but it is not an input to the renderer and is not sufficient to reconstruct the rendered workflow semantics. This duplicates representation and makes the packaged skill resource misleading as release material.

Resolution should establish one source for the stable workflow framing/template while preserving canonical Flow-derived stage/gate content. If behavior changes, use regression-first TDD; if this is a semantics-preserving refactor, keep the full suite green and record it as review remediation rather than inventing RED evidence.

### REV-003 — Publication resource validation accepts nested relative names

Severity: MINOR

Status: OPEN

`resolve_resource_path()` uses `_checked()`, which rejects absolute paths, backslashes and `..`, but accepts names such as `nested/item.md`. The test is named `test_resource_name_must_be_simple_relative_path`, so implementation and test intent are inconsistent. This is not currently exploitable as root escape because the generic publisher retains repository path safety, but the Codex layout contract should either explicitly permit nested logical resources or enforce a single relative filename.

### REV-004 — Verification claim is broader than the isolated probe

Severity: OBSERVATION

Status: OPEN

`verification.md` says the distribution job proves Codex conformance under isolation. The wheel probe directly proves descriptor loading, projection, generic planning, installation-record construction and drift detection; generic CLI `validate`/`doctor` run offline separately. There is no Codex-specific conversion into `AdapterRepresentation` followed by generic `validate_conformance` in the isolated probe. The implementation has unit evidence for invariant assessment and generic conformance, but the wording should be narrowed unless an end-to-end Codex conformance adapter is added.

## Review gate

FAILED pending resolution of REV-001 and REV-002.
