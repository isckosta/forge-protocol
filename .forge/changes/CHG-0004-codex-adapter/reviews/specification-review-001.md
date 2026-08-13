# Specification Review 001 — CHG-0004 Codex Harness Adapter

## Verdict
CHANGES_REQUIRED

## Review posture
Adversarial review against CHG-0002 Adapter invariants, the CHG-0004 Discovery evidence boundary, false-enforcement risk, deterministic/offline requirements, and first-concrete-Adapter precedent.

## Findings

### MAJOR-001 — Enforcement classification is underspecified
FR-025 requires three support states but does not define how they interact with generic CHG-0002 capability booleans/manifest validation. Without a precise mapping, implementation could smuggle a richer Codex-only capability model into the generic Core or report `supported=true` while enforcement is absent.

Required resolution: define capability support separately from invariant enforcement classification. Keep the CHG-0002 capability vocabulary stable. Codex-specific conformance assessment may classify an invariant as `enforced`, `represented`, or `unsupported`, but this classification must not redefine generic capability manifest semantics.

### MAJOR-002 — Skill path/layout is intentionally absent but acceptance assumes an artifact
The specification correctly refuses to invent a Codex-native path, yet AC-003/004 refer to generated skill operations. The implementation needs a deterministic projection resource boundary without claiming an undocumented vendor installation path.

Required resolution: distinguish a Forge-owned Codex projection bundle/resource from publication into a vendor-defined path. CHG-0004 may generate/package deterministic Codex skill content and plan publication only where the target path is evidence-backed or explicitly configured. No default undocumented path may be invented.

### MINOR-001 — Evidence provenance needs a machine-testable minimum
FR-008 and FR-032 require traceability/staleness but leave evidence shape open.

Required resolution: require at least capability, status, source identifier/URL, and observation date in Codex Adapter evidence metadata. This can remain Codex-specific unless later generalized by ADR.

### MINOR-002 — Compatibility with CHG-0002 explicit limitations should be stated
FR-023 should explicitly reuse the generic installation-record limitation field rather than create a second Codex limitations store.

Required resolution: state that Codex limitations are emitted through the generic plan/conformance and installation-record mechanisms.

## Positive observations

- Conservative capability policy is correct for a first Adapter.
- Repository authority and no-Core-duplication boundaries are strong.
- Offline determinism and wheel-isolation scenarios directly protect distribution quality.
- The specification correctly rejects skill-as-universal-capability substitution.

## Gate
Specification Review remains open until MAJOR-001 and MAJOR-002 are resolved and the minor clarifications are incorporated.