---
forge:
  artifact: verification
  schema: 1
change: CHG-0014
status: complete
---

# Verification — CHG-0014

## Commands run and results

All commands below were run directly by this session against this
repository's working tree from `/home/isckosta/forge-protocol` unless noted
otherwise.

- `python -m pytest tests/unit/test_codex_projection_gates.py -v` — RED (2
  failed / 9 passed), then GREEN (11 passed) after TDD-001A/TDD-001B.
- `python -m pytest tests/cli/test_adapter_commands.py -v` — RED (1 failed /
  2 new passed / 18 pre-existing passed), then GREEN (21 passed) after
  TDD-002.
- `python -m pytest tests/unit/test_doctor_diagnostics.py -v` — RED (2
  failed / 5 passed), then GREEN (7 passed) after TDD-003.
- `python -m pytest tests/cli/test_doctor.py -v` — 3 passed (the new
  CLI-level assertion passed immediately; see `tdd-evidence.yml` TDD-003
  notes for why that's disclosed rather than claimed as its own RED).
- `python -m pytest tests/golden_path/ -v` — 2 passed
  (`test_readiness_sequence_surfaces_adapter_install_and_health`,
  `test_golden_path_produces_a_valid_standard_change`), including a live,
  real `pytest` subprocess RED and GREEN inside the second test against a
  disposable copy of `examples/golden-path-standard/starter/`.
- `python -m pytest tests/ -q` — **406 passed**, 0 failed, 0 skipped. This
  is the full existing suite (397 before this Change's Layer A test
  additions) plus this Change's 9 new unit/CLI tests plus 2 new
  `tests/golden_path/` tests, with no regression to any pre-existing
  assertion (CON-001).
- `forge validate` (against this repository itself) — `Forge project is
  valid`, exit 0.
- `forge doctor` (against this repository itself) — all 7 checks `PASS`,
  exit 0; no `adapter:` checks appear, confirming CON-001 (this repository
  has no installed Adapter of its own, so the new aggregation adds nothing
  here — see `discovery.md`/`intent.md` Non-goals on why that's correct,
  not a gap).
- Manual walkthrough of `docs/getting-started.md` steps 2–4
  (`forge init`, `forge adapter install codex`, `forge doctor`) against a
  throwaway `mktemp -d` repository — reproduced exactly as documented,
  confirmation message and full Adapter-scoped `PASS` set observed, exit 0
  (AC-5). Steps 1 (install) and 5–7 (Codex-side) are not executable by this
  session; see Product findings and `examples/golden-path-standard/README.md`.

No lint, type-check, or formatting tool is configured for this repository
(`pyproject.toml` declares no `ruff`/`mypy`/`black`/equivalent tool
section, confirmed directly), so none was run; this matches every prior
Change's own Verification in this repository.

## Requirements traceability

| Requirement | Verified by |
| --- | --- |
| FR-001 | `tests/unit/test_doctor_diagnostics.py`, `tests/cli/test_doctor.py`, `tests/golden_path/test_golden_path_standard.py` |
| FR-002 | `tests/cli/test_adapter_commands.py`, `tests/golden_path/test_golden_path_standard.py` |
| FR-003 | `tests/unit/test_codex_projection_gates.py`, manual SKILL.md inspection below |
| FR-004 | `examples/golden-path-standard/starter/` itself; baseline asserted by `tests/golden_path/test_golden_path_standard.py` |
| FR-005, AC-5 | Manual walkthrough (above) |
| FR-006 | `tests/golden_path/test_golden_path_standard.py::test_readiness_sequence_surfaces_adapter_install_and_health` |
| FR-007, FR-008 | `tests/golden_path/test_golden_path_standard.py::test_golden_path_produces_a_valid_standard_change` |
| FR-009 | `examples/golden-path-standard/README.md` (content review, not executed — Layer C requires a real Codex session) |
| NFR-001 | `pyproject.toml` diff: no new `[project] dependencies` entry (unchanged) |
| NFR-002 | `adapter_cli.py`/`app.py` diff: no new Typer command registered |
| CON-001 | `forge doctor`/`forge validate` against this repository (above); `test_doctor_adds_no_adapter_checks_when_none_installed` |
| CON-002 | no file under `protocol/` touched by this Change (`git diff --name-only` reviewed) |

Manual confirmation that `SKILL.md`'s `standard` gate section states the
pre-Implementation boundary and the three previously-missing completion
checks, generated fresh in a throwaway repository:

```text
### Flow `standard` gate obligations

- Implementation MUST NOT begin until: intent_present, discovery_complete, specification_complete, specification_gate_passed, plan_complete.
- RED must be executed.
- RED must fail for the expected reason.
- Completion requires Verification to pass.
- Completion requires Strict Review to pass.
- Completion requires all blocking review threads on any active external review surface to be resolved.
- Completion requires Documentation Impact to be evaluated.
- Completion requires required documentation to be updated.
- Completion requires TDD compliance or an explicit, recorded exception.
```

## Product findings

### Blocking for this Change (all resolved)

None remain open. The two onboarding-UX gaps and the pre-Implementation
projection gap named in `intent.md`/`discovery.md` were all closed and
verified above.

### Non-blocking, recorded for follow-up

1. **Conformance checking is gate-name-level, not gate-instruction-text-level**
   (`discovery.md` §Verified onboarding-UX gaps). `forge adapter doctor
   codex` can report `PASS conformance` even if a future edit to
   `_gate_instructions` silently dropped an individual completion check
   again, because `validate_conformance`/`ConformanceRequirements` only
   check that a `gates` key (e.g. `before_completion`) is present, not that
   every entry under its `require` list has corresponding instruction text.
   This Change closes the two concrete instances found but does not add
   general protection against the class recurring. **Future conformance
   candidate.**
2. **`before_architecture` (FULL) remains unrepresented** in generated
   Codex instructions. Out of scope: it gates entry to FULL's Architecture
   stage, not entry to Implementation, and FULL Golden Paths are explicitly
   out of scope for this Change. **Future Golden Path (FULL) candidate.**
3. **No mechanically-enforced human-approval Gate exists** between Plan and
   Implementation in canonical Protocol today (`discovery.md` §The
   Plan→Implementation human-approval boundary). This Change represents the
   boundary (in generated Codex instructions and in `docs/
   getting-started.md`'s explicit "Known limitation" note) and models it as
   this session's own conduct, but cannot make Core mechanically enforce
   it without a Contract-level change this Change's own scope excludes.
   **Future Protocol candidate** — would need its own FULL-flow Change with
   `protocol/compatibility.md` analysis of whether it can be additive
   (e.g., an optional-but-checked field) or requires a new integer Protocol
   identifier.
4. **`forge adapter install`'s capability-limitation `WARN` lines print
   before the new success confirmation**, in the same undifferentiated
   stdout stream as the plan's `CREATE`/`UPDATE` operation lines. A
   first-time reader may not immediately parse `WARN
   strict-review: capability skills cannot be enforced` as "this is
   expected and not an error." Non-blocking: the message is accurate and
   the new confirmation line still appears last and is unambiguous; a
   future UX pass could visually separate plan/warning/confirmation
   sections. **Future usability polish candidate**, not filed as a defect.
5. **`forge validate` performs no JSON Schema validation of `manifest.yml`
   / `tdd-evidence.yml` / `provenance.yml` against `protocol/schemas/*`**
   (`discovery.md`, independently confirmed by reading all 489 lines of
   `validation/__init__.py`). Schema conformance is only proven for this
   repository's own artifacts by `tests/contract/test_protocol_contract.py`
   at CI time; a real user's project gets no live protection against a
   malformed Change manifest passing `forge validate`. Pre-existing, well
   outside this Change's narrow scope, but directly relevant to anyone
   extending the Golden Path's Layer B checks later — which is why this
   Change's own Layer B test additionally validates directly against the
   JSON Schema rather than trusting `forge validate` alone. **Future Core
   validation candidate.**

### What worked

- CHG-0010's existing wheel/subprocess probe infrastructure needed zero
  changes and required no new parallel harness to extend Layer A coverage.
- `AdapterService.doctor`'s existing per-Adapter diagnostics were reusable
  as-is for the new top-level aggregation — no new diagnostic logic, only
  composition.
- The example fixture's minimal scope (one function, one rule, stdlib +
  pytest only) kept the Layer B test's real subprocess RED/GREEN cycle fast
  (whole suite: ~30s) and legible.

### What required manual intervention

- A research subagent, despite an explicit read-only instruction, wrote to
  this Change's `intent.md` directly mid-investigation. It was stopped and
  the file was rewritten from scratch by this session (`discovery.md` §Note
  on this Discovery's own process). Not a Golden Path finding in the
  product sense (it did not involve Codex or the Adapter), but recorded
  here for completeness since it affected how this Change's own record was
  produced.
- This Plan's initial assumption that the example fixture could use
  Protocol 1 was wrong (`forge init` always writes `protocol: 2`); caught
  and corrected during Implementation rather than discovered later (see
  `plan.md`'s revision note).

### What was confusing

- `AdapterMutationResult.mutated` and `dry_run` interact non-obviously on
  first read (`dry_run=True` always forces `mutated=False`, regardless of
  what a real run would do) — correct and necessary for FR-002's dry-run
  exclusion, but easy to get backwards without reading `AdapterService.
  install` directly, which this session did before writing TDD-002
  (`discovery.md`/this Change's own investigation notes).

### What failed

Nothing, in the sense of a defect surviving to this point: every RED
observed in this Change's own Implementation (`tdd-evidence.yml`) resolved
to a passing GREEN, and no test was left failing.

## Layer C — not executed by this session

This session has no Codex tool access. `examples/golden-path-standard/
README.md`'s manual acceptance procedure is written and ready but has not
been run against a real Codex session. This is disclosed, not hidden: FR-009
and AC-7 require the procedure to *exist* and be behaviorally specified, not
that this session executes it. Running it is recommended as the first
action after this Change's Strict Review passes.
