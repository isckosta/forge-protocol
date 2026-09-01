---
forge:
  artifact: review
  schema: 1
change: CHG-0052
status: active
---

# CHG-0052 · Review

## Verdict

**PENDING (reopened).** Iteration 1: REQUEST CHANGES — R-001 (BLOCKER), resolved. Iteration 2 (Resolution Verification): REQUEST CHANGES — R-002 (BLOCKER), resolved. Iteration 3 (Resolution Verification): **PASS** against `deee80048ec3e71072229c1d83e1acdfb45d88f4`, no new finding — Strict Review closed and the Change reached `state: complete`. After Completion, an external, independent reviewer (Codex, GitHub PR #47) found R-003 (see below): `capabilities/README.md`'s status paragraph became factually false as a direct consequence of this Change's own delivery. Per `specification-drift.md`, Review is reopened for this narrowly-scoped delta; Iteration 4 (Resolution Verification) is pending independent verification of the fix.

## Review Summary

| | |
|---|---|
| **Iterations** | 4 |
| **Current Subject** | pending Iteration 4 freeze |
| **Open Blockers** | 0 (R-003 resolved, pending independent verification) |
| **Open Majors** | 0 |
| **Open Minors** | 0 |
| **Final Iteration** | 4 |
| **Result** | Pending Resolution Verification |

## Current Subject

| | |
|---|---|
| **Subject SHA** | pending Iteration 4 freeze |
| **Frozen** | No — Resolution applied, not yet frozen for Iteration 4 |
| **Iteration** | 4 |

## Reviewer Independence

`provenance.yml`'s `reviewer-001` record: fresh agent Execution (`a56241cebb2e58ebd`), isolated Git worktree `/home/isckosta/forge-protocol/.claude/worktrees/agent-a56241cebb2e58ebd`, no shared context with the Implementation Execution that produced the subject commit, per C-026. `reviewer-002` record: fresh agent Execution (`ad504272a98650142`), isolated Git worktree `/home/isckosta/forge-protocol/.claude/worktrees/agent-ad504272a98650142`, no shared context with Iteration 1's Reviewer Execution or with the Resolution Execution under review, per C-026. `reviewer-003` record: fresh agent Execution (`a5149613f7d9027e4`), isolated Git worktree `/home/isckosta/forge-protocol/.claude/worktrees/agent-a5149613f7d9027e4`, no shared context with any prior Implementation, Resolution, or Reviewer execution, per C-026. `reviewer-004` (pending): a fourth fresh agent Execution, distinct from all prior Implementation/Resolution/Reviewer executions, required per C-026.

## Open Findings

| Finding | Severity | Status | Iteration |
|---|---|---|---|
| R-003 | BLOCKER | Resolved, pending independent verification | 4 |

## R-003 · BLOCKER — `capabilities/README.md`'s status paragraph became factually false once `investigate` was delivered

**Source**: external, independent reviewer (Codex, GitHub PR #47, inline comment on `CHANGELOG.md:16` anchored to `capabilities/README.md:3-5`, severity P2) — found after this Change's own internal Strict Review had already passed (Iteration 3) and `manifest.yml` had reached `state: complete`.

**Finding**: `capabilities/README.md:3-6` states: "No concrete Capability exists yet — this document defines the abstraction so that the first real Capability (`investigate`, in a later Change) has a place to live without requiring the foundation to be redesigned." This Change's entire purpose is to deliver that first concrete Capability — once `capabilities/investigate/CAPABILITY.md` exists, that sentence is a false statement about the present state of the repository, not a design choice under discussion. Independently re-read against the actual file and confirmed literally true at the Iteration 3 subject (`deee8004`).

**Root cause**: `specification.md`'s FR-006/`CON-001` (this Change's own scope boundary, self-derived from the original request's Architecture boundary list) over-read "do not redesign the foundation" as "do not touch any byte of the foundation's documentation," which the original request never actually required and which blocked a legitimate accuracy correction. See `specification-drift.md` for the full analysis.

**Required Resolution**: correct `capabilities/README.md`'s status paragraph to state the present reality (that `investigate` now exists, introduced by this Change) using the minimum text change needed, without altering any other part of `capabilities/README.md`'s architectural contract or touching `capabilities/capability.md` at all; revise `specification.md`'s FR-006/`CON-001`/Out of Scope/Compatibility Statement (superseded, not deleted) to reflect the corrected boundary.

## Resolution (of R-003)

`specification-drift.md` added, documenting Root Cause/Evidence/Final decision. `specification.md`'s FR-006, `CON-001`, Out of Scope, and Compatibility Statement revised in place (marked "revised per specification-drift.md") to narrow the prohibition to the architectural contract, explicitly permitting this one accuracy correction. `capabilities/README.md`'s introductory status paragraph rewritten to state that `investigate` now exists (introduced by this Change) — no other line of the file changed. Full suite (882 passed) and `forge validate` re-verified. Pending: freeze of this Resolution and independent Resolution Verification (Iteration 4).

## Iteration 1 — REQUEST CHANGES

**Reviewer**: Independent Reviewer execution (fresh agent invocation, isolated Git worktree at `/home/isckosta/forge-protocol/.claude/worktrees/agent-a56241cebb2e58ebd`, no shared context with the Implementation), per C-026.

**Commit reviewed**: `2ff4c5402390aad8a114fa5c44d2c2477b4b4760`.

**Baseline for diff**: `main` (merge-base `94609f20a2cc231cf927fa5b6cc230f3af91515d`).

### R-001 · BLOCKER — `tdd-evidence.yml`'s `notes` entry violates its own schema, and `verification.md`'s "882 passed" full-suite claim was false

`tdd-evidence.yml`'s `cycles[0].notes[1]` was an unquoted plain scalar beginning `One intermediate iteration: the first CAPABILITY.md draft did not name "lifecycle"...`. In block-sequence YAML, an unquoted `key: value`-shaped scalar (colon immediately followed by a space) inside a list item parses as a one-entry mapping, not a string:

```
$ python -c "import yaml; print(yaml.safe_load(open('.forge/changes/CHG-0052-investigate-capability/tdd-evidence.yml'))['cycles'][0]['notes'])"
[..., {'One intermediate iteration': 'the first CAPABILITY.md draft ...'}]
```

`protocol/schemas/tdd-evidence.schema.json` requires `notes[]` items to be `type: string`, so the repository's own contract test failed against the committed subject:

```
$ python -m pytest -q
...
FAILED tests/contract/test_protocol_contract.py::test_canonical_yaml_instances_satisfy_their_declared_schemas
1 failed, 881 passed, 2 warnings in 97.63s
```

`verification.md` claimed `882 passed` — false as written against the frozen subject; the independently reproduced result was 1 failed, 881 passed. `forge validate` alone did not catch this (it does not schema-check canonical YAML — only `pytest tests/contract/` does), consistent with this repository's own prior lesson (`CHG-0047`/R-001, the same defect shape in a different Change).

**Required Resolution**: `tdd-evidence.yml`'s `notes[]` entries must all parse as YAML strings satisfying `protocol/schemas/tdd-evidence.schema.json`, and `verification.md`'s reported full-suite result must match an actually-reproducible `pytest -q` run from the committed tree.

### Checked and found sound (Iteration 1)

- RED independently reproduced: `capabilities/investigate/CAPABILITY.md` temporarily moved aside, `pytest tests/capabilities/test_investigate_capability.py -q` → 20 errors, `CapabilityDefinitionError` from `loader.py:40`; file restored, `git status --porcelain`/`git diff` confirmed clean afterward.
- Foundation files untouched: `git diff main...HEAD -- src/forge_cli/capabilities/loader.py src/forge_cli/capabilities/model.py capabilities/README.md capabilities/capability.md` → empty.
- Architectural boundary search across the full Change diff (`claude|codex|cursor|capabilityregistry|capabilityexecutor|/investigate|skill\.md`, case-insensitive): occurrences only in execution-identity metadata (`provenance.yml`), prose describing the negative assertions themselves, and the test's own `_FORBIDDEN_TERMS` fixture — none inside `capabilities/investigate/CAPABILITY.md` or production code.
- FR-001 through FR-006 and NFR-001 each independently checked against the actual `CAPABILITY.md` content and the actual test assertions — all hold as specified.
- TD-007 (Manual Acceptance) performed independently: `## Behavior` reads as a genuine sequential, disciplined 8-step process (not keyword coverage); `## Applicability` completely covers the required categories plus the already-established-root-cause exclusion; `## Outputs` recommends next action without presuming implementation and without inventing a new mandatory artifact type; Boundaries read as genuinely clear to a reasonable reader; the inconclusive `ROOT CAUSE NOT ESTABLISHED` outcome is genuinely legitimized, not subtly discouraged. TD-007 verdict: **satisfies**.
- `CHANGELOG.md`'s new entry accurately reflects delivered scope.
- `tests/capabilities/test_investigate_capability.py -q` → 20 passed (matches `tdd-evidence.yml`'s GREEN claim); `tests/capabilities/ tests/unit/test_adapter_capabilities.py -q` → 53 passed (matches `verification.md`).

## Resolution (of Iteration 1)

R-001 fixed by quoting the offending `notes[]` entry as a proper double-quoted YAML string in `tdd-evidence.yml` (the entry's internal double quotes escaped). Independently re-verified from the working tree after the fix: `python -c "import yaml; ..."` confirms both `notes` entries now parse as `str`; `pytest tests/contract/ -q` → 71 passed; full suite `pytest -q` → **882 passed**, 2 pre-existing unrelated warnings (genuinely reproduced this time); `forge validate` → Forge project is valid. The resolved revision was frozen at `ae730c297ea0b0cb31f1e1eec37df9cfe0477e94`.

## Iteration 2 — REQUEST CHANGES (Resolution Verification)

**Reviewer**: Independent Reviewer execution (fresh agent invocation, isolated Git worktree at `/home/isckosta/forge-protocol/.claude/worktrees/agent-ad504272a98650142`, no shared context with the Resolution Execution or with Iteration 1's Reviewer Execution), per C-026. Classified as a **Resolution Verification** under C-047: scope bounded to R-001, defects within the Resolution Delta, and Out-of-Scope Mutation.

**Commit reviewed**: `ae730c297ea0b0cb31f1e1eec37df9cfe0477e94` (frozen Resolution revision).

**Resolution Delta inspected**: `git diff 2ff4c5402390aad8a114fa5c44d2c2477b4b4760..ae730c297ea0b0cb31f1e1eec37df9cfe0477e94`.

### R-001: confirmed fixed

Resolution Delta scoped exactly to `.forge/changes/CHG-0052-investigate-capability/{provenance.yml,review.md,tdd-evidence.yml}`. `tdd-evidence.yml`'s fix independently reparsed as valid YAML strings; `pytest tests/contract/ -q` → 71 passed; full suite `pytest -q` → **882 passed, 2 warnings** (matches); `pytest tests/capabilities/ tests/unit/test_adapter_capabilities.py -q` → 53 passed; `forge validate` → PASS. No resolution regression.

### R-002 · BLOCKER — `review.md` cites `provenance.yml` records (`reviewer-001`, `resolution-001`) that did not exist in the reviewed commit, and `manifest.yml` was never updated to record the Iteration

At commit `ae730c29`, the committed `provenance.yml` contained only `plan-approval-001` and `implementation-subject-001` — no `reviewer-001` (role: review) or `resolution-001` (role: resolution) record existed, even though `review.md`'s own Reviewer Independence and Resolution sections asserted them by id. Separately, `manifest.yml`'s `review:` block still read `status: pending, iteration: 0, iterations: []`, contradicting `review.md`'s own Iterations/Final Iteration table. Per `src/forge_cli/merge_readiness/evaluator.py` (MR-018), a passed Review must resolve to admissible `role: review`/`role: resolution` provenance bound to the reviewed/resolved commit via `manifest.yml`'s `review.iterations[]` — this repository's own completed precedent (`CHG-0050`) demonstrates the required shape.

**Root cause**: the `reviewer-001`/`resolution-001` records had been added to the local working tree's `provenance.yml` (by the Resolution Execution, immediately after freezing `ae730c29`) but never committed — an execution-sequencing slip (freeze, then keep editing the just-frozen file without a follow-up commit), not a defect in the records' own content or in the review-control-metadata exemption itself.

**Required Resolution**: `provenance.yml` must contain real, committed `role: review` and `role: resolution` records bound to the correct commits, and `manifest.yml`'s `review.iterations[]` must reference them by id, matching the `CHG-0050` pattern, before Completion.

## Resolution (of Iteration 2)

R-002 fixed by committing the already-drafted `reviewer-001`/`resolution-001` `provenance.yml` records (unchanged content — they were correct, only uncommitted) and by adding `manifest.yml`'s `review.iterations[]` entries (`review-001`, `review-002`) referencing them by id, matching the `CHG-0050` precedent shape. The resolved revision is frozen and referenced by `provenance.yml`'s `resolution-002` record (commit `deee80048ec3e71072229c1d83e1acdfb45d88f4`, followed by a metadata-only provenance-recording commit `d517e1d0611fbef274918e38b6f1e740b8c2650e`).

## Iteration 3 — PASS (Resolution Verification)

**Reviewer**: Independent Reviewer execution (fresh agent invocation, isolated Git worktree at `/home/isckosta/forge-protocol/.claude/worktrees/agent-a5149613f7d9027e4`, no shared context with any prior Implementation, Resolution, or Reviewer execution), per C-026. Classified as a **Resolution Verification** under C-047: scope bounded to R-002, defects within the Resolution Delta, and Out-of-Scope Mutation.

**Commit reviewed**: `deee80048ec3e71072229c1d83e1acdfb45d88f4` (frozen Resolution revision; reviewed via its follow-up provenance-recording commit `d517e1d0611fbef274918e38b6f1e740b8c2650e`, an identical content diff plus the `resolution-002` provenance record itself — review-control metadata only, per the same pattern as `CHG-0051`'s Iteration 1).

**Independently verified**: Reviewable-content stability — `git diff 2ff4c54..d517e1d -- capabilities/ src/ tests/` empty; `capabilities/investigate/CAPABILITY.md` and `tests/capabilities/test_investigate_capability.py` byte-identical to the Iteration 1 subject. `provenance.yml`'s four records (`reviewer-001`, `resolution-001`, `reviewer-002`, `resolution-002`) all real, committed, and bound to correct/ancestor commit SHAs (`git cat-file -e` + `git merge-base --is-ancestor`). `manifest.yml`'s `review.iterations[]` entries resolve to real records with `status`/`kind`/`finding_classes` matching this document's own narration. `forge validate` PASS — the mechanical C-026 Resolution Delta check independently reproduced by hand: both R-001's and R-002's deltas confined exactly to their declared `scope`, zero Out-of-Scope Mutation. `pytest tests/contract/ -q` → 71 passed; `tests/capabilities/ tests/unit/test_adapter_capabilities.py -q` → 53 passed; full suite `-q` → **882 passed**, 2 pre-existing unrelated warnings. No new finding. Workspace clean throughout.

## Conclusion

Iteration 1 found R-001 (BLOCKER, fixed). Iteration 2 (Resolution Verification) found R-002 (BLOCKER, fixed) — a provenance-recording completeness defect, not a defect in `capabilities/investigate/CAPABILITY.md` itself. Iteration 3 (Resolution Verification) returned PASS with no new finding; Strict Review closed and the Change reached Completion. Review was subsequently reopened after Completion when an external, independent reviewer (Codex, PR #47) found R-003 — `capabilities/README.md`'s status paragraph had become factually false as a direct consequence of this Change's own delivery, blocked from correction by this Change's own over-broad self-imposed scope boundary (`specification-drift.md`). R-003 is fixed; Completion is pending Iteration 4's independent Resolution Verification.
