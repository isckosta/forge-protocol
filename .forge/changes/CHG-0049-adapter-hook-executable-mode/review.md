---
forge:
  artifact: review
  schema: 1
change: CHG-0049
status: active
---

# Review — CHG-0049 Adapter Hook Executable Mode

## Verdict

- **Iteration 1** (initial review, `standard` profile): **REQUEST CHANGES**
  — R-001 (BLOCKER), R-002 (MAJOR), R-003 (MINOR). Resolution 1.
- **Iteration 2** (Resolution Verification of `e7b6b45`): **REQUEST CHANGES**
  — R-004 (BLOCKER), R-005 (MAJOR), R-006 (MAJOR), R-007 (MAJOR, later
  found spurious — see below), O-1 (OBSERVATION). Resolution 2.
- **Iteration 3** (Resolution Verification of Resolution 2): _pending._

Both Reviewers independently confirmed the **implementation code is
correct and has not regressed** — it has been byte-identical since
`ea01dc8` (`git diff ea01dc8..<resolution> -- src tests` is empty). Every
Finding across both iterations was in the Change's own evidence artifacts
(`tdd-evidence.yml`, `verification.md`, `manifest.yml`), not its code. The
recurring root cause: `manifest.yml` fields were edited after the test
suite was run and the suite was not re-run before freezing, so
`verification.md` asserted a PASS that
`tests/contract/test_protocol_contract.py` contradicted.

## Iteration 1 — REQUEST CHANGES

- Subject: frozen implementation `ea01dc8feb010e359139a50ae07904ef3b43eac1`
  (`subject_provenance`: implementation-subject-001).
- Reviewer: independent execution + context, isolated Git worktree at the
  subject commit, fresh venv, no shared context with the Implementation
  (`reviewer_provenance`: reviewer-001).
- Profile: `standard` (STANDARD Flow, post-CHG-0048).

### R-001 · BLOCKER · Change breaks the contract test suite

`tdd-evidence.yml` used cycle ids `TDD-C1..TDD-C5`. `tdd-evidence.schema.json`
requires `^TDD-[0-9]{3,}[A-Z]?$`, so
`tests/contract/test_protocol_contract.py::test_canonical_yaml_instances_satisfy_their_declared_schemas`
failed at the frozen subject: full suite **804 passed / 1 failed**,
contract suite **51 passed / 1 failed**. Baseline `52177af` passes the same
test. `forge validate` does not catch this (it does not validate canonical
YAML against declared schemas).

**Resolution 1:** cycle ids renamed `TDD-001..TDD-005` (and the prose
back-references). This removed the finding but Resolution 1 introduced a
new violation of the same test (R-004); the `TDD-*` id fix itself is
correct and verified at Resolution 2 (`test_canonical_yaml_instances_satisfy_their_declared_schemas`
passes; all five ids match `^TDD-[0-9]{3,}[A-Z]?$`).

### R-002 · MAJOR · verification.md misrepresented the test evidence

`verification.md` asserted Result **PASS** with "805 passed / 52 contract
passed"; `manifest.yml` recorded `verification.status: passed`. The real
figures at `ea01dc8` were 804/1-fail and 51/1-fail (the 805/52 were the
*collected* counts). Root cause: the full suite was run before
`tdd-evidence.yml` was finalized with the invalid ids, and not re-run
before the freeze.

**Resolution 1 / 2:** `verification.md` corrected. Resolution 1's
correction was itself inaccurate (it asserted 805/52 for `e7b6b45`, which
was actually 804/51-fail — R-005). Resolution 2 replaces the prose with a
per-revision table (`ea01dc8` 804/1, `e7b6b45` 804/1, Resolution 2
805/52) and only asserts PASS against the Resolution 2 revision.

### R-003 · MINOR · TDD RED did not meet the Change's own "Valid RED" bar

`tdd-evidence.yml` recorded 3 of 5 cycles (TDD-003/004/005) as implemented
before their pytest assertions, and TDD-001's RED was a
`TypeError: unexpected keyword argument` — which `test-design.md`'s own
"Valid RED" section explicitly disqualifies. TDD-002 (the substantive
publisher logic) is a genuine behavioural RED-first cycle. Not a
correctness issue; the disclosure was honest under C-017.

**Resolution:** `tdd-evidence.yml` `status` changed `compliant` →
`exception` with a top-level `reason` recording exactly which cycles
inverted RED-first and how each RED was verified; `manifest.yml`
`tdd.status` set to `exception` with a matching reason. This converts the
finding from "flagged for the record" into an explicit, recorded TDD
exception, which the Flow's completion gate permits in place of clean
compliance.

