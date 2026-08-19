# Discovery — Canonical Artifact Structure for Human-Readable Change Documentation

## Executive Summary

Forge's Protocol normatively defines Artifact *semantics* (what each stage
must establish) but has no normative content for Artifact *structure*
(how that content should be organized for a reader) — the label
"Artifact semantics" exists in `ARCHITECTURE.md:36` but no file fills it.
Comparing seven real Changes shows this gap has real cost: outcome-first
presentation regressed rather than improved over time (CHG-0001 had
`## Result`; CHG-0015 does not), documentation volume grew ~2.7x without
proportional complexity growth, and the Plan/Implementation boundary is
reinforced by hand-written prose reinvented each session instead of by
structure. No existing abstraction fills this gap. `change.schema.json`'s
`artifacts` field is untyped (`{"type": "object"}`), so a Canonical
Artifact Structure can be added with **zero Schema change**. The
project's own layering pattern (`ARCHITECTURE.md` §7: Canonical Protocol
→ ... → Harness Adapter Representation) and the Codex Adapter's existing
projection-by-reference mechanism (it includes raw Flow/Contract content
rather than reimplementing it) both directly support where this guidance
should live and how it should reach a Harness without duplicating
authority. Recommendation: introduce the guidance as new canonical,
**non-binding** content in `protocol/`, Adapter-projected by reference,
with no new Protocol integer required — contingent on one material,
human-authority Decision recorded in Specification (see DEC-001 there):
whether any part of this guidance becomes Contract-binding (`MUST`,
Gate-checked) or remains entirely `SHOULD`-level editorial guidance.

## Repository State at Investigation Time

HEAD: `7985080` (`docs(chg-0015): T-012 -- freeze Implementation subject,
record provenance`), branch `main`, working tree clean. `CHG-0015` is
in-flight (`manifest.yml` state: `strict_review`; `verification: passed`;
`review: pending`) — the most recent complete artifact set available for
comparison is therefore CHG-0015's pre-Verification/Review artifacts, plus
Review from earlier Changes. Fifteen Change directories exist; `CHG-0009`
was deliberately deregistered (commit `67fd0dd`, cited by
`CHG-0014/discovery.md:14-15` and `CHG-0015/discovery.md:14-15`) — skipped
identifiers are an established, accepted pattern, not an error to correct.
Next available Change identifier: **CHG-0016** (this Change).

## Change Creation Mechanism

No `forge change create` command exists. `pyproject.toml`'s `forge`
entrypoint (`forge_cli.app:app`) exposes only `version`, `init`,
`validate`, `doctor`, and `adapter {list,configure,plan,install,validate,
doctor,update}` — all infrastructure, matching Contract F-005 / Protocol
§31 (CLI boundary). `protocol/specification.md:19-21` states Forge
"assigns the next available stable identifier when the repository-native
Change is created," but no code implements assignment; in practice, the
next sequential unused ID is determined by inspecting
`.forge/changes/` directly, exactly as this Discovery did. `forge
validate` is diagnostic only, not a creation path.

## Existing Normative Layers (what already governs this Change)

- **Protocol** (`protocol/specification.md`, 40 sections, Protocol 1) +
  **Protocol 2 delta** (`protocol/versions/2/specification.md`, strictly
  additive over Protocol 1 — Strict Review independence, provenance,
  convergence, Resolution Verification). No section defines Artifact
  structure; §39 (Unresolved Decision Management) and §40 (Delegated
  Execution Authority) are the two most recent additions and both follow
  the same pattern this Change should follow: a short normative paragraph
  in `protocol/specification.md` pointing to full detail in a dedicated
  policy/architecture file, plus a `protocol/compatibility.md` addendum
  explaining why no new integer Protocol was required.
