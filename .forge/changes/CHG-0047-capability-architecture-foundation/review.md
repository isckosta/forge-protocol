---
forge:
  artifact: review
  schema: 1
change: CHG-0047
status: active
---

# Review — CHG-0047 Capability Architecture Foundation

## Verdict

**Pending Iteration 2** (Iteration 1: REQUEST CHANGES — both findings resolved; awaiting independent re-review of the resolved revision)

## Iteration 1 — REQUEST CHANGES

**Reviewer**: Independent Reviewer execution (fresh agent invocation, isolated Git worktree at `/home/isckosta/forge-protocol/.claude/worktrees/agent-ac1fb130508c0e7cc`, no shared context with the Implementation that produced this revision), per C-026.

**Commit reviewed**: `c5418daeb5a3dd0aa9bf21d166cb8d57bfc4fa68`.

**Baseline for diff**: `7495615` (merge-base with `main`).

### R-001 · BLOCKER — `tdd-evidence.yml` violates its own schema, and `verification.md`'s full-suite claim was false

`tdd-evidence.yml` carried a top-level `full_suite:` key not permitted by `protocol/schemas/tdd-evidence.schema.json` (`"additionalProperties": false`, and `full_suite` is not among the declared properties). This made the repository's own contract test fail:

```
$ .venv/bin/python -m pytest -q
...
FAILED tests/contract/test_protocol_contract.py::test_canonical_yaml_instances_satisfy_their_declared_schemas
1 failed, 745 passed, 2 warnings in 135.49s (0:02:15)
```

`verification.md` claimed "746 passed, 2 warnings" — false as written; the independently reproduced result was 1 failed, 745 passed.

**Resolution**: `full_suite:` removed from `tdd-evidence.yml` (that evidence already lived correctly in `verification.md`, which is where full-suite results belong). `verification.md`'s Test Evidence section corrected to the actual, re-verified count (**747 passed** — 746 plus the new TDD-003 regression test below).

### R-002 · MAJOR — Section parser silently truncated a section at a heading-shaped line inside a fenced code block

`_SECTION_HEADING_PATTERN` matched any line starting with `## ` regardless of fenced-code-block context. A section body containing an illustrative code fence with a nested `##`-prefixed line (exactly the pattern `capabilities/capability.md`'s own "Example skeleton" section uses) was silently truncated at that fake heading — no error, wrong data. None of the existing tests covered this case.

**Resolution**: `_parse_sections` in `src/forge_cli/capabilities/loader.py` now scans the body line-by-line, tracking fenced-code-block state (toggling on lines starting with ```` ``` ```` or `~~~`), and only recognizes a `## ` line as a section heading when not inside an open fence. A regression test (`TDD-003`, `tests/capabilities/test_loader.py::test_heading_shaped_line_inside_a_fenced_code_block_is_not_a_new_section`) was added following RED→GREEN: it reproduced the truncation before the fix and passes after.

### OBSERVATION 1 — `match=str(path)` in one test is not `re.escape`d

`test_missing_file_raises_capability_definition_error` passes a raw path string as a `pytest.raises(match=...)` regex. Not a defect today (no regex metacharacters in this environment's `tmp_path` values), but fragile on a path containing regex-special characters. Not fixed — non-blocking, low real-world likelihood, and fixing it does not change any Acceptance Criterion outcome (C-039 proportionality).

### OBSERVATION 2 — Duplicate `##` section headings silently overwrite rather than error

Two `## Behavior` headings in one file would silently keep only the first; not tested, not required by any AC. Not fixed for the same proportionality reason as Observation 1 — left as a known, documented limitation for a future Change to address if it becomes a real problem.

### Checked and found sound (Iteration 1)

- Diff scope: `git diff 7495615..c5418da --stat -- protocol/ pyproject.toml .claude/skills/forge/references/engineering-contract.md src/forge_cli/adapters/capabilities.py` — no output; all confirmed unchanged.
- No `CapabilityRegistry`/`CapabilityExecutor`/`CapabilityPipeline`/`CapabilityGraph`/`CapabilityProvider` anywhere in the new code.
- No Claude/Codex/Cursor coupling in `src/forge_cli/capabilities/`.
- No new CLI command.
- `Capability` dataclass: exact minimal field set, frozen, no Harness-specific field — independently verified.
- `load_capability`: locate → read → parse → normalize → return, with specific `CapabilityDefinitionError` for every invalid-input case tested, including the deliberate `isinstance(schema, bool)` exclusion.
- Determinism test passes; no global/mutable state.
- RED evidence for TDD-001/TDD-002 independently reproduced by removing `model.py`/`loader.py` in the reviewer's own worktree and re-running the tests.
- GREEN minimality (C-013): no registry, executor, discovery, caching, or package-resource fallback exists.
- Documentation (TD-007): `capabilities/README.md` covers all six required FR-001 points, including the explicit `adapters/capabilities.py` distinction; `capability.md` lists and describes all seven required sections, shows the minimal frontmatter, and explicitly states a `CAPABILITY.md` is not a `SKILL.md`; no JSON Schema introduced.
- `forge validate`: PASS.
- Proportionality: independently agreed this is the smallest design preserving the required boundaries — no premature abstraction, no speculative empty directory for Codex/Cursor/plugin registries.
- `tests/capabilities/` in isolation: 25 passed (matching `verification.md`'s claim for that scope at the reviewed commit).

## Resolution

Both findings were fixed in the Implementation's own session, in direct response to Iteration 1 (not resolved inside the Reviewer's own execution/context, per C-026's Resolver-independence requirement — the Resolver here is the original Implementation Execution, which is not the Reviewer). See `verification.md`'s Compatibility/Limitations section and `tdd-evidence.yml`'s `TDD-003` entry for the resolution detail. The resolved revision is frozen and referenced by `provenance.yml`'s `implementation-subject-002` record; Iteration 2 (below, once recorded) independently re-reviews that exact revision.
