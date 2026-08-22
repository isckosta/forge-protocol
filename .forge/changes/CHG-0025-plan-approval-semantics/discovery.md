---
forge:
  artifact: discovery
  schema: 1
change: CHG-0025
status: complete
---

# Discovery — Plan Approval Semantics

## Executive Summary

**Recommendation: Option A — a recorded human checkpoint, with an RFC
first. Confidence: High (0.86).** Renaming `approved` would improve honesty
but would not solve the authority problem: an agent could still write
`ready` or `complete` and cross the same Gate without evidence of an
authorization act. The repository already treats human authority as a
semantic property that cannot be substituted by agent confidence (C-054 and
C-055), and the Plan/Implementation boundary is a lifecycle Gate. Therefore
the durable fix belongs in canonical Contract/Gate semantics, not only in
Adapter prose.

The recommendation does not yet choose the concrete repository-native record
or validation surface. That belongs in Specification and Architecture after
the RFC decision is accepted. No implementation or Contract edit is made by
this Discovery.

## Root Cause and Data Flow

The Standard Flow declares `plan_complete` in
`gates.before_implementation.require` at `protocol/flows/standard.yml:39`.
The Full Flow declares the same Gate at `protocol/flows/full.yml:53`. These
are canonical requirements, but they do not identify an asserting authority
or require a recorded authorization event.

The Plan convention uses `status: approved` in current Change artifacts and
the manifest uses `plan: approved`. The scaffolded Plan text also describes
the first work item as approved, while separately saying that reaching
`plan_complete` is not authorization. That leaves two meanings adjacent:
technical readiness is represented by a field whose name implies human
approval, and the boundary warning has no machine-checkable evidence.

The v2 Change Schema confirms the gap: `artifacts` is only constrained as an
object and has no schema for Plan status, Plan authority, or approval
evidence. The validation module has a concrete C-055 check for Decisions at
`src/forge_cli/validation/__init__.py:465`:
`authority: human` cannot be paired with
`resolved_via: autonomous_decision`. No analogous Plan check exists.

CHG-0021 supplies corroborating process evidence, not an existing mechanism.
Its `provenance.yml` implementation-001 record says that the execution
received explicit human approval ("Sim") at the Plan/Implementation
boundary, while also stating that no provider-native attestation is claimed.
That demonstrates a useful human act but also demonstrates that the current
repository records it only as execution prose, not as a canonical Gate
condition.

## Option A — Recorded Human Checkpoint

This option extends the existing authority model to the Plan/Implementation
boundary. It is consistent with:

- C-055, which requires an explicit human act for human-authority Decisions;
- C-062, which prohibits delegated self-authorization through an
  authority-defining Artifact;
- C-065, which requires fail-closed behavior when authorization is
  indeterminate; and
- the existing Flow Gate, whose purpose is to control entry into
  Implementation rather than merely label a Markdown file.

It changes canonical Gate semantics and likely adds a new repository-native
piece of evidence or validation rule. `CONTRIBUTING.md` explicitly requires
an RFC before material changes to Gate semantics or the Engineering Contract.
The RFC should therefore precede any Contract or executable implementation
commit. RFC-0003 is the closest process precedent: its RFC was committed
before the specification and implementation commits in the same CHG-0023
history, and the RFC format is the one used here. The precedent does not
show a separate RFC-only merge as a requirement; it does show that the RFC
must exist before the material implementation work.

## Option B — Rename, Do Not Gate

This option would replace `approved` with a term such as `complete` or
`ready`, and propagate it through the Contract, artifact structure, manifest
convention, projections, schemas, and historical references where permitted.
It would reduce the false implication that an agent-authored status is a
human act. However, it would not establish who may cross `plan_complete`,
would not fail closed on missing authorization, and would leave the exact
authority defect described by C-055 unresolved. It is therefore a useful
compatibility or wording component of Option A if needed, but insufficient as
the primary remediation.

The repository's RFC trigger also covers material Change semantics and the
Engineering Contract. Because the existing Plan field is documented as
approved content (for example in `protocol/artifact-structure.md:47`) and
its meaning is consumed by Change artifacts, a standalone rename would at
minimum require an explicit compatibility analysis. It should not be used as
a way to bypass the RFC gate.

## `specification_gate_passed` Assessment

The same silent-approval shape is **not established for this Gate** by the
current evidence. `specification_gate_passed` appears as a Flow Gate and in
Adapter projection tests, but there is no corresponding `specification:
approved` artifact status in the audited current Change conventions; the
Specification artifact is `status: complete`. The v2 Schema likewise does
not define a specification approval field. The present issue is therefore
the missing authority evidence for the Plan/Implementation crossing, not a
second undocumented human approval field.

Specification must still state that `specification_gate_passed` is a
technical lifecycle Gate and not evidence of human authorization. A future
Change may extend the same authority mechanism to that Gate only if it
introduces a real human-authority requirement; this Change does not broaden
the requirement without such evidence.

## Flow Classification

The effective classification is **FULL**. FAST is explicitly disqualified by
`architectural_change`, `authorization_model_change`, `new_domain_invariant`,
and `major_public_contract_change` in `protocol/flows/fast.yml`. This Change
changes the meaning of crossing a canonical Gate and likely updates the
Engineering Contract, so it is not a localized validation correction. FULL's
Specification Review, Architecture, Test Strategy, Tasks, TDD when
applicable, Verification, Knowledge Capture, and independent Strict Review
stages are proportionate to that semantic impact. The Standard Flow would
not provide the required adversarial specification checkpoint.

## RFC and TDD Decision

An RFC is required before the selected Option A changes the Contract or Gate
semantics. The RFC should be recorded as the first material decision of this
Change, following the established RFC-0003 format; no Contract or runtime
behavior should be changed before it is accepted through the repository's
normal PR process.

The RFC text itself is prose and has `tdd: not_applicable` semantics. Any
subsequent authorization record, Gate validation, or CLI-visible behavior is
executable and must have a real RED test observed before GREEN, under C-016
and C-021. This Discovery does not claim TDD evidence for either portion.

## Open Questions for Specification

1. What existing repository-native record can prove the human act without
   making transient chat history authoritative?
2. Which exact Gate assertion consumes that record, and how does it fail
   closed when the record is absent or ambiguous?
3. How are existing Protocol 1/2 Change records preserved under C-045 and
   C-046, and what prospective adoption boundary is required?
4. Does the selected record need schema support, or can existing provenance
   and manifest structures express it without weakening validation?
