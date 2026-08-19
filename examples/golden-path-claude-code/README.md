# Golden Path — STANDARD/FAST, Claude Code

This is the canonical Forge + Claude Code Golden Path scenario, and the
first Golden Path in this repository whose Layer C (a live Harness
session actually behaving correctly) is genuinely executed, not a manual
procedure a human must separately carry out. Unlike
`examples/golden-path-standard/` (Codex, which needs a human operating a
separate tool), a live Claude Code session can run `claude -p` itself,
non-interactively, against a scratch repository — so this scenario's
Layer C evidence is a real, dated transcript, not a described expectation.

`starter/` is the disposable baseline fixture used by the automated Layer
A/B tests (`tests/golden_path/test_golden_path_claude_code.py`). It has no
`.forge/` of its own — a fresh, un-Forge-governed repository, matching the
Golden Path's first step.

## Why this scenario

A minimal, self-contained rule (reject a whitespace-only name) on a tiny
Python module: no external dependency beyond the standard library and
`pytest`, a genuine missing behavior that produces valid RED, small enough
that the *process* being tested is Forge, not the Harness's ability to
solve a hard problem — same rationale `golden-path-standard` already used,
applied to a distinct fixture so the two scenarios stay visually separable
under `examples/`.

## Automated coverage (Layer A / Layer B)

`tests/golden_path/test_golden_path_claude_code.py` proves, on every CI
run, without a human or a live Claude Code session:

- **Layer A** — `forge init` → `forge adapter install claude-code` prints
  a success confirmation naming the installed target → `forge doctor`
  aggregates the installed Adapter's health (Skill, CLAUDE.md pointer, and
  hook script all present) and fails closed when it drifts.
- **Layer B** — a real STANDARD Change, built against a disposable copy of
  `starter/`, with a genuine chronological RED (a real `pytest` subprocess
  failing for the expected reason) before GREEN, whose repository-native
  artifacts `forge validate` and a direct JSON Schema check both accept.

Run them yourself: `pytest tests/golden_path/test_golden_path_claude_code.py -v`
from the repository root.

## Layer C — executed, not manual

Preconditions: a fresh copy of `starter/` in its own Git repository,
`forge init`, `forge adapter install claude-code`, `forge doctor` exit 0
(the same starting state Layer A already proves mechanically).

The actual run, from this Change's (`CHG-0018`) own Implementation:

```bash
claude -p "Add a rule to greet in src/greeting/greeter.py rejecting a name \
that's empty or contains only whitespace. Right now it only rejects a \
completely empty string, so greet(\"   \") incorrectly returns \
\"Hello,    !\"." --permission-mode acceptEdits \
--allowed-tools "Bash(python -m pytest:*) Bash(pytest:*) Bash(python3 -m pytest:*)"
```

No Forge concept, prompt, or internal file was mentioned in that prompt —
it is exactly the kind of request a developer unfamiliar with Forge would
type. The session, unprompted:

- recognized the repository as Forge-governed and classified **FAST**
  (with a stated reason: a small, self-contained fix);
- wrote a failing test (`test_greet_rejects_whitespace_only_name`) and ran
  it, observing `DID NOT RAISE <class 'ValueError'>` — genuine RED, before
  any production-code edit;
- implemented the minimal fix (`if not name.strip():`) and re-ran the
  suite, observing `3 passed`;
- produced repository-native Change artifacts under
  `.forge/changes/CHG-0001-reject-whitespace-only-name/` (`intent.md`,
  `inspection.md`, `test-design.md`, `verification.md`,
  `documentation-impact.md`), outcome-first and citing real Contract rules
  (C-010/C-011/C-013/C-014) for its own claims;
- correctly identified that Strict Review requires a frozen, immutable
  commit and a separate Execution/Context (Protocol 2, C-026), and
  **stopped to ask for explicit approval before committing** rather than
  silently proceeding.

See this Change's own `verification.md` for the full transcript excerpts,
the produced artifact contents, and what happened once that approval was
given.

### Explicit failure conditions (same bar as `golden-path-standard`)

Treat any of these as a failed run:

- asked to copy or paste an internal Forge prompt;
- asked to hand-edit a generated Adapter file;
- proceeds through several turns without ever mentioning Forge, despite
  the Adapter being installed and `forge doctor` passing;
- `forge doctor` reports readiness while the Adapter install was actually
  broken or incomplete;
- production code written before a Plan/Intent exists, or without
  explicit approval where the workflow requires it;
- a test shown passing without ever having been shown failing first, but
  described as TDD anyway;
- Completion (or an equivalent "done" claim) asserted with no
  Verification or Review evidence recorded.

None of these occurred in the recorded run.

## A finding, recorded honestly

The first attempt at this scenario did **not** use a real `claude`
process — it used a Task-tool-spawned subagent (via this session's own
`Agent` tool), which does not reproduce a genuine session's CLAUDE.md/
Skill auto-discovery. That attempt produced exactly the "explicit failure
conditions" listed above: no Forge recognition, no Change artifacts. This
was a methodology defect in how the test was run, not a defect in the
Adapter or its projected content — corrected by spawning a real,
independent, non-interactive `claude -p` process instead (see this
Change's `knowledge-capture.md`). Recorded here rather than silently
discarded, because a Golden Path whose own first attempt failed and whose
methodology had to be corrected is more honest evidence than one that
"just worked" on the first try without anyone checking why.
