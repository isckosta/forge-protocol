---
forge:
  artifact: review
  schema: 1
change: CHG-0047
status: active
---

# Review — CHG-0047 Capability Architecture Foundation

## Verdict

**Pending Iteration 4 (Initial Review).** Iteration 1: REQUEST CHANGES, resolved. Iteration 2: REQUEST CHANGES, resolved. Iteration 3: REQUEST CHANGES — Convergence Limit reached (Protocol 2 §12, limit = 2). The user recorded an explicit `convergence_decision: new_full_review`; R-006/R-007 were fixed; a fresh, unrestricted Initial Review of the whole subject is now pending against the current revision.

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

## Iteration 3 — REQUEST CHANGES (Resolution Verification)

**Reviewer**: Independent Reviewer execution (fresh agent invocation, isolated Git worktree at `/home/isckosta/forge-protocol/.claude/worktrees/agent-a853c531d6133a76b`, no shared context with Resolution 2's Execution or with either prior Reviewer Execution), per C-026. Classified as a **Resolution Verification** under C-047: scope bounded to R-003, R-004, R-005, defects within the Resolution 2 Delta, and Out-of-Scope Mutation.

**Commit reviewed**: `ea433b64bda9e5a92977cdb05dd5efd7d10810a6` (frozen Resolution 2 revision).

**Resolution 2 Delta inspected**: `git diff fbb1a8bd8768774a3b6df8bb583eb42d4219ec54..ea433b64bda9e5a92977cdb05dd5efd7d10810a6 -- .forge/changes/CHG-0047-capability-architecture-foundation/{tdd-evidence.yml,verification.md,review.md} src/forge_cli/capabilities/loader.py tests/capabilities/test_loader.py`.

### R-006 · MAJOR — R-005's remaining "mismatched delimiter length" limitation is mischaracterized: it can fail completely silently, not loudly as claimed

`_parse_sections`'s fence tracking closes a fence on any line matching `_FENCE_PATTERN` whose first character equals the opening delimiter — it checks delimiter *type* only, never *length*. Per CommonMark, a closing fence must be at least as long as the opening fence. A same-character but *shorter* line is accepted as a valid closer, prematurely ending the fence; a heading-shaped line that follows before the "real" (length-correct) close is then treated as a genuine new section — silently, with no exception at all. Reproduced directly against `load_capability`: a body opening with 4 backticks, containing a 3-backtick line (should not close per CommonMark, does close in this implementation), followed by `## Real Heading After Bad Close` and more text — `load_capability` returns successfully with the heading-shaped line and everything after it silently dropped from the enclosing section, no error of any kind.

This directly contradicts the explicit "fails loudly, not silently" claim written into `tdd-evidence.yml`, `verification.md`, and this file's own Iteration 2/Resolution-of-Iteration-2 text as the stated justification for not fixing this sub-case further. `capabilities/capability.md`'s own "Example skeleton" section already nests one fence inside prose about fencing, making a differently-sized outer/inner fence pairing a plausible authoring pattern in this repository, not a contrived one. Not classified as BLOCKER: it does not break a machine-checked contract test, and constructing it requires a somewhat deliberate fence-length setup.

### R-007 · MINOR (informational) — Indentation tolerance also accepts tabs beyond the documented "3 leading spaces," but never on the corruption side

`_FENCE_PATTERN` counts each leading tab as 1 character toward the 3-character budget rather than applying CommonMark's tab-stop-of-4 equivalence, so a fence indented with 1–3 leading tabs is still recognized — more permissive than `TDD-004`'s `behavior` field, which only mentions spaces. Because the deviation is in the over-recognize-as-fence direction, it cannot cause silent truncation (it protects more content, not less); it only means a line a strict CommonMark renderer would treat as a real heading gets swallowed as literal fence content instead. Non-blocking; flagged for documentation accuracy only.

### Checked and found sound (Iteration 3)

- Out-of-Scope Mutation: `git diff --stat fbb1a8b..ea433b6` (unfiltered) touches exactly 7 files — the 5 declared plus `manifest.yml`/`provenance.yml` (review-control metadata, already checked sound by Iteration 2). No new files, no touched source outside `loader.py`. **No Out-of-Scope Mutation.**
- R-003 (BLOCKER) genuinely fixed: `pytest tests/contract/test_protocol_contract.py -q` → 34 passed; independently parsed `tdd-evidence.yml` and confirmed every `notes` entry is a plain string.
- Full suite independently counted (fresh venv): `pytest -q` → 749 passed, 2 warnings — matches the Resolution's claim exactly.
- `tests/capabilities/` in isolation: 28 passed, matching `tdd-evidence.yml`/`verification.md`.
- R-004 (MAJOR) genuinely fixed, adversarially: tab-indented fences, the 3-space CommonMark boundary (recognized) vs. 4-space (correctly *not* recognized, matching true CommonMark indented-code-block semantics — not a regression), `~~~` fences, and two consecutive fences of different types in one section all round-trip correctly.
- R-005's delimiter-type half genuinely fixed: independently reproduced outside the shipped test harness.
- R-005's unterminated-fence sub-case: confirmed it does still fail loudly as disclosed (`CapabilityDefinitionError`, not silent) — that specific part of the disclosure is accurate; only the mismatched-*length* sub-case (R-006) is mischaracterized.
- No repeat of R-003's unescaped-`word:`-clause pattern in any newly added `tdd-evidence.yml` scalar.

### Verdict

**REQUEST CHANGES.** R-006 (MAJOR) is a new, independently-reproduced silent-data-corruption path, plus a factually incorrect "fails loudly" safety claim repeated across three of this Change's own records as the stated reason for not fixing it — matching the BLOCKER/MAJOR bucket's defining examples, not MINOR's. R-004 and the delimiter-type half of R-005 are genuinely and adversarially confirmed fixed; R-003 is genuinely fixed and independently re-verified; no Out-of-Scope Mutation occurred. R-007 is non-blocking, reported for completeness.

This is the second consecutive `failed` Resolution Verification with material findings for this Change, reaching Protocol 2's Convergence Limit (§12–13, C-049). `review.convergence.state: review_convergence_failed` applies; a further scoped `resolution_verification` Iteration is not valid. The next Iteration, when it occurs, must be `kind: initial_review` (full, unrestricted) and must carry its own `convergence_decision` (`option` and `reason`) — which Forge MUST NOT select automatically; authority returns to the human engineer.

## Convergence

Two consecutive `resolution_verification` Iterations (`review-002`, `review-003`) returned `status: failed` with `new_material_findings > 0` — the Convergence Limit (2) is reached at this point in the Iteration history. Per Protocol 2 §13, `review.convergence.state: review_convergence_failed` is recorded in `manifest.yml`, and `review.status: passed` MUST NOT be asserted while this state holds. Continuing requires an explicit human-engineer decision (`convergence_decision`: `new_full_review`, `return_to_earlier_phase`, `accept_residual_risk`, or `abort_or_supersede`) recorded on the Iteration immediately following this one — not selected autonomously by any agent.

### Convergence Decision

The situation (R-006's finding, the Convergence Limit being reached, and the four available options with their consequences) was presented to the user in the active chat session on 2026-08-25. The user selected **`new_full_review`**: fix R-006 (and, if cheap, R-007), then have a fresh, unrestricted Initial Review — not another scoped Resolution Verification — re-evaluate the whole subject from scratch. Rationale recorded at the time: R-006's root cause is narrow and well understood (compare closing-fence run length against the opening run length, not just delimiter type), the architecture and documentation have held up across all three prior Iterations with no structural rework needed, and `return_to_earlier_phase`/`abort_or_supersede` were judged disproportionate to a localized parser fix, while `accept_residual_risk` would leave a demonstrated silent-truncation defect unfixed in the shipped foundation.

## Resolution (of Iteration 3)

R-006 fixed: `_parse_sections` now also tracks the opening fence's delimiter run length and only closes the fence on a same-type line whose run length is `>=` that length, matching CommonMark's actual fence-closing rule (`TDD-005`, RED→GREEN). R-007 addressed by correcting `TDD-004`'s behavior description (it already tolerated tabs, not just spaces, in the safe direction; the description was updated to say so honestly, no code change). Full suite and `forge validate` re-verified after the fix (see `verification.md`). See `provenance.yml`'s `resolution-003` record for the frozen revision this produced.

## Iteration 4 — Initial Review (pending)

Per the Convergence Decision above, this Iteration is classified `kind: initial_review` — a fresh, unrestricted re-evaluation of the whole subject, not a scoped Resolution Verification. Recorded below once the independent Reviewer returns its verdict.
