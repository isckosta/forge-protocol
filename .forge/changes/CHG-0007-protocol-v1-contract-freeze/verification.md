---
forge:
  artifact: verification
  schema: 1
change: CHG-0007
status: passed
---

# Verification — Protocol v1 Contract Freeze

## Scope

Verification covered all 16 Requirements and six acceptance scenarios across
stable version identity, compatibility/deprecation policy, schema catalog
closure, canonical instance validity, Flow/Gate semantics, truth-preserving
historical migration, and installed-wheel availability.

## Automated evidence

### Focused contract verification

```text
.venv/bin/pytest tests/contract/test_protocol_contract.py -v
24 passed
```

Coverage includes:

- catalog uniqueness, file closure, meta-schema validity, and identity;
- all canonical YAML instances selected by their schema identifier;
- Adapter Protocol bounds and existing semantic interval ordering tests;
- Flow identity, exact stage order, requiredness, conditional applicability,
  RED Gates, and Completion Gates;
- closed normative Policy structures and semantic dimensions;
- complete/compliant TDD evidence requirements and explicit exception reasons;
- preservation of both CHG-0004 requirement-task and acceptance mappings.

### Full suite and distribution

The final verification command is:

```text
uv --cache-dir /tmp/forge-protocol-uv-cache run --with pip --extra test pytest -v
162 passed in 2.98s
```

The integration distribution test builds an isolated wheel, extracts it away
from the source package import path, loads the packaged schema catalog, asserts
catalog/file closure, validates every Draft 2020-12 schema and identity, and
runs with `PYTHONNOUSERSITE=1` and `PIP_NO_INDEX=1` for the installed probe.

The CI wheel probe independently loads the installed catalog and every
cataloged schema with network proxies disabled.

### Repository hygiene

```text
git diff --check
```

No whitespace error is accepted. Local `.codex/`, `docs/superpowers/`, the
session document, and `uv.lock` remain untracked and are excluded from commits.

## Acceptance scenarios

- **AC-001:** `forge version` reports `Forge Protocol 1` and excludes
  `1-draft`.
- **AC-002:** the catalog closes exactly over all schema files and identities.
- **AC-003:** canonical repository instances validate offline.
- **AC-004:** schema bounds reject non-Protocol identifiers; semantic Adapter
  validation rejects `min >= max_exclusive`.
- **AC-005:** FAST, STANDARD, and FULL retain common RED and Completion Gates,
  exact stage sequences, and canonical requiredness.
- **AC-006:** CHG-0004 mappings are identical after structural migration.

## Historical evidence integrity

Initial CHG-0007 working-tree RED observations were not independently
auditable from Git because tests and implementation first appeared together.
They are therefore Verification coverage only. Three Strict Review remediation
cycles have durable test-only RED and subsequent GREEN commits.

CHG-0005 retains its historical behavior as Verification evidence but is now an
explicit TDD exception because its original artifact stored no auditable RED or
GREEN details. No missing evidence was reconstructed.

## External review surface

No pull request exists yet for CHG-0007. The blocking external-review-thread
condition is therefore satisfied trivially for local Verification, but it must
be re-evaluated before Completion if a pull request is opened.

## Result

All Requirements and acceptance scenarios are covered. The final fresh run
passed all 162 tests, including distribution isolation and schema catalog
closure.
