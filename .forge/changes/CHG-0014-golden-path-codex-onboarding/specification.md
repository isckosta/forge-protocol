---
forge:
  artifact: specification
  schema: 1
change: CHG-0014
status: complete
---

# Specification — Golden Path Baseline and Codex Onboarding Validation

## Terminology

- **Golden Path** — the canonical install-to-first-governed-Change scenario
  this Change validates: Forge install → `forge init` → Codex Adapter
  install → readiness confirmation → Codex session → natural-language
  Change request → Forge-governed STANDARD lifecycle → Completion boundary.
- **Layer A (Infrastructure)** — deterministic, CLI/Adapter-level behavior:
  package install, `forge init`, Adapter install/validate/doctor,
  idempotence, drift, offline operation. Mostly pre-proven (`discovery.md`).
- **Layer B (Repository outcome)** — deterministic, Change-artifact-level
  behavior: does a resulting Change's repository-native state
  (`manifest.yml`, TDD evidence, etc.) validate and reflect the correct
  Flow, ordering, and content.
- **Layer C (Interactive acceptance)** — non-deterministic, requires a real
  Codex session: whether Codex actually surfaces Forge semantics and
  respects the human-approval boundary. Specified behaviorally here;
  executed by a human operator, not by this session or CI.

## Functional requirements

### FR-001 — `forge doctor` reports installed-Adapter readiness

`forge doctor` (`src/forge_cli/doctor/__init__.py`) MUST, after its existing
checks, enumerate every packaged Adapter that has a repository-native
installation record (`.forge/adapters/<id>/installation.yml`) present, and
report one `AdapterDoctorResult` (via the existing
`AdapterService.doctor`) per such Adapter, each check surfaced with an
`adapter:<id>:<check-id>` id so it composes with, rather than replaces, the
plain workspace checks. `forge doctor`'s overall pass/fail and exit code
(`app.py:138-139`) MUST reflect a failing Adapter check.

A repository with **no** installed Adapter MUST see no behavior change
(FAST-reduces-ceremony-shaped: this is additive, not a new required step).
A repository whose only installed Adapter is invalid/drifted/stale MUST see
that surfaced by `forge doctor` alone, with no separate `forge adapter
doctor <id>` invocation required to learn it.

### FR-002 — `forge adapter install` confirms success and names the next step

