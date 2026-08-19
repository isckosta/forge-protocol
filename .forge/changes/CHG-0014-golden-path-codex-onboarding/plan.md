---
forge:
  artifact: plan
  schema: 1
change: CHG-0014
status: complete
---

# Plan — CHG-0014

## Implementation plan

### 1. `src/forge_cli/adapters/codex/projection.py` (FR-003, TDD-001A/TDD-001B)

- `_gate_instructions`: add branches for `documentation_impact_evaluated`,
  `required_documentation_updated`, `tdd_compliant_or_explicitly_excepted`
  (completion side) and a new pre-Implementation branch reading
  `gates.get("before_implementation")` when present, rendering its
  `require` list as one instruction line. No fallback to
  `before_architecture` (a different, earlier boundary — `discovery.md`).
  Pure function, no new parameters, no signature change.

### 2. `src/forge_cli/adapter_cli.py` (FR-002, TDD-002)

- `install()`: after `service.install(...)`, branch on `result.mutated`;
  when `True`, print a confirmation line naming the resolved target
  (`planned.plan`'s target — already computed) and stating the next action
  (open the installed Harness). Existing `if not result.mutated` branch is
  unchanged.

### 3. `src/forge_cli/doctor/__init__.py` (FR-001, TDD-003)

- `diagnose()`: after existing checks, if the project is initialized and
  configuration is valid, build the packaged Adapter registry
  (`build_packaged_registry`, already used by `adapter_cli.py`), and for
  each Adapter with `load_optional_installation_record(...) is not None`,
  call `AdapterService(registry).doctor(project_root, adapter_id)` and fold
  each returned `AdapterCheck` into `DoctorResult.checks` with id
  `adapter:<adapter_id>:<check.id>`, preserving `check.status`/`message`.
  No installed Adapter → no new checks appended (CON-001).
- `app.py`'s `doctor()` command needs no change: it already iterates
  `result.checks` generically and already fails on any `"failed"` status.

### 4. `examples/golden-path-standard/starter/` (FR-004)

- `pyproject.toml` (or a flat `src/` + `tests/` with no build backend —
  decided below) minimal Python package.
- `src/accounts/users.py`: `def create_username(name: str) -> str` that
  currently accepts any non-empty string (existing baseline behavior).
- `tests/test_users.py`: existing passing tests for the current behavior
  (non-empty check only) — the true "before" baseline (FR-004, AC-4).
- No `.forge/` in `starter/`: it is deliberately an un-initialized
  repository, matching Golden Path step 1.
- No build backend/packaging metadata beyond what `pytest` needs to collect
  the package (a `pyproject.toml` with `[tool.pytest.ini_options]` and
  `pythonpath`, no `[build-system]`) — avoids a real installable package for
  a fixture that is never published, per NFR-001 and the brief's "avoid
  heavy dependency" guidance (§18).

### 5. `docs/getting-started.md` (FR-005, FR-008)

Outline: Prerequisites → Install Forge → `forge init` → Install the Codex
Adapter (`forge adapter install codex`) → Confirm readiness (`forge doctor`)
→ Open Codex → Request a Change in natural language → What happens next
(Flow classification, Discovery/Specification/Plan, **explicit stop for your
approval before Implementation — currently a documented practice, not yet a
mechanically enforced Gate; see Known limitations**) → TDD/Verification/
Review/Completion, briefly → Where to go deeper (links to
`ARCHITECTURE.md`, `protocol/specification.md`, this Change). A short "Known
limitations" section states the Plan→Implementation boundary is
represented, not enforced (honest per `discovery.md`).

### 6. `examples/golden-path-standard/README.md` (FR-009)

Manual acceptance procedure per FR-009/AC-7: preconditions, starting state,
install steps, Codex-opening step, the exact natural-language request to
give Codex ("add a rule to `create_username` in `src/accounts/users.py`
rejecting usernames shorter than three characters"), expected behavioral
milestones (Flow classification observed; Discovery/Specification/Plan
artifacts appear; session stops and asks for approval before writing
production code; RED observed before GREEN; Verification recorded; Strict
Review recorded — or, under Protocol 2, the session names the independent-
review handoff instead of self-reviewing), explicit failure conditions
(brief §25, verbatim list adapted), and evidence to inspect at each
milestone (`.forge/changes/<id>/*` in the fixture's own initialized copy).

### 7. Layer A/B automated test (FR-006, FR-007, FR-008)

New module `tests/golden_path/test_golden_path_standard.py` (new
`tests/golden_path/` package, `__init__.py` only if needed for discovery —
`pyproject.toml`'s `testpaths = ["tests"]` already covers any subdirectory,
confirmed against `pyproject.toml:33`, no config change needed):

- `test_readiness_sequence_surfaces_adapter_install_and_health` (Layer A, FR-001/002):
  temp Git repo, source-tree `forge` invocation (via `typer.testing.
  CliRunner` against `forge_cli.app.app`, matching `tests/cli/*` convention)
  → `init` → assert plain `doctor` unchanged with no Adapter → `adapter
  install codex` → assert confirmation message present → `doctor` → assert
  Adapter-scoped PASS lines present and exit 0 → drift the installed
  `SKILL.md` → `doctor` → assert Adapter-scoped FAIL line present and exit
  code 2.
- `test_golden_path_produces_a_valid_standard_change` (Layer B, FR-007/008):
  copies `examples/golden-path-standard/starter/` into a temp Git repo,
  `forge init`, then programmatically performs the Test Design's Layer-B TDD
  sequence (real `pytest` subprocess calls) against the copied fixture,
  authors a minimal but real `.forge/changes/CHG-0001-.../` artifact set
  (`intent.md`, `discovery.md`, `specification.md`, `plan.md`,
  `test-design.md`, `tdd-evidence.yml`, `manifest.yml`) reflecting exactly
  what the subprocess calls observed, asserts (via `git merge-base
  --is-ancestor`) that the Plan commit precedes the RED commit and the RED
  commit precedes the Implementation commit, then runs `forge validate`
  against the fixture repo and asserts exit 0, plus a direct JSON Schema
  check against `change-v2.schema.json`/`tdd-evidence.schema.json` (stronger
  than `forge validate` alone — `discovery.md`).

  Revised during Implementation from this Plan's original assumption: `forge
  init` unconditionally writes `protocol: 2` (`version.py::PROTOCOL_ID`), so
  the fixture is a Protocol 2 project too, not Protocol 1 as first assumed.
  Rather than downgrading it to dodge Protocol 2's independent-review
  requirement, the constructed manifest honestly leaves `review.status:
  pending` with an empty `iterations: []` — which `forge validate` accepts
  cleanly (`_validate_protocol2_review_provenance` only engages once a bound
  Review Iteration exists) and which is *more* honest: the nested example
  naturally stops at the same Verification → independent Strict Review
  boundary this Change's own Non-goals stop at, rather than being
  artificially exempted from it.

## Compatibility check

Re-confirms `specification.md` §Compatibility: every change above is
additive to existing functions/commands, touches no schema/Contract/
Protocol file, and CON-001/CON-002 hold. No `protocol/compatibility.md`
update is needed.

## Explicit approval boundary

This is the STANDARD Flow's `before_implementation` Gate
(`protocol/flows/standard.yml:33-39`: `intent_present`,
`discovery_complete`, `specification_complete`, `specification_gate_passed`,
`plan_complete`). All five are satisfied by `intent.md`, `discovery.md`,
`specification.md`, and this `plan.md`. `specification_gate_passed` here
means this Specification is internally consistent and traceable to
Discovery's evidence, which this session has checked; STANDARD does not
require a separate adversarial Specification Review stage the way FULL
does (`protocol/flows/standard.yml` has no `specification_review` stage).

As documented in `discovery.md`, Forge's canonical Protocol does not
mechanically gate STANDARD Implementation on an explicit human approval act
today. This session's own Non-goals commit to not inventing that Gate
silently. Consistent with the originating brief's §10 and §37 ("Optimize
for: ...clearer boundaries... without weakening Forge's engineering
guarantees"), this session stops here as a matter of its own conduct and
requests the user's explicit go-ahead before writing any production code,
test code, or fixture content for FR-001–FR-009.

**Plan ready. Awaiting explicit human approval before Implementation
begins.**

## Approval record

Explicit human approval received via `AskUserQuestion` ("Aprovar e
prosseguir") on 2026-08-18. Implementation begins only now, after this
record exists, matching the boundary this Plan itself asserts.
