---
forge:
  artifact: discovery
  schema: 1
change: CHG-0030
status: complete
---

# Discovery — Forge Experience Reporting

## Executive Summary

**Recommendation: FULL Flow and Forge Experience Report (FER).** The
repository has no contributor mode, feature-flag framework, or experience
artifact. It does have explicit project configuration, repository-native
Markdown/YAML/JSON artifacts, Git provenance, CLI command groups, and
Harness projection resources. The new mechanism should reuse those boundaries
without extending Protocol semantics.

The work is architecturally material: it adds contributor configuration,
durable persistence, an execution association model, a CLI recording surface,
Harness guidance, validation, and concurrency/failure semantics. FAST is
disqualified by `architectural_change`, `new_integration`, and
`significant_cross_module_change`; STANDARD lacks the required adversarial
Specification Review, Architecture, Test Strategy, and Tasks stages.

## Investigation

## Repository truth

- `.forge/forge.yml` is the existing project configuration, validated by
  `protocol/schemas/project.schema.json`; it has no contributor or feature-flag
  field today.
- `forge init`, `forge validate`, `forge doctor`, `forge change`, and `forge
  adapter` are the existing CLI surfaces. The CLI deliberately does not own
  Specification, Review, or Completion workflows.
- `.forge/changes/` is the normative Change artifact area. `ARCHITECTURE.md`
  identifies Markdown/YAML/JSON plus local Git as the filesystem source of
  truth and says generated Adapter state is derived.
- Protocol 1 and 2 contracts, Flows, schemas, and Change validation are
  normative. Nothing currently defines FER, contributor mode, or an internal
  artifact namespace.
- Codex and Claude Code workflow resources are parallel packaged projections;
  their instructions are guidance and cannot technically enforce Forge
  semantics.
- Existing provenance safely records known Forge version, Change, execution,
  context, timestamp, and immutable Git revision, but is specifically
  designed for Change review control. Reusing `provenance.yml` for FER would
  couple a non-normative artifact to Review authority, so FER needs a separate
  lightweight context model.
- The roadmap addendum records experience-derived fixes, but only as manual
  after-action knowledge. No durable report format exists.

## Terminology decision

“Forge Experience Report (FER)” is selected. “Experience Report” does not
conflict with current Protocol vocabulary; “Dogfooding Report” is narrower
than deliberate external validation; “Contributor Report” is too broad.

## Options considered

1. Environment variable only: easy to opt in, but poor discoverability,
   session-scoped, and weakly Git-native.
2. Extend `.forge/forge.yml`: discoverable and deterministic, but requires
   widening the project schema and makes a contributor-only concern part of
   ordinary project configuration/validation.
3. Separate `.forge/contributor.yml` plus `dogfooding/reports/`: explicit,
   local, deterministic, absent by default, ignored by normal validation, and
   clearly separated from `.forge/changes/`. **Selected.**

## Eager versus lazy

Lazy creation is selected. A report is created atomically on the first
accepted observation or positive evidence, preventing empty reports for
executions that discover nothing and preserving the requested noise rule.
Known execution context is collected at record time; unknown fields remain
`unknown` or absent.

## Boundary decision

No RFC or Protocol edit is required for the selected design. The implementation
must document that FER is contributor tooling, not Contract state, and must
keep `forge validate` and all Change Gates ignorant of FER. A future Change
may refer to a FER in prose without changing the Change schema.
