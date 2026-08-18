# ADR-0012 — Unresolved Decision Management

Status: Accepted for CHG-0013 Implementation; independent Strict Review pending.

## Decision

Forge gains a normative concept, Unresolved Decision: a material decision
required for an Artifact or Gate to be considered sufficiently determined,
whose answer does not yet have valid normative authority. Detection MUST
NOT be followed by silent resolution.

Every Unresolved Decision is classified into exactly one of four Decision
Classes — `product`, `contract`, `architectural`, `technical` — which
determines its owning Artifact and default Decision Authority (`human`,
`agent`, or `agent_with_review`, `protocol/policies/decision.yml`). Two
candidate classes from prior art, `evidence` and `discovery`, were
deliberately not adopted: Evidence Resolution is a resolution path
available to any Class, not itself a Class, and `discovery` would collide
with the existing Flow stage of the same name (`specification.md` §
"Decision taxonomy" in `CHG-0013`'s own Specification has the full
rationale).

A question is first assessed for Materiality (would it change a
Requirement, Acceptance Criterion, public Contract, Schema, Compatibility
boundary, Security posture, domain Invariant, ownership boundary, failure
semantics, state transition, Architecture, Verification Strategy, or
operational behavior); a Non-material question requires no Decision record
and no interruption. Before escalating a Material Decision, Forge attempts
Evidence Resolution (citing an existing normative source); when Authority
permits autonomy, Forge performs Analysis and produces a Recommendation
before resolving the Decision itself; when Authority is `human`, Forge
performs Analysis, Alternatives, and Trade-offs, produces a Recommendation,
and stops — a Recommendation, regardless of Confidence, is never itself a
Decision.

A Gate MUST NOT pass while a dependent Artifact has a Material Decision it
owns in an Open-blocking state (`open`, `analyzing`, `awaiting_decision`).
A downstream Artifact MUST NOT resolve a Decision it does not own; when one
discovers a Decision belonging upstream, the owning Artifact is revisited
and any Gate it already passed must be re-satisfied, and the resolution
must explicitly declare which downstream Artifacts it invalidates.

New Contract rules (C-051–C-059, `protocol/contract/engineering.md`,
backfilled together with the previously-missing C-047–C-050 into
`protocol/versions/2/contract/engineering.md`) bind a Change only once it
records a `decisions[]` entry, following the C-045/C-046/C-047-050
precedent CHG-0008/CHG-0011 set for the same shared file. No RFC accompanies
this ADR: `docs/rfcs/` contains only the two foundational Protocol RFCs
(0001, 0002); neither CHG-0008 (which introduced Protocol 2 itself) nor
CHG-0011 (which added C-047–C-050) produced a new RFC, only an ADR —
established repository practice, not merely written policy, resolves this
Change's own F-008 evaluation the same way.

## Consequences

Forge can now stop an ambiguity from silently becoming a Requirement,
Architecture choice, or Task, while doing the engineering work it can do
for itself (evidence investigation, alternatives, trade-offs,
recommendation) before asking a human — without becoming either an
arbitrarily autonomous agent (human-authority Decisions can never be
resolved autonomously, C-055) or a questionnaire that offloads analysis to
the user (analysis and a Recommendation are required before escalation,
C-053/C-054). `convergence_decision` (CHG-0011) is not migrated onto this
mechanism; it remains valid, narrower prior art for the same underlying
pattern, and unifying the two is explicit future work, not done here.
Every historical manifest in this repository (`CHG-0001`–`CHG-0012`)
continues to validate with zero new findings, confirmed directly
(`verification.md`), not assumed.
