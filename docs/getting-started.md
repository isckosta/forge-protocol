# Getting Started

This is the fastest path from "nothing installed" to "Codex is ready to
receive a Change request" in a real Git repository. It assumes no prior
knowledge of Forge's internal architecture.

You should not need `ARCHITECTURE.md`, `protocol/specification.md`,
`protocol/contract/*`, Adapter internals, or Change schemas to complete this
page. Links to those are at the end, for when you want to go deeper.

## 1. Install Forge

Forge is pre-release software. From a clone of this repository:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
forge version
```

(Once Forge publishes to a package index, this step becomes a normal
`pip install`/`pipx install`. Nothing else on this page changes.)

## 2. Initialize your repository

From the root of any Git repository you want Forge to govern:

```bash
forge init
```

This creates `.forge/` at your repository root — Forge's own workspace —
even if you run it from a nested directory. It requires Git and fails
clearly if Git isn't available or you aren't inside a Git repository.

## 3. Install the Codex Adapter

```bash
forge adapter install codex
```

This shows you a plan (which files it will create), then publishes a
Forge-native Codex skill under `.agents/skills/forge/`. You will see a
confirmation line naming the installed location, followed by the next step
to take. You do not need to open or edit anything it generated.

Run it again any time — it is idempotent. If you ever want to preview what
it would do without changing anything, use `forge adapter plan codex` or
`forge adapter install codex --dry-run`.

## 4. Confirm your repository is ready

```bash
forge doctor
```

This reports on your Forge workspace *and* every installed Adapter's
health (configuration, Protocol compatibility, installation state, drift,
conformance, and any capability limitations) in one command. A clean exit
code (`0`) means you're ready for step 5. A non-zero exit code names exactly
which check failed and what to run to fix it — you never need to guess.

## 5. Open Codex

Open Codex in this same repository. The installed skill is discovered
automatically; you do not copy or paste any prompt.

## 6. Ask for a Change, in your own words

Describe what you want, e.g.:

> Add a rule to `create_username` in `src/accounts/users.py` rejecting
> usernames shorter than three characters.

You don't need to say "STANDARD Flow" or mention any Forge terminology.
Classification, Flow selection, and lifecycle stage names are Forge's job,
not yours.

## 7. What happens next

For an ordinary small feature (Forge's STANDARD Flow), expect roughly this
shape:

```text
Intent -> Discovery -> Specification -> Plan
    -> [ stop, and ask you to approve before writing code ]
    -> TDD (a failing test first, then the minimal fix)
    -> Verification -> Strict Review -> Documentation -> Completion
```

The important part: **after Plan, Forge should stop and ask you to approve
before Implementation begins.** If it starts writing production code before
that, that's a defect worth reporting, not something to accept.

Everything durable lives in your repository under `.forge/changes/<id>/`,
not only in the chat transcript — you can inspect it, and it survives
closing the chat.

### Known limitation

Forge's canonical Flow definitions declare this Plan → stop → approval →
Implementation boundary as an artifact-completeness precondition (Intent,
Discovery, Specification, and Plan must all be complete first), and the
installed Codex skill now states it explicitly. Neither Forge's Core
Protocol nor the CLI mechanically *enforces* a human approval act today the
way it enforces, for example, independent Strict Review under Protocol 2.
Treat it as a strongly represented expectation you should hold your Harness
to, not yet a technical guarantee Forge can prove on its own. See
`.forge/changes/CHG-0014-golden-path-codex-onboarding/discovery.md` for the
full analysis.

## Where to go deeper

- `README.md` — what Forge is and the full CLI surface.
- `ARCHITECTURE.md` — component boundaries and configuration resolution.
- `protocol/specification.md` — the full Core Protocol.
- `examples/golden-path-standard/` — a complete worked example, including a
  scripted acceptance procedure you can run yourself.
