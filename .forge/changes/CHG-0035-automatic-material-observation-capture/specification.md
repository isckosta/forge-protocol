---
forge:
  artifact: specification
  schema: 1
change: CHG-0035
status: pending
---

# Specification — CHG-0035 Automatic Material Observation Capture

## Summary

Introduce a small Event → Capture Policy → FER Recorder path at mechanically
observable Forge-owned boundaries. It is active only when FER is explicitly
enabled, records only policy-accepted material observations, and preserves
manual recording for semantic evidence.

## Classification

**FULL.** The Change crosses runtime detection, policy, persistence,
deduplication, privacy, Adapter/CLI boundaries, compatibility, and tests, but
does not change Protocol or lifecycle authority.

## Functional Requirements

## FR-001 — Opt-in disabled path

Automatic capture MUST resolve the existing contributor configuration before
recording or fingerprint persistence. Missing/false configuration MUST have
no report, auxiliary-state, lifecycle, or Gate side effect.

## FR-002 — Structured event boundary

Producers MUST emit bounded structured events rather than writing FER. Events
MUST contain supported type, expected invariant, observed condition, context,
and bounded evidence. Raw prompts, logs, environment dumps, secrets,
credentials, full stdout/stderr, and arbitrary file contents MUST be rejected.

## FR-003 — Capture policy

`ExperienceCapturePolicy` MUST return `IGNORE` or `CAPTURE`. Ordinary project
failures, generic exceptions, non-zero exits, and unclassified findings MUST
return `IGNORE`; only supported Forge-owned invariant events may capture.

## FR-004 — Hybrid attribution and provenance

Automatic observations MUST default to `classification: uncertain` and include
bounded provenance identifying automatic mode and detector. Manual recording
MUST preserve the existing input surface and classifications.

## FR-005 — Stable deduplication

Equivalent events in one report MUST NOT create duplicate observations. The
identity MUST use stable event type, Change, execution/boundary, expected
invariant, and observed condition; it MUST exclude timestamps and volatile
output. Distinct stable conditions MUST remain independently representable.

## FR-006 — Backward-compatible FER

Existing `forge/experience-report@1` YAML and Markdown MUST remain valid. New
automatic fields MUST be optional where possible; no `@2` schema is introduced
without a demonstrated compatibility failure and explicit decision.

## FR-007 — Failure isolation

Policy or FER persistence failure MUST preserve the primary Forge result,
Change state, lifecycle, Gates, and Adapter result, while exposing a truthful
bounded secondary diagnostic.

## FR-008 — Non-normative responsibility

Automatic capture MUST NOT become a requirement for validate, Change validity,
lifecycle progression, Review/Resolution PASS, Gate completion, Flow
resolution, Adapter conformance, or mergeability. Semantic observations remain
manual unless a future verifiable boundary exists.

## Acceptance Criteria

## AC-001 — Disabled

Absent/false configuration produces no report, Markdown, fingerprint, or
auxiliary state and does not alter the primary result.

## AC-002 — Material event

An enabled, supported Forge-owned event accepted by policy creates one concise
`uncertain` observation with automatic detector provenance.

## AC-003 — Ordinary failure ignored

A project/test failure, generic exception, or non-zero result without a
supported Forge event produces no observation.

## AC-004 — Deduplication

Repeated equivalent events coalesce; different stable expected/observed
conditions create separate observations.

## AC-005 — Isolation and privacy

Injected policy/write failure preserves the primary result, and unsafe or
unbounded evidence is rejected before persistence.

## AC-006 — Compatibility and projection

Historical reports remain valid, manual recording continues to work, and
automatic entries render consistently in YAML and Markdown.

## Out of Scope

Generic event logging, telemetry, external services, crash reporting, all
failure capture, root-cause diagnosis, automatic `forge_problem` assignment,
candidate CRUD/confirmation commands, lifecycle/approval/review execution,
Protocol/Contract/Flow/Gate changes, and replacement of investigation, fix,
Review, or Resolution workflows.
