# Canonical Artifact Structure

Status: Stable (non-binding guidance — see `protocol/specification.md` §41 and `protocol/contract/engineering.md` C-067)

## 1. Purpose

Forge's Protocol defines what each Change stage and Artifact must
establish (Contract, Flow, Policy). It does not define how that content
should be organized for a human reader. This document fills that gap: it
is canonical guidance for the information architecture of Forge's human
Markdown Artifacts, introduced by `CHG-0016`.

This document is guidance, not obligation — see
`protocol/contract/engineering.md` C-067 for the exact, authoritative
statement of what that means; it is not restated here (INV-001, below).
An Artifact that does not follow this structure is not non-conforming.

This document MAY reference Contract, Flow, and Policy rules by stable
identifier. It MUST NOT restate their normative content in its own words
(Specification INV-001) — where this document and a Contract rule appear
to overlap, the Contract rule is authoritative and this document is
wrong if it says otherwise.

## 2. Principles

### 2.1 Progressive Disclosure

Information should generally be reachable at three levels: **Outcome**
(what a reader needs immediately — a verdict, a conclusion, an
objective), **Reasoning** (context, rationale, trade-offs, Requirements,
Findings), and **Evidence** (commands, outputs, references, paths,
commits, validation detail). A reader should not need to consume Level 3
to discover Level 1.

This repository's own history shows both directions. `CHG-0001/verification.md`
opened with `## Result` immediately after its title — Level 1 first. By
`CHG-0015/verification.md`, that heading was gone entirely; the PASS/FAIL
outcome existed only inside a prose evidence paragraph and in
`manifest.yml`, not in the human-readable Artifact. The convention
existed and was lost, not merely never formalized — see §4 (Verification)
and §4 (Review) below for the recommended fix.

### 2.2 Artifact Responsibility

An Artifact SHOULD primarily contain information belonging to the
lifecycle responsibility it represents. Discovery contains what was
found, not what was decided. Plan contains the approved work and its
recorded authority evidence, not what Implementation later discovered.
Verification contains what was checked
and its result, not a re-argument of the Specification. When information
belongs to a different Artifact's responsibility, it SHOULD be referenced
from where it lives, not duplicated.

### 2.3 Result-Before-Evidence

Decisional and verificatory Artifacts SHOULD present their outcome before
their supporting evidence. This is Progressive Disclosure applied
specifically to Verification and Review, where the cost of losing it is
highest: a reviewer or a future reader who only needs to know PASS or
FAIL should not have to read the evidence that produced that answer to
find it.

### 2.4 Scanability

Large Artifacts should favor predictable headings, short summaries,
tables where they genuinely improve legibility, stable identifiers
(`FR-xxx`, `DEC-xxx`, `TDD-xxx`), and a clear separation between
conclusion and evidence. Not everything benefits from a table, and
narrative remains the right representation wherever it is the more
faithful one — Specification Drift's own responsibility (tracing how a
correction was found and resolved) is inherently narrative, and forcing
a table onto it would reduce, not improve, scanability. See §4.

### 2.5 Proportionality

An Artifact SHOULD NOT contain a section with no material content for
that Change merely to look complete. A four-line `inspection.md` for a
trivial FAST fix is a fully conforming example, not an incomplete one —
see `CHG-0005-review-completion-gate/inspection.md`. Sections in §4 below
marked *conditional* exist only when materially applicable; this
document's own `specification.md` (`CHG-0016`) demonstrates the pattern
directly — its Security Requirements section states `None` in one line
with a one-sentence reason, rather than being omitted silently or padded
with boilerplate.

### 2.6 Extensibility

The structural cores in §4 are a floor, not a ceiling. A Change MAY, and
often SHOULD, introduce domain-specific sections its own nature requires
— a Migration Strategy, a Threat Model, a Data Model, a Rollback
Strategy, a Compatibility Matrix, a Failure Semantics section — that no
generic guidance predicts. This document does not enumerate every
possible domain-specific need and does not attempt to.

## 3. Real Artifact Taxonomy

This document covers the Artifact types this repository's own history
actually produces, under their real names: Intent, Discovery,
Specification, Specification Review, Architecture, Test Design, Test
Strategy, Plan, Tasks, Verification, Review, Specification Drift,
Knowledge Capture, and Inspection. `Specification Drift` (Protocol §13)
is this repository's real name for a normative correction discovered
during Review or Resolution that changes the Specification's meaning —
it is not called "Resolution" here, because this repository does not
call it that.

