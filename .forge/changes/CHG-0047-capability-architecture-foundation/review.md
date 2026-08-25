---
forge:
  artifact: review
  schema: 1
change: CHG-0047
status: complete
---

# Review — CHG-0047 Capability Architecture Foundation

## Verdict

**PASS.** Iteration 1: REQUEST CHANGES, resolved. Iteration 2: REQUEST CHANGES, resolved. Iteration 3: REQUEST CHANGES — Convergence Limit reached (Protocol 2 §12, limit = 2); the user recorded an explicit `convergence_decision: new_full_review`; R-006/R-007 were fixed. Iteration 4 (fresh, unrestricted Initial Review of the whole subject) returned **PASS** against commit `9f85aac` — one non-blocking MINOR finding, R-008. Because fixing R-008 touched `plan.md`, a reviewable file, C-026 required the refrozen revision to be independently re-verified regardless of R-008's severity. Iteration 5 (Resolution Verification scoped to R-008, commit `53aa1f0`) returned **PASS**. Iteration 6 (Documentation Impact addition — `CHANGELOG.md`, ADR-0019 — Initial Review, commit `356f201`) returned **PASS**. No BLOCKER or MAJOR finding across all six Iterations survives in the final revision. Strict Review for CHG-0047 is closed.

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

## Iteration 4 — PASS (Initial Review)

**Reviewer**: Independent Reviewer execution (fresh agent invocation, isolated Git worktree at `/home/isckosta/forge-protocol/.claude/worktrees/agent-a74feac752af6f16c`, no shared context with any prior Execution — Implementation, Resolution, or any of the three prior Reviewer Executions), per C-026.

**Commit reviewed**: `9f85aac996246ac014d81990ea87a917ab61d157`.

**Classification**: `kind: initial_review`, per the Convergence Decision above (`new_full_review`) — a fresh, unrestricted re-audit of the entire subject against the pre-Change baseline (`7495615`), not a scope-bounded Resolution Verification.

### Summary

Every claim in `verification.md`/`tdd-evidence.yml` was independently reproduced. The Reviewer read `loader.py`/`model.py` fresh (no assumption prior fixes were correct), constructed 20+ new adversarial cases against `load_capability` beyond all five TDD cycles' shipped tests — including cross-checking ambiguous fence/heading cases against a real CommonMark parser (`markdown-it-py`) — reverted the two most recent fixes (TDD-004, TDD-005) in an isolated worktree to independently confirm their RED evidence, and audited diff scope and forbidden-vocabulary constraints end to end. No new BLOCKER or MAJOR defect was found.

### R-008 · MINOR — `plan.md` carried unfilled template placeholder text and a duplicated "Implementation Boundary" section

