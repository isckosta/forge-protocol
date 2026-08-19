# ADR-0016 — Second Harness Adapter (Claude Code)

Status: Accepted for CHG-0018 Implementation; independent Strict Review pending.

## Decision

Forge gains its second concrete Harness Adapter,
`src/forge_cli/adapters/claude_code/`, registered in `adapters/packaged.py`
alongside `CodexDriver`. Harness selection is Claude Code, per
`ROADMAP.md`'s own named candidate, backed by capability evidence fetched
live from `code.claude.com` on 2026-08-19 (the date this Change began):
Claude Code documents `persistent_instructions` (`CLAUDE.md`), `commands`
(slash commands, unified with skills), `skills` (`.claude/skills/<name>/
SKILL.md`), `hooks` (`.claude/settings.json` or Skill-frontmatter-scoped,
lifecycle-event shell commands — `PreToolUse` can genuinely block a tool
call), `agent_roles` (subagents, `.claude/agents/*.md`), and
`generated_files` (file read/write/edit) — all six of `adapter.schema.json`'s
fixed capability vocabulary, `true`. Codex declares only `skills` and
`generated_files`; this is the materially different profile
`ROADMAP.md`'s stated Architecture Test needs.

Two pre-existing leaks of Codex-specific logic into the nominally-generic
Adapter Core were found and fixed as part of proving that test genuinely
holds, not merely asserting it: a `.codex` reserved-path rule hardcoded in
the generic `adapters/configuration.py` and
`protocol/schemas/adapter-configuration.schema.json` (whose regex also had
a latent unescaped-`.` bug), and `assess_invariant`/`to_generic_limitation`
(100% generic logic, zero Codex references) misfiled under
`codex/assessment.py`. Both now live correctly: the `.codex` reservation
solely in Codex's own `validate_publication_root`, and the invariant-
assessment logic in a new `adapters/assessment.py` both Drivers import.

The Claude Code Adapter projects through three real mechanisms, all
`forge_owned`, all sharing one publication root (`.claude` — not
`.claude/skills/forge`, because `ownership.require_publication_root_ownership`
requires every generated artifact to be a strict descendant of exactly one
root, and the Skill subtree and the CLAUDE.md pointer are siblings, not
parent/child):

1. **Skill** (`.claude/skills/forge/SKILL.md` + `references/*`) — full
   workflow content, structurally parallel to Codex's own projection
   (same effective Contract/Flow/artifact-structure/interaction-language
   inputs, plus the Protocol 2 Reviewer/Resolver-independence guidance
   Codex's own `SKILL.md` already carries).
2. **CLAUDE.md pointer** (`.claude/CLAUDE.md`) — a short, durable pointer
   naming the Skill rather than restating it (this repository's own
   INV-001 discipline), following Claude Code's own documented best
   practice that a multi-step procedure belongs in a skill, not CLAUDE.md.
3. **Illustrative enforcement hook** — declared in `SKILL.md`'s own
   frontmatter (`hooks.PreToolUse`, active once the skill has been invoked
   in a session), running a `forge_owned` script that denies in-place
   shell mutation (`sed -i`/`perl -i`/`truncate`/redirection) of
   `.forge/changes/*/{manifest.yml,provenance.yml,review.md}` — explicitly
   not matching read-only or version-control commands against the same
   paths (a real gap the first draft had, found and fixed at Specification
   Review). This is the one mechanism Codex (`hooks: false`) structurally
   cannot offer, and the only one of the three this Change represents as
   genuinely enforcement-capable rather than merely instructional — never
   claimed as a general security boundary, only as the one narrow,
   mechanically-checkable pattern it actually is.

`OwnershipMode.SHARED` (a driver-computed merge over pre-existing content)
was deliberately not used for either new mechanism: it would require
extending `AdapterProjectionContext` with observed-repository-content
access, a Core signature change, for a mode no real Adapter has ever
exercised. Both mechanisms instead reuse the already-safe, already-tested
`FORGE_OWNED` path, at file locations chosen specifically to avoid needing
a merge at all. No shared Skill-renderer was extracted between Codex and
Claude Code (a real, considered trade-off — see `architecture.md` DEC-003
— not an oversight): the two formats diverge exactly where the hook
mechanism needs them to.

A new shared, Harness-agnostic conformance test suite
(`tests/unit/test_adapter_driver_conformance.py`, parametrized over both
concrete Drivers, plus one parametrized CLI install/doctor round trip) is
the literal `ROADMAP.md` exit criterion "both Adapters pass shared
conformance tests" — not previously built for even one Adapter. A new
Contract rule, `C-074`, makes passing it a durable Completion obligation
for any future Harness Adapter, not a one-time exercise for this Change's
own two.

## Consequences

`forge adapter install claude-code` works end-to-end, verified against
real scratch repositories through the actual CLI (install, doctor,
idempotent reinstall), not only unit tests. The generic Adapter Core
required zero new vendor-specific concepts to support a second, materially
different Harness — and is measurably more vendor-neutral after this
Change than before it, having had two real (if narrow) leaks removed.
Gate D ("at least two concrete Harness Adapters demonstrate the generic
Core boundary") is satisfied with genuine, not merely nominal, evidence.
Because I am Claude Code, this Change also unlocks something the existing
Codex Golden Path structurally cannot offer: a fully-automated, live-
session-executed Layer A/B/C Golden Path, dogfooded as part of this
Change's own Verification (`examples/golden-path-claude-code/`) rather
than requiring a human to operate a separate tool. The hook mechanism's
real, if narrow, enforcement capability is a genuine architectural first
for this repository — no prior Adapter has ever been able to claim
anything stronger than `represented` for a Forge invariant — and this
Change is careful never to overstate what it actually covers.
