---
forge:
  artifact: strict_review
  schema: 1
change: CHG-0004
iteration: 4
status: passed
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

Status: RESOLVED

Architecture requires `descriptor.py` to load the packaged immutable Codex descriptor and `evidence.py` to own packaged evidence metadata. The implemented runtime loader instead constructs the manifest and evidence from hard-coded Python constants in `codex/__init__.py`; `resources/adapter.yml` and `resources/capabilities.yml` are only checked for partial consistency. This creates two independently editable release authorities and allows packaged evidence to diverge from runtime behavior without necessarily failing the existing tests.

Strict Review regression probe: commit `f3d256b2adb8e80298f33d699e74f6be0a7c82d1`, workflow run `31713000903` — the stronger full-field consistency checks passed. That means current values happen to agree; it does not resolve the architectural duplication. Resolution requires either making packaged resources the runtime source or revising the approved architecture through an explicit decision. Do not fabricate a RED for a pure refactor.

Resolution: TDD-008 made `resources/adapter.yml` and `resources/capabilities.yml` the inputs to the runtime descriptor. The compatibility facade in `codex/__init__.py` now re-exports the descriptor/evidence types and loader rather than defining a parallel metadata authority. The regression was RED at commit `953c4bcff0dda6052ca6fd17dbded9748bec27ca` (Tests run `31714282849`) and GREEN at commit `17ff84cacfd76c676e931ffd686fc7d4f8e613b4` (Tests run `31715000881`). Commit `5fb85f28119f0bd09a6fcba1148f58af982b4036` was rejected as GREEN evidence because its malformed fixture failed during YAML parsing rather than proving the intended behavior.

### REV-002 — Packaged workflow skill resource is disconnected from projection rendering

Severity: MAJOR

Status: RESOLVED

Architecture says `projection.py` produces workflow skill content from canonical Forge semantics and the wheel must contain the projection resources required for planning. `resources/skills/workflow.md` currently contains only a three-line static statement, while the actual workflow representation is independently authored in `_instructions()` inside `projection.py`. The resource is packaged and asserted to exist, but it is not an input to the renderer and is not sufficient to reconstruct the rendered workflow semantics. This duplicates representation and makes the packaged skill resource misleading as release material.

Resolution should establish one source for the stable workflow framing/template while preserving canonical Flow-derived stage/gate content. If behavior changes, use regression-first TDD; if this is a semantics-preserving refactor, keep the full suite green and record it as review remediation rather than inventing RED evidence.

Resolution: TDD-009 connects `resources/skills/workflow.md` to projection rendering as the stable workflow framing. Required stage order and Gate statements remain derived from canonical Flow input. The regression was RED at commit `02256742b57787a10fbb34d3ce528c9b2202c418` (Tests run `31715085289`) and GREEN at commit `d4930792fe8756aab571d1bb5ddec28db87bf6d1` (Tests run `31715325950`; Distribution Verification run `31715325961`).

### REV-003 — Publication resource validation accepts nested relative names

Severity: MINOR

Status: ACCEPTED

`resolve_resource_path()` uses `_checked()`, which rejects absolute paths, backslashes and `..`, but accepts names such as `nested/item.md`. The test is named `test_resource_name_must_be_simple_relative_path`, so implementation and test intent are inconsistent. This is not currently exploitable as root escape because the generic publisher retains repository path safety, but the Codex layout contract should either explicitly permit nested logical resources or enforce a single relative filename.

Disposition: nested logical resource names remain permitted beneath the validated publication root. The generic publisher still enforces repository confinement, traversal protection, and symlink safety before mutation. The imprecise test name is accepted as a non-blocking maintainability risk; no behavioral contract or security boundary depends on single-component resource names.

### REV-004 — Verification claim is broader than the isolated probe

Severity: OBSERVATION

Status: RESOLVED

`verification.md` says the distribution job proves Codex conformance under isolation. The wheel probe directly proves descriptor loading, projection, generic planning, installation-record construction and drift detection; generic CLI `validate`/`doctor` run offline separately. There is no Codex-specific conversion into `AdapterRepresentation` followed by generic `validate_conformance` in the isolated probe. The implementation has unit evidence for invariant assessment and generic conformance, but the wording should be narrowed unless an end-to-end Codex conformance adapter is added.

