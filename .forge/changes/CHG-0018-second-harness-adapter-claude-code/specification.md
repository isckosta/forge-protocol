# Specification — Second Harness Adapter (Claude Code)

## Summary

Fix two pre-existing Codex-specific leaks in the generic Adapter Core;
add `src/forge_cli/adapters/claude_code/`, a second concrete Harness
Adapter, projecting through three real mechanisms (Skill, CLAUDE.md
pointer, illustrative enforcement hook), registered alongside Codex; add
a shared/parametrized conformance test suite; record an ADR with dated
capability evidence; dogfood a real Golden Path through the installed
Adapter, executed by the live Claude Code session producing this Change.

## Classification

**Flow: FULL.** Touches the generic Core (two fixes), a new executable
Adapter package, a probable new Contract obligation, and a new ADR — see
`discovery.md` "Flow Classification Finding".

## Functional Requirements

### FR-001 — Generalize the `.codex` reserved-path leak

`adapters/configuration.py`'s `_checked_target` and
`protocol/schemas/adapter-configuration.schema.json`'s `target` pattern
lose the `.codex` literal, keeping only generic path-safety rules
(non-empty, no `~`/absolute/`..`/backslash/colon/NUL). The schema's regex
bug (unescaped `.` matching `Xcodex`) is fixed as a byproduct of removing
the clause entirely. `codex/targets.py`'s own `.codex` rejection in
`validate_publication_root` is unchanged.

### FR-002 — Relocate generic invariant-assessment logic

`assess_invariant`/`to_generic_limitation` move from `codex/assessment.py`
to `adapters/assessment.py`. `codex/driver.py` imports from the new
location. No behavior change.

### FR-003 — Claude Code Adapter package and dated capability evidence

`src/forge_cli/adapters/claude_code/` provides `descriptor.py`,
`evidence.py`, `targets.py`, `projection.py`, `driver.py`, and packaged
`resources/{adapter.yml,capabilities.yml,publication.yml}` plus a skill
template, mirroring `codex/`'s shape. `adapter.yml` declares
`capabilities: {persistent_instructions: true, commands: true, skills:
true, hooks: true, agent_roles: true, generated_files: true}`.
`capabilities.yml` carries one evidence entry per capability, each
`status: supported`, `source:` a `code.claude.com` URL, `observed_on:
"2026-08-19"` — see `discovery.md`'s evidence table for the exact six.

### FR-004 — Skill projection mechanism

`ClaudeCodeDriver.project()` produces a `forge_owned` `.claude/skills/
forge/SKILL.md` + `references/{engineering-contract,artifact-structure,
flows/*}.md`, content-equivalent to Codex's projection: effective
Contract, effective Flows, artifact-structure (when resolved), and the
`interaction_language` instruction line — reusing exactly the same
`AdapterProjectionContext` fields `service.py` already populates
generically.

### FR-005 — CLAUDE.md pointer mechanism

`ClaudeCodeDriver.project()` additionally produces a `forge_owned`
`.claude/CLAUDE.md` (distinct from a project's conventional root
`CLAUDE.md`, per `discovery.md`) — a short (≈5–10 line) pointer stating
the repository is Forge-governed, naming the `forge` Skill, and stating
the effective interaction-language directive. It MUST NOT restate the
Skill's full content (INV-001-style: reference, not duplicate normative
content).

### FR-006 — Illustrative enforcement hook

The Skill's `SKILL.md` frontmatter declares a `hooks.PreToolUse` entry
matching `Bash`, running a `forge_owned` script under
`.claude/skills/forge/hooks/` that denies (`permissionDecision: "deny"`)
a shell command matching a narrow, specific in-place-mutation pattern
(`sed -i`, `perl -i`, `truncate`, or output redirection `>`/`>>`) whose
target includes a path under `.forge/changes/*/` ending in
`manifest.yml`, `provenance.yml`, or `review.md`. It MUST NOT match
read-only or version-control commands against the same paths (`cat`,
`ls`, `git add`, `git commit`, `git status`, `git diff`, `git show`,
`grep`) — those remain unaffected, since blocking ordinary `git add`/
`git commit` of these exact files would break the normal Forge workflow
this very Change's own commits depend on (found in Specification Review,
SR-001). It MUST NOT claim to enforce anything beyond that narrow,
mechanically-checkable pattern, and MUST NOT represent itself as active
before the Skill has been invoked at least once in a session (C-073-style
honesty).

### FR-007 — Registration

`adapters/packaged.py`'s `build_packaged_registry()` returns
`AdapterRegistry((CodexDriver(), ClaudeCodeDriver()))`.

### FR-008 — Shared conformance test suite

