---
forge:
  artifact: specification_review
  schema: 1
change: CHG-0021
status: passed
---

# Specification Review — Adapter Reference Schema Projection

## Verdict

**PASS, with 4 MINOR and 1 OBSERVATION finding to carry forward.** No
BLOCKER or MAJOR findings. Specification proceeds to Architecture; the
findings below should be corrected in `specification.md` (or carried
into Architecture, where DEC-001 is already anticipated for the import-
direction constraint) before or during that stage — none of them changes
the shape of the intended solution or the FULL classification.

This Review independently re-derived every checkable factual claim in
`intent.md`, `discovery.md`, and `specification.md` against the current
repository state: `git rev-parse HEAD` = `d102d664b452e17b4cf6b747bf012731655aa737`,
`pytest -q` → 524 passed / 0 failed, `forge validate` → "Forge project is
valid" (exit 0), `forge doctor` → 7/7 checks PASS with one non-blocking
`migration_available` WARN — all four independently re-run during this
Review, and all four match the Baseline `discovery.md` records exactly.
The great majority of citations (file:line references, constant names,
function names, test names, schema enum values, Flow disqualifiers,
Contract rule titles) check out exactly against the real files. The
findings below are the ones that do not, or that identify a real gap.

## Findings

### SR-001 — MINOR — Import-direction citation is off by one line

**Problem:** `discovery.md`'s "A real constraint: import direction"
section — explicitly "carried into Architecture as the basis for
DEC-001" — states that `src/forge_cli/validation/__init__.py:9` already
imports from `forge_cli.protocol_resolution`. Line 9 is not that import.

**Evidence:**
```
$ sed -n '9,10p' src/forge_cli/validation/__init__.py
9:from forge_cli.configuration import InvalidProjectConfigurationError, UnsupportedProtocolVersionError, load_project_configuration
10:from forge_cli.protocol_resolution import CanonicalContractUnavailableError, InvalidProjectFlowConfigurationError, UnknownCanonicalFlowError, resolve_effective_contract, resolve_effective_flow
```
Line 9 is the `forge_cli.configuration` import; the `forge_cli.protocol_resolution`
import is line 10. The underlying substantive claim is correct — I
independently confirmed `src/forge_cli/protocol_resolution/__init__.py`
imports nothing from `forge_cli.validation` (its only imports are
`__future__`, `dataclasses`, `pathlib`, `typing`, `yaml`), and that
`src/forge_cli/adapters/service.py` imports `resolve_effective_artifact_structure`
from `protocol_resolution` but nothing from `validation` — so the cycle
risk NFR-002 guards against (`validation → protocol_resolution →
validation`) is real. Only the specific line number is wrong.

**Impact:** Low on its own — the substance survives — but this is
exactly the kind of citation Architecture is expected to trust without
re-deriving. An Architecture author who opens line 9 to confirm the
constraint before writing DEC-001 will find the wrong import.

**Required Resolution:** Correct the citation to
`validation/__init__.py:10` before Architecture copies it forward.

### SR-002 — MINOR — The "direct precedent" argument attributes a citation to CHG-0016 that CHG-0016 never made

**Problem:** Both `discovery.md`'s "Flow Classification Finding" and
`specification.md`'s "Classification" section state that CHG-0016
"classified FULL, reasoning from FAST's `significant_cross_module_change`
disqualifier" — implying CHG-0016 itself named and relied on that
specific disqualifier.

**Evidence:**
```
$ grep -n "significant_cross_module_change\|Classification" \
  .forge/changes/CHG-0016-canonical-artifact-structure/specification.md
14:## Classification
23:`discovery.md` § Flow Classification Finding for full evidence. FAST is
```
The full line reads "FAST is inapplicable (multi-file, cross-module,
normative-guidance change)" — generic prose. `significant_cross_module_change`
never appears anywhere in CHG-0016's Intent, Discovery, Specification,
Architecture, or Specification Review.

**Impact:** Low — `significant_cross_module_change` is a real disqualifier
in `protocol/flows/fast.yml` (confirmed directly), this Change genuinely
touches `validation/__init__.py`, both Adapters' `projection.py`/`driver.py`,
and `adapters/driver.py`/`adapters/service.py` (confirmed directly), and
`protocol/flows/standard.yml` has no `specification_review` stage at all
(only `full.yml` does — confirmed directly) — so FULL is independently
defensible on its own merits and this finding does not change the
classification outcome. But the "direct precedent" argument as written
retrofits a specific rule citation onto a precedent that reasoned only in
prose.

**Required Resolution:** Rephrase the Classification section to present
the `significant_cross_module_change` citation as this Change's own
independent reasoning, not as something CHG-0016 "reasoned from."

