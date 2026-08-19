---
forge:
  artifact: test_design
  schema: 1
change: CHG-0014
status: complete
---

# Test Design — CHG-0014

## Scope

Three code changes to `forge-protocol` itself (FR-001, FR-002, FR-003) are
reasonably testable executable behavioral changes and therefore follow real
TDD (C-008/C-009/C-010), each as its own cycle. The example fixture's
username-length rule (FR-004) is *also* reasonably testable and *also*
follows real TDD, but as the subject the Layer B test drives programmatically
rather than as a cycle authored ahead of time by this session — its RED must
be produced live, inside the Layer B test, against the fixture, or it would
not be evidence of the Golden Path actually working (a canned/pre-baked RED
would only prove this session can write fixtures, not that the mechanism
holds).

## TDD cycles (this Change's own Implementation)

### TDD-001A — Codex gate instructions include the full completion-gate set (FR-003)

- Behavior: `_gate_instructions` emits a line for
  `documentation_impact_evaluated`, `required_documentation_updated`, and
  `tdd_compliant_or_explicitly_excepted` when present in a Flow's
  `gates.before_completion.require`.
- RED: extend `tests/unit/test_codex_projection_gates.py` (existing module
  covering this function) with an assertion that the rendered gate section
  for `standard`/`fast`/`full` contains text for all three previously-missing
  checks. Run before touching `projection.py`; expect failure because the
  current `_gate_instructions` body has no branch for them.
- GREEN: add the three `if` branches to `_gate_instructions`, minimal text,
  no restructuring.
- REFACTOR: none anticipated; the function is already a flat, additive
  `if`-chain.

### TDD-001B — Codex gate instructions state the pre-Implementation boundary (FR-003)

- Behavior: `_gate_instructions` also reads `gates.before_implementation`
  when present (STANDARD and FULL both declare one; FAST does not, and must
  not have one fabricated for it) and emits an instruction that
  Implementation must not begin until that gate's `require` list is
  satisfied.
- RED: same test module, a new assertion per Flow that the rendered section
  states the pre-Implementation precondition, naming at minimum
  `specification_complete` (STANDARD) or `architecture_complete` (FULL), and
  a separate assertion that a Flow with no `before_implementation` key (FAST)
  renders no such line. Run first; expect failure, since `_gate_instructions`
  today never reads `before_implementation` at all (confirmed directly
  against `projection.py:92-124` in `discovery.md` — not inferred).
- GREEN: read `gates.get("before_implementation")` when present and render
  its `require` list as a single "Implementation MUST NOT begin until: ..."
  instruction line. No fallback to `before_architecture`: that gate governs
  entry to FULL's Architecture stage, not entry to Implementation, and
  representing it would conflate two different boundaries.
- REFACTOR: none anticipated.

### TDD-002 — `forge adapter install` prints a success/next-step message (FR-002)

- Behavior: on `result.mutated is True`, `install()` in `adapter_cli.py`
  prints a line after the plan output naming the resolved target and the
  next action.
- RED: extend `tests/cli/test_adapter_commands.py` with an assertion on a
  fresh install's `stdout` for the new confirmation line; also assert the
  *existing* "No changes required." branch is unchanged for a no-op
  reinstall. Run first; expect failure (no such line exists yet).
- GREEN: add the `else` branch printing the confirmation message, sourced
  from `planned.plan`'s resolved target.
- REFACTOR: none anticipated.

### TDD-003 — `forge doctor` aggregates installed-Adapter diagnostics (FR-001)

- Behavior: `diagnose()` in `doctor/__init__.py`, after its existing checks,
  iterates packaged Adapters with an installation record present and merges
  each `AdapterService.doctor(...)` check into its own result, id-prefixed
  `adapter:<id>:<check>`; overall `passed` reflects them.
- RED: extend `tests/unit/test_doctor_diagnostics.py` (calls
  `doctor.diagnose()` directly) with two cases: (a) no installed Adapter →
  behavior unchanged from today; (b) Codex Adapter installed and then
  drifted → `diagnose()`'s result fails and names the drifted check. Run
  first against the unmodified `diagnose()`; expect case (b) to fail because
  no Adapter checks are aggregated at all yet. Also extend
  `tests/cli/test_doctor.py` (`CliRunner` against `app`) with one case
  confirming the CLI exit code surfaces an aggregated Adapter failure.
- GREEN: add the aggregation loop, reusing `build_packaged_registry`,
  `load_optional_installation_record`, and `AdapterService.doctor` exactly
  as `adapter_cli.py`'s existing `list`/`doctor` commands already do — no
  new diagnostic logic invented.
- REFACTOR: none anticipated.

## Layer B TDD (executed live by the Layer B test, FR-007)

The Layer B automated test constructs, inside a disposable temp copy of
`examples/golden-path-standard/starter/`, the following real TDD cycle as
part of proving FR-007, by literally invoking `pytest` as a subprocess at
each step and inspecting its result (not simulating outcomes):

1. Run the fixture's existing test suite against `starter/` unmodified →
   must pass (a true baseline, FR-004).
2. Write a new test asserting the username-length rule → run it → must fail,
   and the failure must be attributable to the missing rule (an assertion
   failure on the new test, not a collection error, import error, or
   unrelated failure) — this is the RED the constructed Change's
   `tdd-evidence.yml` will honestly record as `red: {observed: true}`.
3. Implement the minimal rule → rerun → the new test and the full suite both
   pass (GREEN).
4. Assert no other pre-existing test needed to change.

The test then asserts the constructed Change's own `manifest.yml`/`tdd-
evidence.yml` accurately describe exactly this sequence, and that `forge
validate` accepts the result — proving both that the mechanism produces a
correct outcome and that the record it produces is truthful, per this
Change's own honesty standard (`discovery.md`).

## Test level mapping

| Requirement | Level | Location |
| --- | --- | --- |
| FR-001 | Layer A (new unit/CLI test) | `tests/cli/test_doctor.py` or `tests/unit/test_doctor_diagnostics.py` |
| FR-002 | Layer A (new CLI test) | `tests/cli/test_adapter_commands.py` |
| FR-003 | Layer A (existing unit module, extended) | `tests/unit/test_codex_projection_gates.py` |
| FR-004 | Fixture content | `examples/golden-path-standard/starter/` |
| FR-006 | Layer A integration | new test under `tests/integration/` or `tests/golden_path/` (see `plan.md`) |
| FR-007, FR-008 | Layer B integration | same new test module, second test function |
| FR-009 | Layer C, manual | `examples/golden-path-standard/README.md`, executed by a human operator |
| FR-005, AC-5 | Manual, executed once by this session during Verification | `docs/getting-started.md` |

No Layer C assertion is encoded as an automated test. No test in this
Change asserts on Codex's exact generated prose beyond the specific,
already-mechanical properties FR-003/AC-3 name (presence of specific gate
check identifiers' instruction text), consistent with the originating
brief's explicit prohibition on conversation-snapshot/exact-wording testing.
