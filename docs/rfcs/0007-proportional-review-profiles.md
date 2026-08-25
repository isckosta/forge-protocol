# RFC-0007 — Proportional Review Profiles

Status: Accepted for Protocol 2

## Summary

This RFC proposes replacing Forge's single, Flow-invariant Review model
— every Change, regardless of Flow, undergoes identically strict,
adversarial Strict Review — with three canonical **Review Profiles**
bound to Flow: `focused` (FAST), `standard` (STANDARD), `strict`
(FULL). The Review lifecycle, evidence requirements, Finding
severities, Resolution, Resolution Verification, Convergence Limit,
and repository-native provenance (C-026) remain a single, unchanged
mechanism. A profile changes **posture and scope** — what a Reviewer is
instructed to emphasize and how exhaustively it must search for
rejection grounds — not evidence rigor, independence, or any blocking
semantics. Every Change continues to require Review; not every Change
requires the `strict` profile's adversarial posture.

This RFC explicitly **supersedes** RFC-0005's non-goals barring
"changes to current Flows, Review policy, Contract, schemas, or CLI"
and "removal of adversarial Review" — narrowly, for the review-profile
concept this RFC defines, and only to the extent this RFC's own
Decision below authorizes. RFC-0005's proposal (a descriptive Review
Calibration Profile layered *on top of* a uniformly adversarial model)
remains a materially different, narrower idea; this RFC does not adopt
RFC-0005's specific calibration-dimension vocabulary, and RFC-0005
should be marked `Status: Superseded by RFC-0007` once this RFC is
accepted.

## Motivation

Today, `protocol/flows/fast.yml`, `standard.yml`, and `full.yml` each
declare an identical `review: {required: true, strict: true,
adversarial: true}` block, and Contract C-022/C-023 state this as a
flat, Flow-independent obligation: "Every Change MUST undergo Strict
Review" / "Strict Review MUST actively search for reasons to reject
the Implementation." A one-line copy-fix Change (FAST) and a
Protocol/Contract-level architectural Change (FULL) both pay the same
adversarial-review cost today, even though Forge already has a
semantic Flow classifier expressly designed to distinguish exactly
this kind of impact difference (`fast.yml`'s own `disqualifiers` list:
`architectural_change`, `security_model_change`,
`authorization_model_change`, `major_public_contract_change`, etc.).
The classifier already does the hard work of separating low-impact
from high-impact Changes; Review today does not use that signal at
all — `src/forge_cli/validation/__init__.py`'s review/convergence logic
never reads `manifest.flow`.

Two design patterns already exist in this repository for
Flow-conditional stage behavior — `full.yml` alone adds
`specification_review` (`mode: adversarial`) and `tasks` stages, and
`protocol/versions/2/policies/review.yml`'s
`reviewer_resolver_separation.independence` field is already
Flow-keyed (`{fast: execution_context, standard: execution_context,
full: execution_context}`), even though all three values are
identical today — confirming this vocabulary was anticipated but never
populated with real per-Flow variance for Review itself.

## Decision proposed

1. Introduce a `profile` field (enum: `focused | standard | strict`)
   to each Flow's `review:` block (`protocol/flows/fast.yml` →
   `focused`, `standard.yml` → `standard`, `full.yml` → `strict`) and
   to `protocol/versions/2/policies/review.yml`'s canonical Protocol 2
   policy. `required: true` remains unconditional on all three Flows —
   Review is never optional.
2. `focused` (FAST): Review is scoped to the actual diff, regressions
   it could introduce, the specific Requirement(s) it targets, and any
   material Finding a Reviewer actually observes — not an unrestricted
   search across the whole subject for any conceivable rejection
   ground.
3. `standard` (STANDARD): Review evaluates Specification compliance,
   correctness, and implementation quality with genuine, evidence-based
   scrutiny, without the `strict` profile's obligation to exhaustively
   search for adversarial grounds beyond what the Change's own claimed
   scope and evidence make relevant.
4. `strict` (FULL): unchanged from today's model — Strict Review
   remains fully adversarial, actively searching for reasons to
   reject, exactly as C-023 states today.
