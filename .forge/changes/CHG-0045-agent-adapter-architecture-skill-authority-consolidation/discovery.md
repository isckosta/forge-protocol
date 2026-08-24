---
forge:
  artifact: discovery
  schema: 1
change: CHG-0045
status: complete
---

# Discovery — CHG-0045 Agent Adapter Architecture Skill Authority Consolidation

## Executive Summary

The Agent Adapter architecture this Change is asked to design already
exists in substantial form: `src/forge_cli/adapters/` is a real,
harness-agnostic generation/publication/drift-detection pipeline
(`registry.py`, `service.py`, `planner.py`, `ownership.py`, `publisher.py`,
`state.py`, `validation.py`, `diagnostics.py`), with two concrete
Adapters (`claude_code/`, `codex/`) built on it, and it already carries a
digest-based drift record (`installation.yml`, schema
`forge/adapter-installation@2`) surfaced through `forge doctor` and
`forge adapter doctor`. This Change is therefore **not** "build the Agent
Adapter abstraction"; it is "remove the normative duplication the existing
generator still bakes into its output, and make the existing drift
machinery something an agent is actually instructed to trust and check."

The single strongest, concretely reproducible finding: the duplication the
governing prompt hypothesizes is real, is located in the *generator code*
(not just its output), and exists on two independent axes simultaneously —
per-Flow (inside `claude_code/projection.py`) and per-Adapter (between
`claude_code/projection.py` and `codex/projection.py`). A second,
independently reproducible finding: this repository's own installed
Adapters are, right now, in the exact "Agent Adapter Drift" state the
prompt asks this Change to detect — `forge adapter plan claude-code`
reports `CONFLICT` for `SKILL.md` and two `references/*` files because
canonical `protocol/` content moved after the last `forge adapter update`.
Both findings are cited with reproduction commands below.

## Investigation

### Where SKILL.md and its references come from (not hand-authored)

`.claude/skills/forge/SKILL.md` and `.claude/skills/forge/references/*`
are Forge-owned generated output, never meant to be hand-edited — the same
is true for `.agents/skills/forge/` (Codex). Nothing in this Change should
treat the currently-installed files as a source; the source is:

- `SKILL.md` ← `_skill_content()` (`src/forge_cli/adapters/claude_code/projection.py:193-235`), which concatenates: YAML frontmatter with the `PreToolUse` hook registration (`_hook_frontmatter_lines()`, :182-190); the static prose fragment `resources/skills/workflow.md`, loaded verbatim by `load_workflow_skill_template()` (:44-46); generated reference links (`_reference_links()`, :165-179); an interaction-language line (`_interaction_language_line()`, :62-72); fixed "Illustrative enforcement hook" prose (:220-232); and `_gate_instructions()` (:112-162), which parses each effective Flow's YAML and renders English gate-obligation bullets.
- `references/engineering-contract.md` ← `resolve_effective_contract()` (`src/forge_cli/protocol_resolution/__init__.py:115-138`): canonical `protocol/contract/engineering.md` plus the project's additive `.forge/contract/engineering.md` extension (currently just `F-001`–`F-011`, confirmed by direct comparison — the installed reference file's C-001…C-075/C-077 body is byte-identical in substance to `protocol/contract/engineering.md`, with `F-001`–`F-011` appended from the project file).
- `references/artifact-structure.md` ← `resolve_effective_artifact_structure()` (`protocol_resolution/__init__.py:141-161`), canonical `protocol/artifact-structure.md`.
- `references/decision-rules.md` ← a dedicated renderer over the same Python constants `forge validate` enforces (`src/forge_cli/validation/__init__.py`: `_DEC_CLASSES`, `_DEC_MATERIALITY`, `_DEC_STATUSES`, `_DEC_AUTHORITIES`, `_DEC_RESOLVED_VIA`, `_DEC_OWNING_BY_CLASS`, `_DEC_AUTHORITY_FLOOR`), introduced by **CHG-0021** specifically so this content would never be hand-duplicated (`decision-rules.md:1-3` states this in its own header). This is the one reference in the current architecture that already fully matches the "deterministic generation over hand-duplication" principle this Change is asked to generalize.
- `references/flows/<id>.yml` ← a re-serialized (`yaml.safe_dump`) copy of canonical `protocol/flows/<id>.yml`. Confirmed byte-for-byte semantically identical to canonical content by diff; the only differences are YAML formatting (block-style indentation, a stripped `# C-077` comment) introduced by the round-trip through a YAML dumper, not content drift.
- `.claude/skills/forge/hooks/check-manifest-edit.sh` ← fully generated inline in Python (`_hook_script_content()`, `projection.py:253-282`), not a static shipped file — unlike `workflow.md`, which is the one large genuinely hand-authored fragment.
- `.claude/CLAUDE.md` pointer ← `_claude_md_pointer()` (`projection.py:238-...`), fully generated.

