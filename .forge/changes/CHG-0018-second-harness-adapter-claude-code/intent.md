# Intent — Second Harness Adapter (Claude Code)

## Summary

Forge has exactly one concrete Harness Adapter (Codex). `ROADMAP.md`'s
"Second Harness Adapter" milestone (Gate D: "at least two concrete Harness
Adapters demonstrate the generic Core boundary") requires a second,
materially different one, naming Claude Code as the strong candidate. This
Change adds `src/forge_cli/adapters/claude_code/`, a Claude Code Harness
Adapter that reuses the existing generic Adapter Core, and — because I am
Claude Code — lets this repository dogfood a genuine, fully-automated
Golden Path (through the actual point a live Harness session behaves,
Layer C) for the first time, something the existing Codex Golden Path
structurally cannot do without a human operating Codex.

## Problem

The generic Adapter Core (`AdapterService`, `AdapterRegistry`,
`ownership.py`, `state.py`, `plan.py`, `planner.py`, `publisher.py`,
`capabilities.py`, `manifest.py`, `validation.py`, `diagnostics.py`,
`repository.py`, `adapter_cli.py`) has never been exercised by a second
concrete Adapter. `ADR-0006` deliberately deferred building even the first
Adapter in the same Change as the Core abstraction, "so that no specific
Harness shapes this Core abstraction prematurely" — but the inverse risk,
that the Core is *accidentally* Codex-shaped without anyone having
verified it, has never been tested either. Two real leaks of Codex-only
logic into the nominally-generic Core were found during Discovery for this
Change (Explore research, 2026-08-19):

- A `.codex` reserved-path rule hardcoded in the generic
  `adapters/configuration.py:58-59` and in the generic
  `protocol/schemas/adapter-configuration.schema.json:14` (whose regex
  additionally has a latent unescaped-`.` bug, matching `Xcodex` too) —
  not scoped to Codex at all, even though `codex/targets.py:36` already,
  correctly, has its own copy.
- `codex/assessment.py`'s `assess_invariant`/`to_generic_limitation` are
  100% generic (zero Codex references) but live under the Codex package,
  which would force a second Adapter to either duplicate them or import
  across Adapter packages — a layering violation.

Both are exactly the kind of Core pollution the ROADMAP's stated
Architecture Test ("not merely whether the second Adapter works, but
whether it can be implemented without introducing vendor-specific concepts
into the generic Adapter Core") warns against, and both predate this
Change.

## Desired Outcome

`forge adapter install claude-code` works end-to-end against a real
repository. The Claude Code Adapter's `adapter.yml`/`capabilities.yml`
truthfully reflect Claude Code's actual, currently-documented capabilities
(dated evidence, fetched live for this Change) — a materially richer
profile than Codex's (Claude Code supports hooks, subagents, persistent
CLAUDE.md instructions, and slash commands; Codex declares only skills and
generated files). The generic Core requires zero new vendor-specific
concepts to support it; the two pre-existing leaks above are fixed as part
of proving that. A shared conformance test suite exercises both Adapters.
I then dogfood a real Change through the installed Adapter myself, as the
live Harness, producing genuine repository-native Layer C evidence no
prior Change in this repository has been able to produce.

## Scope

- `src/forge_cli/adapters/claude_code/` — descriptor, evidence, targets,
  driver, projection, packaged resources (`adapter.yml`, `capabilities.yml`,
  `publication.yml`, skill template).
- Three real projection mechanisms: a Skill (`.claude/skills/forge/`,
  primary, full workflow content — mirrors Codex), a CLAUDE.md pointer
  (secondary, minimal, per Claude Code's own documented best practice),
  and one narrow, safe, illustrative `PreToolUse` enforcement hook
  (tertiary — Claude Code's one genuinely enforcement-capable mechanism,
  which Codex structurally cannot offer).
- Registration in `adapters/packaged.py`.
- Fixing the two pre-existing Core leaks named above.
- A new shared/parametrized conformance test suite exercising both
  Adapters, plus Claude-Code-specific test parity with the ~15 existing
  Codex-specific test files.
- A new ADR recording the Harness-selection Decision (dated capability
  evidence) and the three-mechanism design.
- A dogfooded Golden Path scenario, executed by me as the live Harness.

## Out of Scope

- Any change to `AdapterProjectionContext`'s existing fields
  (`artifact_structure_content`, `interaction_language`) — both were
  already designed generically by `CHG-0016`/`CHG-0017` for exactly this
  moment.
- A third Harness Adapter, or any change to Codex's own behavior beyond
  the two Core-leak fixes (which affect Codex only by relocating already-
  generic logic and removing a redundant, now Codex-owned-only check from
  the generic layer).
- The ROADMAP's separate "End-to-End Examples & External Validation"
  milestone (Laravel/PHP, Node/TS, Python, monorepo, legacy-repository
  matrix) — still deferred, per the earlier scoping decision.
- Any MCP-server Adapter mechanism, even though Claude Code documents MCP
  support — outside the six-capability vocabulary `adapter.schema.json`
  already fixes, and not required to prove Harness independence.

## Success Criteria

See `specification.md` for concrete Acceptance Criteria. At Intent stage,
success means: the generic Core needs no vendor-specific addition to
support Claude Code; both Adapters pass a shared conformance suite; and a
real, dogfooded Change reaches at least Strict Review through the
installed Claude Code Adapter, produced by a live Claude Code session
(this one) rather than simulated.
