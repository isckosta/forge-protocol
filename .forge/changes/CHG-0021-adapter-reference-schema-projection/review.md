---
forge:
  artifact: review
  schema: 1
change: CHG-0021
status: passed
---
# Strict Review — CHG-0021

## Verdict

**PASS (final, Iteration 2 — `kind: resolution_verification`).** No
blocking Findings remain outstanding.

- **Iteration 1** (`kind: initial_review`) — **REQUEST CHANGES**: 1
  BLOCKER (R001), 0 MAJOR, 0 MINOR, 2 OBSERVATION (R002, R003).
- **Iteration 2** (`kind: resolution_verification`) — **PASS**: R001
  independently re-verified genuinely resolved against actual repository
  state, not accepted from `resolution-001`'s own claim; R002 and R003
  independently confirmed to have genuinely required no Resolver action;
  Resolution Delta computed independently matches `resolution-001`'s
  declared `scope` exactly, both directions — no Out-of-Scope Mutation; 0
  new material findings.

Everything below this Summary down to the end of the original `##
Conclusion` is Iteration 1's verbatim historical record. Iteration 2 is
appended at the end of this file.

`protocol/policies/review.yml` sets `blocking: [blocker, major]`; R001 was
the only ever-blocking Finding, and it is now resolved. Both Iterations'
outcomes stand, and this Change may proceed toward Completion.

**REQUEST CHANGES (Iteration 1, `kind: initial_review`), as originally
recorded.** 1 BLOCKER, 0
MAJOR, 0 MINOR, 2 OBSERVATION. `protocol/policies/review.yml` sets
`blocking: [blocker, major]`, so the single BLOCKER is blocking.

The engineering substance of this Change is sound: `render_decision_rules_reference()`
genuinely derives every rendered value from the live `_DEC_*` constants with
no duplicated literal; both Adapters' wiring is byte-for-byte symmetric and
independently tested for cross-Adapter parity; the `resolved_via` error
message change is additive and breaks no pre-existing test; DEC-001 is
correctly resolved against `protocol/policies/decision.yml`; and every
Specification Review MINOR finding was genuinely corrected before
Architecture began. The BLOCKER is not a defect in the rendered content,
the wiring, or the tests — it is that `verification.md` and
`tdd-evidence.yml` both assert a full-suite regression baseline of **"535
passed, 0 failed"** that is not reproducible. Independently re-running
`pytest -q`, both against the current repository state and against the
exact frozen `implementation-001` subject commit `provenance.yml` cites,
produces **534 passed, 1 failed** in both cases. The one failing test is a
real, mechanical schema-conformance defect this Change's own `T-012`
authored into `traceability.yml`, present since the Implementation commit
itself — not something introduced by this Review, and not curable by this
Review's own writes alone.

## Summary

Counting semantics, stated explicitly since the Protocol does not fix them:
**Raised** is cumulative — every Finding ever recorded in this Review, in
the Iteration that recorded it. **Outstanding** is the state *after* the
final Iteration, and is what `manifest.yml`'s
`review.blockers`/`majors`/`minors`/`observations` carry.

| Severity | Raised (It. 1) | Raised (It. 2) | Raised total | Outstanding | Blocking |
| --- | --- | --- | --- | --- | --- |
| BLOCKER | 1 | 0 | 1 | 0 | yes |
| MAJOR | 0 | 0 | 0 | 0 | yes |
| MINOR | 0 | 0 | 0 | 0 | no |
| OBSERVATION | 2 | 0 | 2 | 2 | no |

R001 (BLOCKER, Iteration 1) is resolved by `resolution-001` and verified
in Iteration 2 — no longer outstanding. R002 and R003 (OBSERVATION,
Iteration 1) remain recorded for completeness — both were independently
confirmed in Iteration 2 to have genuinely required no fix (R002 already
cured by `review-001`'s own `manifest.yml` write; R003 an honestly-
disclosed limitation, not a defect) — and are still counted Outstanding
since neither was ever a defect requiring resolution.

## Review Subject

