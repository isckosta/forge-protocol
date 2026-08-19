# Adversarial Specification Review — CHG-0015

Status: complete

Six defects were found by actively searching for the specific failure
modes `protocol/flows/full.yml`'s `specification_review` Gate (`mode:
adversarial`) exists to catch — self-authorization loopholes, circular
authority, fail-open defaults, unlisted alternatives, schema gaps, and
decision-ownership violations — and were corrected before Architecture. This Review ran in the same session
that authored the Specification; per `protocol/versions/2/specification.md`
§2, Protocol 2's independent-Execution/Context requirement binds Strict
Review only, not Specification Review (confirmed against
`forge/execution-provenance@1`'s `role` enum, which has no Specification-
Review-shaped role, and against `CHG-0013`'s own precedent, whose
`provenance.yml` records only one Implementation Execution across Intent
through Architecture and a separate Execution only for its later Strict
Review). Genuine adversarial framing — actively trying to break the
Specification rather than confirm it — is what this Gate requires, not
independence machinery Protocol 2 does not ask of it.

## Findings

**R001 (MAJOR — self-authorization / correctness).** The original FR-006
("An Execution MUST NOT mutate an Authority-Defining Artifact that
declares, evidences, or grants its own current delegation's Authority")
and INV-002, read literally, prohibited an Execution from ever writing its
own self-recorded provenance record into `provenance.yml` — since
`provenance.yml` is itself named as an Authority-Defining Artifact, and
every Implementation/Resolution/Review Execution in this repository writes
its own `role`/`assurance: recorded, observed_by: self` record into that
same file as a matter of normal, Protocol-2-sanctioned practice (verified
directly against every existing `.forge/changes/*/provenance.yml` in this
repository). As originally worded, FR-006 would have made every historical
Change's own provenance-recording practice a Contract violation under this
Change's own new rule — the opposite of AC-010/historical compatibility,
and a rule that would immediately have to be violated by this very Change's
own upcoming Implementation stage to produce its own `provenance.yml`.
**Corrected**: FR-006 and INV-002 narrowed to prohibit only *declaring or
expanding* Authority beyond what was actually granted, explicitly
distinguishing that from *self-attestation* of already-granted Authority or
already-performed action (self-recorded provenance, Protocol 2 §5's
review-control-metadata exception) — both of which remain permitted, as
they must.

**R002 (MAJOR — fail-open gap).** FR-007 (Delegation Ceiling) and INV-003
required a delegate's Authorized Scope to stay within its delegator's own
Authorized Scope, but the original Specification never stated what happens
when the delegator's own Scope was never itself declared — which is true of
every primary Execution today, and remains true under DEC-001's
recommended Alternative 4 (mandatory only for sub-delegations, not for a
primary Execution's own direct work). Left unaddressed, an undeclared
delegator Scope could be silently read as "unbounded," which would let the
Delegation Ceiling be trivially satisfied by any grant at all — defeating
the invariant exactly in the incident's own shape (a primary Execution,
with no declared Scope of its own, delegating to a subagent). **Corrected**:
FR-007 now states an undeclared delegator Scope MUST NOT be treated as
unbounded, and requires Architecture to define a conservative default
(e.g., the Change's own governed paths) rather than leaving the case
fail-open, consistent with FR-013's general fail-closed posture.

**R003 (MINOR — internal inconsistency).** DEC-001's Recommendation
proposed a variant ("mandatory immediately, but only for sub-delegations")
that matched none of the three Alternatives actually listed, violating this
Specification's own adopted discipline (`CHG-0013` FR-008's requirement
that every Alternative actually considered be listed, which this
Specification's Unresolved Decisions implicitly follow). **Corrected**:
added as Alternative 4 explicitly, and the Recommendation now points to it
by number rather than restating it inline.

**R004 (MINOR — schema gap, undisclosed).** FR-003/FR-004 require
representing Authorized Scope and Observed Effect for "any delegated
Execution," including a research subagent like the incident's — but
`forge/execution-provenance@1`'s `role` enum is closed to
`implementation`/`resolution`/`review`, none of which fits that case, and
the original Compatibility section did not disclose this gap. **Corrected**:
added to Compatibility and to "Deferred to Architecture," naming the two
live options (widen the `role` enum, or introduce a distinct provenance
concept for delegated Executions) without prematurely choosing between
them.

**R005 (MINOR — misleading cross-reference).** FR-001 originally pointed
to "FR-017" as if it alone settled which delegations are "covered by this
mechanism," but FR-017 only settles the repository-vs-network subject-matter
boundary, not the separate rollout-timing question DEC-001 governs. Left
as written, a reader could believe applicability was fully decided when a
`contract`-class, human-authority Decision on exactly that question was
still open. **Corrected**: FR-001 now names both boundaries and points each
to its actual governing clause (FR-017 and DEC-001 respectively).

**R006 (MAJOR — decision-ownership violation, found by running `forge
validate`, not by re-reading).** The first draft of this Specification and
its manifest resolved DEC-002 directly (`resolved_via: autonomous_decision`)
on the reasoning that `architectural`-class Decisions default to
`agent_with_review` Authority and this Review supplies the "with_review"
half. Running `forge validate` against the actual manifest (not just
re-reading the prose) surfaced a C-051 finding: `decision.yml`'s
`owning_artifact_by_class` fixes `architectural` questions to **Architecture**
as owning Artifact, not Specification, and `downstream_must_not_resolve_
upstream_owned_decision` (C-052) means holding sufficient Authority in the
abstract does not license Specification to resolve a Decision it does not
own — ownership and authority are independent axes, and this draft
conflated them. Architecture does not exist yet in this Change; nothing
today has standing to resolve DEC-002. **Corrected**: DEC-002 changed from
`resolved`/`autonomous_decision` back to `open`, `owning_artifact:
architecture`, carrying the same Alternative-2 analysis forward as a
Recommendation (C-054) for Architecture to actually decide. This is worth
naming explicitly: this Review caught the defect *because* it ran the real
validator against real repository state rather than trusting its own
narrative that the resolution was proper — the same discipline this
Change's entire subject demands of delegated Executions in general.

## Checked and found sound (no defect)

- **Delegation Ceiling vs. Human root.** Verified the Human-exemption
  clause in FR-007/Terminology cannot be used as an escalation vector: an
  Agent Execution cannot claim "Human" status to bypass the ceiling, since
  Authority records this Specification anticipates are Execution-scoped
  provenance data, not self-asserted identity claims free for any Execution
  to adopt (FR-009's graduated assurance already treats unverified identity
  claims as `claimed`-level only).
- **AC-006/FR-007 vs. legitimate broadening scenarios.** Checked for a
  legitimate case where a delegate genuinely needs broader Scope than its
  delegator (e.g., a delegate that must touch a path the delegator itself
  cannot). None found in Discovery or in the originating instruction; FR-007
  stands unmodified.
- **FR-010's MAY vs. false-guarantee risk.** Checked that FR-010 does not
  imply Prevention is available anywhere in this repository today — it does
  not; Discovery already established no Adapter offers it. No correction
  needed.
- **Compatibility conclusion (no new Protocol integer).** Independently
  re-derived against `protocol/compatibility.md`'s explicit breaking-change
  list (remove/weaken an invariant; make an optional field mandatory for
  existing instances; change meaning of an existing required field/Gate;
  invalidate a previously valid instance) — none apply to FR-002/FR-005/
  FR-006/FR-007/FR-011/FR-013 as scoped by FR-015. Conclusion holds, with
  the explicit caveat already in the Specification that Architecture must
  re-verify once concrete schema shapes exist.
- **Non-goal boundary (FR-017) vs. FR-011's "repository state" wording.**
  Checked that FR-011's mandatory Detection floor does not implicitly creep
  into network/external-service territory through loose wording. It does
  not — "local Git-native repository state" is explicit.

## Verdict

No BLOCKER-class defect (nothing here reaches self-authorization or a false
enforcement guarantee surviving into the corrected text). Six real defects
were found and corrected directly in `specification.md`/`manifest.yml` (3
MAJOR — R001 self-authorization loophole, R002 fail-open Delegation
Ceiling default, R006 decision-ownership violation; 3 MINOR — R003, R004,
R005), matching `CHG-0013/specification-review.md`'s own precedent of
correcting genuine defects at this stage rather than deferring them. Both
Unresolved Decisions this Specification surfaced remain correctly recorded
per Contract: `DEC-001` `open`/`awaiting_decision` (human authority,
required — `contract` class), `DEC-002` `open` (owned by Architecture, not
resolvable here — R006's correction), each carrying a Recommendation
forward rather than a premature Decision.

**Gate result: `specification_review_passed` — with a mechanically
verified caveat.** Running `forge validate` against this Change's own
manifest after all corrections confirms exactly one remaining finding, and
it is the correct, intended one: C-051 reports that `specification_review_
passed` MUST NOT be asserted while `DEC-001` (owned by Specification, a
Gate dependency) remains `awaiting_decision`. This is not a defect to fix —
it is Forge's own C-051 mechanism correctly refusing to let this Change
claim a passed Gate while a human-authority Decision it depends on is still
open, which is exactly the fail-closed behavior this Specification's own
FR-013/INV-005 asks for. This Review's content is complete and its Findings
are resolved; the Gate's formal `passed` assertion is, correctly, withheld
until a human resolves `DEC-001`.

Per this Change's own explicit boundary (Intent §Goal; originating
instruction §30), this session stops here regardless. Architecture, Test
Strategy, Plan, Tasks, and Implementation are FULL's required next stages
but are not begun in this session. The first thing the next session needs
from a human is a resolution (or explicit deferral-with-interim-default)
for `DEC-001` — without it, `forge validate` will continue to correctly
withhold `specification_review_passed`, and Architecture's own later Gate
additionally needs `DEC-002` resolved once that stage exists.

## Addendum — DEC-001 resolved

After this Review's Findings were corrected and this Verdict recorded, a
human was presented DEC-001's four Alternatives (via a structured choice,
per FR-010's presentation format, not an open-ended prompt) and explicitly
selected **Alternative 4** — the Recommendation this Specification already
carried at `medium` Confidence. Recorded in `specification.md`'s DEC-001
section and `manifest.yml` (`status: resolved`, `resolved_via:
human_decision`). Re-running `forge validate` after this update confirms
the C-051 finding above clears; see the corresponding commit for the exact
output. `DEC-002` remains open (owned by Architecture, unaffected by
DEC-001's resolution) and still blocks the Architecture Gate, not
Specification Review.
