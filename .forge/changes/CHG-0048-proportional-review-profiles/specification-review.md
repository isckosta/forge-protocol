---
forge:
  artifact: specification_review
  schema: 1
change: CHG-0048
status: complete
---

# Adversarial Specification Review — CHG-0048

**Verdict: REQUEST CHANGES → PASS (seven findings, all resolved in the same authoring session).**

Per `protocol/flows/full.yml`'s `specification_review` Gate (`mode: adversarial`), this Review ran as an independent agent execution (fresh isolated Git worktree, no shared context with the Specification's authoring session) reviewing the Specification against `docs/rfcs/0007-proportional-review-profiles.md`, `discovery.md`, and the actual current repository state (Contract text, Flow files, Schemas, validation code, Adapter projections) — verifying every factual claim independently rather than trusting Discovery's summary. Protocol 2's independent-Execution/Context requirement (C-026) binds Strict Review only, not Specification Review; running this one independently anyway was extra rigor proportional to this Change's normative weight (Contract/Schema/CLI/Adapter changes), not a Gate requirement.

## Findings

### SR-001 (Foundational) — RFC-0007 never rebutted RFC-0005's calibration-pilot rationale
**Found:** RFC-0007's supersession of RFC-0005 addressed RFC-0005's *mechanism* (a descriptive calibration overlay vs. a real posture change) but never engaged RFC-0005's *epistemic* objection — that immediate binding thresholds were rejected specifically because no calibration data/pilot existed yet.
**Resolution:** Added a dedicated "Waiting for RFC-0005's calibration pilot before proposing anything binding" entry to RFC-0007's Alternatives rejected, explaining why the pilot's specific risk (an under-calibrated *numeric* threshold) does not transfer to three fixed, non-numeric, Protocol-authored profiles with every mechanically-checked guarantee held constant. Applied to `docs/rfcs/0007-proportional-review-profiles.md`.

### SR-002 (Implementability gap) — FR-010's "project's effective configuration" was undefined and missed the schema that actually implements it
**Found:** `.forge/forge.yml`'s existing `review:` block (validated by `project.schema.json`, `additionalProperties: false`, `strict: {const: true}`) is the real mechanism FR-010 needs, but FR-008 never listed `project.schema.json` among the schemas gaining `profile` — AC-010 as originally written could not be satisfied.
**Resolution:** FR-008 revised to include `project.schema.json`; FR-010 revised to name it concretely; AC-008 gained an explicit acceptance check that `.forge/forge.yml`'s existing block still validates. Applied to `specification.md` and `docs/rfcs/0007-proportional-review-profiles.md` (Decision point 8).

### SR-003 (Conceptual/Contract) — FR-008's "purely additive" claim conflated two different schema operations for `flow.schema.json`
**Found:** Replacing `flow.schema.json`'s hardcoded `const: true` on `strict`/`adversarial` with an enum removes an existing, universal, machine-checkable guarantee — a narrowing, not an addition — and this narrowing was never separately surfaced to the human maintainer alongside the Contract-prose question RFC-0007's acceptance actually resolved.
**Resolution:** FR-008 and RFC-0007 (Decision point 8) revised to state explicitly that this schema change is the direct, expected encoding of the already-resolved Contract decision (not an independent additive claim), and that no historical *instance* exists to invalidate (only three live canonical Flow files, edited in place by this Change). Recorded, not silently smoothed over.

### SR-004 (Ambiguity risk, acknowledged design tradeoff) — `focused`/`standard` give no mechanical way to distinguish "scoped-but-thorough" from "under-searched"
**Found:** A Reviewer instructed under `focused`/`standard` who finds nothing is, after the fact, indistinguishable from one who simply didn't look hard enough — an intentional design choice (RFC-0007 item 10, keeping Core validation-blind to profile) that the Specification never stated as an accepted residual risk.
**Resolution:** Added CON-003, explicitly naming this residual risk and the accepted mitigation (non-negotiable Flow floor, identical rejection authority on any Finding actually observed) rather than a mechanical exhaustiveness audit. Applied to `specification.md`.

