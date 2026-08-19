# Architecture — Second Harness Adapter (Claude Code)

## Solution Summary

Mirror `codex/`'s package shape for a new `claude_code/` package; fix the
two Core leaks Discovery found; project through three real, safe
mechanisms (Skill, CLAUDE.md pointer, Skill-frontmatter hook), all
`forge_owned`, all reusing existing, already-tested ownership/planning
machinery with zero Core signature change; register in `packaged.py`;
build the shared conformance suite; add one new Contract rule (C-074).

## DEC-001 — CLAUDE.md publication path

**Class**: `architectural`. **Authority**: `agent_with_review`.

**Question**: Where does Forge's CLAUDE.md contribution live?

**Alternatives**: (A) `.claude/CLAUDE.md`, `forge_owned` — selected. (B)
the project's conventional root `./CLAUDE.md`, `shared`-owned with a
driver-computed marker-delimited merge. (C) don't project CLAUDE.md
content at all, Skill-only.

**Resolution**: A. `.claude/CLAUDE.md` is an officially documented,
equally-valid project CLAUDE.md location, distinct from the conventional
root path almost every real project already uses for its own instructions
— so collision risk is low, and when it does happen, the existing
`forge_owned` CONFLICT path (used today by Codex's `SKILL.md`) handles it
safely without inventing anything. Alternative B would require extending
`AdapterProjectionContext` with observed-repository-content access (a
Core signature change) to compute a merge inside a currently-pure
`project()` — for a `SHARED` mode that has never been exercised by any
real Adapter. Alternative C forgoes a real, distinct second mechanism the
user asked to explore for no compensating benefit. **Resolved via**:
`autonomous_decision`, confidence high — the collision-avoidance argument
is decisive and mechanically checkable (Strict Review can verify no Core
signature changed).

**Correction found during Implementation, before any freeze**:
`ownership.require_publication_root_ownership` requires *every* generated
artifact to be a strict descendant of one publication root
(`root not in artifact.parents` raises). `.claude/CLAUDE.md` is a sibling
of `.claude/skills/forge`, not a descendant of it — so the Skill and the
CLAUDE.md pointer cannot share Codex's pattern of "publication root =
skill directory." Resolution: this Adapter's `default_target`/
`publication.yml` is `.claude` (the shared Claude Code configuration
root), not `.claude/skills/forge`; the Skill's own artifacts are placed
at `skills/forge/...` relative to it and CLAUDE.md at `CLAUDE.md`
relative to it — both remain strict descendants of `.claude`, satisfying
the existing generic check with zero Core change, exactly as originally
argued, just via a different publication-root value than first drafted.
This also removes the need for any Claude-Code-owned reserved-path rule
symmetrical to Codex's `.codex` reservation: unlike Codex's default
target (which does *not* live under `.codex/`), this Adapter's default
target *is* `.claude` itself, so there is no unrelated, always-forbidden
sibling directory to protect — every path Forge generates under it uses
Forge-owned names, already protected by the existing generic
FORGE_OWNED/digest-conflict machinery. `claude_code/targets.py` has no
reserved-path rule beyond the generic path-safety checks it already
shares with Codex's `_checked()` shape.

## DEC-002 — Hook placement and invariant

**Class**: `architectural`. **Authority**: `agent_with_review`.

**Question**: Where is the illustrative enforcement hook configured, and
what does it enforce?

**Alternatives**: (A) `SKILL.md` frontmatter `hooks:` block, scoped to the
already-`forge_owned` Skill tree — selected. (B) a `forge_owned` entry
merged into `.claude/settings.json`, most projects' pre-existing,
user-owned permissions/settings file. (C) no hook; two mechanisms only.

**Resolution**: A. Claude Code's own docs confirm SKILL.md frontmatter
supports a `hooks:` field ("registered when you or Claude invoke the
skill... remain active for the rest of the session"), so the hook is just
more content inside a file Forge already fully owns — zero new ownership
mechanics, zero risk of corrupting a user's own settings (permissions,
sandbox config, env vars) the way Alternative B risks. Alternative C
forgoes exercising Core's `enforced`/`represented`/`unsupported`
distinction against a real enforcement-capable mechanism, the single most
interesting capability difference from Codex. Invariant: deny in-place
shell mutation (`sed -i`/`perl -i`/`truncate`/redirection) of
`.forge/changes/*/{manifest.yml,provenance.yml,review.md}`, explicitly
excluding read-only/VCS commands (Specification Review SR-001) — narrow,
mechanically verifiable, directly C-026/C-016-adjacent (review-control
metadata integrity), and something Codex (`hooks: false`) structurally
cannot offer. Honest limitation, stated in FR-006 and this Change's own
Verification: only active once the Skill has been invoked in a session,
not from session start. **Resolved via**: `autonomous_decision`,
confidence high.

## DEC-003 — No shared Skill-renderer extraction

**Class**: `architectural`. **Authority**: `agent_with_review`.

**Question**: Should Codex's and Claude Code's SKILL.md-rendering logic
share one generic renderer?

**Alternatives**: (A) keep `claude_code/projection.py` a parallel,
independent implementation — selected. (B) extract a shared renderer
(e.g. `adapters/skill_projection.py`) both drivers call into.

**Resolution**: A. The two formats diverge exactly where DEC-002 needed
them to: Claude Code's `SKILL.md` frontmatter carries a `hooks:` block
Codex's never will. What looked like near-identical duplication before
Discovery is smaller and more divergent after it. Extracting now would
also mean refactoring Codex's already-shipped, already-reviewed
projection code inside the same Change introducing a materially new,
higher-risk component — two kinds of risk stacked instead of one.
Revisitable as its own focused Change once a second real implementation
makes the actual (not assumed) duplication visible and stable.
**Resolved via**: `autonomous_decision`, confidence medium (a real,
debatable trade-off, not a decisive argument like DEC-001/DEC-002 — noted
honestly, not inflated).

## Content Shape

### `claude_code/resources/adapter.yml`

```yaml
schema: forge/adapter@1
adapter:
  id: claude-code
  version: 0.1.0
  harness: claude-code
protocol:
  min: 1
  max_exclusive: 3
capabilities:
  persistent_instructions: true
  commands: true
  skills: true
  hooks: true
  agent_roles: true
  generated_files: true
```

### `claude_code/resources/capabilities.yml`

Six `evidence:` entries (`discovery.md`'s table), each `status: supported`,
real `code.claude.com` URLs, `observed_on: "2026-08-19"` — the date this
Change's evidence was actually fetched, not Codex's unrelated
`2026-08-13` observation date.

### `claude_code/resources/publication.yml`

```yaml
target: .claude
source: https://code.claude.com/docs/en/skills
observed_on: "2026-08-19"
```

(`.claude`, not `.claude/skills/forge` — see DEC-001's Correction, above:
the Skill and CLAUDE.md pointer must share one common ownership-root
ceiling.)

### `claude_code/projection.py`

Three render functions: `_skill_bundle(...)` (SKILL.md + references,
parallel to `codex/projection.py`'s shape but with a `hooks:` frontmatter
block and no Codex-specific gate-instruction wording reused verbatim —
written fresh against the same generic `AdapterProjectionContext` fields),
`_claude_md_pointer(...)` (short, references the Skill by path), and
`_hook_script()` (static, `forge_owned`, deterministic content — a small
POSIX shell script reading `tool_input.command` via `jq`, matching the
pattern from Claude Code's own documented hook example shape).

### `claude_code/driver.py`

`ClaudeCodeDriver` implements `HarnessDriver` exactly like `CodexDriver`:
`manifest` (from `descriptor.py`), `default_target` (from `targets.py`),
`validate_publication_root` (generic path-safety + a Claude-Code-owned
reservation, mirroring Codex's own pattern for its own default target
prefix), `project(context)` returning all three mechanisms' artifacts as
one `AdapterProjection`.

## Contract and Specification Placement

`C-074` appended to `protocol/contract/engineering.md` and
`protocol/versions/2/contract/engineering.md` (matching the dual-file
convention `CHG-0017` used for `C-070`–`C-073`). No `protocol/
specification.md` change — confirmed unnecessary in Discovery (§34–38
already generic).

## Adapter/Harness Integration

- `adapters/packaged.py`: `AdapterRegistry((CodexDriver(),
  ClaudeCodeDriver()))`.
- `adapters/assessment.py` (new, relocated from `codex/assessment.py`):
  imported by both `codex/driver.py` and `claude_code/driver.py`.
- `adapters/configuration.py` / `adapter-configuration.schema.json`: the
  `.codex` clause removed; `codex/targets.py` keeps its own, now-sole
  copy. `claude_code/targets.py` has no equivalent reservation — DEC-001's
  Correction explains why one isn't justified.

## Compatibility

Purely additive/relocating. No Protocol version bump. `.codex` removal
from the generic schema only *widens* what validates (CON-002). No
existing `.forge/forge.yml`, historical Change, or Codex behavior changes
functionally.

## Risks

- **A third future Harness Adapter might need yet another ownership
  pattern** neither `forge_owned`-distinct-path nor Skill-frontmatter-
  hooks generalizes to. Not mitigated preemptively — the same "wait for a
  second real case before generalizing" discipline DEC-003 already
  applies here; a third Adapter is explicitly out of scope.
- **The hook's shell-pattern matching could have a real false-negative/
  false-positive gap** no test suite fully closes (arbitrary shell
  quoting/obfuscation could evade a pattern match; an unusual but
  legitimate command could match it). Mitigated by keeping the pattern
  narrow and the claim honest (FR-006: "MUST NOT claim to enforce
  anything beyond that narrow, mechanically-checkable pattern") — this is
  an illustrative capability demonstration, not a security boundary, and
  is never represented as one anywhere in this Change's own Artifacts.

## What This Change Deliberately Does Not Build

- Any change to `OwnershipMode.SHARED`'s actual mechanics or to
  `AdapterProjectionContext`'s signature.
- A shared Skill-renderer (DEC-003).
- Any MCP-server, Plugin-manifest (`.claude-plugin/plugin.json`), or
  marketplace-distribution mechanism, even though Claude Code documents
  all three — none is required to prove Harness independence, and Skills
  installed directly under `.claude/skills/` (not as a Plugin) is the
  simpler, already-proven-safe mechanism Codex's own precedent uses.
- Any third Harness Adapter.
