---
forge:
  artifact: specification
  schema: 1
change: CHG-0022
status: approved
---

# Specification — Change Scaffolding CLI

## Summary

Add `forge change new <slug>`, an offline, deterministic scaffold command
that resolves the project's active canonical Flow, plans creation of its
repository-native Change artifacts, prints the plan, and then publishes the
artifacts if no conflict exists.

## Classification

**STANDARD.** FAST is disqualified by `significant_cross_module_change` in
`protocol/flows/fast.yml`. The scoped work crosses CLI registration, Flow
resolution, artifact rendering, manifest generation, and multiple test
surfaces. FULL is not required because no canonical Protocol, schema,
security/authorization model, persistence model, or external integration is
changed. If implementation evidence expands the scope to any such surface,
the Change must escalate to FULL before continuing.

## Functional Requirements

### FR-001 — CLI command and workspace preconditions

The CLI shall expose `forge change new <slug>` through a `change_app` Typer
sub-application registered in `src/forge_cli/app.py`. It shall require a Git
repository with an initialized, valid Forge workspace and shall report stable
environment/domain errors without a traceback: `E_FORGE_CHANGE_INVALID_SLUG`
and `E_FORGE_CHANGE_CONFLICT` use exit code 2; existing `E_FORGE_GIT_UNAVAILABLE`
and `E_FORGE_NOT_GIT_REPOSITORY` use exit code 3; validation/configuration
failures preserve `E_FORGE_NOT_INITIALIZED`, `E_FORGE_INVALID_PROJECT_CONFIGURATION`,
`E_FORGE_UNSUPPORTED_PROTOCOL`, `E_FORGE_INVALID_PROJECT_FLOW`, and
`E_FORGE_UNKNOWN_CANONICAL_FLOW` with exit code 2; unsafe destination paths
use `E_FORGE_CHANGE_INVALID_PATH`/2;
unavailable packaged resources use `E_FORGE_INTERNAL_ERROR`/70; publication
failures use the dedicated publication/rollback codes in the table below;
unexpected failures use exit code 70. It shall operate from a
nested directory by resolving the repository root, matching existing
infrastructure commands.

The complete failure contract is:

| Failure | Code | Exit | Mutation guarantee |
| --- | --- | ---: | --- |
| Git executable unavailable | `E_FORGE_GIT_UNAVAILABLE` | 3 | no mutation |
| Not a Git repository | `E_FORGE_NOT_GIT_REPOSITORY` | 3 | no mutation |
| Forge not initialized | `E_FORGE_NOT_INITIALIZED` | 2 | no mutation |
| Invalid project config | `E_FORGE_INVALID_PROJECT_CONFIGURATION` | 2 | no mutation |
| Unsupported Protocol | `E_FORGE_UNSUPPORTED_PROTOCOL` | 2 | no mutation |
| Missing, malformed, or disabled project Flow file | `E_FORGE_INVALID_PROJECT_FLOW` | 2 | no mutation |
| Unknown canonical Flow | `E_FORGE_UNKNOWN_CANONICAL_FLOW` | 2 | no mutation |
| Invalid slug | `E_FORGE_CHANGE_INVALID_SLUG` | 2 | no mutation |
| Unsafe destination | `E_FORGE_CHANGE_INVALID_PATH` | 2 | no mutation |
| Destination collision | `E_FORGE_CHANGE_CONFLICT` | 2 | existing bytes unchanged |
| Publication failure with complete rollback | `E_FORGE_CHANGE_PUBLICATION` | 70 | target absent; unrelated bytes unchanged |
| Publication failure with incomplete rollback | `E_FORGE_CHANGE_ROLLBACK_INCOMPLETE` | 70 | unknown/concurrent bytes preserved; path reported |
| Packaged resource or other unexpected failure | `E_FORGE_INTERNAL_ERROR` | 70 | no mutation before publication; rollback attempted after claim |

### FR-002 — Valid slug and runtime identifier allocation

The command shall accept only a non-empty lowercase slug consisting of ASCII
letters, digits, and single hyphens, beginning and ending with an alphanumeric
character. The exact accepted pattern is
`^[a-z0-9]+(?:-[a-z0-9]+)*$`; consecutive, leading, and trailing hyphens are
rejected, as are Unicode letters and uppercase characters. It shall scan
immediate directories under `.forge/changes/` at runtime, find the highest
canonical `CHG-NNNN-<slug>` number, and allocate the next number with a
minimum width of four digits. It shall never use a hardcoded next number or
create a reservation outside the scaffold directory.

### FR-003 — Active Flow resolution

The command shall read `flows.default` from `.forge/forge.yml`, require the
corresponding `.forge/flows/<default>.yml` to exist with
`schema: forge/project-flow@1`, require its `flow.canonical` reference and
`flow.enabled: true`, and resolve it through the packaged canonical Protocol
resources. A missing, malformed, or disabled project Flow file fails with
`E_FORGE_INVALID_PROJECT_FLOW`; a project Flow whose canonical reference does
not exist fails with `E_FORGE_UNKNOWN_CANONICAL_FLOW`. The generated
manifest shall record the resolved canonical Flow as both `flow.initial` and
`flow.current`, with no escalation entries.

