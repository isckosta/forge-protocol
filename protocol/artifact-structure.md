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

**Structural core:** a `# CHG-XXXX · <Change Title>` identity heading,
a short `Change Intent` callout, an `Overview` metadata table containing
only safely derivable fields, Problem, Goal, Scope, Out of Scope, and
Success Criteria. Structural headings remain in English; surrounding prose
uses the interaction language applicable to the project or user.

**Conditional:** Business Impact, Current Behavior, Desired Behavior,
Expected Outcome, Business Rules, and Operational Boundary appear only when
they materially clarify the Change. Do not generate empty sections or invent
context metadata such as Domain, Primary Module, or Business Risk. A compact
Evidence/References subsection MAY separate technical provenance from the
narrative when references would otherwise dominate it.

Intent explains why the Change exists and what must be true when it ends. It
is not a Specification, Implementation Plan, repository audit, or test plan;
formal requirement and acceptance identifiers belong to Specification, and
repository findings belong to Discovery. The scaffold emits the core layout
with authoring prompts; agents decide conditional applicability from the
Change content.

The redesign is presentation-only: the existing `forge:` front matter and
`schema: 1` remain unchanged, and historical artifacts are not rewritten.
`Non-goals` remains a valid historical/legacy heading where existing tooling
or prior Changes depend on it; new scaffolds use the reader-facing `Out of
Scope` heading.

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

**Structural core:** a clear Change Contract identity, Overview, Summary,
Classification (for STANDARD/FULL), Functional Requirements (`FR-xxx`),
Compatibility Statement, Specification Gate, and Out of Scope. Functional
Requirements SHOULD be self-contained units with a visible normative
`Requirement`, optional `Expected Behavior` and `Boundary`, and nearby
`Acceptance` content. The historical `Acceptance Criteria` heading remains
valid; new scaffolds use the more local `Acceptance` form without changing
its contract meaning.

**Conditional, present only when materially applicable:** User Stories
(`US-xxx`) are required when the Specification declares observable behavior;
they are omitted for genuinely technical Changes. Acceptance Scenarios,
Non-functional Requirements (`NFR-xxx`),
Security Requirements (`SEC-xxx` — or an explicit one-line `None` with
reason, not silent omission, §2.5), Invariants (`INV-xxx`), Constraints
(`CON-xxx`), and Unresolved Decisions (`DEC-xxx`, per `decision.yml`). User
Stories are behavioral context for a meaningful actor, capability, and
outcome; they do not replace Requirements and must not be invented for
technical Changes. Requirements, NFRs, and Constraints may exist without a
User Story, and relationships are many-to-many where applicable. User Stories
use first-person actor/capability/outcome prose and keep their Acceptance
Criteria nearby. Story
quality is reviewed semantically; the CLI only enforces the explicit
classification and stable identifier floor.

A Traceability Matrix MAY be included as an index connecting Discovery, User
Stories, Requirements, and Acceptance. It MUST NOT become the only
relationship representation or restate normative content already carried by
Requirements, Acceptance, or `traceability.yml`. When no User Stories apply,
the matrix SHOULD degrade to Discovery → Requirement → Acceptance.
Acceptance Scenarios MAY use Given/When/Then prose, but are not executable
BDD tests and do not require a parser or external framework.

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

### Test Design

**Structural core (redesigned by `CHG-0038`):** Overview, Test Strategy
(a Layer/Scope/Method table when Layers add clarity), a Coverage Map
indexing Requirement → Scenario → Method, per-scenario entries as stable
`### TD-xxx ·` headings with `Requirements`/`Stories`/`Type`/`Priority`
and `#### Purpose`/`#### Preconditions`/`#### Scenario`/`#### Evidence`/
`#### Failure Condition`/`#### Boundary` subsections (present only when
materially applicable — an empty subsection is omitted, not padded with
`N/A`), a closing Requirement Coverage table, Coverage Gaps, and a Test
Design Gate. `Type: Manual Acceptance` is a distinct category from
automated types and MUST NOT be presented as an automated guarantee.

This supersedes the prior guidance for this Artifact, which instructed
"do not redesign" the bare `## TDD-xxx` shape below. That instruction is
non-binding (C-067) and this document is itself expected to evolve when
real practice does — the same way this document's own Specification
entry was rewritten by `CHG-0037`. The reason for diverging here,
specifically: Test Design (FAST/STANDARD, when behavioral) now needs
explicit Requirement traceability, evidence typing, and manual/automated
separation to serve as a pre-Implementation verification contract; Test
Strategy (FULL) keeps its existing shape unchanged, so the two Artifacts
no longer share one description (see below).