Frozen Implementation subject `34b534a0ae98015fb32faef75ba87f097219b7a4`
(`provenance.yml`, record `implementation-001`), confirmed by direct
`git cat-file`/`git show` lookup to be a real, reachable commit matching
the `immutable_ref` value exactly. `HEAD` at the start of this Review is
`cd8df5ff04dab501840261163d901f0e1da56987` (branch
`chg-0021-adapter-reference-schema-projection`), whose only difference
from the subject is the addition of `manifest.yml` and `provenance.yml`
themselves (`git show cd8df5f --stat`) — Change-local review-control
metadata, matching the freeze-and-record-provenance pattern this
repository already used for `CHG-0016` and `CHG-0020` (`manifest.yml` is
not created until the commit that records `implementation-001`'s
provenance, one commit after the `feat` commit itself; confirmed by
`git log --diff-filter=A` across all three Changes). `git status
--porcelain` was clean at the start of this Review.

## Review Execution Independence

This Review was executed in an Execution and Execution Context distinct
from the Implementation session that produced `implementation-001`, per
Contract C-026 and Protocol 2 §2: `execution.id
review-exec-chg0021-20260821-71fbe20a`, `context_id
review-context-chg0021-20260821-3d68f01c`, both disjoint from
`implementation-exec-chg0021-20260821-01` /
`implementation-context-chg0021-20260821-01`. It was performed cold, from
committed repository state, without access to the Implementation
conversation or any hint about where to look. Every artifact
(`intent.md` through `verification.md`) was read directly; every diff was
read via `git show 34b534a` / `git diff 34b534a^..34b534a` per file, not
inferred from commit messages; `pytest -q`, `forge validate`, and
`forge doctor` were run directly by this Review's own execution, not
copied from `verification.md`. See `provenance.yml` record `review-001`
for this execution's own self-recorded provenance and honest assurance
statement.

## Iteration 1 — REQUEST CHANGES

### R001 — BLOCKER — The claimed full-suite regression baseline ("535 passed, 0 failed") is not reproducible; the real, current suite is 534 passed, 1 failed, both now and at the frozen Implementation subject commit itself