`forge adapter install`/`update` (`AdapterService`, `service.py:535-601`)
both funnel through `_prepare()` → `driver.project(...)` → `planner.py`'s
`plan_adapter()`, which classifies every generated path via
`ownership.classify_artifact()` against on-disk digests
(`repository.py`'s `_snapshot_artifact`, `plan.py:26-27`'s
`digest_content = sha256(...).hexdigest()`) into
CREATE/UPDATE/UNCHANGED/CONFLICT, then `publisher.py` writes the plan. The
per-file SHA-256 digests are recorded in
`.forge/adapters/claude-code/installation.yml` (schema
`forge/adapter-installation@2`) as `generated_artifacts: [{path, digest}]`.
There is no `sync` command; only `install` (requires no prior record, or
an unchanged-version one) and `update` (requires an existing record,
refuses to run over unresolved drift). `forge doctor` and
`forge adapter doctor` both already surface a `generated_drift` check
(`service.py:333-426`) that compares recorded digests against current
on-disk content.

**This means Section 15's "derived references with generator/digest
metadata" and Section 16's "drift detection" are already built**, at
Core level, harness-agnostically. The open question for Architecture is
not whether to build them, but (a) whether `installation.yml`'s existing
digest ledger is sufficient bootstrap-time evidence for an *agent* — today
nothing in `SKILL.md` tells the agent to check it — and (b) whether the
per-file digest is the right drift granularity, or whether a single
adapter-level digest/version stamp would better support the "detect
drift, never silently operate on stale content" requirement.

### The duplication is in the generator, confirmed on two axes

`projection.py:75-109` defines
`_REVIEWER_RESOLVER_INDEPENDENCE_LINES: tuple[str, ...]`, a 17-line,
hand-written constant holding the exact "Reviewer/Resolver independence"
block. `_gate_instructions()` (:112-162) iterates
`sorted(flows, key=...)` — one iteration per effective Flow — and, for
every Protocol-≥2 Flow in `{fast, standard, full}`, does
`lines.extend(_REVIEWER_RESOLVER_INDEPENDENCE_LINES)` (:158-159) *inside*
that per-Flow loop. The rendered `SKILL.md` therefore repeats the
identical block three times (confirmed: lines 48-63, 80-95, 112-127 of the
currently installed `.claude/skills/forge/SKILL.md` are byte-identical
except for the `###` heading each sits under). This is Section 4.3 of the
governing prompt's "Review policy duplication," reproduced exactly and
traced to its exact generating line.

Independently, `src/forge_cli/adapters/codex/projection.py:58` defines
*its own, separately hand-written* `_REVIEWER_RESOLVER_INDEPENDENCE_LINES`
constant — same content, different file, no shared import. Two Adapters
currently each own a private copy of the same normative English
translation of C-026; keeping them in agreement requires a human or agent
to edit both files identically every time C-026's wording or scope
changes. This is a real, current instance of Contract-authority
duplication *between* Adapters, not only within one.

The CHG-0025/C-077 Plan Decision sentence follows the same shape:
`_gate_instructions()` does not currently emit it at all (confirmed by
reading the full function body — no `CHG-0025` or `C-077` string appears
in `projection.py`), yet the *installed* `SKILL.md` contains it, hand
written, in the `full` and `standard` Flow sections (lines 67-69 and
99-101). That specific sentence is present in the generator-owned static
fragment `resources/skills/workflow.md:21-25` exactly once — so the
canonical generator's actual current behavior would **not** reproduce
today's installed file; the installed file is stale relative to its own
generator, which is the second finding below.

### The installed Adapters are currently drifted — reproducible right now

