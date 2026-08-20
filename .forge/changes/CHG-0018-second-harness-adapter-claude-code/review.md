---
forge:
  artifact: review
  schema: 1
change: CHG-0018
status: passed
---
# Strict Review — CHG-0018

## Verdict

**PASS (final, Iteration 2 — `kind: resolution_verification`).** No
blocking Findings remain outstanding.

- **Iteration 1** (`kind: initial_review`) — **PASS**: 0 BLOCKER/MAJOR, 1
  MINOR (R001), 0 OBSERVATION.
- **Iteration 2** (`kind: resolution_verification`) — **PASS**: R001
  verified resolved against actual repository state, not accepted from
  `resolution-001`'s own claim; no Out-of-Scope Mutation; 0 new material
  findings; 1 new non-blocking OBSERVATION recorded (R002, an unrelated
  latent Core-validation finding, recorded per C-050, out of this
  Iteration's own bounded authority per C-047).

Everything below this Summary down to the end of the original `##
Conclusion` is Iteration 1's verbatim historical record, except the
Summary table immediately below, which is restated in Raised/Outstanding
form to account for R001's resolution. Iteration 2 is appended at the end
of this file.

`protocol/policies/review.yml` sets `blocking: [blocker, major]`; R001 was
never blocking, and neither is R002. Both Iterations pass, and this Change
may proceed toward Completion.

**PASS (Iteration 1, `kind: initial_review`), as originally recorded.** No
BLOCKER or MAJOR Findings. 1 MINOR, 0 OBSERVATION — non-blocking per
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

Counting semantics, stated explicitly since the Protocol does not fix them:
**Raised** is cumulative — every Finding ever recorded in this Review, in
the Iteration that recorded it. **Outstanding** is the state *after* the
final Iteration, and is what `manifest.yml`'s
`review.blockers`/`majors`/`minors`/`observations` carry.

| Severity | Raised (It. 1) | Raised (It. 2) | Raised total | Outstanding | Blocking |
| --- | --- | --- | --- | --- | --- |
| BLOCKER | 0 | 0 | 0 | 0 | yes |
| MAJOR | 0 | 0 | 0 | 0 | yes |
| MINOR | 1 | 0 | 1 | 0 | no |
| OBSERVATION | 0 | 1 | 1 | 1 | no |

R001 (MINOR, Iteration 1) is resolved by `resolution-001` and verified in
Iteration 2 — no longer outstanding. R002 (OBSERVATION, Iteration 2) is a
new, unrelated latent finding, not targeted by any Resolution, and remains
outstanding.

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

## Iteration 2 — PASS (`kind: resolution_verification`)

### Iteration 2 scope and authority

This Iteration is a **Resolution Verification**, not a second Initial
Review. Per `protocol/contract/engineering.md` C-047 and
`protocol/versions/2/specification.md` §10, its authority is bounded to
exactly three things:

1. R001, the one Finding `resolution-001` targets;
2. defects within `resolution-001`'s own Resolution Delta;
3. Out-of-Scope Mutation.

It is deliberately **not** a re-audit of `implementation-001`. Nothing in
Iteration 1's "Checked and found sound" section — the other 66 tests, the
Claude Code Driver, the ADR, the shared conformance suite, Layer C, C-074
dual-file parity, and everything else Iteration 1 already examined and
found sound — was re-litigated here. Re-opening any of that is precisely
what C-047 forbids.

### Iteration 2 execution independence

Executed cold, from committed repository state, in an Execution and
Execution Context distinct from `implementation-001`/`resolution-001`
(both `implementation-exec-chg0018-20260819-01` /
`implementation-context-chg0018-20260819-01`) and from `review-001`
(`review-exec-chg0018-20260819-f27d37ea` /
`review-context-chg0018-20260819-6e5e2500`). This session has no memory
of any of them and read Iteration 1 of this file, `provenance.yml`,
`manifest.yml`, and `protocol/versions/2/specification.md` §10-§11
directly. No claim in `resolution-001`'s own `provenance.yml` statement
or its commit message was accepted without independent reproduction
against the actual generated script, the actual diff, and the actual test
suite. See `provenance.yml` record `review-002` for this execution's own
self-recorded provenance.

Subject: `resolution-001`, frozen at
`7385799030be6562633a87e1e9f468544a14ac3c` (revision
`chg-0018-resolution-001`). `HEAD` at the start of this Iteration is
`75e3678`, whose only difference from the subject is `provenance.yml`
(the `resolution-001` record itself). That is Change-local review-control
metadata, which the §5 effective-workspace freeze permits;
`git status --porcelain` was otherwise clean.

### Resolution Delta, computed independently — no Out-of-Scope Mutation

Computed per §11 as the committed diff between the immutable revision of
the Iteration immediately preceding this one (`review-001`'s subject,
`6214390dc0f36ee982b0ce83185b1eaa08f21d7d`) and this Iteration's own
subject (`7385799030be6562633a87e1e9f468544a14ac3c`) — both already-frozen
historical commits, not the current workspace — minus this Change's exact
`manifest.yml`, `provenance.yml`, and `review.md` paths:

```
$ git diff --name-only 6214390..7385799
.forge/changes/CHG-0018-second-harness-adapter-claude-code/manifest.yml
.forge/changes/CHG-0018-second-harness-adapter-claude-code/provenance.yml
.forge/changes/CHG-0018-second-harness-adapter-claude-code/review.md
src/forge_cli/adapters/claude_code/projection.py
tests/unit/test_claude_code_projection_bundle.py
```

Subtracting the three Change-local paths leaves exactly two:

| # | Resolution Delta path | Covered by declared `scope` |
| --- | --- | --- |
| 1 | `src/forge_cli/adapters/claude_code/projection.py` | yes |
| 2 | `tests/unit/test_claude_code_projection_bundle.py` | yes |

`resolution-001` declares exactly these same two paths as `scope`. The
two sets are **exactly equal** in both directions — no Resolution Delta
path is uncovered, and no declared `scope` entry is broader than the
Delta actually taken. **Out-of-Scope Mutation: none.** Consequently
`full_review_required` is `false` and this Iteration is eligible to be
`status: passed`.

### R001, re-checked against actual repository state — resolved

Not accepted from `resolution-001`'s own claimed verification results.
Generated the real, current hook script directly from source:

```
$ source .venv/bin/activate
$ python3 -c "from forge_cli.adapters.claude_code.projection import _hook_script_content; print(_hook_script_content())"
```

The generated script confirms the root-cause fix `resolution-001`
describes: the two independent whole-string `case` glob patterns are gone,
replaced by a single
`grep -Eq '(sed[[:space:]]+-i|perl[[:space:]]+-i|truncate|>{1,2})[[:space:]]*[^&|;]{0,80}\.forge/changes/[^[:space:]&|;]*(manifest\.yml|provenance\.yml|review\.md)'`
check — the mutation token and the protected path must now be within 80
characters of each other with no `&&`/`||`/`;`/`|` shell separator between
them, rather than each matching independently anywhere in the whole
command string.

Piped real JSON `tool_input.command` payloads to this actual script via
`sh -c` myself (not read from `resolution-001`'s claimed 14-case run):

**Both of `review.md` Iteration 1's originally-demonstrated R001
false-positive commands — now correctly ALLOW:**

```
$ echo '{"tool_input":{"command":"git status > /tmp/status.txt && git add .forge/changes/CHG-0018-x/manifest.yml"}}' | sh check-manifest-edit.sh
(no output, exit 0 — allowed)

$ echo '{"tool_input":{"command":"git commit -m \"docs(chg-0018): note -- see .forge/changes/CHG-0018-x/manifest.yml > also check review.md\""}}' | sh check-manifest-edit.sh
(no output, exit 0 — allowed)
```

**All four originally-denied mutation cases — still correctly DENY:**
`sed -i 's/a/b/' .../manifest.yml`, `perl -i -pe 's/a/b/' .../provenance.yml`,
`truncate -s 0 .../review.md`, and `echo x > .../manifest.yml` all returned
the `permissionDecision: deny` JSON.

**Regression-guard cases (a genuine attack chained with an unrelated
command) — still correctly DENY**, confirming the narrower proximity match
did not become too permissive: `sed -i 's/a/b/' .../manifest.yml && echo
done` and `echo start; sed -i 's/a/b/' .../manifest.yml` both denied — the
`[^&|;]{0,80}` bound in the regex does not cross a `&&`/`;` shell
separator, so a genuine mutation immediately followed or preceded by an
unrelated clause is still caught.

**Iteration 1's originally-sound cases, re-confirmed unchanged (not a
re-review — a regression check on the exact behavior R001 sits next to):**
`git add`, `git commit -m "docs(chg-0018): update manifest.yml"`, `cat`,
`grep`, bare `ls -la`, `git status`, `git diff`, and `git show` against a
protected path all still ALLOW; `sed -i`/redirect against each of
`manifest.yml`/`provenance.yml`/`review.md` individually all still DENY.

**Two additional adversarial probes I designed myself, beyond
`resolution-001`'s own claimed cases, to check for a new false negative
the fix might have introduced:** a legitimate `cat .../manifest.yml >
/tmp/copy.txt` (reading the protected file and redirecting *output*
elsewhere) correctly ALLOWs, since no protected path appears after the
`>` token; and a reordered `sed -i .../manifest.yml -e 's/a/b/'` (file
argument before the edit expression) still correctly DENIEs, since the
`sed -i` token itself is always textually first and the proximity window
still finds the path. I found no case in which the narrower match let a
genuine mutation of a protected path through.

R001 is resolved: the demonstrated false positive is gone, and the fix
does not trade it for a new false negative.

### R002 — OBSERVATION — unrelated latent finding, recorded per C-050 — Core's C-026 freeze check does not exempt an earlier bound Iteration whose subject is properly superseded by a later `resolution_verification` Iteration

**Not targeted by `resolution-001`, not inside the Resolution Delta, and not
counted toward this Iteration's `new_material_findings`** (C-047 scopes
this Iteration's authority to R001, the Resolution Delta, and Out-of-Scope
Mutation; C-050 requires an unrelated Finding discovered incidentally be
recorded, not discarded, and not treated as license to re-audit further).
Recorded here because it is real, demonstrated, and would otherwise go
unrecorded.