### Test Strategy

**Structural core (unchanged):** Objective, Strategy, per-case entries as
`## TDD-xxx` headings (this repository's real, stable, already-consistent
convention — sixteen such cases in `CHG-0015/test-strategy.md` alone; do
not redesign it), Non-mechanical Validation for content that TDD cannot
reasonably cover (Protocol §19), Completion Criteria. Test Strategy is
the FULL-Flow Artifact; `CHG-0038` deliberately left it unredesigned so
this shape, and its sixteen real precedent cases, remain valid without
rewriting.

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
For an active Change adopted from CHG-0025 onward, the Plan/Implementation
boundary additionally requires the C-077 recorded human Decision; a Plan's
`status: approved` string alone is not authorization.

### Tasks

**Structural core (redesigned by `CHG-0039`):** an `Overview` (Change,
Flow, Status), an `Execution` section grouping the checklist under the
Plan item each group executes (`### Plan N · <Plan item title>`), and a
closing `## Status` section stating plainly what has and has not
started and why. `T-xxx` remains a stable checklist identifier
(`- [ ] T-xxx <work>`) — never a Markdown list number — and the
checklist itself remains the authoritative source of execution state;
`Overview`/`Status` present that state, they do not introduce a second,
manually-maintained one.

This supersedes the prior guidance for this Artifact, which described
only a flat checklist with no grouping (matching `CHG-0015/tasks.md`
closely). That prior guidance is non-binding (C-067) and was not wrong
for the Change it was written against; it stopped scaling once a Plan
grows past a handful of items and the reader has to reconstruct, by
hand, which Plan item produced which Task. The same pattern already
applied to Specification (`CHG-0037`) and Test Design (`CHG-0038`)
applies here: evolve the existing, stable shape rather than replace it
with an incompatible one. `Tasks` only exists as a Flow stage in FULL
(`protocol/flows/full.yml`). Behavioral STANDARD scaffolds additionally
materialize `tasks.md` and `traceability.yml` as conditional support artifacts
because C-079 requires Story-to-work traceability once Implementation starts;
technical Changes and FAST Changes without Stories do not receive them.

**Conditional, present only when the relationship actually exists:** a
compact inline metadata line beneath a Task —
`` `Plan: N` · `Requirements: FR-xxx` · `Stories: US-xxx` · `Test Design: TDD-xxx` ``
— referencing the Plan item, Requirement(s), User Story(ies), and/or
Test Strategy case(s) it implements. `TDD-xxx` is the correct
convention here (Test Strategy, FULL's own pre-Implementation
verification Artifact); `TD-xxx` is Test Design's convention. In STANDARD,
the conditional `tasks.md` is a support artifact rather than a Flow stage.
Not
every Task carries every reference kind, and a Task with none of them
is still valid — forcing a reference that does not exist would misstate
the Change's real traceability rather than clarify it.

Marking a Task complete (`- [x] T-xxx`) records that the work was
executed; it does not mean the Requirement it references is verified —
Verification remains the Artifact responsible for demonstrating that
(§2.2). Material work discovered during Implementation that the Plan
did not anticipate belongs to a Decision, a re-Plan, or Verification's
own findings, not to a Task silently added to absorb new scope.

### Verification

**Structural core (elaborated by `CHG-0040`):** `## Result` as the
first substantive section — one of `PASS`, `FAIL`, `SKIPPED`, or `NOT
APPLICABLE` — before any evidence. `INCONCLUSIVE` is deliberately not
offered: it has no precedent anywhere in this repository's Protocol or
Contract and does not exist in the current model. Render the value as
bold or plain text (`**PASS**`), not as a nested heading — every real
Artifact in this repository uses exactly one `#` heading, its title; a
second `#` under `## Result` breaks document outline semantics. This is
the direct, concrete fix for this document's own motivating finding
(§2.1) — `CHG-0001` already did this; `CHG-0015` did not.

