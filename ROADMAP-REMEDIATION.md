# Roadmap Addendum: First External Validation Remediation

> Not part of the canonical `ROADMAP.md` v1 stage list. This is a
> separate, ordered punch list of fixes originating from a first real
> external validation of Forge outside this repository, kept here at
> the project root so any harness/agent picking up the next item finds
> it without needing prior conversation context.

## Source

- **Report**: after-action report from the agent that conducted
  `CHG-0001-sanctum-authentication` (Laravel Sanctum authentication) in
  an external repository (`crud-produtos`, Laravel 13), 2026-08-20, using
  the Claude Code Adapter.
- **Why it matters**: `ROADMAP.md`'s own "External Validation Matrix"
  lists Laravel/PHP as an open ecosystem with "no real target repository
  ... in any ecosystem other than this one." This report is that first
  entry. It confirmed Forge's central value proposition (adversarial
  Review found a real security bug — a login timing side-channel — that
  conventional tests could not) while also surfacing eleven concrete
  friction/tooling gaps.
- Each item below was verified against this repository's actual source
  before being turned into a roadmap item — see the corresponding Forge
  Change's `discovery.md` for exact file:line evidence once a Change
  exists.

## Status

| Priority | Item | Slug | Status | Change |
| --- | --- | --- | --- | --- |
| P0 | Project Schemas/enums into adapter references | `adapter-reference-schema-projection` | **Done** | `CHG-0021` (merged, PR #13) |
| P0 | `forge change new <slug>` scaffolding | `change-scaffolding-cli` | **Done** | [`CHG-0022`](.forge/changes/CHG-0022-change-scaffolding-cli/) |
| P0 | Document first Change with no prior Git history | `first-change-baseline-guidance` | **Done** | [`CHG-0023`](.forge/changes/CHG-0023-first-change-baseline-guidance/) |
| P1 | `forge doctor` detect zero adapters installed | `adapter-readiness-doctor-check` | **Done** | [`CHG-0024`](.forge/changes/CHG-0024-adapter-readiness-doctor-check/) |
| P1 | Real semantics for `plan.md status: approved` | `plan-approval-semantics` | **Done** | [`CHG-0025`](.forge/changes/CHG-0025-plan-approval-semantics/) |
| P1 | Document skill-propagation latency after adapter install | `skill-propagation-diagnostics` | **Done** | [`CHG-0026`](.forge/changes/CHG-0026-skill-propagation-diagnostics/) |
| P1 | Review cost proportional to diff size (RFC-level) | `review-cost-proportionality` | **Done** | [`CHG-0027`](.forge/changes/CHG-0027-review-cost-proportionality/) |
| P2 | Chat communication cadence guidance | `chat-cadence-guidance` | **Done** | [`CHG-0028`](.forge/changes/CHG-0028-chat-cadence-guidance/) |
| P2 | Suggest publishing key artifacts as Artifact | `artifact-publication-suggestion` | **Done** | [`CHG-0029`](.forge/changes/CHG-0029-artifact-publication-suggestion/) |
| P2 | Document real limits of Reviewer "independence" | `reviewer-independence-disclosure` | Open | — |

Slugs have no fixed `CHG-NNNN` number reserved, matching `ROADMAP.md`'s
own stated convention: Forge assigns the next stable identifier when a
stage begins as an actual repository-native Change. The last Change assigned
in this repository's history is `CHG-0023`; the next free number is
`CHG-0024`.

## P0 — Block healthy adoption

### 1. `adapter-reference-schema-projection` — DONE (`CHG-0021`)

Both Adapters now project `references/decision-rules.md`, generated
directly from `forge_cli.validation`'s own Decision-structural-rule
constants (`class`/`materiality`/`status`/`authority`/`resolved_via`
enums, `class` → valid `owning_artifact`, `class` → authority floor).
The `resolved_via` invalid-value error message now states the expected
values. See `.forge/changes/CHG-0021-adapter-reference-schema-projection/`
for the full artifact trail (Intent through Completion, including a real
BLOCKER an independent Strict Review found and a Resolver fixed).

### 2. `change-scaffolding-cli` — DONE (`CHG-0022`)

**Origin**: the original report's Achado #3 — no `forge change new`
command exists; every Change artifact (`intent.md`, `specification.md`,
`manifest.yml`, etc.) had to be hand-written by analogy to an example
Change from a *different* repository that happened to be present on the
machine. This was the direct cause of the two schema errors
`CHG-0021` fixed the discoverability half of.

Implemented by this Change's Specification:

- a `forge change new <slug>` command that generates
  `.forge/changes/CHG-NNNN-<slug>/` with the artifact set the *active
  Flow* requires (STANDARD vs. FULL differ — see `protocol/flows/*.yml`
  `stages:`), each file carrying correct `forge:` frontmatter
  (`protocol/artifact-structure.md` §4) and placeholder sections
  (`## FR-001 — <requirement>`, etc.);
- reuse the same plan-before-mutation transparency `forge adapter
  install`/`forge adapter plan` already establish (`CREATE forge_owned
  <path>` per file, shown before acting);
- `manifest.yml`'s scaffold should pre-fill only schema-*valid* enum
  placeholders — this is the concrete dependency on `CHG-0021`: the
  scaffold must not reintroduce the same invalid `resolved_via`/
  `owning_artifact` guesses the original report made, and can now derive
  correct values the same way `render_decision_rules_reference()` does
  (single source of truth, not a second hand-typed template);
- must work offline, from an installed wheel, matching every other CLI
  command's constraint (`ROADMAP.md` "Adapter CLI & Codex Installation
  UX" exit criteria).

**Explicitly not required**: a full interactive wizard; scaffolding for
any Flow this repository does not already define; changes to
`protocol/schemas/*.json`.

### 3. `first-change-baseline-guidance` — DONE (`CHG-0023`)

**Origin**: Achado #5 — the report's own repository was on its first Git
commit; nothing in the Contract/`SKILL.md` covers how to establish a
"before" baseline in that case, and the agent's own heuristic attempt
excluded some pre-existing files from the baseline commit by mistake,
caught only by Strict Review.

**Scope**: an explicit rule in the Contract or the Adapter-projected
skill instructions: *if this is the repository's first commit, commit
the complete pre-existing state — no file excluded — before starting
Implementation.* Should be demonstrated in at least one `examples/`
entry, not only stated in prose.

Implemented by `CHG-0023`: RFC-0003, C-076 in both effective Contract
representations, identical Codex/Claude Code workflow guidance, and the
illustrative `examples/first-change-baseline/` fixture.

## P1 — Reduce friction and cost without weakening rigor

### 4. `adapter-readiness-doctor-check`

`src/forge_cli/doctor/__init__.py`'s `_adapter_readiness_checks` (as of
`CHG-0021`, unchanged by it) silently produces zero `DoctorCheck` entries
when **no** Adapter has an installation record at all — confirmed by
reading the function directly: it `continue`s past every driver with no
record, so a workspace with `.forge/` initialized but no Adapter
installed gets no warning anywhere. Add an explicit `warning` check for
this exact state, suggesting `forge adapter install`.