## 4. Per-Artifact-Type Guidance

Each entry below distinguishes **structural core** (what almost always
belongs, in the recommended order), **conditional** (present only when
materially applicable to the Change), and **optional** (domain-specific
extension, §2.6).

Every entry's structural core additionally includes, as its very first
element, a `forge:` YAML frontmatter block (`artifact`, `schema`,
`change`, `status`) before the `# <Type> — <title>` heading — this
repository's single most consistent real Artifact convention (present in
every Change from `CHG-0006` onward without exception, `CHG-0003` and
`CHG-0005` being the only pre-existing gaps). It is not restated per type
below to avoid repeating it fourteen times; omitting it is a defect, not
a style choice, unless a Change states explicitly why a given Artifact
does not carry it.

### Intent

**Structural core:** Summary, Problem, Desired Outcome, Scope, Out of
Scope, Success Criteria. This matches real, stable precedent closely —
no material change is recommended.

### Discovery

**Structural core:** an Executive Summary / Recommendation as the first
section, stating the strongest finding and its implication before the
detailed investigation — followed by the investigation itself, organized
by subject rather than by numbered finding IDs. No sampled Discovery in
this repository's history uses an Executive Summary; none uses `D-xxx`
numbered findings either, and none should be introduced: nothing
downstream (no Schema field, no `traceability.yml` entry, no `decisions[]`
entry) ever references a Discovery finding by ID the way it references
`FR-xxx` or `DEC-xxx`, so a numbered scheme here would add ceremony
without a consumer. **Conditional:** a Compatibility Finding section when
the Change touches `protocol/compatibility.md`'s concerns; an Open
Questions section when a Decision is being escalated from this stage.

### Specification

**Structural core:** Summary, Classification (for STANDARD/FULL),
Functional Requirements (`FR-xxx`), Acceptance Criteria (`AC-xxx`,
mapped to Requirements), Out of Scope. **Conditional, present only when
non-empty:** Non-functional Requirements (`NFR-xxx`), Security
Requirements (`SEC-xxx` — or an explicit one-line `None` with reason, not
silent omission, §2.5), Invariants (`INV-xxx`), Constraints (`CON-xxx`),
Unresolved Decisions (`DEC-xxx`, per `decision.yml`). **Do not add** a
Markdown Traceability section restating what `traceability.yml` already
carries — that would duplicate normative authority (§1; this document's
own Specification omits one for this exact reason).

### Specification Review

**Structural core:** Verdict at the top (the same PASS / REQUEST CHANGES
pattern Strict Review already uses), Findings (`SR-xxx` — this
repository's real Specification Review finding prefix, distinct from
Strict Review's `Rxxx`), Checked and found sound, Conclusion.
**Conditional:** a Resolution Applied section when findings were resolved
within the same authoring session rather than deferred; an Addendum
section when a Decision the Review evaluated resolves after the Review
itself was written (this document's own `CHG-0016/specification-review.md`
demonstrates both).

### Architecture

**Structural core:** Solution Summary first, then Architectural Goals,
then the design content itself. Embedded Decision records use `## DEC-xxx`
— never `ADR-xxx`. `docs/adr/NNNN-slug.md` is a separate, project-durable
namespace (Contract F-008) for architectural knowledge that outlives a
single Change; a Change's own `architecture.md` is scoped to that Change.
Mixing the two numbering spaces is a real risk this document exists partly
to prevent — see this repository's own `CHG-0015/architecture.md:37`,
which already keeps them separate in practice.

### Test Design / Test Strategy

**Structural core:** Objective, Strategy, per-case entries as `## TDD-xxx`
headings (this repository's real, stable, already-consistent convention
— sixteen such cases in `CHG-0015/test-strategy.md` alone; do not
redesign it), Non-mechanical Validation for content that TDD cannot
reasonably cover (Protocol §19), Completion Criteria. Test Design and
Test Strategy are not the same Artifact scaled differently — Test Design
(FAST/STANDARD, when behavioral) and Test Strategy (FULL) have distinct
Flow roles and both keep this same shape.

### Plan

**Structural core:** a flat, numbered list of concrete work items, each
naming the files or resources it touches — **not** one heading per work
item. No sampled real Plan in this repository's history (`CHG-0007`,
`CHG-0013`, `CHG-0015`) uses heading-per-item structure; a flat numbered
list is already dense, cross-referential, and scanable in practice, and
introducing headings would add ceremony without improving it. The list is
followed by a canonically named, always-last `## Implementation Boundary`
section stating explicitly that reaching a `tasks_ready` Gate is not
authorization to begin Implementation, and that Implementation-time
discoveries belong in Verification, a Decision record, or a documented
re-Plan — not in a silent edit to already-approved Plan content. Two
Changes (`CHG-0013`, `CHG-0015`) independently hand-wrote nearly the same
paragraph under an ad-hoc "Explicit boundary" heading; naming and
positioning it canonically removes the need to reinvent it a third time.

