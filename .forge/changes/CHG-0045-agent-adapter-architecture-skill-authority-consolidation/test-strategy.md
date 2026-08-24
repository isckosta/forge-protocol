---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0045
status: complete
---

# Test Strategy — CHG-0045

## Objective

Prove the behavior each FR claims, not just the presence of a string in
generated output. Three test levels, matching the three kinds of claim
this Change makes:

- **Rendering-shape tests** (pytest, no real Git repository) — assert the
  generated `SKILL.md`/hook content has the structural property an FR
  requires (block appears once, sentence appears once, matcher list
  extended).
- **Behavioral/golden tests** (pytest, real subprocess execution against
  the actual generated artifacts — the existing pattern
  `test_hook_script_denies_in_place_mutation_of_review_control_paths`
  already uses for the Bash case) — pipe real JSON payloads to the actual
  generated hook script and assert allow/deny, exactly as Architecture's
  Risk about not overclaiming coverage requires.
- **Repository-fixture tests** (pytest, `tmp_path` + real `git`
  init/worktree) — for the worktree and installation-record claims
  (US-006, DEC-004), where no amount of reading code substitutes for
  actually creating a second worktree and observing what Forge resolves.

## Strategy

Every existing test in `tests/` that currently exercises
`claude_code/projection.py`, `codex/projection.py`, `ownership.py`,
`service.py`, or the generated hook script MUST continue passing
unchanged except where an FR's Acceptance explicitly requires new
behavior (NFR-002). New tests are added, not substituted for old ones,
unless an old test asserted the exact duplication this Change removes (in
which case Verification records the intentional removal, per
`artifact-structure.md`'s Verification guidance, rather than silently
deleting a test with no explanation).

## TDD-001 · Independence block renders exactly once
FR-001 / AC-004. Given a project with `fast`, `standard`, `full` all
enabled under Protocol 2, when `_skill_content()` (or its successor)
renders, then `"### Reviewer/Resolver independence"` occurs exactly once
in the output — assert via `content.count(...)`.

## TDD-002 · Every applicable Flow section still points at the shared block
FR-001 / AC-004 (Specification Review SR-002 fix). Given the same
rendered output, when each of the three per-Flow gate-obligation sections
is inspected, then each contains an explicit reference/pointer to the
single Reviewer/Resolver-independence section — not merely its absence.

## TDD-003 · Claude Code and Codex share one independence-text source
FR-002 / AC-005. Given both drivers' modules are imported, when their
independence-text constants/functions are compared, then they resolve to
the same shared object/value — the test MUST fail if either module
redefines its own local copy (e.g. by asserting `is` identity or by
asserting both import from the same shared module path, not merely equal
strings that could independently drift back apart later).

## TDD-004 · Shared independence text agrees with the effective C-026 paragraph on mechanically-checkable claims
FR-002 / NFR-001 (Specification Review SR-001 fix). Given the current
`protocol/contract/engineering.md` C-026 text and the shared independence
module's rendered text, when both are scanned for a fixed set of required
terms (independent Execution/Execution Context; `claimed`/`recorded`/
`verified`; Role-change-inside-one-Execution insufficiency), then both
contain all of them — this test is expected to fail loudly if a future
Contract edit changes C-026's substance without a matching Adapter update,
which is its actual purpose (an early-warning regression guard, not proof
of semantic equivalence).

## TDD-005 · CHG-0025/C-077 sentence renders exactly once
FR-003 / AC-003. Given the same three-Flow rendered output, then the
CHG-0025/C-077 Plan Decision sentence (or its successor wording sourced
from `workflow.md`) occurs exactly once, not once per applicable Flow.

## TDD-006 · Generator output is idempotent and matches a fresh install
FR-003 / AC-003. Given a fresh `forge adapter install claude-code` into an
empty fixture project at this Change's final state, when its generated
`SKILL.md` is compared to the output of running `forge adapter update`
against a fixture pre-seeded with the pre-Change generator's output, then
both converge to byte-identical content — proving the specific staleness
Discovery found (installed file containing text the generator no longer
emits) cannot recur silently.

## TDD-007 · Bootstrap drift-check instruction is present and correctly scoped
FR-004 / AC-006, AC-007. Given the rendered `SKILL.md`, then a Bootstrap-
section instruction references checking Adapter drift (naming
`forge doctor` or `forge adapter doctor`) before trusting `references/*`,
and states the "stop and report, do not silently self-heal" behavior
required by FR-004's Expected Behavior.