5. C-022 is revised to decouple "Review is required" from "Review is
   strict": *"Every Change MUST undergo Review, at the rigor and
   posture defined by its Flow's Review Profile. `focused` and
   `standard` remain genuine Review with real rejection authority —
   never a rubber stamp, diff-only inspection, or passing-tests-only
   sufficiency."* C-023 is scoped: *"The `strict` Review Profile MUST
   actively search for reasons to reject the Implementation. `focused`
   and `standard` Review Profiles MUST reject on any material Finding
   they actually identify, without the added obligation to
   exhaustively search beyond the Change's own declared scope and
   evidence."*
6. Everything else is explicitly **unchanged**, regardless of profile:
   C-024 (TDD is reviewable), C-025 (evidence for BLOCKER/MAJOR),
   C-026 (Reviewer/Resolver independence, execution/context
   separation, provenance binding), C-027 (blocking Findings block
   Completion), C-047–C-050 (Resolution Verification scoping,
   Out-of-Scope Mutation, Convergence Limit, unrelated-latent-finding
   handling), C-059 (a Reviewer discovering a missing material Decision
   requests changes, regardless of profile — this is triggered by
   discovery, not by a search mandate, so it is profile-orthogonal by
   construction), C-067–C-068 (Artifact structure guidance,
   outcome-before-evidence). Finding severities
   (BLOCKER/MAJOR/MINOR/observation), the Convergence Limit (2), and
   repository-native provenance are a single mechanism shared by all
   three profiles.
7. C-031 is clarified, not weakened: *"FAST's Review Profile
   (`focused`) MUST NOT remove applicable TDD, Verification, Review, or
   Documentation Impact evaluation — it narrows Review's search
   obligation, not its authority to block on a real Finding."*
8. Schema changes: `profile` is a new, optional (defaulted) enum field
   in `protocol/schemas/change-v2.schema.json`'s `review` object,
   `protocol/schemas/policy-review-v2.schema.json`, and
   `protocol/schemas/project-flow.schema.json`'s `review` object — the
   already-existing, already-consumed per-Flow project override
   mechanism (`.forge/flows/<flow_id>.yml`, `schema:
   forge/project-flow@1`, merged with the canonical Flow by
   `resolve_effective_flow`, which `forge validate` already calls for
   every such file) — giving a project's effective configuration a
   concrete, schema-legal, already-wired place to declare a
   stricter-than-floor profile per Decision point 12.
   `.forge/forge.yml`'s separate, project-wide `review.strict` field
   (`protocol/schemas/project.schema.json`) is intentionally left
   untouched: it is not read by any CLI code today (confirmed by
   Architecture inspection) and is not the right integration point. A
   manifest, policy, or project-flow config that omits `profile` is
   interpreted as `strict` (the historically universal behavior) — the
   compatible-evolution reading under C-045: no existing valid
   instance's minimum obligation is reduced by silence. Separately,
   `protocol/schemas/flow.schema.json`'s `review` sub-schema replaces
   its hardcoded `strict`/`adversarial` `const: true` with the new
   `profile` enum (`required: true` stays constant) — this is **not**
   an independent additive change: it is the direct schema encoding of
   the Contract-text decision already resolved below (Open normative
   question), since that schema constraint existed only to enforce
   today's C-022/C-023 obligation. It narrows a previously
   unconditional, machine-checked guarantee to hold only for `profile:
   strict`; no historical Flow-file *instance* is invalidated by it
   (only three live canonical files exist, edited in place by this
   Change, not a population of historical documents to check against),
   but it is recorded here explicitly as a schema-level consequence of
   the Contract decision, not a separately-additive claim.
9. `protocol/schemas/policy-review.schema.json` (Protocol 1) is left
   untouched — Protocol 1 keeps its existing, hardcoded
   `strict`/`adversarial` consts unconditionally. Profiles are a
   Protocol-2-only concept for this RFC, consistent with C-026 already
   being Protocol-2-specific.
10. `src/forge_cli/validation/__init__.py`'s review/convergence
    functions remain profile-blind for everything they currently
    check (independence, evidence, severities, convergence) — a
    profile changes what a Reviewer is *instructed* to do
    (Adapter-projected guidance), not what Core *validates* after the
    fact. This keeps the validation blast radius minimal (F-010,
    F-011) and avoids inventing a new enforcement surface for
    something that is fundamentally a reviewing posture, not a
    mechanically checkable property.
