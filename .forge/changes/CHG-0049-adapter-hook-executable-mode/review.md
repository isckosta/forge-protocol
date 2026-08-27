---
forge:
  artifact: review
  schema: 1
change: CHG-0049
status: complete
---

# Review — CHG-0049 Adapter Hook Executable Mode

## Verdict

- **Iteration 1** (initial review, `standard` profile): **REQUEST CHANGES**
  — R-001 (BLOCKER), R-002 (MAJOR), R-003 (MINOR). Resolution 1.
- **Iteration 2** (Resolution Verification of `e7b6b45`): **REQUEST CHANGES**
  — R-004 (BLOCKER), R-005 (MAJOR), R-006 (MAJOR), R-007 (MAJOR, later
  found spurious — see below), O-1 (OBSERVATION). Resolution 2.
- **Iteration 3** (Resolution Verification of Resolution 2 `540e35c`):
  **PASS**. R-001..R-006 each independently re-verified (full suite
  805/0, contract 52/0, the three canonical YAMLs re-validated against
  their schemas, historical revision cross-check matched
  `verification.md`'s table, `git diff ea01dc8..540e35c -- src tests`
  empty, provenance un-rewritten, end-to-end repro re-confirmed). One
  non-blocking OBSERVATION (O-2), addressed post-PASS.
- **External review (PR #41, Codex)**: R-008 (P1 / BLOCKER) — the
  executable-bit check accepted any of `0o111` instead of the owner bit.
  Resolution 3 (the only post-review code change). Iteration 4
  (Resolution Verification of Resolution 3): _pending._

**Overall: PASS through Iteration 3; Iteration 4 pending on R-008.**

Iterations 1–3 confirmed the code was byte-identical since `ea01dc8` and
correct for its declared cases; the recurring finding there was
`manifest.yml`/`tdd-evidence.yml` fields edited after the suite was run
and not re-run, so `verification.md` asserted a PASS
`tests/contract/test_protocol_contract.py` contradicted. R-008 is the
first genuine code-correctness finding — from an external review surface,
after Iteration 3 passed.

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

## Iteration 3 — Resolution Verification — PASS

- Subject: frozen Resolution 2 `540e35c815e252f13791897bc5ff140d297e1006`
  (`subject_provenance`: resolution-002); worktree at `ffdc249` (adds only
  `resolution-002` to `provenance.yml`).
- Reviewer: independent execution + context, isolated worktree, fresh
  venv, no shared context with the Implementation, reviewer-001,
  reviewer-002, or either Resolution (`reviewer_provenance`: reviewer-003).

**Findings: none blocking.** R-001/R-004 (contract test) — full suite
805/0, contract 52/0, `test_canonical_yaml_instances_...` passes;
`manifest.yml`, `tdd-evidence.yml`, `provenance.yml` independently
re-validated against their schemas. R-002/R-005 — `verification.md`'s
per-revision table is accurate row-by-row against measurement; PASS
asserted only for `540e35c`. R-003 — `tdd.status: exception` + honest
`reason`, schema-valid. R-006 — `manifest.yml` review block internally
consistent, both prior iteration entries present. No Out-of-Scope
Mutation (`git diff ea01dc8..540e35c -- src tests` empty; `540e35c..ffdc249`
is `provenance.yml` only). Provenance complete (6 records) and
un-rewritten (C-026: the four pre-Resolution-2 records byte-identical
between first commit `1338181d` and `ffdc249`). End-to-end external-repo
behaviour re-confirmed.

### O-2 · OBSERVATION (non-blocking) · addressed

`manifest.yml` `review-002` carried `finding_classes: []` where every
other repo Change populates it for a failed `resolution_verification`.
Set to `[resolution_regression, unresolved_finding]` to match this
review's own prose (R-004 was a Resolution 1 regression; R-002/R-005 an
unresolved finding across Resolution 1). A non-blocking metadata
alignment to already-reviewed content; no further review round.

## External Review — PR #41 (Codex) — R-008

### R-008 · BLOCKER (P1) · `repository.py:_snapshot_artifact` — executable check must require the owner bit

`stat.S_IMODE(mode) & 0o111` reports a file executable when *any* execute
bit is set. A hook at `0o655` (`chmod u-x` on the published `0o755` —
group/other execute set, owner not) is therefore misreported executable.
Since the Adapter installs and runs the hook as the owning user, POSIX
permission selection stops at the owner class and never consults
group/other — the hook is *not* runnable — yet `doctor` passes and
`adapter update` classifies the byte-current artifact as `UNCHANGED`,
leaving the guard inoperative.

**Resolution 3:** `repository._snapshot_artifact` now tests
`& stat.S_IXUSR` (owner execute). The two test-helper `_is_executable`
functions aligned to `S_IXUSR` for the same precision (result unchanged
for the `0o755`/`0o644` files they check). +2 regression tests:
`test_snapshot_requires_the_owner_execute_bit` (unit) and
`test_doctor_and_update_treat_owner_execute_stripped_hook_as_broken`
(integration: `0o655` → doctor fails → update repairs → idempotent).
RED-verified by reverting the one-line change (`2 failed`); GREEN
`807 passed` full suite, `52` contract.

## Resolution 3 (revision _pending freeze_)

- Target: R-008. Scope: `src/forge_cli/adapters/repository.py`,
  `tests/unit/test_adapter_repository.py`,
  `tests/integration/test_adapter_service.py`,
  `tests/integration/test_adapter_publisher.py` (test-helper alignment),
  plus the `tdd-evidence.yml` / `verification.md` / `manifest.yml` /
  `review.md` evidence updates.
- This is the sole `src/` change since `ea01dc8`.

## Iteration 4 — Resolution Verification

_Pending. An independent Reviewer (distinct from the Implementation and
reviewer-001/002/003) re-reviews the frozen Resolution 3 revision: R-008
resolved, the `& S_IXUSR` change correct and complete, no other `src/`
delta, no regression, `resolution-003` provenance present._

## Convergence

One failed `resolution_verification` iteration to date (`review-002`,
`new_material_findings > 0`). The Convergence Limit (2 consecutive scoped
Resolution Verifications) has not been reached.