```
$ forge doctor
...
FAIL adapter:claude-code:generated_drift: Generated artifacts have drifted
  (modified: .claude/skills/forge/SKILL.md,
   modified: .claude/skills/forge/references/artifact-structure.md,
   modified: .claude/skills/forge/references/engineering-contract.md).
FAIL adapter:codex:generated_drift: Generated artifacts have drifted
  (modified: .agents/skills/forge/SKILL.md, ...)

$ forge adapter plan claude-code
UNCHANGED forge_owned .claude/CLAUDE.md
CONFLICT  forge_owned .claude/skills/forge/SKILL.md
UNCHANGED forge_owned .claude/skills/forge/hooks/check-manifest-edit.sh
CONFLICT  forge_owned .claude/skills/forge/references/artifact-structure.md
UNCHANGED forge_owned .claude/skills/forge/references/decision-rules.md
CONFLICT  forge_owned .claude/skills/forge/references/engineering-contract.md
...
E_FORGE_ADAPTER_CONFLICT: Adapter plan contains unresolved conflicts.
```

`git diff HEAD -- .claude/skills/forge/` is empty — this is **not** an
uncommitted hand-edit of the installed files. `git log` shows the
canonical sources moved instead: `protocol/artifact-structure.md` was
edited by CHG-0044 (commits `92366d7`, `80d72e5`) and
`protocol/contract/engineering.md` was most recently touched by the
merge-readiness gate work (`3bea840`), both merged to `main` after
`.forge/adapters/claude-code/installation.yml` was last written by a
`forge adapter update`. The installed Adapter representation is
demonstrably behind the canonical Core it is supposed to project, and
nothing currently blocks an agent from reading the stale `SKILL.md`
without ever learning that `forge doctor` already knows it is stale.

