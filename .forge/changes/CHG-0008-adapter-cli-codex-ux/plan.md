# Adapter CLI and Codex Installation UX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the complete offline `forge adapter` CLI and install a safe, deterministic, repository-scoped Codex skill.

**Architecture:** A generic driver/registry and service orchestrate existing Adapter Core primitives. Codex implements the driver and renders a valid skill; all mutation passes through the generic planner and atomic publisher. Typer handlers only translate inputs, domain results, errors, and stable output.

**Tech Stack:** Python 3.12+, Typer, PyYAML, jsonschema Draft 2020-12, importlib.resources, pytest, hatchling.

## Global Constraints

- Repository-native Forge state remains authoritative.
- The packaged Codex default target is exactly `.agents/skills/forge`.
- No default or test writes to `.codex/`, a home directory, or a global target.
- Runtime Adapter behavior performs no vendor network discovery.
- Every behavioral implementation requires an executed valid RED first.
- User-authored or drifted content is never silently adopted, overwritten, or deleted.
- `plan`, `validate`, `doctor`, and `install --dry-run` are read-only.
- Success exits `0`, domain validation exits `2`, Git/environment exits `3`, and unexpected errors exit `70`.
- Do not add `.codex/`, `docs/superpowers/`, `uv.lock`, or local session documents to Git.

## File structure

- `src/forge_cli/adapters/driver.py`: generic driver protocol and projection input/output types.
- `src/forge_cli/adapters/registry.py`: immutable Adapter registry and lookup errors.
- `src/forge_cli/adapters/packaged.py`: application composition of packaged drivers.
- `src/forge_cli/adapters/configuration.py`: schema-backed Adapter configuration and atomic writes.
- `src/forge_cli/adapters/repository.py`: installation/desired-path snapshots and safe digest observation.
- `src/forge_cli/adapters/service.py`: plan/install/update orchestration and typed domain errors.
- `src/forge_cli/adapters/diagnostics.py`: validation findings and doctor checks.
- `src/forge_cli/adapters/formatting.py`: stable human-readable plan/diagnostic rendering.
- `src/forge_cli/adapter_cli.py`: Typer Adapter command group and exit mapping.
- `src/forge_cli/adapters/codex/driver.py`: Codex driver composition.
- `src/forge_cli/adapters/codex/projection.py`: valid Codex skill rendering.
- `src/forge_cli/adapters/codex/targets.py`: target precedence and evidence source.
- `src/forge_cli/adapters/codex/resources/publication.yml`: packaged dated target evidence.
- `protocol/schemas/adapter-configuration.schema.json`: public configuration schema.
- Existing Core files `plan.py`, `planner.py`, `ownership.py`, `publisher.py`, and `state.py`: no-op/delete/update semantics.

---

### Task 1: Generic driver contract and packaged registry

**Requirements:** FR-002, FR-003, NFR-003, INV-005; TDD-001.

**Files:**

- Create: `src/forge_cli/adapters/driver.py`
- Create: `src/forge_cli/adapters/registry.py`
- Create: `src/forge_cli/adapters/packaged.py`
- Create: `src/forge_cli/adapters/codex/driver.py` as an identity-only
  scaffold; projection remains unimplemented until Task 3's behavioral RED.
- Create: `tests/unit/test_adapter_registry.py`

**Interfaces:**

- Produces `AdapterProjectionContext`, `AdapterProjection`, and `HarnessDriver`.
- Produces `AdapterRegistry.list() -> tuple[HarnessDriver, ...]` and `get(adapter_id: str) -> HarnessDriver`.
- Produces `build_packaged_registry() -> AdapterRegistry`.

- [ ] **Step 1: Write registry RED tests**

```python
def test_registry_orders_drivers_and_rejects_unknown() -> None:
    registry = AdapterRegistry((_driver("zeta"), _driver("alpha")))
    assert [item.manifest.adapter_id for item in registry.list()] == ["alpha", "zeta"]
    with pytest.raises(UnknownAdapterError) as error:
        registry.get("missing")
    assert error.value.code == "E_FORGE_ADAPTER_UNKNOWN"

def test_packaged_registry_contains_codex_without_network(monkeypatch) -> None:
    monkeypatch.setattr(socket, "create_connection", lambda *args, **kwargs: pytest.fail("network"))
    assert build_packaged_registry().get("codex").manifest.harness == "codex"
```

