# Specification Review — Interaction Language Resolution

## Verdict

**APPROVED, with 2 MINOR findings resolved in place.** No BLOCKER or
MAJOR findings. Specification proceeds to Architecture.

## Findings

### SR-001 — MINOR — C-072/C-073 have no stated `forge validate` posture

**Finding**: FR-002 drafts C-072 ("deterministic project configuration...
MUST take precedence over any Harness-observed or chat-inferred language
signal") and C-073 (Harness-honesty) as binding MUSTs, but neither the
Functional Requirement nor the rule text says whether `forge validate`
mechanically checks them. Core cannot observe live chat output (INV-001
already states this), so a reader could reasonably expect either "Core
checks what it can" or "Core checks nothing here" — the Specification as
drafted answers neither, leaving the same ambiguity C-067 explicitly
closed for Canonical Artifact Structure ("MUST NOT be validated by `forge
validate` beyond what a future Contract revision explicitly adds").

**Resolution applied**: C-072 and C-073's drafted text (Architecture
stage) will each carry the same explicit disclaimer C-067 uses, and
`specification.md` FR-002 is amended to state it directly rather than
leaving it implicit. See `specification.md` FR-002 (amended) below this
finding.

### SR-002 — MINOR — AC-003's "worded identically" needs a stated basis

**Finding**: AC-003 asserted `protocol/contract/engineering.md` and
`protocol/versions/2/contract/engineering.md` would contain C-070–C-073
"worded identically" without checking whether the two files' existing
C-067–C-069 (the closest precedent) actually match. Asserting an
Acceptance Criterion without checking its own precedent is a process gap,
not a wording gap.

**Checked during this Review**: `diff` of both files' C-067–C-069 sections
confirms byte-identical rule text (only cosmetic paragraph-wrapping
differs, consistent with each file's own pre-existing line-length
convention — root file wraps prose near 72 columns, the versioned copy
does not). AC-003 is achievable and is retained as drafted; no
Specification text needed to change, only this Review's evidence trail.

## Checked and found sound (no defect)

- DEC-001's Alternatives/Trade-offs/Recommendation shape matches
  `protocol/policies/decision.yml`'s `recommendation.required_fields`
  exactly (`recommendation, rationale, alternatives, trade_offs,
  evidence, confidence` — confidence implicit as "recommended," rationale
  and evidence present in the Trade-offs paragraph).
- FR-001's regex (`^(auto|[a-z]{2,3}(-[A-Z]{2})?)$`) was checked against
  a handful of real BCP-47-shaped codes a project might plausibly set
  (`pt-BR`, `en`, `es`, `zh` — all match) and against the malformed
  examples AC-002 names (`Portuguese`, `PT_BR`, `""` — all correctly
  rejected). It does not accept script subtags (e.g. `zh-Hans`) or
  3-letter region codes — a real limitation, but one Alternative A's own
  Trade-offs paragraph already anticipates by choosing a narrow,
  extensible-later pattern over an exhaustive enum; not a defect against
  this Change's own stated scope.
- CON-003 (Decision recorded once, not restated) matches how DEC-001 is
  written here: the Specification states the Decision's outcome and
  pointer to the ADR, and does not re-derive the Trade-offs a second time
  anywhere else in this Change's own Artifacts.
- INV-001 (no false compliance claim) is self-consistent with C-073 —
  neither the Specification nor the planned Contract text anywhere
  states or implies Core verifies actual Harness chat-language output.

## Resolution Applied

`specification.md` FR-002 amended (C-072/C-073 bullets) to add: "Neither
C-072 nor C-073 is validated by `forge validate`; both are honesty and
precedence obligations on the Harness/Adapter, not mechanically checked
Gate conditions, matching C-067's own disclaimer for a different concern."

## Conclusion

Two MINOR findings, both resolved without reopening Discovery or
Architecture. Specification is APPROVED and proceeds to Architecture.
