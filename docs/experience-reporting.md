# Forge Experience Reporting

Forge Experience Reporting (FER) is an opt-in, local-first way for Forge
maintainers and contributors to preserve evidence from real Forge dogfooding
or deliberate external validation.

FER is disabled by default. Enable it only when you are specifically
contributing to or investigating Forge:

```bash
forge experience enable
```

Record one concise YAML observation or positive evidence entry:

```yaml
observation:
  area: plan-approval
  classification: uncertain
  expected: The Harness should stop after Plan generation.
  observed: The Harness continued directly into Implementation.
  evidence:
    - The next stage started without a recorded approval.
  impact: The cause was not yet isolated.
  workaround: The user manually interrupted execution.
  follow_up: Investigate Forge, Harness, Adapter, and project causes.
```

```bash
forge experience record --input observation.yml
```

The command prints the report path. Use its report ID with `--report` for
additional entries from the same execution:

```bash
forge experience record --input another-observation.yml --report FER-0001
```

Reports are created lazily in `dogfooding/reports/FER-####.yml`. A report
preserves expected, observed, evidence, impact, workaround, follow-up,
positive evidence, and safe provenance such as Forge version and Git commit.
Each canonical YAML report may have a generated sibling
`dogfooding/reports/FER-####.md` for human review. The YAML is the canonical
source of truth for Forge tooling; the Markdown is only a deterministic,
human-readable projection.

Do not edit the generated Markdown manually. Regenerate one report or all
historical reports from canonical YAML with:

```bash
forge experience render FER-0001
forge experience render --all
```

Rendering never reads Markdown back, never adds data, and does not require FER
to be enabled when explicitly invoked for historical recovery. If the two
files diverge, the canonical YAML wins. A missing or drifted projection does
not affect normal Forge validation or the disabled FER workflow.
Unknown values are not inferred. Use `classification: uncertain` when the
cause is unclear; an ordinary application defect is not automatically a Forge
problem.

Disable FER with `forge experience disable`. Recording is non-blocking for the
primary Forge execution: a write failure is reported honestly and does not
change Change state. Multiple local writers use exclusive IDs and atomic
updates. If canonical YAML is persisted but the derived Markdown write fails,
the command returns an error; the canonical report remains valid and a later
explicit `render` repairs the projection.

FER is not telemetry, logging, Strict Review, a bug tracker, a Change,
Protocol state, a Requirement, or a Gate. It never uploads data, captures
complete prompts/conversations/logs, or creates Issues, RFCs, or Changes.
Human contributors review reports and decide whether any follow-up is useful.
For Git review, open the `.md` sibling as the first human-readable entry
point: its stable headings and ordering make diffs easy to scan. Consult the
canonical `.yml` when checking exact machine-readable values or tooling state;
the YAML remains authoritative if the two files ever differ.

## Automatic and assisted capture

When FER is enabled, Forge may emit bounded structured facts to an Experience
Capture Policy. The policy decides `IGNORE` or `CAPTURE` before persistence.
FER is not an execution log: ordinary commands, tests, exceptions, exit codes,
and project failures are ignored.

The current automatic detector is Adapter conformance. It records only
structured Forge-owned findings such as a required stage, gate, or invariant
being removed or bypassed. Lifecycle, approval, review-authority, workaround,
and root-cause observations still depend on the Harness, Agent, or contributor
using manual `forge experience record`; guidance is not enforcement.

Automatic capture does not mean automatic classification as a Forge bug. Its
initial classification is `uncertain`; later investigation may refine it to
`forge_problem` or `project_problem`. Equivalent events in one report use a
stable fingerprint based on event type, boundary context, expected invariant,
and observed condition. Timestamps and volatile output are excluded, and no
fingerprint state is created while FER is disabled.

Automatic provenance is bounded and purpose-specific:

```yaml
capture:
  mode: automatic
  detector: adapter-conformance
  fingerprint: stable-report-local-identity
```

Automatic persistence failure is secondary and cannot change the primary Forge
result. FER remains opt-in, local, non-normative, and outside validation,
lifecycle, Gates, Review, Resolution, and Adapter conformance results.