- [ ] **Step 2: Create importable scaffolding and execute behavioral RED**

Run: `.venv/bin/python -m pytest tests/unit/test_adapter_registry.py -v`

Before running, create only enough importable type/module scaffolding for test
collection; it MUST NOT implement ordering, unknown lookup, duplicate rejection,
or packaged discovery. Expected: tests collect and fail by assertion or the
expected domain exception because those behaviors are absent. Import, syntax,
fixture, or collection errors do not count as RED. Record only the behavioral
failure in `tdd-evidence.yml`.

- [ ] **Step 3: Implement the minimal generic contract and registry**

```python
@dataclass(frozen=True)
class AdapterProjectionContext:
    project_protocol: int
    flows: tuple[tuple[str, str], ...]
    contract_content: str
    target: str

@dataclass(frozen=True)
class AdapterProjection:
    artifacts: tuple[ProjectedArtifact, ...]
    limitations: tuple[CapabilityLimitation, ...]
    representation: AdapterRepresentation

class HarnessDriver(Protocol):
    @property
    def manifest(self) -> AdapterManifest:
        raise NotImplementedError

    @property
    def default_target(self) -> str | None:
        raise NotImplementedError

    def project(self, context: AdapterProjectionContext) -> AdapterProjection: ...
```

Reject duplicate Adapter ids during construction and sort once. Keep the Codex
import only in `packaged.py`. The initial `CodexDriver` exposes its packaged
manifest, has no target yet, and raises `NotImplementedError` from `project`;
Task 3 adds projection behavior test-first.

- [ ] **Step 4: Execute GREEN and regression tests**

Run: `.venv/bin/python -m pytest tests/unit/test_adapter_registry.py tests/unit/test_codex_adapter_descriptor.py -v`

Expected: all pass; inspect `rg -n "codex" src/forge_cli/adapters/{driver,registry}.py` and require no matches.

- [ ] **Step 5: Commit**

```bash
git add src/forge_cli/adapters/driver.py src/forge_cli/adapters/registry.py src/forge_cli/adapters/packaged.py src/forge_cli/adapters/codex/driver.py tests/unit/test_adapter_registry.py .forge/changes/CHG-0008-adapter-cli-codex-ux/tdd-evidence.yml
git commit -m "feat(adapter): add packaged driver registry"
```

### Task 2: Adapter configuration and Codex publication evidence

**Requirements:** FR-005–FR-007, FR-023, INV-005, AC-009, AC-011; TDD-002.

**Files:**

- Create: `protocol/schemas/adapter-configuration.schema.json`
- Modify: `protocol/schemas/catalog.yml`
- Create: `src/forge_cli/adapters/configuration.py`
- Create: `src/forge_cli/adapters/codex/resources/publication.yml`
- Modify: `src/forge_cli/adapters/codex/targets.py`
- Create: `tests/unit/test_adapter_configuration.py`
- Modify: `tests/unit/test_codex_publication_targets.py`
- Modify: `tests/contract/test_protocol_contract.py`

**Interfaces:**

- Produces immutable `AdapterConfiguration(adapter_id: str, target: str | None)`.
- Produces `adapter_configuration_path(project_root, adapter_id)`,
  `load_adapter_configuration(project_root, adapter_id)`,
  `write_adapter_configuration(project_root, config)`, and
  `resolve_configured_target(explicit, config, evidence)`. Configuration APIs
  derive the exact `.forge/adapters/<adapter-id>/config.yml` path internally;
  callers cannot supply an arbitrary destination.

- [ ] **Step 1: Write configuration and precedence RED tests**

```python
def test_target_precedence_is_explicit_then_config_then_evidence(tmp_path: Path) -> None:
    config = AdapterConfiguration(adapter_id="codex", target="configured/codex")
    assert resolve_target("explicit/codex", config, ".agents/skills/forge").root == "explicit/codex"
    assert resolve_target(None, config, ".agents/skills/forge").root == "configured/codex"
    assert resolve_target(None, None, ".agents/skills/forge").root == ".agents/skills/forge"

@pytest.mark.parametrize("target", ["/tmp/x", "../x", r"x\\y", "C:/x", ".codex/forge"])
def test_invalid_or_forbidden_target_is_rejected(target: str) -> None:
    with pytest.raises(InvalidAdapterConfigurationError):
        AdapterConfiguration(adapter_id="codex", target=target)
```

