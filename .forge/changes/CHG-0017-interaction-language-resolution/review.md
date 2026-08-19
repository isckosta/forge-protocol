---
forge:
  artifact: review
  schema: 1
change: CHG-0017
status: passed
---
# Strict Review — CHG-0017

## Verdict

**PASS (Iteration 1, `kind: initial_review`).** No BLOCKER or MAJOR Findings.
2 MINOR, 1 OBSERVATION — all non-blocking per `protocol/policies/review.yml`
(`blocking: [blocker, major]`).

The Implementation subject does what it says: the schema field is genuinely
additive, the Contract rules are byte-identical (modulo pre-existing wrapping
convention) between `protocol/contract/engineering.md` and
`protocol/versions/2/contract/engineering.md`, the Codex projection renders
exactly the two instruction variants FR-004 specifies, `validate_conformance`
is genuinely untouched, and no Artifact this Change produced overclaims what
Core can verify about a Harness's actual chat-language output — the single
invariant (C-073/INV-001) this Change exists to protect. Every mechanical
claim in `verification.md` and `tdd-evidence.yml` was independently
reproduced, not accepted on the Change's own word. The two MINOR Findings are
a citation error in newly-added, permanent Specification text and a
self-disclosed TDD-discipline gap whose overall status label understates it
against this repository's own precedent.

## Summary

| Severity | Count |
| --- | --- |
| BLOCKER | 0 |
| MAJOR | 0 |
| MINOR | 2 |
| OBSERVATION | 1 |

## Review Subject

Frozen Implementation subject `410c4c6e379e4ace86caf706f3d2b74af6473443`
(`provenance.yml`, record `implementation-001`), reviewed against the
Change's own baseline `85c8ce0cf00d085b797933245a9dd371c7792f3a`. The later
commit `0c8d9ac` (implementation-role provenance recording) is Change-local
review-control metadata, exempt from the freeze per this task's own framing,
and was not treated as part of the reviewed diff.

## Review Execution Independence

This Review was executed in an Execution and Execution Context distinct from
the Implementation session that produced `implementation-001`, per Contract
C-026 and Protocol 2 §2. It was performed cold, from repository state alone,
with no access to the Implementation conversation and no prior memory of this
Change beyond what the committed Artifacts and diff state. Every diff was
read directly (`git diff 85c8ce0..410c4c6`, `git show d1d0feb --stat`); no
claim in `verification.md`, `tdd-evidence.yml`, `specification-review.md`, or
any commit message was accepted without independent reproduction. See
`provenance.yml` record `review-001` for this execution's own self-recorded
provenance and honest assurance statement.

## Iteration 1 — PASS

### R001 — MINOR — `protocol/specification.md` §42 cites §2 for a claim §2 does not make

**Problem:** §42's second precedence level reads: "Core cannot resolve this
level itself — per §2 and §33, the chat is the runtime and Core has no
access to live chat state" (`protocol/specification.md:296-300`). §2 of the
same file is titled "Change" and its entire content is: "A Change is the
fundamental Forge unit of engineering work. Every Forge-governed
modification MUST belong to a Change. A Change MUST have a stable
identifier, title, kind, explicit Intent, assigned Flow, lifecycle state,
TDD status, Verification status, Review status, and Documentation Impact
status." (`protocol/specification.md:11-15`). Nothing in §2 discusses chat,
runtime, or live session state. §33 ("Local operation") is one sentence —
"Canonical Forge operation MUST NOT require a Forge-hosted backend"
(`protocol/specification.md:147-149`) — related in spirit (no hosted
backend) but does not itself say "the chat is the runtime" or "Core has no
access to live chat state" either.

**Evidence:**

- `grep -n "chat\|runtime" protocol/specification.md` returns no hit inside
  §2 or §33's actual body text; the only genuinely on-point section is §28
  ("Repository-native state"): "Essential Forge engineering state MUST NOT
  exist only in transient chat history" (`protocol/specification.md:127-129`).
