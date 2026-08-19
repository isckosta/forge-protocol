---
forge:
  artifact: review
  schema: 1
change: CHG-0016
status: passed
---
# Strict Review — CHG-0016

<!-- Structure per this Change's own deliverable, protocol/artifact-structure.md
     §4 (Review): aggregate ## Verdict first, the existing
     ## Iteration N — <verdict> convention preserved beneath it, Rxxx Findings.
     The `forge:` frontmatter block above is deliberate — see R002. -->

## Verdict

**PASS (final, Iteration 2 — `kind: resolution_verification`).** No blocking
Findings remain outstanding.

- **Iteration 1** (`kind: initial_review`) — **REQUEST CHANGES**: 1 BLOCKER,
  2 MAJOR, 6 MINOR, 3 OBSERVATION.
- **Iteration 2** (`kind: resolution_verification`) — **PASS**: all 11 targeted
  Findings verified resolved against repository state; R009 confirmed as a
  correctly-excluded standing limitation, not a dropped Finding; **no
  Out-of-Scope Mutation**; **0 new material findings**; 2 new non-blocking
  OBSERVATIONs recorded (R013, R014).

`protocol/policies/review.yml` sets `blocking: [blocker, major]`, so the BLOCKER
and both MAJOR Findings raised in Iteration 1 were blocking for this project.
All three are resolved. The two Findings Iteration 2 adds are OBSERVATION
severity and therefore non-blocking.

Everything below this Summary down to the end of `## Conclusion` is Iteration 1's
verbatim historical record, unaltered. Iteration 2 is appended at the end of this
file.

The BLOCKER (R012) is not a defect in this Change's Implementation subject — it
is a latent defect in `src/forge_cli/validation/__init__.py` inherited from
`CHG-0015`, which this Change is simply the first to reach. Recording this Review
Iteration in `manifest.yml` makes `forge validate` fail with a C-026 finding,
because the C-026 check hard-codes `forge/execution-provenance@1` and rejects the
`@2` ledger `CHG-0015` introduced. **`CHG-0016` cannot reach `review_passed` with
a valid project until it is fixed**, so it is a genuine blocker for this Change
regardless of where it originated. It is reported, not resolved, per C-025.

Setting that aside, nothing in this Change is broken, unsafe, or misrepresented as
working when it is not. The engineering is real, the tests are real, and every
mechanical claim `verification.md` makes was independently reproduced. The two
MAJOR Findings are narrower: one declared Requirement (NFR-002) is violated by the
shipped artifact while `traceability.yml` records evidence asserting the opposite,
and the guidance document omits the single most consistent real convention in this
repository's Artifact history — reproducing, in its own new artifacts, the exact
convention-loss failure mode it was written to prevent.

## Summary

