---
forge:
  artifact: test_design
  schema: 1
change: CHG-0022
status: approved
---

# Test Design — Change Scaffolding CLI

## Objective

Prove the command's externally visible behavior, schema validity, Flow-derived
artifact selection, plan-before-mutation ordering, collision safety, and
installed-wheel locality. Every executable requirement uses a real RED →
GREEN → REFACTOR cycle. Metadata-only regression checks are recorded as
compatibility guards when they do not have a meaningful pre-fix RED.

## Strategy

Use a focused unit module for slug/numbering and template rendering, a CLI
module using `typer.testing.CliRunner` for command behavior, a contract test
for generated manifests/frontmatter, and the existing distribution probe for
the wheel boundary. Temporary repositories are initialized with real Git and
Forge workspace state; no production filesystem calls are mocked when the
behavior under test is filesystem mutation.

## TDD-001 — Runtime ID allocation and slug validation (FR-002)

**RED:** import the planned `ChangeScaffold`/numbering API before it exists;
pytest must fail during collection with the missing-symbol error.

**GREEN:** implement the smallest pure helper that scans canonical immediate
Change directories, returns the next number, and rejects invalid slugs.

**Cases:** empty/uppercase/Unicode/underscore/path-traversal/consecutive-
hyphen/leading-hyphen/trailing-hyphen slugs reject; digits and single hyphens
are accepted; gaps are ignored; the highest valid number advances; malformed
directory names do not control allocation; a four-digit minimum is preserved
for low numbers.

## TDD-002 — Flow-derived FAST, STANDARD, and FULL templates (FR-003–FR-005)

**RED:** call the planned renderer with parsed canonical Flow data and assert
the required artifact names/frontmatter/headings; pytest must fail because the
renderer does not exist.

**GREEN:** add a data-driven stage-to-artifact template map and render only
the selected Flow's required stages. Assert exact relative path sets for
FAST and STANDARD include `test-design.md` by default; FULL omits it because
the canonical FULL Flow has no `test_design` stage. For all three Flows assert
the full
behavioral/non-behavioral truth table and that
`tdd-evidence.yml` is present with `active`/zero cycles when behavioral and
absent with manifest `not_applicable` when non-behavioral. Validate all YAML
output with PyYAML. The
initial TDD evidence uses schema-valid `status: active`, `cycle_count: 0`,
and `cycles: []`; `pending` is not a permitted tdd-evidence status.

## TDD-003 — Schema-valid pending manifest (FR-006)

**RED:** load the generated manifest and run the existing schema validator;
the test must fail before the manifest renderer exists.

**GREEN:** render `forge/change@2` with `review.iteration: 0`,
`iterations: []`, pending states, and no Decisions. Assert schema validity
and exact pending values. Also assert the exact title transformation and
manifest markers for `documentation_impact`, `documentation`, conditional
`tdd_evidence`, and `completion`.

## TDD-004 — CLI wiring and plan-before-mutation (FR-001, FR-007)

**RED:** invoke `runner.invoke(app, ["change", "new", "sample-change"])`
against a temporary initialized project; pytest must fail because the
subcommand is not registered.

**GREEN:** register `change_app`, resolve the project root, render a plan,
print every CREATE line, then call a publication seam. The seam asserts the
target does not exist after plan emission and before publication, and that
the changes root has no new temporary sibling. The command then publishes the
complete set and the target exists after success. The test compares a
pre-command snapshot mapping every existing non-Git workspace path, including
unrelated files outside `.forge/changes/`, to its bytes with the snapshot
captured at the publication seam, proving no mutation preceded plan output.
The same byte snapshot is asserted unchanged for invalid configuration,
unsupported Protocol, invalid slug, unsafe path, collision,
publication-failure, packaged-resource failure, Git, environment, and
initialization cases.

## TDD-005 — Collision and failure atomicity (FR-007, INV-001)

**RED:** create a target collision and assert the command returns the domain
error while existing bytes remain unchanged; the new behavior must fail before
implementation.

**GREEN:** preflight every destination, render every byte in memory, invoke a
testable `before_claim` seam, claim the target with exclusive directory
creation, and create each file with exclusive `x` mode. On any write failure,
remove only files created by this invocation and remove the claimed directory
only when it is empty.
The test seam creates the target after plan emission and before the claim;
the command must report a collision and preserve the injected bytes. A second
test injects a failure while writing file N and asserts the final target and
all temporary siblings are absent while unrelated pre-existing files remain
byte-for-byte unchanged. Additional CLI cases cover missing, malformed, and
disabled default Flows, unknown canonical Flow references, unsupported
Protocol, missing initialization, and Git/environment failures, all with the
same byte-snapshot assertion and exact error codes; a rollback test injects
concurrent content before cleanup
and asserts it is preserved while `E_FORGE_CHANGE_ROLLBACK_INCOMPLETE` is
returned, with the same full workspace byte snapshot. A separate injected
failure with successful cleanup asserts
`E_FORGE_CHANGE_PUBLICATION` and an absent target.

## TDD-006 — Installed wheel and offline locality (FR-008)

**RED:** extend `tests/integration/test_adapter_distribution.py` and its
`tests/integration/adapter_cli_wheel_probe.py` helper to invoke `forge change new` in a
clean temporary repository; the probe must fail because the installed wheel
has no command.

**GREEN:** build/install through the existing offline verification path and
assert the same Flow-derived filenames and valid manifest without network or
source-checkout access.

## TDD-007 — Documentation and roadmap regression (FR-009)

**RED:** add assertions for the README command text, CHANGELOG entry, and
roadmap status/link; run before documentation edits and observe failures.

**GREEN:** update only the requested documentation and item #2. Assert that
items #3–#10 remain unchanged.

## Non-mechanical Validation

Manual Review must confirm that generated prose is useful, that the command
does not imply it executed a lifecycle stage, and that the selected Flow
classification remains proportional. No prose snapshot substitutes for the
executable checks above.

## Completion Criteria

- TDD-001 through TDD-007 have honest RED/GREEN evidence.
- AC-001 through AC-008 are traceable to tests or explicit Review evidence.
- The full suite, `forge validate`, `forge doctor`, and wheel probe pass after
  final evidence assembly.
- Independent Strict Review passes with no unresolved blocking Finding.
