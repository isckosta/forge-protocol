# Golden Path — STANDARD, Codex

This is the canonical Forge + Codex Golden Path scenario: prove that a
developer unfamiliar with Forge can install it, initialize a repository,
install the Codex Adapter, confirm readiness, and carry one small behavioral
Change through Forge's real STANDARD lifecycle, ending at (but not
past) the point this repository's own Protocol 2 requires independent
Strict Review.

`starter/` is the disposable baseline fixture used by both the automated
Layer A/B tests (`tests/golden_path/test_golden_path_standard.py`) and this
manual procedure. It has no `.forge/` of its own — it is deliberately a
fresh, un-Forge-governed repository, matching the Golden Path's first step.

## Why this scenario

A minimal, self-contained rule (username length validation) on a tiny
Python module: no external dependency beyond the standard library and
`pytest`, a genuine missing behavior that produces valid RED, and small
enough that the *process* being tested is Forge, not the Harness's ability
to solve a hard problem (see the originating brief, §8).

## Automated coverage (Layer A / Layer B)

`tests/golden_path/test_golden_path_standard.py` already proves, on every
CI run, without a human or a live Codex session:

- **Layer A** — `forge init` → `forge adapter install codex` prints a
  success confirmation naming the installed target → `forge doctor`
  aggregates the installed Adapter's health and fails closed when it drifts.
- **Layer B** — a real STANDARD Change, built against a disposable copy of
  `starter/`, with a genuine chronological RED (a real `pytest` subprocess
  failing for the expected reason) before GREEN, whose repository-native
  artifacts (`manifest.yml`, `tdd-evidence.yml`, Plan preceding
  Implementation) `forge validate` and a direct JSON Schema check both
  accept.

Run them yourself: `pytest tests/golden_path/ -v` from the repository root.

## Manual acceptance procedure (Layer C)

This is the one layer automated tests cannot cover: whether a real Codex
session, given the installed projection, actually behaves correctly. No
step below depends on Codex's exact wording — every expected outcome is
behavioral.

### Preconditions

- Forge installed in a Python 3.12+ virtual environment
  (`docs/getting-started.md` steps 1–2 already done against a scratch copy
  of `starter/`, not against this repository itself).
- Codex available and able to open a local repository.
- No prior Forge or Codex state in the scratch copy.

### Starting state

A fresh copy of `examples/golden-path-standard/starter/` in its own Git
repository:

```bash
cp -r examples/golden-path-standard/starter /tmp/golden-path-manual
cd /tmp/golden-path-manual
git init -q && git add -A && git commit -q -m "baseline"
```

### Steps

1. `forge init`
2. `forge adapter install codex`
3. `forge doctor` — confirm exit code `0` before continuing.
4. Open Codex in `/tmp/golden-path-manual`.
5. Ask, in your own words: *"Add a rule to `create_username` in
   `src/accounts/users.py` rejecting usernames shorter than three
   characters."*

### Expected behavioral milestones

- Codex recognizes the repository as Forge-governed without you pasting
  anything — it should reference Forge concepts (Change, Flow, Intent) on
  its own.
- It classifies a Flow (STANDARD is expected for this scenario's size) and
  states which one, with a reason.
- A repository-native Change appears under `.forge/changes/` before
  Implementation — inspect `intent.md` and (once produced)
  `specification.md`/`plan.md`.
- After producing a Plan, it **stops and asks you to approve** before
  writing production code. It must not silently proceed.
- Once you approve, it writes a failing test **before** the fix, runs it,
  and shows you that it failed for the right reason — before writing the
  fix itself.
- After the fix, it re-runs tests and shows them passing.
- It records Verification, then either performs Strict Review or —
  correctly, under this repository's Protocol 2 rules if the scratch
  repository was also initialized at Protocol 2 — explains that Review
  requires a separate session/context and names that as the next step,
  rather than reviewing its own work.
- Nothing it does requires you to open, read, or edit
  `.agents/skills/forge/` yourself.

### Explicit failure conditions

Treat any of these as a failed run, and record it as a Golden Path finding:

- You are asked to copy or paste an internal Forge prompt.
- You are asked to hand-edit a generated Adapter file.
- Codex proceeds through several turns without ever mentioning Forge,
  despite the Adapter being installed and `forge doctor` passing.
- `forge doctor` reported readiness while the Adapter install was actually
  broken or incomplete.
- Implementation (production code) is written before a Plan exists, or
  without your approval.
- A test is written and shown passing without ever having been shown
  failing first, but is described as TDD anyway.
- Completion (or an equivalent "done" claim) is asserted with no
  Verification or Review evidence recorded.
- You needed to read `protocol/` or `ARCHITECTURE.md` to understand what to
  do next at any point.

### Evidence to inspect

`/tmp/golden-path-manual/.forge/changes/<id>/` — every artifact Codex
produced, plus `.forge/adapters/codex/installation.yml` for the Adapter's
own installation record. Keep or discard the scratch directory afterward;
nothing under it is part of this repository.