Also assert malformed YAML, unknown keys, wrong Adapter identity, `~` targets,
unsafe Adapter ids, and a symlink at the configuration file or any ancestor
under the repository root do not mutate existing bytes or escape the project.

- [ ] **Step 2: Create importable scaffolding and execute behavioral RED**

Run: `.venv/bin/python -m pytest tests/unit/test_adapter_configuration.py tests/unit/test_codex_publication_targets.py -v`

Before running, create only importable API scaffolding that returns no effective
configuration/default. Expected: tests collect and fail on literal precedence,
validation, schema, or atomicity assertions. Import, syntax, fixture, or
collection errors do not count as RED.

- [ ] **Step 3: Implement schema-backed atomic configuration**

Use schema identity `forge/adapter-configuration@1`, `additionalProperties:
false`, exact safe Adapter id, and optional safe target. Derive the only allowed
path from the resolved project root, reject symlinks at every existing path
component, and serialize via a sibling temporary file plus `os.replace`; never
accept an arbitrary configuration destination or rewrite `.forge/forge.yml`.
Load `publication.yml` with target, source URL, and `observed_on` date, and
expose `.agents/skills/forge` from the Codex driver.

- [ ] **Step 4: Execute GREEN and contract closure**

Run: `.venv/bin/python -m pytest tests/unit/test_adapter_configuration.py tests/unit/test_codex_publication_targets.py tests/contract/test_protocol_contract.py -v`

Expected: all pass and the schema catalog contains exactly one mapping for `forge/adapter-configuration@1`.

- [ ] **Step 5: Commit**

```bash
git add protocol/schemas src/forge_cli/adapters/configuration.py src/forge_cli/adapters/codex tests/unit/test_adapter_configuration.py tests/unit/test_codex_publication_targets.py tests/contract/test_protocol_contract.py .forge/changes/CHG-0008-adapter-cli-codex-ux/tdd-evidence.yml
git commit -m "feat(adapter): add schema-backed target configuration"
```

### Task 3: Valid deterministic Codex skill projection

**Requirements:** FR-008–FR-010, FR-022, NFR-001/NFR-003, INV-001/INV-005, AC-010/AC-012; TDD-003.

**Files:**

- Modify: `src/forge_cli/adapters/codex/driver.py`
- Modify: `src/forge_cli/adapters/codex/projection.py`
- Modify: `src/forge_cli/adapters/codex/resources/skills/workflow.md`
- Modify: `src/forge_cli/adapters/codex/__init__.py`
- Replace or extend: `tests/unit/test_codex_projection_bundle.py`
- Create: `tests/unit/test_codex_skill_projection.py`
- Modify: `tests/unit/test_codex_distribution_resources.py`

**Interfaces:**

- `CodexDriver.project(context: AdapterProjectionContext) -> AdapterProjection`.
- Logical resource names are exactly `SKILL.md`, `references/engineering-contract.md`, and `references/flows/<id>.yml`.

- [ ] **Step 1: Write skill-layout RED tests**

```python
def test_codex_projection_is_a_valid_repo_skill() -> None:
    projection = CodexDriver().project(_context(flows=("standard", "full")))
    by_path = {item.path: item.content for item in projection.artifacts}
    assert tuple(sorted(by_path)) == (
        ".agents/skills/forge/SKILL.md",
        ".agents/skills/forge/references/engineering-contract.md",
        ".agents/skills/forge/references/flows/full.yml",
        ".agents/skills/forge/references/flows/standard.yml",
    )
    metadata = yaml.safe_load(by_path[".agents/skills/forge/SKILL.md"].split("---", 2)[1])
    assert metadata["name"] == "forge"
    assert "Repository-native Forge state remains authoritative" in by_path[".agents/skills/forge/SKILL.md"]
```

Add repeated-generation equality and deletion-of-output-does-not-touch-input fixtures.

- [ ] **Step 2: Create importable scaffolding and execute behavioral RED**

Run: `.venv/bin/python -m pytest tests/unit/test_codex_skill_projection.py -v`

