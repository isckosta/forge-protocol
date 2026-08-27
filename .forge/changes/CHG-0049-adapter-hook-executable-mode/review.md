---
forge:
  artifact: review
  schema: 1
change: CHG-0049
status: in_progress
---

# Review — CHG-0049 Adapter Hook Executable Mode

## Verdict

**Iteration 1 (initial review, `standard` profile): REQUEST CHANGES** — 1
BLOCKER (R-001), 1 MAJOR (R-002), 1 MINOR (R-003). All three resolved in
Resolution 1. Iteration 2 (Resolution Verification): _pending independent
re-review of the Resolution revision._

The Reviewer independently reproduced the entire end-to-end behaviour
(materialize → execute hook → break → doctor fails → update repairs →
idempotent) and audited every touched module for correctness, finding no
code-correctness defect within scope. The blocking findings were both in
the Change's own evidence artifacts, not its code.

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

**Resolution:** cycle ids renamed `TDD-001..TDD-005` (and the two prose
back-references in `tdd-evidence.yml` and the one in `verification.md`).
Full suite re-run → **805 passed**; contract suite → **52 passed**.

### R-002 · MAJOR · verification.md misrepresented the test evidence

`verification.md` asserted Result **PASS** with "805 passed / 52 contract
passed"; `manifest.yml` recorded `verification.status: passed`. The real
figures at `ea01dc8` were 804/1-fail and 51/1-fail (the 805/52 were the
*collected* counts). Root cause: the full suite was run before
`tdd-evidence.yml` was finalized with the invalid ids, and not re-run
before the freeze.

**Resolution:** `verification.md` Test Evidence, Forge Evidence, and
Conclusion sections corrected to state the frozen-subject failure
explicitly and to attribute the 805/52 figures to the post-Resolution
run. Verification result re-affirmed **PASS against the Resolution
revision**, not the frozen subject.

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

## Resolution 1

- Targets: R-001, R-002, R-003.
- Scope (evidence artifacts only — no source-code change):
  `.forge/changes/CHG-0049-adapter-hook-executable-mode/tdd-evidence.yml`,
  `.forge/changes/CHG-0049-adapter-hook-executable-mode/verification.md`,
  `.forge/changes/CHG-0049-adapter-hook-executable-mode/manifest.yml`,
  `.forge/changes/CHG-0049-adapter-hook-executable-mode/review.md`.
- Post-Resolution evidence: `pytest -q` → 805 passed, 2 (pre-existing)
  warnings; `pytest tests/contract -q` → 52 passed; `forge validate` →
  valid.
- No source file, no test file, and no behaviour changed between `ea01dc8`
  and the Resolution revision — the R-001 failure was entirely a
  schema-invalid identifier string in one YAML file.

## Iteration 2 — Resolution Verification

_Pending. An independent Reviewer (distinct execution and context from
both the Implementation and reviewer-001) must re-review the frozen
Resolution revision and confirm R-001/R-002/R-003 are resolved with no
regression and no out-of-scope mutation._
