---
forge:
  artifact: intent
  schema: 1
change: CHG-0045
status: active
---

# CHG-0045 · Agent Adapter Architecture Skill Authority Consolidation

> **Change Intent**
>
> Consolidate the Claude Code Agent Adapter (`SKILL.md` and its generated
> references) so it stops re-deriving normative Forge content by hand and
> instead orchestrates a small, precise, drift-resistant projection of the
> Core's actual authority — removing the Flow-obligation and
> Reviewer/Resolver-independence duplication that currently exists both
> across Flows within one Adapter and across the Claude Code and Codex
> Adapters.

## Overview
| | |
|---|---|
| **Change** | CHG-0045 |
| **Flow** | FULL |
| **Status** | Active |

## Problem

The Claude Code Agent Adapter already has a real generation pipeline
(`src/forge_cli/adapters/claude_code/projection.py`, driven by
`AdapterService`/`planner.py`/`ownership.py`/`publisher.py`) that composes
`SKILL.md` and `references/*` from canonical Core sources
(`protocol/contract/engineering.md`, `protocol/flows/*.yml`,
`protocol/artifact-structure.md`) plus one static prose fragment
(`resources/skills/workflow.md`), and it already records per-file SHA-256
digests in `.forge/adapters/claude-code/installation.yml` for drift
detection (`forge doctor`, `forge adapter doctor`).

Despite that machinery, the generator itself — not just its output —
duplicates normative content: `_gate_instructions()`
(`projection.py:112-162`) loops over every effective Flow and, for Protocol
≥ 2, appends the same 17-line `_REVIEWER_RESOLVER_INDEPENDENCE_LINES` block
(`projection.py:75-109`) once per Flow, so the installed `SKILL.md`
currently repeats that block three times verbatim (fast/standard/full) and
repeats the CHG-0025/C-077 Plan Decision sentence in two of the three Flow
sections. The Codex Adapter (`src/forge_cli/adapters/codex/projection.py:58`)
independently defines its own copy of the identical
`_REVIEWER_RESOLVER_INDEPENDENCE_LINES` constant, so the same normative
English text is hand-maintained in two Python files that must be kept in
sync by hand — a second, cross-Adapter axis of the same duplication.

Separately, `forge adapter plan claude-code` currently reports `CONFLICT`
for `SKILL.md`, `references/artifact-structure.md`, and
`references/engineering-contract.md`: canonical `protocol/` content changed
in later Changes (CHG-0044 and the merge-readiness gate work) without a
`forge adapter update` republishing the projection, so the installed
Adapter is presently, demonstrably stale relative to its own recorded
digests. This is a live instance of exactly the "Agent Adapter Drift" this
Change's governing prompt asks it to address — not a hypothetical.

Finally, the Adapter's mechanical enforcement surface is a single
`PreToolUse` hook matched only against `Bash`, honestly disclosed in its
own text as "illustrative" and narrow; the same protected-path mutation is
trivially reachable through `Edit`/`Write`, which the hook does not see at
all, and the hook itself only exists once this Skill has been invoked in
the session.

## Goal

1. Make the Claude Code Adapter's generated `SKILL.md` orchestrate rather
   than restate: it should resolve effective Forge state and load the
   already-existing generated references, not re-derive their content in
   Adapter-specific English prose duplicated per Flow or per Adapter.
2. Collapse the Reviewer/Resolver-independence and Flow-gate-obligation
   text to one generation path shared across Flows, and evaluate whether
   it can also be shared across Adapters (Claude Code, Codex) instead of
   being independently hand-maintained twice.
3. Make the existing drift-detection machinery (`installation.yml`
   digests, `forge doctor`/`forge adapter doctor`) the thing a bootstrapping
   agent is instructed to trust and check, rather than something that can
   silently go stale under an agent operating on pre-existing installed
   files.
4. Preserve, without weakening, every Contract invariant this repository
   already enforces (C-001 through C-077 as currently defined), the
   Reviewer/Resolver independence semantics of C-026, the Plan Decision
   boundary of C-077, and the FAST/STANDARD/FULL gate obligations — this
   Change changes how they are *projected*, never what they *mean*.
5. State explicitly, in the Specification and Architecture, the
   self-hosting boundary already articulated in this repository's `forge`
   skill instructions: the Forge state effective at this Change's own
   start governs this Change's own execution; nothing this Change produces
   retroactively alters this Change's own Flow, gates, or Review
   requirements.

## Scope

- The Claude Code Agent Adapter's generation logic
  (`src/forge_cli/adapters/claude_code/`) and its effect on the installed
  `SKILL.md` / `references/*` / `hooks/*`.
- The shared, harness-agnostic Adapter machinery in
  `src/forge_cli/adapters/*.py` to the extent it must change to remove
  duplication or strengthen drift detection/reporting.
- Whether and how the same de-duplication should extend to the Codex
  Adapter, given C-074's shared-conformance-suite obligation and this
  repository's own `F-004` (canonical Forge behavior must not exist
  exclusively inside a Harness Adapter).
- Documentation of the resulting Agent Adapter architecture
  (authority model, generation model, drift lifecycle) where the
  Engineering Contract, `protocol/`, `docs/`, or adapter-facing
  documentation requires it.

## Out of Scope

- Building new Harness Adapters (a hypothetical Cursor/VS Code Adapter).
  This Change must not foreclose that future, but does not implement it.
- Replacing Git as the review substrate, replacing Strict Review, making
  it optional, or weakening TDD.
- A new Protocol identifier. Nothing here is expected to require a
  breaking Contract change (C-046); if Discovery or Architecture finds
  otherwise, that is itself a Material Unresolved Decision requiring
  human authority, not something this Change resolves unilaterally.
- Silently resolving the currently-live `CONFLICT` drift between canonical
  `protocol/` content and the installed Claude Code/Codex Adapters as an
  incidental side effect. Bringing the installed representation back into
  agreement with canonical Core content is expected to be a *consequence*
  of shipping the new generator (a normal `forge adapter update`
  republish), not a separate hand-patch of the currently installed files.
- A general-purpose sandbox or absolute mechanical enforcement guarantee.
  The mechanical guard boundary this Change may extend remains an honest,
  partial guard, not a security boundary.

## Success Criteria

- The generated `SKILL.md` no longer contains the Reviewer/Resolver
  independence block more than once, and Flow-specific gate text is
  resolved from the effective Flow rather than hand-duplicated per Flow in
  the generator.
- `forge doctor` / `forge adapter doctor` cleanly detect and report drift
  for the new generation shape, and the Adapter's own bootstrap-facing
  instructions direct an agent to check and honor that signal before
  trusting installed references.
- The Engineering Contract, Decision Rules, and Flow authority remain
  exactly where they already are (Core); the new `SKILL.md` is smaller or
  equal in normative surface, is explicit about not being that authority,
  and is explicit about the mechanical guard's real, partial coverage.
- Every existing passing test and `forge validate`/`forge doctor` clean
  state is preserved or improved, with new behavioral test coverage for
  whatever de-duplication and drift-reporting behavior this Change adds.
