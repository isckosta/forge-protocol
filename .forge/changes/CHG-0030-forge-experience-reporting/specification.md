---
forge:
  artifact: specification
  schema: 1
change: CHG-0030
status: complete
---

# Specification — CHG-0030 Forge Experience Reporting

## Summary

Forge Experience Reporting (FER) is an explicitly enabled, contributor-only
facility for preserving concise evidence about real Forge behavior. It is
disabled when `.forge/contributor.yml` is absent or does not contain
`experience_reporting.enabled: true`. Disabled FER is not read by normal
Forge commands and creates no artifact, warning, validation requirement, or
Gate.

## Classification

**FULL.** This is a new cross-module contributor subsystem with configuration,
CLI, persistence, concurrency, Harness guidance, and failure isolation. It is
not a Protocol or Change-lifecycle extension. Discovery records the repository
evidence and rejected alternatives.

## Functional Requirements

### FR-001 — Explicit default-off enablement

FER MUST be disabled by default. `forge experience enable` MUST be the
explicit repository-local opt-in and `disable` MUST turn it off. Missing,
false, or invalid contributor configuration MUST NOT enable FER; invalid
configuration MUST be reported only by the explicitly invoked experience
command and MUST NOT make normal `forge validate` fail.

### FR-002 — Separate contributor boundary

FER state MUST live in `.forge/contributor.yml` and reports MUST live under
`dogfooding/reports/`. FER MUST NOT add fields to the Project, Change,
Protocol, Flow, Contract, Review, or provenance schemas and MUST NOT be read
by `forge validate`, `forge doctor`, Flow resolution, Change commands, or
Review completion.

### FR-003 — Minimal CLI surface

The CLI MUST expose only `forge experience enable`, `disable`, `status`,
`record`, and `validate`. `record` MUST accept one contributor-authored
structured input document from a path or stdin and MAY accept explicit
execution context options. It MUST not capture chat, prompts, logs, secrets,
credentials, or environment variables automatically.

### FR-004 — Lazy durable report

The first accepted observation or positive evidence for an execution MUST
create exactly one report lazily at `dogfooding/reports/FER-####.yml`.
Executions with nothing material MUST create no empty report. The report MUST
be human-readable, machine-readable, Git-friendly, and use
`forge/experience-report@1`.

### FR-005 — Observation semantics

Each observation MUST have an independent ID, `area`, `classification`,
`expected`, `observed`, `evidence`, and `impact`; `workaround` and `follow_up`
are optional but supported. Classification MUST be one of
`forge_problem`, `project_problem`, or `uncertain`. The writer MUST preserve
the difference between evidence and interpretation and MUST accept
`uncertain` without inventing causality.

### FR-006 — Positive evidence and candidates

Reports MUST support independent positive evidence entries and reports with
positive evidence but no failures. `follow_up_candidates` MAY contain
non-normative proposals only. Recording MUST NOT create or approve an Issue,
RFC, Change, Requirement, Review Finding, or Gate.

### FR-007 — Safe provenance

FER SHOULD populate only safely known Forge version, Protocol, Change, Flow,
Adapter, Harness, repository, commit, execution/context, and timestamp
values. Unknown or unavailable values MUST be absent or explicitly `unknown`,
never inferred. Repository paths and inputs MUST be rejected when they
contain unsupported sensitive material rather than being captured as raw
execution data.

### FR-008 — Failure isolation and concurrency

A report write failure MUST return an honest diagnostic and non-zero command
result while leaving the primary Change state untouched. Report ID
reservation and observation append MUST be safe for concurrent local
executions: no silent overwrite, duplicate report/entry ID, or lost update.
The implementation MAY use a local lock and atomic replacement; it MUST NOT
introduce distributed infrastructure.

### FR-009 — Optional Harness guidance

Codex and Claude Code projections MAY instruct contributors to record only
material Forge observations when FER is enabled, not ordinary project work,
and to use `uncertain` where causality is unclear. The guidance MUST be
identical in substance and MUST NOT claim technical enforcement or impose a
Harness obligation when FER is disabled.

## Acceptance Criteria

### AC-001 — Disabled behavior

In a normal repository with no contributor config, existing `forge validate`,
`forge doctor`, `forge change`, Adapter rendering, all supported Protocols,
and FAST/STANDARD/FULL paths behave as before; no report or FER warning exists.

### AC-002 — Opt-in behavior

After explicit enablement, a valid material input produces one durable report
and a concise path message; disablement prevents subsequent recording without
changing existing reports.

### AC-003 — Structured evidence

A report round-trip demonstrates context, expected, observed, evidence,
impact, workaround, follow-up, one `uncertain` observation, and positive
evidence without a formal Review severity.

### AC-004 — Privacy and non-normative flow

The implementation contains no network upload, telemetry, analytics, full
conversation/log capture, automatic triage, or mutation of Protocol/Change
state. Human review is the only next step.

### AC-005 — Robustness

Parallel writers produce unique IDs and preserve all accepted entries; an
injected write/lock failure is surfaced honestly and leaves Change state
unchanged; explicit FER validation reports invalid FER artifacts without
being part of normal project validation.

## Out of Scope

Telemetry, remote services, dashboards, analytics, clustering, prioritization,
automatic issue/RFC/change creation, new lifecycle stages or Gates, Change
schema references, project bug auto-classification, automatic capture of
secrets or conversation data, formal severity, and a general artifact CRUD
framework.
