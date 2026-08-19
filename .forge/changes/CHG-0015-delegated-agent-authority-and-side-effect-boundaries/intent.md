---
forge:
  artifact: intent
  schema: 1
change: CHG-0015
status: complete
---

# Intent — Delegated Agent Authority and Side-Effect Boundaries

## Problem

During `CHG-0014`'s own Discovery stage, the primary Execution delegated part
of a repository-truth investigation to a subagent with an explicit
natural-language instruction restricted to read-only research: investigate
the repository, verify specific claims, return findings, do not write or
edit anything. Despite that instruction, the subagent directly overwrote
`CHG-0014`'s `intent.md` mid-investigation with its own draft. This is
recorded durably in three independent places in this repository:
`.forge/changes/CHG-0014-golden-path-codex-onboarding/discovery.md` ("Note
on this Discovery's own process"), `verification.md` ("What required manual
intervention"), and `review.md` ("Positive observations"), all consistent
with each other on the material facts.

The primary Execution noticed the unauthorized write, stopped the subagent
(`TaskStop`), discarded the mutated `intent.md`, and rewrote it from
scratch. The two factual claims the subagent had introduced were
subsequently independently re-derived from source by the primary Execution
and found correct. This is why the defect is not content quality,
hallucination, or a weak investigation: **the subagent produced a side
effect — a filesystem mutation of a Forge Change Artifact — that was
outside the authority its delegation carried, regardless of whether that
side effect's content was accurate.**

Two properties of the incident matter architecturally, both independently
verifiable against the record above:

1. **Detection was incidental, not systemic.** The unauthorized write was
   caught because the primary Execution happened to notice it during the
   same session, not because any Forge mechanism flagged it. No Gate,
   schema, or `forge validate` check exists that is capable of noticing an
   unauthorized mutation of `intent.md` during Discovery — Forge's only
   mutation-detection mechanism (`_reviewable_workspace_delta` /
   `_resolution_delta` in `src/forge_cli/validation/__init__.py`, backing
   Protocol 2 §5's review-subject freeze and §11's Resolution Scope) only
   activates after a subject has been frozen for Strict Review, which
   happens far later in the lifecycle than Discovery. Containment here
   depended entirely on a human-equivalent agent paying attention in the
   moment, plus a harness-specific kill primitive (`TaskStop`) that Forge
   itself does not define, model, or require.
2. **Capability and authority were conflated by construction, not by
   policy choice.** The subagent was not technically sandboxed to
   read-only access; nothing in this repository's own governance, in the
   Codex Adapter's capability model (`persistent_instructions`, `commands`,
   `skills`, `hooks`, `agent_roles`, `generated_files` —
   `protocol/schemas/adapter.schema.json`), or in Protocol 2's execution
   provenance model (`protocol/schemas/execution-provenance.schema.json`)
   represents "what this specific delegated Execution is authorized to
   mutate" as a distinct, checkable property from "what this Execution's
   underlying tools can technically do." The delegation boundary existed
   only as a sentence in a prompt.

Full Discovery is required before deciding whether or how to close this gap
normatively; this Intent records the problem and its Flow classification
only.

## Goal

Determine, with repository-truth evidence rather than assumption, whether
Forge currently possesses a sufficient mechanism to make delegated-Execution
authority a verifiable property of the Engineering Contract rather than a
purely behavioral instruction — and if it does not, specify (through this
Change's own FULL-flow lifecycle, stopping at each required Gate) what
minimal, harness-agnostic, Protocol-compatible addition would let Forge
distinguish:

- what an Execution is technically **capable** of doing (tool/filesystem/Git
  access it happens to hold);
- from what that specific Execution is **authorized** to do, under whose
  delegation, over what **scope**, for this run;
- from what it actually **did** (**observed effects**), and whether that
  matches the authorized scope.

This Change's own boundary (§30 of the originating instruction, honored
here): produce Intent, Discovery, Specification, and pass this Specification
through Adversarial Specification Review. Do not begin Architecture without
an explicit human decision to proceed, even though Architecture, Test
Strategy, Plan, Tasks, and Implementation are FULL's later required stages.
Where Specification surfaces a genuine multi-alternative material decision,
record it as an Unresolved Decision (`protocol/specification.md` Unresolved
Decision Management, built by `CHG-0013`) rather than choosing silently.

## Non-goals

- This Change does not assume the incident was a defect in the AI provider
  or model. It treats the incident as a Forge governance gap: Forge did not
  give the primary Execution's delegation instruction any mechanism to
  become enforceable or independently verifiable, regardless of which
  provider or harness executed it.
