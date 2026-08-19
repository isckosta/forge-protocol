# Architecture — Canonical Artifact Structure for Human-Readable Change Documentation

## Solution Summary

Add one new canonical file, `protocol/artifact-structure.md`, alongside
`protocol/specification.md`, `protocol/compatibility.md`, and
`protocol/contract/engineering.md` — same authority tier, same prose
style, no new Schema, no new Policy YAML. Wire it in with the smallest
possible touch to each existing surface: a two-paragraph pointer section
in `protocol/specification.md`, a small additive Contract rule block, a
one-sentence `ARCHITECTURE.md` clarification, a `protocol/compatibility.md`
addendum (established three-time pattern), and one new
`_resource()`-backed inclusion in the Codex Adapter's projection code.
Everything about *how strongly* this binds future Changes is deferred to
DEC-001 (open, human authority) — this Architecture is written so that
either resolution of DEC-001 changes only FR-006's rule wording and
`compatibility.md`'s addendum text, not the file layout or projection
mechanism decided here.

## Architectural Goals

- Single canonical source; zero duplicated authority (INV-001).
- Zero Schema change; zero Gate change under the recommended resolution
  of DEC-001.
- Adapter projects by reference, exactly like Flow and Contract already
  do — no second content-delivery mechanism.
- Guidance recognizes and formalizes real, already-working conventions
  (`FR/NFR/SEC/INV/CON-xxx`, `DEC-xxx`, `## Iteration N — <verdict>`,
  flat numbered Plan work lists) rather than inventing new ones the
  prompt that originated this Change assumed without checking.

## DEC-002 — Where the guidance lives, how it is projected, and whether it requires a new Protocol integer

**Class:** `architectural` · **Materiality:** material (changes
`architecture`) · **Authority:** `agent_with_review` (architectural
default per `decision.yml`) · **Owning Artifact:** Architecture ·
**Status:** `resolved`

**Question:** Among the options the originating prompt asked to be
validated — (A) Protocol normative specification, (B) canonical Protocol
guidance (non-binding), (C) Adapter-only guidance, (D) some existing
abstraction — where does the Canonical Artifact Structure live, how does
a Harness Adapter obtain it, and does introducing it require a new
integer Protocol?

**Evidence resolution (no fresh analysis needed for two of the three
sub-questions):** `ARCHITECTURE.md:36` already normatively lists
"Artifact semantics" as canonical content living in `protocol/` — this
directly resolves *where* in favor of (B), by citation, not invention.
`ARCHITECTURE.md` §7's layering diagram and the Codex Adapter's existing
`projection.py` mechanism (raw inclusion of Flow/Contract content via
`_resource()`, digested, not re-authored) directly resolve *how it
reaches a Harness*: by reference/inclusion, the same as every other
canonical resource — this rules out (C) (Adapter-only would let Adapters
diverge, contradicting `ARCHITECTURE.md:32`/§21 "Adapters translate...
may not redefine") and (D) (Discovery found no existing abstraction
narrower than "new file beside `specification.md`/`compatibility.md`" —
inventing a new Policy YAML schema for prose guidance would fail CON-002
and misuse a schema class designed for machine-consumed governance data,
not human-readable structural recommendations). Option (A) — folding this
into `protocol/specification.md` itself as new binding sections — was
rejected because Specification 40 sections define Core semantics tersely
and normatively; per-Artifact-type structural guidance is inherently
longer and example-bearing, and mixing the two would violate this
Change's own Artifact Responsibility principle applied to
`protocol/specification.md` itself.

**Remaining actual decision:** file identity and shape. Decided:
`protocol/artifact-structure.md`, Markdown prose (not YAML — this is
guidance for a human/agent reader, not a machine-validated governance
policy; the existing `protocol/policies/*.yml` files all describe
enforcement rules consumed by validation code, which this explicitly is
not, per FR-003).

**Decision:** `protocol/artifact-structure.md` is created as new
canonical, non-binding-by-default content. It is loaded and projected by
Harness Adapters exactly as Flow and Contract content already are (Codex:
`_resource()` inclusion into the generated skill bundle); Core does not
parse, load, or enforce its content beyond what DEC-001 separately
decides for the narrow outcome-heading question. No new integer Protocol
is required for this file's introduction itself (creating an unenforced,
referenced document changes no required field, stage, or Gate meaning) —
this is independent of DEC-001, which only concerns whether one specific
downstream Contract rule becomes `MUST`-and-Gate-checked.

