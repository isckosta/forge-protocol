---
forge:
  artifact: intent
  schema: 1
change: CHG-0030
status: complete
---

# Intent — Forge Experience Reporting

## Summary

Introduce a local-first, opt-in mechanism for Forge maintainers and
contributors to preserve structured evidence about real Forge behavior during
dogfooding and deliberate external validation.

## Problem

Material observations currently remain in chat, temporary logs, or memory and
may never become durable maintainer evidence. The missing capability is
contributor evidence, not telemetry or project execution tracing.

## Desired Outcome

When explicitly enabled, a contributor can record a small human- and
machine-readable FER report without interrupting the primary Change workflow.
When absent or disabled, Forge behaves exactly as it does today.

## Scope

- Resolve the canonical name and non-normative architectural boundary.
- Add explicit contributor-only enablement and local Git-native report storage.
- Define a minimal report and observation model with provenance, evidence,
  uncertainty, positive evidence, follow-up candidates, and failure isolation.
- Provide the smallest CLI/guidance surface that makes recording practical.
- Dogfood the mechanism in this Change after implementation is authorized.

## Out of Scope

- No Protocol Contract, Flow, Gate, Change lifecycle, Review, or schema
  semantics are changed.
- No telemetry, network upload, analytics, dashboard, database, or automatic
  Issue/RFC/Change creation.
- No automatic capture of prompts, conversations, logs, secrets, credentials,
  environment variables, or ordinary project defects.

## Success Criteria

1. FER is disabled by default and has zero validation or lifecycle effect when
   disabled.
2. Explicit opt-in produces a durable report only when a material observation
   or positive evidence is recorded.
3. Reports distinguish expected, observed, evidence, impact, workaround, and
   non-normative follow-up; `uncertain` is valid.
4. Known provenance is populated without invented values and report failures
   do not change normative Change state.
5. Concurrent recording cannot silently overwrite reports or observations.
