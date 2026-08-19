# Discovery — Second Harness Adapter (Claude Code)

## Executive Summary

Two Explore agents traced the entire Codex Adapter architecture and the
generic Adapter Core; live doc research (code.claude.com, 2026-08-19)
established dated Claude Code capability evidence. Findings below resolve
every open design question the originating plan deferred to this stage,
with real citations rather than assumption.

## Repository State at Investigation Time

HEAD: `023649a` (`docs(chg-0017): Completion`). `docs/adr/` highest number
`0015`; next free is `0016`. `protocol/specification.md` §34–38 already
speak in Adapter-plural, harness-neutral language (§34: "Initial ownership
modes are `forge_owned`, `user_owned`, and `shared`"; capability
vocabulary already lists all six names generically) — written before any
concrete Adapter existed (ADR-0006 predates Codex), so **no Specification
change is anticipated** for this Change; confirmed, not assumed, by
reading all five sections in full.

## Generic Core: two real pre-existing leaks (fix scope, per your answer)

1. **`.codex` hardcoded in the generic Core, three places**:
   `adapters/configuration.py:58-59` (`_checked_target`, used for *any*
   adapter's `.forge/adapters/<id>/config.yml`),
   `protocol/schemas/adapter-configuration.schema.json:14` (generic
   schema; regex `(?!.codex(?:/|$))` has an unescaped `.` — also matches
   `Xcodex`, a real latent bug beyond the vendor-leak itself), and
   `codex/targets.py:36` (Codex's own copy — correctly scoped, stays).
   Fix: strip the vendor literal from the first two; Codex's own
   `validate_publication_root` keeps its existing, now-sole `.codex`
   reservation.
2. **`codex/assessment.py`** (`assess_invariant`, `to_generic_limitation`)
   is 100% generic (only import: `adapters.capabilities.CapabilityLimitation`;
   zero Codex references). Fix: move to `adapters/assessment.py`; update
   `codex/driver.py`'s import. Pure relocation, verified by the unchanged
   Codex suite passing after the move.

Test impact: `tests/unit/test_adapter_configuration.py:200`'s
`test_invalid_or_forbidden_target_is_rejected` parametrize list currently
includes `.codex/forge` in the same set as unsafe/cross-platform cases —
this specific case moves to a new Codex-specific test (no equivalent
Codex-level test currently exists for it at all, confirmed by grepping
`tests/unit/test_codex_publication_targets.py`, which only covers
generic path-safety, never `.codex` itself).

## `AdapterProjectionContext` needs no new field

`artifact_structure_content` (`CHG-0016`) and `interaction_language`
(`CHG-0017`) were both deliberately designed generically in anticipation
of this Change (`CHG-0017/architecture.md` Risks section, quoted in
Intent). Confirmed: both fields carry through `ClaudeCodeDriver.project()`
exactly as they do for `CodexDriver`, no Core signature change required.

## `HarnessDriver` Protocol and registration are already generic

`AdapterService` (`service.py`) has zero Codex branches — every method
dispatches through `registry.get(adapter_id)` and the four-member
`HarnessDriver` Protocol (`manifest`, `default_target`,
`validate_publication_root`, `project`). `adapter_cli.py` takes
`adapter_id` as a free-form string; `forge adapter install claude-code`
is already a generically valid invocation today, failing only with
`E_FORGE_ADAPTER_UNKNOWN` because `adapters/packaged.py`'s
`build_packaged_registry()` only instantiates `CodexDriver()`. Adding
`ClaudeCodeDriver()` to that one tuple is the entire registration step.

## Ownership mechanics for the CLAUDE.md and hook mechanisms — resolved without a Core change

`driver.project()` is a pure function of `AdapterProjectionContext` (no
repository read access). `OwnershipMode.SHARED` (`ownership.py`) requires
the *caller* to already have computed a `merge_result` — which needs
current on-disk content `project()` cannot see. Making SHARED usable here
would require extending `AdapterProjectionContext` with observed-content
read access — exactly the kind of Core-signature change the ROADMAP asks
to be wary of introducing without strong justification, for a mode
(`SHARED`) that has never been exercised by any real Adapter (`planner.py`
fully implements it, mechanically, but nothing in this repository's
history has ever produced a `merge_result`). **Avoided entirely**, for
both new mechanisms, by choosing paths that need no merge at all:

- **CLAUDE.md pointer**: publish to `.claude/CLAUDE.md` — a real,
  independently-documented, equally-valid project CLAUDE.md location
  (`code.claude.com/docs/en/memory`: *"A project CLAUDE.md can be stored
  in either `./CLAUDE.md` or `./.claude/CLAUDE.md`"*), distinct from the
  conventional root `./CLAUDE.md` every doc example uses. `forge_owned`,
  reusing the exact same, already-safe, already-tested ownership
  machinery Codex's `SKILL.md` already relies on — collision (an existing
  `.claude/CLAUDE.md` with unrecognized content) safely reports CONFLICT,
  never silently overwrites, exactly like any other `forge_owned` file
  today. Zero Core change.
- **Hook**: `code.claude.com/docs/en/hooks` documents that `SKILL.md`
  frontmatter itself supports a `hooks:` field (event name, `matcher`,
  `command`, and an `once` option meaningful only there) — hooks
  "registered when you or Claude invoke the skill" and "remain active for
  the rest of the session." This means the hook lives **inside the
  already-`forge_owned` Skill tree** (`SKILL.md`'s own frontmatter, plus a
  script file under `.claude/skills/forge/hooks/`) — no separate
  `.claude/settings.json` merge problem at all, since Forge never touches
  a file it doesn't already fully own. Zero Core change. Honest,
  documented limitation: the hook is only active once the Skill has been
  invoked at least once in a session, not from session start — recorded
  explicitly, not glossed over (matches this repository's own C-073
  discipline).

Both resolutions are recorded as Architecture-stage Decisions
(`architectural` class, `autonomous_decision`) rather than assumed here —
Discovery found the facts; Architecture owns the resolution formally.

## `DEC-Skill-Sharing`: not extracted in this Change

The originating plan flagged whether Codex's and Claude Code's SKILL.md-
rendering logic should share a generic renderer, since both use the
identical `SKILL.md` + `references/*` shape. Discovery finds they diverge
at exactly the point Claude Code's own hook mechanism requires: Claude
Code's `SKILL.md` frontmatter needs a `hooks:` block Codex's never will
(Codex declares `hooks: false`). "Structurally nearly identical" was true
before this Discovery, less true after it. Recommendation, resolved at
Architecture: **do not extract a shared renderer in this Change** —
duplicating a real but now-diverging ~150-line renderer is a smaller,
safer risk than refactoring Codex's already-shipped, already-reviewed
projection code inside the same Change that introduces a materially new,
higher-risk component (the hook mechanism, and the first-ever real use of
a second Adapter package). Revisitable as its own future Change once two
real implementations make the actual (not assumed) duplication visible.

## Dated Claude Code capability evidence (fetched live, 2026-08-19)

| Capability | Status | Source | Key fact |
| --- | --- | --- | --- |
| `skills` | supported | `code.claude.com/docs/en/skills` | `.claude/skills/<name>/SKILL.md`, on-demand or `/name`-invoked, bundled reference files |
| `generated_files` | supported | `code.claude.com/docs/en/overview` | "reads your codebase, edits files, runs commands" |
| `persistent_instructions` | supported | `code.claude.com/docs/en/memory` | `CLAUDE.md`, "read at the start of every session"; explicitly "context... not enforced configuration" |
| `hooks` | supported | `code.claude.com/docs/en/hooks` | `PreToolUse` can genuinely block (exit 2 / JSON `permissionDecision: deny`); only enforcement-capable mechanism of the six |
| `agent_roles` | supported | `code.claude.com/docs/en/overview` | subagents, `.claude/agents/*.md` |
| `commands` | supported | `code.claude.com/docs/en/skills` | slash commands, now unified with skills, still a distinct declared capability |

All six `true` — the materially different profile from Codex's
(`skills: true, generated_files: true`, all others `false`) the ROADMAP's
Architecture Test needs a *materially different* Harness to exercise.

## Flow Classification Finding

Touches: `adapters/configuration.py` + its schema (Core fix), a new
`adapters/assessment.py` (Core fix/relocation), a new Adapter package with
executable code, new Contract obligation (shared conformance suite,
pending final Specification confirmation), and a new ADR. Same combination
class (Protocol/Contract-adjacent + executable Core + new package) that
classified `CHG-0013`/`CHG-0015`/`CHG-0016`/`CHG-0017` as **FULL**.

## Documentation Impact Signal (preliminary)

Expected: `CHANGELOG.md`, `ROADMAP.md` (flip "Second Harness Adapter"
status), new ADR-0016, possibly one new Contract rule (final Specification
confirmation pending — see above). `docs/getting-started.md` likely gains
a `forge adapter install claude-code` mention alongside the existing Codex
one, confirmed/declined at Documentation Impact evaluation.

## Open Questions Requiring Decision — all resolved in Discovery, owned formally at Architecture

- CLAUDE.md ownership mechanism → `.claude/CLAUDE.md`, `forge_owned`, no
  Core change (architectural, autonomous).
- Hook mechanism and exact invariant → Skill-frontmatter-scoped
  `PreToolUse` hook blocking direct shell mutation of
  `.forge/changes/*/{manifest.yml,provenance.yml,review.md}` (review-
  control metadata integrity — a real, narrow, C-026/C-016-adjacent
  invariant Codex cannot enforce at all), no Core change (architectural,
  autonomous).
- `DEC-Skill-Sharing` → not extracted this Change (architectural,
  autonomous).

None of these are `product`/`contract` class (no Requirement, public
Contract surface, schema, or domain invariant turns on any of them — they
are implementation-shape choices within an already-approved Specification)
so none carries the `human`-authority floor `CHG-0017`'s DEC-001 did.
