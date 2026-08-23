---
forge:
  artifact: plan
  schema: 1
change: CHG-0030
status: approved
---

# Plan — Forge Experience Reporting

## Plan summary

Implement the selected non-normative FER subsystem in small TDD cycles:

1. Add `src/forge_cli/experience/` for configuration, model, context, and
   storage; keep it out of normal validation and Change lifecycle paths.
2. Add `src/forge_cli/experience_cli.py` and register the `experience` command
   group in `src/forge_cli/app.py` with `enable`, `disable`, `status`,
   `record`, and `validate` only.
3. Store opt-in state in `.forge/contributor.yml`; lazily store reports as
   `dogfooding/reports/FER-####.yml` using the contributor schema
   `forge/experience-report@1` and atomic/locked writes.
4. Add focused tests in `tests/unit/`, `tests/cli/`, and compatibility tests
   for Protocol 1/2, existing Flows, validate, doctor, Change, and Adapter
   projections.
5. Add identical optional guidance to the packaged Codex and Claude Code
   workflow resources, plus contributor documentation and a realistic fixture.
6. Enable FER only after this Plan is explicitly approved, dogfood the actual
   execution, review/redact the resulting report, and record durable knowledge.

## Planned files/components

- Create: `src/forge_cli/experience/__init__.py`, `configuration.py`,
  `context.py`, `model.py`, `storage.py`.
- Create: `src/forge_cli/experience_cli.py`; modify `src/forge_cli/app.py`.
- Create: focused unit/CLI/compatibility tests under existing test suites.
- Modify: both packaged Adapter workflow resources with non-binding FER
  guidance; add contributor documentation and one realistic report example.
- Create during implementation: the actual `dogfooding/reports/FER-*.yml`
  produced by dogfooding, only if a material observation is genuinely found.
- Do not modify: `protocol/`, `.forge/changes/` semantics, Change schemas,
  Flow files, Contract, Doctor, or external services.

## Verification sequence

Run focused RED/GREEN cycles first, then CLI and model tests, then Protocol
contract/schema tests, Adapter/golden-path tests, `forge validate`,
`forge doctor`, and the full pytest suite. Inspect the Git diff for secrets,
network calls, accidental normative artifacts, and disabled-path changes.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation.
<!-- forge:plan-approval-confirmation -->

Generation was not treated as approval. Explicit human authorization was
received from the user as “Autorizo.” in the active session on
2026-08-22T23:51:42-03:00. This record authorizes crossing the Plan /
Implementation boundary for CHG-0030; it is repository evidence, not
cryptographic or provider-native attestation.

<!-- forge:plan-approval-record -->

**Approval record.** Explicit human authorization was received from the user
as “Autorizo.” in the active session on 2026-08-22T23:51:42-03:00.