**Problem:** `forge validate` currently exits 2:

```
C-026 [.../manifest.yml] C-026 review subject changed after its immutable
revision freeze; create new subject provenance.
```

This is `_validate_protocol2_review_provenance` (`src/forge_cli/validation/
__init__.py:349`) checking, independently for *every* bound Iteration in
`review.iterations`, whether the repository has changed since that
Iteration's own frozen subject commit (excluding this Change's own
`manifest.yml`/`provenance.yml`/`review.md`). For `review-001` specifically
(subject `implementation-001`, frozen at `6214390`, `status: passed`), the
check is satisfied only if nothing outside those three metadata paths has
changed since `6214390` — but `resolution-001` (`7385799`) real-code
Resolution necessarily changed `projection.py` and the test file after that
freeze. The check has no notion of "this earlier Iteration's subject freeze
is now properly superseded by a later, correctly-bound
`resolution_verification` Iteration" (`review-002`, subject
`resolution-001`) — it evaluates each bound Iteration's own freeze in
isolation, so `review-001`'s binding trips regardless of `review-002`
existing. `protocol/versions/2/specification.md` §10-§11 defines exactly
this two-Iteration lifecycle (Iteration 1 passed on a non-blocking Finding,
optional Resolution, `resolution_verification` Iteration 2 verifying it) as
a legitimate path — it does not say an already-`passed` Iteration 1 forbids
a subsequent Resolution — so this reads as an implementation gap in Core's
per-iteration freeze loop, not a Specification violation by this Change's
own artifacts.

