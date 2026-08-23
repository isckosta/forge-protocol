---
forge:
  artifact: plan
  schema: 1
change: CHG-0033
status: approved
---

# Plan — CHG-0033 Forge Experience Report Markdown

## Plan Summary

Implement the Markdown projection as a narrow derived-artifact extension of
the existing FER subsystem:

1. Add a pure renderer for canonical `forge/experience-report@1`, with stable
   section order, source-order arrays, optional-section omission, exact IDs and
   values, safe plain-text escaping, and a generated-file comment.
2. Integrate rendering into `ExperienceStorage.record` so creation and append
   operations update the projection. Preserve locks, lazy creation, symlink
   checks, atomic canonical writes, and contributor-only failure isolation.
3. Add `forge experience render FER-####` and `forge experience render --all`
   for historical generation and drift repair. It validates canonical YAML,
   never parses Markdown, and works when FER is disabled because it is explicit.
4. Add renderer, integration, CLI, migration, drift, determinism, ordering,
   optional-field, failure-isolation, and disabled-path tests.
5. Generate Markdown for tracked FER fixtures, update
   `docs/experience-reporting.md`, and state clearly that YAML is canonical and
   Markdown is generated/derived.
6. Dogfood only after implementation approval, render historical reports,
   inspect readability/data fidelity, and record verification evidence.

## Canonical and Derived Paths

- Canonical: `dogfooding/reports/FER-####.yml`.
- Derived: `dogfooding/reports/FER-####.md`. The repository stores reports in
  one shared directory, so a shared `report.md` would collide; this
  collision-free sibling filename preserves the existing layout.
- Historical fixture: `examples/experience-report/FER-0001.md`.

## Files and Components

- Create `src/forge_cli/experience/markdown.py`.
- Modify `src/forge_cli/experience/storage.py` and
  `src/forge_cli/experience_cli.py`.
- Add focused renderer/CLI tests and extend FER integration tests.
- Modify `docs/experience-reporting.md`; add generated fixture Markdown.
- Do not modify Protocol schemas, Flow files, Change schemas, Harness
  resources, contributor enablement semantics, or normal validation paths.

## Failure and Drift Decisions

Render before persistence and never fail because a projection is missing. If
canonical replacement succeeds and derived replacement fails, report an
incomplete projection, leave canonical YAML authoritative, and permit
recovery with explicit `render`. Drift is only detected/repaired by explicit
FER operations; normal validation does not inspect Markdown.

## Verification Sequence

Run focused RED/GREEN tests, existing FER/CLI and contract/golden-path tests,
`forge experience validate`, `forge experience render --all` twice with diff
checks, the full suite, and a manual readability/data-fidelity inspection.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation.

<!-- forge:plan-approval-confirmation -->

Plan approved explicitly by the user in the active session on 2026-08-23.

<!-- forge:plan-approval-record -->

The approval record is mirrored in `provenance.yml` as `plan-approval-001`.
