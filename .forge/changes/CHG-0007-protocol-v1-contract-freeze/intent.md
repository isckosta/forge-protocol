---
forge:
  artifact: intent
  schema: 1
change: CHG-0007
status: approved
---

# Intent — Protocol v1 Contract Freeze

## Problem

Forge implements the Foundation semantics but still describes Protocol 1 as
`1-draft`. Its compatibility guarantees and deprecation rules are incomplete,
not every canonical machine-readable artifact has an explicit schema entry,
and completed repository-native Changes contain structural drift from the
current schemas.

Without a freeze, adopters cannot distinguish a compatible Protocol 1
extension from a breaking change, and passing tests do not prove that the
repository's own artifacts satisfy the contract it publishes.

## Desired outcome

Promote integer Protocol `1` to a stable contract with the human label `1`,
document its evolution rules, validate all supported schemas and canonical
instances offline, reconcile canonical Flow/Gate semantics, and migrate
schema-invalid historical structures without changing their meaning.

## Success criteria

- Protocol 1 has stable naming and explicit compatibility/deprecation rules.
- Every supported machine-readable schema is cataloged and itself valid.
- Canonical Protocol and repository-native instances pass schema validation.
- FULL, STANDARD, and FAST retain consistent quality Gates.
- Historical TDD, Verification, and Review facts remain unchanged.
- Verification and adversarial Strict Review pass with no blocker or major.

## Classification

FULL is required because this Change freezes a public contract, changes
compatibility policy, spans canonical Protocol areas, and affects externally
consumed version and schema semantics.

## Constraints

- Protocol compatibility remains integer `1`.
- CLI, Protocol, Schema, and Adapter versions remain independent.
- Validation must be deterministic and offline.
- Structural migration must not falsify historical evidence.
- No lifecycle execution commands are added to the CLI.
- Local `docs/superpowers/` content is excluded from version control.

## Out of scope

- Adapter installation UX;
- interaction-language resolution;
- external project examples;
- a second Harness Adapter;
- packaging and publishing the v1 release.
