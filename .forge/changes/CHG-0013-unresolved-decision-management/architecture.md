---
forge:
  artifact: architecture
  schema: 1
change: CHG-0013
status: complete
---

# Architecture — Unresolved Decision Management

## Reuse over parallel subsystem

Per C-032/C-033, existing patterns are reused wherever they already do the
job:

- **Prose ledger + compact manifest index**, exactly like `review.md` (prose
  Findings) + `manifest.yml: review.{status,iteration,blockers,...}` (compact
  state). `decisions.md` holds the full Decision record; `manifest.yml:
  decisions[]` holds only what Core needs to check mechanically.
- **Append-only-once-committed identity**, exactly like Review Iteration and
  provenance-record identity under C-026. A `DEC-NNN` section is never
  rewritten to mean something different once committed; correction is
  superseding, not editing.
- **Policy as agent-consumed YAML, not a mechanically-interpreted rule
  engine**, exactly like `architecture.yml`, `documentation.yml`,
  `review.yml`, `security.yml`, `testing.yml`. `decision.yml` follows the
  same convention: default values an agent reads and a project may extend.
- **The mechanical/declarative split already established by CHG-0011**:
  Python enforces the narrow, deterministic slice (manifest shape,
  Open-blocking-state Gate conflicts, `resolved_via` consistency);
  everything requiring semantic judgment (was this Materiality call
  correct? was the Recommendation actually good engineering?) remains a
  Strict Review responsibility, never a `forge validate` claim.
- **`convergence_decision` (CHG-0011) is not touched.** It already
  implements one narrow, valid instance of "Forge stops and requires an
  explicit human choice from a fixed option set with a reason." This Change
  generalizes the *pattern*; it does not migrate that existing, already-
  shipped, already-reviewed mechanism onto the new one. A future compatible
  Change MAY do so once both have field experience; doing it now would be
  scope creep unrelated to the Materiality/Authority/Recommendation problem
  this Change actually solves, and would touch CHG-0011's reviewed surface
  for no functional gain.

## `decisions.md` shape (new file, per Change)

Plain Markdown, one `##` section per Decision, IDs stable and sequential
(`DEC-001`, `DEC-002`, ...), append-only in meaning once a section's outcome
is committed. Worked example (the shape every Decision record follows,
whether Evidence-resolved, autonomously decided, or human-decided):

```markdown
## DEC-001 — Idempotency key reuse with a different payload

- Class: product
- Materiality: material — changes observable API behavior and failure
  semantics (FR-003: public/API Contract, failure/error semantics)
- Owning artifact: specification
- Discovered in: specification
- Decision Authority: human
- Status: awaiting_decision

### Question
What should happen when the same idempotency key is reused with a request
payload that differs from the original?

### Evidence investigated
- `protocol/contract/engineering.md`: no existing rule addresses idempotency
  key semantics.
- `specification.md` (this Change's own domain Specification, not this
  repository's): no prior Requirement addresses this case.
- No precedent Decision record exists (`decisions.md` has none yet).
- Conclusion: not Evidence-resolvable; proceeding to Alternatives.

### Alternatives

**A — Reject conflicting reuse (409 Conflict)**
Advantages: no silent data loss; caller learns immediately; matches common
idempotency-key precedent (e.g. Stripe).
Disadvantages: caller must handle a new error class; requires payload
hashing/comparison to detect conflict.

**B — Return the original operation's result, ignore the new payload**
Advantages: simplest caller experience; no new error class.
Disadvantages: silently discards caller intent when the payload differs;
masks caller-side bugs.

### Recommendation
Option A. Rationale: silent payload discard (B) violates the general
principle that a Material behavior difference must be observable, not
absorbed; conflict detection cost is bounded (one comparison) and the
caller-facing failure mode is explicit and recoverable.
Confidence: high.

### Decision
_pending — awaiting human decision_
```

Once decided, the `### Decision` section is appended (never replacing the
Recommendation section above it), stating the chosen Alternative,
`resolved_via`, who decided, and why if it diverges from the Recommendation.
`Status:` in the frontmatter-like block updates to `resolved`.

