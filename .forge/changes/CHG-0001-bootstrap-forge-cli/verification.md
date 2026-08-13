---
forge:
  artifact: verification
  schema: 1
change: CHG-0001
status: passed
---

# Verification — Bootstrap Forge CLI

## Result

Verification passed. One material distribution defect was discovered during the initial verification and corrected through regression-first TDD. Strict Review later produced additional behavioral fixes; the full test and isolated-distribution verification were rerun after those fixes.

## Verification finding — V-001

Severity: MAJOR

Status: RESOLVED

The first isolated-wheel verification built and installed the package and executed `forge version`, but `forge validate` failed after initialization because the canonical Project Schema was resolved through a source-tree-relative path.

Initial failing distribution evidence:

- workflow run: `31670483873`;
- job: `94353874439`;
- observed failure: canonical Project Schema missing from the installed environment.

Regression RED:

- workflow run: `31670537580`;
- job: `94354031510`;
- observed failure: `ModuleNotFoundError: No module named 'forge_cli.protocol_resources'`.

Resolution:

- canonical Protocol resources are bundled under `forge_cli/resources/protocol`;
- runtime resolution prefers packaged resources;
- source-tree Protocol resolution is only a development fallback.

Initial GREEN evidence:

- Tests workflow run: `31670613378`;
- Distribution Verification run: `31670613450`.

## Final post-review verification

Verified code commit: `094e06885cc9c59ff3bd3ce6f89596b7c6e4d14e`.

### Automated suite

- workflow run: `31671363071`;
- job: `94356481812`;
- result: SUCCESS;
- Pytest step: SUCCESS.

### Isolated distribution

- workflow run: `31671363034`;
- job: `94356481901`;
- result: SUCCESS.

The distribution workflow verified:

1. building the wheel;
2. creating a clean Python 3.12 virtual environment;
3. installing only the wheel and declared runtime dependencies;
4. executing installed `forge version` outside the source tree;
5. creating a new Git repository;
6. executing `forge init` from a nested directory;
7. executing `forge validate` on the generated workspace;
8. executing `forge doctor` on the generated workspace;
9. running the installed CLI with HTTP/HTTPS/ALL proxies pointed at an unreachable local endpoint;
10. auditing runtime dependencies for prohibited AI SDK, agent framework, and database framework dependencies.

All checks passed.

## Strict Review regression verification

Review fixes were driven through additional TDD cycles:

- TDD-010: safe YAML serialization for YAML-significant repository names;
- TDD-011: cross-platform-safe workspace paths and exclusive initialization locking;
- TDD-012: missing Git executable classified as an environment failure.

The final automated and distribution runs above include those fixes and the Protocol version metadata refactor.

## Requirement status

All 32 Functional Requirements have implementation and verification evidence.

Verification status: PASSED.
