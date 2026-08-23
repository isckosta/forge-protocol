---
forge:
  artifact: architecture
  schema: 1
change: CHG-0030
status: complete
---

# Architecture — Forge Experience Reporting

## Solution Summary

Add a small `forge_cli.experience` module with four responsibilities kept
separate: opt-in configuration, report model/serialization, atomic repository
storage, and CLI orchestration. The feature reads `.forge/contributor.yml`
only when an experience command is invoked. Reports live at
`dogfooding/reports/FER-####.yml`, outside `.forge/changes/`, and use
`forge/experience-report@1` as a contributor-tooling schema rather than a
Protocol artifact.

The first `forge experience record` call lazily creates one report for an
execution. It accepts a contributor-authored structured observation (or
positive evidence), captures only provenance the CLI can establish, and
atomically updates the report. It emits one concise path message on success.

## Components and interfaces

- `experience/configuration.py`: resolve `.forge/contributor.yml`; missing
  means disabled; only `enabled: true` enables writes.
- `experience/model.py`: typed report/observation/positive-evidence data and
  YAML-safe validation. Classifications are `forge_problem`, `project_problem`,
  and `uncertain`; no severity enum is introduced.
- `experience/storage.py`: reserve the next report ID with exclusive create,
  lock the selected report, write a temporary sibling, fsync/replace, and
  release the lock. A failed write leaves the primary Change untouched and
  returns a truthful non-zero diagnostic.
- `experience/context.py`: collect Forge CLI version, supported/selected
  Protocol when safely resolvable, repository root, HEAD SHA, and explicit
  Change/Flow/Adapter/Harness values. Unavailable values are absent or
  `unknown`, never guessed.
- `experience_cli.py`: expose `enable`, `disable`, `status`, `record`, and
  `validate`. `record` is the only write operation that creates a report;
  `enable`/`disable` change contributor config only. No generic CRUD command is
  added.
- Adapter workflow resources: add concise, identical optional guidance that
  invokes FER only for material Forge observations, allows `uncertain`, and
  excludes normal project activity. Guidance must not imply technical
  enforcement.

## Data model

```yaml
schema: forge/experience-report@1
report: FER-0001
created_at: 2026-08-22T12:00:00-03:00
source:
  forge_version: 0.1.0a2
  protocol: 2
  change: CHG-0030
  flow: full
  adapter: unknown
  harness: unknown
  repository: /workspace/forge-protocol
  commit: <sha>
observations:
  - id: FER-0001-O001
    area: plan-approval
    classification: uncertain
    expected: "The Harness should stop after Plan generation."
    observed: "The execution continued into Implementation."
    evidence: ["contributor-supplied concise evidence"]
    impact: "The cause was not yet isolated."
    workaround: "The user manually interrupted execution."
    follow_up: "Investigate whether the cause is Forge, Harness, Adapter, or project."
positive_evidence:
  - id: FER-0001-P001
    area: plan-approval
    observed: "A later run stopped and requested explicit human approval."
follow_up_candidates: []
```

The writer rejects missing required observation distinctions and refuses to
serialize raw prompts, logs, environment data, or credentials. Follow-up
candidates are plain proposals and cannot create normative state.

## Enablement and execution association

`forge experience enable` writes only:

```yaml
schema: forge/contributor@1
experience_reporting:
  enabled: true
```

`disable` writes `enabled: false`; absence and false are equivalent. The
command is deterministic at repository scope and does not alter
`.forge/forge.yml`. `record` accepts explicit context options where the
contributor/Harness knows them; otherwise it records safe context only. It
prints the created report ID; subsequent entries from the same execution use
`--report FER-####` explicitly.

## Failure and concurrency semantics

Report creation uses exclusive ID reservation, and each append uses a
repository-local lock plus atomic replacement. Existing report content is
never silently overwritten. If lock, validation, or write fails, the command
reports the failure and exits non-zero; no Change manifest, lifecycle state,
Gate, or primary execution result is modified. A caller may continue the
primary workflow.

## Architectural boundary

FER is not read by `forge validate`, Change lifecycle validation, Flow
resolution, Doctor, Adapter conformance, or Review completion. It does not
extend the Engineering Contract, Protocol schemas, or Change schema. The
report directory is ordinary Git-native contributor evidence; commit, review,
redact, or delete decisions remain human decisions.
