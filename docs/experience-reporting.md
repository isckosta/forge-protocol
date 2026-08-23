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
Unknown values are not inferred. Use `classification: uncertain` when the
cause is unclear; an ordinary application defect is not automatically a Forge
problem.

Disable FER with `forge experience disable`. Recording is non-blocking for the
primary Forge execution: a write failure is reported honestly and does not
change Change state. Multiple local writers use exclusive IDs and atomic
updates.

FER is not telemetry, logging, Strict Review, a bug tracker, a Change,
Protocol state, a Requirement, or a Gate. It never uploads data, captures
complete prompts/conversations/logs, or creates Issues, RFCs, or Changes.
Human contributors review reports and decide whether any follow-up is useful.
