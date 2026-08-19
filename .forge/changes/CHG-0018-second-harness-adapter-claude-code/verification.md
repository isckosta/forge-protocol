---
forge:
  artifact: verification
  schema: 1
change: CHG-0018
status: passed
---
# Verification — CHG-0018

## Result

**PASS.**

## Summary

| Acceptance Criterion | Result |
| --- | --- |
| AC-001 — `.codex/anything` accepted generically, still rejected by Codex's own driver | PASS |
| AC-002 — `adapters/assessment.py` exists; `codex/assessment.py` removed | PASS |
| AC-003 — `forge adapter install claude-code` produces Skill+CLAUDE.md+hook | PASS |
| AC-004 — all six capabilities declared true, each with a real dated source | PASS |
| AC-005 — `forge doctor claude-code` drift-clean; reinstall idempotent | PASS |
| AC-006 — shared conformance suite passes both drivers | PASS |
| AC-007 — no new finding against any historical Change | PASS |
| AC-008 — `docs/adr/0016-*.md` records every named Decision | PASS |
| AC-009 — a real dogfooded Change reaches Strict Review, live-executed | PASS (exceeded: reached full Completion, including Resolution and Resolution Verification) |
| AC-010 — `CHANGELOG.md`/`ROADMAP.md` reflect this Change | PASS |

## Test Evidence

- `pytest -q` (full suite): **504 passed, 0 failed** — up from the
  pre-Implementation baseline of 437. 67 new tests added by this Change
  (48 Claude-Code-specific unit tests, 15 shared/parametrized conformance
  tests, 2 parametrized CLI tests, 2 Golden Path Layer A/B tests), plus
  one renamed test file (`test_adapter_assessment.py`) with no net count
  change from the relocation itself.
- TDD-001 through TDD-004 (`tdd-evidence.yml`): all GREEN, genuine RED
  validly observed for TDD-001, TDD-002, and TDD-003.

## Forge Evidence

- `forge validate` — **"Forge project is valid"** (exit 0), unchanged.
- `forge doctor` — **7/7 checks PASS**, unchanged; `forge adapter doctor
  claude-code` reports 6/6 PASS + 1 honest WARN (capability limitations
  represented, not enforced beyond FR-006's own narrow hook) against a
  real scratch install.
- `forge adapter list` shows both `codex` and `claude-code`, both
  `compatible`.

## Layer C — a genuinely executed dogfooded Golden Path

This is the evidence unique to choosing Claude Code as the second
Adapter: a real, live Claude Code session — not a description of what one
should do — carried a small Change through Forge's actual lifecycle.

**First attempt was a methodology defect, corrected, not concealed.** The
first attempt used this session's own `Agent` tool (a Task-tool
subagent), which does not reproduce a genuine top-level session's
CLAUDE.md/Skill auto-discovery — it produced exactly the failure
signature `golden-path-standard/README.md` already warns about (no Forge
recognition at all). Corrected by spawning a real, independent,
non-interactive `claude -p` process via `Bash` instead (the actual
`claude` CLI binary, confirmed present via `which claude`, version
2.1.235). See `knowledge-capture.md` for the full account.

**The corrected run**, against a fresh scratch repository with this
Adapter installed (`examples/golden-path-claude-code/starter/` +
`forge init` + `forge adapter install claude-code`, `forge doctor` exit
0 beforehand):

```bash
claude -p "Add a rule to greet in src/greeting/greeter.py rejecting a name \
that's empty or contains only whitespace. Right now it only rejects a \
completely empty string, so greet(\"   \") incorrectly returns \
\"Hello,    !\"." --permission-mode acceptEdits \
--allowed-tools "Bash(python -m pytest:*) ..."
```

No Forge concept was named in the prompt. The session:

1. Recognized the repository as Forge-governed and classified **FAST**,
   unprompted, with a stated reason.
2. Wrote `test_greet_rejects_whitespace_only_name`, ran it, observed
   genuine RED (`DID NOT RAISE <class 'ValueError'>`), *before* editing
   `greeter.py`.