11. Harness Adapter projections (`review_independence.py`,
    `claude_code/projection.py`, `codex/projection.py`) gain
    profile-specific review-instruction text per Flow's
    gate-obligation section, while the shared Reviewer/Resolver
    independence block remains verbatim-shared across all three
    (independence is profile-invariant per point 6).
12. A project's effective configuration MAY require a **more**
    rigorous profile than a Flow's canonical default (e.g. force
    `strict` for FAST in a given repository), but MUST NOT declare a
    profile weaker than the Flow's canonical floor — `forge validate`
    fails closed if project configuration attempts to declare a
    profile below the canonical floor for a Flow.
13. A Change's Review Profile is derived from `manifest.flow.current`
    (the Change's **effective** Flow) at the time each Review Iteration
    actually runs, never fixed at Specification or Plan time. A Change
    that escalates Flow under C-005 mid-Change escalates its Review
    Profile with it for any Review Iteration recorded after the
    escalation; a Review Iteration already recorded before an
    escalation is not retroactively invalidated (C-045) — it remains
    valid evidence under the profile that applied when it ran.
14. `src/forge_cli/merge_readiness/evaluator.py`'s `MR-004` diagnostic
    label (`"STRICT REVIEW NOT READY"`) is renamed to a profile-neutral
    label (e.g. `"REVIEW NOT READY"`), since "Strict Review" no longer
    describes every Change's Review once this RFC ships — a one-line,
    purely cosmetic rename with no change to `MR-004`'s trigger
    condition or blocking semantics.

## Open normative question — resolved at acceptance

C-022/C-023 today apply their full, undifferentiated obligation to
**every** Change regardless of Flow — including FAST and STANDARD.
Decoupling FAST/STANDARD from the `strict`/adversarial posture is,
read one way, a **weakening of an existing invariant** for those Flow
classes, which C-046 says "MUST require a new integer Protocol
identifier" (a new Protocol 3, not a Protocol-2-compatible amendment).
Read the other way, it is a **clarification**: `focused`/`standard`
remain genuine, evidence-based, real-rejection-authority Review — no
existing Change's evidence obligations, independence guarantees, or
blocking severities are removed — so the *invariant* ("every Change is
reviewed, and a real reviewer can and must reject it on a material
Finding") is preserved, only the *posture* (exhaustive adversarial
search vs. scoped genuine search) changes, and C-045's "preserve the
meaning and minimum obligations of existing valid instances" is
arguably satisfied since no *historical* Change's already-recorded
Review is invalidated (requirement 12 of the originating request).

This was exactly the kind of Material Unresolved Decision (Contract
class, human authority) that must be recorded and escalated, not
decided by an agent (C-054, C-055) — so it was presented to the human
maintainer with both readings and their consequences, rather than
resolved by default.

**Resolved: (a), Protocol-2-compatible clarification.** The human
maintainer explicitly accepted this reading in the active chat session
on 2026-08-25: no historical Change's recorded Review is invalidated,
Reviewer/Resolver independence and rejection authority remain
identical across all three profiles, and only the adversarial-search
*posture* changes for `focused`/`standard` — the underlying invariant
is preserved, satisfying C-045. Protocol remains `2`; no new Protocol
identifier is introduced by this RFC.

## Non-goals and safeguards

This RFC does not authorize:

- automatic Flow downgrade from line/file counts or any other
  heuristic (Flow classification remains C-003's semantic-impact
  authority, untouched);
- a numeric review score that can override semantic classification or
  Finding severity;
- diff-only Review, or treating passing tests as sufficient, at any
  profile;
- removing or weakening Reviewer/Resolver independence (C-026), for
  any profile;
- removing or weakening the Convergence Limit (C-049) or
  Out-of-Scope-Mutation handling (C-048), for any profile;
- removing BLOCKER/MAJOR blocking-Completion semantics (C-027) at any
  profile;
- a project or Harness silently declaring a profile weaker than a
  Flow's canonical floor;
- retroactively invalidating any historical Change's already-recorded
  Review outcome, at any profile (C-045).

## Alternatives rejected

### Keep the single adversarial model, optimize its cost some other way

This is the status quo RFC-0005 partially explored (a calibration
*layer* on top of, not instead of, a uniform adversarial model). It
does not address the actual problem statement: cost stays
disproportionate to impact because the review *posture* itself never
changes, only planning/emphasis metadata around it. Rejected as
insufficient for the stated Expected Outcome.

### Fully freeform, project-configurable review rigor with no Protocol floor

Rejected: this would let a project's own configuration silently
weaken Core's minimum guarantee per Flow, which Contract C-042
("Project configuration cannot weaken the Contract") and this
originating request's own Requirement 11 both explicitly forbid. Every
profile has a canonical Protocol-defined floor per Flow; configuration
may only raise it.

### A new, fourth review engine or workflow per profile

Rejected per F-010 (foundation simplicity) and the originating
request's own Constraint ("Não criar três sistemas de Review"). A
single Review lifecycle, Finding vocabulary, evidence model, and
Convergence mechanism serves all three profiles; only the
Reviewer-facing instructions (an Adapter-projection concern) and one
new Flow-scoped policy field vary.

### Waiting for RFC-0005's calibration pilot before proposing anything binding

RFC-0005's own "Immediate mandatory thresholds" rejection, and its
5–10-Change Calibration Pilot, were reasons to distrust an *ad hoc,
data-derived, numeric* threshold chosen without a representative
sample — exactly the kind of proposal RFC-0005 itself was scoped to
avoid inventing prematurely. This RFC does not do that: it defines no
numeric threshold, no score, and no measurement-derived cutoff at all.
It defines three fixed, discrete, Protocol-authored profiles, each
with every mechanically-checked guarantee (independence, evidence,
severities, Convergence Limit, provenance) held identical and
unconditioned on profile (Decision point 6, 10) — the entire class of
risk a calibration pilot exists to bound (an under-calibrated numeric
threshold silently letting real risk through) does not arise here,
because nothing here is calibrated from data and nothing quantitative
is being set. What *does* carry residual, honestly-acknowledged risk —
a `focused` or `standard` Reviewer that under-searches, indistinguishable
after the fact from one that searched correctly and found nothing — is
addressed by keeping the floor per Flow non-negotiable (Decision point
12) and by every profile retaining real, evidence-backed rejection
authority on any Finding actually observed (Decision points 2–3), not
by a pilot period. A pilot remains the right tool for a future,
separate proposal that *does* want to introduce data-derived numeric
calibration on top of this profile floor; it is not a precondition for
adopting three fixed, non-numeric, Protocol-authored profiles.

## Compatibility and consequences

Schema changes are additive (a new optional, defaulted enum field) —
existing `forge/change@2` manifests and `provenance.yml` records that
predate this field remain valid and are interpreted as `strict`
(today's universal behavior), so no historical Change's recorded
Review is invalidated (C-045). `protocol/schemas/policy-review.schema.json`
(Protocol 1) is untouched. `src/forge_cli/validation/__init__.py`'s
independence, evidence, severity, and convergence checks are unchanged
for every profile — only Adapter-projected review *instructions* vary
by Flow, which is new prose generation, not new enforcement. The
practical benefit is that FAST and STANDARD Changes stop paying the
`strict` profile's full adversarial-search cost in reviewer time and
token usage, while FULL — where that cost is actually justified —
keeps today's rigor exactly as-is. The Open Normative Question above
is the one place this RFC's acceptance requires a specific, recorded
human choice about Protocol-identifier consequences, not left implicit.

## Acceptance record

Proposed and accepted in the same active chat session on 2026-08-25,
following the pattern of `docs/rfcs/0002-harness-adapter-foundation.md`
(proposal and acceptance as distinct commits — this RFC's proposal
commit and this acceptance are likewise separate commits, not a single
combined act). The human maintainer's acceptance explicitly recorded
the resolution to the Open Normative Question above (Protocol-2-
compatible clarification, not a new Protocol 3) before any Contract
text, Flow file, schema, or CLI code was changed — mirroring C-077's
Plan/Implementation boundary, applied here to the RFC/Contract-change
boundary. `docs/rfcs/0005-review-cost-proportionality.md` is marked
`Status: Superseded by RFC-0007` as a consequence of this acceptance.
CHG-0048's own `provenance.yml` records the acceptance as repository-
native evidence (`rfc-acceptance-001`), per the same evidentiary
standard C-077 applies to Plan authorization.
