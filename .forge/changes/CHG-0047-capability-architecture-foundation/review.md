---
forge:
  artifact: review
  schema: 1
change: CHG-0047
status: active
---

# Review — CHG-0047 Capability Architecture Foundation

## Verdict

**Pending Iteration 3** (Iteration 1: REQUEST CHANGES, resolved. Iteration 2: REQUEST CHANGES, resolved. Awaiting independent re-review of the current resolved revision.)

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

## Resolution (of Iteration 1)

Both findings were fixed by a Resolution Execution distinct from Iteration 1's Reviewer Execution, in direct response to Iteration 1 (per C-026's Resolver-independence requirement — a Resolver MUST NOT resolve blocking findings inside the Reviewer's own Execution Context). See `verification.md`'s Compatibility/Limitations section and `tdd-evidence.yml`'s `TDD-003` entry for the resolution detail. The resolved revision (`fbb1a8bd8768774a3b6df8bb583eb42d4219ec54`) is frozen and referenced by `provenance.yml`'s `resolution-001` record.

## Iteration 2 — REQUEST CHANGES (Resolution Verification)

**Reviewer**: Independent Reviewer execution (fresh agent invocation, isolated Git worktree at `/home/isckosta/forge-protocol/.claude/worktrees/agent-a23a2996c846c3c01`, no shared context with the Resolution Execution or with Iteration 1's Reviewer Execution), per C-026. Classified as a **Resolution Verification** under C-047: scope bounded to R-001, R-002, defects within the Resolution Delta, and Out-of-Scope Mutation.

**Commit reviewed**: `fbb1a8bd8768774a3b6df8bb583eb42d4219ec54` (frozen Resolution revision).

**Resolution Delta inspected**: `git diff c5418daeb5a3dd0aa9bf21d166cb8d57bfc4fa68..fbb1a8bd8768774a3b6df8bb583eb42d4219ec54`.

### R-003 · BLOCKER — The R-001 fix reintroduced a schema violation in the same file; the "747 passed" claim was false

`tdd-evidence.yml`'s new `TDD-003.notes` entries were unquoted YAML strings beginning with a colon-bearing clause (`- Fix: ...`, `- Full suite re-verified after this fix: ...`), which YAML parses as single-key mappings, not strings. `forge/tdd-evidence@1`'s schema requires `notes` items to be `type: string`, so this failed the same contract test R-001 was about:

```
$ .venv/bin/python -m pytest tests/contract/test_protocol_contract.py -q
FAILED ...test_canonical_yaml_instances_satisfy_their_declared_schemas
E   .../tdd-evidence.yml:cycles.2.notes.0: {'Fix': '...'} is not of type 'string'
E   .../tdd-evidence.yml:cycles.2.notes.1: {'Full suite re-verified after this fix': '...'} is not of type 'string'
```

Independently reproduced full-suite run: `1 failed, 746 passed, 2 warnings` — not the 747 passed claimed. `forge validate` does not catch this (it does not validate `tdd-evidence.yml` against its schema — only the pytest contract test does), so a passing `forge validate` was not evidence against this finding.

### R-004 · MAJOR — The R-002 fence-tracking fix is incomplete: an indented fence still reproduces the original silent-truncation bug

`_FENCE_PATTERN = re.compile(r"^(```|~~~)")` required the delimiter at column 0. CommonMark allows up to 3 leading spaces of indentation for a fence. An indented fence-open line was never recognized as a fence, so a heading-shaped line inside it was silently treated as a real section heading — R-002's exact original symptom, triggered by a different, equally valid input than `TDD-003` covered. Independently reproduced with an adversarial case beyond the shipped regression test.

### R-005 · MINOR (informational) — Mismatched fence delimiter type and unterminated fences produce a misleading diagnostic

A fence opened with `` ``` `` and containing a `~~~` line not intended to close it (CommonMark: a backtick fence only closes on backticks, a tilde fence only on tildes) desynchronized the type-agnostic toggle, eventually surfacing as a confusing "missing required section" error rather than a fence-specific diagnostic. Same symptom for an unterminated fence. Lower severity than R-004 because it fails loudly rather than silently.

Two adversarial cases were also confirmed handled correctly at this revision (offered for balance): two separate, properly closed, un-indented fenced blocks in one section; a single un-indented fence around a heading-shaped line with text before/after (the shipped `TDD-003` scenario).

### Checked and found sound (Iteration 2)

- `git diff --stat` between the two commits: exactly 6 files — the 5 the Resolution declared plus `provenance.yml` (which only adds the `implementation-subject-001` record — pure review-control metadata, explicitly permitted to differ post-freeze). **No Out-of-Scope Mutation.**
- `resolution-001`'s declared `scope:` in `provenance.yml` matches the same 5 files.
- R-001's original trigger (the `full_suite:` key) genuinely removed.
- `TDD-003`'s RED and GREEN claims independently reproduced by swapping in the pre-fix `loader.py` and re-running the targeted test, then restoring it (workspace confirmed clean afterward).
- The fence fix is not merely test-shaped: two independently-constructed adversarial cases beyond the shipped test also parse correctly.
- `forge validate`: PASS, reproduced at this exact commit.

## Resolution (of Iteration 2)

R-003 fixed by quoting the two offending `tdd-evidence.yml` notes strings. R-004 and R-005 (the delimiter-type-matching half) fixed by making `_FENCE_PATTERN` tolerate up to 3 leading spaces/tabs and tracking which delimiter character opened the current fence (only a matching delimiter closes it) — matching CommonMark fence semantics for these two cases. A regression test (`TDD-004`) covers both, following RED→GREEN. R-005's remaining, lower-severity half (unterminated fence / mismatched delimiter *length* producing a generic rather than fence-specific error) is left as a documented, accepted limitation — see `verification.md`'s Compatibility/Limitations section for the proportionality rationale (C-039). See `provenance.yml`'s `resolution-002` record for the frozen revision this produced.