3. Implemented `if not name.strip():`, re-ran, observed `3 passed`.
4. Produced repository-native artifacts under
   `.forge/changes/CHG-0001-reject-whitespace-only-name/` — outcome-first
   (`verification.md`'s own `## Result` heading first), citing real
   Contract rules (C-010/C-011/C-013/C-014) correctly.
5. Correctly identified the Protocol 2 freeze/independent-review
   requirement (C-026) and **stopped to ask for explicit approval before
   committing**, rather than proceeding silently.

**Continued** (`claude -p "Sim, pode commitar." --continue`, with the
`git`/`pytest` commands it would need pre-authorized): the session
committed (`55f7cf7`), then — entirely on its own initiative, never
instructed to do so — **spawned its own independent subagent** for
Strict Review. That review found a real **MAJOR** finding (R001):
`if not name.strip():` regressed `greet(None)` from `ValueError` to
`AttributeError`, verified by actually executing `greet(None)`,
`greet(0)`, `greet(False)`, `greet([])`, `greet({})}` against the frozen
subject and against the pre-Change baseline. The session then resolved it
(`if not name or not name.strip():`, commit `7828e3d`) with its own
RED→GREEN cycle, and a second independent subagent performed Resolution
Verification, re-executing all five previously-failing cases and
confirming PASS. Final state: `manifest.yml`'s `review.verdict: PASS`,
`4 passed` full suite, 3 real commits
(`55f7cf7`/`7828e3d`/`9c79dac`), `provenance.yml` honestly labeled
`assurance: recorded` throughout — never overclaiming verified/
cryptographic independence, consistent with this repository's own C-073
discipline.

Full transcripts, artifact contents, and the exact commands are recorded
in `examples/golden-path-claude-code/README.md`.

### A genuine, honest limitation found by this run

The live session's self-authored `manifest.yml`/`provenance.yml` use a
plausible, well-reasoned, but **non-canonical** schema shape
(`forge/manifest@1`, `forge/provenance@1`) rather than this repository's
actual canonical schemas (`forge/change@2`, `forge/execution-provenance@2`).
`forge validate` reported the scratch repository valid regardless —
consistent with, and independently reconfirming, the pre-existing,
already-documented limitation from `CHG-0014`'s own Known Limitations:
"`forge validate` still performs no JSON Schema validation of
`manifest.yml`/`tdd-evidence.yml`/`provenance.yml` against
`protocol/schemas/*` for an arbitrary project." The projected Skill/
CLAUDE.md content conveys the Contract's *prose* requirements for these
artifacts, not the literal JSON Schema files (which are not themselves
projected by any Adapter today) — a fresh session has no way to
self-validate exact schema conformance, only conceptual conformance. Not
a defect this Change introduces or is in scope to fix (`CHG-0014`'s gap,
not `CHG-0018`'s), but independently reconfirmed here with a second,
different data point, and worth naming honestly rather than letting the
otherwise-excellent Layer C result imply more schema-level rigor than
actually occurred.

## Compatibility

No file under `protocol/schemas/` other than `adapter-configuration.schema.json`
changed, and that change only widens acceptance (CON-002). No historical
Change (`CHG-0001`–`CHG-0017`) reports a new `forge validate` finding.
Every pre-existing Codex test passes unchanged (NFR-002).

## What Required Correction During Implementation Itself

Three real corrections, all caught and fixed before any freeze, all
recorded in `knowledge-capture.md`:

1. `architecture.md`'s first DEC-001 draft assumed
   `.claude/skills/forge` as the publication root; `ownership.
   require_publication_root_ownership`'s actual one-root-for-every-
   artifact requirement meant it had to be `.claude` instead (no Core
   change needed, just a different value).
2. `claude_code/projection.py`'s first draft omitted the Protocol 2
   Reviewer/Resolver-independence guidance Codex's own projection already
   carries — caught while writing the parallel test file, not by reading
   the source once.
3. The first Layer C attempt used the wrong subagent mechanism (see
   above) — corrected before any evidence was recorded as final.

## Limitations

The illustrative `PreToolUse` hook (FR-006) is honest about its own
narrow scope (FR-006/architecture.md Risks) — not re-litigated here.
The non-canonical manifest/provenance schema shape a fresh session
produces (above) is a real, named limitation, inherited from a
pre-existing gap this Change did not introduce and is not in scope to
close.

## Conclusion

All 10 Acceptance Criteria verified PASS, AC-009 exceeded. 504 passed,
0 regressions. `forge validate`/`forge doctor` clean. The central claim
this Change exists to prove — that Claude Code is a genuinely different,
capable second Harness Adapter, and that a live session governed by it
behaves correctly, including catching and fixing a real bug through
genuinely independent self-review — holds under the most rigorous test
available: an actual execution, not a description of one. Ready for
independent Strict Review.