After Result: a short `## Summary` giving an aggregate read (how many
Acceptance Criteria were checked, how many passed/failed, whether
Manual Evidence or Limitations apply) without reproducing individual
detail; then `## Acceptance Coverage`, a compact table mapping
`Acceptance | Requirement | Result | Evidence` by id (`AC-xxx`,
`FR-xxx`/`NFR-xxx`, `TDD-xxx`/`TD-xxx`, or an evidence reference) —
never the full text of an Acceptance Criterion, which already lives in
Specification (§2.2); then `## Test Evidence` and `## Forge Evidence`;
then `## Compatibility and Limitations`; then a short `## Conclusion`.
`## Manual Evidence` and `## Requirement Coverage` are **conditional**
(§2.5): Manual Evidence exists only when a real manual verification
occurred, kept distinct from Test/Forge Evidence so a reader never
mistakes a human observation for an automated guarantee; Requirement
Coverage exists only when it adds information Acceptance Coverage does
not already express (e.g. one Requirement covered by several Acceptance
Criteria, or by a static check with no `AC-xxx` of its own) — a Change
with a 1:1 Acceptance-to-Requirement relationship correctly omits it.

Test Evidence SHOULD reference a `TDD-xxx` cycle by id when
`tdd-evidence.yml` already records `red`/`green` for it, instead of
renarrating the RED→GREEN sequence by hand — the structured record is
the authority (§34 below); the Markdown presents it, it does not
duplicate it. Forge Evidence records only what the cited command
actually guarantees — `forge validate` passing is not itself evidence
that every semantic aspect of the Change was checked.

Result-Before-Evidence (§2.3) is only honest if it survives a `FAIL`:
when `Result` is `FAIL`, `Acceptance Coverage` still identifies which
criteria failed, and `Conclusion` MUST NOT imply the Change is ready
for its next gate. When `Result` is `SKIPPED` or `NOT APPLICABLE`, a
rationale proportional to the Change accompanies it — Verification
being skipped or inapplicable is itself a claim that needs a reason, not
a silent absence.

This elaborates, not replaces, the direction already normatively
required by C-068 and demonstrated by this document's own canonical
`examples/canonical-artifacts/verification.md` since `CHG-0016`; it is
not a new Gate obligation (C-067) and does not require any historical
`verification.md` to be rewritten — the same evolve-in-place pattern
`CHG-0037`/`CHG-0038`/`CHG-0039` already used for Specification/Test
Design/Tasks.

### Review

**Structural core (elaborated by `CHG-0041`):** a `## Verdict` aggregate
summary at the very top of the file, stating the final outcome across
every iteration a reader would otherwise have to scroll through to find
(a Change with several iterations, most negative and one final PASS,
currently gives a top-to-bottom reader every negative verdict before the
one that matters for Completion — e.g. `CHG-0008`, six iterations).
Render the aggregate verdict as bold or plain text, not a nested
heading, for the same reason as Verification above — one of `PASS` or
`REQUEST CHANGES`; no third state has real precedent or Contract
authority.

After Verdict: a `## Review Summary` giving a derived aggregate read
(iteration count, current subject, open Blocker/Major/Minor counts,
final iteration, result) — derived from `manifest.yml: review`
(`iteration`, `blockers`, `majors`, `minors`, `observations`), never a
hand-maintained count that can drift from it; then `##
Current Subject`, making the frozen revision explicit by referencing
the relevant `provenance.yml` record by id rather than inventing a new
freeze concept — the mechanism is `protocol/policies/review.yml`'s
`reviewer_resolver_separation` (`review_subject_freeze_required`,
`post_freeze_subject_mutation_invalidates_binding`), already real and
already enforced independently of this document; then `## Reviewer
Independence`, similarly referencing the reviewing Execution's
`provenance.yml` record (`role: review`) as evidence of a distinct
Execution and Execution Context from the Implementation or Resolution
under review, not a bare declaration; then `## Open Findings`, a
compact index (`Finding | Severity | Status | Iteration`) of findings
still open — present only when findings remain open (§2.5); when none
do, a short `No open findings.` line replaces the table, never an empty
one.

The existing, already-working `## Iteration N — <verdict>` convention
per iteration is preserved **exactly unchanged** beneath these new
sections, not replaced, not renamed, not renumbered, and not wrapped
under a new parent heading — every real `review.md` from `CHG-0016`
onward uses this flat form, and no real precedent for a nested
`Iteration History` grouping exists anywhere in this repository's
history. Findings use `Rxxx` (Strict Review's real, stable prefix since
`CHG-0016` — distinct from Specification Review's `SR-xxx`; the older
`CHG-XXXX-Rxxx` change-scoped form from `CHG-0008`–`CHG-0014` is
historical and not reproduced in new scaffolds). A finding's Required
Resolution states the property that must hold, not a prescribed
implementation — Reviewer identifies and classifies the problem;
Resolver chooses the fix within the Contract (C-026). BLOCKER and MAJOR
findings carry evidence (C-025); MINOR and OBSERVATION findings are not
required to. A closing `## Conclusion` states the effect of the Verdict
in one or two sentences and MUST NOT imply Completion when later Flow
gates remain outstanding.

