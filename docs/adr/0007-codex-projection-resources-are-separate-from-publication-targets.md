# ADR-0007 — Separate projection resources from publication targets

Status: Accepted

## Decision
The Codex Adapter may generate deterministic logical projection resources without assigning them a filesystem destination. Publication requires either an evidence-backed destination packaged with the Adapter release or an explicitly configured destination validated by Forge.

If no destination is resolved, projection generation remains valid and no installation record is created.

Codex-specific evidence and invariant assessment remain outside generic Adapter Core until another Adapter justifies generalization.

## Consequences
This prevents undocumented vendor paths from becoming Forge contracts, keeps planning deterministic, and preserves the harness-agnostic Core.