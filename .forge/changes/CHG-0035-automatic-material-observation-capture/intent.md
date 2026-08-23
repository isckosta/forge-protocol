---
forge:
  artifact: intent
  schema: 1
change: CHG-0035
status: active
---

# Intent — CHG-0035 Automatic Material Observation Capture

## Summary

Evolve the existing opt-in Forge Experience Reporting (FER) facility so that
mechanically observable Forge-relevant facts can be evaluated by a capture
policy and recorded without relying exclusively on contributor memory.

## Problem

The current `forge experience record` surface is deliberately manual. The
repository has no runtime lifecycle/approval executor, so broad automatic
recording would either miss semantics the Forge cannot observe or turn FER
into noisy telemetry.

## Desired Outcome

When FER is enabled, structured Forge facts pass through an Experience Capture
Policy. Accepted high-confidence facts become concise observations with
automatic provenance and stable deduplication; ordinary project/test failures
are ignored; semantic observations remain available through manual recording.

## Scope

- Define the smallest structured event, policy, recorder, and deduplication
  boundaries needed by current Forge mechanics.
- Integrate only with mechanically verifiable Forge-owned findings.
- Preserve `forge/experience-report@1`, Markdown projection, positive evidence,
  manual recording, opt-in configuration, privacy guards, and failure
  isolation.
- Document responsibility across Forge CLI, Adapter, Harness, Agent, and
  contributor.

## Out of Scope

No generic event bus, lifecycle engine, telemetry, logging, crash reporting,
automatic root-cause diagnosis, capture of all failures, new CRUD commands,
Protocol/Contract/Flow/Gate semantics, or mandatory FER state.

## Success Criteria

1. Disabled FER performs no report, fingerprint, or auxiliary-state write.
2. A supported Forge-owned fact is policy-accepted and recorded as
   `uncertain` unless causality is independently established.
3. Ordinary project/test failures are ignored.
4. Equivalent facts do not create observation spam; distinct facts remain
   independently representable.
5. Automatic provenance identifies detector and mode without raw prompts,
   logs, secrets, or unbounded output.
6. FER write failure is visible secondarily and cannot alter the primary Forge
   result or lifecycle state.
