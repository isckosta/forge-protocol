---
forge:
  artifact: verification
  schema: 1
change: CHG-0015
status: complete
---
# Verification — CHG-0015

## Test evidence

- `pytest -q` (full suite): **423 passed, 0 failed** — up from the
  pre-Implementation baseline of 407 recorded in `plan.md`
  (commit `f41f45e`), matching the 16 new tests in
  `tests/unit/test_delegated_authority.py` exactly.
- `forge validate`: **"Forge project is valid"** (exit 0).
- `forge doctor`: all checks `PASS` (`git_available`, `git_repository`,
  `forge_initialized`, `project_configuration`, `protocol_compatibility`,
  `canonical_flows`, `canonical_contract`).
- Direct `jsonschema.Draft202012Validator` validation performed against:
  this Change's own `manifest.yml` (against `change-v2.schema.json`),
  `traceability.yml` (against `traceability.schema.json`), `tdd-evidence.yml`
  (against `tdd-evidence.schema.json`), and
  `protocol/schemas/execution-provenance-v2.schema.json` itself (schema
  well-formedness, via `jsonschema.Draft202012Validator.check_schema`) —
  none of these reused `forge validate` alone as proof of schema
  conformance, per this repository's own established convention
  (`CHG-0014` Strict Review; `CHG-0013` knowledge-capture.md's own note
  that `forge validate` does not JSON-Schema-validate `manifest.yml`
  directly).
- `tests/contract/` suite specifically (schema/catalog conformance): 35
  passed, run standalone before Contract/schema edits began and again
  after, confirming the new `forge/execution-provenance@2` schema file is
  picked up by the existing generic catalog-driven validation without
  bespoke test additions.

## TDD discipline: no ordering deviation this time

Unlike `CHG-0013`'s own disclosed TDD-ordering deviation
(`knowledge-capture.md`'s own entry on it), this Change's RED preceded its
GREEN in real chronological order: `tests/unit/test_delegated_authority.py`
was written and run against the unmodified validator first (commit
`0b788de`'s own message records the literal pytest failure text for each
of the 9 genuinely-RED cycles), and only then were
`_delegated_execution_effect`/`_validate_delegated_authority`/etc.
implemented. This is recorded as a positive finding, not asserted without
evidence: the exact `AssertionError` text for each RED cycle is preserved
in `tdd-evidence.yml`.

## What worked

- `_reviewable_workspace_delta`'s Git-native diffing primitives
  (`_diff_paths`, `_untracked_paths`, `_review_control_metadata_paths`,
  `_git_exists`) needed zero modification and composed directly into the
  new `_delegated_execution_effect` — the reuse Architecture planned for
  actually held up against real fixture-repo tests, not only on paper.
- `_committed_history_mappings` (the machinery underlying C-026's "first
  committed representation is authority" rule) was directly reusable for
  an entirely different purpose (self-authorization) once the specific
  acceptance-check coupling to `_record_fields` was identified and
  isolated into its own narrower sibling function.

## What required correction during Implementation itself

Two genuine design defects were found by writing and running real
fixture-repo tests, not by re-reading `architecture.md` — both already
disclosed in detail in `architecture.md`'s own revision history and
`knowledge-capture.md`, referenced here for completeness rather than
repeated:

1. The review-control-metadata exclusion question was corrected twice
   (commits `d1ec5e8`, `c7ffb47`) before RED was even written — the second
   correction was itself found while *designing* the fixture-repo test
   helpers, before the test file was complete.
2. `_first_committed_provenance_record` was found unreusable for
   self-authorization *after* RED was written and the first GREEN attempt
   was run against it — `test_self_authorization_rewriting_own_scope`
   failed with `C-065` instead of the expected `C-062`, which is what
   surfaced the `_record_fields` role-set incompatibility. Fixed within
   the same commit (`0b788de`) with `_deleg_first_committed_scope`.

Neither correction was concealed or retroactively smoothed over in
`architecture.md`; both remain visible in that document's own text as
"found while writing GREEN" / "found while writing Test Strategy," and
both are recorded again in `knowledge-capture.md` as general lessons.

## What was confusing

- Distinguishing "the delegate's Observed Effect" from "the delegating
  Execution's own bookkeeping write of the delegate's provenance record"
  is easy to get backwards on first read: both are, mechanically, just
  paths that changed in the working tree relative to a baseline. The
  distinction is not visible from a path-diff at all — it requires the
  self-authorization check to compare *content* against *history*
  instead. Writing the TDD-003 (incident) and TDD-006 (self-authorization)
  fixtures side by side, deliberately, was what made this clear enough to
  fix; reading `architecture.md`'s prose description alone was not.

## Not yet independently verified

Per Protocol 2 §2/C-026, this session cannot perform this Change's own
Strict Review — self-review is impossible by construction. This Change
stops at Verification, freezes the reviewable subject
(`provenance.yml`'s `implementation-001` record, commit `db814b7`), and
hands off to an independent Execution/Context for Strict Review. See the
final message of this session for the exact next step.
