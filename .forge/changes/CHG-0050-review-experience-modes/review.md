---
forge:
  artifact: review
  schema: 1
change: CHG-0050
status: active
---

# CHG-0050 · Review

## Verdict

**PENDING.** Iteration 1: REQUEST CHANGES — R-001 (MAJOR) and R-002 (MINOR) found and resolved; R-003 (OBSERVATION) accepted/disclosed, R-004 (OBSERVATION) corrected. Iteration 2 (Resolution Verification) pending.

## Review Summary

| | |
|---|---|
| **Iterations** | 1 (Iteration 2 pending) |
| **Current Subject** | `817cda3913d789da3a8d6d0ba28f1b4d47d1fd3a` (Iteration 1's reviewed subject; superseded pending Resolution freeze) |
| **Open Blockers** | 0 |
| **Open Majors** | 0 (R-001 resolved) |
| **Open Minors** | 0 (R-002 resolved) |
| **Final Iteration** | pending |
| **Result** | pending |

## Reviewer Independence

`provenance.yml`'s `reviewer-001` record (fresh agent invocation, isolated Git worktree, no shared Execution or Execution Context with the Implementation).

## Iteration 1 — REQUEST CHANGES

**Reviewer**: Independent Reviewer execution (fresh agent invocation, isolated Git worktree at `/home/isckosta/forge-protocol/.claude/worktrees/agent-a9c707c9110126514`, no shared context with the Implementation that produced this revision), per C-026. This Review ran at the `strict` profile (this Change's own Flow is FULL), fully adversarial.

**Commit reviewed**: `817cda3913d789da3a8d6d0ba28f1b4d47d1fd3a`.

**Baseline for diff**: `94b75b4` (Plan approval provenance commit, i.e. the last commit before Implementation began).

### R-001 · MAJOR — `forge change review-status` crashes with an unhandled `KeyError` instead of failing cleanly

`resolve_effective_review_profile` (`protocol_resolution/__init__.py`) does `PROFILE_RANK[floor]` with no guard. `review_status()`'s call chain can supply an *unvalidated* `floor` — `compute_review_profile_floor` returns a project-flow override's `review.profile` value verbatim, without checking it against the enum — and `review_status()`'s surrounding `try/except` did not catch `KeyError`. Live-reproduced: a `.forge/flows/standard.yml` override of `review.profile: super-strict` (a value `forge validate` already rejects with `E_FORGE_REVIEW_PROFILE_BELOW_FLOOR`) made `forge change review-status` dump a raw Python traceback and exit 1, instead of degrading the way the adjacent configuration-error handling already does. FR-006's Boundary explicitly requires this command to be safe to run on a project in a bad state.

**Resolution**: added `KeyError` to `review_status()`'s existing `except` tuple, so an unrecognized floor degrades exactly like every other caught configuration error (the "Resolved profile" line is omitted; the rest of the report still renders). New regression test `test_review_status_does_not_crash_on_an_invalid_project_flow_override_profile` (`tests/cli/test_change_review_status.py`) reproduces R-001 as valid RED against the pre-fix code (`KeyError('super-strict')`, exit 1) and passes after. See `tdd-evidence.yml`'s `TDD-011`.

### R-002 · MINOR — `compute_review_profile_floor` did not eliminate the duplication Architecture claimed it removed

`_validate_review_profile_floor` still independently re-derived the canonical-profile chain inline instead of the extraction actually removing it, per `architecture.md`'s Component Map claim. Not a functional bug (the duplicate branch was dead code on the only path exercised), purely a maintainability concern.

**Resolution**: extracted the shared `_canonical_review_profile(effective)` helper, used by both `compute_review_profile_floor` and `_validate_review_profile_floor`; behavior-preserving (existing `TDD-001` tests pass unchanged).

### R-003 · OBSERVATION — the per-Flow mode-resolution line reflects the canonical Flow's profile, not a project's stricter override

`render_mode_resolution_line` is computed from the canonical Flow only; a project using a stricter-than-canonical `.forge/flows/<flow>.yml` override would see Adapter-projected text that doesn't reflect that override, even though FR-002's own "floor" definition includes it. Confirmed pre-existing: the adjacent, unmodified `REVIEW_PROFILE_INSTRUCTION` line has the identical characteristic, and `_gate_instructions` only ever receives canonical Flow content at this call site (traced via `adapters/service.py`'s `_effective_flows`).

**Not fixed** — accepted, disclosed limitation, consistent with this being a pre-existing Adapter-projection characteristic this Change did not introduce, not a regression. A candidate for a future, narrowly-scoped Change if a project's own stricter override in practice needs to be reflected in install-time projected text.

### R-004 · OBSERVATION — `test-strategy.md`'s TDD-010 prose overstated "byte-identical"

The scaffold always writes an explicit `review.mode: recommended` field regardless of whether a project preference is set, so a no-preference scaffold is not literally byte-identical to a pre-CHG-0050 scaffold — permitted by AC-008's own "(or omits it)" alternative, but the Test Strategy prose overstated what was verified.

**Resolution**: `test-strategy.md`'s TDD-010 Scenario/Evidence/Failure Condition corrected to describe the shipped behavior accurately.

### Checked and found sound (Iteration 1)

- Full suite (independent run): 856 passed, 2 pre-existing warnings — exact match to `verification.md`'s claim.
- `forge validate`: PASS — exact match.
- FR-002's never-below-floor guarantee independently re-derived by code inspection and live reproduction across garbage `mode` values (no crash; always resolves to `floor` or one rank above).
- FR-004's `_validate_review_current_phase` scope confirmed to match AC-010–AC-012b exactly, no more and no less.
- FR-005/DEC-004's claim independently re-derived, not trusted: generated Adapter projections at both the parent and target commits from archived trees, diffed them, and confirmed the `### Reviewer/Resolver independence` block is byte-for-byte identical; confirmed `_gate_instructions` only ever receives canonical Flow content (immune to the R-001-class crash at that call site).
- FR-007 confirmed by absence: zero references to `"stopped"` anywhere in `validation/__init__.py`'s Completion/`review_passed` gating logic.
- FR-006's exit-code/error-path ordering (`passed` → `stopped` → blockers/majors → `resolving` → fallback) traced and found sound and non-overlapping.
- Both new schema additions confirmed genuinely additive (`required` arrays and `additionalProperties: false` unchanged).
- AC-009 (no retroactive override) confirmed structurally: `preferred_mode` is read at exactly one call site in the entire `src/forge_cli/` tree.
- `rfc-acceptance-001`/`plan-approval-001` provenance records independently spot-checked (content digest recomputation, referenced commits exist and substantiate the claimed events).
- `tdd-evidence.yml`'s claimed RED states for TDD-001–004 independently reproduced against the parent commit's archived tree.
- CON-001/CON-002 confirmed: no Contract file touched; independence, evidence/severity handling, and the FR-010 targeted-re-review escalation logic are unmodified.

## Resolution

R-001 and R-002 were fixed, and R-004's documentation inaccuracy corrected, in a Resolution Execution distinct from Iteration 1's Reviewer Execution, in direct response to Iteration 1 (per C-026's Resolver-independence requirement). R-003 was evaluated and explicitly left unfixed as a disclosed, accepted, pre-existing limitation. `tdd-evidence.yml` gained `TDD-011` documenting R-001's RED→GREEN cycle. The resolved revision is frozen and referenced by `provenance.yml`'s `resolution-001` record; Iteration 2 independently re-reviews that exact revision.