Before running, create only an importable `CodexDriver` stub that returns an
empty projection through the declared interface. Expected: tests collect and
fail on the required skill layout, metadata, content, or determinism assertions.
Import, syntax, fixture, or collection errors do not count as RED.

- [ ] **Step 3: Implement the Codex driver and skill renderer**

Render strict YAML frontmatter with `name: forge` and a description that triggers on Forge-governed engineering Changes. Put canonical/project contract text and enabled resolved Flows only in references. Sort by logical path, normalize one trailing newline, and convert Codex limitations to generic limitations before returning.

- [ ] **Step 4: Execute GREEN and existing Codex regressions**

Run: `.venv/bin/python -m pytest tests/unit/test_codex_skill_projection.py tests/unit/test_codex_projection_bundle.py tests/unit/test_codex_projection_gates.py tests/unit/test_codex_distribution_resources.py -v`

Expected: all pass and repeated digests match.

- [ ] **Step 5: Commit**

```bash
git add src/forge_cli/adapters/codex tests/unit/test_codex_skill_projection.py tests/unit/test_codex_projection_bundle.py tests/unit/test_codex_projection_gates.py tests/unit/test_codex_distribution_resources.py .forge/changes/CHG-0008-adapter-cli-codex-ux/tdd-evidence.yml
git commit -m "feat(codex): render repository Forge skill"
```

### Task 4: No-op, obsolete artifact, deletion, and rollback semantics

**Requirements:** FR-011, FR-013–FR-019, NFR-001/NFR-002, INV-002/INV-004, AC-003–AC-008; TDD-004.

**Files:**

- Modify: `src/forge_cli/adapters/plan.py`
- Modify: `src/forge_cli/adapters/ownership.py`
- Modify: `src/forge_cli/adapters/planner.py`
- Modify: `src/forge_cli/adapters/publisher.py`
- Modify: `src/forge_cli/adapters/state.py`
- Modify: `tests/unit/test_adapter_ownership.py`
- Modify: `tests/unit/test_adapter_planner.py`
- Modify: `tests/integration/test_adapter_publisher.py`

**Interfaces:**

- Add `OperationIntent.UNCHANGED = "unchanged"`.
- Extend `plan_adapter` with the optional keyword
  `previous_generated: Iterable[GeneratedArtifact] = ()`, retaining its existing
  manifest, effective-configuration, projections, repository-state, and
  additional-limitations parameters.
- `publish_adapter_plan` skips `UNCHANGED`, safely applies `DELETE_GENERATED`, and validates the next record against all desired Forge-owned operations.

- [ ] **Step 1: Write RED state-transition tests**

```python
def test_recorded_equal_desired_file_is_unchanged() -> None:
    decision = classify_artifact(
        ownership=OwnershipMode.FORGE_OWNED,
        exists=True,
        current_digest=digest_content("same"),
        expected_digest=digest_content("same"),
        desired_digest=digest_content("same"),
        merge_result=None,
    )
    assert decision.intent is OperationIntent.UNCHANGED

def test_obsolete_intact_generated_file_is_deleted_but_drifted_one_conflicts() -> None:
    previous = (GeneratedArtifact("old.md", digest_content("old")),)
    intact = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(),
        repository_state=(RepositoryArtifactState("old.md", True, digest_content("old"), digest_content("old")),),
        previous_generated=previous,
    )
    assert intact.operations[0].intent is OperationIntent.DELETE_GENERATED
    drifted = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(),
        repository_state=(RepositoryArtifactState("old.md", True, digest_content("edited"), digest_content("old")),),
        previous_generated=previous,
    )
    assert drifted.operations[0].intent is OperationIntent.CONFLICT
```

Add a publisher failure injected after create/update/delete and assert every file plus `installation.yml` is byte-identical to the pre-run snapshot.

- [ ] **Step 2: Execute RED**

Run: `.venv/bin/python -m pytest tests/unit/test_adapter_ownership.py tests/unit/test_adapter_planner.py tests/integration/test_adapter_publisher.py -v`

Expected: missing `UNCHANGED`, unsupported delete, and failed rollback assertions.

- [ ] **Step 3: Implement minimal Core transitions**

Require `current == expected` before comparing desired. Emit `UNCHANGED` only for recorded Forge ownership; retain conflict for unrecorded equal bytes. For delete, require a regular non-symlink file and `expected_current_digest`, capture bytes before unlink, and restore them on any later failure. Include CREATE/UPDATE/UNCHANGED desired digests in record validation; exclude DELETE.