Counting semantics, stated explicitly because the Protocol fixes them nowhere
(this is the ambiguity Iteration 1's R006 named): **Raised** is cumulative — every
Finding ever recorded in this Review, in the Iteration that recorded it.
**Outstanding** is the state *after* the final Iteration, and is what
`manifest.yml`'s `review.blockers`/`majors`/`minors`/`observations` carry.

| Severity | Raised (It. 1) | Raised (It. 2) | Raised total | Outstanding | Blocking |
| --- | --- | --- | --- | --- | --- |
| BLOCKER | 1 | 0 | 1 | 0 | yes |
| MAJOR | 2 | 0 | 2 | 0 | yes |
| MINOR | 6 | 0 | 6 | 0 | no |
| OBSERVATION | 3 | 2 | 5 | 3 | no |

The three outstanding OBSERVATIONs are R009 (a standing limitation of what any
Reviewer can verify from squashed Git history — never actionable, never
"resolved"), and R013/R014 (recorded by Iteration 2, non-blocking, left to the
Change's own judgment or to a future Change).

## Review Subject

Frozen Implementation subject `e50d3c594c49a33c0816b5febcaf0c3e78c9cb2d`
(`provenance.yml`, record `implementation-001`). Reviewed cumulatively against
the pre-CHG-0016 baseline `7985080`, plus the post-freeze
review-control-metadata commit `f7829d9`.

## Review Execution Independence

This Review was executed in an Execution and Execution Context distinct from the
Implementation session that produced `implementation-001`, per Contract C-026 and
Protocol 2 §2. It was performed cold, from repository state, without access to
the Implementation conversation. Every diff was read directly (`git show` /
`git diff 7985080..e50d3c5`); no claim in `verification.md`, `tdd-evidence.yml`,
or any commit message was accepted without independent reproduction. See
`provenance.yml` record `review-001` for this execution's own self-recorded
provenance and its honest assurance statement.

## Iteration 1 — REQUEST CHANGES

### R012 — BLOCKER — `forge validate`'s C-026 check rejects `forge/execution-provenance@2`, so no Protocol 2 Change using the `@2` ledger can record a bound Review Iteration and remain valid

**Problem:** `src/forge_cli/validation/__init__.py:320` reads:

```python
if p is None or p.get("schema")!="forge/execution-provenance@1":
    out.append(_finding(r,ppath if ppath.exists()else mpath,
        "Protocol 2 bound Review Iterations require supported repository-native provenance."));continue
```

It accepts only `forge/execution-provenance@1`. `CHG-0015` introduced
`forge/execution-provenance@2`, registered it in `protocol/schemas/catalog.yml`,
and widened its own new delegated-execution check (line 564,
`not in {"forge/execution-provenance@1","forge/execution-provenance@2"}`) — but
did not widen line 320. `CHG-0016`'s ledger declares `@2`, so the moment this
Review's Iteration is bound to provenance, C-026 fires.

**Evidence, reproduced directly:**

- Before this Review wrote anything: `forge validate` → "Forge project is valid",
  exit 0. (`review.iterations: []`, so line 304's guard short-circuits.)
- After recording `review-001` with `subject_provenance: implementation-001`:
  `forge validate` → exit 2, `C-026
  [.forge/changes/CHG-0016-canonical-artifact-structure/provenance.yml] Protocol 2
  bound Review Iterations require supported repository-native provenance.` That
  message string is unique to line 320.
- `.forge/changes/CHG-0016-.../provenance.yml` declares `schema:
  forge/execution-provenance@2`, which is a valid, catalogued schema
  (`protocol/schemas/catalog.yml:11`) and validates cleanly against
  `protocol/schemas/execution-provenance-v2.schema.json`.
- Line 320 originates in `70841bd` ("feat: verifiable review independence",
  CHG-0008), which predates `@2`'s existence. This is an omission in `CHG-0015`'s
  rollout of `@2`, not a defect authored by `CHG-0016`.
- Scope: exactly two Changes use the `@2` ledger — `CHG-0015` and `CHG-0016`.
  `CHG-0015` has not tripped it only because its `review.iterations` is still
  empty; it will hit the identical wall the instant its own Strict Review is
  recorded.

**Impact:** The Strict Review stage is unreachable for any `@2` provenance ledger
while keeping the project valid. `CHG-0016` cannot satisfy `review_passed` and
therefore cannot Complete. Worse, the shape of the failure invites the wrong fix:
dropping `subject_provenance` from the Iteration makes `forge validate` pass again
(line 308's `if not bound and rev.get("status")!="passed": continue`) while
silently discarding exactly the Reviewer-independence binding C-026 exists to
enforce. This Review deliberately did **not** take that path.

**Required Resolution:** Widen line 320 to accept both supported provenance schema
identifiers, matching line 564's existing set, with a regression test that binds a
Review Iteration against a `forge/execution-provenance@2` ledger and asserts the
project validates. Whether that lands as a Resolution within `CHG-0016` or as its
own Change is the Resolver's call — it touches `src/forge_cli/validation/` and a
Contract-enforcement path, which is outside `CHG-0016`'s declared scope
(`specification.md` Out of Scope; `architecture.md` "What This Change Deliberately
Does Not Build"), so a separate Change may well be the correct disposition. Note
also that this bounds `verification.md`'s AC-013 claim: `forge validate` was
indeed unchanged across the *Implementation* snapshot, but the Change's completion
path was never exercised, so the claim does not extend as far as its wording
suggests.

### R001 — MAJOR — NFR-002 (Harness independence) is violated by the shipped canonical file, and `traceability.yml` records evidence asserting the opposite

**Problem:** `protocol/artifact-structure.md` §5 (line 267) reads:

> See `ARCHITECTURE.md` §25 for the Codex Adapter's general projection mechanism

`specification.md` NFR-002 states the file "MUST contain no Codex-specific,
Claude-specific, or other single-provider content." `ARCHITECTURE.md` §25 is
titled "Codex Harness Adapter". The Requirement is violated by the deliverable.

**Evidence:**

- `grep -ni "codex\|claude\|anthropic\|openai\|cursor" protocol/artifact-structure.md`
  returns exactly one hit: line 267. This is precisely the falsification test
  `specification-review.md`'s own "Checked and found sound" section nominated for
  NFR-002 ("grep for Codex-specific terms in the canonical file"). The test was
  specified and then not run.
- `traceability.yml` records
  `NFR-002: {tasks: [T-001], evidence: artifact_structure_md_contains_no_harness_specific_content}`.
  The evidence token asserts a fact that is false of the file as shipped. This is
  the aggravating half of the Finding: an unmet Requirement recorded as met.
- Compounding: `ARCHITECTURE.md` is a repository-root document. `pyproject.toml`
  force-includes only `"protocol" = "forge_cli/resources/protocol"`, so
  `ARCHITECTURE.md` is not packaged in the wheel. The pointer is therefore
  dangling in every consuming project that receives this file through the exact
  projection mechanism FR-009 built for it (`references/artifact-structure.md`).
- `protocol/artifact-structure.md:267` is the only reference to `ARCHITECTURE.md`
  anywhere under `protocol/` (`grep -rn "ARCHITECTURE.md" protocol/`). There is no
  precedent for a canonical Protocol file pointing at an unpackaged repository-root
  document.

**Impact:** A declared Requirement is unsatisfied in the Change's central
deliverable; the traceability record is affirmatively wrong about it; and the one
harness-coupled sentence is the one a second Adapter implementer would read as
normative direction toward Codex.

**Required Resolution:** Either remove the Codex/`ARCHITECTURE.md`-specific
sentence from §5 (the generic first sentence of §5 already carries the whole
point and cites Protocol §34), or, if the pointer is judged worth keeping, amend
NFR-002 and re-record `traceability.yml`'s NFR-002 evidence to state what is
actually true. Do not leave a false evidence token in `traceability.yml` either
way.

### R002 — MAJOR — The guidance omits this repository's most consistent real Artifact convention, and this Change's own new Artifacts drop it

**Problem:** Every Artifact type section in `protocol/artifact-structure.md` §4
enumerates a "structural core", and none of the fourteen mentions the `forge:`
YAML frontmatter block that opens the overwhelming majority of real Artifacts in
this repository. This Change's own `verification.md` and both canonical examples
then omit it — so the Change simultaneously fails to document the convention and
ships three new artifacts that abandon it.

**Evidence:**

- 13 of 15 `verification.md` files and 12 of 14 `review.md` files under
  `.forge/changes/` open with a `forge:` frontmatter block (`artifact:`,
  `schema:`, `change:`, `status:`). The only exceptions are `CHG-0003` and
  `CHG-0005`. Every Change from `CHG-0006` onward carries it without exception —
  until `CHG-0016`.
- This Change's own `plan.md`, `tasks.md`, and `knowledge-capture.md` all carry
  the block. Its `verification.md` does not. Nothing in any artifact explains the
  divergence.
- `examples/canonical-artifacts/verification.md` and
  `examples/canonical-artifacts/review.md` — the two files whose declared purpose
  (`examples/canonical-artifacts/README.md`) is to be the copyable model — both
  omit it.
- `architecture.md`'s own Architectural Goals state the method: "Guidance
  recognizes and formalizes real, already-working conventions ... rather than
  inventing new ones." `discovery.md`'s and ADR-0014's motivating finding is
  literally that "the convention existed and was lost."
- The block is not Schema-validated (`forge validate` passes without it; I
  confirmed no Core code parses it), so this is a convention-fidelity defect, not
  a functional break. That is what keeps it at MAJOR rather than BLOCKER.

**Impact:** FR-002 requires recommended structure "for every human Artifact type
this repository actually produces." The most stable, most universal structural
element of those Artifacts is undocumented, and the guidance's own exemplars now
model its absence. This is the same regression-by-silent-omission that motivated
the entire Change, reintroduced by the Change.

**Required Resolution:** Either (a) document the `forge:` frontmatter block in
`protocol/artifact-structure.md` §4 — once generically, or per type — and restore
it in `CHG-0016/verification.md` and both canonical examples; or (b) if its
omission is a deliberate scope decision (metadata is not "information
architecture"), state that explicitly in §1 or §3 with reasoning, so a future
reader cannot mistake silence for oversight — the same standard
`specification-review.md` SR-003 already applied to the `INCONCLUSIVE` omission.

### R003 — MINOR — `protocol/specification.md` §41 calls a deliberately non-normative document the source of "full normative detail"

**Problem:** §41's closing paragraph reads: "Full normative detail is defined by
`protocol/artifact-structure.md` and `protocol/contract/engineering.md`
C-067–C-069." `protocol/artifact-structure.md` is, by DEC-001's resolution, C-067,
FR-003, and §41's own preceding paragraph, explicitly *not* normative.

**Evidence:** §41 paragraph 1 calls it "canonical, non-binding guidance"; C-067
says conformance "MUST NOT be treated as a Gate condition"; `artifact-structure.md`
§1 says "An Artifact that does not follow this structure is not non-conforming."
The sentence is copied boilerplate from §39 and §40, where the pointed-to sources
(`protocol/policies/decision.yml`, CHG-0015's Architecture record) genuinely are
normative and Core-enforced. The pattern does not transfer.

**Impact:** A canonical Protocol section contradicts itself two paragraphs apart,
in the one document a future Change would consult to decide how binding this
guidance is.

**Required Resolution:** Reword §41's closing sentence so the normative half
(C-067–C-069) and the non-normative half (`artifact-structure.md`) are not
described with the same word.

### R004 — MINOR — `artifact-structure.md` §1 restates C-067 in its own words and narrows it, which INV-001 forbids

**Problem:** INV-001 permits referencing Contract rules by identifier but states
the document "MUST NOT restate their normative content in its own words." §1
paragraph 2 does exactly that, and the restatement is not faithful.

**Evidence:**

- C-067: "Conformance to it MUST NOT be treated as a Gate condition, and MUST NOT
  be validated by `forge validate` **beyond what a future Contract revision
  explicitly adds**."
- `artifact-structure.md` §1: "conformance to this document MUST NOT be treated as
  a Gate condition, and `forge validate` performs no check against it."

The forward-compatibility escape clause is dropped, so the guidance document
states a strictly stronger rule than the Contract rule it claims to be merely
citing. §1 paragraph 3's precedence clause ("the Contract rule is authoritative
and this document is wrong if it says otherwise") mitigates the consequence but
does not cure the INV-001 violation — an invariant added specifically in response
to `specification-review.md` SR-002.

**Impact:** The first concrete instance of duplicated normative authority in the
document is a drifted one, in the document's own statement of the discipline.

**Required Resolution:** Replace §1's paraphrase with a pointer ("see
`protocol/contract/engineering.md` C-067"), or quote C-067 verbatim rather than
restating it in narrower words.

### R005 — MINOR — `traceability.yml` maps AC-004 to two tests that do not verify it

**Problem:** `traceability.yml` records
`AC-004: [test_projection_bundle_includes_artifact_structure_when_provided, test_codex_projection_includes_artifact_structure_reference_when_present]`.
Neither test verifies AC-004.

**Evidence:** AC-004 is "Verification guidance recommends `## Result` as the first
substantive section; Review guidance recommends a `## Verdict` summary at the top,
and the existing `## Iteration N — <verdict>` convention is explicitly preserved."
Both cited tests pass synthetic content
(`artifact_structure_content="# Canonical Artifact Structure\nProgressive
Disclosure.\n"`) and assert only that a `references/artifact-structure.md`
resource appears in the bundle and that its content is not inlined into
`SKILL.md`. Neither test mentions `## Result`, `## Verdict`, or `## Iteration`.
The same two tests are correctly mapped to AC-009, where they do belong. Every
other genuinely non-mechanical Acceptance Criterion (AC-001, AC-002, AC-003,
AC-005–AC-008, AC-010–AC-013) is correctly mapped to `[]`, which is why this one
stands out as a slip rather than a policy.

**Impact:** AC-004 is in fact satisfied by reading the shipped document, so the
Acceptance Criterion holds — but the recorded mechanical evidence for it is an
overclaim in the artifact whose entire purpose is to be trustworthy evidence.

**Required Resolution:** Set `AC-004: []` and record its verification as
non-mechanical (document inspection), consistent with the eleven other
non-mechanical Acceptance Criteria.

### R006 — MINOR — The canonical `examples/canonical-artifacts/review.md` is internally inconsistent

**Problem:** The example's `## Summary` table reports `MINOR 0` and
`OBSERVATION 1`. Its body enumerates exactly one Finding — `R001`, explicitly
labelled MINOR — and contains no numbered OBSERVATION at all.

**Evidence:** `R001 — MINOR — Boundary case (exactly 3 characters) untested`
appears under `## Iteration 1`. The claimed OBSERVATION exists only as unnumbered
prose in Iteration 2 ("One OBSERVATION recorded (naming style, non-blocking)").
The table never states whether its counts are cumulative across iterations or
outstanding at the final iteration; both readings are needed to make it
self-consistent, and they conflict.

**Impact:** `manifest.yml`'s `review.minors` / `review.observations` are
Schema-required integers (`protocol/schemas/change-v2.schema.json`) whose counting
semantics the Protocol does not define anywhere. The one canonical example that
could have settled that ambiguity instead demonstrates two incompatible readings
simultaneously, in a file whose stated purpose is to be copied.

**Required Resolution:** Make the example's Summary table internally consistent
with its own enumerated Findings, and state which counting semantics it
demonstrates.

### R007 — MINOR — Both canonical examples and this Change's own `verification.md` nest an H1 inside an H2

**Problem:** `## Result` is followed immediately by `# PASS`, and `## Verdict` by
`# PASS (final, Iteration 2)` — a level-1 heading nested inside a level-2 section.

**Evidence:** `examples/canonical-artifacts/verification.md`,
`examples/canonical-artifacts/review.md`, and
`.forge/changes/CHG-0016-canonical-artifact-structure/verification.md` all do
this. Every real Artifact in this repository uses exactly one H1, as the title.
`protocol/artifact-structure.md` §4 specifies that `## Result` must be the first
substantive section and enumerates its permitted values, but says nothing about
how the value should be rendered — so the examples are the only guidance a reader
has, and they model an inverted outline.

**Impact:** Breaks document outline semantics: table-of-contents generation,
Markdown outline views, and assistive-technology heading navigation all read a
second H1 as a new top-level document. In a Change whose entire subject is the
information architecture of Markdown documents, and whose §2.4 principle is
Scanability, this is a self-inflicted counterexample.

**Required Resolution:** Render the value without a heading (bold text, a blockquote,
or plain paragraph), or as a subordinate heading level. Optionally state the
recommendation in §4 so the next author does not have to infer it from the
examples.

### R008 — MINOR — DEC-002's `resolved_via: evidence` is not fully supported by its own record

**Problem:** `manifest.yml` records `DEC-002: {resolved_via: evidence}`.
`architecture.md`'s DEC-002 record does not sustain that classification for the
whole Decision.

**Evidence:**

- DEC-002's Question poses three sub-questions (where it lives, how a Harness
  Adapter obtains it, whether a new Protocol integer is required).
- Its Evidence section is headed "Evidence resolution (no fresh analysis needed
  for **two of the three** sub-questions)" and then states: "**Remaining actual
  decision:** file identity and shape. Decided: `protocol/artifact-structure.md`,
  Markdown prose (not YAML ...)." That is a design choice reached by reasoning,
  not by citing an existing source of normative authority.
- Its Confidence paragraph then says "**Both** sub-answers were reached by direct
  citation" — miscounting its own three-part Question and quietly dropping the
  residual decision from the accounting.
- `protocol/policies/decision.yml` sets
  `evidence_resolution: {requires_citable_source: true, agent_inference_is_not_evidence: true}`
  and offers `autonomous_decision` in `resolution_paths` for exactly this case.
  `CHG-0015` recorded its structurally comparable architectural DEC-002 as
  `resolved_via: autonomous_decision`.
- Separately, `traceability.yml` labels DEC-002's evidence
  `architecture_stage_evidence_resolution_specification_md_dec_002`, although
  DEC-002 lives in `architecture.md`, not `specification.md`.

**Impact:** `evidence` and `autonomous_decision` are not interchangeable under
`decision.yml` — the former asserts no agent judgment was exercised. Here some
was, and the record says so in prose while the manifest says otherwise. Authority
class, floor, and owning Artifact are all correct; only the resolution path is
mislabelled.

**Required Resolution:** Either re-record DEC-002 as `resolved_via:
autonomous_decision`, or narrow DEC-002's Question to the two genuinely
evidence-resolved sub-questions and record the file-identity choice separately.
Correct the `traceability.yml` evidence token's artifact name either way.

### R009 — OBSERVATION — RED-before-GREEN chronology cannot be verified from git history, and I say so rather than asserting either way

All four CHG-0016 commits were authored within 3m58s (`bf69393` 11:30:23,
`70478ae` 11:30:39, `e50d3c5` 11:30:57, `f7829d9` 11:34:21), and the new tests and
the production implementation land together in the single commit `70478ae`. There
is no commit in which the tests exist and the implementation does not, so git
provides no independent evidence of ordering. `protocol/policies/review.yml`
requires me to inspect `test_precedes_production_behavior`, `red_was_observed`,
and `red_failed_for_expected_reason`; I can only do so circumstantially.

What I *can* confirm is that the claimed RED reasons are exactly what the
pre-change code shape would produce, which is a meaningful consistency check:

- `generate_codex_skill_bundle` had no `artifact_structure_content` parameter at
  `7985080`, so `TypeError: unexpected keyword argument` is precisely right for
  `test_projection_bundle_includes_artifact_structure_when_provided`.
- `AdapterProjectionContext` had no such field, so the same `TypeError` is right
  for `test_codex_projection_includes_artifact_structure_reference_when_present`.
- `forge_cli.protocol_resolution` exposed neither
  `resolve_effective_artifact_structure` nor
  `CanonicalArtifactStructureUnavailableError`, so `AttributeError: module ... has
  no attribute` is right for all three
  `tests/unit/test_protocol_resolution.py` additions.

`tdd-evidence.yml` also honestly declares `red.observed: false` for TDD-002 and
TDD-003 with stated reasons, rather than fabricating RED runs for a
backward-compatibility assertion and a baseline guard — which is the behavior
`post_hoc_tests_not_misrepresented` is looking for. I found no indication of
misrepresentation. This commit pattern matches `CHG-0015`'s and is not a new
deficiency introduced here; it is recorded as a standing limitation of what a
Reviewer can verify from squashed history.

### R010 — OBSERVATION — the `has_artifact_structure` branch is unreachable from production code

`AdapterService` calls `resolve_effective_artifact_structure(...)` unconditionally
at both `AdapterProjectionContext` construction sites (`service.py:445`,
`service.py:609`), and that resolver raises
`CanonicalArtifactStructureUnavailableError` rather than returning `""` when the
file is missing. So in every shipped path the content is non-empty and the
omit-branch in `projection.py` is exercised only by direct library callers and by
`test_projection_bundle_omits_artifact_structure_resource_when_not_provided`.

I am not asking for the branch to be removed: `generate_codex_skill_bundle` is a
public, pre-existing API, the default-valued parameter is what makes the additive
backward-compatibility claim true, and the conditional itself is two lines of
ordinary `*(... if cond else ())` splatting — proportionate, not over-engineered.
The observation is narrower: the "backward compatibility" TDD-002 protects is
compatibility for a caller shape no production code uses, and neither
`tdd-evidence.yml` nor `verification.md` says so.

### R011 — OBSERVATION — `tasks.md` marks T-008 `[x]` for a task it describes as "Not performed", and T-009 references a non-existent TDD identifier

`tasks.md` line for T-008 reads `- [x] T-008 **Not performed.** ... Retained here,
struck through in spirit`. The prose is honest, but the checkbox — the scanable
signal, `artifact-structure.md` §2.4 — says done, and "struck through in spirit"
concedes that the notation does not carry the intent (Markdown has `~~...~~`).
Separately, T-009 reads "TDD-001/TDD-002 (and TDD-008 if applicable) remain
GREEN"; this Change's `test-strategy.md` defines only TDD-001 through TDD-003.
`TDD-008` appears to be unedited residue from `CHG-0015`'s task text. Neither
affects correctness; both are legibility defects in a Change about legibility.

## Checked and found sound (no defect)

Recorded explicitly so a Resolver knows what was actually exercised, not merely
skimmed.

- **Test suite, reproduced independently.** `python -m pytest -q` → **429 passed**
  in 32.81s. The claimed figure is correct, not inherited from `verification.md`.
  `forge validate` → "Forge project is valid", exit 0. `forge doctor` → 7/7 PASS.
- **Contract dual-file parity.** C-067, C-068, and C-069 are byte-identical
  between `protocol/contract/engineering.md` and
  `protocol/versions/2/contract/engineering.md` after whitespace normalization,
  verified by programmatic per-rule diff, not by eye. Line-wrapping differs, which
  matches the pre-existing style difference between the two files.
- **AC-012 (Schema stability).** `git diff 7985080..e50d3c5 --stat` touches no file
  under `protocol/schemas/`. Confirmed.
- **AC-010 / CON-004 (no historical Change reformatted).** The full cumulative diff
  touches exactly one directory under `.forge/changes/` — CHG-0016's own. No
  `CHG-0001`–`CHG-0015` artifact was modified. `forge validate` reports the project
  valid with all sixteen Change directories present.
- **Backward compatibility of the dataclass changes — every call site checked.**
  `artifact_structure_content: str = ""` is appended **last** in both
  `AdapterProjectionContext` and `CodexProjectionInput`, after all existing fields,
  so no positional-argument caller breaks. Call sites audited: `service.py` (both
  sites, updated), `codex/driver.py` (updated), `projection.py`'s internal
  `generate_codex_projection_bundle` (updated), and every pre-existing test
  constructing either type (unchanged, still passing). No silent behavior change
  for a caller that does not opt in — the omit-branch is what guarantees it.
- **The wheel-probe change genuinely strengthens the test; it does not paper over
  a break.** `_effective_reference_links` asserts `links == expected` — exact list
  equality — so adding `"references/artifact-structure.md"` makes the probe
  *require* the new link at an exact position rather than tolerate it. The added
  `artifact_structure.read_bytes() == (expected_protocol / "artifact-structure.md").read_bytes()`
  assertion is new coverage that did not exist before, verifying the projected file
  byte-for-byte against the packaged canonical file inside a genuinely built,
  offline-installed wheel. Its use of `expected_protocol` (canonical root) rather
  than `versioned_protocol` is correct and deliberate, matching the resolver's
  documented version-fallback. I ran
  `tests/integration/test_adapter_distribution.py` in isolation: 2 passed, and it
  does really build and install the wheel and execute the probe.
- **Every factual claim I spot-checked in `protocol/artifact-structure.md` and
  ADR-0014 is true.** `CHG-0001/verification.md` does open with `## Result` after
  its title; `CHG-0015/verification.md` genuinely has no Result heading (it opens
  with `## Test evidence`); `CHG-0005/inspection.md` is exactly 4 lines;
  `CHG-0008/review.md` has exactly 6 iterations, 5 REQUEST CHANGES then PASS;
  `CHG-0015/test-strategy.md` has exactly 16 `## TDD-` cases;
  `CHG-0012/specification-drift.md` does place `## Final decision` last;
  `CHG-0012/inspection.md` is 86 lines; ADR-0014's "roughly 2.7x" Artifact-volume
  growth is 2404/896 = 2.68x; `docs/adr/0014` is genuinely the next unused number;
  and Test Design is a real type here (`CHG-0005`, `CHG-0014`), not an invented one.
  The document's central discipline — cite real precedent rather than invent
  convention — holds up under checking.
- **DEC-001 handling is correct.** Class `contract` → `authority_floor: human` per
  `decision.yml`; `authority: human`; `owning_artifact: specification` matches
  `ownership.owning_artifact_by_class`; `discovered_in: specification`;
  `resolved_via: human_decision`. The Specification records Recommendation,
  Rationale, Alternatives, Trade-offs, Evidence, and Confidence before the human
  decision, satisfying `recommendation.required_fields`, and states explicitly that
  Confidence is not authorization. The Decision was resolved before
  `specification_review_passed` was asserted, which `knowledge-capture.md`
  independently corroborates via the C-051 validation failure it hit and fixed.
- **INV-001 spot-check across per-type sections.** §4's Specification, Plan, Review,
  Verification, Architecture, and Inspection entries cite conventions, Contract
  identifiers, and real precedent without restating Contract, Flow, or Policy
  normative text. The only restatement I found anywhere in the file is §1's C-067
  paraphrase (R004). The Specification's own INV-001 claim is therefore
  substantially — not entirely — true.
- **Not adding §41 to `protocol/versions/2/specification.md` is correct, not an
  omission.** That file is a Protocol-2 *delta* (13 sections, §1–§13), not a full
  copy of the root Specification's 41 sections — unlike the per-version Contract,
  which is a full copy and correctly received C-067–C-069 in both places. §41's
  "applies independently of declared Protocol version" is the right treatment.
- **The new resolver is a faithful reuse of the existing pattern (NFR-003).**
  `resolve_effective_artifact_structure` mirrors `resolve_effective_flow`'s
  versioned-then-canonical fallback, raises a dedicated
  `ProtocolResolutionError` subclass consistent with
  `CanonicalContractUnavailableError`, and correctly omits the project-extension
  layer that only the Contract has. Its docstring states why. No second
  content-delivery mechanism was introduced.
- **No spurious upgrade breakage for already-installed Adapters.** Adding a
  projected resource does not trigger a false `generated_drift` failure: that check
  compares recorded digests against on-disk files, both unchanged by a CLI upgrade.
  `forge adapter update` handles the new resource, exactly as it did for every prior
  Change that altered projected Contract content. I checked this rather than
  assuming it.
- **`verification.md`'s "What Required Correction During Implementation Itself"
  section is a genuine, unprompted application of this Change's own C-069.** The
  Plan's step 4 undercount (one file named, four changed) is disclosed in
  Verification and Knowledge Capture rather than absorbed by editing the approved
  Plan. Verified by diffing `plan.md` across all four commits: it was not touched
  after approval. This is the Change dogfooding its own rule against itself, and it
  is the strongest single piece of evidence that the guidance is usable.
- **`plan.md` carries the canonical `## Implementation Boundary` section, last
  (FR-005/AC-005), and `specification-review.md` carries a `## Verdict` at the top
  with `SR-xxx` Findings.** The dogfooding is real where it is claimed.

## Note on the guidance's own usability

Since this Change's deliverable recommends a structure for Review, I wrote this
Review to that structure — aggregate `## Verdict` first, `## Iteration N —
<verdict>` preserved beneath it, `Rxxx` Findings — as a live test of whether the
guidance is actually usable rather than merely plausible. It is. The aggregate
Verdict genuinely helps at this size and would help considerably more at
`CHG-0008`'s six iterations, and the `Rxxx`/`SR-xxx` split resolved without
ambiguity. Two frictions surfaced, both already recorded as Findings: §4 gives no
guidance on rendering the Verdict value, so I had to decide against the examples'
own `# PASS` (R007), and §4 says nothing about the frontmatter block every real
Review carries, so I had to consult precedent rather than the guidance (R002).
Both are exactly the kind of gap only use, not review-by-reading, exposes.

## Conclusion

One BLOCKER (R012) and two MAJOR Findings (R001, R002) are blocking under
`protocol/policies/review.yml`'s `blocking: [blocker, major]`. Six MINOR and three
OBSERVATION Findings are non-blocking and are recorded for the Resolver's
judgment.

Within `CHG-0016`'s own Implementation subject the implementation is correct, the
tests are honest, the compatibility claims hold, and the mechanical evidence
reproduced exactly. The BLOCKER is a latent `CHG-0015` defect that this Change is
merely the first to reach — but it blocks `CHG-0016`'s Completion all the same,
and the Resolver should decide deliberately whether it is fixed here or as its own
Change rather than being absorbed silently.

**`forge validate` is expected to report exit 2 with a single C-026 finding while
this Review stands.** That is R012 manifesting, not a defect introduced by this
Review's own edits, and not a reason to unbind the Review Iteration from its
provenance. `forge doctor` remains 7/7 PASS and `pytest -q` remains 429 passed.

Per Contract C-025 and Protocol §25, this Reviewer does not resolve its own
Findings. Nothing in the Implementation subject was modified by this Review;
only `review.md`, `manifest.yml`, and `provenance.yml` — the Change-local
review-control metadata the freeze discipline permits — were written.
Re-review after resolution is required
(`review.yml: re_review.required_after_blocking_resolution: true`) and MUST run in
an Execution and Execution Context distinct from the Resolution that addresses
these Findings.

**REQUEST CHANGES.**

## Iteration 2 — PASS (`kind: resolution_verification`)

### Iteration 2 scope and authority

This Iteration is a **Resolution Verification**, not a second Initial Review. Per
`protocol/contract/engineering.md` C-047 and
`protocol/versions/2/specification.md` §10, its authority is bounded to three
things and was exercised as exactly those three:

1. the Findings `resolution-001` targets;
2. defects within `resolution-001`'s Resolution Delta;
3. Out-of-Scope Mutation.

It is deliberately **not** a re-audit of `implementation-001`. Nothing in
Iteration 1's "Checked and found sound" section was re-litigated, and no opinion
is offered here on `protocol/artifact-structure.md`'s per-type design in general —
Iteration 1 evaluated that content and did not flag it, and re-opening it is
precisely what C-047 forbids.

### Iteration 2 execution independence

Executed cold, from committed repository state, in an Execution and Execution
Context distinct from all three prior records: `implementation-001` and
`resolution-001` (both
`implementation-exec-chg0016-20260819-01` /
`implementation-context-chg0016-20260819-01`) and `review-001`
(`review-exec-chg0016-20260819-add11f8d` /
`review-context-chg0016-20260819-d20e2d8c`). This session has no memory of any of
them and read `review.md` Iteration 1, `provenance.yml`, `manifest.yml`, and the
Protocol/Contract text directly. No claim in `knowledge-capture.md`,
`tdd-evidence.yml`, or any commit message was accepted without independent
reproduction against the actual files, tests, and code. See `provenance.yml`
record `review-002`.

Subject: `resolution-001`, frozen at
`848adc992d63bc510f3fae2917d47557095c9049` (revision `chg-0016-resolution-001`).
`HEAD` at the time of this Review is `67766d3`, whose only difference from the
subject is `provenance.yml` (48 added lines — `resolution-001`'s own record).
That is Change-local review-control metadata, which the §5 effective-workspace
freeze permits; `git status --porcelain` is otherwise clean.

### Resolution Delta, computed independently — no Out-of-Scope Mutation

Computed per §11 as the committed diff between the immutable revision of the
Iteration immediately preceding this one (`review-001`'s subject,
`e50d3c594c49a33c0816b5febcaf0c3e78c9cb2d`) and this Iteration's own subject
(`848adc99…`) — both already-frozen historical commits, not the current
workspace — minus this Change's exact `manifest.yml`, `provenance.yml`, and
`review.md` paths:

```
git diff --name-only e50d3c5..848adc9 -- . \
  ':(exclude).forge/changes/CHG-0016-canonical-artifact-structure/manifest.yml' \
  ':(exclude).forge/changes/CHG-0016-canonical-artifact-structure/provenance.yml' \
  ':(exclude).forge/changes/CHG-0016-canonical-artifact-structure/review.md'
```

Twelve paths result. `resolution-001` declares twelve `scope` entries. The two
sets are **exactly equal** — set difference is empty in both directions
(no uncovered path, and no declared-but-untouched path either, so the Scope is not
padded to swallow a wider delta than was taken):

| # | Resolution Delta path | Covered by declared `scope` |
| --- | --- | --- |
| 1 | `.forge/changes/CHG-0016-canonical-artifact-structure/architecture.md` | yes |
| 2 | `.forge/changes/CHG-0016-canonical-artifact-structure/knowledge-capture.md` | yes |
| 3 | `.forge/changes/CHG-0016-canonical-artifact-structure/tasks.md` | yes |
| 4 | `.forge/changes/CHG-0016-canonical-artifact-structure/tdd-evidence.yml` | yes |
| 5 | `.forge/changes/CHG-0016-canonical-artifact-structure/traceability.yml` | yes |
| 6 | `.forge/changes/CHG-0016-canonical-artifact-structure/verification.md` | yes |
| 7 | `examples/canonical-artifacts/review.md` | yes |
| 8 | `examples/canonical-artifacts/verification.md` | yes |
| 9 | `protocol/artifact-structure.md` | yes |
| 10 | `protocol/specification.md` | yes |
| 11 | `src/forge_cli/validation/__init__.py` | yes |
| 12 | `tests/cli/test_validate.py` | yes |

**Out-of-Scope Mutation: none.** This is the mechanical §11 result, not a
judgment. Consequently `full_review_required` is `false`, C-048 does not engage,
and this Iteration is eligible to be `status: passed`.

**Core independently agrees, and I proved the check is live rather than
vacuously silent.** After recording this Iteration, `forge validate` runs
`_validate_resolution_verification`, which recomputes the Delta from
`provenance.yml` and compares it against the declared `scope` itself — it returns
"Forge project is valid", exit 0. To confirm that result is a real agreement and
not a check that silently skipped, I removed a single entry
(`protocol/artifact-structure.md`) from `resolution-001`'s declared `scope` and
re-ran: `forge validate` exits 2 with "Resolution Delta contains Out-of-Scope
Mutation not covered by declared scope (protocol/artifact-structure.md); a
resolution_verification Iteration that detects this MUST be status: failed with
full_review_required: true, never passed." I then restored the file. My
hand-computed Delta and Core's are the same set.

The narrower, genuinely discretionary check — whether anything nominally inside a
declared-scope path exceeds "fixing the eleven targeted Findings" — was also run,
against `git diff --stat` and then the diffs themselves. It comes back clean. The
largest production change is **one line** (`validation/__init__.py`, an `!=`
equality widened to a two-element set membership). The largest content change is
`protocol/artifact-structure.md` at +50/−~15, every hunk of which maps to a named
Finding (R001 §5, R002 §4, R004 §1, R007 §4 ×2). `knowledge-capture.md` grows by
46 lines, all of it three new lessons corresponding to R001, R002, and R008 — the
established shape of that artifact, not an unrelated rewrite. No file in the Delta
contains an edit I could not attribute to a targeted Finding.

### The eleven targeted Findings, each verified against repository state

`resolution-001.targets` reads `[R001, R002, R003, R004, R005, R006, R007, R008,
R010, R011, R012]` — confirmed against the actual file, eleven ids, and it
matches the eleven Findings Iteration 1 raised other than R009.

**R012 (BLOCKER) — resolved.** `src/forge_cli/validation/__init__.py:320` now
reads `p.get("schema")not in{"forge/execution-provenance@1","forge/execution-provenance@2"}`,
byte-identical in its accepted set to the pre-existing line 564. Verified three
ways, none of them by trusting the record:

- `grep -n 'execution-provenance@' src/forge_cli/validation/__init__.py` returns
  exactly two lines (320 and 564) with the identical two-element set. The fix is
  a widening to the already-blessed set, not a loosening: any schema outside those
  two still takes the same rejection path, and `p is None` is still checked first.
- `forge validate` against this repository — which now carries a *real* bound
  Review Iteration (`review-001`, `subject_provenance: implementation-001`)
  against a `forge/execution-provenance@2` ledger — returns **"Forge project is
  valid", exit 0**. Iteration 1 recorded exit 2 with a C-026 finding at this exact
  state. That is R012's manifestation disappearing under the fix, observed
  directly.
- **The regression test is genuinely RED against the pre-fix code, and I proved
  it rather than reading the claim.** I reverted line 320 to its pre-fix
  single-schema equality form in a scratch copy of the working tree and ran
  `test_protocol2_accepts_execution_provenance_v2_ledger_for_bound_review_iteration`:
  it fails with `assert 2 == 0` on `result.exit_code` — the same exit code and the
  same cause `tdd-evidence.yml` TDD-004 records. I then restored the file
  (`git diff` clean). This is the one RED claim in this Change that *is*
  independently verifiable after the fact, and it verifies.

The test also tests what it claims. `_base_protocol2_manifest()` supplies a
`review.iterations[0]` with both `subject_provenance` and `reviewer_provenance`
and `status: passed`, so line 304's guard does not short-circuit and line 320 is
actually reached; the only thing the test varies from the adjacent passing
fixture is `provenance["schema"] = "forge/execution-provenance@2"`. It is a
one-variable test on the exact predicate that was wrong.

**R001 (MAJOR) — resolved.** `grep -ni "codex\|claude\|anthropic\|openai\|cursor"
protocol/artifact-structure.md` — the falsification test
`specification-review.md` itself nominated for NFR-002 — now returns **zero
hits**. `grep -rn "ARCHITECTURE.md" protocol/` returns **nothing**, so the
dangling unpackaged-document pointer is gone too. §5 keeps its generic first
sentence and its Protocol §34 citation. `traceability.yml`'s false evidence token
is replaced with
`artifact_structure_md_section_5_no_named_harness_after_r001_resolution`, which is
a true statement of the file as shipped. Both halves of the Finding — the
Requirement violation and the false evidence record — are addressed.

**R002 (MAJOR) — resolved.** `protocol/artifact-structure.md` §4 now opens with a
paragraph documenting the `forge:` frontmatter block generically ("Every entry's
structural core additionally includes, as its very first element…"), with the
per-type non-repetition rationale stated. Its factual claim is true: I ran an
independent census of all 29 `verification.md`/`review.md` files under
`.forge/changes/` — 25 carry the block as line 1, and the only four that do not
are `CHG-0003` and `CHG-0005`, exactly as the paragraph says. The block is
restored in `CHG-0016/verification.md` (line 1) and in both
`examples/canonical-artifacts/` files. See R013 below for a residual, non-blocking
placement wrinkle in the two examples.

**R003 (MINOR) — resolved.** `protocol/specification.md` §41 now reads "The full
non-binding guidance is defined by `protocol/artifact-structure.md`; its normative
binding strength is defined by `protocol/contract/engineering.md` C-067–C-069."
The normative and non-normative halves are no longer described with the same word,
which is what the Required Resolution asked for. §41 no longer contradicts itself.

**R004 (MINOR) — resolved.** `artifact-structure.md` §1's paraphrase is gone,
replaced with a pointer: "see `protocol/contract/engineering.md` C-067 for the
exact, authoritative statement of what that means; it is not restated here
(INV-001, below)." The narrowing — the dropped
"beyond what a future Contract revision explicitly adds" escape clause — cannot
recur, because no restatement remains to drift. INV-001 is satisfied at the one
place Iteration 1 found it violated.

**R005 (MINOR) — resolved.** `traceability.yml` now records `AC-004: []`,
consistent with the eleven other non-mechanical Acceptance Criteria. The two tests
remain correctly mapped to AC-009, where Iteration 1 confirmed they belong.

**R006 (MINOR) — resolved.** `examples/canonical-artifacts/review.md`'s Summary
table now reads `MINOR 1 / OBSERVATION 1`, and its body enumerates exactly one
MINOR (`R001`, Iteration 1) and one numbered OBSERVATION (`R002 — OBSERVATION —
Local variable naming…`, Iteration 2), which the Resolution promoted from
unnumbered prose. Table and body now agree. The Resolution additionally states the
counting semantics it demonstrates ("cumulative across every iteration … stated
explicitly because the Protocol does not fix this counting semantics anywhere"),
which is the second half of the Required Resolution and the more valuable half.

**R007 (MINOR) — resolved.** `# PASS` and `# PASS (final, Iteration 2)` are gone
from all three files, replaced with `**PASS.**` / `**PASS (final, Iteration 2).**`.
`grep -n '^# '` over all three now returns exactly one H1 each — the title.
Iteration 1's optional half was also taken: §4's Verification and Review entries
each now carry an explicit rendering recommendation, so the next author does not
have to infer it from the examples. **Regression check performed:** nothing
referenced the removed headings. `TDD-008` residue aside (see R011), no
cross-reference anywhere in the repository points at `# PASS` as a heading, and
the full suite passes, so no test or projection asserted on the old shape.

**R008 (MINOR) — resolved.** `manifest.yml` now records
`DEC-002: resolved_via: autonomous_decision`. `architecture.md`'s record gains an
explicit **Resolution path** paragraph that accounts for all three sub-questions
(two by citation, the third — file identity and shape — as design reasoning) and
states the governing principle ("classified by its weakest link, not its
strongest"). The miscounting "Both sub-answers were reached by direct citation"
sentence is gone; **Confidence: high** now stands alone, which is honest.
`traceability.yml`'s mislabelled evidence token is corrected from
`architecture_stage_evidence_resolution_specification_md_dec_002` to
`architecture_md_dec_002_autonomous_decision`, naming the artifact the Decision
actually lives in. This also brings the Change into line with `CHG-0015`'s
structurally comparable Decision, which Iteration 1 cited as precedent.

**R010 (OBSERVATION) — resolved.** `tdd-evidence.yml` gains a note stating plainly
that both `AdapterProjectionContext` construction sites call
`resolve_effective_artifact_structure` unconditionally and that it raises rather
than returning `""`, so the omit-branch TDD-002 protects "is exercised only by
direct library callers and by the test itself, not by any shipped production path
today." That is exactly the honesty gap Iteration 1 described, closed without
removing the branch — which is what Iteration 1 explicitly did not ask for.

**R011 (OBSERVATION) — resolved.** `tasks.md` T-008 is now `- [ ] ~~T-008~~
**Not performed, by design.**` — unchecked, struck through in actual Markdown
rather than "in spirit", with the reason retained rather than the task silently
dropped. T-009's `TDD-008` residue is corrected to `TDD-001/TDD-002/TDD-003`,
which are the three cycles `test-strategy.md` actually defines. `grep -rn
"TDD-008"` over the Change directory now hits only `review.md` and
`manifest.yml`'s `evidence_gap` — both of which are historical records *of* the
Finding and must keep the string.

### Disposition of R009 (not targeted) — confirmed correctly excluded, not dropped

R009 is deliberately absent from `resolution-001.targets`, and that remains the
accurate characterization. Iteration 1's own text asks for nothing: it states "I
found no indication of misrepresentation", records the limitation as "a standing
limitation of what a Reviewer can verify from squashed history", and notes the
same commit pattern predates this Change. There is no Required Resolution
paragraph in R009 — the only Finding in Iteration 1 without one. `resolution-001`
declares the exclusion explicitly in its `revision.description` and its `source.statement`
rather than leaving it to be inferred. That is the correct disposition of a
non-actionable OBSERVATION under C-050: recorded, not discarded, not amplified.

Worth noting as a genuine improvement rather than merely an absence of harm: the
Resolution's own new cycle, TDD-004, is the first cycle in this Change whose RED
*is* independently verifiable after the fact, and I verified it (above). R009's
limitation does not extend to the Resolution's own work.

### New Findings introduced by the Resolution

Two, both **OBSERVATION** severity, both strictly inside the Resolution Delta,
both introduced by the Resolution's own edits. Neither is blocking under
`protocol/policies/review.yml` (`blocking: [blocker, major]`); neither is counted
in `new_material_findings` — see "Convergence accounting" below for why.

#### R013 — OBSERVATION — the frontmatter block the Resolution added to both canonical examples is not on line 1, so it is not parseable frontmatter and does not match the placement §4 now prescribes

**Problem:** `examples/canonical-artifacts/verification.md` and
`examples/canonical-artifacts/review.md` open with
`<!-- Illustrative example, not a real Change. See README.md. -->`, a blank line,
and *then* the `---`/`forge:` block on line 3. A YAML frontmatter block is
frontmatter only when it is the first line of the file; preceded by anything, it
is a literal `---` thematic break followed by plain text in every standard
Markdown frontmatter parser.

**Evidence:** `git show 848adc9 -- examples/canonical-artifacts/` shows the
Resolution inserting the block *after* the pre-existing disclaimer comment in both
files. The same commit's §4 paragraph prescribes the block "as its very first
element … before the `# <Type> — <title>` heading". Independent census: all 25
real `verification.md`/`review.md` files in this repository that carry the block
put it on line 1, without exception — the exemplars are the only two artifacts
anywhere that place it elsewhere.

**Impact:** Functionally nil — Iteration 1 already established that no Core code
parses the block, and `forge validate`/`pytest` are unaffected. The impact is the
one this Change exists to care about: the two files whose declared purpose
(`examples/canonical-artifacts/README.md`) is to be the copyable model demonstrate
a placement the guidance's own new paragraph rules out, in the very convention
R002 was raised to restore. There is a real counter-argument, which is why this is
an OBSERVATION and not a MINOR: the disclaimer comment is a "this is not a real
Artifact" marker, and hoisting genuine-looking frontmatter to line 1 would make
the file read as a real Change's artifact. If that is the reasoning, it is
defensible — it is simply nowhere stated.

**Suggested disposition (not required):** either move the block to line 1 and the
disclaimer comment beneath it, or add one clause to the README or to the files'
own annotations saying the disclaimer deliberately precedes the frontmatter and is
not part of what a copier copies. Not resolved here, per C-025.

#### R014 — OBSERVATION — §4's new "omitting it is a defect, not a style choice" sits in tension with §1's "not non-conforming"

**Problem:** The R002 paragraph the Resolution added to §4 ends: "omitting it is a
defect, not a style choice, unless a Change states explicitly why a given Artifact
does not carry it." §1 of the same document says "An Artifact that does not follow
this structure is not non-conforming", and C-067 makes conformance to the whole
document non-Gate-checked.

**Evidence:** the two sentences are 100 lines apart in
`protocol/artifact-structure.md`. "Is a defect" plus an exception clause phrased
as a condition (`unless a Change states explicitly…`) reads as a requirement with
a documented-waiver escape hatch, which is a stronger register than any other
recommendation in §4 — every one of which is phrased as "recommended", "reads
well here", or "closely follows precedent".

**Impact:** Narrow, and arguably none: "defect" is a quality judgment and
"non-conforming" is a Gate judgment, and those are genuinely different things, so
the two sentences can be read compatibly. But this is structurally the *same*
class of defect as R003 — a document being imprecise about how binding it is, two
sections apart — in a document whose §1 exists to settle exactly that question. It
is recorded because the Resolution introduced the sentence, not because it changes
anything mechanical.

**Suggested disposition (not required):** soften to the register §4 uses
elsewhere ("its omission is a gap worth stating a reason for"), or say explicitly
that "defect" here means a quality gap and not non-conformance in C-067's sense.
Not resolved here, per C-025.

### Independent mechanical verification

Every figure below was produced by this execution, not read from
`verification.md`, `knowledge-capture.md`, or any commit message.

- `python -m pytest -q` → **430 passed** in 33.61s. Matches the Resolution's
  claimed 430 (up from Iteration 1's independently-reproduced 429; the delta is
  exactly TDD-004's one new test).
- `forge validate` → **"Forge project is valid", exit 0**, both before this
  Iteration's writes and after them (with `review-002`, the
  `resolution_verification` entry, and the advanced `state.current` all recorded).
  This is the material change from Iteration 1, which recorded exit 2 with a C-026
  finding at this same bound-Iteration state.
- `forge doctor` → **7/7 PASS**, exit 0.
- `git status --porcelain` → clean at `67766d3` before this Review's own writes.
- Pre-fix RED reproduction for TDD-004 → confirmed failing, `assert 2 == 0`,
  file restored afterwards (see R012 above).

### Scope discipline (C-047 / C-050)

No unrelated latent Finding was discovered in this Iteration. Had one been, C-050
requires it be recorded and *not* treated as license for an unrestricted re-audit;
R013 and R014 are not unrelated latent Findings — both are inside the Resolution
Delta and are the Resolution's own responsibility, which is squarely within
C-047's second authorized category.

For the record of what was deliberately **not** done: the per-Artifact-type design
of `protocol/artifact-structure.md`, the Adapter projection mechanism, the
dataclass compatibility argument, the wheel probe, the Contract dual-file parity,
and every factual claim Iteration 1 spot-checked were all left alone. Iteration 1
examined them and found them sound; re-examining them would be the unrestricted
re-audit C-047 forbids, and it would also be a poor use of an independent
Reviewer, since the second look adds nothing the first did not already establish.

One item that *is* in scope and worth stating rather than leaving silent:
`verification.md` still records "429 passed" while the suite is now 430. That is
correct as written — `verification.md` is the verification record of the frozen
`implementation-001` subject, and 429 was the true figure at that subject. The
Resolution's own post-fix figure is recorded in `tdd-evidence.yml` TDD-004 and in
`848adc9`'s commit message. No Finding.

### Convergence accounting

`new_material_findings: 0`, and `full_review_required: false`.

The reasoning, stated because §12's definition is precise and this is the field
that drives C-049's automatic-termination machinery:

- There is no Out-of-Scope Mutation to count (mechanically established above).
- R013 and R014 *are* Findings the Resolution is responsible for, but the field
  counts **material** new findings, and both are OBSERVATION severity —
  non-blocking under this project's `blocking: [blocker, major]`. §12's own
  exclusions point the same way: the counter exists to stop a Resolution cycle
  that keeps breaking things, not to register cosmetic residue in guidance prose.
- Core enforces the same reading: `_validate_resolution_verification` rejects a
  `passed` Iteration that declares `new_material_findings > 0`. A verdict of PASS
  on non-blocking Findings and a non-zero counter are mutually exclusive by
  construction, and the blocking policy is what decides which of the two applies.
- No original Finding recurs, so nothing is countable on that basis either — and
  §12 forbids counting recurrences regardless.

Derived `consecutive_unconverged_verifications` is therefore **0**; the trailing
run of `resolution_verification` + `failed` + `nmf > 0` entries is empty. The
Convergence Limit (2) is not approached, `review.convergence.state` remains
nominal, and §13 does not engage. `manifest.yml` declares no `convergence` block,
which agrees with the Core-derived value of 0 — Core raises a finding only on
disagreement with a *declared* value.

### Verdict

**PASS.**

All eleven targeted Findings are resolved in repository state, verified file by
file rather than accepted from the record. R009's exclusion is correct. The
Resolution Delta contains no Out-of-Scope Mutation, and the declared Resolution
Scope is exact in both directions — no uncovered path, and no padding. The one
production-code change is a single line that widens a check to a set that already
existed ten lines-of-logic away, guarded by a regression test I confirmed is red
against the pre-fix code and green against the fixed one. `forge validate` exits 0
for the first time since Iteration 1 was recorded, which is R012's resolution
observable from outside the code.

Two non-blocking OBSERVATIONs (R013, R014) are recorded for the Change's judgment.
Per C-025 this Reviewer resolved neither, and nothing outside `review.md`,
`manifest.yml`, and `provenance.yml` was written by this Iteration.