### SR-003 — MINOR — Two of Intent's own Success Criteria have no corresponding Acceptance Criterion

**Problem:** `intent.md`'s Success Criteria lists five items in the same
specific, verifiable style the FR/AC pairs elsewhere in this Change use.
Two are not covered by any AC in `specification.md`:

1. "both Adapters project the same rendered content, byte-for-byte" —
   AC-002 and AC-003 each check that a single bundle-generator call
   includes the exact content *passed into it*; neither checks, at the
   composition-root wiring level (`adapters/service.py`, where content is
   resolved once and threaded into both Drivers, mirroring the
   `artifact_structure_content` precedent at `service.py:445,612`), that
   the *same* rendered string in fact reaches both Adapters.
2. "full test suite, `forge validate`, and `forge doctor` remain green" —
   no AC in AC-001–AC-005 covers this baseline regression check.

**Evidence:** Direct precedent disagrees with this omission for item 2:
CHG-0016's `specification.md` has an explicit `AC-013` — "`forge validate`
and `forge doctor` report the same overall project-valid status before
and after Implementation (regression baseline; see `test-strategy.md`
TDD-003)" (confirmed at `.forge/changes/CHG-0016-canonical-artifact-structure/specification.md:221`).
CHG-0021's Specification has no equivalent.

**Impact:** Low-to-moderate. Verification will very likely run the full
suite and `forge validate`/`forge doctor` regardless, as ordinary FULL
Flow practice (`before_completion` gate: `verification_passed`) — so item
2 is unlikely to be silently skipped even without an explicit AC. Item 1
is the more concrete gap: nothing currently forces a test asserting
cross-Adapter content parity, and this Change's central compatibility
promise (both Adapters "stay at parity," per FR-003) is exactly the kind
of claim that benefits from an explicit, mechanical AC.

**Required Resolution:** Add an AC (or extend AC-002/AC-003) asserting
that the rendered content, threaded through both Adapters via
`AdapterProjectionContext`, produces byte-identical
`decision-rules.md`/`references/decision-rules.md` resources; add an AC
(or a note under an existing one) tying the baseline regression check to
Test Strategy/Verification the way CHG-0016's AC-013 does.

### SR-004 — MINOR — An Out of Scope item is disconnected from anything else in the Change

**Problem:** `intent.md`'s Out of Scope lists "guidance for a Change
opened in a repository with no prior Git history" as a fourth bullet.
Nothing in `intent.md`'s Problem, Scope, or Success Criteria; nothing in
`discovery.md`; and nothing in `specification.md`'s Functional
Requirements discusses Git history or any Git dependency at all — FR-001's
render function reads only in-process Python constants
(`_DEC_CLASSES` et al.), with no filesystem or Git access implied
anywhere in its description.

