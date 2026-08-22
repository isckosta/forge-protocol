---
forge:
  artifact: plan
  schema: 1
change: CHG-0022
status: approved
---

# Plan — Change Scaffolding CLI

1. Add pure scaffold models and helpers in
   `src/forge_cli/change_scaffolding.py`: validate the slug, scan
   `.forge/changes/`, resolve the next number, map canonical FAST, STANDARD,
   and FULL Flow stage IDs to the repository's artifact filenames, including
   FAST's conditional `test-design.md` by default, render
   Markdown frontmatter/placeholders, resolve the default project's enabled
   Flow reference, explicitly rejecting missing/malformed/disabled project
   Flow files before canonical resolution, and render the pending
   `forge/change@2` manifest plus
   schema-valid active zero-cycle TDD evidence.
2. Add `tests/unit/test_change_scaffolding.py` for slug rules, runtime
   numbering, FAST/STANDARD/FULL behavioral and non-behavioral truth-table
   path sets, deterministic title/plan ordering, and YAML/frontmatter
   validity; run TDD-001 through TDD-003 RED before adding production
   behavior.
3. Add `src/forge_cli/change_cli.py` with `change_app` and `new`; reuse the
   existing Git root/error conventions, resolve the configured default Flow,
   print deterministic `CREATE forge_owned` lines in filtered canonical stage
   order, invoke the publication seam, claim the destination with exclusive
   directory creation, and create each file with exclusive `x` mode; on
   failure remove only files created by this invocation and preserve unknown
   concurrent content.
4. Register `change_app` in `src/forge_cli/app.py` and extend
   `tests/cli/test_cli_contract.py` with help, nested-root, successful
   scaffold, invalid-input, Flow-resolution/error-matrix,
   publication-order snapshot, injected-race collision, injected file-N
   failure, and rollback cases; execute
   TDD-004/TDD-005 RED before implementation.
5. Add contract assertions for generated `forge/change@2` manifests and
   artifact frontmatter in a focused contract module, ensuring the generated
   pending review shape is schema-valid and no Decision enum is invented.
6. Extend `tests/integration/test_adapter_distribution.py` and
   `tests/integration/adapter_cli_wheel_probe.py` to invoke the new command
   in a clean temporary repository, then execute TDD-006 against the
   installed distribution.
7. Update `README.md`, `CHANGELOG.md`, and only item #2 in
   `ROADMAP-REMEDIATION.md`; add documentation assertions and execute
   TDD-007.
8. Assemble `tdd-evidence.yml`, `traceability.yml`, `verification.md`,
   `review.md`, `provenance.yml`, and `manifest.yml` from real execution
   evidence. Do not claim completion or write final PASS state before the
   final full-suite/schema validation run.
9. Run the final regression baseline after all Change-local evidence files
   exist: `.venv/bin/python -m pytest -q`, `forge validate`, `forge doctor`,
   and the installed-wheel probe. Record exact outputs and any warnings.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation until
the STANDARD `before_implementation` Gate is satisfied. Implementation-time
discoveries belong in Verification, a Decision record, or a documented
re-Plan; they must not be silently absorbed into this approved Plan.