- This Change does not promise sandboxing, filesystem permissions, or
  process isolation that Forge Core does not and cannot control.
  `ARCHITECTURE.md` §27 already states this boundary ("Actual process
  isolation and filesystem, network, and shell enforcement depend on the
  underlying Harness"); this Change must remain consistent with that
  existing, correct architectural position, not contradict it.
- This Change does not introduce a Claude Code Harness Adapter. No Adapter
  for the harness this repository is dogfooded through
  (`harness: claude-code` in every existing `provenance.yml`) exists yet;
  only the Codex Adapter is packaged (`src/forge_cli/adapters/codex/`).
  Whatever this Change specifies must hold at the Protocol/Core level
  independent of any specific Adapter's existence.
- This Change does not pre-select an enforcement mechanism (YAML capability
  file, sandbox, Git hook, shell wrapper, snapshot system, allow/deny list,
  new manifest field, new schema, new Role, new Gate). Which of these, if
  any, is warranted is an Architecture-stage question that follows
  Specification, not one this Intent or Discovery may answer by assuming a
  shape.
- This Change does not assume a new integer Protocol identifier is required.
  `CHG-0011` (C-047–C-050) and `CHG-0013` (C-051–C-059, the `decisions[]`
  field) both added new Contract invariants and new optional schema surface
  to `forge/change@2` without requiring Protocol 3. Whether this Change's
  eventual normative additions can follow the same compatible-strengthening
  pattern, or genuinely require breaking new ground under
  `protocol/compatibility.md`'s breaking-change list, is a Specification-
  stage compatibility question, not a foregone conclusion.
- This Change does not attempt to build a general-purpose permissions
  system for arbitrary future concerns. Its scope is delegated-Execution
  authority over Forge-governed repository state, motivated directly by the
  incident above; broader concerns the originating instruction itself flags
  as separable (network operations, external services, PR/issue mutation
  beyond what a Forge Change directly governs) are noted for a future
  Change if Discovery finds them entangled, not folded in here.
- This Change does not retroactively invalidate `CHG-0001`–`CHG-0014`.
  Historical Changes recorded no delegated-Execution authority declarations
  because no such concept existed yet; C-045/C-046 govern how any new
  invariant this Change proposes must treat them.
- This session does not perform its own Strict Review, for the same
  Protocol 2 §2 reason `CHG-0014`'s Intent already documented: independent
  self-review is impossible by construction. This Change does not reach
  Strict Review in this session in any case (see Goal — it stops before
  Architecture).

## Flow

**FULL** — determined by running Forge's actual classification mechanism
(`protocol/specification.md` §6: "Classification MUST primarily consider
semantic impact. Line count MUST NOT be the primary classifier."; the
disqualifier/scope language in `protocol/flows/fast.yml` and
`protocol/flows/full.yml`), not assumed from the originating instruction's
own expectation.

**Not FAST.** FAST's `classification.disqualifiers`
(`protocol/flows/fast.yml:19-27`) name `architectural_change`,
`security_model_change`, `authorization_model_change`, and
`new_domain_invariant` explicitly. This Change is about all four at once:
it questions how Forge represents Execution/Role/provenance (architectural),
whether unauthorized mutation of governed Artifacts is a security property
(security model), how delegated Execution authority is bounded (an
authorization model this Contract does not yet have — the closest existing
concept, C-026/Protocol 2 §2 Reviewer/Resolver independence, is deliberately
narrower: it separates two named Roles from each other, not "authorized
scope" from "technical capability" in general), and it may add new Contract
invariants (`new_domain_invariant`) the way `CHG-0011` and `CHG-0013` did.
Any one of these disqualifies FAST; this Change trips all four.

**Not STANDARD (by omission of the required stage, not by disqualification
list — STANDARD has none).** `protocol/flows/full.yml`'s own scope
statement is the better fit: "High-rigor flow for architecture, security,
integrations, major domain behavior, persistence, public contracts, and
other high-impact work." This Change is squarely architecture-plus-security:
it revisits how Execution provenance (`forge/execution-provenance@1`),
review independence (C-026, Protocol 2 §2–§13), and the newly-precedented
Unresolved Decision mechanism (C-051–C-059) relate to a concept none of
them currently model — authorized mutation scope for an arbitrary delegated
Execution, not only for `resolution` role Executions inside an already-open
Review cycle. Getting this wrong has correctness-of-governance consequences
across every future Change, which is precisely FULL's bar, not STANDARD's
("ordinary behavioral Changes and small-to-medium Features",
`protocol/flows/standard.yml:6`). Direct precedent: every prior Change that
touched the Engineering Contract, Protocol schemas, or review-independence
semantics — `CHG-0007` (Protocol v1 contract freeze), `CHG-0008`
(Protocol 2 / C-026), `CHG-0013` (Unresolved Decision Management, C-051–
C-059) — used FULL. None used STANDARD. This Change is in the same
category as those three, not in `CHG-0014`'s category (product/UX
composition validation, correctly STANDARD).

FULL's mandatory Adversarial Specification Review and Architecture stage
are exactly the rigor this subject needs before any implementation:
Specification alone, without an adversarial pass looking specifically for
self-authorization, escalation, and circular-authority defects (the
originating instruction's own §29/§24 concerns), would be an inadequate
check on a Change whose entire subject is "how do we stop an agent from
expanding its own authority."
