---
forge:
  artifact: discovery
  schema: 1
change: CHG-0050
status: complete
---

# Discovery — CHG-0050 Review Experience Modes

## Executive Summary

The two capabilities this Change actually needs to build — a live point
that resolves an "effective review profile" from a developer-facing
mode preference, and a way to observe which Review phase is active —
**do not exist today in any form**. Review Profile (`focused`/
`standard`/`strict`, RFC-0007/CHG-0048) is a static value read directly
off the canonical Flow YAML at Adapter-projection time
(`review.get("profile", "strict")` in both
`src/forge_cli/adapters/claude_code/projection.py:92` and
`codex/projection.py:71`); there is no function that resolves an
"effective profile" from anything beyond the Flow file, and no
per-Change or persistent-preference field exists anywhere in the
schema today. Review guidance itself is a **static Markdown/instruction
projection**, generated once at `forge adapter install` time — there is
no runtime state channel a Harness could read or write to say "I am in
Discovery now" or "2 findings remain."

The good news bounds this Change's real scope: every hard invariant it
must not disturb is already implemented in Core, already
profile-independent, and reusable as-is. Targeted re-review after
Resolution, escalating to a full Initial Review only when the
Resolution mutates outside its declared scope, is already the real
behavior of `_validate_resolution_verification` in
`src/forge_cli/validation/__init__.py` (the "FR-010 Full Review
Escalation" rule) — CHG-0050 does not need to invent this, only expose
it. The Convergence Limit (C-049, hardcoded at 2, Core-derived rather
than self-declared) already prevents any profile, including a future
`Thorough` mode, from authorizing unlimited loops — no special-casing
is needed for that guarantee to hold. This means CHG-0050 is primarily
an **additive UX, schema, Adapter-projection, and observability layer**
on top of stable Core mechanics, not a rewrite of Review itself — but
the two missing pieces (profile resolution from a mode preference, and
phase observability) are real, undesigned gaps that Architecture must
resolve deliberately, not by extension of an existing pattern.

## Investigation

### Review Profile resolution today

No function named `resolve_effective_review_profile` (or equivalent)
exists. `profile` is a flat, per-Flow constant declared once in each
canonical Flow file:

- `protocol/flows/fast.yml:68-72` → `focused`
- `protocol/flows/standard.yml:62-66` → `standard`
- `protocol/flows/full.yml:77-81` → `strict`

`protocol/versions/2/policies/review.yml` documents this explicitly in
its inline comment: the policy's own `profile` field is "the Protocol's
own highest-tier review posture... The profile that actually applies to
a given Change is derived from that Change's effective Flow... never
from this policy alone."

The only code that touches `profile` beyond reading it verbatim is a
**floor validator**, not a resolver:
`src/forge_cli/validation/__init__.py:773-786`
(`_validate_review_profile_floor`, `_PROFILE_RANK = {"focused": 0,
"standard": 1, "strict": 2}`) rejects a project-flow override
(`.forge/flows/<flow>.yml`) that declares a profile *weaker* than the
Flow's canonical floor (`E_FORGE_REVIEW_PROFILE_BELOW_FLOOR`). It never
raises a profile automatically and has no notion of a per-Change
preference — it only fails closed on an explicit downward override.
`resolve_effective_flow` (`src/forge_cli/protocol_resolution/__init__.py:66-112`)
merges canonical and project Flow data without picking a "winning"
profile; that choice is left to whichever consumer reads the result.

Implication: a UX mode that is supposed to influence the effective
profile (while never going below the Flow floor) has no existing
integration point to extend — Architecture must design this
resolution function from scratch, deciding where it lives (Core
`protocol_resolution`, a new module, or the existing floor validator
extended) and how it composes with the already-existing project-flow
override.

### CLI/Harness surface for Review today

No `forge` command reports live Review status or progress. The full
command surface (`src/forge_cli/app.py`, `change_cli.py`,
`adapter_cli.py`, `experience_cli.py`) is: `version`, `init`,
`validate`, `migrate`, `doctor`, `adapter [...]`, `change [new |
merge-check]`, `experience [...]`. The closest existing thing,
`forge change merge-check`, is **post-hoc and diff-based**: it
diffs two Git refs (`--base`/`--head`), loads `manifest.yml` /
`provenance.yml` / `review.md` from the head revision via `git show`,
and emits a single verdict (`ready`/`blocked`/`operational`) plus a
flat list of `MR-xxx` diagnostics (`src/forge_cli/merge_readiness/evaluator.py`).
It has no concept of a currently-active Discovery/Findings/Resolution/
Re-review phase — it only ever answers "is this commit range mergeable
right now." `forge doctor` does not mention Review at all.

Review guidance for the Harness is generated once, as static text, at
`forge adapter install` time: `_gate_instructions` in both
`src/forge_cli/adapters/claude_code/projection.py:92-122` and
`codex/projection.py:71-101` reads each Flow's `gates.*` sections and
`review.profile` and renders fixed instruction lines (e.g. "Completion
requires Review to pass, at the `focused` profile: ..."). The shared
Reviewer/Resolver-independence prose lives once in
`src/forge_cli/adapters/review_independence.py`
(`REVIEWER_RESOLVER_INDEPENDENCE_LINES`, `REVIEW_PROFILE_INSTRUCTION`)
and is imported by both Adapters to avoid duplication — this is the
existing, real precedent for how profile-specific instruction text is
already shared across Adapters, and the natural place additional
mode-aware instruction text would be added.

Implication: today "the Harness knows what to do" only via fixed
instruction text baked in at install time. There is no live channel a
Harness could update mid-Review to make phase progress observable —
this has to be designed, and its guarantee level (mechanically
verifiable vs. narrated-only) is a genuine open question (see Open
Questions).

### Persistent configuration mechanisms

`.forge/forge.yml` (`schema: forge/project@1`,
`protocol/schemas/project.schema.json:14-24`) has a `review.strict`
field, but it is `const: true` — locked, vestigial. RFC-0007 already
confirmed this in prose (`docs/rfcs/0007-proportional-review-profiles.md:121-123`):
"not read by any CLI code today... is not the right integration
point." Grep confirms it: the only field under `review.*` in
`forge.yml`'s schema actually read by code is
`review.convergence.allow_residual_risk_acceptance`, consumed by
`_residual_risk_permitted` (`src/forge_cli/validation/__init__.py:115-119`)
to authorize `convergence_decision.option: accept_residual_risk`. This
is real precedent for "a persistent project-level Boolean that changes
Review's authorized outcomes" — but it is a single narrow risk-flag,
not a named mode.

`.forge/flows/<flow_id>.yml` (`schema: forge/project-flow@1`,
allowed keys `{schema, flow, review, testing}` per
`src/forge_cli/protocol_resolution/__init__.py:32`) is the canonical,
already-wired, schema-legal place RFC-0007 explicitly anticipated
(RFC-0007 §8, decision point 12) for a project to declare a
*stricter-than-floor* profile override. It is scoped **per Flow**, not
per Change and not as a named mode — it cannot by itself represent
"this developer generally prefers Thorough" as a cross-Flow,
cross-Change preference.

No field exists today, anywhere, for a **per-Change** review-mode
choice — `manifest.yml`'s `forge/change@2` schema has no such field.

Implication: a persistent, developer-facing mode preference and a
per-Change mode override are both new schema surface. The per-Flow
override file is a partial precedent for "project can require more,
never less," but is the wrong shape for a named, cross-Flow preference
— Architecture needs a new, additive field (or file) rather than
repurposing either existing mechanism.

### Merge readiness as an observability candidate

`src/forge_cli/merge_readiness/evaluator.py` already distinguishes
`initial_review` from `resolution_verification` in the `iterations[]`
data it reads (schema: `protocol/schemas/change-v2.schema.json`,
`review.iterations[]` with `kind`, `full_review_required`,
`new_material_findings`, `finding_classes`, `convergence_decision`).
Diagnostic `MR-004` was already renamed from `"STRICT REVIEW NOT
READY"` to the profile-neutral `"REVIEW NOT READY"`
(`evaluator.py:90`) — confirming RFC-0007 decision point 14 already
shipped. But this data is read only **after the fact**, on demand, via
`forge change merge-check` comparing two Git refs; nothing runs
continuously or exposes "which phase is active right now." The
`iterations[]` structure is a usable **source of record** for a phase
timeline, but the live, in-progress signal CHG-0050 needs does not
exist and cannot be retrofitted from merge-readiness alone.

### Review lifecycle: targeted re-review already exists

The Intent's requirement to default re-review to the resolved
findings and delta, restarting full Discovery only when warranted, is
**already the enforced behavior**, not a gap:
`_validate_resolution_verification` in
`src/forge_cli/validation/__init__.py` computes a Resolution Delta from
Git (`_resolution_delta`) and compares it against the Resolution's
declared scope; any mutation found outside that scope
(`_uncovered_paths`) forces `status: failed` with
`full_review_required: true` (lines ~157-161). Once
`full_review_required: true` appears on an iteration, the rule (commented
"FR-010: Full Review Escalation", lines ~166-172) forbids the next
iteration from being another scoped `resolution_verification` — only a
fresh `initial_review` is legal. CHG-0050 should reuse this invariant
verbatim rather than reinvent a targeting policy; its job is to make
this existing behavior visible to the developer as "why did this
become a full review," not to change when it triggers.

### Convergence Limit already bounds every profile, including a future Thorough

C-049 is mechanically enforced, not merely documented, in the same
function: it counts consecutive failed `resolution_verification`
iterations with `new_material_findings > 0`, hardcodes the limit at 2
(matching `protocol/versions/2/policies/review.yml`'s
`convergence_limit: 2`), and is **Core-derived, not self-declared** — a
manifest's own `consecutive_unconverged_verifications` must match
Core's recomputed value or it is a Finding. On reaching the limit,
`review.status: passed` is blocked until an explicit
`convergence_decision` (`new_full_review` /
`return_to_earlier_phase` / `accept_residual_risk` /
`abort_or_supersede`) is recorded, with `accept_residual_risk` gated
behind the project's explicit permission flag (previous section).
Nothing in this function reads `profile` at all — the limit already
applies identically regardless of profile. This directly satisfies the
Intent's "Thorough does not authorize unlimited loops" requirement
without CHG-0050 adding any new enforcement: it only needs to avoid
building a parallel path that could bypass this one.

### Adapter architecture is already repository-agnostic

`src/forge_cli/adapters/` separates a generic orchestration layer
(`service.py`, `driver.py`, `manifest.py`, `plan.py`, `planner.py`,
`publisher.py`, `repository.py`, `registry.py`, `configuration.py`,
`diagnostics.py`) from two concrete implementations
(`claude_code/`, `codex/`), each supplying only a `HarnessDriver` and a
`projection` function. `AdapterService` resolves protocol compatibility
and builds/publishes a plan generically for any repository with `.forge/`
initialized; `resolve_effective_flow`/`resolve_effective_contract` are
parametrized by `project_root`, not hardcoded to this repository. This
already satisfies the Intent's "must work in any Forge-enabled
repository" requirement by construction — CHG-0050 only needs to keep
following this existing pattern (no forge-protocol-specific state),
not build new infrastructure for it.

Separately, `src/forge_cli/capabilities/` (CHG-0047, "capability
architecture foundation") exists as a foundation with no real
Capability published yet: `model.py` defines a `Capability` dataclass
(id, schema, identity, purpose, applicability, inputs, behavior,
outputs, evidence_expectations, source_path) and `loader.py` parses a
single `CAPABILITY.md` file (frontmatter + required sections). No
`CAPABILITY.md` exists anywhere in the repository today. If Review
Experience Modes is framed as a Capability, it would be the first real
one — worth a deliberate Architecture-stage decision, not an
assumption.

### No prior art for a Review-mode UX layer

`grep -rniE "review mode|thorough review|fast review|recommended
review|review preference|review ux"` across `docs/`, `src/forge_cli/`,
and `protocol/` returns nothing beyond RFC-0007's own unrelated phrase
"Flow-invariant Review model." No RFC, ADR, comment, or TODO proposes a
developer-facing Recommended/Fast/Thorough vocabulary anywhere in this
repository's history. CHG-0050 is the first proposal of this kind —
there is no existing design to reconcile with, but also no precedent
to lean on for the two genuinely new mechanisms this Change needs
(mode-to-profile resolution, phase observability).

### Protocol 2 Contract text already supports a profile-scoped model

`protocol/versions/2/contract/engineering.md` (the live Protocol 2
Contract — `protocol/contract/engineering.md` is Protocol 1 and is
intentionally left untouched, per `protocol/compatibility.md`'s
CHG-0048 entry) already carries RFC-0007's revised text: C-022 requires
Review "at the rigor and posture defined by its Flow's Review
Profile," C-023 scopes the exhaustive-search obligation to `strict`
only, and C-031 clarifies that `focused` "narrows Review's search
obligation, not its authority to block on a real Finding." CHG-0050
does not need to touch these clauses to introduce a UX mode layered on
top of the existing profile concept — it only needs to guarantee, by
construction, that mode selection can never resolve to a profile below
what these clauses (via Flow) already require. (Note for anyone
reading this Discovery later: the `forge` skill's own bundled reference
copy of the Engineering Contract is a Protocol-2-labeled snapshot that
still shows the pre-RFC-0007 C-022/C-023/C-031 wording — it is stale
relative to the repository's live `protocol/versions/2/contract/engineering.md`.
This Discovery relied on the repository file, not the skill's cached
copy, consistent with the skill's own instruction that repository-native
state is authoritative.)

## Open Questions

Two decisions were identified here as Contract/product/architectural in
nature. Both are now resolved; this section keeps the reasoning and
the resolution as repository-native evidence, following the same
pattern RFC-0007 used for its own open normative question (resolved
in-chat with the human maintainer, recorded in
`docs/rfcs/0007-proportional-review-profiles.md`'s "Open normative
question" section).

**OQ-1 — Does this Change warrant a preceding RFC, and does Flow
escalate to FULL?** CHG-0050 introduces a new persistent schema field
(per-Change mode, and a cross-Change developer preference), a new
Harness-observability contract projected into at least two Adapters,
and a new default-visible developer experience for every
Forge-enabled repository — matching `fast.yml`'s own disqualifiers
(`architectural_change`, `major_public_contract_change`) and
Contract F-008's precedent (`docs/rfcs/`/`docs/adr/` required for
architectural knowledge that outlives one Change), exactly as CHG-0048
found for a comparable-scope proposal.

**Resolved: yes to both** (`DEC-001`, `manifest.yml`; class:
architectural, authority: agent, `resolved_via: evidence`). This is an
evidence-grounded classification call within agent authority (no
human-authority floor applies to the `architectural` class per the
Decision Rules), consistent with CHG-0048's own `DEC-001` handling the
same kind of call the same way. Flow is escalated STANDARD → FULL in
`manifest.yml`; an RFC (RFC-0008) will be authored before
Specification.

**OQ-2 — What guarantee level should Review-phase observability carry?**
Two designs were both viable and had different honesty implications
(this repository already has real precedent for being explicit about
this distinction — C-072/C-073's Harness-honesty framing for
interaction-language projection): (a) *Projection-only*: Adapters
instruct the Harness to narrate its current phase in the conversation;
nothing is mechanically verified, so a Harness that fails to narrate
correctly cannot be detected by Core, and a new Harness-honesty
Contract clause would be needed to say so explicitly. (b)
*Schema-tracked*: a new field (e.g. a `phase` value on
`review.iterations[]` or a top-level `review.current_phase` in
`manifest.yml`) that Core can read and validate, at the cost of new
schema surface and a new obligation on the Harness to keep it current.
This is `product`-class (the Decision Rules' human-authority floor
applies) because it changes the actual guarantee Forge makes to the
developer, not just an implementation choice.

**Resolved: (b), schema-tracked.** The human maintainer chose this
option explicitly in the active chat session on 2026-08-30, preferring
a mechanically verifiable guarantee over a narration-only one. This
also means no new Harness-honesty Contract clause (the (a)-only
consequence) is needed for this Change — the guarantee is enforced by
Core validation, not by an honesty disclaimer about unverifiable
Harness behavior.