### SR-005 (Completeness) — FR-007's "invariants preserved" list omitted C-059
**Found:** A full grep of the Contract for Review-scoped rules turned up C-059 ("Reviewer discovering a missing material decision requests changes") in both Protocol 1 and Protocol 2 Contract files, absent from FR-007's enumerated preserved set.
**Resolution:** C-059 added to FR-007, CON-002, and RFC-0007's Decision point 6, with a one-line note that it is profile-orthogonal by construction (triggered by discovery, not a search mandate).

### SR-006 (Requirement gap) — mid-flight Changes and C-005 escalation were unaddressed
**Found:** No Requirement stated that Review Profile derives from a Change's *effective* Flow at the time a Review Iteration actually runs, as opposed to Flow at Specification/Plan time — leaving a Change already Plan-approved when this ships, or a Change escalating Flow mid-Change under C-005, with no defined Review Profile behavior.
**Resolution:** Added FR-012 (Review Profile derived from `manifest.flow.current` at Review-Iteration time; escalation propagates the profile prospectively; already-recorded Iterations are not retroactively invalidated) and RFC-0007 Decision point 13.

### SR-007 (Minor, scope-honesty) — `merge_readiness/evaluator.py`'s `MR-004` label goes stale
**Found:** Discovery had already inspected `evaluator.py:90`'s hardcoded `"STRICT REVIEW NOT READY"` label but the Specification never mentioned it, leaving a literal inaccuracy once "Strict Review" no longer describes every Change's Review.
**Resolution:** Added FR-013 (purely cosmetic label rename to a profile-neutral string, no change to `MR-004`'s trigger condition or blocking semantics) and RFC-0007 Decision point 14.

## Checked and found sound

- C-022, C-023, C-031 exact current text (Protocol 1 and Protocol 2 files) — verified byte-identical to Discovery's quotes.
- The three Flow `review:` blocks — verified byte-identical (`required: true, strict: true, adversarial: true`) at the claimed lines.
- `full.yml`'s `specification_review` stage `mode: adversarial` precedent, and `strict_review`'s lack of a `mode:` field in all three Flows — confirmed, and a genuine precedent for the `profile` mechanism.
- `flow.schema.json`'s `if`/`then` keying on `flow.id` for `stages` arrays — confirmed real precedent for Flow-conditional schema shape.
- `change-v2.schema.json`'s `review` object has no `profile` key today — genuinely additive there.
- `policy-review-v2.schema.json`'s `additionalProperties: true` at the review-object level — `profile` is already schema-legal there without editing the file, confirmed.
- `policy-review.schema.json` (Protocol 1) — confirmed untouched by this Change's scope, consistent with the Out-of-Scope claim.
- `src/forge_cli/validation/__init__.py`'s Flow-blindness on review/convergence logic — confirmed independently (only 2 "flow" occurrences in the file, neither in the relevant functions).
- Adapter conformance code (`adapters/service.py`, `claude_code/driver.py`) computing `strict_review_required` from stage presence, not from the `strict`/`adversarial` values — confirmed this is not put at risk by the schema/value change, ruling out a hidden regression.
- The `_gate_instructions()` review-instruction line is a clean, single, localized edit point in both Adapters and the generated `SKILL.md` — confirmed FR-009 is scoped correctly and narrowly.
- RFC-0007 acceptance provenance (`rfc-acceptance-001`) — commit hash matches the real acceptance commit; `observed_by: operator` satisfies the C-054/C-055 evidentiary bar.
- No contradiction between FR-001–FR-013 and the Out of Scope section.

## Specification Review Gate

All seven findings are resolved and applied directly to `specification.md` and `docs/rfcs/0007-proportional-review-profiles.md` in the same authoring session (Protocol 2 does not require independent Execution/Context for this Gate — see above). No BLOCKER-equivalent finding remains open. Ready for Architecture.
