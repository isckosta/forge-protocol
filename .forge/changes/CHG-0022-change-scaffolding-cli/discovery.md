---
forge:
  artifact: discovery
  schema: 1
change: CHG-0022
status: active
---

# Discovery — Change Scaffolding CLI

## Executive Summary

The repository already has the required primitives for a safe scaffold, but
they are split across CLI, Protocol-resolution, validation, and Adapter-plan
boundaries. The narrowest compatible design is a new Change-specific planner
and publisher that reuses the Adapter plan vocabulary and output formatter,
while resolving Flow stages from the packaged canonical resources and using
the project configuration's `flows.default` only as the active Flow selector.
No schema change is needed. The current repository configuration selects
STANDARD, so the first real scaffold in this repository should produce the
STANDARD artifact set; FULL must remain covered by a temporary-project test.

## Existing CLI and repository boundaries

`src/forge_cli/app.py` registers `adapter_app` with
`app.add_typer(adapter_app, name="adapter")`. A sibling `change_app` can be
registered identically without changing the CLI's existing infrastructure
boundary. `adapter_cli.py` already maps Git, domain, and internal failures to
stable exit codes and emits a plan before `AdapterService.install()` mutates
the repository.

`src/forge_cli/adapters/plan.py` and `formatting.py` provide the relevant
language for this Change: `AdapterOperation` carries an operation intent and
ownership, while `plan_lines()` renders lines such as
`CREATE forge_owned <path>`. `adapters/planner.py` produces deterministic
plans, but its inputs are Adapter-specific and include protocol compatibility
and ownership classification. The scaffold should reuse the output contract
and operation vocabulary without pretending a Change scaffold is an Adapter
installation.

## Flow resolution and artifact set

The project's `.forge/forge.yml` contains `flows.default`, currently
`standard`; `.forge/flows/{fast,standard,full}.yml` reference canonical Flow
identifiers and are resolved against packaged Protocol resources by
`resolve_effective_flow()`. Canonical `standard.yml` stages are:
`intent`, `discovery`, `specification`, `test_design`, `plan`,
`tdd_implementation`, `verification`, `strict_review`, `documentation`, and
`completion`. Canonical `full.yml` adds `specification_review`, `architecture`,
`test_strategy`, `tasks`, and `knowledge_capture` around the shared lifecycle.

The scaffold must map stage identifiers to this repository's established
artifact filenames (`test_design` → `test-design.md`,
`tdd_implementation` → `tdd-evidence.yml`, and lifecycle metadata to
`manifest.yml`/`traceability.yml` where applicable). It must not generate a
literal list that silently diverges from the selected Flow. A stage that is
represented by the manifest or by a non-file lifecycle state should be
represented in the manifest rather than as a fabricated Markdown artifact.

## Artifact conventions and schema constraints

`protocol/artifact-structure.md` §4 requires Markdown artifacts to begin with
the `forge:` frontmatter block containing `artifact`, `schema`, `change`, and
`status`. CHG-0021's review shows why generated metadata must be checked after
all evidence artifacts are assembled: `traceability.yml` requires non-empty
task arrays, and `manifest.yml`'s pending review state requires
`iteration: 0` and `iterations: []`. The scaffold therefore needs an
explicit pending-state template and contract tests against the generated
instances, not only string snapshots.

The current `forge/change@2` schema accepts the canonical Change kinds and
Flow identifiers, requires `review.iteration`, counters, and `iterations`,
and permits an omitted `decisions` array. The safest initial manifest is
therefore Decision-free. If a future scaffold adds a Decision placeholder,
its class, authority, owning artifact, and resolved-via values must be
derived from the live validation constants; this Change will not duplicate
those enums.

## Runtime numbering and safety

The Protocol says identifiers are assigned when a repository-native Change is
created and must not be reserved by planning documents. The command should
scan only immediate directories under `.forge/changes/`, recognize canonical
`CHG-[0-9]{4,}-<slug>` names, and choose one greater than the highest valid
number. It must reject an already-existing target, malformed slug, missing
Forge workspace, invalid project configuration, and unsafe path resolution
before printing a mutation plan or writing files.

## Flow Classification Finding

**STANDARD.** FAST is disqualified by `significant_cross_module_change` in
`protocol/flows/fast.yml`: the feature adds a CLI sub-app, runtime Flow
resolution, artifact rendering, manifest generation, and multiple test
surfaces. FULL is not required because the scoped design does not change a
canonical Protocol, schema, security/authorization model, persistence model,
or public cross-system integration; `protocol/flows/full.yml`'s additional
architecture and knowledge stages would be disproportionate. The required
STANDARD stages are exactly the stages this Change will scaffold and execute.
If implementation discovery expands the semantic surface into a canonical
Protocol or schema change, the Change must escalate to FULL rather than
silently continuing under STANDARD.

## Documentation Impact Signal

Required updates are `README.md`'s CLI command documentation,
`ROADMAP-REMEDIATION.md` item #2's status/link, and `CHANGELOG.md`. No
canonical Protocol file, schema, RFC, or ADR is expected from the scoped
design. The generated scaffold itself is the user-facing documentation of the
artifact workflow and must be covered by the Change's Verification.

## Baseline

Recorded before this Change's Implementation on branch
`chg-0022-change-scaffolding-cli`:

- `.venv/bin/python -m pytest -q` → **535 passed, 0 failed**.
- `forge validate` → **Forge project is valid**, exit 0.
- `forge doctor` → all seven checks PASS, with the existing non-blocking
  `migration_available` WARN reporting six candidates.