### Specification Drift

**Structural core (elaborated by `CHG-0042`):** a chronological
narrative — `Context`, `Trigger`, `Original Specification`, `Observed
Conflict`, `Root Cause`, `Evidence`, `Specification Correction`,
`Impact Assessment`, `Affected Artifacts`, `Re-verification`, and a
`## Final decision` section placed **last**, not first (`CHG-0012`'s
real casing — lowercase "decision" — preserved). This is a deliberate
exception to Result-Before-Evidence (§2.3): this Artifact's
responsibility (§2.2) is tracing *how* a drift was discovered and
resolved, which is inherently sequential, not announcing a verdict a
reader needs before anything else — `CHG-0012/specification-drift.md`
already does this well. Unlike every other Artifact in this document,
Specification Drift has no scaffold, no Flow stage, and no code
representation anywhere in the repository (confirmed by `CHG-0042`'s
own Discovery) — it is created by hand, only when Protocol §13
actually applies, and this elaboration changes nothing about that;
this section remains guidance for hand-authoring it, not a template a
tool renders.

Not every occurrence needs every section (§2.5): a simple drift may use
only `Context`, `Root Cause`, `Evidence`, `Specification Correction`,
and `Final decision`; a complex one — `CHG-0012`'s four-attempt
Resolution history is the real precedent — may need the full sequence.
`Context` and `Trigger` establish what Change, stage, and Review/
Resolution/finding revealed the problem, without repeating the
Change's full history. `Original Specification` and `Observed
Conflict` separate what the contract said from what behavior actually
demonstrated, before concluding why — a premature Root Cause tends to
misdiagnose. `Root Cause` explains *how* the ambiguity or gap entered
the contract (missing case, contradictory Requirements, incorrect
domain assumption), not merely that it existed. `Evidence` stays
compact — findings, tests, diffs, Contract/Protocol rules — never full
logs.

**Specification Drift is not a second Specification** (C-067's
non-duplication principle applies here too): `Specification Correction`
records what changed and why, but the corrected `specification.md` —
or the affected Requirement directly — remains the one authoritative
contract;
the correction MUST be applied there, not left to exist only in this
document. Likewise, this Artifact does not substitute for **Resolution**
(the `role: resolution` provenance-recorded work a Finding may require),
**Decision** (`manifest.yml: decisions[]`, `DEC-xxx` — the escalation
mechanism when a drift reveals more than one valid normative answer,
per C-051–C-059), or **Review** (whose independent verdict a
Specification correction does not itself satisfy — correcting the
Specification is not the same as resolving the Finding that revealed
it; a new subject still needs independent re-review). When the
correct semantics are still undecided, `Final decision` MUST NOT be
fabricated — the real, undecided state is recorded instead, and a
material trade-off routes through the Decision mechanism rather than a
silent choice.

**Specification Drift is materially narrower than Specification
Review** (`CHG-0013/specification-drift.md` states this real
distinction plainly): Protocol §13 requires Drift only when
*Implementation evidence* invalidates the Specification. A correction
made during adversarial Specification Review, before Architecture,
against no Implementation evidence, is ordinary
`specification-review.md` iteration (`SR-xxx`), not Drift — and a
typo fix, wording clarification, or formatting change with no semantic
consequence is not Drift either, regardless of when it happens.
`Impact Assessment`/`Affected Artifacts` name only the areas actually
affected (Plan, Tasks, Test Design/Test Strategy, Verification,
Review, Compatibility) — a Verification that already passed against
the old contract may no longer be sufficient evidence once the
Specification changes materially, and `Re-verification` records what
new evidence closing that gap requires, without executing it here.

### Knowledge Capture

**Structural core (elaborated by `CHG-0043`):** `What Changed`,
`Durable Knowledge`, `Consequences for Future Changes`, `References` —
the same four headings, in the same order, that seven of this
repository's 25 real occurrences already use precisely
(`CHG-0021`, `CHG-0022`, `CHG-0023`, `CHG-0030`, `CHG-0033`,
`CHG-0035`, `CHG-0036`; FULL Flow only, `required: true`, gating
Completion via `required_knowledge_capture_complete`). The other 18
are broader real content precedent for what belongs in this Artifact
without using this exact structured form — some predate it and use
different or no headings (`CHG-0016`, discussed below, is a flat
bullet list with none at all). This elaboration formalizes the
already-dominant structured shape as the recommended one going
forward; no section is added, removed, or reordered relative to it.
Content SHOULD be knowledge that outlives this Change — it SHOULD NOT
restate Specification, Architecture, Verification, Review, or
Specification Drift content that already lives in those Artifacts
(§2.2); reference them instead of duplicating them. `What Changed`
stays short — context for the knowledge below, not a file-by-file
account (that belongs to Plan, Tasks, or the diff).

`Durable Knowledge` is the central section. The real precedent shows
two legitimate shapes: short prose for a single dominant lesson
(`CHG-0033`, `CHG-0035`, `CHG-0036`, most occurrences), or a flat list
of independent lessons when several exist (`CHG-0016`, seven distinct
lessons). `### K-xxx · <title>` items are available for the latter
case, but ids are optional structure, not a required namespace — no
`K-xxx` id has ever appeared in this repository's history before this
elaboration, and no tooling consumes it; a Change with one lesson
correctly uses plain prose. The test that decides whether something
belongs here: will it still be true and useful once no one is working
on this Change anymore, and could another Change decide better by
knowing it? An honest "no additional knowledge beyond this Change was
identified" is itself a valid, complete answer — proportionality
(§2.5) applies here exactly as it does to `## Checked and found sound`
sections and to Specification Drift's own real "No Drift to record"
precedent; nothing here requires fabricated content merely because the
Flow requires the file. `Consequences for Future Changes` gives each
conclusion a scope (Forge Core, Harness Adapter, CLI, review workflow,
…) rather than a system-wide claim the evidence does not support.