This is direct, load-bearing evidence for the prompt's Section 16
("the agent must never silently operate on a reference known to be
stale") and Section 6 ("if a derived reference diverges from repository
authority... detect adapter/reference drift... report the
inconsistency"): the detection mechanism exists; the instruction to
*consult* it before trusting `SKILL.md`'s own references does not.

### Authority map (per the governing prompt's Section 43 classification)

| Content currently in `SKILL.md` | Classification | Real authority |
|---|---|---|
| Contract rules (C-001…C-077, F-001…F-011) | NORMATIVE, but wrongly *sourced* into SKILL.md's own English prose in places (gate bullets) | `protocol/contract/engineering.md` + `.forge/contract/engineering.md`, via `resolve_effective_contract()` |
| Flow stage/gate structure | DERIVED correctly (flows/*.yml) but *re-derived a second time, redundantly*, as English prose in `_gate_instructions()` | `protocol/flows/<id>.yml`, via `resolve_effective_flow()` |
| Reviewer/Resolver independence English block | DUPLICATED (3× per Adapter × 2 Adapters = 6 live copies of the same text) | Should be C-026 alone, rendered once |
| CHG-0025/C-077 Plan Decision sentence | STALE/QUESTIONABLE — hand-present in installed file, absent from current generator, present once in `workflow.md` | C-077 (Contract) — already a compatibility rule *centrally defined in the Contract itself*, not something SKILL.md should reconstruct |
| "Illustrative enforcement hook" disclosure | PROCEDURAL/DOCUMENTARY, honestly scoped, generator-owned (`projection.py:220-232`) — no change needed to its honesty posture | Adapter (accurately describes Adapter-owned mechanism) |
| Interaction language line | DERIVED correctly, single source (`_interaction_language_line()`), governed by C-070–C-073 | Adapter, correctly thin |
| Decision structural rules reference | DERIVED correctly (CHG-0021 precedent) — model to imitate | `src/forge_cli/validation/__init__.py` constants |
| Branch/PR workflow, first-commit baseline, chat-cadence, artifact-publication, FER guidance (`workflow.md:10-72`) | PROCEDURAL, Adapter-owned, largely non-duplicative of Core — but accreted from ≥6 separate Changes (CHG-0023, 0025, 0026, 0028/0031, 0029, 0030/0032/0033/0035) into one undifferentiated block with no internal structure | Adapter (legitimately Adapter-owned operational instruction; needs internal organization, not relocation) |
| `check-manifest-edit.sh` mechanical guard | MECHANICALLY_ENFORCED, but honestly self-described as narrow (`Bash`-only, `.forge/changes/*/{manifest.yml,provenance.yml,review.md}`-only) | Adapter-owned guard; its *coverage claim* is accurate, its *coverage* is incomplete (Section "Guard coverage" below) |

### Guard coverage: Bash-only, and only after Skill invocation

`check-manifest-edit.sh` matches only `Bash` tool_input via a `PreToolUse`
hook registered in `SKILL.md`'s own frontmatter (`_hook_frontmatter_lines()`,
`projection.py:182-190`, matcher `"Bash"`). Two structural gaps, both
already honestly disclosed in `SKILL.md`'s own prose (`SKILL.md:21`,
`:36`) but not yet mechanically addressed:

1. **Tool-equivalence gap.** An `Edit` or `Write` tool call against
   `.forge/changes/*/manifest.yml`/`provenance.yml`/`review.md` is not
   intercepted at all — only `Bash` is matched. The same mutation this
   hook exists to make auditable (in-place rewrite of review-control
   metadata) is reachable through either tool with no guard whatsoever.
2. **Activation-window gap.** Claude Code hooks declared in a Skill's
   frontmatter activate once that Skill has been invoked in the session
   (confirmed by the hook's own comment and this repository's `forge`
   skill instructions, reproduced verbatim at the top of this
   conversation's skill-load output: "active once this skill has been
   invoked in a session, not from session start"). Before first
   invocation, no protection exists for any tool.

Whether project-level `.claude/settings.json` `PreToolUse` hooks (which
would not depend on Skill invocation and could match `Edit`/`Write` in
addition to `Bash`) are the correct mechanical remedy, versus extending
the generated hook script's tool-matcher list, versus leaving the gap
honestly disclosed and unaddressed, is Architecture's decision to make
explicit with tradeoffs — not something Discovery should pre-decide.

### Worktree handling: not yet adapter-aware

The repository already uses Git worktrees operationally (five present
under `.claude/worktrees/agent-*` at Discovery time, evidently created by
prior agent sessions). `AdapterService`/`repository.py` resolve the
publication root and canonical `protocol/` sources relative to the
*project root* passed in at construction time; nothing found in
`service.py`, `repository.py`, or `protocol_resolution/__init__.py`
during this Discovery resolves `cwd` versus the Git worktree's own
top-level versus the main checkout's `.git` common directory. This is a
concrete open question for Architecture (Section 19 of the governing
prompt): does `forge doctor`/`forge validate`/`adapter doctor`, run from
inside a worktree, resolve the correct effective Change, Flow, and
canonical `protocol/` content, or the main checkout's? No test in
`tests/` was found asserting worktree-correct behavior for the Adapter
subsystem specifically (general repository test coverage was not
exhaustively enumerated in this pass; Test Strategy will need a
worktree-specific probe rather than relying on absence-of-evidence here).

### Self-hosting boundary — already stated once, not duplicated further

The `forge` skill's own workflow instructions already state the exact
self-hosting principle the governing prompt asks this Change to record:
*"Repository-native Forge state remains authoritative. Use the effective
Flow and Engineering Contract references in this skill as derived,
repository-local representations; do not redefine their lifecycle here."*
This Change reuses that existing statement as the authority for its own
self-hosting boundary rather than writing a second, competing one: the
Forge Protocol 2 / FULL Flow / Engineering Contract effective at this
Change's `intent` stage (2026-08-24, this repository's `main` at the
commit this branch forked from) governs this Change's own gates,
Review requirements, and Plan Decision boundary, regardless of what
`SKILL.md` shape this Change ultimately produces. Recorded explicitly in
Specification and Architecture per the governing prompt's Section 2.

### Non-authorities excluded from this Discovery

`RELATORIO-SESSAO-2026-08-22.md` (an untracked file at the repository
root) and `ROADMAP.md` were not used as authority for any claim above —
per the governing prompt's Section 3, only current code and current
normative documents (`protocol/`, `.forge/`, `src/forge_cli/`) were
treated as ground truth. Historical Change artifacts (CHG-0002, CHG-0018,
CHG-0021, CHG-0024, CHG-0026, CHG-0034) were read for *design precedent*
(how prior Changes solved adjacent problems) and cited as such, not as
authority for current behavior — current code was always checked directly
where the two could plausibly disagree.