- The exact phrase this Change attributes to §2 — "The chat remains the
  runtime. The repository remains durable memory. Forge remains the
  protocol." — is real, but it lives in `ROADMAP.md:9` (and a close paraphrase
  in `README.md:11`), not in `protocol/specification.md` at all.
- The miscitation is not a one-off slip: it is repeated verbatim across this
  Change's own artifact chain — `intent.md:35` ("§2, §33"), `discovery.md:46-48`
  (quotes the ROADMAP/README sentence and attributes it to "`protocol/
  specification.md` §2"), the Change's own copy of `specification.md:68`, and
  `test-strategy.md:77` ("§2/§29/§33's existing... framing") — and was not
  caught by `specification-review.md`, which approved the Specification with
  only two unrelated MINOR findings (SR-001, SR-002).

**Impact:** A future reader (or a second Harness Adapter implementer)
consulting §42 to verify why Core cannot resolve the Harness-hint precedence
level would open §2, find nothing supporting the claim, and have to guess
the intended citation was §28. The underlying substance is true and
independently supported elsewhere in the Protocol (§28, and this repository's
own README/ROADMAP framing) — this is a citation-accuracy defect in
permanent, normative Specification text, not a behavioral or Gate-affecting
one, which is why it is MINOR and not MAJOR (matching this repository's own
severity calibration for a structurally similar self-citation defect,
`CHG-0016` review R003).

**Required Resolution:** Correct §42's citation from "§2 and §33" to "§28
(and, optionally, §33 for the no-hosted-backend framing)". The equivalent
wording in `intent.md`, `discovery.md`, and `test-strategy.md` is historical
record of this Change and does not need retroactive correction, but should
not be treated as a citable precedent by a future Change.

### R002 — MINOR — `tdd-evidence.yml`'s top-level `status: compliant` understates a self-disclosed RED gap against this repository's own `exception` precedent

**Problem:** `tdd-evidence.yml`'s `notes` honestly discloses that the four
`test_project_configuration.py` interaction-language companion tests
(`test_accepts_absent_interaction_language`,
`test_accepts_explicit_interaction_language`,
`test_accepts_auto_interaction_language`,
`test_rejects_malformed_interaction_language`) were written in the same
commit as the schema edit they test, so "no RED was observed for them,
unlike TDD-001's genuine RED" — a direct Contract C-009/C-010 gap
(RED-before-production-behavior; RED must be observed) for that slice of
this Change's testable, executable behavior (schema validation is
executable behavior with a real failure mode: `InvalidProjectConfigurationError`
either raises or does not). Despite this, the file's own top-level `status:`
field is `compliant` — the same value used for a Change with zero such
gaps.

**Evidence:**

- `git show d1d0feb --stat` and `git log -p -- protocol/schemas/project.schema.json
  tests/unit/test_project_configuration.py` confirm the disclosure is
  factually accurate: the schema edit and all four companion tests land in
  the single commit `d1d0feb`, together with the Contract/Specification/ADR
  text — there is no earlier commit or working-tree state in which the tests
  existed and failed against the pre-edit schema.
- This repository has direct, applicable precedent for exactly this
  shape of gap: `CHG-0007-protocol-v1-contract-freeze/tdd-evidence.yml` sets
  `status: exception` with a top-level `reason:` field stating "test and
  implementation first appear together in commits 60b7326 and e85f3bc. They
  are retained as Verification coverage, not credited as independently
  auditable TDD evidence." `protocol/schemas/tdd-evidence.schema.json`
  requires a `reason` field precisely when `status` is `exception` or
  `not_applicable`, and does not require it for `compliant` — the schema
  itself treats these as materially different postures, and CHG-0007 chose
  `exception` for the same "landed together" fact pattern CHG-0017 now has
  for one slice of its own evidence.
- `manifest.yml`'s compact `tdd: {status: compliant, cycles: 2}` summary
  carries none of this nuance forward — a reader relying on the manifest
  alone (as `forge validate`/`forge doctor` consumers reasonably might) would
  see an unqualified "compliant" with no indication that four of the
  Change's tests were written post-hoc relative to their own subject.

**Impact:** Non-blocking, because: the gap is honestly and specifically
disclosed (this is not a C-016 misrepresentation — the notes explicitly say
"no RED was observed"); the primary executable-behavior TDD cycle (TDD-001,
the Codex projection rendering) is genuinely RED-then-GREEN with reproduced
evidence; and the affected slice is declarative JSON Schema with a narrower
failure-mode space than the projection code. But the top-level `status`
value is the one field most likely to be read in isolation (via `manifest.yml`),
and this repository's own prior practice reserves `compliant` for a Change
with no such gap.

**Required Resolution:** Either (a) change `tdd-evidence.yml`'s top-level
`status` to `exception` with a `reason` field summarizing the schema-layer
gap (mirroring `CHG-0007`'s own resolution for the identical fact pattern),
or (b) if `compliant` is judged the correct label because the primary
executable-behavior cycle (TDD-001) is fully disciplined and the schema
gap is treated as a documented sub-note rather than a status-level
qualifier, state that judgment explicitly in the `notes` themselves rather
than leaving the status/notes tension for a reader to reconcile unaided.

### O1 — OBSERVATION — DEC-002's Alternatives/Trade-offs are presented at Architecture stage, but Specification's own FR-004 had already fixed the outcome

**Observation:** `specification.md` FR-004 states, as a Functional
Requirement: "The Codex Adapter's generated `SKILL.md` contains exactly one
interpolated interaction-language instruction line" — the "interpolated
line, not a new resource file" outcome DEC-002 (`architectural` class,
resolved at Architecture stage via `autonomous_decision`) is framed as
independently deciding between. Both the Specification (containing FR-004)
and the Architecture (containing DEC-002) were authored and committed
together in `df1a87a`, so there is no independently checkable evidence that
DEC-002 was a live choice made after FR-004 was already fixed, as opposed to
a decorative post-hoc Decision record for an outcome the Specification had
already committed to. This does not violate `decision.yml`'s
`downstream_must_not_resolve_upstream_owned_decision` (DEC-002 is genuinely
`architectural`-class and Architecture is its correct owning artifact per
`ownership.owning_artifact_by_class`), and single-session authorship of
Discovery-through-Plan is this repository's normal, disclosed practice
(`plan.md`'s own "Implementation Boundary" section). Recorded as a
process-sequencing observation only, not a Finding requiring Resolution.

## Checked and found sound (no defect)

- **Test suite, reproduced independently.** `python -m pytest -q` →
  **437 passed** in 34.25s, matching `verification.md`'s claimed figure
  exactly (not inherited from it). `forge validate` → "Forge project is
  valid", exit 0. `forge doctor` → 7/7 checks PASS. All three reproduced
  fresh in this Review's own Execution.
- **The single most important invariant (C-073/INV-001) holds under
  adversarial reading.** Checked every Artifact this Change produced —
  `verification.md`'s "Forge Evidence" and "Limitations" sections,
  `knowledge-capture.md`, the ADR, `specification.md` §42, and both Contract
  files — for any statement that Core verified, confirmed, or guaranteed
  what a live Harness chat session actually produced. Found none.
  `verification.md`'s end-to-end CLI claims are correctly scoped to the
  *rendered SKILL.md instruction line* (independently reproduced below), not
  to Harness output; its own "Limitations" section states this explicitly
  ("this Verification... can confirm what language a live Harness session
  actually produced — only that the correct instruction was projected").
  C-073's Contract text itself states the same limit in both Contract files.
  This is the invariant the Change exists to protect, and it is not
  violated anywhere I checked.
- **End-to-end SKILL.md rendering, reproduced independently in two fresh
  scratch repositories** (not merely re-reading the Change's own claim):
  `forge init` → `forge adapter install codex` with no `interaction`
  configuration produced `Interaction language: auto -- use the active
  chat's observed language if there is one, otherwise English
  (C-070-C-073).`; adding `interaction: {language: pt-BR}` to
  `.forge/forge.yml` and running `forge adapter update codex` produced
  `Interaction language: pt-BR (project configuration takes precedence --
  C-072).`; `forge doctor` reported `adapter:codex:generated_drift` PASS in
  the updated case. Both match `verification.md`'s claimed output exactly,
  character for character.
- **Contract dual-file parity.** C-070 through C-073 are byte-identical
  between `protocol/contract/engineering.md` and
  `protocol/versions/2/contract/engineering.md` after whitespace/wrapping
  normalization — verified by direct read of both files, not by eye-skim.
  Line-wrapping differs exactly the way it already differs for the
  pre-existing C-067–C-069 precedent (root wraps near 72 columns; the
  versioned copy does not), consistent with `specification-review.md`
  SR-002's own precedent check.
- **Schema additivity, verified against this repository's own live
  configuration, not merely asserted.** `.forge/forge.yml` (this
  repository's own project configuration) has no `interaction` key and
  validates unchanged (`forge doctor`'s `project_configuration` check
  passes). `interaction` is absent from `project.schema.json`'s top-level
  `required` array, and `language` is absent from `interaction`'s own
  `required` (there is none), so `interaction: {}` and an absent
  `interaction` key are both valid and both resolve to the `auto` default
  via `configuration.get("interaction", {}).get("language", "auto")` at
  both `service.py` construction sites — checked directly, not inferred.
- **Regex pattern, tested directly against every example both
  `specification-review.md` and `specification.md` name.** `^(auto|[a-z]{2,3}
  (-[A-Z]{2})?)$` accepts `auto`, `pt-BR`, `en`, `es`, `zh`; rejects
  `Portuguese`, `PT_BR`, `""`, `zh-Hans`, `pt-br`, `EN` — every claim in
  AC-002 and specification-review.md's "Checked and found sound" section
  holds.
- **`validate_conformance` (`src/forge_cli/adapters/validation.py`) is
  genuinely untouched.** `git diff 85c8ce0..410c4c6 -- src/forge_cli/adapters/validation.py`
  is empty. Confirmed, not merely trusted from `architecture.md`'s claim.
- **Backward compatibility of the dataclass changes, every call site
  checked.** `interaction_language: str = ""` is appended last on both
  `AdapterProjectionContext` and `CodexProjectionInput`, after every
  existing field, so no positional-argument caller breaks. All four
  documented touch points (`driver.py`, `codex/projection.py`,
  `codex/driver.py`, both `service.py` construction sites) were located and
  read directly; both `service.py` sites correctly reference their own
  in-scope configuration variable (`project_configuration` at the
  conformance/doctor site, `configuration` at the `_prepare`/publish site) —
  not a copy-paste mismatch.
- **`_interaction_language_line`'s two branches match FR-004 exactly and do
  not leak into each other.** `test_projection_bundle_renders_explicit_interaction_language_when_provided`
  asserts `"auto" not in` the explicit-language line's own text, ruling out
  a template bug where both branches' wording coexist. Read the rendering
  function directly (`src/forge_cli/adapters/codex/projection.py:157-168`);
  it matches `architecture.md`'s "Content Shape" design exactly, not merely
  approximately.
- **The new `SKILL.md` line does not collide with the wheel-probe's
  hardcoded link-list assertion.** `tests/integration/adapter_cli_wheel_probe.py`'s
  `_effective_reference_links` regex anchors on `## Effective Forge
  references` and only captures markdown bullet-link lines
  (`- [text](link)`); the new `Interaction language: ...` line is plain
  prose placed after that section, not a bullet, and is rendered via a
  separate render path not touched by this Change's diff to
  `_reference_links`. Consistent with `verification.md`'s claim that no
  pre-existing test required modification.
- **`tests/unit/test_project_configuration.py`,
  `test_codex_projection_bundle.py`, and `test_codex_skill_projection.py`'s
  new tests each test what they claim.** Read every new test body directly:
  they assert on the actual rendered string content (`"Interaction
  language: pt-BR" in skill`, `"C-072" in skill`, `"interaction" not in
  result` for the absent case, `InvalidProjectConfigurationError` with the
  correct error code for the malformed case) — none is a tautology or an
  assertion on an unrelated property.
- **DEC-001 classification is correct.** `product` class → non-negotiable
  `human` Authority floor per `decision.yml`'s `authority_floor`, matching
  the recorded `authority: human`; `owning_artifact: specification` matches
  `ownership.owning_artifact_by_class.product`; `materiality: material` is
  justified (`decision.yml`'s `material_when_changes` includes
  `requirement`, and DEC-001 genuinely shapes FR-003's stated precedence
  chain). The Specification's Alternatives/Trade-offs/Recommendation
  satisfy `recommendation.required_fields` (confirmed independently in
  `specification-review.md`'s own "Checked and found sound," and re-checked
  here).
- **DEC-002 classification is defensible.** `architectural` class →
  `agent_with_review` default authority, matching the recorded value;
  `owning_artifact: architecture` matches `ownership.owning_artifact_by_class.architectural`.
  The question (interpolated line vs. new resource file) does not touch any
  `product`- or `contract`-class Materiality trigger (no requirement,
  public contract, or domain-invariant change turns on this choice) — an
  `architectural`-only classification is reasonable on its substance, even
  setting aside the sequencing observation recorded as O1 above.
- **Flow classification (FULL) is correctly justified**, not merely
  asserted: this Change genuinely touches a Protocol schema, both Contract
  files, `protocol/specification.md`, and executable Adapter code with new
  tests — the same combination `discovery.md` cites as already having
  classified `CHG-0013`, `CHG-0015`, and `CHG-0016` as FULL. No FAST/STANDARD
  candidate signal is present.
- **Documentation Impact evaluation matches what actually shipped.**
  `git diff 85c8ce0..410c4c6 -- CHANGELOG.md ROADMAP.md` confirms both were
  updated as `verification.md` AC-010 and `manifest.yml`'s `documentation:`
  block claim — a new "Interaction Language Resolution" `CHANGELOG.md`
  subsection (including an explicit, honest "Known limitation" callout for
  the deferred repository/context heuristic level) and a `ROADMAP.md`
  status line pointing at the ADR. `docs/getting-started.md` genuinely does
  not mention `interaction` or enumerate `.forge/forge.yml` fields
  (`grep` returns no hit), so Discovery's claim that no edit was required
  there holds.
- **No scope creep.** `git diff 85c8ce0..410c4c6 --stat` touches exactly the
  files `plan.md`/`architecture.md` name in advance: the schema, both
  Contract files, the Specification, the ADR, four Adapter source files,
  three test files, `CHANGELOG.md`/`ROADMAP.md`, and this Change's own
  `.forge/changes/CHG-0017-.../` artifacts. No file under `protocol/schemas/`
  other than `project.schema.json` changed (CON-002). No historical
  `CHG-0001`–`CHG-0016` artifact was touched.
- **Baseline figure (430) is independently corroborated from real commit
  history, not merely asserted.** `CHG-0016`'s own `tdd-evidence.yml` TDD-003
  records 429 passed post-Implementation; commit `848adc9` (CHG-0016's R012
  BLOCKER resolution) then adds exactly one new regression test
  (`test_protocol2_accepts_execution_provenance_v2_ledger_for_bound_review_iteration`),
  landing at 430 — exactly the pre-Implementation baseline `test-strategy.md`
  and `tdd-evidence.yml` both cite for CHG-0017.

## Conclusion

Two MINOR Findings and one OBSERVATION, none blocking under
`protocol/policies/review.yml`'s `blocking: [blocker, major]`. The
Implementation subject is verified, not merely claimed: every mechanical
assertion in `verification.md` and `tdd-evidence.yml` was independently
reproduced against real command output, real file content, and real git
history, and the Change's central discipline — that Core projects an
instruction but never claims to verify a Harness's actual chat-language
output — holds under adversarial reading everywhere I checked. This Change
is **PASS** and may proceed toward Completion; the Resolver's judgment on
R001/R002 is optional per C-025 (a Reviewer resolves nothing) but recorded
for that judgment regardless, per this repository's own convention of
reporting non-blocking Findings even when they do not gate Completion.