`forge adapter install <adapter>` (`adapter_cli.py:201-221`), when it
actually mutates the repository (`result.mutated is True`), MUST print a
confirmation line after the plan/operation output, analogous in spirit to
`forge init`'s `Forge initialized at {path}` (`app.py:93`). The message MUST
name the resolved publication target and state the next action in terms a
first-time user can act on without reading Adapter internals (open the
installed Harness; no further Forge-side step is required). It MUST NOT
claim technical enforcement of Forge semantics (`ARCHITECTURE.md` §25: "these
instructions represent Forge requirements and do not claim technical
enforcement").

### FR-003 — Codex gate instructions represent the complete gate set, including the pre-Implementation boundary

`_gate_instructions` (`adapters/codex/projection.py:92-124`) MUST translate
every entry already present in each effective Flow's `gates` mapping into a
corresponding instruction line, not only the two `gates` keys it reads
today (`before_behavioral_implementation`, `before_completion`). Concretely:

- (completion side, as originally scoped) when present in the resolved
  Flow's YAML, the generated `SKILL.md` MUST state that Completion requires
  Documentation Impact evaluation (`documentation_impact_evaluated`), that
  required documentation updates are applied
  (`required_documentation_updated`), and that TDD compliance is satisfied
  or explicitly excepted (`tdd_compliant_or_explicitly_excepted`), in
  addition to the three checks already represented.
- (pre-Implementation side, found during Discovery — `discovery.md` §The
  Plan→Implementation human-approval boundary) the generated `SKILL.md`
  MUST also state, from `gates.before_implementation.require` when the
  effective Flow declares one (STANDARD and FULL; FAST has no Plan stage and
  legitimately declares none), that Implementation MUST NOT begin until the
  listed predecessor artifacts (Intent, Discovery, Specification,
  Specification Gate, Plan, or, for FULL, Architecture/Test Strategy/Tasks)
  are complete — i.e., the Plan-ready → stop → Implementation boundary
  central to this Change's own Goal must be something Codex is actually
  told, not only something canonical Flow YAML happens to encode.

This is additive text only: no existing line is removed, no capability
boolean, manifest field, or Adapter version changes (`discovery.md` §Scope
decisions). It does **not** introduce a mechanically-enforced human-approval
Gate (`discovery.md` explains why that is out of scope); it makes an
already-declared artifact-completeness precondition visible to Codex, the
same way FR-003's completion-side half does.

### FR-004 — Example fixture exists and is self-contained

`examples/golden-path-standard/` MUST contain a minimal starter fixture
(`starter/`) that: has no Forge workspace of its own (a genuinely fresh
repository, matching the Golden Path's first lifecycle step); contains a
single small Python module with one currently-missing behavioral rule
(username length validation, see `test-design.md`); has an existing passing
test suite that says nothing about the missing rule (a true baseline, not a
pre-broken one); and has no external runtime dependency beyond the Python
standard library and `pytest`.

### FR-005 — `docs/getting-started.md` is sufficient standalone

`docs/getting-started.md` MUST let a reader reach "Codex is ready to receive
a Change request" using only: this document, `README.md`'s existing install
instructions, and CLI `--help`/output text. It MUST NOT require reading
`ARCHITECTURE.md`, `protocol/specification.md`, `protocol/contract/*`,
Adapter internals, or Change schemas first (may link to them as optional
deeper reading). It MUST NOT instruct the reader to copy an internal prompt,
hand-edit a generated Adapter file, or manually paste Forge instructions
into Codex (originating brief §11, §17).

### FR-006 — Layer A: readiness aggregation is deterministically verified

An automated test MUST prove FR-001 and FR-002 end-to-end from a fresh
temporary Git repository through the real `forge` CLI (source-tree
invocation is sufficient for this new surface; FR-001/FR-002/FR-003 do not
need a fresh wheel-probe pass because CHG-0010's existing wheel probe
already proves the packaged/offline path for the surrounding install
sequence — this Change extends what that sequence emits and checks, it does
not change how it is packaged).

### FR-007 — Layer B: a real Change's repository outcome validates

An automated test MUST construct, against a disposable copy of the
`examples/golden-path-standard/starter/` fixture, a real repository-native
STANDARD Change implementing FR-004's missing behavioral rule through
genuine TDD (RED authored and observed before GREEN — see
`test-design.md`), then assert: `forge validate` passes against that
fixture repository; the Change's `manifest.yml` records `flow.current:
standard`; required STANDARD artifacts are present
(`protocol/flows/standard.yml` stage list); the TDD evidence record's `red:
{observed: true}` claim is truthful (the test that produced it actually
existed and actually failed for the expected reason before the fix, checked
via the same subprocess-pytest-then-inspect approach used to author it, not
merely asserted); and Implementation is never dated/ordered before Plan in
the constructed artifacts (approval-boundary ordering, FR-008).

### FR-008 — The Plan→Implementation approval boundary is explicit and checked

The Layer B test (FR-007) MUST assert that the constructed Change's
artifacts reflect Plan being authored and an explicit approval marker
recorded *before* any production-behavior commit exists in the fixture's own
Implementation evidence — i.e., that the scenario used to prove FR-007
cannot pass by silently collapsing Plan and Implementation into one
undifferentiated step. `docs/getting-started.md` (FR-005) MUST also state
this boundary explicitly in the form: Plan ready → stop → explicit human
approval → Implementation, per the originating brief §10.

### FR-009 — Layer C manual acceptance procedure is behaviorally specified

`examples/golden-path-standard/README.md` MUST contain a manual acceptance
procedure with: preconditions; exact starting repository state; installation
steps; the Codex-opening step; the natural-language request to give Codex;
expected behavioral milestones (not exact prose); explicit failure
conditions drawn from the originating brief §25; and the evidence an
operator should inspect at each milestone. No assertion in this procedure
may depend on Codex's exact generated wording.

## Non-functional requirements

### NFR-001 — No new runtime dependency

No change in this specification requires adding a dependency to
`[project] dependencies` in `pyproject.toml`. The example fixture's own
`pytest` need is a dev/test-only dependency of the fixture, not of
`forge-protocol` itself.

### NFR-002 — No lifecycle CLI surface added

No new Typer command is added. FR-001/FR-002/FR-003 extend existing
commands (`doctor`, `adapter install`) and existing generation logic
(`_gate_instructions`); none of them are `specify`/`implement`/`verify`/
`review` equivalents (`protocol/specification.md` §31, `ARCHITECTURE.md`
§20).

## Constraints

### CON-001 — Additive and backward compatible

FR-001–FR-003 MUST NOT change any existing passing assertion in
`tests/integration/adapter_cli_wheel_probe.py`,
`tests/integration/test_adapter_distribution.py`,
`tests/integration/test_codex_acceptance.py`, or any `tests/unit/
test_codex_*`/`test_adapter_*` module, except where a test asserts the
*absence* of behavior this Specification requires adding (in which case the
assertion is updated in the same commit as the behavior, not left
contradictory).

### CON-002 — No Protocol/Schema/Contract change

Nothing in this Specification requires editing `protocol/specification.md`,
`protocol/contract/engineering.md`, any `protocol/schemas/*.json`, or
`protocol/compatibility.md`. `discovery.md`'s materiality check covers the
two scope calls that could plausibly have required one.

## Acceptance criteria

- AC-1 (FR-001, FR-006): `forge doctor` run against a repository with the
  Codex Adapter installed and healthy prints Adapter-scoped `PASS` lines and
  exits 0; run against one with deliberately drifted Adapter state, prints a
  failing Adapter-scoped line and exits 2.
- AC-2 (FR-002, FR-006): `forge adapter install codex` on a fresh repository
  prints a confirmation line distinct from, and after, the plan operation
  lines, naming the resolved target path.
- AC-3 (FR-003, targeted unit test): the generated `SKILL.md` for every
  canonical Flow contains instruction text for
  `documentation_impact_evaluated`, `required_documentation_updated`, and
  `tdd_compliant_or_explicitly_excepted` wherever the source Flow YAML
  declares them, AND contains an explicit statement that Implementation must
  not begin before the applicable pre-Implementation gate's required
  artifacts are complete, sourced from `before_implementation` (STANDARD/
  FAST) or `before_architecture` (FULL).
- AC-4 (FR-004): `examples/golden-path-standard/starter/`'s existing test
  suite passes as-is, and fails (for the expected reason) once a test for
  the missing username-length rule is added, before the rule is
  implemented.
- AC-5 (FR-005, FR-008): a first-time reader following only
  `docs/getting-started.md` + `README.md` reaches "Codex Adapter installed,
  ready to request a Change" without consulting any file this Specification
  excludes; this is checked by this session performing that exact sequence
  once as part of Verification and recording the transcript, and is not
  itself a Layer C claim about Codex's behavior.
- AC-6 (FR-007, FR-008): the Layer B test passes, `forge validate` exits 0
  against the constructed fixture Change, and the constructed Change's own
  TDD evidence is genuine per the honesty standard in `discovery.md`
  (chronological RED, not reconstructed, and disclosed if it ever isn't).
- AC-7 (FR-009): `examples/golden-path-standard/README.md`'s manual
  acceptance procedure, read cold by someone who has not seen this Change's
  other artifacts, contains everything item 33 of the originating brief
  requires (preconditions, starting state, steps, expected milestones,
  failure conditions, evidence to inspect).

## Compatibility

No integer Protocol identifier, schema suffix, Adapter manifest capability,
or canonical Contract rule changes. `protocol/compatibility.md`'s "optional
artifacts whose absence preserves existing meaning" and "implementation
fixes that enforce already-published semantics" categories both apply by
analogy: FR-001–FR-003 make already-declared obligations (the `before_
completion` gate set; a successful `install`'s obvious next step) visible
where they were previously silently incomplete, without changing what those
obligations *are*. No historical Change or completed Protocol instance is
invalidated.