**Evidence, reproduced independently, not inferred:** I isolated the
variable by testing three repository states directly with `git stash` /
targeted `git checkout <ref> -- <path>` (restoring cleanly afterward each
time, confirmed via `git status --porcelain`):

1. `.forge/changes/CHG-0018-.../` reset to its state at `6214390` itself
   (pre-`review-001`, `review.iterations: []`, `status: pending`) with `HEAD`
   still at `75e3678`: `forge validate` → **exit 0** (the freeze loop never
   engages because there is no bound Iteration yet).
2. `.forge/changes/CHG-0018-.../{manifest.yml,provenance.yml,review.md}`
   reset to their state at `3d954dd` (`review-001` recorded, `status:
   passed`, no `resolution-001`/`review-002` yet) with `HEAD` still at
   `75e3678` (i.e. the real post-Resolution code): `forge validate` →
   **exit 2, this exact C-026 message** — confirming the finding already
   existed the moment `resolution-001`'s code commit landed, before
   `resolution-001`'s own provenance record or this Iteration's `review-002`
   record were ever written. Not caused by anything I added.
3. The current working tree, with `review-002` added (this Iteration's own
   work): `forge validate` → **exit 2, the identical single C-026 message**
   — my own addition does not introduce a second or different finding; the
   pre-existing one is unchanged in kind or count.