### FR-004 — Flow-derived artifact set

The command shall generate this exact artifact set for each supported Flow.
`forge change new <slug>` defaults to a behavioral scaffold; the explicit
`--non-behavioral` option is the only way to omit stages whose Flow declaration
uses `required_when: behavioral_change`. The default mode sets both
`behavioral_change` and `tdd_applicable` true; `--non-behavioral` sets both
false. No other conditional combination is accepted or inferred.

The conditional-stage truth table is:

| Flow | Behavioral scaffold | `--non-behavioral` scaffold |
| --- | --- | --- |
| FAST | `test-design.md` + active zero-cycle `tdd-evidence.yml` | neither file; `tdd.status: not_applicable` |
| STANDARD | `test-design.md` + active zero-cycle `tdd-evidence.yml` | neither file; `tdd.status: not_applicable` |
| FULL | active zero-cycle `tdd-evidence.yml` plus unconditional FULL artifacts | no TDD evidence file; `tdd.status: not_applicable` plus unconditional FULL artifacts |
For FAST:

| Artifact | Path | Initial status/content |
| --- | --- | --- |
| Intent | `intent.md` | `active`, with required Intent sections |
| Inspection | `inspection.md` | `pending`, proportional inspection placeholder |
| Test Design | `test-design.md` | `pending`, when behavioral (default) |
| TDD Evidence | `tdd-evidence.yml` | `active`, when TDD is applicable |
| Verification | `verification.md` | `pending`, Result `PENDING` |
| Review | `review.md` | `pending`, Verdict `PENDING` |
| Manifest | `manifest.yml` | schema-valid pending lifecycle state |

For STANDARD:

| Artifact | Path | Initial status/content |
| --- | --- | --- |
| Intent | `intent.md` | `active`, with required Intent sections |
| Discovery | `discovery.md` | `pending`, with Executive Summary placeholder |
| Specification | `specification.md` | `pending`, with classification/FR/AC placeholders |
| Test Design | `test-design.md` | `pending`, with objective/case placeholders (default behavioral scaffold) |
| Plan | `plan.md` | `pending`, with numbered work-item placeholder and boundary |
| TDD Evidence | `tdd-evidence.yml` | `active`, zero cycles |
| Verification | `verification.md` | `pending`, Result `PENDING` |
| Review | `review.md` | `pending`, Verdict `PENDING` |
| Manifest | `manifest.yml` | schema-valid pending lifecycle state |

For a FULL Flow, the command shall generate only the files represented by
FULL's own canonical `stages:`: `intent.md`, `discovery.md`,
`specification.md`, `specification-review.md`, `architecture.md`,
`test-strategy.md`, `plan.md`, `tasks.md`, conditional `tdd-evidence.yml`,
`verification.md`, `review.md`, `knowledge-capture.md`, and `manifest.yml`.
It shall not generate `test-design.md`, because FULL has no `test_design`
stage. For a non-behavioral STANDARD or FULL scaffold,
`test-design.md` and `tdd-evidence.yml` are omitted by the same conditional
rule. The mapping shall be represented by a single stage-to-
artifact definition used by the renderer; it shall not silently generate
artifacts for stages absent from the resolved Flow. `traceability.yml`,
`provenance.yml`, and final review-control metadata are lifecycle evidence
artifacts assembled as evidence becomes available; they are not generated as
empty initial placeholders. When `--non-behavioral` is supplied, conditional
Test Design and TDD Evidence files are omitted and the manifest records
`tdd.status: not_applicable` with reason `The scaffold was created as
non-behavioral.`. The exact manifest mapping is: file artifacts use their
artifact key and status `pending` (Intent is `active`, TDD Evidence is
`active` when present); the `documentation`
and `documentation_impact` stage IDs are represented by the
`documentation.impact_evaluated: false` object and, respectively, an
`artifacts.documentation: pending` marker; FAST instead uses
`artifacts.documentation_impact: pending`; `completion` is represented by
`state.current: intent` and is not duplicated as a file artifact. The exact
file-artifact keys are the selected Markdown/YAML files, with
`tdd_evidence` present only for a behavioral scaffold.

### FR-005 — Artifact shape and frontmatter

Every generated Markdown artifact shall begin with a `forge:` YAML
frontmatter block containing `artifact`, `schema: 1`, `change`, and `status`,
followed by a title containing the generated Change ID and humanized slug.
Placeholders shall use the canonical section names from
`protocol/artifact-structure.md`, including `## FR-001`, `## AC-001`, and
`## TDD-001` where those structures apply. YAML artifacts shall use their
canonical top-level schema identifiers and shall not be incorrectly treated
as Markdown frontmatter documents.

### FR-006 — Schema-valid initial manifest