**Evidence:**
```
$ grep -rn "no prior Git history" .forge/changes/*/*.md
.forge/changes/CHG-0021-adapter-reference-schema-projection/intent.md:73:- guidance for a Change opened in a repository with no prior Git history;
```
The phrase is unique to this Change. Git-history-dependent "fail closed"
behavior is a real, recurring concern elsewhere in this codebase
(`validation/__init__.py:147` and `:611`, `protocol/versions/2/specification.md:33`,
`CHG-0015`'s delegated-authority work) — but none of that machinery is
touched by, or relevant to, this Change's actual mechanism, which is a
pure in-memory renderer over constants already resident in the installed
package (confirmed: `resolve_effective_artifact_structure`, the closest
functional analog cited by `discovery.md` itself, reads a file from
`protocol_root`, not Git history, and this Change's own renderer needs
even less than that).

**Impact:** Low, but real: `protocol/artifact-structure.md` (§2, on
Out-of-Scope coherence generally) and this Review's own charter both
treat an unexplained exclusion as a place where a reader cannot tell
whether it is deliberate, copy-pasted, or evidence of an undocumented
concern. As written it reads as leftover text from a different draft,
most plausibly the Git-history-fail-closed family of concerns that is
real elsewhere in this repository but not here.

**Required Resolution:** Either remove the bullet, or replace it with one
sentence explaining what it actually guards against, if a real reason
exists.

### SR-005 — OBSERVATION — The Problem statement's motivating incident is external and unverifiable from within this repository

**Problem:** `intent.md`'s Problem section grounds this entire Change in
a specific external event — "A first real external validation of Forge
(`crud-produtos`, Laravel 13, `CHG-0001-sanctum-authentication`,
conducted 2026-08-20 with only the Claude Code Adapter installed)" — and
`discovery.md` goes further, quoting what it presents as verbatim text
from that external report ("o enum real ... só existe no `.py` do
pacote instalado ... e no JSON Schema ... nenhum dos dois presente nos
`references/`"). No file, commit, or artifact anywhere in this
repository records, archives, or links to that report or that external
repository.

**Evidence:**
```
$ grep -rln "crud-produtos\|explicit_human_act" --include="*.md" --include="*.yml" .
(no results outside CHG-0021's own intent.md/discovery.md)
$ find . -iname "*crud-produtos*" -o -iname "*external-validation*"
(no results)
```
`ROADMAP.md`'s own "End-to-End Examples & External Project Validation"
section (line 195) still reads, unchanged: "The External validation
matrix below remains entirely open: no real target repository exists in
any ecosystem other than this one" — consistent with there being no
in-repo record of the crud-produtos validation, but also in some tension
with `intent.md` treating that validation as an established fact this
Change is built on.

**Impact:** Low. Both rejections the Problem statement reports are
independently, mechanically verifiable against this repository's own
code regardless of whether the external incident happened exactly as
described (this Review confirmed both: `resolved_via: 'explicit_human_act'`
is genuinely not in `_DEC_RESOLVED_VIA`, and `class: architectural` with
`owning_artifact: specification` genuinely fails the
`_DEC_OWNING_BY_CLASS` check) — so nothing in `specification.md`'s FRs
actually depends on the external report being authentic. This is a
traceability observation, not a defect in the proposed solution.

**Required Resolution:** None required to proceed. If practical, a future
Change capturing the crud-produtos validation as durable evidence (the
way `CHG-0020` curated `CHG-0016`/`CHG-0018` as internal examples) would
let `ROADMAP.md`'s External validation matrix be flipped for Laravel/PHP
on real, in-repo evidence rather than leaving it silently stale next to a
Change that treats the underlying incident as fact.

## Checked and found sound (no defect)

- FR-001's constant names (`_DEC_CLASSES`, `_DEC_MATERIALITY`,
  `_DEC_STATUSES`, `_DEC_AUTHORITIES`, `_DEC_RESOLVED_VIA`,
  `_DEC_OWNING_BY_CLASS`, `_DEC_AUTHORITY_FLOOR`) and `discovery.md`'s
  line citations (`validation/__init__.py:364-371`, exact set spans
  369-371 as claimed) are exact against the live file.
- FR-004's citation of the existing `owning_artifact` error message
  (`validation/__init__.py:439`, `"...expected one of {sorted(allowed_owning)})"`)
  is exact, and the current `resolved_via` message
  (`validation/__init__.py:418`, `"has an invalid resolved_via {resolved_via!r}."`)
  genuinely lacks that convention today — the Problem statement is not
  exaggerated.
- `change-v2.schema.json`'s cited lines are exact:
  `authority` (line 90, flat 3-value enum), `owning_artifact` (line 91,
  unconstrained `{"type": "string", "minLength": 1}`), `resolved_via`
  (line 93, 4-value enum including `null`) — confirming Discovery's
  central finding that `resolved_via` is schema-documented but
  unprojected, while `owning_artifact`/class-conditional rules have no
  schema representation at all.
- The CHG-0016 precedent call chain is exact at every hop:
  `protocol_resolution/__init__.py:141` (`resolve_effective_artifact_structure`)
  → `adapters/service.py:445,612` → `adapters/driver.py:20`
  (`AdapterProjectionContext.artifact_structure_content`) →
  `adapters/{codex,claude_code}/driver.py:46` →
  `adapters/{codex,claude_code}/projection.py`, including that
  `has_artifact_structure = bool(artifact_structure_content)` gates both
  the resource and its `- [Artifact Structure](references/artifact-structure.md)`
  link identically in both Adapters' `projection.py` today — a real,
  reusable, already-shipped pattern.
- `resolve_effective_artifact_structure` (`protocol_resolution/__init__.py:141-161`)
  genuinely has a versioned-root-then-canonical-root file-read fallback
  and no project-extension layer, supporting Discovery's argument that
  the new function should be a renderer over constants, not a reuse of
  that resolver.
- `test_claude_code_projection_bundle.py` and
  `test_codex_projection_bundle.py` both contain
  `test_projection_bundle_omits_artifact_structure_resource_when_not_provided`
  and `test_projection_bundle_includes_artifact_structure_when_provided`
  exactly as assumed (confirmed at lines 77/87 and 77/89 respectively) —
  AC-005's "extend the existing tests" plan has a concrete, real target.
- The Claude Code Adapter's `"## Effective Forge references"` heading and
  its `- [Engineering Contract](references/engineering-contract.md)` /
  conditional Artifact Structure link (`projection.py:167-170`) are exact,
  supporting FR-002's claim about where a decision-rules link would be
  added.
- CON-001/CON-002 do not conflict with anything found in the schema or
  Contract: no file under `protocol/schemas/` needs to change for any
  stated FR, and no Gate/Finding-severity/Decision-semantic/Flow-stage
  change is implied anywhere in the FRs.
- FR/NFR/AC/CON/INV numbering is sequential and gapless (FR-001–005,
  NFR-001–002, AC-001–005, CON-001–002, INV-001), matching
  `protocol/artifact-structure.md` §4's Specification guidance
  (structural core: Summary, Classification, FR, AC, Out of Scope;
  conditional: NFR, Security, INV, CON — all present here in the right
  conditional slots) and CHG-0016's own AC-to-FR-only mapping convention
  (CHG-0016 maps no AC to an NFR either, so CHG-0021 not doing so is
  consistent precedent, not a gap).
- FULL classification is independently defensible on its own facts, apart
  from the SR-002 citation issue: `protocol/flows/fast.yml` genuinely
  lists `significant_cross_module_change` as a disqualifier, this Change
  genuinely touches every module named, and `protocol/flows/standard.yml`
  has no `specification_review` stage at all — FULL is the only one of
  the three canonical Flows under which this Review is even a required
  Gate.
- Security Requirements "None" is accurate: this Change adds a pure
  documentation-rendering function reading only in-process constants and
  sharpens an error message; no new input surface, authorization
  boundary, or attack surface is introduced.
- The Problem statement's two rejections are both real and independently
  reproducible against `validation/__init__.py` exactly as described,
  regardless of the external-provenance question raised in SR-005: `C-055`'s
  actual title ("Human-authority Decisions require an explicit human
  act", `protocol/contract/engineering.md:193`) makes the reported
  `resolved_via: 'explicit_human_act'` mistake plausible and consistent
  with the Contract rule it appears to paraphrase.
- The import-cycle constraint's substance (independent of the SR-001 line
  citation) is real: `protocol_resolution/__init__.py` imports only
  `__future__`, `dataclasses`, `pathlib`, `typing`, `yaml` — nothing from
  `forge_cli.validation` — while `validation/__init__.py` already imports
  from `protocol_resolution`, confirming the one-way edge NFR-002 must
  preserve.
- Baseline reproducibility: `pytest -q` (524 passed), `forge validate`
  ("Forge project is valid", exit 0), and `forge doctor` (7/7 PASS, one
  pre-existing non-blocking `migration_available` WARN) were all re-run
  independently during this Review and match `discovery.md`'s recorded
  Baseline exactly.

## Conclusion

Every load-bearing factual claim in `intent.md`, `discovery.md`, and
`specification.md` that is checkable against this repository — every
cited line number, constant name, function name, test name, schema enum,
Flow disqualifier, and Contract rule title — matches the real repository
with two narrow exceptions (SR-001, SR-002), both minor and neither
changing the Change's technical content or its classification outcome.
The Functional and Non-functional Requirements are internally
consistent, each Acceptance Criterion evaluated is mechanically
verifiable as written, and the two additions identified in SR-003 close
real, precedented gaps rather than correcting something wrong. SR-004
flags a disconnected Out-of-Scope bullet, and SR-005 records — without
requiring any change — that the Problem statement's founding incident is
external to this repository and currently unarchived here. The
`resolved_via` / `owning_artifact` gap this Change fixes is real and
independently reproducible against `validation/__init__.py` on its own
terms, and the CHG-0016 precedent this Change reuses is a genuinely
working, already-shipped mechanism, not an aspirational one.

**PASS** — Specification proceeds to Architecture, carrying the four
MINOR findings and one OBSERVATION above forward for correction alongside
or before DEC-001.

## Resolution Applied

All four MINOR findings were corrected in the same authoring session
that received this Review, before Architecture began:

- **SR-001** — `discovery.md` "A real constraint: import direction"
  corrected from `validation/__init__.py:9` to `:10`.
- **SR-002** — `discovery.md` "Flow Classification Finding" and
  `specification.md` "Classification" reworded: CHG-0016's own
  Classification is now described accurately (prose reasoning, no named
  disqualifier), and `significant_cross_module_change` is presented as
  this Change's own independent reasoning, not attributed to CHG-0016.
- **SR-003** — `specification.md` Acceptance Criteria gained **AC-006**
  (cross-Adapter byte-identical content parity at the
  `AdapterProjectionContext` wiring level) and **AC-007** (regression
  baseline, mirroring CHG-0016's `AC-013` convention).
- **SR-004** — `intent.md`'s disconnected "no prior Git history" Out of
  Scope bullet was removed.

**SR-005** required no resolution per its own "Required Resolution: None
required to proceed" — left as recorded, an OBSERVATION for a possible
future Change, not a defect in this one.
