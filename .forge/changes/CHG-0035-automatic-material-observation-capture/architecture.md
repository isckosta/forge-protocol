---
forge:
  artifact: architecture
  schema: 1
change: CHG-0035
status: pending
---

# Architecture — CHG-0035 Automatic Material Observation Capture

## Solution Summary

Add three small boundaries under `src/forge_cli/experience/`: a structured
`ExperienceEvent`, an `ExperienceCapturePolicy`, and an
`ExperienceRecorder` adapter over the existing `ExperienceStorage`. Producers
submit facts; they never write FER directly. The policy rejects unsupported or
ordinary failures before persistence and accepts only named Forge-owned
detector events.

The first detector boundary is Adapter conformance validation, where the
existing code already has structured findings for removed stages/gates/
invariants, TDD-red bypass, strict-review bypass, and authority shift. Generic
project validation remains ignored. No lifecycle detector is introduced until
Forge owns a lifecycle execution boundary.

## Data Flow

```text
Forge-owned producer
        ↓ bounded ExperienceEvent
ExperienceCapturePolicy
        ↓ IGNORE | CAPTURE
ExperienceRecorder
        ↓ optional provenance + stable fingerprint
existing ExperienceStorage
        ↓ canonical YAML + Markdown projection
FER report
```

The recorder first checks enablement. Disabled operation returns without
fingerprinting, candidate persistence, report creation, or filesystem writes.

## Event and policy model

`ExperienceEvent` contains a supported `event_type`, optional Change,
execution, and boundary identifiers, bounded `expected`, `observed`, and
purpose-specific evidence, plus detector provenance. It contains no raw
stdout/stderr, prompt, environment, secret, credential, stack trace, or file
dump.

`ExperienceCapturePolicy.evaluate(event)` returns an immutable decision. The
initial policy allowlist contains only explicit Adapter conformance event
types. It returns `IGNORE` for ordinary validation findings and all unlisted
types. Accepted observations use existing FER fields and optional fields:

```yaml
capture:
  mode: automatic
  detector: adapter-conformance
fingerprint: <stable bounded identity>
```

The policy owns the default `uncertain` classification; it never upgrades a
candidate to `forge_problem`.

## Deduplication

Fingerprint identity is computed from event type, Change, execution/boundary,
expected invariant, and observed condition after bounded normalization. It is
stored on the observation itself as an optional field, so no separate index or
candidate file exists. Repeated identical events are ignored after the first
capture. Materially different stable conditions receive new observations.

This deliberately chooses ignore-after-first over counters/evidence growth:
the current FER schema has no occurrence model, and a count would add little
high-density evidence while complicating compatibility. A later Change may
introduce bounded occurrence metadata if real dogfooding demonstrates value.

## Failure isolation and diagnostics

The recorder catches policy/storage failures at the producer boundary and
returns a secondary `ExperienceCaptureDiagnostic`. The producer preserves its
original result and may surface the diagnostic through existing diagnostic
collections or a concise stderr warning, without changing the exit status or
normative state. No retry queue, persistent candidate store, or external
service is added.

## Compatibility and security

`ExperienceStorage._valid_document` accepts historical reports and optional
automatic fields. Markdown renders the optional capture metadata deterministically.
All new event text passes the existing bounded/sensitive-data checks before
the recorder calls storage. Automatic capture remains outside normal
validation and Change state.

## Responsibility boundaries

Forge Core/CLI may emit only mechanically established events. Adapters expose
structured conformance facts. Harnesses and Agents retain semantic/manual
capture through the existing CLI. Contributor judgment remains necessary for
root cause, workaround meaning, and follow-up.