**Distinct from adjacent Artifacts:** Decision (`DEC-xxx`) records
which option was chosen; Architecture records the design; Specification
records this Change's own obligation; Review records a problem found in
the reviewed subject; Specification Drift records how a contract had to
change. Knowledge Capture may preserve the durable, reusable lesson any
of those reveals — it does not restate the source. It is also distinct
from the **Forge Experience Report** (`docs/experience-reporting.md`):
FER is opt-in, local, and records what happened during a real
execution (expected/observed/evidence/impact/workaround), stored
outside any Change's own directory; Knowledge Capture is always present
when the Flow requires it and records distilled, durable knowledge
scoped to this Change.

`References` points at what already exists rather than duplicating it.
When the work is materially architectural or Protocol-level, Contract
F-008 already requires a `docs/adr/`/`docs/rfcs/` entry as part of the
work itself — `CHG-0036`'s `## References` cites
`docs/rfcs/0006-merge-readiness-gate.md` this way directly; `CHG-0013`,
`CHG-0015`, and `CHG-0016` predate this structural section and mention
the same real ADR practice in unstructured prose instead, not through a
dedicated `References` heading — either form points at what F-008
already produced, and `References` should do the same going forward.
This document does not invent a separate "promotion" workflow for
moving content into permanent documentation after the fact, since no
such mechanism exists
today.

### Inspection

**Structural core (elaborated by `CHG-0044`):** proportionality first,
still — whatever the fix actually requires explaining, nothing more, and
nothing less. This is Inspection's one non-negotiable property (§2.5,
NFR-001 of `CHG-0016`'s own Specification); this elaboration adds an
optional vocabulary and a consistent identity heading around that
property, it does not relax it. A short paragraph is a fully conforming
example for a trivial fix — `CHG-0005/inspection.md` is a title followed
by two short paragraphs of real context, three sentences total (a
lifecycle gap and a stray misleading test name), not a title-only file,
but it is still the repository's real minimal-Inspection precedent. An
86-line file with a confirmed root cause, a precedent for the fix, and a
documented Strict-Review correction is equally conforming for a
genuinely more complex one (`CHG-0012`). No section below is expected,
required, or validated — a real
`inspection.md` may use zero of them, one, or several, in any order,
exactly as six real occurrences already do (`CHG-0005`, `CHG-0012`,
`CHG-0024`, `CHG-0026`, `CHG-0028`, `CHG-0029`), each proportional to its
own fix and each using its own organic heading names for the same
handful of underlying concepts.

