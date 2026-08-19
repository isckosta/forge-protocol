# Specification — Canonical Artifact Structure for Human-Readable Change Documentation

## Summary

Introduce `protocol/artifact-structure.md`: canonical, non-binding
guidance defining information-architecture principles and a recommended
(not enforced) structural breakdown per Forge human Artifact type. Wire it
into the Effective Engineering Contract via a small additive rule, into
`protocol/specification.md` via a short pointer section, into
`protocol/compatibility.md` via a precedent-following addendum, and into
the Codex Adapter's existing raw-inclusion projection mechanism — with no
Schema change and no historical Change invalidated.

## Classification

**FULL.** Every sampled Change touching `protocol/contract/engineering.md`,
a canonical Policy, or `protocol/specification.md` (CHG-0008, CHG-0011,
CHG-0013, CHG-0015) was classified FULL without exception; the one
sampled STANDARD Change (CHG-0014) touched neither. This Change modifies
`protocol/contract/engineering.md`, adds new `protocol/` content, edits
`ARCHITECTURE.md`, and changes Codex Adapter projection behavior — the
same category of impact, not CHG-0014's category. See
`discovery.md` § Flow Classification Finding for full evidence. FAST is
inapplicable (multi-file, cross-module, normative-guidance change); FULL
is warranted over STANDARD on `ARCHITECTURE.md:75`'s own listed signals
(public contracts, cross-module behavior, compatibility). No downgrade is
performed and none is warranted.

## Functional Requirements

### FR-001 — Canonical guidance document
`protocol/artifact-structure.md` MUST exist and MUST define, at minimum,
the following design principles: Progressive Disclosure (Outcome /
Reasoning / Evidence), Artifact Responsibility (an Artifact primarily
contains information belonging to its own lifecycle responsibility),
Result-Before-Evidence (for decisional/verificatory Artifacts),
Scanability, Proportionality (no filler sections), and Extensibility
(domain-specific sections remain always permitted).