- **Engineering Contract**: two layers, not duplicates.
  `protocol/contract/engineering.md` (canonical, C-001–C-066) governs every
  Forge project; `.forge/contract/engineering.md` (project-local, F-001–F-011)
  governs this repository specifically and explicitly says so
  (`.forge/contract/engineering.md:5`, "governed by
  `protocol/contract/engineering.md` plus the rules below"). F-008 is
  directly relevant: *"Material Protocol Changes require RFC. Material
  Architecture Changes require ADR."* F-010: *"Forge MUST prefer explicit
  structures over premature plugin systems, services, or hidden
  automation."*
- **Policies**: `protocol/policies/decision.yml` (`forge/policy/decision@1`)
  is the mature, already-in-production Unresolved Decision Management
  mechanism (introduced by CHG-0013, used live in CHG-0015 — see its
  `manifest.yml` `decisions:` array with `DEC-001`/`DEC-002`). It defines
  four Decision Classes (`product`, `contract`, `architectural`,
  `technical`), default and floor Decision Authority per class
  (`product`/`contract` floor at `human`; `architectural` defaults
  `agent_with_review`; `technical` defaults `agent`), a Materiality test,
  and `ownership.owning_artifact_by_class` (`product`/`contract` →
  Specification; `architectural` → Architecture; `technical` → Plan or
  Tasks). This Change reuses it directly rather than inventing anything
  parallel, per the user's own Discovery instruction.
- **Schemas**: `change.schema.json` / `change-v2.schema.json` both type
  `artifacts` as a bare `{"type": "object"}` — no per-Artifact-file shape
  is Schema-enforced today. A Canonical Artifact Structure therefore
  requires **no Schema change** to exist; `traceability.schema.json` and
  `tdd-evidence.schema.json` remain the deterministic machine-readable
  layer and are explicitly out of this Change's scope.
- **ARCHITECTURE.md §7** gives the exact layering the user's prompt asked
  Discovery to validate: `Canonical Protocol → Protocol Defaults →
  Project Configuration → Project Policies → Project Contract Extensions
  → Effective Forge Configuration → Harness Adapter Representation`.
  §5 lists "Artifact semantics" as canonical-`protocol/` content — this
  is direct, pre-existing normative authority that the new guidance
  belongs in `protocol/`, not in a Contract obligation, an Adapter, or a
  README (resolves Option A vs B vs C vs D from the user's prompt via
  Evidence Resolution, not fresh analysis — see `specification.md`
  DEC-002).
- **Codex Adapter projection** (`src/forge_cli/adapters/codex/
  projection.py`, `resources/skills/workflow.md`): the existing mechanism
  loads the *canonical* Flow YAML and Contract Markdown content and
  injects them, largely verbatim (with a SHA-256 digest per resource, via
  `_resource()`), into a generated Codex skill — it does not restate their
  semantics in Adapter-authored prose. `adapter.yml` declares capability
  `skills: true`. This is the direct precedent for how the new guidance
  should reach a Harness: by inclusion/reference, not redefinition.

## Comparative Artifact Analysis (seven real Changes)

Investigated: CHG-0001 (foundation baseline, 896 total Markdown lines),
CHG-0007 (`protocol-v1-contract-freeze`, FULL, 838 lines, has
`specification-review.md`), CHG-0008 (`reviewer-resolver-separation`,
FULL, 565 lines, 6 Review iterations), CHG-0011 (`review-convergence-
boundary`, FULL, 1420 lines, has `specification-drift.md`), CHG-0013
(`unresolved-decision-management`, FULL, 1845 lines — the mechanism this
Change reuses), CHG-0014 (`golden-path-codex-onboarding`, **STANDARD**,
1435 lines), CHG-0015 (FULL, in-flight, 2404 lines). CHG-0005 and
CHG-0012 (FAST, `inspection.md`) were also read for proportionality
evidence.

**Result-before-evidence regressed, it was never absent.**
`CHG-0001/verification.md:9-11` opens directly with `## Result` and a
short PASS statement. `CHG-0015/verification.md` has no `## Result`
heading anywhere; its first heading is `## Test evidence`, and the
"423 passed, 0 failed" outcome is embedded mid-prose inside a bullet.
PASS/FAIL for CHG-0015 exists only in `manifest.yml`
(`verification: {status: passed}`) — a human reading the `.md` file
cannot get the result without reading the evidence first. CHG-0011 and
CHG-0013 show the same regression. This is the strongest, most concrete
finding in this Discovery and directly motivates the Specification's
outcome-first requirement for Verification and Review.

**Review's verdict-in-heading pattern is real but incomplete.**
Every sampled Review (`CHG-0001`, `CHG-0007`, `CHG-0008`, `CHG-0011`,
`CHG-0014`) already writes `## Iteration N — PASS` /
`## Iteration N — REQUEST CHANGES` as the heading text itself — a real,
stable convention the Specification should recognize, not invent. What is
missing is an aggregate summary: CHG-0008 has six iterations (five
`REQUEST CHANGES`, one final `PASS`); a top-to-bottom reader sees five
negative verdicts before the outcome that actually matters for
Completion. No sampled Review has a top-of-file "Final: PASS" or
equivalent.

**Plan/Implementation boundary: reinforced by reinvented prose, not by
mechanical drift.** `git log --follow` on `plan.md` for CHG-0015,
CHG-0013, and CHG-0007 each show a single commit — Plan is not, in
practice, silently rewritten after approval to absorb Implementation
discoveries in this repository's real history. This **partially
contradicts** the user's original hypothesis (§14/§28 of the prompt): the
mechanical historical-mutation failure mode is not currently occurring.
What *is* occurring: `CHG-0015/plan.md` and `CHG-0013/plan.md` each
contain a hand-authored "Explicit boundary" section, independently
written, making nearly the same argument ("reaching `tasks_ready` is not
authorization to begin Implementation"). Post-approval corrections are
recorded elsewhere — CHG-0015/verification.md's "What required correction
during Implementation itself" section, CHG-0014's "What required manual
intervention" section — never by editing Plan. The real problem is
boilerplate reinvention, which argues for formalizing this boundary as a
canonical Plan section rather than for building new mutation-detection
tooling (out of the stated non-goals in any case).

**Specification's Requirement/Decision ID scheme is already stable and
should be recognized, not redesigned.** All sampled Specifications use
`### FR-00N` / `### NFR-00N` / `### SEC-00N` / `### INV-00N` / `### CON-00N`
consistently. CHG-0013 and CHG-0015 both add `## Unresolved Decisions`
with `### DEC-00N` sub-entries containing Question/Evidence/Alternatives/
Decision — this is the real, working Unresolved Decision Management
surface, confirmed in production use, not something to reinvent.

**Discovery has no numbered-finding precedent.** No sampled Discovery
uses `D-001`-style numbered findings or an "Executive Summary" heading;
all use subject headings (e.g. `## Repository truth audit`,
`## Compatibility finding`) with the conclusion arriving well into the
document (CHG-0015/discovery.md's main reconstruction starts at line 23
of 285, with no preceding summary). This *does* support adding an
outcome-first Executive Summary/Recommendation — this document does so —
but numbered `D-xxx` Finding IDs have no precedent and are not adopted:
nothing downstream (Schema, traceability.yml, decisions array) references
a Discovery finding by ID the way it references `FR-xxx` or `DEC-xxx`, so
inventing IDs here would add ceremony without a consumer.

**`specification-drift.md` is a real Artifact type the user's prompt did
not enumerate.** Present in CHG-0008, CHG-0011, CHG-0012, CHG-0013; it
records normative corrections discovered during Review/Resolution that
change the Specification's meaning (Protocol §13: Specification Drift).
CHG-0012's version (96 lines) already puts its `## Final decision` last,
after a full Root-Cause/Evidence narrative — the reverse of
outcome-first, but appropriate for its role (this artifact's job is
tracing *how* a drift was discovered and resolved, not announcing a
verdict). This repository's real Artifact taxonomy, used by this
Specification, is therefore: Intent, Discovery, Specification,
Specification Review, Architecture, Test Strategy / Test Design, Plan,
Tasks, Verification, Review, Specification Drift (the real name for what
the user's prompt called "Resolution"), Knowledge Capture, and Inspection
(FAST's condensed Intent-adjacent stage).

**Proportionality already works for FAST.** CHG-0005's `inspection.md` is
four lines (title only) for a trivial fix; CHG-0012's is 86 lines because
that bug genuinely needed the explanation. FAST already does not inherit
manufactured ceremony — the Canonical Artifact Structure must preserve
this, not regress it.

**Traceability duplication risk is real and should be avoided.**
`traceability.yml` already carries Requirement-to-evidence mapping.
CHG-0015's `specification.md` has no `## Traceability` section and relies
solely on `traceability.yml`. Adding a Markdown `## Traceability` section
to Specification (as suggested by the user's prompt §11) would create a
second, driftable copy of the same authority — directly the risk the
user's own prompt §34 warns against. Recommendation: do not add it.

**`docs/adr/` naming must not collide with in-Artifact Decision records.**
`docs/adr/` has 13 numbered ADRs (durable, project-level architectural
knowledge; next free number is 0014). `CHG-0015/architecture.md:37`
already uses `## DEC-002` — not `## ADR-002` — for its embedded,
Change-scoped Decision record, because `DEC-xxx` is the
`decision.yml`-defined identifier space, distinct from `docs/adr/`'s
project-durable `NNNN-slug.md` space. This Change's own Architecture
guidance must keep that separation explicit and must **not** introduce
`ADR-NNN` headings inside per-Change `architecture.md` files (the user's
prompt §12 example layout suggested `### ADR-001` — real precedent
contradicts this and should be followed instead).

## Flow Classification Finding

Every sampled Change that added or modified Contract rules, canonical
Policy, or `protocol/` content — CHG-0008 (Reviewer/Resolver separation),
CHG-0011 (review convergence), CHG-0013 (Unresolved Decision Management),
CHG-0015 (Delegated Execution Authority) — was classified **FULL**, with
no exception. The one STANDARD Change sampled, CHG-0014, added no
Contract rule and no `protocol/` content (Golden Path fixtures and
onboarding validation only). This Change modifies
`protocol/contract/engineering.md` (new Contract rules), adds new
canonical content under `protocol/`, touches `ARCHITECTURE.md`, and
changes Codex Adapter projection behavior — materially equivalent in kind
to CHG-0008/0011/0013/0015, not to CHG-0014. Per `ARCHITECTURE.md:75`
("Flow selection is based on semantic impact... domain rules,
Architecture... public contracts... cross-module behavior... compatibility"),
this repository's own real classification history is direct Evidence
Resolution against the user prompt's initial STANDARD guess. **This
Change is classified FULL**, not STANDARD (see Specification's
Classification section for the formal record).

## Compatibility Finding

If the new Contract guidance stays entirely `SHOULD`-level (no Gate
changes, no existing required field redefined, no previously valid
Change invalidated), this follows exactly the pattern
`protocol/compatibility.md` already documents three times over (CHG-0011,
CHG-0013, CHG-0015: "optional artifacts whose absence preserves existing
meaning") — **no new integer Protocol** is required, and every historical
Change (CHG-0001–CHG-0015) remains valid unchanged. If any part were
instead elevated to `MUST` and Gate-checked (e.g., requiring `## Result`
in Verification), that would retroactively invalidate CHG-0001 through
CHG-0015's own Verification/Review artifacts, which `compatibility.md:42`
explicitly identifies as requiring a new integer Protocol. This dependency
is material and is the substance of Specification's DEC-001 (human
authority, `contract` class, currently **open**).

## Documentation Impact Signal (preliminary)

Likely touched, pending Specification/Plan confirmation: `ARCHITECTURE.md`
§5 (one clarifying sentence, matching CHG-0015's own precedent of
"one added sentence"), `protocol/compatibility.md` (new addendum section,
same pattern as the three prior additive Changes), a new `docs/adr/0014-
canonical-artifact-structure.md` (F-008: material Architecture change
requires ADR — this is analogous in weight to CHG-0013's ADR-0012, not to
an RFC-level foundational change; no RFC is recommended), and
`CHANGELOG.md`. No `ROADMAP.md` item currently names this work — it is
genuinely new, not a formalization of a planned initiative.

## Open Questions Requiring Human Decision

One material, `contract`-class Unresolved Decision is escalated to the
human via `specification.md` (`DEC-001`): the enforcement level of the
Canonical Artifact Structure — entirely `SHOULD`/non-blocking guidance
(this Discovery's recommendation), versus elevating specific elements
(most plausibly, the outcome heading in Verification/Review) to a
`MUST`, Gate-checked obligation with an accompanying new Protocol
integer. This is not resolved here; see Specification and the
Plan-readiness summary presented to the user at the end of this session.