The generated `manifest.yml` shall conform to the repository's active
`forge/change@2` schema and shall contain pending values: `change.id`, a
humanized title, `kind: feature`, the resolved Flow in `flow.initial/current`,
`state.current: intent`, the exact artifact statuses above, `tdd.status:
pending` when behavioral or `not_applicable` with the stated reason when
non-behavioral,
`verification.status: pending`, `review.status: pending` with
`iteration: 0`, zero counters and `iterations: []`, and
`documentation.impact_evaluated: false`. The generated title shall be
deterministic: split the slug on hyphens, capitalize the first ASCII letter
of each segment without changing remaining characters, and join segments with
single spaces (for example, `api-v2-fix` becomes `Api V2 Fix`). It shall not create a Decision entry
or prefill Decision enum values.

### FR-007 — Plan-before-mutation and atomic publication

Before creating the directory or any file, the command shall print one
deterministic line per planned file in the form
`CREATE forge_owned <repository-relative-path>`. Lines shall follow the
filtered canonical stage order exactly: FAST `intent, inspection, [test_design],
[tdd_implementation], verification, strict_review, manifest`; STANDARD
`intent, discovery, specification, [test_design], plan, [tdd_implementation],
verification, strict_review, manifest`; FULL inserts its required
`specification_review, architecture, test_strategy` before `plan`, `tasks`
after `plan`, and `knowledge_capture` after `documentation` and before
`manifest`. Bracketed
stages are included only for behavioral scaffolds; non-file stages are not
printed. The publisher shall render every file in memory, claim the final
destination with an exclusive directory creation, and create each file with
exclusive-create semantics
(`x` mode); no rename or replace operation may overwrite a target. On any
write failure, the publisher shall remove only files it created. It shall
remove the claimed directory only when it is empty; if concurrent content is
if concurrent content is present, it shall preserve that content and report
`E_FORGE_CHANGE_ROLLBACK_INCOMPLETE`
with the target path rather than deleting unknown data. A target that exists
during preflight or at the exclusive claim is a deterministic collision. A
normal existing Change is skipped by choosing the next number, so the
collision test covers a destination appearing after planning as well as an
explicitly occupied target.

The publication guarantee is transactional rollback and no overwrite, not
atomic read visibility: a reader could observe a claimed directory while its
files are being created. The command must never claim completion until all
files are present.

### FR-008 — Offline installed-wheel behavior

The command shall resolve all required Protocol resources from the installed
package and shall not access the network, a Forge-hosted service, an AI
provider SDK, or a source-checkout-only path. An installed wheel in a clean,
temporary Git repository shall create the same artifact names and valid
manifest as the source checkout.

### FR-009 — Documentation impact

The Change shall update `README.md` with the command and its plan-before-
mutation behavior, add an `Unreleased` entry to `CHANGELOG.md`, and update
`ROADMAP-REMEDIATION.md` item #2 to `Done` with the real Change link. No
roadmap item #3–#10 shall be changed.

## Non-functional Requirements

### NFR-001 — Determinism

Identical repository state and slug shall produce identical planned paths and
file bytes, apart from the allocated number changing when repository state
changes.

### NFR-002 — Locality and portability

The implementation shall use repository-relative paths, UTF-8 text, and
packaged resources only. It shall preserve unrelated untracked files and
shall work from a nested current directory.

### NFR-003 — Single source of truth

Flow stage IDs, manifest enums, and Decision structural enums shall not be
retyped as a second authority. Canonical Flow content shall be parsed from
the resolved resource; manifest lifecycle values shall be limited to values
already accepted by the active schema and existing validation constants.

## Security Requirements

None. The command creates only a validated repository-relative directory under
`.forge/changes/`; it introduces no authentication, authorization, secret,
network, or code-execution surface.

## Constraints / Invariants

### CON-001

No file under `protocol/schemas/` changes. This Change consumes the existing
schema and must not alter Protocol definitions to accommodate the scaffold.

### CON-002

The CLI remains infrastructure-only. It creates lifecycle artifacts but does
not execute any lifecycle stage or assert that a stage has passed.

### INV-001

The plan is informational until all preconditions are checked; no mutation may
occur before the complete plan has been emitted, and any conflict must leave
the target absent or byte-for-byte unchanged.

## Acceptance Criteria

- **AC-001** (FR-001): CLI help exposes `change new`; nested invocation works
  in an initialized repository and environment/domain errors are stable.
- **AC-002** (FR-002): runtime numbering selects the next available ID,
  advances around gaps, and rejects invalid slugs without mutation.
- **AC-003** (FR-003/FR-004): FAST, STANDARD, and FULL temporary projects
  resolve their configured Flow and generate exactly their specified artifact
  sets.
- **AC-004** (FR-005): generated Markdown frontmatter/headings and YAML
  schema identifiers are valid.
- **AC-005** (FR-006): generated `manifest.yml` passes the existing contract
  schema test and contains the pending review placeholder shape.
- **AC-006** (FR-007): all `CREATE forge_owned` operations print before the
  first target file exists; collisions leave existing bytes unchanged.
- **AC-007** (FR-008): an installed-wheel probe succeeds offline in a clean
  temporary Git repository.
- **AC-008** (FR-009): README, CHANGELOG, and roadmap status are updated and
  items #3–#10 remain unchanged.

## Out of Scope

See `intent.md` “Out of Scope”. This Change does not add an interactive
wizard, modify schemas or canonical Flows, or address remediation items #3–#10.
