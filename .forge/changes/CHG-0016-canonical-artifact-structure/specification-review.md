# Adversarial Specification Review — CHG-0016

## Verdict

# REQUEST CHANGES (Iteration 1) → PASS (Iteration 2, after resolution)

Three findings raised against `specification.md` as originally written.
All three are addressed below in the same pass (single-session FULL
Change; see `CHG-0007`/`CHG-0008`/`CHG-0013` for precedent of resolving
Specification Review findings within the authoring session rather than a
separate Resolution artifact at this stage — Specification Drift is
reserved for corrections discovered *after* Specification is complete and
downstream stages are underway, per Protocol §13, which does not apply
yet here).

## Findings

### SR-001 — MINOR — DEC-001's Alternative B reasoning overstates what a new Protocol integer would invalidate

**Problem:** DEC-001 and CON-004 (as originally drafted) state that
choosing Alternative B "requires a new integer Protocol... since it
changes the meaning of Verification/Review as previously-valid instances
understood it" and that CON-004 could be violated ("no completed Change
may become invalid... unless DEC-001 accepts this cost"). This implies
retroactive invalidation of CHG-0001–CHG-0015.

**Evidence:** `protocol/compatibility.md:22`: "Previously valid conforming
Protocol 1 projects and completed Change instances MUST remain valid
merely because Protocol 2 exists." A new integer Protocol binds only
Changes that opt in by declaring it (`protocol: N`); it does not
retroactively re-judge already-completed history. This is exactly how
Protocol 2 itself relates to CHG-0001–CHG-0007 (Protocol 1, still valid).

**Impact:** A human reading DEC-001 to make the Alternative A/B decision
would be evaluating a false cost ("this could invalidate 15 completed
Changes") that does not actually apply. This materially affects Decision
quality.

**Required Resolution:** Correct DEC-001's Evidence/Trade-offs and CON-004
to state precisely: Alternative B requires a new integer Protocol because
it would change the meaning of an existing required stage/field for
Changes that declare that Protocol version going forward (per
`compatibility.md:36-44`'s "change the meaning of an existing required
field... stage... Gate" clause) — not because it invalidates historical
Changes, which no Protocol integer change ever does retroactively in this
repository's own compatibility model.

### SR-002 — MINOR — No invariant prevents `protocol/artifact-structure.md` from duplicating Contract/Flow/Policy normative text

**Problem:** FR-001/FR-002 require the new document to *exist* and cover
certain content, but nothing in the Specification prevents an
implementation from restating Contract or Flow rules inside it — the
exact duplicated-authority risk the user's own prompt (§34) and this
Specification's own FR-007/FR-009 wording ("MUST NOT restate... MUST NOT
redefine or paraphrase") already apply narrowly to §41 and Adapter
projection, but not to the guidance document itself.

**Evidence:** `discovery.md`'s Traceability-duplication and
`docs/adr/`-namespace findings show this repository has already been
burned by near-duplication once (traceability.yml vs a hypothetical
Markdown Traceability section, avoided by not adding one). The same
discipline should apply structurally, not just in the two places
currently called out.

**Required Resolution:** Add `INV-001` to Specification: the guidance
document may reference Contract, Flow, and Policy rules by identifier
(e.g. "see C-014") but MUST NOT restate their normative content in its
own words.

### SR-003 — OBSERVATION — Specification silently omits Security Requirements and assumes no `INCONCLUSIVE` state without stating why

**Problem:** No `## Security Requirements` section exists, and FR-004's
Result enum (`PASS`, `FAIL`, `SKIPPED`, `NOT APPLICABLE`) omits
`INCONCLUSIVE` without explanation, even though the user's original
request explicitly asked for `INCONCLUSIVE` to be considered "only if it
already makes sense in the current model."

**Evidence:** `grep -rni "inconclusive"` across `protocol/` and
`.forge/` returns no normative usage anywhere in the repository — the
state does not exist in the current model, confirming omission is
correct. For security: this Change adds one new canonical Markdown file
under `protocol/` (no new input surface) and one new Adapter resource
inclusion using the pre-existing `_resource()` path-safety/digest
mechanism (Protocol §35, already covering traversal/symlink rejection) —
no new attack surface is introduced.

**Required Resolution:** Not a defect requiring a Specification change to
substance, but the reasoning should be recorded rather than left
implicit, so a future reader does not mistake silence for oversight. Add
a one-line "Security Requirements: none — see Specification Review SR-003"
note and confirm the `INCONCLUSIVE` omission explicitly in FR-004.

## Checked and found sound (no defect)

- FR-002's Artifact type list matches Discovery's confirmed real taxonomy
  (including `Specification Drift`, excluding invented types) — verified
  against Discovery's Comparative Artifact Analysis section directly.
- CON-003's `DEC-NNN` vs `docs/adr/NNNN` namespace separation is verified
  against real precedent (`CHG-0015/architecture.md:37`), not asserted.
- FR-011's proposed ADR number (`0014`) was checked against `docs/adr/`
  at Discovery time (`0013` is the current highest) but is correctly
  treated as provisional — Plan MUST re-verify immediately before
  Implementation rather than treat it as reserved, consistent with
  Protocol §3's Change-identifier assignment rule applied by analogy.
- DEC-001's Decision Class (`contract`) and Authority (`human`) are
  correctly derived from `decision.yml`'s `authority_floor` for the
  `contract` class — no under-authorization.
- NFR-001/NFR-002/NFR-003 are each independently falsifiable at
  Verification time (inspect `inspection.md` sections, grep for
  Codex-specific terms in the canonical file, diff the Adapter
  projection mechanism) — none is vague aspiration.

## Resolution Applied

`specification.md` amended in place (single-session FULL Change,
Specification not yet downstream of Architecture — ordinary Specification
Review resolution, not Specification Drift):

- DEC-001 Evidence/Trade-offs and CON-004 corrected per SR-001.
- `INV-001` added per SR-002.
- FR-004 amended to note the confirmed absence of `INCONCLUSIVE`; a
  one-line Security Requirements note added per SR-003.

## Conclusion

With the three findings resolved, Specification is internally consistent,
each Requirement is independently verifiable, DEC-001 presents an
accurate cost comparison to the human decision-maker, and no duplicated
normative authority is introduced. **PASS.**

## Addendum — DEC-001 resolved

DEC-001 was `open` at the time this Review was conducted above; the human
decision-maker subsequently confirmed Alternative A (2026-08-19), exactly
as this Review's own "Checked and found sound" section verified the
Decision's evidence and authority derivation to be sound. No re-review of
Specification is required: the resolution changed no Requirement,
Constraint, or Acceptance Criterion — it settled the one question
Specification had deliberately left open, in the direction Specification
itself recommended.
