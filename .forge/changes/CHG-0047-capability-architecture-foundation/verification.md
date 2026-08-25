---
forge:
  artifact: verification
  schema: 1
change: CHG-0047
status: complete
---

# Verification — CHG-0047 Capability Architecture Foundation

## Result

**PASS**

## Summary

`capabilities/README.md` and `capabilities/capability.md` document the
Forge Capability concept, its boundaries, and its minimal human contract.
`src/forge_cli/capabilities/` implements the minimal, frozen `Capability`
model and a deterministic `load_capability(path)` loader (locate → read →
parse → normalize → return), with explicit, specific errors for a missing
file, missing/invalid frontmatter, or a missing/empty required section.
No concrete capability, registry, executor, plugin system, or new Gate
was introduced.

## Test Evidence

- `.venv/bin/python -m pytest tests/capabilities/ -q`: **26 passed**.
- Full suite: `.venv/bin/python -m pytest -q`: **747 passed, 2 warnings**
  (warnings pre-exist this Change — deliberate failure injection in
  `tests/unit/test_experience_capture.py`, unrelated to this Change).
- `TDD-001` (RED, `tests/capabilities/test_model.py`): failed collection
  before the change (`ModuleNotFoundError: No module named
  'forge_cli.capabilities.model'`) for the expected reason; passes after
  (3 passed).
- `TDD-002` (RED, `tests/capabilities/test_loader.py`): failed collection
  before the change (`ModuleNotFoundError: No module named
  'forge_cli.capabilities.loader'`) for the expected reason; passes after
  (22 passed at the time; 23 after TDD-003 added one more test).
- `TDD-003` (RED, `tests/capabilities/test_loader.py -k fenced`): added in
  response to independent Strict Review Iteration 1, Finding R-002 —
  failed for the expected reason (a heading-shaped line inside a fenced
  code block inside a section body was silently treated as the start of
  a new section, truncating the enclosing section); passes after fixing
  `_parse_sections` to track fence state.

## Forge Evidence

- `forge validate`: **PASS** ("Forge project is valid").
- `git diff --stat` against tracked files: no output — every change in
  this Change is a new, previously untracked path (`capabilities/`,
  `src/forge_cli/capabilities/`, `tests/capabilities/`, and this Change's
  own `.forge/changes/CHG-0047-...` Artifacts); no existing tracked file
  was modified.
- `grep` for `CapabilityRegistry`, `CapabilityExecutor`,
  `CapabilityPipeline`, `CapabilityGraph`, `CapabilityProvider` across
  `src/forge_cli/capabilities/`, `capabilities/`, and
  `tests/capabilities/`: **no matches**.
- `pyproject.toml`, `protocol/`, `.claude/skills/forge/references/engineering-contract.md`,
  and `src/forge_cli/adapters/capabilities.py` are unchanged by this
  Change (confirmed via `git diff --name-only` against each path:
  no output).

## Compatibility/Limitations

No concrete Capability (`investigate`, `review`, `provenance`,
`challenge`, or other) was implemented — this Change is the foundation
only, as scoped. No `capabilities/<name>/` directory beyond the
documentation pair exists yet; a future Change introducing `investigate`
is expected to add `capabilities/investigate/CAPABILITY.md` and use the
existing loader unmodified.

`src/forge_cli/adapters/capabilities.py` (Harness capability
requirements/limitations — an unrelated, pre-existing concept) is
untouched; `capabilities/README.md` explicitly documents the distinction
so a future reader does not conflate the two.

The loader takes an explicit `Path` and performs no package/fallback
resolution (unlike `protocol_resources.resolve_protocol_root`) and no
discovery/enumeration across a directory — this is a deliberate,
documented scope boundary (NFR-001, FR-004's Boundary), not an
oversight: a Forge Capability definition is repository-native content of
whichever Forge-enabled repository uses it, not a packaged resource of
the `forge-cli` distribution, so no `pyproject.toml` change was needed or
made.

No JSON Schema or other rigid machine format was introduced for the
capability contract, per the original request; `capability.md` is prose
with a two-field frontmatter (`capability`, `schema`) and seven `##`
sections, matching the minimal, human contract FR-002 requires.

Independent Strict Review Iteration 1 (`review.md`) found two defects in
the revision it evaluated, both fixed in this revision before Iteration
2: `tdd-evidence.yml` carried a `full_suite:` key not permitted by
`forge/tdd-evidence@1`'s schema (`additionalProperties: false`), which
made `tests/contract/test_protocol_contract.py::test_canonical_yaml_instances_satisfy_their_declared_schemas`
fail (R-001, BLOCKER) — removed; and the section parser mistook a
heading-shaped line inside a fenced code block for a new section,
silently truncating the enclosing section (R-002, MAJOR) — fixed by
tracking fence state in `_parse_sections`, with a regression test
(TDD-003). Two non-blocking observations from Iteration 1 (a
non-`re.escape`d path in one `pytest.raises(match=...)` call; duplicate
`##` headings silently overwrite rather than error) were left as
documented, accepted limitations — neither affects any Acceptance
Criterion, and manufacturing a fix for a non-blocking, low-likelihood
edge case was judged disproportionate for a foundation Change (C-039).

## Conclusion

Verification passes for the implemented scope, including the fixes made
in response to independent Strict Review Iteration 1's findings. The
Change is not marked complete until independent Strict Review Iteration
2 passes against this revision.