## `manifest.yml` shape (additive, both `forge/change@1` and `forge/change@2`)

```yaml
decisions:
  - id: DEC-001
    class: product              # product | contract | architectural | technical
    materiality: material       # material | non_material
    status: awaiting_decision   # open | analyzing | awaiting_decision | resolved | superseded
    authority: human            # human | agent | agent_with_review
    owning_artifact: specification
    discovered_in: specification
    resolved_via: null          # evidence | autonomous_decision | human_decision | null
    supersedes: null
    superseded_by: null
    invalidates: []             # artifact keys this Decision's resolution invalidates, once resolved
```

Only `material` Decisions need appear here at all (FR-003/C-058); recording
a `non_material` one is permitted but never required and never blocks
anything — Core treats its presence as inert.

## Validator changes (`src/forge_cli/validation/__init__.py`)

New function `_validate_unresolved_decisions(root, mpath, manifest, gate_dependency_sets)`,
called from `validate_project` for **every** protocol id (unlike
`_validate_protocol2_review_provenance`, which is Protocol-2-only, this
concept does not depend on Execution/Context independence — it applies
identically to `forge/change@1` and `forge/change@2`). It:

1. Loads `manifest.get("decisions")`; returns immediately (no findings) if
   absent or empty — the compatibility invariant (§Compatibility below).
2. Validates each entry's shape: `id` unique and matching `^DEC-[0-9]{3,}$`;
   `class` in the four-value enum; `materiality` in the two-value enum;
   `status` in the five-value enum; `authority` in the three-value enum;
   `owning_artifact`/`discovered_in` non-empty strings; `resolved_via` in
   `{evidence, autonomous_decision, human_decision}` or `null`.
3. Checks FR-009/C-054/C-055 mechanically: a non-null `resolved_via` MUST
   correspond to a `status: resolved` entry; `authority: human` combined
   with `resolved_via: autonomous_decision` is a finding (C-055); a `status:
   resolved` entry with `resolved_via: null` is a finding (a Decision cannot
   be resolved by nothing). Additionally — added during Resolution of
   independent Strict Review Finding CHG-0013-R002, which found the check
   above insufficient on its own — the `product`/`contract` authority floor
   (C-055/FR-017) is checked as a property of `class` itself, independent of
   `resolved_via`: `class` in `{product, contract}` combined with any
   `authority` other than `human` is a finding, so the floor cannot be
   bypassed simply by declaring a non-`human` `authority` directly.
4. Checks INV-003 mechanically only to the extent it is representable
   without semantic Flow-order knowledge beyond what already exists: cross-
   references `owning_artifact` against the fixed Class→Owning-Artifact
   table from `specification.md` (this is a static lookup, not inference —
   fully deterministic).
5. Computes Gate-dependency conflicts (INV-001/FR-013): for each of the
   Gate-dependency sets already implied by canonical Flow stage order
   (`specification_review` depends on `specification`; `before_implementation`
   depends on `architecture`; `before_completion` depends on all), a
   `decisions[]` entry whose `owning_artifact` falls in that set and whose
   `status` is an Open-blocking state (`open`, `analyzing`,
   `awaiting_decision`) is a finding when the corresponding
   `artifacts.<stage>` entry (or `review.status`/`state.current`) claims
   that Gate already passed.
6. Checks FR-014/C-057 mechanically: any `invalidates` entry naming an
   `artifacts.*` key that is currently `complete`/`approved` while the
   Decision that declared it is itself still Open-blocking, or while the
   named artifact was never subsequently transitioned through
   `invalidated`→(revised), is a finding — including, after Resolution of
   Finding CHG-0013-R003, an `invalidates` key that is not tracked in
   `artifacts` at all (a missing key is not the same as a present-and-
   complete one, and the original check silently passed the former).

This mirrors exactly the shape and rigor of
`_validate_resolution_verification` (same file): small, pure, operating
only on already-loaded YAML mappings, no network, no Harness SDK, fully
covered by `tests/unit/test_validation.py`-style fixtures.

## Contract and Specification placement