### FR-002 — Per-Artifact-type structural guidance
The document MUST provide recommended structure — distinguishing
structural core, conditional, and optional sections — for every human
Artifact type this repository actually produces: Intent, Discovery,
Specification, Specification Review, Architecture, Test Design, Test
Strategy, Plan, Tasks, Verification, Review, Specification Drift,
Knowledge Capture, and Inspection. It MUST NOT invent Artifact types this
repository does not use, and MUST use `Specification Drift` (this
repository's real name, Protocol §13) rather than inventing a
"Resolution" Artifact the taxonomy does not have.

### FR-003 — Non-enforcement default
All guidance introduced by this Change MUST be framed as RECOMMENDED
(`SHOULD`), not validated by `forge validate`, unless DEC-001 (below)
resolves otherwise. `forge validate` MUST continue to perform only
Schema and repository-native semantic validation after this Change.

### FR-004 — Outcome-first Verification and Review guidance
The guidance for Verification MUST recommend a `## Result` section (one
of `PASS`, `FAIL`, `SKIPPED`, `NOT APPLICABLE`) as the first substantive
section, before test/Forge evidence. `INCONCLUSIVE` is deliberately
excluded: it has no precedent anywhere in `protocol/` or `.forge/`
(confirmed by repository-wide search, Specification Review SR-003) and
does not exist in the current model. The guidance for Review MUST
recommend a `## Verdict` (or equivalent) summary at the top of the file
—distinct from, and in addition to, the existing per-iteration
`## Iteration N — PASS/REQUEST CHANGES` convention, which MUST be
preserved as-is (real, working precedent; not replaced).

### Security Requirements
None. This Change adds one canonical Markdown file under `protocol/` (no
new input surface) and one Adapter resource inclusion reusing the
existing `_resource()` path-safety/digest mechanism (Protocol §35). No
new attack surface is introduced (Specification Review SR-003).

### FR-005 — Plan boundary section
The guidance for Plan MUST define a canonical boundary section (naming
TBD in Architecture) capturing the Plan → Implementation approval
boundary, replacing the ad-hoc "Explicit boundary" prose independently
reinvented in `CHG-0015/plan.md` and `CHG-0013/plan.md`. The guidance
MUST state that Implementation-time discoveries belong in Verification
(or a Decision record, or a documented re-Plan / escalation through
existing Unresolved Decision Management and Gate re-satisfaction
mechanics), not in silent edits to the already-approved Plan content.

### FR-006 — Contract wiring
`protocol/contract/engineering.md` MUST gain new additive Contract
rule(s) (next available identifiers after C-066) that reference
`protocol/artifact-structure.md` without restating its content, following
the same brief-pointer pattern as C-051–C-059 (Unresolved Decision
Management) and C-060–C-066 (Delegated Execution Authority). The exact
binding strength (`SHOULD` vs any `MUST`) is governed by DEC-001.

### FR-007 — Specification pointer section
`protocol/specification.md` MUST gain one new numbered section (§41)
stating the existence and purpose of Canonical Artifact Structure
guidance in one to two paragraphs, in the same style as §39/§40, pointing
to `protocol/artifact-structure.md` for full detail. It MUST NOT restate
per-Artifact-type structure inline.

### FR-008 — Compatibility addendum
`protocol/compatibility.md` MUST gain a new addendum section
("Canonical Artifact Structure (CHG-0016)") documenting, following the
CHG-0011/CHG-0013/CHG-0015 precedent, why this Change does or does not
require a new integer Protocol — contingent on DEC-001's resolution.

### FR-009 — Adapter projection support
The Codex Adapter (`src/forge_cli/adapters/codex/`) MUST be able to
include `protocol/artifact-structure.md`'s content in its generated
skill bundle, using the existing `_resource()`-based raw-inclusion
mechanism already used for Flow and Contract content (`projection.py`).
This MUST NOT redefine or paraphrase the guidance in Adapter-authored
prose, per Protocol §34 (Adapters project, they do not redefine).

### FR-010 — Canonical example(s)
At least one canonical example demonstrating outcome-first Verification
and/or Review structure MUST be added (new fixture — new location or an
addition to `examples/golden-path-standard/`, decided in Architecture).
Historical Changes (CHG-0001–CHG-0015) MUST NOT be reformatted.

### FR-011 — Documentation Impact
This Change MUST update `ARCHITECTURE.md` §5 (clarifying that "Artifact
semantics" is now populated by `protocol/artifact-structure.md`), add one
new `docs/adr/` entry (next available: `0014`) per Contract F-008
("Material Architecture Changes require ADR"), and update `CHANGELOG.md`.
No RFC is required (F-008's RFC threshold is "Material Protocol Changes";
this Change is additive guidance of the same weight as CHG-0013's
ADR-only precedent, not a foundational Protocol redefinition).

## Non-functional Requirements

### NFR-001 — FAST proportionality preserved
Nothing introduced by this Change may add a new required or newly
expected section to `inspection.md` beyond what already exists in
practice. CHG-0005's four-line `inspection.md` must remain a valid,
unremarkable example after this Change.

### NFR-002 — Harness independence
`protocol/artifact-structure.md` MUST contain no Codex-specific,
Claude-specific, or other single-provider content. Any Harness-specific
projection detail belongs in that Harness's own Adapter, not in the
canonical document.

### NFR-003 — Projection follows existing pattern
Adapter changes MUST reuse the existing raw-inclusion/digest mechanism
(`_resource()`) rather than introducing a second, parallel content-
delivery mechanism for guidance versus Flow/Contract content.

## Constraints

### CON-001 — No semantic regression
This Change MUST NOT alter Gate semantics, Finding severities, Review
convergence semantics, Reviewer/Resolver separation, or Unresolved
Decision Management semantics as defined by existing Protocol sections
and `protocol/policies/decision.yml`.

### CON-002 — Schema stability
No file under `protocol/schemas/` MUST change as part of this Change.

### CON-003 — Namespace separation
`docs/adr/NNNN-slug.md` (durable, project-level architectural knowledge)
and `DEC-NNN` (Change-scoped Unresolved Decision records, per
`decision.yml`) MUST remain visibly distinct namespaces. No per-Change
`architecture.md` guidance introduced by this Change may recommend
`ADR-NNN`-style headings; `CHG-0015/architecture.md:37`'s real
`## DEC-002` precedent is authoritative.

### CON-004 — Historical validity
No completed Change (CHG-0001–CHG-0015) may become invalid, non-
conforming, or require retroactive modification as a result of this
Change, per `protocol/compatibility.md`'s "optional artifacts whose
absence preserves existing meaning" pattern. This holds regardless of how
DEC-001 resolves: per `protocol/compatibility.md:22`, a new integer
Protocol never retroactively invalidates already-completed history — it
only changes what a *future* Change opting into that Protocol integer
must do. DEC-001's Alternative B cost is a new integer Protocol for
Changes prospectively declaring it, not retroactive invalidation of
CHG-0001–CHG-0015.

### INV-001 — No duplicated normative authority
`protocol/artifact-structure.md` MAY reference Contract, Flow, or Policy
rules by stable identifier (e.g. "see C-014") but MUST NOT restate their
normative content in its own words. This applies the same
duplicated-authority discipline already required narrowly by FR-007 and
FR-009 to the guidance document as a whole (Specification Review SR-002).

## Acceptance Criteria

- **AC-001**: `protocol/artifact-structure.md` exists and defines all six
  principles listed in FR-001.
- **AC-002**: The document provides structural guidance for all fourteen
  Artifact types Discovery confirmed real, under their real names,
  including `Specification Drift` (FR-002).
- **AC-003**: `forge validate` behavior is unchanged for the SHOULD-only
  guidance — no new blocking check exists for it (FR-003). Contingent: if
  DEC-001 resolves as Alternative B, this AC is superseded by a revised
  AC covering the new narrow validation check, added at that time.
- **AC-004**: Verification guidance recommends `## Result` as the first
  substantive section; Review guidance recommends a `## Verdict` summary
  at the top, and the existing `## Iteration N — <verdict>` convention is
  explicitly preserved, not replaced (FR-004).
- **AC-005**: Plan guidance defines a canonically named, always-last
  `## Implementation Boundary` section (FR-005).
- **AC-006**: `protocol/contract/engineering.md` gains new rule(s) at
  `C-067` onward that reference, and do not restate, the guidance
  document (FR-006, INV-001).
- **AC-007**: `protocol/specification.md` gains `§41`, a brief pointer
  section matching the `§39`/`§40` style (FR-007).
- **AC-008**: `protocol/compatibility.md` gains an addendum documenting
  the Protocol-integer impact of this Change (FR-008).
- **AC-009**: The Codex Adapter's generated skill bundle includes
  `protocol/artifact-structure.md`'s content via the existing
  `_resource()` mechanism (FR-009) — mechanically verifiable by an
  automated test (see `test-strategy.md` TDD-001).
- **AC-010**: At least one canonical example under
  `examples/canonical-artifacts/` demonstrates outcome-first
  Verification/Review structure; no historical Change is reformatted
  (FR-010).
- **AC-011**: `ARCHITECTURE.md`, `docs/adr/`, and `CHANGELOG.md` are
  updated per Documentation Impact; no RFC is added (FR-011).
- **AC-012**: No file under `protocol/schemas/` changes (CON-002).
- **AC-013**: `forge validate` and `forge doctor` report the same
  overall project-valid status before and after Implementation
  (regression baseline; see `test-strategy.md` TDD-003).

## Unresolved Decisions

### DEC-001 — Enforcement level of the Canonical Artifact Structure

**Class:** `contract` · **Materiality:** material (changes `public_contract`
and potentially `compatibility_boundary`) · **Authority:** `human`
(contract-class floor, per `decision.yml` `authority_floor`) ·
**Owning Artifact:** Specification · **Status:** `resolved`

**Question:** Should the Canonical Artifact Structure remain entirely
`SHOULD`-level, non-Gate-checked guidance (FR-003 as written), or should
a specific element — most plausibly, the presence of a `## Result`
heading in Verification and a `## Verdict` heading in Review — be
elevated to a Contract `MUST` enforced by a new, narrow validation check
and an accompanying Gate condition?

**Evidence investigated:** `protocol/compatibility.md`'s own stated
criteria (lines 36-44) list "change the meaning of an existing required
field, stage, Gate, severity, or ownership mode" as a condition requiring
a new integer Protocol. Verification and Review are already required
stages; a `MUST`-and-Gate-checked heading would change what "valid
Verification/Review" means for any *future* Change declaring that
Protocol integer — it would **not** retroactively invalidate
CHG-0001–CHG-0015, exactly as Protocol 2's introduction did not
retroactively invalidate Protocol 1's completed Changes
(`compatibility.md:22`; corrected per Specification Review SR-001, which
found the original draft overstated this cost as retroactive
invalidation). A `SHOULD` interpretation requires no new Protocol integer
at all, following the exact "optional artifact" pattern already used
three times (CHG-0011, CHG-0013, CHG-0015).
Contract F-010 ("prefer explicit structures over premature ... hidden
automation") and the user's own stated non-goal ("Forge does not become
a Markdown linter... `forge validate` continues validating semantics, not
cosmetic preference") both weigh toward `SHOULD`.

**Alternatives:**
- **A — SHOULD-only (no Gate change, no Protocol bump).** Guidance is
  purely editorial; `forge validate` is untouched; every historical
  Change remains conforming with zero exception language needed.
- **B — MUST for the outcome heading only, in Verification and Review,
  Gate-checked.** Requires: a new, narrow Core validation check (heading
  presence only — not full structure, to avoid becoming a linter); an
  explicit compatibility exception or grace period for CHG-0001–CHG-0015
  (which do not have it); and, per `compatibility.md:36-44`, a new
  integer Protocol, since it changes the meaning of Verification/Review
  as previously-valid instances understood it.

**Trade-offs:** A is fully backward-compatible and matches this
repository's established pattern for additive Policy/Contract changes,
but relies entirely on agent discipline to actually fix the regression
Discovery found (no mechanical guarantee). B mechanically guarantees the
regression cannot recur, but introduces a new Protocol integer for a
single heading's presence, new validation code with linter-adjacent risk
(explicitly a non-goal), and a compatibility exception mechanism this
repository has not needed before for something this narrow.

**Recommendation:** **A (SHOULD-only)**, confidence: high. The single
most concrete finding in this Change — the CHG-0001→CHG-0015 outcome-
first regression — is real, but Discovery found no evidence the
regression was caused by absence of a Gate; it was caused by absence of
*any* canonical guidance at all. Publishing the guidance and having the
Codex Adapter surface it (FR-009) is a substantially smaller, fully
reversible intervention than adding a new Protocol integer and Gate
condition for one heading, and can be revisited later (as its own,
separately classified Change) if agent discipline proves insufficient
once the guidance exists. This Decision was **not** self-authorized: it is `contract`-class with
`authority_floor: human`, and required explicit human Decision before
`specification_review_passed` could be asserted.

**Decision (human, 2026-08-19):** Alternative A confirmed — the
Canonical Artifact Structure remains entirely `SHOULD`-level guidance. No
new integer Protocol, no new Gate, no new Core validation. Architecture's
DEC-002 and Plan were drafted assuming this outcome; the dependency was
stated explicitly throughout so this resolution required no revision to
either.

## Out of Scope

Everything listed in `intent.md`'s Out of Scope, plus: any change to
`forge/change@1`/`@2`, `forge/execution-provenance@1`/`@2`,
`forge/policy/decision@1`, or any other Schema; any new Flow stage or
Gate; any change to Finding severities or Review convergence; any
retroactive reformatting of CHG-0001–CHG-0015; any second Harness Adapter
implementation (Codex remains the only concrete Adapter; guidance itself
stays Harness-independent per NFR-002).

## Traceability

Requirement-to-evidence mapping is maintained in `traceability.yml`, not
duplicated here as a Markdown section — see Discovery's "Traceability
duplication risk" finding. `traceability.yml` is created once Plan/Tasks
identifiers exist to trace against.