## TDD-008 · Restructured sections are locatable
FR-005 / AC-001. Given the rendered `SKILL.md`, then a reader can find,
each in an identifiable section (not scattered across three near-duplicate
Flow blocks): what is authoritative, what to resolve before mutating, what
to do at a human-authority boundary, what to do on guard denial. Asserted
by presence/ordering checks on section headings actually chosen during
Implementation (this test is written after Implementation's concrete
heading choice exists, per TDD's normal RED-before-behavior sequencing —
the *property* is fixed now; the *literal heading strings* are not).

## TDD-009 · Hook frontmatter registers Edit and Write matchers
FR-006 / AC-008. Given the generated `SKILL.md` frontmatter, then
`PreToolUse.hooks` contains matcher entries for `Bash`, `Edit`, and
`Write`, all pointing at the same generated hook script path.

## TDD-010 · Hook denies an Edit-shaped protected-path mutation (golden, behavioral)
FR-006 / AC-008. Given the actual generated `check-manifest-edit.sh` from
a fresh `forge adapter install`, when a realistic Claude Code `PreToolUse`
JSON payload for `Edit` targeting
`.forge/changes/CHG-XXXX/manifest.yml` is piped to it via subprocess, then
it emits `permissionDecision: "deny"` — mirroring the existing Bash golden
test's actual-subprocess methodology, not a unit test of Python string
logic.

## TDD-011 · Hook allows a non-protected Edit/Write call (false-positive avoidance)
FR-006 / AC-009. Given the same script, when a realistic `Edit`/`Write`
payload targeting an unrelated path (e.g. `src/forge_cli/adapters/
claude_code/projection.py`) is piped to it, then it allows (no
`permissionDecision` output), matching the existing Bash case's R001
false-positive-avoidance precedent (CHG-0018).

## TDD-012 · Existing Bash guard behavior is unchanged
Regression. The existing
`test_hook_script_denies_in_place_mutation_of_review_control_paths` suite
(all documented allow/deny cases from CHG-0018) continues passing
unchanged against the extended script.

## TDD-013 · Boundary-reporting instruction is present
FR-007 / AC-002. Given the rendered `SKILL.md`, then an instruction
requires reporting Current Change, Effective Flow, Current State,
Boundary, Required Decision/Evidence, and Next Permitted Action at a
human-authority/blocked/missing-evidence boundary.

## TDD-014 · Generated SKILL.md does not grow
NFR-003. Given the same three-Flow Protocol-2 fixture project, when line
counts of the pre-Change and post-Change generated `SKILL.md` are
compared, then the post-Change count is less than or equal to the
pre-Change count (captured as a fixture/golden baseline recorded during
Implementation, compared exactly — not a heuristic).

## TDD-015 · Codex bundle regresses nothing beyond the intended shared source
NFR-002. The full pre-existing Codex Adapter test suite passes unchanged
except for the specific assertion(s) TDD-003 replaces (Codex's own
independence-text constant no longer independently defined).

## TDD-016 · Worktree root resolution is correct (golden, repository-fixture)
US-006 / AC-010. Given a real `git init` fixture repository with a second
worktree created via `git worktree add`, when `resolve_project_root(Path.cwd())`
is invoked with `cwd` set inside the secondary worktree, then it returns
the secondary worktree's own top-level path, not the primary checkout's —
executed against real `git`, not mocked, since Architecture's claim rests
entirely on `git rev-parse --show-toplevel`'s actual behavior.

## TDD-017 · Committed installation record is available in a fresh worktree
DEC-004. Given `installation.yml` is committed (Plan task), when a second
worktree is created from the same commit, then `forge adapter doctor`
run inside that second worktree reports the same `generated_drift` state
as the primary checkout, without requiring a separate `forge adapter
install` in the second worktree first.

## Non-mechanical Validation

- **Guard-coverage honesty (Architecture Risk).** The generated
  disclosure naming MCP-tool/`NotebookEdit`/subagent coverage as
  unverified is reviewed by a human/Reviewer for accuracy, not asserted by
  a test — whether Claude Code's `PreToolUse` hooks apply to subagent tool
  calls is outside this repository's control to assert with a unit test;
  Verification records what was actually checked and what remains
  genuinely unknown, per C-021 ("Tests are evidence" — not proof).
- **SKILL.md readability.** FR-005's "locatable" property (TDD-008) is
  reviewed by a human/Reviewer reading the rendered file top-to-bottom,
  in addition to the mechanical heading-presence check.

## Completion Criteria

- TDD-001 through TDD-017 pass.
- `forge validate` and `forge doctor` report clean (no `FAIL`, no
  `CONFLICT`) after a fresh `forge adapter update` republish for both
  Adapters in this repository's own project configuration.
- The full pre-existing `pytest` suite passes unchanged except for the
  specific, disclosed removals TDD-003/TDD-015 name.
- Strict Review passes independently per this repository's own C-026
  requirements (self-hosting boundary, Specification's own recorded
  statement).