**Impact:** Not a defect in `resolution-001`'s actual diff (the two
in-scope files), and not a defect in R001's fix. It is a real, currently
active block on `forge validate` returning exit 0 for this Change while
`state.current` remains `in_progress` (`protocol/versions/2/specification.md`
§8 lists "the frozen reviewable workspace has changed without renewed
provenance" as a Completion blocker — arguably the intent is already
satisfied here, since provenance *was* renewed via `resolution-001` +
`review-002`, but Core's current per-iteration loop does not recognize
that renewal for the earlier Iteration's own binding). This will need
attention — most likely a Core fix to exempt an earlier bound Iteration's
freeze when a later, validly-bound `resolution_verification` Iteration in
the same `iterations` list already accounts for the delta — before this
Change can reach Completion. It is also possible this resolves itself once
Completion sets `state.current: complete` (the check's own
`st.get("current")!="complete"` guard would then exempt it entirely,
matching every already-`complete` Change I sampled, e.g. `CHG-0016`,
`CHG-0017`) — I could not determine from this repository alone whether
`forge validate` exit 0 is a hard precondition of that step. Either way,
not resolved here, per C-025/C-047: recording it is this Iteration's full
obligation, and the Completion step (outside this Iteration's role) is
where it should next be addressed.

### New Findings introduced by the Resolution

None within `resolution-001`'s own Resolution Delta. `new_material_findings: 0`
for this Iteration's own bounded scope (R001, the Resolution Delta,
Out-of-Scope Mutation) — see R002 immediately above for the one unrelated
latent finding recorded per C-050, which does not count against this field
for the reasons stated there. The Resolution's diff is 27
insertions/10 deletions across exactly the two declared-scope files: a
regex-based rewrite of the hook's matching logic (with an added code
comment documenting R001 and the fix, both read directly) and four new
test cases (two allowed, two denied) added to the existing test's
existing lists. I read the full diff of both files, not only the
production file: the test additions are exactly the four cases the
commit message and `resolution-001` describe, appended to the existing
`denied`/`allowed` lists without altering any pre-existing case in either
list. Nothing else in either file changed.

### Independent mechanical verification

Every figure below was produced by this execution, not read from
`resolution-001`'s own statement or any commit message.

- `python -m pytest -q` → **504 passed** in 38.57s, unchanged from
  Iteration 1's independently-reproduced figure — consistent with a
  behavior-preserving fix plus new test coverage for previously-untested
  cases, not a change in test count.
- All 7 of `resolution-001`'s own headline cases (2 false-positive-now-
  allowed, 4 originally-denied, 1 regression-guard) reproduced directly
  against the actual generated script, plus a second regression-guard
  case and two additional adversarial probes of my own — 12 cases in
  total, all matching expected behavior.
- `git status --porcelain` clean at `75e3678` before this Iteration's own
  writes.
- `forge validate` → **exit 2, one C-026 finding** (see R002 above) — not
  newly introduced by this Iteration, reproduced identically before
  `review-002` existed. Not part of this Iteration's own PASS determination
  per C-047.

### Scope discipline (C-047 / C-050)

No unrelated latent Finding was discovered in this Iteration. For the
record of what was deliberately **not** done: the shared conformance
suite, the Claude Code Driver, C-074, the ADR, the Golden Path Layer C
claim, and every other item in Iteration 1's "Checked and found sound"
section were left alone. Iteration 1 examined them and found them sound;
re-examining them here would be the unrestricted re-audit C-047 forbids.

### Convergence accounting

`new_material_findings: 0`, `full_review_required: false`. There is no
Out-of-Scope Mutation to count, R001 is genuinely resolved with no new
material defect in the fix itself, and no original Finding recurs.
`consecutive_unconverged_verifications` is therefore 0; the Convergence
Limit is not approached and §13 does not engage.

### Verdict

**PASS.**

R001 is resolved in repository state, re-verified directly against the
actual generated hook script rather than accepted from `resolution-001`'s
own claim. The Resolution Delta contains no Out-of-Scope Mutation, and
the declared Resolution Scope is exact in both directions. The fix
narrows the false-positive surface (both of Iteration 1's demonstrated
false-positive commands now correctly allow) without widening the
false-negative one (every originally-denied case, plus two chained-attack
regression guards and two of my own adversarial probes, still correctly
deny). The full test suite is unchanged at 504 passed. This Change
remains **PASS** and this Resolution may stand as recorded. One unrelated
latent finding (R002, a Core validation gap, non-blocking to this
Iteration's own scoped verdict per C-047) was discovered incidentally and
is recorded per C-050 rather than pursued further here.