The genuinely adapter-agnostic existing unit tests (see `discovery.md`'s
Explore report / `architecture.md`'s test-file list) are parametrized over
both drivers where their own assertions are actually driver-independent.
Claude-Code-specific test files mirror the Codex-specific ones' shape
(descriptor, evidence, publication targets, projection bundle/gates,
distribution resources, packaged authority parity).

### FR-009 — Contract obligation for future Adapters

Confirmed in Specification (grep of `protocol/contract/engineering.md` for
"conformance": one unrelated hit, C-067, about Canonical Artifact
Structure — no existing rule addresses Adapter conformance testing at
all). New binding rule, `C-074`: a Change introducing a new Harness
Adapter MUST pass the shared conformance test suite (FR-008) before
Completion. This formalizes FR-008 as a durable obligation for any future
Harness Adapter beyond this Change's own two, not a one-time exercise.

### FR-010 — ADR

`docs/adr/0016-second-harness-adapter-claude-code.md` (number re-verified
immediately before writing) records the Harness-selection Decision (dated
evidence), the two Core-leak fixes, the three-mechanism design, and the
three architectural Decisions Discovery resolved (CLAUDE.md path, hook
placement, no skill-renderer extraction).

### FR-011 — Dogfooded Golden Path

A real Change is carried at least through Strict Review by a live Claude
Code session (this one) against a scratch repository with the installed
Claude Code Adapter, producing genuine repository-native Layer C evidence
— recorded under `examples/golden-path-claude-code/` alongside this
Change's own Verification.

## Non-functional Requirements

### NFR-001 — No vendor-specific concept in the generic Core

No file under `adapters/*.py` (excluding `codex/` and `claude_code/`
subpackages) references `codex`, `claude`, `claude-code`, `.claude`, or
`.codex` by name after this Change, except the pre-existing, intentional
`adapters/packaged.py` composition-root imports of both concrete drivers.

### NFR-002 — Codex functionally unaffected

Every existing Codex unit/integration/CLI test passes unchanged after
FR-001/FR-002's relocation — confirmed by running the full pre-existing
Codex test surface before and after, byte-for-byte identical pass count
modulo the one intentionally-removed/relocated `.codex` parametrize case
(FR-001).

### NFR-003 — Capability evidence honesty

No capability declared `true` in `claude_code/resources/adapter.yml`
implies Core, `forge validate`, or `forge doctor` verifies live Harness
behavior for it — matches C-073 (`CHG-0017`) applied to a second Adapter's
own evidence, not only to interaction-language projection specifically.

## Constraints

### CON-001 — No new Protocol integer

Nothing here weakens or redefines an existing Protocol invariant.

### CON-002 — Schema change is a narrowing removal only

`adapter-configuration.schema.json`'s only change is removing a clause
(more strings validate afterward, none fewer) — every existing
`.forge/adapters/*/config.yml` (this repository has none currently
configured beyond defaults) continues to validate.

### CON-003 — Historical validity

Every historical Change (`CHG-0001`–`CHG-0017`) remains valid; `forge
validate`/`forge doctor` report no new finding against any of them.

### CON-004 — No FAST/STANDARD ceremony change

Nothing here touches Flow, Gate, Finding-severity, or Review-convergence
semantics for ordinary (non-Adapter-authoring) Changes.

### INV-001 — No duplicated normative authority

The CLAUDE.md pointer (FR-005) references the Skill; it does not restate
Contract/Flow/artifact-structure content in its own words.

## Acceptance Criteria

- **AC-001**: `adapters/configuration.py`/`adapter-configuration.schema.json`
  accept a target of `.codex/anything`; `codex/targets.py`'s
  `validate_publication_root` still rejects it.
- **AC-002**: `adapters/assessment.py` exists and exports
  `assess_invariant`/`to_generic_limitation`; `codex/assessment.py` no
  longer does (or re-exports only, if a compatibility shim is judged
  necessary at Architecture — default: fully removed, no shim, since
  nothing outside `codex/driver.py` imports it, confirmed by Discovery).
- **AC-003**: `forge adapter install claude-code` succeeds against a fresh
  scratch repository, producing `.claude/skills/forge/SKILL.md` +
  `references/*`, `.claude/CLAUDE.md`, and the hook script + SKILL.md
  frontmatter `hooks:` block.
- **AC-004**: `capabilities.yml`/`adapter.yml` declare all six
  capabilities `true`, each with a real, dated, fetchable source.
- **AC-005**: `forge doctor claude-code` reports drift-clean after
  install; a second `forge adapter install claude-code` on an unmodified
  install is a no-op (idempotent), matching Codex's own existing
  guarantee.
- **AC-006**: The shared conformance suite runs the same assertions
  against both `CodexDriver()` and `ClaudeCodeDriver()` and passes for
  both.
- **AC-007**: `forge validate`/`forge doctor` report no new finding
  against any historical Change after this Change lands.
- **AC-008**: `docs/adr/0016-*.md` exists and records every Decision named
  in FR-010.
- **AC-009**: A real dogfooded Change under
  `examples/golden-path-claude-code/` (or this Change's own Verification,
  if Architecture judges a separate example directory redundant with this
  Change's own dogfooding — confirmed at Architecture) reaches at least
  Strict Review, executed by a live session, not simulated or narrated.
- **AC-010**: `CHANGELOG.md`/`ROADMAP.md` reflect this Change at
  Completion.

## Unresolved Decisions

All three real open questions this Change faced (`CLAUDE.md` ownership
mechanism, hook placement/invariant, whether to extract a shared
Skill-renderer) were resolved during Discovery with concrete evidence
(see `discovery.md`) rather than left open here — none is `product`/
`contract` class (none touches a Requirement, public Contract surface,
schema, or domain invariant on its own), so `architectural`/
`agent_with_review` authority applies and Architecture formally records
each as a Decision, not a silent implementation choice.

## Out of Scope

- A third Harness Adapter.
- The ROADMAP's "End-to-End Examples & External Validation" milestone.
- Any MCP-server Adapter mechanism.
- Extending `OwnershipMode.SHARED` to actually support driver-computed
  merges (would require a Core signature change; avoided entirely per
  `discovery.md`).
- Any change to Codex's declared capabilities, publication target, or
  projected content, beyond the two relocation/generalization fixes.

## Traceability

Populated in `traceability.yml` at Plan/Tasks stage onward.
