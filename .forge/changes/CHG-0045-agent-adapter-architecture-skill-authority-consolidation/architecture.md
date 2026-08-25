---
forge:
  artifact: architecture
  schema: 1
change: CHG-0045
status: complete
---

# Architecture — CHG-0045 Agent Adapter Architecture Skill Authority Consolidation

## Solution Summary

No new subsystem is introduced (C-032/C-033: the existing
`src/forge_cli/adapters/` pipeline — `registry.py`/`service.py`/
`planner.py`/`ownership.py`/`publisher.py`/`state.py` — is reused
unchanged in shape). This Change modifies three things inside that
existing pipeline: (1) `claude_code/projection.py`'s `_gate_instructions()`
stops re-emitting the Reviewer/Resolver-independence block per Flow and a
new shared module gives both `claude_code/projection.py` and
`codex/projection.py` one common source for that text and for the
CHG-0025/C-077 sentence's consistency check; (2) the generated `SKILL.md`
gains a short Bootstrap instruction that names the existing
`generated_drift` diagnostic as the thing to check before trusting
`references/*`; (3) the existing generated hook (`check-manifest-edit.sh`)
and its `PreToolUse` registration gain `Edit`/`Write` matchers alongside
the existing `Bash` one, protecting the same three paths.

## Architectural Goals

- Preserve C-043 (Adapters cannot redefine Forge) and F-004 (canonical
  Forge behavior must not exist exclusively inside a Harness Adapter) by
  keeping every normative source exactly where it already is.
- Reduce the number of places a human must edit identically to keep
  Reviewer/Resolver-independence and Plan-Decision text correct, from
  today's six (3 Flows × 2 Adapters) to one.
- Make the Adapter's own already-correct drift signal (`installation.yml`
  digests) something a bootstrapping agent is actually told to consult,
  instead of adding a second, competing drift mechanism.
- Widen mechanical guard coverage only where the existing hook's own
  ownership boundary (Adapter-owned, Claude-Code-specific,
  path-scoped) already applies, without inventing a new enforcement layer
  Core does not currently have.

## Answering the governing questions

**1. Normative authority.** `protocol/contract/engineering.md` (Contract),
`protocol/flows/*.yml` (Flow), `protocol/artifact-structure.md`, and
`src/forge_cli/validation/__init__.py`'s Decision-Rules constants — all
Core, all unchanged by this Change. `.forge/contract/engineering.md` is
the project-level additive extension (F-001–F-011); it cannot weaken
canonical content (C-042) and doesn't.

**2. Flow resolution.** `src/forge_cli/protocol_resolution/
resolve_effective_flow()` (Discovery) — already the single, harness-
agnostic resolver both Adapters call through `AdapterService.
_effective_flows()`. Unchanged.

**3. Reference generation.** `AdapterService`/`driver.project()` →
`generate_claude_code_skill_bundle()` / the Codex equivalent — unchanged
call shape; only `_gate_instructions()`'s internals and the new shared
independence-text source change.

**4. SKILL.md generation.** Generated, not static, both before and after
this Change (Discovery). The parts that change: `_gate_instructions()`'s
per-Flow loop (stops embedding the independence block); `_skill_content()`
gains one new Bootstrap paragraph; `_hook_frontmatter_lines()` gains two
matchers.

**5. What's generated vs. static.** Unchanged split: `workflow.md` remains
the one large hand-authored fragment (Adapter-owned procedural
instruction, Discovery's authority-map row confirms this is legitimately
Adapter-owned, not duplicative of Core); everything else in `SKILL.md` is
composed at render time from Core sources or from the new shared
independence module.

**6. Drift detection.** Already exists (`ownership.detect_generated_drift()`,
surfaced by `forge doctor`/`forge adapter doctor`). This Change does not
add a second detector; it adds one Bootstrap-section sentence in the
*generated output* directing an agent to run/consult it (**DEC-001**,
below) before treating `references/*` as current.

**7. Hook registration.** `.claude/skills/forge/SKILL.md`'s own YAML
frontmatter (`_hook_frontmatter_lines()`), unchanged mechanism — this
Change adds two more `matcher` entries (`Edit`, `Write`) pointing at the
same generated script path.

**8. Where policy executes.** Inside the generated shell script itself
(`_hook_script_content()`), unchanged location (**DEC-002**, below,
records why this Change does not move policy into a new `forge internal
guard` CLI entry point).

**9. Who interprets the hook payload.** The shell script itself, via
`jq` over the JSON piped to its stdin — unchanged for `Bash`; extended
with equivalent `jq` extraction of `tool_input.file_path` for `Edit`/
`Write` (Claude Code's documented `PreToolUse` payload shape for those
tools carries `file_path`, not `command`).