## Resolution 1 (revision `e7b6b45`)

- Targets: R-001, R-002, R-003. Scope: `tdd-evidence.yml`,
  `verification.md`, `manifest.yml`, `review.md` (plus `provenance.yml`
  review-control metadata). No `src/` or `tests/` change.
- Outcome at Iteration 2: R-003 resolved; R-001/R-002 **not** resolved —
  see R-004/R-005.

## Iteration 2 — Resolution Verification — REQUEST CHANGES

- Subject: frozen Resolution 1 `e7b6b459700ac76b74abff72de11d517c9ae5bd6`
  (`subject_provenance`: resolution-001).
- Reviewer: independent execution + context, isolated worktree at
  `e7b6b45`, fresh venv, no shared context with the Implementation,
  reviewer-001, or the Resolution (`reviewer_provenance`: reviewer-002).

### R-004 · BLOCKER · Resolution 1 introduced a new violation of the same contract test

`manifest.yml` `review.status: in_progress` is not in
`change-v2.schema.json`'s enum `[pending, active, passed, failed]`, so
`test_canonical_yaml_instances_satisfy_their_declared_schemas` still
failed at `e7b6b45` (full suite 804 / 1, contract 51 / 1). Root cause
(again): `review.status` was set to `in_progress` *after* the
post-rename pytest run, which was not repeated. `review.md` frontmatter
`status: in_progress` had the same non-conventional value.

**Resolution 2:** `manifest.yml` `review.status` → `active`; `review.md`
frontmatter `status` → `active`; `manifest.yml` `artifacts.review` →
`active`. Full suite re-run from the committed state → **805 passed**;
contract suite → **52 passed**; `test_canonical_yaml_instances_...`
passes.

### R-005 · MAJOR · verification.md re-asserted a false PASS against `e7b6b45`

Resolution 1's `verification.md` claimed the post-Resolution run was
"805 passed / 52 passed" and reaffirmed PASS; the real `e7b6b45` figures
were 804/1-fail and 51/1-fail (R-004). Same class as R-002, re-pointed.

**Resolution 2:** `verification.md` Test Evidence replaced with a
per-revision results table; PASS is asserted only against the
Resolution 2 revision, whose 805/52 was produced by re-running the full
and contract suites *from the committed Resolution 2 tree*.

### R-006 · MAJOR · manifest counters / artifact status inconsistent

While R-004 was open, `review.blockers: 0` understated an open blocking
condition, and `artifacts.review: pending` disagreed with
`review.status` / `review.iteration: 1`.

**Resolution 2:** `artifacts.review` → `active`. With R-004 genuinely
fixed and the suite green, `review.blockers: 0` is now accurate; the
`review-001` iteration entry retains `status: failed` /
`new_material_findings: 3` and a `review-002` entry records Iteration 2's
`status: failed` / `new_material_findings: 3`.

### R-007 · MAJOR (spurious) · "no `resolution-001` provenance record"

reviewer-002's worktree was pinned at `e7b6b45`, which pre-dates commit
`1338181d` ("record Resolution 1 provenance"). `resolution-001` **does**
exist, one commit later. This was a review-setup error (the reviewer was
pointed at the pre-provenance commit), not a Change defect. Resolution 2
re-freezes with all provenance in place and Iteration 3 reviews the
correct revision.

### O-1 · OBSERVATION · Resolution 1 commit also touched `provenance.yml`

Adding `reviewer-001` (Iteration 1 record) in the Resolution 1 commit is
review-control metadata and permitted, but it is outside the four-file
scope `review.md` declared. Resolution 2 keeps provenance appends in
their own `chore(...)` commits.

## Resolution 2

- Targets: R-004, R-005, R-006 (and re-freeze to moot R-007).
- Scope: `manifest.yml`, `review.md`, `verification.md` (evidence
  artifacts only; `provenance.yml` review-control metadata in a separate
  commit). No `src/` or `tests/` change since `ea01dc8`.
- Evidence, from the committed Resolution 2 tree: `pytest -q` → **805
  passed**, 2 pre-existing warnings; `pytest tests/contract -q` → **52
  passed**; `forge validate` → valid; end-to-end external-repo repro
  re-confirmed.

## Iteration 3 — Resolution Verification

_Pending. A third independent Reviewer (distinct from the Implementation,
reviewer-001, and reviewer-002) re-reviews the frozen Resolution 2
revision: R-001..R-006 resolved, no Out-of-Scope Mutation, no regression,
`resolution-002` provenance present._