Resolution: Verification now distinguishes the isolated wheel probe from unit-level invariant assessment and generic conformance evidence. It no longer attributes Codex-specific `AdapterRepresentation` validation to the distribution probe.

## Iteration 2 — Adversarial Re-review

Result: PASSED

Re-review examined:

- packaged descriptor and capability evidence as runtime authority;
- packaged workflow framing with stages and Gates still derived from canonical Flow input;
- public facade compatibility after descriptor/evidence extraction;
- deterministic projection content and digests;
- capability overclaim and invariant enforcement separation;
- optional publication target resolution and repository path confinement;
- generic planner, ownership, collision, drift, and installation-state reuse;
- isolated wheel resource loading and offline operation;
- runtime dependency isolation from Codex/OpenAI SDKs;
- temporal validity of TDD-008 and TDD-009 evidence.

No unresolved BLOCKER or MAJOR findings remain.

Fresh post-remediation evidence at code commit `b24630f0a4b2a0930504008a43ab516894779005`:

- Tests workflow run `31716161391`, job `94501326877`: SUCCESS (`134 passed`);
- Distribution Verification run `31716161380`, job `94501326662`: SUCCESS;
- isolated wheel build/install and packaged Codex resource probe: SUCCESS;
- offline `forge version`, `init`, `validate`, and `doctor`: SUCCESS;
- runtime dependency audit: SUCCESS;
- independent local full suite: `134 passed`.

## Review gate

PASSED.

Remaining accepted risk: REV-003 only.

## Iteration 3 — GitHub Review Reconciliation

Result: FAILED

### REV-005 — Represented-invariant limitations do not reach the plan

Severity: MAJOR

Status: RESOLVED

The unresolved P1 thread on PR #5 identifies a real integration gap. `assessment.to_generic_limitation()` can classify a represented but technically unenforced Forge invariant, but `plan_codex_projection()` accepts only generic capability requirements. Because the Codex descriptor advertises `skills` as supported, generic capability evaluation emits no limitation for an invariant represented through that skill. The resulting plan and installation record therefore omit required non-enforcement evidence, violating FR-024 and FR-031.

Resolution requires regression-first TDD proving that a generic `CapabilityLimitation` created from Codex invariant assessment survives both planning and installation-record construction independently of the supported capability boolean.

Resolution: TDD-010 adds a separate `invariant_limitations` input at the Codex integration boundary and forwards those already-assessed limitations to the generic planner independently of capability support evaluation. The regression was RED at commit `5b2d8cc4fcf09d456474561e9c77d5e89fd350e8` (Tests run `31718814345`, job `94510276284`: `1 failed, 134 passed`) and GREEN at commit `5b6a53e5bf98e5bbb4650c20a78fd71bf85ee96d` (Tests run `31719038475`, job `94511020787`: `135 passed`; Distribution Verification run `31719038459`, job `94511020449`). The test follows the real assessment-to-plan path and proves the limitation survives installation-record construction.

## Iteration 3 review gate

FAILED at Iteration 3, requiring remediation and a new adversarial re-review.

## Iteration 4 — Adversarial Re-review

Result: PASSED

Re-review examined:

- the unresolved P1 GitHub thread against FR-024 and FR-031;
- the real Codex invariant-assessment to generic-limitation conversion path;
- separation between supported capability evaluation and represented-but-unenforced invariant limitations;
- persistence of both limitation sources through `AdapterPlan` and `AdapterInstallationRecord`;
- temporal validity of the TDD-010 RED and GREEN commits;
- regression safety through the full automated suite and isolated wheel verification;
- the previously reported packaged-resource authority concern, already resolved by TDD-008.

No unresolved BLOCKER or MAJOR findings remain.

Fresh post-remediation evidence at code commit `5b6a53e5bf98e5bbb4650c20a78fd71bf85ee96d`:

- Tests workflow run `31719038475`, job `94511020787`: SUCCESS (`135 passed`);
- Distribution Verification run `31719038459`, job `94511020449`: SUCCESS;
- isolated wheel build/install and packaged Codex resource probe: SUCCESS;
- offline `forge version`, `init`, `validate`, and `doctor`: SUCCESS;
- runtime dependency audit: SUCCESS;
- focused local Codex integration suite: `16 passed`;
- independent local full suite: `135 passed`.

## Final review gate

PASSED.

Remaining accepted risk: REV-003 only.