- `protocol/contract/engineering.md` — append C-051 through C-059 after the
  existing C-050 (shared canonical Contract; applies whether a project
  declares `protocol: 1` or `protocol: 2`, since `_versioned_protocol_root`
  only substitutes a versioned directory when one exists and is not
  Unresolved-Decision-specific).
- `protocol/versions/2/contract/engineering.md` — backfill C-047–C-050
  (CHG-0011, previously missing from this file, see `discovery.md`) and add
  C-051–C-059, so this repository's own effective Protocol 2 Contract
  (`.forge/forge.yml` declares `protocol: 2`) actually contains the rules
  this Change and CHG-0011 both depend on. This is the only place this
  Change touches CHG-0011's prior work, and only to complete a placement
  CHG-0011 itself already committed to but missed.
- `protocol/specification.md` — new §39 "Unresolved Decision Management",
  summarizing Terminology, the four-Class taxonomy, Materiality, Decision
  Authority defaults, the three resolution paths, Gate blocking, and
  backward invalidation at Specification-document density (the full
  normative detail stays in this Change's own `specification.md`, which
  becomes historical Change record once merged — `protocol/specification.md`
  states the durable Core rule, matching how existing shared-Specification
  sections summarize rather than restate every Change's own reasoning).
- `protocol/policies/decision.yml` (new file, schema `forge/policy/decision@1`)
  — the default Authority table (FR-017) plus the Materiality criteria list
  (FR-003) in policy-YAML form, mirroring how `review.yml` restates C-026
  family invariants in YAML for agent/human consumption alongside the
  Markdown Contract.
- `protocol/schemas/policy-decision.schema.json` (new) + `catalog.yml` entry
  (`forge/policy/decision@1`).
- `protocol/schemas/change.schema.json` and `change-v2.schema.json` — add
  the optional `decisions` array (shape above) to both, `additionalProperties:
  false` preserved on the array's item schema.
- `protocol/compatibility.md` — a short new subsection analogous to the
  existing CHG-0011 subsection, stating the same "optional fields, no
  invalidated instance" argument for this Change plus the
  `protocol/versions/2/contract/engineering.md` backfill note.
- `ARCHITECTURE.md` (repository-level, not `protocol/`) — §17 (Gates) gets
  one added sentence naming Decision Gate blocking as a cross-cutting Gate
  condition, not a new Flow stage. No other section of that file changes;
  the pre-existing staleness of §26 ("Protocol `1` is the stable integer
  compatibility contract," never updated for Protocol 2) is a real
  Documentation Impact gap but belongs to whichever Change owns keeping
  `ARCHITECTURE.md` current for Protocol 2 generally — out of scope here,
  noted for the Documentation Impact evaluation to consider, not silently
  fixed as a side effect of this Change (same discipline as CHG-0011's own
  discovery.md, which noted analogous drift without expanding scope).

## Compatibility mechanics

`_validate_unresolved_decisions` returns immediately with no findings when
`manifest.get("decisions")` is absent, `None`, or `[]` — structurally
identical to how `_validate_resolution_verification` returns immediately
when no Iteration declares `kind`. Every existing manifest in this
repository (`CHG-0001`–`CHG-0012`) has no `decisions` key and is therefore
provably unaffected; `tests/contract/test_protocol_contract.py`-style
fixtures against those exact historical manifests are the regression
baseline (Test Strategy TDD-001).

## What this Change deliberately does not build

- No CLI subcommand for creating, listing, or resolving Decisions (C-031
  CLI boundary is unaffected; enforcement remains inside `forge validate`
  and the agent-followed process, exactly like every other Gate).
- No automatic, diff-based computation of invalidation blast radius —
  `invalidates` is always an explicit, reviewable declaration (FR-014
  rationale).
- No semantic materiality classifier, ML or otherwise — Materiality is an
  agent judgment call recorded with a rationale, checked adversarially by
  Strict Review, not computed.
- No retrofit of `review.convergence_decision` onto this mechanism (see
  "Reuse over parallel subsystem" above).
- No project-configurable relaxation of `product`/`contract` Authority below
  `human` (C-055 makes this a canonical floor, not a project choice).
- No new integer Protocol identifier, no new `forge/change@N` schema suffix.