After the `<!-- forge:plan-approval-record -->` marker, `plan.md` contained the literal unfilled template line `1. Describe the first approved work item and files.` (every sibling Change's `plan.md` in this repository replaces this with real prose narrating the approval; CHG-0047 was the only one that hadn't), followed by a second, duplicate `## Implementation Boundary` section identical to the one already present earlier in the file. Neither defect is caught by `forge validate` (the `plan` artifact's prose is not schema-parsed), and neither compromises the actual approval record: `provenance.yml`'s `plan-approval-001` independently and correctly documents the human's explicit approval, with its own `content_digest` over the plan.md content as it stood at that frozen commit — the provenance chain remains internally consistent regardless of this prose gap. Not BLOCKER/MAJOR: no Acceptance Criterion references this text, and no shipped code, test, or the substantive approval record depends on it.

### Investigated and found not to be defects (recorded for completeness)

`manifest.yml`'s `tdd.cycles: 4` vs. `tdd-evidence.yml`'s `cycle_count: 5` (5 real `TDD-xxx` entries) looked like the same class of drift R-001/R-003 punished, but the Reviewer confirmed this field is not treated as strictly synced anywhere in this project's real practice (e.g. `CHG-0046`'s merged `manifest.yml` carries `tdd.cycles: 7` against its own `tdd-evidence.yml`'s `cycle_count: 12`, and `change-v2.schema.json` does not cross-validate the two) — not reported as a finding. Several fence/heading edge cases that looked plausible as new silent-truncation instances (a 4-space-indented fence, a fence properly nested under a list item, an unterminated fence in the final required section, a YAML-boolean-word `capability` id, CRLF line endings) were each independently checked — including against a real CommonMark parser for the ambiguous indentation cases — and confirmed to behave correctly (either loading correctly or failing loudly with a specific `CapabilityDefinitionError`), not silently.

### Checked and found sound (Iteration 4)

- `pytest tests/capabilities/ -q`: 29 passed (independently reproduced, fresh venv).
- Full suite `pytest -q`: 750 passed, 2 warnings (matches `verification.md` exactly; warnings pre-exist, unrelated).
- `pytest tests/contract/test_protocol_contract.py -q`: 34 passed; `tdd-evidence.yml` re-confirmed to parse with every `notes` entry as a plain string.
- `forge validate`: PASS.
- Diff scope: `git diff 7495615..9f85aac --stat` touches exactly 17 files (the 7 code/doc/test files this Specification scopes, plus this Change's own 10 Artifacts); `pyproject.toml`, `protocol/`, the Engineering Contract, and `src/forge_cli/adapters/capabilities.py` confirmed byte-identical to baseline.
- Forbidden class names (`CapabilityRegistry`/`CapabilityExecutor`/`CapabilityPipeline`/`CapabilityGraph`/`CapabilityProvider`) appear only in prose *discussing the prohibition*, never in shipped code; no Claude/Codex/Cursor coupling in `src/forge_cli/capabilities/` (the only hits are the intentional negative assertion in `test_model.py`).
- No speculative empty directories anywhere in the diff.
- `Capability` model: exactly the required fields, frozen, no Harness-specific field, independently confirmed via `dataclasses.fields()`.
- `load_capability`: locate → read → parse → normalize → return exactly as specified; every invalid-input path raises a specific, path-identifying `CapabilityDefinitionError`.
- Determinism reconfirmed.
- Fence-vs-heading disambiguation (the subject of R-002/R-004/R-005/R-006 across three prior Iterations): 20+ new adversarial cases beyond the shipped tests, several cross-checked against a real CommonMark parser, found no surviving silent-truncation case.
- TDD-004/TDD-005 RED evidence independently reproduced by reverting each fix in the Reviewer's own worktree, re-running the targeted tests (`2 failed` and `1 failed` respectively, matching `tdd-evidence.yml` exactly), then restoring — worktree confirmed clean afterward.
- Documentation (`capabilities/README.md`, `capabilities/capability.md`) read fresh in full: covers all required FR-001/FR-002 points, including the explicit `adapters/capabilities.py` disambiguation and the explicit "not a `SKILL.md`" statement; no JSON Schema introduced.
- Proportionality reassessed after 5 TDD cycles and 3 review rounds: the design has not drifted — still a frozen dataclass and a single small loader file, no registry/executor/discovery/cache/package-resource fallback.
- Iteration 2's and Iteration 3's own RED/GREEN claims independently spot-checked and found accurate (review-history honesty check).

### Verdict

**PASS** against the subject reviewed (`9f85aac`). No BLOCKER or MAJOR finding survived independent, adversarial re-verification. R-008 (MINOR) is genuine but non-blocking, affecting only this Change's own `plan.md` prose, not any Acceptance Criterion, shipped code, test, or the substantive human-approval provenance record.

## Resolution (of R-008)

R-008's non-blocking severity means it does not, by itself, prevent Completion (C-027) — but fixing it edits `plan.md`, a reviewable file, not review-control metadata (only `manifest.yml`/`provenance.yml`/`review.md` are exempt from the C-026 freeze invariant). So the fix itself still produces a new revision that differs from Iteration 4's frozen subject, which `forge validate` correctly flags (C-026: "review subject changed after its immutable revision freeze") until that new revision is itself frozen and independently re-verified. The unfilled template placeholder line was replaced by removing it (the marker itself, `<!-- forge:plan-approval-record -->`, remains and is followed directly by the file's actual final content), and the duplicate `## Implementation Boundary` section was removed, leaving the single original one intact — see `provenance.yml`'s `resolution-004` record for the frozen revision this produced, and Iteration 5 below for its independent re-verification.

## Iteration 5 — PASS (Resolution Verification)

**Reviewer**: Independent Reviewer execution (fresh agent invocation, isolated Git worktree at `/home/isckosta/forge-protocol/.claude/worktrees/agent-a641ae74c47b0ecf8`, no shared context with the Resolution Execution that produced this revision or with any of the four prior Reviewer Executions), per C-026.

**Commit reviewed**: `53aa1f00bf50818fec219511c8c938fa98e9708f`.

**Classification**: `kind: resolution_verification`, scoped to R-008 — not a re-audit of the whole subject (Iteration 4 already performed that).

### Resolution Delta inspected

`git diff 9f85aac..53aa1f0` touches exactly four files: `plan.md` (the R-008 fix itself) plus `manifest.yml`/`provenance.yml`/`review.md` (review-control metadata, exempt, legitimately differing). **No Out-of-Scope Mutation.**

### plan.md content check

Confirmed: the unfilled template placeholder line is gone with no occurrence anywhere in the file; exactly one `## Implementation Boundary` section remains, text intact; the `<!-- forge:plan-approval-confirmation -->`/`<!-- forge:plan-approval-record -->` markers and the real approval prose between them (the substantive C-077 human-approval record) are byte-for-byte unchanged — the diff hunk starts only after the closing marker.

### `provenance.yml` `plan-approval-001` sanity check

Untouched by this diff (confirmed by hunk position); still references the original immutable Plan commit `9e6fe0ec1d33154ba9cfec0a035425b015da83b4` with its own `content_digest`, independent of and unaffected by this Resolution.

### R-009 · MINOR — already resolved before this Iteration's report was recorded

At the exact commit reviewed (`53aa1f0`), `review.md`'s "Resolution (of R-008)" section and top Verdict line stated Strict Review "is closed" and that R-008's non-blocking severity meant no further independent Review Iteration was required — conflating finding severity with the separate, controlling question of whether the fix touched a reviewable file under C-026. This was corrected in a later commit (`ef13ec8`, itself review-control metadata — `review.md` is exempt from the C-026 freeze invariant, so this correction did not require its own Resolution Verification) before this Iteration's result was recorded: see the current Verdict line and "Resolution (of R-008)" section above, which now correctly attribute the re-verification requirement to `plan.md` being a reviewable file, not to R-008's severity. No further action needed.

### Checked and found sound (Iteration 5)

- `git diff --stat 9f85aac..53aa1f0`: exactly 4 files, matching declared scope; no code, test, or documentation file outside this Change's own directory touched.
- `forge validate` (isolated venv built inside the Reviewer's own worktree, at `53aa1f0`, not the shared repo's differently-pinned editable install): `Forge project is valid`.
- Full suite `pytest -q` (same isolated venv): 750 passed, 2 warnings — unregressed, consistent with a docs-only Resolution.
- `manifest.yml`'s `tdd.cycles: 4 → 5` (the only substantive change in that file at this commit) correctly matches `tdd-evidence.yml`'s `cycle_count: 5` — an accuracy correction to exempt metadata, not a defect.

### Verdict

**PASS.** No BLOCKER or MAJOR finding. R-009 (MINOR) was already resolved by a subsequent review-control-metadata-only correction before this report was recorded. `plan.md`'s content is correct, diff scope is exactly as declared (no Out-of-Scope Mutation), `plan-approval-001` is untouched and internally consistent, `forge validate` is clean, and the full suite is unregressed. This closes Strict Review for CHG-0047.

## Iteration 6 — PASS (Documentation Impact, Initial Review)

**Reviewer**: Independent Reviewer execution (fresh agent invocation, isolated Git worktree at `/home/isckosta/forge-protocol/.claude/worktrees/agent-a43a864a38974e415`, no shared context with the Implementation that produced this revision or with any of the five prior Reviewer Executions), per C-026.

**Commit reviewed**: `356f201068d9d73953a9a264af7d52511f4ebe09`.

**Classification**: `kind: initial_review`. STANDARD Flow's `documentation` stage runs after `strict_review`; `CHANGELOG.md` and `docs/adr/0019-capability-architecture-foundation.md` are reviewable files, so this new revision (the Documentation Impact addition) requires its own independent review before Completion, matching this repository's `CHG-0039` precedent. No prior Finding is being fixed, so `initial_review`, not `resolution_verification`.

### Resolution Delta inspected

`git diff 53aa1f0..356f201 --stat`: exactly `CHANGELOG.md`, `docs/adr/0019-capability-architecture-foundation.md` (new), plus this Change's own `manifest.yml`/`provenance.yml`/`review.md` (review-control metadata). **No Out-of-Scope Mutation.**

### R-010 · BLOCKER (process gap, found and fixed before this report was recorded) — Commit `356f201` was reviewed before its subject-freeze provenance record was committed

The Reviewer correctly identified that, at the exact moment `356f201` was checked out, `provenance.yml` had no `documentation-001` (or equivalent) record freezing that commit, and `forge validate` failed with `C-026 ... review subject changed after its immutable revision freeze`. Root cause: the `documentation-001` provenance record had been authored in the working tree but was not yet committed when this Iteration's Reviewer was launched — a process sequencing error, not a defect in `CHANGELOG.md`/`docs/adr/0019-...`'s content (the Reviewer found neither BLOCKER nor MAJOR content defects in either file). Fixed immediately: `documentation-001` committed (`63aa0a4`) before this report was recorded, matching this Change's own established pattern (every prior fix commit is followed by a review-control-metadata commit before the next Iteration).

### R-011 · MINOR (documentation accuracy, accepted, not fixed) — ADR-0019 misattributes two finding IDs in its own history summary

ADR-0019's Consequences paragraph reads "no fence-indentation tracking (R-002), no delimiter-type tracking (R-004), no delimiter-length tracking (R-006)." Checked against this file's own record: R-002 (Iteration 1) is the *original*, fence-unaware bug, not specifically an indentation finding; R-004 (Iteration 2) is the actual indentation finding; R-005 (Iteration 2, MINOR/informational) is the actual delimiter-type finding, omitted from the ADR's list; R-006 (Iteration 3) is correctly the delimiter-length finding. The overall narrative (successively narrower fence-parsing gaps across three Iterations, closing with a Convergence Limit episode) is accurate; only this one sentence's ID-to-gap mapping is off by one for two of three IDs, and omits R-005.

**Not fixed.** Editing `docs/adr/0019-...md` is itself a reviewable-file mutation that would, under the same C-026 mechanism R-010 just demonstrated, require yet another frozen subject and independent Iteration to close — disproportionate for a documentation-accuracy correction with no AC, code, test, or safety-claim impact (unlike R-001/R-003, this does not misstate what was verified or make a false pass-count claim). Recorded here as a known, accepted, non-blocking limitation, consistent with how Observations 1–2 and R-007 were handled (C-039 proportionality).

### Checked and found sound (Iteration 6)

- `CHANGELOG.md`'s new entry and ADR-0019 spot-checked against the actual shipped files (`capabilities/README.md`'s architectural-boundaries list, `capabilities/capability.md`'s seven required sections and "no JSON Schema" declaration, `loader.py`'s own docstring, `model.py`'s `@dataclass(frozen=True)`) — accurate.
- Neither document overclaims scope: no concrete Capability, registry, or executor is claimed to exist; `grep` for the five forbidden class names in `src/forge_cli/capabilities/` returns no matches.
- F-010 and F-008 quoted correctly against `.claude/skills/forge/references/engineering-contract.md`.
- `pyproject.toml` confirmed byte-identical to the pre-Change baseline (`git diff 7495615..356f201 -- pyproject.toml`: no output).
- The ADR's Convergence/Iteration-4/Iteration-5 narrative independently checked line-by-line against this file's own "Convergence", "Convergence Decision", "Iteration 4", "Resolution (of R-008)", and "Iteration 5" sections — accurate.
- ADR numbering: `0019` used exactly once.
- Full suite (fresh venv): 750 passed, 2 warnings — unregressed (docs-only addition). `tests/capabilities/`: 29 passed. `tests/contract/test_protocol_contract.py`: 34 passed.

### Verdict

**PASS.** No BLOCKER or MAJOR content defect in `CHANGELOG.md` or `docs/adr/0019-...`. R-010 was a process-sequencing gap, fixed before this report was recorded (see `documentation-001` in `provenance.yml`, commit `63aa0a4`). R-011 (MINOR) is a genuine but non-blocking documentation-accuracy note, recorded and accepted rather than fixed, per C-039 proportionality.