**Resolution path:** `autonomous_decision`, not `evidence` — corrected
from this Decision's own first draft (Strict Review R008). Two of the
three sub-questions (*where* it lives, *how* a Harness Adapter obtains
it) were resolved by direct citation of already-existing normative text
and already-existing working code — genuine Evidence Resolution. The
third (file identity and shape, immediately above) was not: it is a
design choice reached by reasoning about which existing category
(`protocol/*.md` prose vs. `protocol/policies/*.yml` data) fits, not a
citation of a source that already determined the answer
(`decision.yml`'s `evidence_resolution.agent_inference_is_not_evidence:
true`). `resolution_paths` offers `autonomous_decision` for exactly this
— Authority permits it (`agent_with_review`), Analysis and a
Recommendation were produced above, and the whole Decision is
classified by its weakest link, not its strongest.

**Confidence:** high.

## Content Shape of `protocol/artifact-structure.md` (design, not production text)

Structural sections the file itself will contain (Implementation, not
this Architecture, writes the final prose):

1. **Principles** — Progressive Disclosure (Outcome / Reasoning /
   Evidence), Artifact Responsibility, Result-Before-Evidence,
   Scanability, Proportionality, Extensibility (FR-001), each 1-2
   paragraphs, each citing at least one real example from this
   repository's own history where the principle already holds or
   currently fails (reusing Discovery's evidence, not fabricating new
   examples).
2. **Per-Artifact-type guidance** (FR-002), one subsection per type,
   each listing: structural core (what almost always belongs, in
   recommended order), conditional (present only when materially
   applicable — e.g. Security Requirements only when non-empty, per this
   Change's own Specification setting the example), and optional
   (domain-specific extensions always permitted, FR-001 Extensibility).
   Concretely, informed by Discovery's real-precedent findings rather
   than the originating prompt's untested assumptions:
   - **Intent**: Summary, Problem, Desired Outcome, Scope, Out of Scope,
     Success Criteria — matches real precedent closely; no change needed
     beyond stating it.
   - **Discovery**: adds an Executive Summary / Recommendation as the
     first section (this Change's own `discovery.md` demonstrates it) —
     real precedent has no such section today (regression-by-omission,
     not by omission-of-convention, since none ever existed). No
     numbered `D-xxx` Findings (Discovery §37 finding: no consumer, no
     precedent, rejected as invented ceremony).
   - **Specification**: `FR/NFR/SEC/INV/CON-xxx` sub-headings (already
     stable, recognized not reinvented), `## Unresolved Decisions` with
     `DEC-xxx` (already real, per `decision.yml`), no `## Traceability`
     section (would duplicate `traceability.yml`, INV-001).
   - **Specification Review**: `SR-xxx` findings (CHG-0007's real
     convention — this Change's own `specification-review.md`
     demonstrates it and initially mis-used the Strict-Review-only
     `Rxxx` convention before self-correcting), Verdict at the top.
   - **Architecture**: `DEC-xxx` for embedded Decision records (never
     `ADR-xxx` — CON-003), Solution Summary first.
   - **Test Design / Test Strategy**: `TDD-xxx` per-case headings
     (already real and consistently used, CHG-0015's 16 cases), no
     restructuring needed — recognize, don't redesign.
   - **Plan**: **not** heading-per-work-unit (the originating prompt's
     `### P-001` suggestion has no precedent and was rejected — real
     Plans, including `CHG-0015/plan.md` and `CHG-0013/plan.md`, are a
     single flat numbered list of concrete, file-referencing work items,
     which is already dense and scanable). The one real, recurring gap:
     no canonical name or fixed position for the boundary paragraph.
     Structural core becomes: numbered work-item list (as already
     practiced) followed by a **canonically named, always-last**
     `## Implementation Boundary` section (FR-005) replacing the
     ad-hoc "Explicit boundary" heading independently reinvented twice.
   - **Tasks**: Status summary + checklist body — matches
     `CHG-0015/tasks.md`'s real, minimal shape; no material change.
   - **Verification**: `## Result` first (`PASS`/`FAIL`/`SKIPPED`/
     `NOT APPLICABLE`, FR-004), then evidence — the concrete fix for
     Discovery's strongest finding (the CHG-0001→CHG-0015 regression).
   - **Review**: `## Verdict` aggregate summary at the top (FR-004),
     `## Iteration N — <verdict>` preserved unchanged per iteration,
     `Rxxx` Findings (real Strict Review convention, distinct from
     Specification Review's `SR-xxx`).
   - **Specification Drift**: recognized under its real name (Discovery
     finding); structural core stays narrative with `## Final decision`
     last — its role (tracing *how* a drift was found and resolved) is
     not outcome-first by nature, and the guidance says so explicitly
     rather than mechanically forcing Result-Before-Evidence where the
     Artifact's own responsibility argues against it (this Change's own
     Extensibility/Proportionality principle applied to itself).
   - **Knowledge Capture**: What Changed, Durable Knowledge, Consequences
     — matches real precedent; no material change identified.
   - **Inspection**: no new expectation beyond what FAST already does
     (NFR-001) — the guidance explicitly says proportionality means a
     four-line Inspection stays a fully conforming example.
3. **A short "how this document is projected" note**, itself an example
   of the Result-Before-Evidence/Artifact-Responsibility principles it
   defines, pointing at Protocol §41 and this Change's own
   `architecture.md` rather than restating Adapter mechanics (INV-001).

## Contract and Specification Placement

New Contract rules land in `protocol/contract/engineering.md` starting at
`C-067`, following the exact two-paragraph brief-pointer style of
C-051–C-059/C-060–C-066 — no restatement of per-type structure in
Contract prose (INV-001 applies to Contract too, not only to the new
file). `protocol/specification.md` gains `§41 Canonical Artifact
Structure`, same brief-pointer pattern as §39/§40. Exact rule count and
wording (in particular, whether a rule references the `## Result`/
`## Verdict` recommendation as `SHOULD` or, per DEC-001 Alternative B, as
`MUST` with a Gate condition) is finalized once DEC-001 resolves — Plan
below is written for DEC-001 = Alternative A (Specification's
recommendation) and states explicitly what changes if the human instead
selects B.

## Adapter/Harness Integration

Codex Adapter (`src/forge_cli/adapters/codex/projection.py`): add one
more `_resource()`-backed field to `CodexProjectionInput`/
`CodexProjectionBundle` (alongside existing `flow_content`,
`contract_content`), loading `protocol/artifact-structure.md` and
including it, with its own digest, in the generated skill the same way
Flow/Contract content is included today. No change to `adapter.yml`
capability declarations is required (`skills: true` already covers this;
no new capability is introduced). Any future second Harness Adapter
consumes the same canonical file the same way — nothing here is
Codex-specific (NFR-002); this section documents the first concrete
consumer, not a Codex-only mechanism.

## Compatibility

Confirmed resolution (DEC-001 = A, human decision, 2026-08-19): zero
Schema change, zero Gate change, zero historical Change invalidated, zero
new Protocol integer —
`protocol/compatibility.md` addendum follows the CHG-0011/CHG-0013/
CHG-0015 "optional artifact whose absence preserves existing meaning"
template exactly, substituting this Change's specifics. If DEC-001
instead resolves as B: the addendum instead documents a new integer
Protocol for the single `MUST`-checked heading obligation, prospective
only (Specification Review SR-001's correction applies), and Plan gains
one additional Task (a narrow Core validation check plus its own TDD
cycle) — this Architecture explicitly marks that Task as
DEC-001-contingent rather than silently assuming Alternative A succeeds.

## Canonical Examples (FR-010)

New directory `examples/canonical-artifacts/` (not an addition to
`examples/golden-path-standard/`, which Discovery found is a code-fixture
directory for Layer A/B testing, not a Markdown-artifact showcase — mixing
concerns there would violate this Change's own Artifact Responsibility
principle). Contents: one example `verification.md` and one example
`review.md` (the two Artifacts with the concrete, demonstrated
regression), each annotated with an inline comment (HTML comment, invisible
in rendered Markdown, consistent with how documentation examples are
typically annotated) explaining which principle each section
demonstrates. Not a full fifteen-Artifact fixture set — proportional to
what Discovery actually found broken.

## Risks

- **Guidance is read but not followed** (the core risk DEC-001
  Alternative A accepts): mitigated by projection into the Codex skill
  (FR-009) making it visible at the point of authoring, not just
  archived in `protocol/`; accepted as a reasonable initial bet per
  Specification's Recommendation, revisitable as its own future Change.
- **Per-Artifact-type guidance drifts out of sync with real practice**
  (the same failure mode Discovery found in the originating prompt's own
  untested assumptions, e.g. `### P-001` headings, `D-xxx` Findings,
  `ADR-xxx` in Architecture): mitigated by grounding every recommendation
  in cited real precedent rather than invented ideals, and by keeping the
  file a single canonical source so future drift-correction touches one
  place.
- **Scope creep toward enforcement**: mitigated by FR-003's explicit
  default and by keeping DEC-001 open rather than silently choosing the
  stronger option.

## What This Change Deliberately Does Not Build

Markdown AST validation, HTML/PDF rendering, heading-presence linting
beyond DEC-001's single narrow (and currently undecided) case, a second
Harness Adapter, any change to `manifest.yml`/`provenance.yml`/
`tdd-evidence.yml`/`traceability.yml` shape, retroactive reformatting of
CHG-0001–CHG-0015, or a new lifecycle stage, Flow, or Gate.
