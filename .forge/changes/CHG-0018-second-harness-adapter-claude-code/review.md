---
forge:
  artifact: review
  schema: 1
change: CHG-0018
status: passed
---
# Strict Review — CHG-0018

## Verdict

**PASS (Iteration 1, `kind: initial_review`).** No BLOCKER or MAJOR
Findings. 1 MINOR, 0 OBSERVATION — non-blocking per
`protocol/policies/review.yml` (`blocking: [blocker, major]`).

The Implementation subject does what it says, at a scale this repository
has not previously attempted in one Change: the two pre-existing Core
leaks (`.codex` hardcoding, misfiled generic invariant-assessment logic)
are genuinely fixed, not just described; the generic Core's `adapters/*.py`
surface is verified, by direct grep, to be free of vendor names outside
the one disclosed composition-root exception; a second concrete Harness
Adapter installs, projects, and drift-checks correctly against real scratch
repositories; the shared conformance suite exercises real, non-trivial,
driver-agnostic assertions (determinism, ownership-root containment,
honest capability-limitation representation) against both concrete
Drivers; C-074 is byte-identical between both Contract files; and — the
claim this Review treated as requiring the most scrutiny — the dogfooded
Layer C Golden Path is genuine. I did not accept that claim from
`verification.md`'s prose: I located the actual scratch Git repository the
live Claude Code session produced, still present on this host's
filesystem, inspected its real commit history and file contents directly,
independently re-executed the claimed bug/fix in Python myself, read the
raw Claude Code session transcripts (JSONL) documenting real Skill
auto-discovery and a real `PreToolUse`-eligible tool-use event, and then
ran my own fresh, independent `claude -p` session against a fresh copy of
`examples/golden-path-claude-code/starter/` and observed the same
mechanism (unprompted Skill invocation, real RED-before-GREEN via actual
`pytest` subprocess runs, and correct Protocol 2 independent-review
behavior) fire again. Full detail below and in `provenance.yml`.

One MINOR finding: the illustrative `PreToolUse` hook's substring-based
pattern matching produces a real, demonstrated false-positive on a
plausible compound Git command that FR-006 explicitly says must remain
unaffected.

## Summary

| Severity | Count |
| --- | --- |
| BLOCKER | 0 |
| MAJOR | 0 |
| MINOR | 1 |
| OBSERVATION | 0 |

## Review Subject

