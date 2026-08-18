---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0013
status: complete
---
# Knowledge Capture — CHG-0013

- A taxonomy field ("Decision Class," "Finding severity," etc.) should be
  validated against the question "what distinct operational consequence does
  each value produce" before being accepted from a first draft. Two of six
  candidate Decision Classes proposed by this Change's originating brief
  (`EVIDENCE`, `DISCOVERY`) turned out to answer a different question
  entirely ("how was this resolved" and "which existing Flow stage does this
  collide with," respectively) than the other four ("who owns this subject
  matter"). Catching this during Discovery/Specification, before any schema
  or Contract text existed, avoided baking a false-choice taxonomy into a
  normative Protocol surface.
- `protocol/versions/2/contract/engineering.md` is a *separate, complete*
  file `resolve_effective_contract` substitutes wholesale for
  `protocol/contract/engineering.md` when a project declares `protocol: 2` —
  it is not a delta/overlay. CHG-0011's own `discovery.md` asserted this file
  "does not exist for Protocol 2," which was false at the time CHG-0011
  shipped (or became false without CHG-0011 noticing), and CHG-0011 added
  C-047–C-050 only to the root file as a result. Consequence: this
  repository's own effective Protocol 2 Contract silently lacked four rules
  its own shipped mechanism depends on, until this Change's Discovery caught
  and backfilled it. **General lesson: when a Change's Discovery claims a
  versioned resource "does not exist," that claim is itself something to
  verify with a filesystem check, not carry forward from a prior Change's
  Discovery text — Discovery documents are historical record, not live
  authority, and can themselves go stale exactly like any other artifact.**
- `forge validate` still does not JSON-Schema-validate `manifest.yml`
  directly (confirmed again, same finding CHG-0011's knowledge-capture
  recorded); the separate `tests/contract/test_protocol_contract.py`
  contract test is what actually enforces schema conformance for every
  `.forge/changes/*/manifest.yml`, including this Change's own. A planning
  artifact that references a not-yet-implemented schema field (this Change's
  own first draft of `manifest.yml` briefly included `decisions: []` before
  the schema was extended) is caught by that contract test, not by `forge
  validate` — worth remembering which of the two actually gates a given
  mistake.
- A Lifecycle state that represents "no longer authoritative, but was once
  resolved" (`superseded`) is easy to conflate with "not yet resolved" if a
  Gate-blocking check is written as `status != resolved` instead of `status
  in {the actual open set}`. The former silently makes every superseded
  record block forever, since a superseded record is not expected to itself
  transition to `resolved` — its successor is. This is the same shape of bug
  as CHG-0011's own resettable-counter defect (a derived check written
  against the wrong direction of "what counts"), caught here one stage
  earlier — during Specification Review, before any code existed — by
  applying this Change's own discipline to itself.
- **This Change's own TDD-ordering deviation, disclosed in
  `verification.md`/`tdd-evidence.yml`:** writing production code and its
  test file in the same session without enforcing chronological RED-first
  ordering is easy to do by accident under time/scope pressure, even while
  actively designing a Contract rule set that exists specifically to prevent
  silent process shortcuts elsewhere. Reconstructing RED after the fact
  (temporarily disabling only the wiring call, confirming genuine failures,
  restoring) is better than not doing so, but is not equivalent to true
  RED-first discipline and is recorded as exactly that — a real, disclosed
  deviation for independent Review to weigh, not a self-granted exception.
- **The Protocol 2 §5 review-control metadata exception is exactly three
  paths — `manifest.yml`, `provenance.yml`, `review.md` — and nothing else,
  including files that "feel" like they should qualify.** This Change's own
  Implementation edited `verification.md` after freezing its subject,
  assuming (never actually checking against the Specification text) that a
  verification write-up was as harmless post-freeze as updating the review
  ledger. It is not exempt, and doing so broke the freeze — caught only by
  independent Strict Review Finding CHG-0013-R001, which additionally found
  that the *diagnosis* recorded for the resulting `C-026` failure was
  itself wrong (blamed on unrelated pre-existing untracked files, "verified"
  by a stash experiment whose result was a coincidence, not a proof). Two
  compounding lessons: (1) an exempted-path set defined by exact enumeration
  means exactly that — verify against the literal set, not intuition about
  which files "feel like metadata"; (2) an experiment that produces the
  *expected* result is not automatically evidence of the *hypothesized*
  cause — the independent Reviewer re-ran the identical experiment and got
  a different, correct answer, underscoring why C-026 requires the
  Reviewer to be a genuinely separate Execution/Context rather than the
  same session self-checking its own hypothesis.
- **A guard expressed only as a conjunction of two fields
  (`authority == human AND resolved_via == autonomous_decision`) is
  bypassable by changing either field independently — the same shape of
  bug CHG-0011's own knowledge-capture flagged for "a field whose presence
  authorizes a specific past event" not being bound to that instance.**
  CHG-0013-R002 found the product/contract authority floor was enforced
  only through the resolved_via combination, not as a direct property of
  `class`; simply declaring `authority: agent` on a `product`-class
  Decision bypassed the entire guarantee. General lesson reinforced a
  second time in this Protocol's history: when a floor/invariant is meant
  to bind unconditionally to a category (here, `class`), check it directly
  against that category, not only through a narrower combination that
  happens to imply it in the common case.
- **`dict.get(key)` returning `None` for an absent key is easy to conflate
  with "key present, value not in the flagged set" when writing a
  membership check (`if current in {...}`).** CHG-0013-R003 found exactly
  this: an `invalidates` entry naming a key never tracked in `artifacts` at
  all silently passed the same check meant to catch it staying
  `complete`/`approved`. Distinguishing "absent" from "present-but-wrong-
  value" needs an explicit `key not in mapping` branch, not reliance on the
  absent case happening to fall outside the flagged value set.
- **Disclosing a Contract deviation honestly is necessary but not
  sufficient — the deviation still needs an explicit accept/reject Decision
  from someone other than whoever made it.** This Change's own
  TDD-ordering deviation (C-009) was fully and honestly disclosed in
  `verification.md`/`tdd-evidence.yml`, but independent Strict Review
  (CHG-0013-R004) correctly refused to treat disclosure as equivalent to
  resolution: "this needs an explicit accept/reject engineering decision...
  not self-adjudicated as acceptable by this same session." Directly
  reinforces this Change's own C-053/C-054/C-055: a Recommendation (or in
  this case, a disclosed rationale) is not a Decision merely because it is
  well-reasoned and transparent.
- **Deferred, not fixed in this Change (Strict Review CHG-0013-R005,
  R006):** `supersedes`/`superseded_by` are schema-declared but never
  mechanically cross-checked for existence/consistency; every Decision
  finding is tagged with the single umbrella code `C-051` regardless of
  which of the ~15 distinct checks actually failed. Both accepted as
  documented follow-up work rather than expanded into this Change's own
  Resolution scope — recorded here so a future Change does not have to
  rediscover them.
- F-008 ("Material Protocol Changes require RFC") is satisfied in this
  repository's actual practice by an ADR alone for Contract/Specification-
  level Changes below the scale of introducing a new integer Protocol
  identifier from scratch: neither CHG-0008 (which *did* introduce Protocol
  2) nor CHG-0011 (which added four Contract rules) produced a `docs/rfcs/`
  entry, only `docs/adr/`. This Change follows that established practice
  rather than the more literal reading of F-008's text, and records the
  precedent explicitly here rather than silently picking one interpretation.