- [ ] **Step 4: Execute GREEN and full Core regressions**

Run: `.venv/bin/python -m pytest tests/unit/test_adapter_ownership.py tests/unit/test_adapter_planner.py tests/unit/test_adapter_drift.py tests/unit/test_adapter_installation_state.py tests/integration/test_adapter_publisher.py -v`

Expected: all pass, including mixed rollback and no silent adoption.

- [ ] **Step 5: Commit**

```bash
git add src/forge_cli/adapters tests/unit/test_adapter_ownership.py tests/unit/test_adapter_planner.py tests/unit/test_adapter_drift.py tests/unit/test_adapter_installation_state.py tests/integration/test_adapter_publisher.py .forge/changes/CHG-0008-adapter-cli-codex-ux/tdd-evidence.yml
git commit -m "feat(adapter): add idempotent update planning"
```

### Task 5: Generic Adapter service for plan, install, and update

**Requirements:** FR-004, FR-006, FR-008, FR-012–FR-019, INV-001/INV-003/INV-004, AC-001/AC-004–AC-006/AC-011; TDD-005.

**Files:**

- Create: `src/forge_cli/adapters/repository.py`
- Create: `src/forge_cli/adapters/service.py`
- Create: `tests/integration/test_adapter_service.py`

**Interfaces:**

- `AdapterService.plan(project_root, adapter_id, explicit_target=None) -> AdapterPlanResult`.
- `AdapterService.install(project_root: Path, adapter_id: str, explicit_target: str | None = None, dry_run: bool = False) -> AdapterMutationResult`.
- `AdapterService.update(project_root: Path, adapter_id: str, explicit_target: str | None = None, dry_run: bool = False) -> AdapterMutationResult`.
- Result exposes plan, target source, installed/current version, and `mutated: bool`.

- [ ] **Step 1: Write service state-machine RED tests**

```python
def test_install_then_reinstall_is_true_noop(initialized_project: Path) -> None:
    service = _service()
    first = service.install(initialized_project, "codex")
    before = _bytes_and_mtimes(initialized_project)
    second = service.install(initialized_project, "codex")
    assert first.mutated is True
    assert second.mutated is False
    assert _bytes_and_mtimes(initialized_project) == before

def test_update_refuses_drift_without_partial_mutation(initialized_project: Path) -> None:
    service = _installed_service(initialized_project)
    skill = initialized_project / ".agents/skills/forge/SKILL.md"
    skill.write_text("user edit\n")
    before = _tree_bytes(initialized_project)
    with pytest.raises(AdapterDriftError):
        service.update(initialized_project, "codex")
    assert _tree_bytes(initialized_project) == before
```

Add different-version install rejection, missing-record update rejection, target precedence, Protocol incompatibility, invalid record identity, and plan read-only tests.

- [ ] **Step 2: Create importable scaffolding and execute behavioral RED**

Run: `.venv/bin/python -m pytest tests/integration/test_adapter_service.py -v`

Before running, create only importable service/result scaffolding whose methods
return empty results or raise a neutral unimplemented domain condition. Expected:
tests collect and fail on state-machine, mutation, or error-code assertions.
Import, syntax, fixture, or collection errors do not count as RED.

- [ ] **Step 3: Implement read-once orchestration**

Resolve Git root outside the service, validate project config, resolve enabled project Flows and effective Contract, load optional config/record, resolve target, snapshot union(desired paths, recorded paths), call the driver and generic planner, then return the result. Install calls publisher only for a first install with no conflicts or for an entirely unchanged current install it returns `mutated=False`. Update requires a valid record, rejects drift before publisher, and writes the new complete record.

- [ ] **Step 4: Execute GREEN and integration regressions**

Run: `.venv/bin/python -m pytest tests/integration/test_adapter_service.py tests/integration/test_codex_acceptance.py tests/integration/test_adapter_publisher.py -v`

Expected: all pass and read-only operations preserve a recursive byte/mtime snapshot.

- [ ] **Step 5: Commit**

```bash
git add src/forge_cli/adapters/repository.py src/forge_cli/adapters/service.py tests/integration/test_adapter_service.py .forge/changes/CHG-0008-adapter-cli-codex-ux/tdd-evidence.yml
git commit -m "feat(adapter): orchestrate safe install and update"
```

