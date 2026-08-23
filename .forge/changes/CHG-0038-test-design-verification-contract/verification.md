---
forge:
  artifact: verification
  schema: 1
change: CHG-0038
status: complete
---

# Verification — CHG-0038 Test Design Verification Contract

## Result

**PASS**

## Summary

The new `test-design.md` scaffold layout (Overview, Test Strategy, Coverage
Map, `TD-xxx` scenarios, Manual Acceptance, valid-RED guidance, Requirement
Coverage, Coverage Gaps, Test Design Gate), the split canonical guidance
(Test Design vs. Test Strategy), and the focused tests are present.
`test-strategy.md` is unchanged. No Protocol integer, Change Schema, or
Markdown validator was added.

## Test Evidence

- `.venv/bin/python -m pytest tests/unit/test_change_scaffolding.py -q`: **31 passed**.
- `.venv/bin/python -m pytest tests/contract/ -q`: **34 passed**.
- Full suite: `.venv/bin/python -m pytest -q`: **653 passed, 2 warnings** (warnings are from tests that deliberately inject failures into the experience-capture recorder; not product failures).
- `TDD-001` (RED, `tests/unit/test_change_scaffolding.py -k 'test_design or test_strategy_template'`): failed before the change (5 failed) for the expected reason — the old renderer emitted the legacy `Objective`/`Strategy`/`TDD-001`/`Completion Criteria` template; passes after (31 passed).

## Forge Evidence

- `forge validate`: **PASS** ("Forge project is valid").
- `git diff --check`: **PASS**.

## Compatibility/Limitations

Historical `test-design.md` files (e.g. `CHG-0037/test-design.md`) are not
rewritten and remain valid — the redesign applies to newly generated
scaffolds only. `test-strategy.md` (FULL Flow) is unchanged; its template
in `_markdown()` was diffed and confirmed byte-identical to the prior
version. `TD-xxx` scenario structure, Manual Acceptance, and valid-RED
content are documentation guidance only; `forge validate` does not parse
or enforce them, consistent with Contract C-067.

The Harness Adapter skill projections under `.claude/skills/forge/references/`
and `.agents/skills/forge/references/` were already stale relative to
`protocol/artifact-structure.md` before this Change (confirmed by diff
during Discovery — they predate `CHG-0037`'s Specification rewrite as
well). Refreshing those projections is an Adapter-install concern outside
this Change's scope, consistent with `CHG-0037` leaving the same gap.

Independent Strict Review remains pending.

## Conclusion

Verification passes for the implemented scope; the Change is not marked
complete until independent Strict Review is performed.
