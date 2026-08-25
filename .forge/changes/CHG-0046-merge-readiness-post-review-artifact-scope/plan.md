---
forge:
  artifact: plan
  schema: 1
change: CHG-0046
status: draft
---

# Plan — CHG-0046 Merge Readiness Post Review Artifact Scope

1. `tests/cli/test_merge_check.py`: add TDD-001 (`state.current: complete`
   Change-local post-freeze file tolerated, AC-001), confirm RED against
   unmodified `evaluator.py` for the expected reason (`MR-015` present in
   stdout).
2. `tests/cli/test_merge_check.py`: add TDD-002 (same Change-local file,
   `state.current` not `complete`, AC-003), confirm it already passes
   against unmodified `evaluator.py` — recorded as a guard test, not a RED
   cycle, since Architecture's design does not change this path.
3. `tests/cli/test_merge_check.py`: add TDD-003 (characterization test:
   `change_root`-external `src/` file changed post-freeze while
   `state.current: complete`; asserts today's actual outcome, currently
   `MERGE READY` with no `MR-015`, confirmed by Discovery's reproduction)
   — this is a characterization test of the pre-existing, Out-of-Scope gap
   (AC-002), not a RED cycle for this Change's own behavior.
4. `src/forge_cli/merge_readiness/evaluator.py`: implement Architecture's
   Design section — compute `is_complete = manifest.get("state", {}).get("current") == "complete"`
   in `_check_change()` (`manifest` already loaded at function entry) and
   change the MR-015 staleness predicate at `evaluator.py:145` from
   `any(item and item not in allowed for item in delta.stdout.splitlines())`
   to the state-conditioned form that also tolerates
   `item.startswith(f"{change_root}/")` when `is_complete`. Confirm TDD-001
   GREEN, TDD-002 and TDD-003 unaffected (still pass, for the same reasons
   as before).
5. `tests/cli/test_merge_check.py`: add TDD-004, parametrized over the ten
   paths Discovery/Test Strategy list, asserting
   `classify_path(path, load_materiality_policy())` returns `material`.
   Confirm RED against unmodified `protocol/policies/merge-readiness.yml`
   (`ambiguous` today).
6. `protocol/policies/merge-readiness.yml`: add the four prefix entries
   Architecture selects (`.claude/skills/forge/`, `.agents/skills/forge/`,
   `.forge/adapters/`, and `.claude/CLAUDE.md` as an exact `material_paths`
   entry — it is a single file, not a prefix) to `material_prefixes`/
   `material_paths`. Confirm TDD-004 GREEN.
7. Confirm the pre-existing `test_ambiguous_unclassified_diff_is_blocked`
   and the full existing `tests/cli/test_merge_check.py` suite still pass
   unmodified (AC-005, TDD-005 per Test Strategy — no new test needed
   there beyond this confirmation).
8. Run the full `pytest -q` suite, `forge validate`, `forge doctor` against
   this repository's own real state — establish the true pre-Change
   baseline is preserved (no unrelated regression).
9. Reproduce CHG-0045's actual PR #36 scenario directly: run
   `forge change merge-check --base 3aa195539218b8902296ff37f043359dd6e2614c --head 9f49c13761be6c3779045b3a186c3aeaccaff938`
   against this Change's implementation and confirm `MR-015` and `MR-017`
   no longer appear (MR-006/MR-008 are expected to still appear — Out of
   Scope, not this Change's success condition). Record the before/after
   output in `verification.md`.
10. `verification.md`: real evidence for every TDD-xxx cycle, the full
    `pytest -q`/`forge validate`/`forge doctor` output, and item 9's
    before/after `forge change merge-check` reproduction — `## Result`
    first (`artifact-structure.md` §4).
11. Documentation Impact evaluation: assess whether `CHANGELOG.md` needs an
    Unreleased entry (a CI-gate behavior change is user-facing to every
    contributor whose PR the gate evaluates) and whether an ADR is
    warranted (DEC-001 is a material architectural decision — F-008
    threshold likely met; confirmed, not pre-decided, during Documentation
    Impact with real Implementation evidence in hand).
12. `knowledge-capture.md`: durable lessons from this Change — at minimum,
    that two independent implementations of the same Contract invariant
    (evaluator.py's MR-015, validation/__init__.py's C-026 check) had
    silently diverged, and that probing an Acceptance Criterion's actual
    truth (AC-002) during Architecture surfaced a more severe, unrelated,
    live gap Specification's original draft had not verified.
13. Strict Review: independent Execution/Context, evaluated against this
    Change's own frozen subject once all of the above lands and `forge
    validate`/`forge doctor` are clean.

## Validation Strategy

`pytest -q` (existing suite plus TDD-001–004), `forge validate`, `forge
doctor` — run before Implementation begins to capture the true pre-Change
baseline, and again after every numbered item completes. Item 9's direct
reproduction against CHG-0045's actual PR #36 commits is the Specification-
level acceptance check (Success Criteria), run in addition to the unit-level
TDD suite, not instead of it.

## Compatibility Impact

No Protocol version change (C-046; Specification CON-001). No schema
change to any `.forge/changes/*` artifact or to
`protocol/policies/merge-readiness.yml`'s own schema
(`forge/policy/merge-readiness@1`) — only its data grows. Every Change
already merged to `main` is unaffected retroactively; this Change only
changes future `forge change merge-check` evaluations. No other Harness
Adapter or CLI command reads `merge_readiness/evaluator.py` or
`merge-readiness.yml` directly (confirmed: `grep -rl` for both across
`src/` finds only the merge-readiness package itself and its own CLI
wiring in `change_cli.py`).

## Implementation Boundary

Reaching `tasks_ready` is not, by itself, authorization to begin
Implementation. For an active Change adopted from CHG-0025 onward —
CHG-0046 is — C-077 additionally requires a recorded human-authority Plan
Decision: a material technical Decision owned by `plan` with
`authority: human`, `status: resolved`, `resolved_via: human_decision`,
plus the Plan and provenance recording the explicit human confirmation
observed by the operator. `status: approved` alone is not authorization,
and this Plan's `forge:plan-approval-confirmation`/
`forge:plan-approval-record` markers below remain empty until that
confirmation is actually received in this session. No Implementation or
TDD GREEN work may begin before then.

<!-- forge:plan-approval-confirmation -->

This Plan is explicitly authorized by the human maintainer to proceed to
Implementation.

<!-- forge:plan-approval-record -->

**Approval record.** Explicit human approval was received from the user,
selecting "Aprovar e prosseguir" in response to a direct AskUserQuestion
Plan Decision prompt in the active session on 2026-08-25. This
confirmation authorizes the recorded Plan decision (DEC-002) and
continuation under C-077.