### 5. `plan-approval-semantics`

`plan.md status: approved` is written by the agent itself with no real
human act behind it in the normal flow — the same shape of self-approval
Contract `C-055` already forbids for human-authority Decisions, but
nothing analogous exists for the Plan artifact or the `plan_complete`
gate (`protocol/flows/standard.yml`/`full.yml`). Decide: require a real
human checkpoint at this boundary, or rename the field so it stops
implying an approval that did not happen.

### 6. `skill-propagation-diagnostics`

After `forge adapter install claude-code`, the newly installed skill is
not immediately available via `Skill({skill: "forge"})` in the same
session — a harness-runtime limitation outside this repository's
control. Document it explicitly in the adapter's own install output and
in the projected `SKILL.md`, so an agent does not have to rediscover the
delay.

### 7. `review-cost-proportionality` (RFC-level, not a direct implementation Change)

The only lever for review cost/time today is the binary Flow choice
(FAST/STANDARD/FULL); security/auth work is disqualified from FAST by
`protocol/flows/fast.yml`'s own `disqualifiers`, so a small, well-scoped
auth feature has no lighter option even when the diff itself is small.
Requires an RFC before any implementation Change, per `CONTRIBUTING.md`'s
RFC trigger ("Review semantics") — must not weaken `C-023`'s adversarial
requirement.

## P2 — Improve experience without touching process integrity

### 8. `chat-cadence-guidance`

No guidance today on how much of a Change's progress should be narrated
in chat versus only recorded in artifacts. Add a non-binding suggestion
to the projected skill instructions: narrate stage transitions, not
every individual command.

### 9. `artifact-publication-suggestion`

Nothing suggests publishing `review.md`/`specification.md` as a
shareable Artifact when a key stage completes, so the human-readable
detail of an adversarial Review often never reaches the user inside the
chat itself. Add a non-binding suggestion to the projected skill
instructions.

### 10. `reviewer-independence-disclosure`

The Reviewer sub-agent's independence today is *execution* independence
(distinct Execution/Execution Context), not vendor/model independence —
a real, current limitation the Contract does not currently state
explicitly. Add a Contract note clarifying the exact guarantee, and
consider allowing an explicit hint-free review mode as a stricter
option (this repository already demonstrated the value of a genuinely
hint-free Review three times over in `CHG-0021` alone).

## Sequencing note

`change-scaffolding-cli` (#2) is next. It has no hard dependency left —
`adapter-reference-schema-projection` (#1) already shipped the piece it
needed (a real source of truth for valid `manifest.yml` enum values).
`first-change-baseline-guidance` (#3) can proceed in parallel; it is
documentation-only and touches no code #2 also touches.