### Task 6: Read-only validation and doctor diagnostics

**Requirements:** FR-020–FR-023, NFR-001/NFR-004, INV-003, AC-007/AC-010/AC-011; TDD-006.

**Files:**

- Create: `src/forge_cli/adapters/diagnostics.py`
- Create: `tests/unit/test_adapter_diagnostics.py`
- Modify: `src/forge_cli/adapters/service.py`
- Modify: `tests/integration/test_adapter_service.py`

**Interfaces:**

- `AdapterValidationResult(passed: bool, findings: tuple[AdapterFinding, ...])`.
- `AdapterDoctorResult(passed: bool, checks: tuple[AdapterCheck, ...])` with status `passed`, `failed`, or `warning`.
- `AdapterService.validate(project_root: Path, adapter_id: str, explicit_target: str | None = None) -> AdapterValidationResult` is read-only.
- `AdapterService.doctor(project_root: Path, adapter_id: str, explicit_target: str | None = None) -> AdapterDoctorResult` is read-only.

- [ ] **Step 1: Write diagnostics RED tests**

```python
def test_doctor_reports_drift_and_action_without_mutating(project: Path) -> None:
    before = _tree_bytes_and_mtimes(project)
    result = _service().doctor(project, "codex")
    assert result.passed is False
    drift = next(item for item in result.checks if item.id == "generated_drift")
    assert drift.status == "failed"
    assert "restore the recorded artifact" in drift.remediation
    assert _tree_bytes_and_mtimes(project) == before

def test_limitations_are_warnings_not_enforcement() -> None:
    result = diagnose_adapter(_fixture_with_limitation())
    assert any(item.status == "warning" for item in result.checks)
    assert all("enforced" not in item.message.lower() for item in result.checks if item.status == "warning")
```

- [ ] **Step 2: Create importable scaffolding and execute behavioral RED**

Run: `.venv/bin/python -m pytest tests/unit/test_adapter_diagnostics.py tests/integration/test_adapter_service.py -v`

Before running, create only importable diagnostic/result scaffolding with empty
checks/findings. Expected: tests collect and fail on required statuses,
remediation, read-only behavior, or limitation assertions. Import, syntax,
fixture, or collection errors do not count as RED.

- [ ] **Step 3: Implement deterministic findings/checks**

Use stable ids ordered as configuration, compatibility, target, installation,
generated_drift, conformance, limitations. Validation converts failed checks to
stable findings and treats warnings as non-failing. Each failure includes one
specific safe remediation; neither method calls configuration writer or publisher.

- [ ] **Step 4: Execute GREEN**

Run: `.venv/bin/python -m pytest tests/unit/test_adapter_diagnostics.py tests/integration/test_adapter_service.py -v`

Expected: all pass, repeated results equal, and snapshots prove no mutation.

- [ ] **Step 5: Commit**

```bash
git add src/forge_cli/adapters/diagnostics.py src/forge_cli/adapters/service.py tests/unit/test_adapter_diagnostics.py tests/integration/test_adapter_service.py .forge/changes/CHG-0008-adapter-cli-codex-ux/tdd-evidence.yml
git commit -m "feat(adapter): add validation and diagnostics"
```

### Task 7: Public `forge adapter` command group

**Requirements:** FR-001–FR-007, FR-011, FR-015/FR-016, FR-020/FR-021, FR-023, NFR-004, AC-001–AC-003/AC-005/AC-009; TDD-007.

**Files:**

- Create: `src/forge_cli/adapters/formatting.py`
- Create: `src/forge_cli/adapter_cli.py`
- Modify: `src/forge_cli/app.py`
- Create: `tests/cli/test_adapter_commands.py`
- Modify: `tests/cli/test_cli_contract.py`

**Interfaces:**

- Typer subgroup `adapter_app` registered as `app.add_typer(adapter_app, name="adapter")`.
- All seven commands accept the exact names in FR-001; configure/install/plan/update accept `--target`; install accepts `--dry-run`.

- [ ] **Step 1: Write CLI RED tests**