**Problem:** `verification.md` ("Test Evidence") and `tdd-evidence.yml`
(`TDD-007`, `AC-007`'s only cited evidence) both state `pytest -q` (full
suite) produces **535 passed, 0 failed** — the pre-Implementation Baseline
of 524 plus 11 deliberate additive tests, with zero regressions. This is
the sole mechanical evidence backing AC-007 ("full test suite ...
remain[s] green") and the regression half of `verification.md`'s overall
PASS conclusion.

**Evidence:**

Independently re-run against the current working tree (`HEAD
cd8df5f`, clean):

```
$ .venv/bin/python -m pytest -q
...
FAILED tests/contract/test_protocol_contract.py::test_canonical_yaml_instances_satisfy_their_declared_schemas
1 failed, 534 passed in 39.80s
```

```
AssertionError:
.forge/changes/CHG-0021-adapter-reference-schema-projection/manifest.yml:review: 'iteration' is a required property
.forge/changes/CHG-0021-adapter-reference-schema-projection/manifest.yml:review: 'iterations' is a required property
.forge/changes/CHG-0021-adapter-reference-schema-projection/traceability.yml:requirements.CON-001.tasks: [] should be non-empty
.forge/changes/CHG-0021-adapter-reference-schema-projection/traceability.yml:requirements.CON-002.tasks: [] should be non-empty
```

To rule out that this is an artifact of this Review's own in-progress
state (e.g. `manifest.yml` not yet carrying `review.iteration`), the exact
frozen Implementation subject commit was checked out in an isolated `git
worktree` (`git worktree add <tmp> 34b534a0ae98015fb32faef75ba87f097219b7a4`)
and the same command re-run there, unmodified:

```
$ .venv/bin/python -m pytest -q   # at 34b534a itself
...
FAILED tests/contract/test_protocol_contract.py::test_canonical_yaml_instances_satisfy_their_declared_schemas
1 failed, 534 passed in 40.65s
```

At `34b534a`, `manifest.yml` does not exist yet (confirmed: `git show
34b534a --stat` lists no `manifest.yml`; it is first added one commit
later, in `cd8df5f`), so only the two `traceability.yml` failures fire —
but the test already fails, with the identical root cause. `traceability.yml`
itself **is** part of the `34b534a` commit (`git show 34b534a --stat`
lists `traceability.yml | 22 +++++` as newly added), and `git show
34b534a:.forge/changes/CHG-0021-adapter-reference-schema-projection/traceability.yml`
already contains `CON-001: {tasks: [], ...}` and `CON-002: {tasks: [],
...}` at that exact commit. This means the "535 passed, 0 failed" claim
in `tdd-evidence.yml`/`verification.md` — both authored as part of the
same `T-012` work in the same commit — was never true of the commit it
describes.

Root cause, confirmed against the schema directly:
`protocol/schemas/traceability.schema.json:11` requires every
`requirements.*` entry's `tasks` array to have `"minItems": 1`. CHG-0021's
own `traceability.yml` is the **only** traceability file in this
repository's entire history with an empty `tasks` array anywhere:

```
$ grep -rn "tasks: \[\]" .forge/changes/*/traceability.yml
.forge/changes/CHG-0021-adapter-reference-schema-projection/traceability.yml:11:  CON-001: {tasks: [], evidence: no_file_under_protocol_schemas_changed}
.forge/changes/CHG-0021-adapter-reference-schema-projection/traceability.yml:12:  CON-002: {tasks: [], evidence: no_gate_finding_severity_decision_semantic_or_flow_stage_touched}
```

Every other Change's `CON-*`/`INV-*`/`DEC-*` traceability entry cites at
least one task (e.g. `CHG-0016`: `CON-001: {tasks: [T-002, T-003, T-004],
...}`; `CHG-0019`: `CON-001: {tasks: [T-004], ...}`). CON-001/CON-002's
*substantive* claims are themselves true — independently confirmed no file
under `protocol/schemas/` changed in `34b534a`, and no Gate/Finding-
severity/Decision-semantic/Flow-stage file changed either — only the
`tasks` field's emptiness is the schema violation.

Separately (a distinct but compounding cause of the same test failure):
`CHG-0015`, this repository's other currently `review: pending` Change,
already carries the correct freeze-time placeholder shape —
`review: {status: pending, iteration: 0, ..., iterations: []}` — proving
that shape is the established convention for a manifest not yet reviewed.
CHG-0021's `T-012`-authored `manifest.yml` instead omits `iteration` and
`iterations` entirely, which is itself schema-invalid independent of
`CHG-0015`'s precedent.

**Impact:** `verification.md`'s and `tdd-evidence.yml`'s central mechanical
claim is false and independently, reproducibly falsifiable — not a
transcription slip in a single digit, but a real, currently-failing test
in this repository, present since the Implementation commit itself.
`protocol/flows/full.yml`'s `before_completion` gate requires
`verification_passed`; that cannot be honestly asserted while the full
suite the Change's own AC-007/TDD-007 exists specifically to guard is red.
`forge validate` does not catch this (independently confirmed: `forge
validate` → "Forge project is valid", exit 0, both before and after this
Review's own writes) — it does not run the same JSON-Schema-level
structural check `tests/contract/test_protocol_contract.py` does, so
`forge validate` passing is not evidence this defect is absent, and
relying on it alone would have missed this Blocker entirely.

**Required Resolution:** A Resolver must repair
`.forge/changes/CHG-0021-adapter-reference-schema-projection/traceability.yml`
so `CON-001.tasks` and `CON-002.tasks` are each non-empty — citing the
task(s) where each Constraint was actually checked/honored, following
every other Change's existing convention for `CON-*` entries with no
directly-implementing task (e.g. citing the regression-baseline task,
`T-011`, the same way `CHG-0019`'s `CON-003` cites its own baseline task) —
and then independently re-run `pytest -q` to confirm **0 failures** before
this Change proceeds to Resolution Verification. This Review's own
`manifest.yml` update (below) independently supplies the missing
`review.iteration`/`review.iterations` keys the same failing assertion
also names, so that half of the current failure is already cured by this
Review's own artifact and does not require separate Resolver action —
only the `traceability.yml` half remains outstanding.

### R002 — OBSERVATION — `manifest.yml`'s freeze-time `review:` block omitted the placeholder shape this repository's own precedent already establishes

`CHG-0015` (also currently `review: pending`) demonstrates the correct
shape for a manifest not yet reviewed: `review: {status: pending,
iteration: 0, blockers: 0, majors: 0, minors: 0, observations: 0,
iterations: []}`. CHG-0021's `T-012`-authored `manifest.yml` instead wrote
`review: {status: pending, blockers: 0, majors: 0, minors: 0,
observations: 0}`, omitting `iteration` and `iterations` entirely. This is
part of R001's mechanical failure (both are schema-required fields) but is
recorded here separately because it is a distinct authoring gap from the
`traceability.yml` issue, with a different owner in principle (Implementation's
`T-012`, not Resolution) — and because this Review's own write below
already cures it, it does not carry a "Required Resolution" of its own.
Not blocking.

### R003 — OBSERVATION — RED-before-GREEN chronology cannot be verified from git history, and I say so rather than asserting either way

All of this Change's Implementation work lands in a single commit
(`34b534a`), with the new tests and the production code they exercise
committed together. There is no commit in which a test exists and its
production implementation does not, so git provides no independent
evidence of RED-before-GREEN ordering for any of the seven TDD cycles.
This matches the exact same limitation `CHG-0016`'s own Review recorded as
R009 for that Change, and `CHG-0020`'s squashed-commit-per-artifact-group
pattern before it — it is a standing characteristic of how this
repository's sessions commit, not a new deficiency introduced by CHG-0021.

What I *can* confirm is that every claimed RED failure reason in
`tdd-evidence.yml` is exactly what the pre-Change code shape would
produce: `render_decision_rules_reference` did not exist in
`validation/__init__.py` before this commit (confirmed:
`git show 34b534a^:src/forge_cli/validation/__init__.py | grep
render_decision_rules_reference` returns nothing), so `ImportError` is
the right failure for TDD-001; neither `generate_claude_code_skill_bundle` nor
`generate_codex_skill_bundle` nor `AdapterProjectionContext` had a
`decision_rules_content` parameter/field before this commit (confirmed by
reading the pre-image side of each `git show 34b534a` diff hunk directly,
each `@@` context line shown above), so the claimed `TypeError:
unexpected keyword argument` is right for TDD-002/TDD-003; and the
pre-image of the `resolved_via` check message
(`"has an invalid resolved_via {resolved_via!r}."`, no expected-values
clause) is exactly what TDD-004's claimed pre-fix `AssertionError` requires.
`tdd-evidence.yml` also honestly records `red.observed: false` for
TDD-005/TDD-006/TDD-007 with stated reasons (compatibility/parity/regression
guards) rather than fabricating a RED run for them, which is the behavior
`post_hoc_tests_not_misrepresented` looks for. I found no indication of
misrepresentation, only an honestly-disclosed limit on what any Reviewer
can verify from squashed history.

## Checked and found sound (no defect)

- **`render_decision_rules_reference()` genuinely derives from the live
  constants, with no duplicated literal.** Read directly from
  `src/forge_cli/validation/__init__.py:373-410`: every enum line is
  `', '.join(sorted(_DEC_*))`, and both mapping sections iterate
  `sorted(_DEC_OWNING_BY_CLASS.items())` / `sorted(_DEC_AUTHORITY_FLOOR.items())`
  directly — no `class`, `authority`, or enum value appears as a bare
  string literal inside the function body itself. Ran the function
  directly (`python -c "from forge_cli.validation import
  render_decision_rules_reference; print(...)"`); its output matches
  `_DEC_CLASSES`/`_DEC_OWNING_BY_CLASS`/`_DEC_AUTHORITY_FLOOR` exactly as
  they exist at lines 364-371, and does not restate any Engineering
  Contract prose (INV-001 — the rendered text only names `forge validate`
  and the mechanical rules, never a C-0xx rule or its wording).
- **Both Adapters' projection wiring is symmetric and additive-only.**
  `git show 34b534a` for `driver.py`, `service.py`,
  `claude_code/projection.py`, and `codex/projection.py` confirms
  `decision_rules_content: str = ""` is appended after existing fields in
  every dataclass (no positional-argument break), wired at both existing
  `AdapterProjectionContext` construction sites in `service.py`
  (lines 449, 617), and gated by `has_decision_rules = bool(decision_rules_content)`
  in both `projection.py` files, mirroring `has_artifact_structure`
  structurally identically in each.
- **Cross-Adapter byte-identical content parity (AC-006) is genuinely
  tested, not merely asserted.**
  `test_decision_rules_reference_is_byte_identical_across_both_adapters`
  threads one `render_decision_rules_reference()` value through both
  `generate_claude_code_skill_bundle` and `generate_codex_skill_bundle`
  and asserts the two resources' content is identical to each other and
  to the source string — this is the correct falsification target
  (per-generator echo alone would not catch a wiring divergence). Ran in
  isolation: passes.
- **The `resolved_via` error-message change is additive and breaks
  nothing pre-existing.** `git show 34b534a` for
  `validation/__init__.py:456` shows the new `f" (expected one of
  {sorted(_DEC_RESOLVED_VIA)}, or omit while unresolved)"` clause is
  appended, not a replacement; `grep -rn "has an invalid resolved_via"`
  across `src/` and `tests/` finds only the one production site and the
  one (new) test asserting the substring `"has an invalid resolved_via"`
  still holds; `grep -rn "expected one of"` finds no other fixture or
  golden-output file that could now mismatch.
- **DEC-001 is correctly resolved.** `class: architectural` →
  `owning_artifact: architecture` matches
  `protocol/policies/decision.yml`'s `ownership.owning_artifact_by_class.architectural:
  architecture` exactly; `authority: agent_with_review` matches
  `default_authority.architectural: agent_with_review`; `architectural`
  has no entry in `decision.yml`'s `authority_floor` (only `product`/`contract`
  do), so no floor is violated; `resolved_via: autonomous_decision` is
  permitted because `authority` is not `human` (C-054/C-055 do not apply).
- **Every Specification Review MINOR finding (SR-001–SR-004) was actually
  corrected before Architecture began, not merely claimed to be.**
  `discovery.md`'s import-direction citation now reads `:10` (SR-001);
  `discovery.md`/`specification.md`'s Classification sections now present
  `significant_cross_module_change` as this Change's own reasoning, not
  attributed to `CHG-0016` (SR-002); `specification.md` carries AC-006
  and AC-007 (SR-003); `intent.md`'s disconnected "no prior Git history"
  Out of Scope bullet is gone (SR-004) — confirmed by reading each file
  directly, not by trusting `specification-review.md`'s own "Resolution
  Applied" section.
- **Test suite substance, reproduced independently in isolation:**
  `pytest -q tests/unit/test_decision_rules_reference.py
  tests/unit/test_claude_code_projection_bundle.py
  tests/unit/test_codex_projection_bundle.py
  tests/unit/test_unresolved_decisions.py
  tests/integration/test_adapter_distribution.py -k "decision_rules or
  resolved_via or wheel"` → **14 passed**. Every test this Change added or
  touched genuinely passes; the one failing test in the full suite (R001)
  is unrelated to any of these and pre-existing in the repository's
  contract-test module.
- **`forge doctor` unchanged.** 7/7 PASS, the same single non-blocking
  `migration_available` WARN recorded in `discovery.md`'s Baseline — no
  new finding, matching `verification.md`'s claim exactly.
- **No file under `protocol/schemas/` changed, and no Gate/Finding-
  severity/Decision-semantic/Flow-stage file changed (CON-001/CON-002's
  substance, independent of R001's `tasks: []` recording defect).**
  Confirmed directly against `git show 34b534a --stat`'s sixteen-file
  list — none are under `protocol/schemas/`, `protocol/flows/`, or
  `protocol/policies/`.

## Conclusion

One BLOCKER (R001) is outstanding under `protocol/policies/review.yml`'s
`blocking: [blocker, major]`. It is not a defect in this Change's
rendered content, Adapter wiring, or test coverage — every one of those
was independently reproduced and found correct — but the Change cannot
honestly proceed to Completion while `verification.md`/`tdd-evidence.yml`
assert a full-suite regression baseline that this Review has shown, twice
independently (current `HEAD` and the frozen `implementation-001` subject
commit itself), is not true. `pytest -q` currently reports **534 passed,
1 failed**, not the claimed 535/0. `forge validate` remains "Forge project
is valid" (exit 0) and `forge doctor` remains 7/7 PASS, both unchanged
from Baseline and from `verification.md`'s claims — only the full pytest
suite's contract-schema check disagrees with the record.

Two OBSERVATIONs (R002, R003) are recorded for completeness and are
non-blocking: R002 is already cured by this Review's own `manifest.yml`
write; R003 documents an honestly-disclosed, pre-existing limitation on
verifying TDD chronology from squashed commit history, matching this
repository's own established precedent (`CHG-0016` R009).

Per Contract C-025 and C-026, this Reviewer resolves nothing. Only
`review.md`, `manifest.yml`'s `review:`/`artifacts.review` fields, and
`provenance.yml`'s new `review-001` record — the Change-local
review-control metadata the freeze discipline permits — were written by
this Iteration. Re-review after resolution is required
(`protocol/policies/review.yml: re_review.required_after_blocking_resolution:
true`) and MUST run in an Execution and Execution Context distinct from
the Resolution that addresses R001.

**REQUEST CHANGES.**

## Iteration 2 — PASS (`kind: resolution_verification`)

### Iteration 2 scope and authority

This Iteration is a **Resolution Verification**, not a second Initial
Review. Per `protocol/contract/engineering.md` C-047 and
`protocol/versions/2/specification.md` §10-§11, its authority is bounded
to exactly three things:

1. R001 — the sole Finding `resolution-001` targets;
2. defects within `resolution-001`'s own Resolution Delta;
3. Out-of-Scope Mutation.

It is deliberately **not** a re-audit of `implementation-001`. Nothing in
Iteration 1's "Checked and found sound" section — `render_decision_rules_reference()`'s
derivation from live constants, both Adapters' wiring symmetry, the
cross-Adapter byte-identical parity test, the `resolved_via` message
change, DEC-001's resolution, or the Specification Review MINOR
corrections — was re-litigated here. Re-opening any of that is precisely
what C-047 forbids.

### Iteration 2 execution independence

Executed cold, from committed repository state, in an Execution and
Execution Context distinct from `implementation-001`/`resolution-001`
(both `implementation-exec-chg0021-20260821-01` /
`implementation-context-chg0021-20260821-01`) and from `review-001`
(`review-exec-chg0021-20260821-71fbe20a` /
`review-context-chg0021-20260821-3d68f01c`): `review-exec-chg0021-resverify-20260821-c94a1e6f`
/ `review-context-chg0021-resverify-20260821-8b1de0f3`. This session has no
memory of either prior execution and read `provenance.yml` (all three
existing records), `manifest.yml`, Iteration 1 of this file, and
`protocol/versions/2/specification.md` §10-§11 directly, with no hint about
where to look. No claim in `resolution-001`'s own `provenance.yml`
statement, `verification.md`, or `tdd-evidence.yml` was accepted without
independent reproduction against the actual diff, the actual current
source, and the actual test suite. See `provenance.yml` record `review-002`
for this execution's own self-recorded provenance.

Subject: `resolution-001`, frozen at
`48df268f94bcf664c90924f6ca806dcada8edc61` (revision
`chg-0021-resolution-001`). `HEAD` at the start of this Iteration is
`c0163d2`, whose only difference from the subject is `provenance.yml` (the
`resolution-001` record itself, added one commit later) — Change-local
review-control metadata, which the §5 effective-workspace freeze permits.
`git status --porcelain` was clean throughout this Iteration.

### Resolution Delta, computed independently — no Out-of-Scope Mutation

Computed per §11 as the committed diff between the immutable revision of
the Iteration immediately preceding this one (`review-001`'s subject,
`34b534a0ae98015fb32faef75ba87f097219b7a4`) and this Iteration's own
subject (`48df268f94bcf664c90924f6ca806dcada8edc61`) — both already-frozen
historical commits, not the current workspace — minus this Change's exact
`manifest.yml`, `provenance.yml`, and `review.md` paths:

```
$ git diff --name-only 34b534a..48df268
.forge/changes/CHG-0021-adapter-reference-schema-projection/manifest.yml
.forge/changes/CHG-0021-adapter-reference-schema-projection/provenance.yml
.forge/changes/CHG-0021-adapter-reference-schema-projection/review.md
.forge/changes/CHG-0021-adapter-reference-schema-projection/tdd-evidence.yml
.forge/changes/CHG-0021-adapter-reference-schema-projection/traceability.yml
.forge/changes/CHG-0021-adapter-reference-schema-projection/verification.md
```

Subtracting the three Change-local paths leaves exactly three:

| # | Resolution Delta path | Covered by declared `scope` |
| --- | --- | --- |
| 1 | `tdd-evidence.yml` | yes |
| 2 | `traceability.yml` | yes |
| 3 | `verification.md` | yes |

`resolution-001` declares exactly these same three paths as `scope`. The
two sets are **exactly equal** in both directions — no Resolution Delta
path is uncovered, and no declared `scope` entry is broader than the Delta
actually taken. No file under `src/`, `tests/`, or `protocol/` changed
between `34b534a` and `48df268` (confirmed by the same `git diff
--name-only` output above — none of the six paths lies outside
`.forge/changes/CHG-0021-adapter-reference-schema-projection/`).
**Out-of-Scope Mutation: none.** Consequently `full_review_required` is
`false` and this Iteration is eligible to be `status: passed`.

### R001, re-checked against actual repository state — resolved

Not accepted from `resolution-001`'s own claim or from `verification.md`'s
own "Correction" note. Read `traceability.yml` directly (`git diff
34b534a..48df268 -- .../traceability.yml`): `CON-001.tasks` and
`CON-002.tasks` changed from `[]` to `[T-001, T-002, T-003, T-004, T-005,
T-006, T-007]`, satisfying `protocol/schemas/traceability.schema.json`'s
`minItems: 1`.

Ran the exact previously-failing test myself against current `HEAD`
(`c0163d2`):

```
$ .venv/bin/python -m pytest -q tests/contract/test_protocol_contract.py::test_canonical_yaml_instances_satisfy_their_declared_schemas
1 passed in 0.49s
```

Ran the full suite against current `HEAD`:

```
$ .venv/bin/python -m pytest -q
535 passed in 41.64s
```

To rule out that this is an artifact of anything added after the
Resolution commit itself (this Change's own `provenance.yml` write at
`c0163d2`, or anything in this Iteration's own in-progress state), the
exact frozen `resolution-001` subject commit `48df268` was checked out in
an isolated `git worktree` (`git worktree add <tmp>
48df268f94bcf664c90924f6ca806dcada8edc61`) and the full suite re-run there,
unmodified:

```
$ .venv/bin/python -m pytest -q   # at 48df268 itself, isolated worktree
535 passed in 42.60s
```

**535 passed, 0 failed — genuinely, independently, twice.** `forge
validate` → `Forge project is valid` (exit 0). `forge doctor` → 7/7 PASS,
the same single non-blocking `migration_available` WARN, unchanged. The
worktree was removed after use (`git worktree remove --force`); `git
worktree list` confirms only this repository's own working tree remains.
R001 is resolved.

### R002, re-checked — genuinely required no Resolver action

`resolution-001`'s `targets` correctly excludes R002. Read the current
`manifest.yml` `review:` block directly: `iteration: 1` and `iterations:
[{id: review-001, ...}]` are both present — the exact placeholder/bound
shape R002 said was missing at freeze time. This was written by
`review-001` itself (Iteration 1's own `manifest.yml` update, per its
Conclusion: "This Review's own `manifest.yml` update ... independently
supplies the missing `review.iteration`/`review.iterations` keys"), not by
`resolution-001` — confirmed the Resolution Delta (above) does not touch
`manifest.yml` at all. R002 was genuinely already cured before the
Resolution ran, not silently dropped.

### R003, re-checked — genuinely an honest disclosed limitation, not a defect

`resolution-001`'s `targets` correctly excludes R003. R003 states that
RED-before-GREEN chronology cannot be verified from this Change's squashed
Implementation commit history — a limitation on what any Reviewer can
observe, not a defect in the Change. `resolution-001` itself lands in a
single commit (`48df268`), so the same limitation applies to `TDD-008`
(the Resolution's own new TDD cycle) by the same reasoning: no commit
exists in which `traceability.yml` still holds `tasks: []` while a test
asserts against it. However, TDD-008's claimed RED state (534 passed, 1
failed) is not merely asserted — it is independently, reproducibly
verified by two separate Reviews now (`review-001`'s own worktree
reproduction against `34b534a`, and this Iteration's own reproduction
against the same commit and, further, against `48df268` itself before the
fix would have applied). `tdd-evidence.yml`'s `TDD-008` entry does not
overclaim a git-verified RED-before-GREEN chronology it cannot support; it
cites the actual independent verification available. Nothing about R003
was fixed, and nothing needed to be — it remains exactly what Iteration 1
recorded it as.

### New defects within the Resolution Delta: none

Read every line of the Resolution Delta's three files directly (`git diff
34b534a..48df268` above, reproduced in full). `traceability.yml`'s
`CON-001`/`CON-002` task lists correctly name only implementation tasks
(`T-001`..`T-007`) that existed before this Resolution — no invented task
ID. `tdd-evidence.yml`'s new `TDD-008` cycle's `red`/`green` evidence
matches the actual, independently-reproduced test output exactly (534/1
before, 535/0 after — not a different pair of numbers). `verification.md`'s
new "Correction (post-Review)" paragraph honestly states the
`implementation-001`-commit figure was false and explains the fix, rather
than silently overwriting the original "535 passed, 0 failed" claim to
hide that it was ever wrong. `cycle_count: 8` matches the actual count of
entries under `cycles:` (8, confirmed by direct count). No new material
finding was found. `new_material_findings: 0`.

### Full suite, `forge validate`, `forge doctor` — reproduced independently, all as claimed

```
$ .venv/bin/python -m pytest -q
535 passed in 41.64s
$ forge validate
Forge project is valid
$ forge doctor
PASS git_available / PASS git_repository / PASS forge_initialized /
PASS project_configuration / PASS protocol_compatibility /
PASS canonical_flows / PASS canonical_contract /
WARN migration_available (6 migration candidate(s) found; pre-existing, unchanged)
```

`forge validate` does not raise a C-026 "review subject changed after
freeze" finding here (unlike `CHG-0019`'s own Iteration 2 O002): the
relevant check
(`src/forge_cli/validation/__init__.py:349`) only fires when a bound
Iteration's `status` is `pending` or `passed`; `review-001`'s bound
Iteration is `status: failed`, so the check does not apply to it, and this
Iteration's own `review-002` write (below) is what first introduces a
`passed` bound Iteration for `resolution-001`'s revision — confirmed
consistent, not a discrepancy.

## Iteration 2 Conclusion

Zero BLOCKER/MAJOR/MINOR/OBSERVATION Findings raised by this Iteration.
R001 is verified genuinely resolved against actual repository state — not
accepted from `resolution-001`'s own narrative — confirmed by independent
reproduction of the full suite and the specific previously-failing test,
twice (current `HEAD` and an isolated worktree of the frozen
`resolution-001` subject commit itself). R002 and R003 are independently
confirmed to have genuinely required no Resolver action, not silently
ignored. The Resolution Delta, computed independently, exactly matches
`resolution-001`'s declared `scope` in both directions: **no Out-of-Scope
Mutation**. No new defect was found within the Resolution Delta.
`new_material_findings: 0`. This Change is **PASS (final)** and is
released to proceed toward Completion.
