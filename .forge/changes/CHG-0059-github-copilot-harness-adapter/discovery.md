---
forge:
  artifact: discovery
  schema: 1
change: CHG-0059
status: pending
---

# Discovery — CHG-0059 Github Copilot Harness Adapter

## Executive Summary

The existing Adapter Core already owns manifest loading, publication targets,
planning, ownership, installation state, drift detection, and diagnostics. The
Copilot implementation can therefore remain a thin packaged Driver and
projection bundle. No Core change is required.

## Investigation

### Existing Adapter boundary

Codex and Claude Code each provide a packaged manifest, dated capability
evidence, publication evidence, descriptor, Driver, and deterministic
projection. `build_packaged_registry()` is the sole packaged registry
composition point. Projection resources are mapped into
`AdapterProjectionContext` and published through generic Forge-owned
operations.

### Copilot repository primitives

Official GitHub documentation records:

- repository-wide instructions at `.github/copilot-instructions.md`;
- project Agent Skills at `.github/skills/<skill-name>/SKILL.md`;
- repository hooks at `.github/hooks/*.json`;
- hooks supported by Copilot CLI and Copilot cloud agent, with documented
  execution differences. This projection supplies a POSIX shell hook for
  Linux/macOS CLI and cloud-agent execution; it does not claim Windows CLI
  coverage; and
- surface-dependent support across IDE agent and code review.

Sources are recorded in the packaged `capabilities.yml` and
`publication.yml`; runtime generation is offline and does not fetch them.

### Authority and enforcement boundary

The generated instruction file is only a discovery pointer. The effective
Engineering Contract, Flows, and canonical Capability definitions remain
repository-native Forge inputs projected as references. Skills are guidance,
not mechanical enforcement. The generated `preToolUse` hook denies matching
review-control metadata mutations only on Copilot surfaces that load repository
hooks; this limitation is stated in the projected Forge skill.

### Process remediation

The initial implementation existed on an incorrectly named feature branch
without a repository-native Change. CHG-0059 records the implementation
scope, evidence, and review retrospectively without claiming that its
Specification or Plan gates preceded the initial edits. The branch is now
named `chg-0059-github-copilot-harness-adapter`; subsequent verification and
review are being recorded against an immutable subject.