**10. `cwd` resolution.** `resolve_project_root(Path.cwd())`
(`src/forge_cli/git/__init__.py:15-30`) — delegates to
`git -C <cwd> rev-parse --show-toplevel`. Verified during Architecture:
for a Git worktree, this correctly returns *that worktree's own* top-level
directory, not the main checkout's — Git itself resolves this, Forge does
not hardcode or assume a single repository path anywhere in
`resolve_project_root`, `AdapterService`, or `doctor/__init__.py`
(`doctor/__init__.py:57` calls the same function). This part of Section 19
was already correct before this Change; no fix is required here.

**11. Worktree identification.** As above — via real `git`, not a Forge-
maintained registry, so it inherits Git's own worktree semantics
correctly by construction.

**12–13. Adapter versioning / backward compatibility.** `adapter.yml`'s
`protocol: {min, max_exclusive}` (unchanged mechanism) plus
`installation.yml`'s recorded `adapter.version` — `AdapterService.
install()`/`update()` already refuse to operate over an unresolved
version/drift mismatch (Discovery). Unchanged by this Change.

**14. Local customization preservation.** `ownership.classify_artifact()`
already treats a `forge_owned` path with a digest mismatch as `CONFLICT`,
not silent overwrite (Discovery, `forge adapter plan claude-code`'s live
`CONFLICT` output is direct proof this already works as intended — it
blocked automatic republishing of the very files this Change will change,
which is correct, not a bug). Unchanged by this Change.

**15. Consulting human authority.** Unchanged: C-077 remains the Contract
rule; `forge validate` remains the enforcement point; the Plan/
Implementation boundary in this repository's own Plan artifact type
(`artifact-structure.md`'s "Plan approval boundary" section) is where the
confirmation is recorded. This Change's FR-003 only removes a stale,
duplicated *restatement* of that rule from the generator; it does not
touch the rule or its enforcement.

**16. Consulting Strict Review independence.** Unchanged mechanism
(C-026, `forge validate`'s provenance checks); FR-001/FR-002 change how
its *English description* is rendered into `SKILL.md`, never its
semantics or its Core-level validation.

**17. Flow-specific context loading.** Confirmed already lazy/selective at
the reference-file level (Contract, Artifact Structure, Decision Rules,
and each Flow's YAML are separate linked files, not inlined into
`SKILL.md` — Discovery). The only content actually inlined into
`SKILL.md` itself is the short per-Flow gate-obligation bullet list. See
**DEC-003** for why this Change does not push that further into per-Flow
lazy-loaded fragments.

**18. Avoiding full normative documentation in context.** Already true
today at the reference-file granularity (Q17); this Change does not
regress it, and FR-001–FR-003 make the one currently-inlined, currently-
duplicated content smaller, not larger (NFR-003).

**19. Future harness adapters.** The shared independence-text module
(FR-002) lives in `src/forge_cli/adapters/` (harness-agnostic layer,
alongside `ownership.py`), not inside either harness-specific package —
a third Adapter (hypothetical) would import the same shared module rather
than write a third copy, directly serving F-004 and the governing
prompt's non-goal of foreclosing multi-Adapter support without building
one prematurely (F-010).

## Decisions

### DEC-001 · Bootstrap instructs, Core detects (drift)
**Class:** architectural · **Materiality:** material · **Authority:**
agent_with_review · **Owning Artifact:** architecture

This Change adds an instruction, not a second detector. Rejected
alternative: have the Adapter re-implement its own content-hash comparison
inside `SKILL.md`'s prose (an agent literally computing digests). Rejected
because it would create exactly the duplicated-authority problem this
Change exists to remove, one layer up — Core's `ownership.
detect_generated_drift()` is already correct, tested, and the single
source of truth; the fix is to point the agent at it, not re-derive it.

### DEC-002 · Guard policy stays in the generated shell script; a centralized `forge internal guard` entry point is deferred, not adopted
**Class:** architectural · **Materiality:** material · **Authority:**
agent_with_review · **Owning Artifact:** architecture

**Option A (chosen):** extend the existing generated
`check-manifest-edit.sh` with additional tool-specific matching logic,
still Python-generated, still Adapter-owned, still a plain shell script
interpreting a JSON payload.
**Option B (considered):** introduce a new `forge internal guard-check`
CLI subcommand; the generated hook script becomes a thin shim that pipes
its stdin to `forge internal guard-check` and relays its exit/decision.
This is the governing prompt's own illustrated "PreToolUse → Forge Guard
Entry Point → policy evaluation" shape, and is architecturally cleaner for
a *third* Adapter's hook to reuse identical policy logic without
reimplementing the shell matching a third time.
**Option C (considered):** move policy entirely into project-level
`.claude/settings.json` hooks outside the Skill/Adapter's own generated
files.

**Rationale for A over B/C:** Only one Adapter (Claude Code) currently
generates a hook artifact at all (Discovery: Codex's bundle has none);
Option B's stated benefit — shared policy logic across multiple hook-
generating Adapters — has no second consumer yet, so building it now would
be exactly the "premature plugin system... hidden automation" F-010
disfavors, for a cost (a new CLI surface, F-005's CLI-boundary discipline,
new argument/exit-code contract, new test surface) this Change's evidence
does not justify. Option C would move a Forge-generated artifact's
lifecycle outside the Adapter's own ownership/digest/drift tracking
(`ownership.py`), directly regressing the one thing already working
correctly (Q14). Option B remains available to a future Change once a
second hook-generating Adapter exists and the duplication becomes real
rather than hypothetical — recorded here so a future maintainer does not
need to rediscover this tradeoff from scratch (F-008 spirit, without
requiring the RFC threshold Option B does not yet meet).

### DEC-003 · Per-Flow gate text stays inlined in SKILL.md; not split into further lazy-loaded fragments
**Class:** architectural · **Materiality:** non_material · **Authority:**
agent_with_review · **Owning Artifact:** architecture

The currently-inlined gate-obligation content, once FR-001/FR-003 remove
the duplicated independence block and stale sentence, is small (≈6-9
lines per Flow). Splitting each Flow's gate bullets into a fourth
generated reference file (`references/gates/<flow>.md`) would add three
new generated artifacts, three new digests to track, and three new links
to resolve — for content already smaller than one screen. Rejected as
disproportionate (C-039); the existing reference-file-per-normative-source
granularity (Q17) already achieves the real goal (not inlining Contract/
Flow/Decision-Rules bulk) without this.

### DEC-004 · Commit `.forge/adapters/*/installation.yml` to version control
**Class:** technical · **Materiality:** material · **Authority:**
agent_with_review · **Owning Artifact:** plan

Discovery/Architecture jointly found `.forge/adapters/` has never been
committed in this repository's history and is not `.gitignore`d (verified:
`.gitignore` excludes only `.forge/.cache/` and `.forge/.tmp/`) — it is
simply uncommitted working-tree state. Because Git worktrees do not share
untracked files, a fresh `git worktree add` checkout currently has no
`installation.yml` at all, so an agent bootstrapping FR-004's drift check
inside a secondary worktree would see "adapter not installed" rather than
an actual drift signal, even though the primary checkout has a real,
current installation. Committing `installation.yml` (a small, deterministic,
repository-native record — exactly the kind of durable knowledge C-030
describes) makes every worktree checkout inherit the correct baseline for
free, via Git itself, with no new code. This is recorded as a Plan task,
not a new FR, because it changes repository state/hygiene, not behavior.

## Risks

- **Residual guard gaps remain after FR-006.** MCP filesystem tools,
  `NotebookEdit`, and subagent-issued tool calls are not verified covered
  (Specification Review SR-003). Test Strategy must either verify subagent
  coverage empirically or the shipped disclosure must say, plainly, that
  it is unverified — never silently imply coverage that was not checked.
- **`forge adapter update` will surface real `UPDATE`s beyond this
  Change's own diff**, because Discovery's live drift (CHG-0044 and
  merge-readiness content) predates this Change. Verification must
  distinguish "drift this Change intentionally produces" from
  "pre-existing drift this Change's republish incidentally also clears,"
  so Completion does not overclaim credit for unrelated upstream changes.
- **DEC-004's commit changes what `git status` shows for every future
  Forge Change** in this repository (a new tracked path). Low risk,
  disclosed explicitly rather than silently bundled into an unrelated
  diff.

## Ownership Matrix

| Artifact | Owner/Authority |
|---|---|
| `protocol/contract/engineering.md` | Forge Core (canonical) |
| `.forge/contract/engineering.md` | Repository (additive project extension) |
| `protocol/flows/*.yml` | Forge Core (canonical) |
| `src/forge_cli/validation/__init__.py` Decision-Rules constants | Forge Core |
| `src/forge_cli/adapters/*.py` (shared, harness-agnostic) | Forge Core |
| `src/forge_cli/adapters/claude_code/*.py`, `codex/*.py` | Harness Adapter (Claude Code / Codex respectively) |
| `resources/skills/workflow.md` | Harness Adapter (Claude Code) — hand-authored, legitimately non-duplicative |
| Generated `SKILL.md`, `references/*`, `hooks/*` | Derived projection (Forge-owned output; never hand-edited) |
| `.forge/adapters/*/installation.yml` | Runtime/Change evidence (repository-native, now version-controlled per DEC-004) |
| `.forge/changes/CHG-0045/*` | This Change's own provenance/evidence |