**Optional structural vocabulary:** when an Inspection genuinely needs
more structure than prose alone, a consistent (not mandatory) vocabulary
is available — `Observation`, `Evidence`, `Root Cause`, `Impact`, `Fix
Boundary`, `Open Question`, `Conclusion`, in English regardless of the
surrounding prose's interaction language — the same convention this
document's own "Intent" entry already states ("Structural headings
remain in English; surrounding prose uses the interaction language
applicable to the project or user"). `Observation` separates the
observed symptom and its reproducing condition from any conclusion about
cause — `CHG-0028`'s "Current state" is real organic precedent for the
same concept under a different name. `Evidence` is exact real precedent
already (`CHG-0024/inspection.md:33`, `CHG-0029/inspection.md:10`, both
literally `## Evidence`). `Root Cause` records the confirmed mechanism,
not merely that something is wrong — `CHG-0024/inspection.md:11`
(`## Root Cause`) and `CHG-0012/inspection.md:10` (`## Root cause`) are
real precedent for the same exact concept; "the validator is broken" is
not a Root Cause, "the aggregator ignores the child status the
validator already reports correctly" is the shape a real one takes. When
cause is not yet confirmed, say so explicitly (a
plain "Likely cause" is sufficient) rather than presenting a hypothesis
as certainty; no numeric or multi-level confidence scale is needed. `Fix
Boundary` — particularly useful for FAST, where scope creep is the real
risk this section exists to prevent — states the smallest safe boundary
of the fix and what does not need to change; `CHG-0012`'s own "Scope
verified not to include" is real precedent for the same concept under a
different name. `Impact` and `Open Question` are used only when
materially applicable (§2.5) — a trivial fix with no wider blast radius
and no open question correctly omits both. `Conclusion` closes with the
outcome in a sentence or two; it is not a Plan, and does not enumerate
implementation steps.

**Evidence quality:** a relevant claim is backed by something concrete —
code, an existing test, a command and its output, a log, observed
runtime behavior, or normative documentation — not unmarked conjecture.
`Symptom → Reproduction → Cause` is a preferable shape to a vague
narrative wherever it applies: what was observed, what reliably produces
it, and (only once confirmed) the mechanism responsible —
`CHG-0012/inspection.md:12` demonstrates this concretely (an exact file
and line, the reproducing condition, and the confirmed effect) without
naming the pattern; this document names it so future Inspections reach
for it deliberately. Evidence stays compact — a short command, a small
diff, a one-line log — never a large dump.

**Inspection is not Discovery, Specification, Plan, Verification, or the
Forge Experience Report**, and the distinction matters because Inspection
and Discovery never coexist in the same Change (FAST has `inspection`;
STANDARD and FULL have `discovery` + `specification` + `plan` instead;
`protocol/flows/*.yml` confirms no Flow has both). Discovery is broad,
pre-Specification understanding-building; Inspection is a narrow,
fix-scoped investigation — it does not need to become a mini-Discovery
merely because a Flow escalation is possible. Specification defines
`FR-xxx` contract obligations; Inspection has no requirement-numbering
convention of its own and does not need one. Plan records approved work
items; Inspection's `Fix Boundary` states what must *not* change, it is
not a list of approved work. Verification records what was checked
*after* the fix, Result-first (§2.3); presenting post-fix verification
evidence inside `inspection.md` would misattribute Verification's own
responsibility (§2.2) — Inspection records what was found, not what was
later confirmed. The Forge Experience Report
(`docs/experience-reporting.md`, opt-in, local, stored outside any
Change's own directory) records what happened during a real execution;
Inspection records technical understanding of the defect itself. When an
Inspection reveals complexity a Change was not classified for, the real
escalation mechanism already exists (`protocol/flows/fast.yml`'s
`escalation.enabled`, `automatic_downgrade: false`;
`protocol/specification.md` §11: "FAST -> STANDARD, STANDARD -> FULL,
FAST -> FULL... Automatic downgrade is forbidden") — use it, rather than
continuing to force STANDARD- or FULL-level content into `inspection.md`
because the file already exists.

No heading in this section is required, validated, or expected to appear
in every occurrence (§2.5) — the scaffold accordingly emits no
section heading at all beyond the document's own identity heading (§4's
introduction), only a short authoring comment pointing back to this
vocabulary.

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
