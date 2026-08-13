# Specification Review 002 — CHG-0004 Codex Harness Adapter

## Verdict
APPROVED

## Resolution check

- MAJOR-001 resolved: generic capability declarations remain unchanged; invariant enforcement uses separate Codex-specific `enforced` / `represented` / `unsupported` assessment without redefining Core capability semantics.
- MAJOR-002 resolved: projection bundle generation is separated from vendor-path publication; no undocumented Codex destination path may be invented.
- MINOR-001 resolved: evidence metadata now requires capability, status, source identifier/URL, and observation date.
- MINOR-002 resolved: Codex limitations explicitly reuse generic plan/conformance and installation-record mechanisms.

## Adversarial re-check

The revised specification preserves CHG-0002 boundaries, does not introduce a hidden Codex SDK dependency, keeps runtime behavior offline/deterministic, protects user artifacts, and makes false enforcement claims structurally testable.

The most important precedent is now explicit: Forge can generate a deterministic Codex projection bundle even when the vendor publication path is not proven. This prevents documentation uncertainty from turning into invented filesystem conventions.

## Gate
Specification Review passes. Architecture may begin.