```python
def test_adapter_help_exposes_only_infrastructure_commands() -> None:
    result = runner.invoke(app, ["adapter", "--help"])
    assert result.exit_code == 0
    for name in ("list", "configure", "plan", "install", "validate", "doctor", "update"):
        assert name in result.stdout
    for forbidden in ("specify", "implement", "review"):
        assert forbidden not in result.stdout

def test_plan_and_install_dry_run_have_identical_operations(project: Path) -> None:
    planned = invoke_in(project, ["adapter", "plan", "codex"])
    dry = invoke_in(project, ["adapter", "install", "codex", "--dry-run"])
    assert planned.exit_code == dry.exit_code == 0
    assert _operation_lines(planned.stdout) == _operation_lines(dry.stdout)
    assert not (project / ".agents").exists()
```

Add command tests for configure, list state, install/no-op, validate, doctor,
update, unknown Adapter, Git/environment errors, every expected exit code, and
stable operation formatting.

- [ ] **Step 2: Execute RED**

Run: `.venv/bin/python -m pytest tests/cli/test_adapter_commands.py tests/cli/test_cli_contract.py -v`

Expected: `adapter` command group is absent.

- [ ] **Step 3: Implement thin handlers and formatters**

Resolve project root using the existing Git boundary, construct the packaged
registry/service once per command, echo the plan before mutation, and map typed
Adapter errors to `CODE: message` plus exit `2`. Format operations as
`INTENT ownership path`, limitations as `WARN limitation`, conflicts as
`CONFLICT path: reason`, and doctor as `PASS|FAIL|WARN id: message — remediation`.

- [ ] **Step 4: Execute GREEN and existing CLI regressions**

Run: `.venv/bin/python -m pytest tests/cli -v`

Expected: all CLI tests pass and existing top-level output is unchanged.

- [ ] **Step 5: Commit**

```bash
git add src/forge_cli/app.py src/forge_cli/adapter_cli.py src/forge_cli/adapters/formatting.py tests/cli .forge/changes/CHG-0008-adapter-cli-codex-ux/tdd-evidence.yml
git commit -m "feat(cli): add Adapter management commands"
```

### Task 8: Installed-wheel offline golden path

**Requirements:** FR-024, NFR-001, INV-001/INV-005, AC-001–AC-012;
distribution Verification by default. It becomes TDD-008 only if the executable
acceptance test reveals a real missing behavior or packaging defect.

**Files:**

- Create: `tests/integration/adapter_cli_wheel_probe.py`
- Modify: `tests/integration/test_adapter_distribution.py`
- Modify: `pyproject.toml` only if the RED proves a required resource is absent.

**Interfaces:**

- Probe takes an isolated `forge` executable and temporary Git repository; it imports no source-tree helpers.

- [ ] **Step 1: Write the executable distribution acceptance test**

Build/install a wheel into a temporary venv, clear `PYTHONPATH`, set
`PYTHONNOUSERSITE=1`, disable index/network for runtime commands, then execute:

```text
forge init
forge adapter list
forge adapter plan codex
forge adapter install codex
forge adapter install codex
forge adapter validate codex
forge adapter doctor codex
edit SKILL.md
forge adapter validate codex        # exit 2, drift
forge adapter update codex          # exit 2, no mutation
restore SKILL.md
forge adapter update codex          # success
```

Assert skill frontmatter, all references, record digests, plan/dry-run parity,
no-op bytes/mtimes, canonical-state survival, and absence of `.codex/`.

- [ ] **Step 2: Execute the acceptance test and classify the result**

Run: `.venv/bin/python -m pytest tests/integration/test_adapter_distribution.py -v`

If it passes immediately, record it as Verification and do not manufacture a
TDD cycle. If it fails because a required behavior or packaged resource is
absent, confirm the assertion is behavioral and record that valid RED as
TDD-008. Environment, dependency-download, import, syntax, fixture, or
collection failures are not RED and must be corrected before classification.

- [ ] **Step 3: Fix only proven distribution gaps**

Add exact missing resource inclusions to Hatch configuration or package paths.
Do not add network calls, vendor SDKs, or source-tree fallbacks.

- [ ] **Step 4: Execute GREEN, offline probe, and full suite**

Run: `.venv/bin/python -m pytest tests/integration/test_adapter_distribution.py -v`

Run: `.venv/bin/python -m pytest`

Expected: distribution test and full suite pass.

