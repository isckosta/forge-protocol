---
forge:
  artifact: verification
  schema: 1
change: CHG-0001
status: passed
---

# Verification — Bootstrap Forge CLI

## Result

Verification passed after one material distribution defect was discovered and corrected through regression-first TDD.

## Automated test suite

Final verified commit before this artifact: `1e34d5ac80ddf6ddb461cc986a1105ad899f4b70`.

GitHub Actions Tests:

- workflow run: `31670700948`
- job: `94354521196`
- result: success
- full Pytest step: success

## Distribution verification

GitHub Actions Distribution Verification:

- workflow run: `31670700974`
- job: `94354521352`
- result: success

Verified behavior:

1. Build a wheel from the repository.
2. Create a clean Python 3.12 virtual environment.
3. Install only the built wheel and runtime dependencies.
4. Execute the installed `forge version` outside the source tree.
5. Create a new Git repository.
6. Execute `forge init` from a nested directory.
7. Execute `forge validate` against the generated workspace.
8. Execute `forge doctor` against the generated workspace.
9. Execute runtime commands with HTTP, HTTPS, and ALL proxy variables pointed at an unreachable local endpoint to demonstrate that normal Core execution does not depend on network access.
10. Inspect package runtime dependencies for prohibited AI SDK / agent framework / database framework dependencies.

All checks passed.

## Verification finding — V-001

Severity: MAJOR

Status: RESOLVED

### Problem

The first isolated-wheel verification successfully built and installed the package and executed `forge version`, but `forge validate` failed after initialization because the canonical Project Schema was resolved through a source-tree-relative path.

Observed error:

`E_FORGE_INVALID_PROJECT_CONFIGURATION [.forge/forge.yml] [Errno 2] No such file or directory: '/tmp/forge-wheel-venv/lib/python3.12/protocol/schemas/project.schema.json'`

Initial failing distribution run:

- workflow run: `31670483873`
- job: `94353874439`

### Resolution

A regression-first TDD cycle introduced a canonical Protocol resource resolver that prefers packaged resources and falls back to the repository `protocol/` directory only for editable development.

The wheel now force-includes the canonical `protocol/` tree under `forge_cli/resources/protocol`.

Regression RED:

- workflow run: `31670537580`
- job: `94354031510`
- observed failure: `ModuleNotFoundError: No module named 'forge_cli.protocol_resources'`

GREEN:

- Tests workflow run: `31670613378`
- Distribution Verification run: `31670613450`

Final offline verification:

- Distribution Verification run: `31670700974`
- job: `94354521352`

## Requirement status

All 32 Functional Requirements have implementation evidence and passed the applicable verification path.

## Remaining gate

Verification passing does not complete the Change.

CHG-0001 must now undergo adversarial Strict Review before Documentation, Knowledge Capture, and Completion.