Frozen Implementation subject `6214390dc0f36ee982b0ce83185b1eaa08f21d7d`
(`provenance.yml`, record `implementation-001`), reviewed against the
Change's own baseline `023649a` (`CHG-0017`'s own Completion commit). The
later commit `b192824` (implementation-role provenance recording, touching
only this Change's own `manifest.yml`/`provenance.yml`) is Change-local
review-control metadata, exempt from the freeze per Protocol 2, and was
not treated as part of the reviewed diff.

## Review Execution Independence

This Review was executed in an Execution and Execution Context distinct
from the Implementation session that produced `implementation-001`, per
Contract C-026 and Protocol 2 §2. It was performed cold, from repository
state alone, with no access to the Implementation conversation and no
prior memory of this Change beyond what the committed Artifacts and diff
state. Every diff was read directly (`git log 023649a..6214390 --oneline`,
`git show <sha>` for each commit); no claim in `verification.md`,
`tdd-evidence.yml`, `knowledge-capture.md`, `specification-review.md`, or
any commit message was accepted without independent reproduction. See
`provenance.yml` record `review-001` for this execution's own
self-recorded provenance and honest assurance statement.

## Iteration 1 — PASS

### R001 — MINOR — The `PreToolUse` hook's substring matching denies plausible, legitimate compound Git commands that FR-006 says must remain unaffected

**Problem:** FR-006 requires: "It MUST NOT match read-only or
version-control commands against the same paths (`cat`, `ls`, `git add`,
`git commit`, `git status`, `git diff`, `git show`, `grep`) — those remain
unaffected." The generated hook script
(`.claude/skills/forge/hooks/check-manifest-edit.sh`,
`src/forge_cli/adapters/claude_code/projection.py:241-263`) implements
this as two nested shell `case` patterns over the *entire* `tool_input.command`
string: the outer pattern requires `.forge/changes/` and one of
`manifest.yml`/`provenance.yml`/`review.md` to appear anywhere in the
string; the inner pattern denies if `sed -i`, `perl -i`, `truncate`, or a
bare `>` appears *anywhere else* in that same string, with no requirement
that the two be adjacent or causally related. A `git add`/`git commit`
invocation of a protected path that happens to also contain a `>`
character anywhere else in the command — a realistic shape, not a
contrived one — is denied, even though it is fundamentally the exact
`git add`/`git commit` shape FR-006 names as always-safe.

**Evidence:** Built the real generated hook script via
`forge adapter install claude-code` against a fresh scratch repository and
piped real JSON payloads to it directly (`sh -c "$SCRIPT"`):

```
$ echo '{"tool_input":{"command":"git status > /tmp/status.txt && git add .forge/changes/CHG-0018-x/manifest.yml"}}' | sh check-manifest-edit.sh
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny", ...}}

$ echo '{"tool_input":{"command":"git commit -m \"docs(chg-0018): note -- see .forge/changes/CHG-0018-x/manifest.yml > also check review.md\""}}' | sh check-manifest-edit.sh
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny", ...}}
```

Both commands are, in substance, an ordinary `git add`/`git commit` of a
review-control path — exactly the workflow FR-006, Specification Review
SR-001, and this Change's own commit history (e.g. the `docs(chg-0018):
record role:` commits) depend on — denied solely because an unrelated `>`
appears elsewhere in the same command line. The existing test,
`test_hook_script_denies_in_place_mutation_of_review_control_paths`
(`tests/unit/test_claude_code_projection_bundle.py:201-254`), only
exercises atomic, single-purpose commands in its `allowed` list (`git add
.../manifest.yml`, `git commit -m 'update manifest.yml'`, etc.) — it does
not cover a compound or a longer, realistic commit-message shape, so this
gap was not caught by TDD-002's own GREEN evidence.

**Impact:** Non-blocking. Architecture's own Risks section already
discloses, in the abstract, that "an unusual but legitimate command could
match [the pattern]" and states the mechanism is "an illustrative
capability demonstration, not a security boundary," and FR-006 itself
requires only that the hook "MUST NOT claim to enforce anything beyond
that narrow, mechanically-checkable pattern" — which it does not. No
Artifact in this Change overclaims what the hook actually does. But the
specific failure mode demonstrated here is more concrete than the
disclosed abstract risk, is plausible under ordinary, non-adversarial use
(a commit message that happens to contain `>`, or a routine multi-command
shell line), and sits closer to the literal git-add/git-commit exclusion
FR-006 names by example than the "arbitrary shell quoting/obfuscation"
evasion class the Risk paragraph was written about.

**Suggested Resolution (non-blocking, Resolver's judgment per C-025):**
Scope the inner in-place-mutation match to require adjacency to (or a
shared shell-clause with) the matched path token, rather than matching
against the whole command string — or narrow the outer match to the exact
command-name token position (e.g. via a leading-word check) rather than
free substring containment. Either way, add at least one compound-command
test case to `test_hook_script_denies_in_place_mutation_of_review_control_paths`'s
`allowed` list documenting the intended behavior once resolved (or, if
left as-is, add an explicit, disclosed note in FR-006/`architecture.md`'s
Risks section naming this specific compound-command shape, not only the
more abstract evasion risk already named).

## Checked and found sound (no defect)

- **Test suite, reproduced independently.** `python -m pytest -q` →
  **504 passed** in ~62s, matching `verification.md`'s claimed figure
  exactly. Arithmetic verified independently, not merely trusted: 48
  Claude-Code-specific unit tests (`pytest --collect-only -k claude_code`),
  15 shared conformance tests (`test_adapter_driver_conformance.py`), 2
  Golden Path Layer A/B tests (`test_golden_path_claude_code.py`), plus 2
  parametrized CLI install/doctor tests = 67 new, 437 + 67 = 504. `forge
  validate` → "Forge project is valid", exit 0. `forge doctor` → 7/7 PASS.
  All reproduced fresh in this Review's own Execution.
- **FR-001/AC-001, reproduced end to end.** `adapters/configuration.py`'s
  `_checked_target` no longer references `.codex`; the schema regex
  (`protocol/schemas/adapter-configuration.schema.json`) no longer has the
  `.codex` clause, and I independently confirmed, via a standalone Python
  script compiling the actual packaged regex, that `.codex/anything` and
  `Xcodex/anything` (the latent unescaped-`.` bug case) both now validate
  at the schema level. `codex/targets.py` still rejects `.codex`/
  `.codex/forge` directly — confirmed by reading the code and by the real
  test `test_codex_owned_reserved_path_is_rejected`
  (`tests/unit/test_codex_publication_targets.py:82-98`), which exercises
  both `resolve_publication_target` and `validate_publication_root`.
- **FR-002/AC-002, reproduced.** `src/forge_cli/adapters/codex/assessment.py`
  no longer exists (`ls` fails); `src/forge_cli/adapters/assessment.py`
  exists, exports `assess_invariant`/`to_generic_limitation` with
  identical logic, and both `codex/driver.py` and `claude_code/driver.py`
  import from it.
- **NFR-001, verified by direct grep, not accepted from the claim.**
  `grep -niE "codex|claude|\.claude|\.codex"` across every `*.py` file
  directly under `src/forge_cli/adapters/` (excluding the `codex/` and
  `claude_code/` subpackages) returns hits only in `adapters/packaged.py`
  (`CodexDriver`/`ClaudeCodeDriver` imports and registration) — exactly
  the one disclosed, intentional composition-root exception.
- **Three real projection mechanisms, verified against real generated
  files, not just source.** Built a fresh scratch Git repository,
  ran `forge init` then `forge adapter install claude-code` against it
  through the actual installed CLI, and inspected the output directly:
  `.claude/skills/forge/SKILL.md` (+ `references/{engineering-contract,
  artifact-structure,flows/*}.md`) with a `hooks.PreToolUse` frontmatter
  block pointing at `${CLAUDE_PROJECT_DIR}/.claude/skills/forge/hooks/
  check-manifest-edit.sh`; `.claude/CLAUDE.md`, a short pointer that names
  the `forge` skill and does not restate Contract/Flow content (INV-001);
  and the hook script itself, present and executable in content.
  `forge adapter install claude-code` re-run against the same repository
  reports `UNCHANGED` for all eight generated files (AC-005 idempotence).
  `forge adapter doctor claude-code` reports 6/6 PASS + 1 honest WARN
  (capability limitations represented, not enforced, for `strict-review`/
  `tdd-red-before-behavior`). `forge adapter list` shows both `codex` and
  `claude-code`, both `compatible`.
- **FR-006's core SR-001 concern (bare `git add`/`git commit`/`cat`/`ls`/
  `grep`/`git status`/`git diff`/`git show` of the three protected paths)
  is genuinely fixed** — verified by piping real JSON payloads to the
  actual generated script for `sed -i`, `perl -i`, `truncate`, and `>`
  against each of `manifest.yml`/`provenance.yml`/`review.md` (all
  correctly denied) and for `git add`, `git commit -m "docs(chg-0018):
  update manifest.yml"`, `cat`, `grep`, and a bare `ls -la` (all correctly
  allowed, no output, exit 0). See R001 above for the one demonstrated gap
  beyond this core case.
- **`enforced_invariants=("INV-005",)` in `claude_code/driver.py` is a
  pre-existing, unrelated Core-level structural claim, not a new
  overclaim about the FR-006 hook.** Byte-identical to `codex/driver.py`'s
  own pre-existing line; INV-005 ("Harness-specific behavior cannot
  redefine canonical Forge semantics", `CHG-0001`) is true by construction
  for any Driver and predates this Change. The FR-006 hook's real, narrow
  enforcement capability is correctly *not* represented anywhere in
  `AdapterRepresentation` — avoiding exactly the overclaim NFR-003 and
  C-073 would forbid.
- **C-074, byte-identical (modulo the pre-existing single-line-vs-wrapped
  convention) between both Contract files** — read both directly
  (`protocol/contract/engineering.md:301-305`,
  `protocol/versions/2/contract/engineering.md:242-243`), matching the
  `C-070`-`C-073` dual-file precedent.
- **`protocol/specification.md` §34-38's claim of pre-existing
  harness-neutrality, confirmed by reading all five sections directly**
  — no Codex- or Claude-Code-specific term appears; the capability
  vocabulary, ownership modes, and conformance language are already
  Adapter-plural and harness-generic. No Specification change was needed,
  as claimed.
- **Capability evidence (NFR-003/AC-004), spot-checked against the actual
  live pages, not merely trusted.** Fetched `code.claude.com/docs/en/hooks`
  and `code.claude.com/docs/en/memory` directly: both confirm the exact
  claims `capabilities.yml`/`discovery.md` cite — Skill-frontmatter
  `hooks:` fields "registered when you or Claude invoke the skill... for
  the rest of the session," `PreToolUse` blocking via `permissionDecision`
  or exit code 2, and "a project CLAUDE.md can be stored in either
  `./CLAUDE.md` or `./.claude/CLAUDE.md`" verbatim.
- **DEC-001/002/003 classification is defensible.** All three are
  genuinely `architectural` class (implementation-shape choices within an
  already-approved Specification — publication path, hook placement, no
  shared renderer) with no `product`/`contract` Materiality trigger
  (`decision.yml`) turning on any of them; `agent_with_review` authority
  and `owning_artifact: architecture` match `decision.yml`'s own
  ownership/authority tables. DEC-001's Implementation-time correction
  (publication root `.claude`, not `.claude/skills/forge`) is recorded
  honestly as a correction, not silently absorbed, and I independently
  confirmed the actual generated artifact paths are consistent with it.
- **Flow classification (FULL) is correctly justified**, not merely
  asserted — this Change genuinely touches the generic Adapter Core (two
  fixes), a Protocol schema, both Contract files, and a large new
  executable package with new tests, the same combination `discovery.md`
  cites as already classifying `CHG-0013`/`CHG-0015`/`CHG-0016`/`CHG-0017`
  as FULL.
- **Documentation Impact matches what actually shipped.**
  `CHANGELOG.md`/`ROADMAP.md` both reflect this Change (`ROADMAP.md`'s
  "Second Harness Adapter" section marked Completed, Gate D referenced);
  `docs/adr/0016-second-harness-adapter-claude-code.md` exists and records
  every Decision FR-010 requires, matching `architecture.md`'s DEC-001/
  002/003 content directly, not a paraphrase that drifts from it.
- **No scope creep.** `git diff 023649a..6214390 --stat` and the commit
  sequence (`723efd9`, `35fbb48`, `4f676b9`, `4531b8f`, `9b23c41`,
  `e5579ec`, `6214390`) touch exactly the files `plan.md`/`architecture.md`
  name in advance: the two Core-fix files, the new `claude_code/` package,
  registration, both Contract files, the ADR, the Golden Path example
  directory, and this Change's own `.forge/changes/CHG-0018-.../`
  artifacts. No historical `CHG-0001`-`CHG-0017` artifact was touched.

## Layer C — the Golden Path claim, verified independently, not accepted from prose

This is the claim this Review treated as requiring the most scrutiny, per
this repository's own instruction that a live, independently-governed
session catching and fixing a real bug through genuine self-review is an
extraordinary claim. Three independent lines of verification, not one:

**1. The actual scratch repository still exists on this host, and I
inspected it directly, not through `verification.md`'s description of
it.** `/tmp/claude-1000/-home-isckosta-forge-protocol/6abe8602-5e05-4041-af38-70ae9a3796bf/scratchpad/golden-path-cc-live`
is a real Git repository with real commit history:
`139a23c` (baseline) → `cb193ee` (Forge init + Adapter install) → `55f7cf7`
(the whitespace-only-name fix, with the regression) → `7828e3d` (R001
resolution) → `9c79dac` (Completion) — the exact hashes `verification.md`
cites. I checked out `55f7cf7`'s and `7828e3d`'s versions of
`src/greeting/greeter.py` and ran `greet(None)`/`greet("  Ana  ")` myself:
`55f7cf7` genuinely raises `AttributeError` on `greet(None)` (the real
regression the spawned review subagent found); `7828e3d` genuinely raises
`ValueError` and correctly preserves `"  Ana  "` unchanged. The
`.forge/changes/CHG-0001-.../manifest.yml`/`provenance.yml` in that
scratch repository genuinely use the non-canonical `forge/manifest@1`/
`forge/provenance@1` schema shape `knowledge-capture.md` claims — read
directly, not inferred. `review.md` in that scratch repository contains a
full, internally consistent, independently-plausible Iteration 1 (R001,
MAJOR, with real `AttributeError` reproductions for `None`/`0`/`False`/
`[]`/`{}`) and Iteration 2 (Resolution Verification, PASS) — matching
`verification.md`'s summary exactly, not a superset or a contradiction of
it.

**2. Raw Claude Code session transcripts (JSONL) corroborate the account
mechanically, including the self-disclosed methodology defect.** Two real
`~/.claude/projects/.../*.jsonl` session logs exist for this scratch
directory (`fcc5621c-...`, 19:57 UTC, and `c6ae2c71-...`, 19:59 UTC — both
before the corrected run's `--allowed-tools` pattern was found, matching
`knowledge-capture.md`'s "two dead ends" account: the earlier session's
last assistant message is a Portuguese prompt asking for approval to run
`pytest`, consistent with the `--permission-mode acceptEdits` stall
`knowledge-capture.md` describes). The later, working session's raw
transcript shows: the literal prompt text quoted in
`examples/golden-path-claude-code/README.md`, a `skill_listing` attachment
naming `forge` at session start (genuine auto-discovery, not asserted),
and an assistant `tool_use` block invoking `Skill({"skill": "forge", ...})`
as its very first action — before any other tool call — with no Forge
term in the user prompt. This is internal harness telemetry (deferred-tool
deltas, agent listings, skill listings) that would be very difficult to
fabricate by hand and is independent of anything `verification.md` itself
asserts.

**3. I ran my own fresh, independent reproduction, not only inspected the
original.** Built a new scratch repository from a clean copy of
`examples/golden-path-claude-code/starter/`, ran `forge init` → `forge
adapter install claude-code` → `forge doctor` (exit 0) myself, then
invoked the real `claude` binary on `$PATH` (`claude --version` → `2.1.236`,
confirming the binary claim) non-interactively with a different but
similarly-shaped, Forge-silent prompt ("...greet() should also reject a
name that is just punctuation..."). The resulting session: auto-discovered
and invoked the `forge` Skill as its first action (confirmed in its own
raw transcript, `~/.claude/projects/.../b2c95e7e-....jsonl`); explicitly
stated it would follow TDD (RED then GREEN); ran `python -m pytest
tests/test_greeter.py -v` before any production-code edit and reported the
expected-reason failure; implemented the fix; re-ran and reported all
tests passing; and — unprompted — recognized that reviewing its own change
inside the same session would not satisfy Protocol 2's independence
requirement (C-026) and spawned an independent subagent for adversarial
review, which returned PASS with one non-blocking observation. This
reproduction did not follow the exact same script as the original (it did
not create formal `.forge/changes/` artifacts, explicitly declining to
fabricate provenance it judged uncertain) — an expected, disclosed
divergence given LLM non-determinism, not a discrepancy in the mechanism
itself. The mechanism claimed — Skill auto-discovery, unprompted Forge
recognition, genuine RED-before-GREEN via real subprocess `pytest` runs,
and correct Protocol 2 self-review-avoidance — fired again, independently,
under my own control.

**Conclusion on Layer C:** genuine. Not fabricated, not narrated-only.
This is the strongest evidentiary standard available to this Review short
of having been present in the original session myself, and I obtained it
through original-artifact inspection, raw-transcript corroboration, and
my own independent re-execution — all three, not just one.

## Conclusion

One MINOR Finding, non-blocking under `protocol/policies/review.yml`'s
`blocking: [blocker, major]`. The Implementation subject genuinely does
what its Artifacts claim: two real Core leaks are fixed (verified by
direct grep and execution, not narrative), a second concrete Harness
Adapter installs and projects correctly against real repositories, the
shared conformance suite exercises substantive driver-agnostic assertions,
C-074 is correctly and identically recorded in both Contract files, and
the central, most extraordinary claim — a live, independently-governed
Claude Code session dogfooding Forge's own lifecycle including catching
and fixing a real bug through genuine independent self-review — holds
under adversarial, hands-on, three-line-of-evidence verification, not
merely a plausible-sounding write-up. This Change is **PASS** and may
proceed toward Completion.