- [ ] **Step 5: Commit**

```bash
git add tests/integration/adapter_cli_wheel_probe.py tests/integration/test_adapter_distribution.py pyproject.toml .forge/changes/CHG-0008-adapter-cli-codex-ux/tdd-evidence.yml
git commit -m "test(adapter): verify offline wheel golden path"
```

### Task 9: Verification and Strict Review

**Files:**

- Create: `.forge/changes/CHG-0008-adapter-cli-codex-ux/verification.md`
- Create: `.forge/changes/CHG-0008-adapter-cli-codex-ux/review.md`
- Modify: `.forge/changes/CHG-0008-adapter-cli-codex-ux/manifest.yml`
- Modify: `.forge/changes/CHG-0008-adapter-cli-codex-ux/traceability.yml`
- Modify: `.forge/changes/CHG-0008-adapter-cli-codex-ux/tdd-evidence.yml`

- [ ] **Step 1: Audit TDD and traceability before claiming Verification**

For every TDD cycle, verify the RED revision precedes its GREEN revision and
the failure was behavioral. Map every FR/NFR/INV and AC to an implemented task
and test. Leave Verification pending if any mapping lacks evidence.

- [ ] **Step 2: Run final Verification commands from a clean revision**

```bash
.venv/bin/python -m pytest
git diff --check
git status --short
```

Also rerun the isolated-wheel acceptance, compare repeated plan output, and
record exact revision, commands, counts, exit codes, and environment in
`verification.md`.

- [ ] **Step 3: Perform adversarial Strict Review**

Review specification/architecture compliance, generic/Codex dependency
direction, all mutation preconditions, rollback, symlink/path safety,
configuration ownership, stale record handling, CLI output, installed wheel,
offline behavior, and forbidden untracked content. Record severity and exact
evidence in `review.md`.

- [ ] **Step 4: Remediate findings regression-first**

For each behavioral finding, add and execute a focused failing regression test,
apply the minimum fix, rerun focused and full tests, update TDD evidence, and
repeat Strict Review until zero blocker/major remains.

- [ ] **Step 5: Commit verified review state**

```bash
git add .forge/changes/CHG-0008-adapter-cli-codex-ux
git commit -m "docs(chg-0008): record verification and strict review"
```

### Task 10: Documentation, Roadmap, and Knowledge Capture

**Files:**

- Modify: `README.md`
- Modify: `ARCHITECTURE.md`
- Modify: `CHANGELOG.md`
- Modify: `ROADMAP.md`
- Create: `docs/adapter-cli.md`
- Create: `.forge/changes/CHG-0008-adapter-cli-codex-ux/knowledge-capture.md`
- Modify: `.forge/changes/CHG-0008-adapter-cli-codex-ux/manifest.yml`

- [ ] **Step 1: Document the tested public contract**

Add the four-command golden path to README and a command reference covering
target precedence, config/record ownership, plan output, no-op behavior, drift,
safe update, limitations, exit codes, and recovery. Use only commands proven by
T-007/T-008.

- [ ] **Step 2: Update architecture and release history**

Document the registry/service/driver boundary, link ADR-0008, and add a
CHG-0008 Changelog entry. Mark the Roadmap stage Completed by `CHG-0008` only
after Verification and Strict Review pass.

- [ ] **Step 3: Capture reusable knowledge**

Record why evidence-backed defaults satisfy rather than weaken ADR-0007, why
equal bytes are not ownership, how no-op differs from preserve, how deletion is
proved/rolled back, and how to add a future packaged Adapter without importing
it into generic Core.

- [ ] **Step 4: Run Completion Gate verification**

```bash
.venv/bin/python -m pytest
git diff --check
git status --short
```

Confirm required docs and Knowledge Capture exist, traceability remains closed,
Verification/Review pass, blocking external review threads are reconciled if a
PR exists, and forbidden local files are absent from `git ls-files`.

- [ ] **Step 5: Commit Completion artifacts**

```bash
git add README.md ARCHITECTURE.md CHANGELOG.md ROADMAP.md docs/adapter-cli.md docs/adr/0008-codex-repository-skill-is-the-default-publication-target.md .forge/changes/CHG-0008-adapter-cli-codex-ux
git commit -m "docs(chg-0008): complete Adapter CLI knowledge capture"
```