### Tasks

**Structural core:** a checklist (`- [ ] T-xxx <work>`) referencing the
Plan items it executes, and a closing `## Status` section stating
plainly what has and has not started and why. Matches real, stable,
minimal precedent (`CHG-0015/tasks.md`) closely.

### Verification

**Structural core:** `## Result` as the first substantive section —
one of `PASS`, `FAIL`, `SKIPPED`, or `NOT APPLICABLE` — before any
evidence. `INCONCLUSIVE` is deliberately not offered: it has no
precedent anywhere in this repository's Protocol or Contract and does
not exist in the current model. Render the value as bold or plain text
(`**PASS**`), not as a nested heading — every real Artifact in this
repository uses exactly one `#` heading, its title; a second `#` under
`## Result` breaks document outline semantics. After Result: a Summary (a
short table mapping `AC-xxx` to its individual result reads well here —
§2.4), then Test Evidence and Forge Evidence, then
Compatibility/Limitations, then a short Conclusion. This is the direct,
concrete fix for this document's own motivating finding (§2.1) —
`CHG-0001` already did this; `CHG-0015` did not.

### Review

**Structural core:** a `## Verdict` aggregate summary at the very top of
the file, stating the final outcome across every iteration a reader would
otherwise have to scroll through to find (a Change with several
iterations, most negative and one final PASS, currently gives a
top-to-bottom reader every negative verdict before the one that matters
for Completion — e.g. `CHG-0008`, six iterations). The existing,
already-working `## Iteration N — <verdict>` convention per iteration is
preserved unchanged beneath it, not replaced. Render the aggregate
verdict as bold or plain text, not a nested heading, for the same reason
as Verification above. Findings use `Rxxx` (Strict Review's real, stable
prefix — distinct from Specification Review's `SR-xxx`).

### Specification Drift

**Structural core:** narrative — Root Cause, Evidence, and a `## Final
decision` section placed **last**, not first. This is a deliberate
exception to Result-Before-Evidence (§2.3): this Artifact's
responsibility (§2.2) is tracing *how* a drift was discovered and
resolved, which is inherently sequential, not announcing a verdict a
reader needs before anything else — `CHG-0012/specification-drift.md`
already does this well.

### Knowledge Capture

**Structural core:** What Changed, Durable Knowledge, Consequences for
Future Changes, References. Matches real, stable precedent; no material
change is recommended. Content SHOULD be knowledge that outlives this
Change — it SHOULD NOT restate Specification, Architecture, or
Verification content that already lives in those Artifacts (§2.2).

### Inspection

**Structural core:** whatever the fix actually requires explaining —
nothing more. A four-line file (title only) is a fully conforming
example for a trivial fix (`CHG-0005`); an 86-line file is equally
conforming for a genuinely more complex one (`CHG-0012`). This document
introduces no new expected section for Inspection (§2.5, NFR-001 of
`CHG-0016`'s own Specification) — FAST's proportionality is a property
this document must preserve, not one it gets to relax.

## Plan approval boundary

When a Plan is declared `approved`, the Plan SHOULD preserve the explicit
human confirmation at the Plan/Implementation boundary using the canonical
Forge markers `forge:plan-approval-confirmation` and
`forge:plan-approval-record`. The confirmation record SHOULD identify the
operator in provenance. These markers are language-invariant; surrounding
prose MAY use the configured interaction language. C-077 remains the normative
Contract rule and `forge validate` is the enforcement point.

## 5. How This Document Is Projected

A Harness Adapter includes this document's content by reference in its
generated representation, the same way it includes Flow and Contract
content — it does not redefine or paraphrase it (Protocol §34). This
document does not restate any specific Adapter's mechanics here (§1,
INV-001, NFR-002 of `CHG-0016`'s own Specification).
