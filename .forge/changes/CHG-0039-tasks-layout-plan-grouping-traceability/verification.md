---
forge:
  artifact: verification
  schema: 1
change: CHG-0039
status: complete
---

# Verification — CHG-0039 Tasks Layout Plan Grouping Traceability

## Result

**PASS**

## Summary

The new `tasks.md` scaffold layout (Overview, Execution grouping the
`T-xxx` checklist under a `### Plan N ·` heading, compact optional
`Plan`/`Requirements`/`Stories`/`Test Design` metadata using the
`TDD-xxx` convention, closing `Status`), and the updated canonical
guidance (`protocol/artifact-structure.md` §4 "Tasks"), and the focused
tests are present. `plan.md` and `test-strategy.md` are unchanged. No
Protocol integer, Change Schema, or Markdown validator was added.

## Test Evidence

- `.venv/bin/python -m pytest tests/unit/test_change_scaffolding.py -q`: **36 passed**.
- `.venv/bin/python -m pytest tests/contract/ -q`: **34 passed**.
- Full suite: `.venv/bin/python -m pytest -q`: **658 passed, 2 warnings** (warnings are from tests that deliberately inject failures into the experience-capture recorder; not product failures).
- `TDD-001` (RED, `tests/unit/test_change_scaffolding.py -k 'tasks or plan_template'`): failed before the change (4 failed, 1 passed) for the expected reason — the old renderer emitted the legacy flat `- [ ] T-001 <work item>` / `## Status` template with no grouping or metadata; passes after (36 passed).

## Forge Evidence

- `forge validate`: **PASS** ("Forge project is valid").
- `git diff --check`: **PASS**.

## Compatibility/Limitations

Historical `tasks.md` files (e.g. `CHG-0015/tasks.md`, `CHG-0016/tasks.md`)
are not rewritten and remain valid — the redesign applies to newly
generated scaffolds only. `plan.md` and `test-strategy.md` (FULL Flow)
are unchanged; both templates in `_markdown()` were diffed and confirmed
byte-identical to the prior version (`test_render_scaffold_plan_template_is_unchanged`,
`test_render_scaffold_test_strategy_template_is_unchanged`). Plan
grouping and compact traceability metadata are documentation guidance
only; `forge validate` does not parse or enforce them, consistent with
Contract C-067. No new example directory was added under
`examples/canonical-artifacts/` — consistent with `CHG-0037`/`CHG-0038`,
which did not add one for the Artifacts they redesigned either; the
human-approved Plan explicitly confirmed the ERP domain example was not
needed.

The Harness Adapter skill projections under `.claude/skills/forge/references/`
and `.agents/skills/forge/references/` were already stale relative to
`protocol/artifact-structure.md` before this Change (confirmed during
Discovery, same gap noted by `CHG-0038`). Refreshing those projections is
an Adapter-install concern outside this Change's scope.

Independent Strict Review remains pending.

## Conclusion

Verification passes for the implemented scope; the Change is not marked
complete until independent Strict Review is performed.
