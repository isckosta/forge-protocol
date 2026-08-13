# Forge

> Build with agents. Engineer with discipline.

Forge is an open-source engineering protocol for AI-assisted software development.

AI can generate code quickly. The difficult part is establishing what should be built, proving expected behavior before implementation, verifying the resulting system, and reviewing the Change rigorously enough to discover why it might still be wrong.

Forge governs that process through Spec-Driven Development, Test-Driven Development, explicit engineering policies, proportional development Flows, Verification, adversarial Strict Review, and repository-native engineering knowledge.

**Your chat is the runtime. Your repository is the durable memory. Forge is the protocol.**

## Status

Forge is in its Foundation phase. The Core Protocol and bootstrap CLI are implemented as pre-release software under Protocol `1` (`1-draft` as the current human-readable maturity label).

## Core engineering loop

For behavioral Changes:

`Specification -> Test Design -> RED -> GREEN -> REFACTOR -> Verification -> Strict Review`

Specification defines what should exist. TDD drives how behavior is implemented. Verification determines whether sufficient evidence supports the resulting system. Strict Review attempts to falsify the Implementation.

## Core properties

- **Repository-native:** durable engineering state belongs to the repository.
- **Chat-executed:** development workflows happen inside supported coding-agent conversations.
- **Harness-agnostic:** canonical semantics do not depend on a specific coding Harness.
- **TDD-first:** reasonably testable behavioral Changes establish valid RED before production behavior.
- **Protocol-first:** the Protocol defines semantics; implementations consume them.
- **Local-first:** canonical operation requires no Forge-hosted backend.

## Bootstrap CLI

Forge currently exposes only infrastructure commands:

```text
forge version
forge init
forge validate
forge doctor
```

`forge init` requires Git and initializes `.forge/` at the Git repository root, even when invoked from a nested directory. `forge validate` validates project state against the bundled canonical Protocol. `forge doctor` performs read-only diagnostics.

The CLI deliberately does **not** expose development-lifecycle commands such as `specify`, `implement`, `verify`, or `review`. Those activities execute in the chat runtime under the Protocol.

### Development installation

Forge currently targets Python 3.12+ and is pre-release software. From a clone of this repository:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
forge version
```

The built wheel bundles the canonical Protocol resources required by the CLI, including Harness Adapter Schemas, so normal runtime operation does not depend on the source tree or a network connection.

## Harness Adapters

Harness Adapters translate resolved Forge semantics into Harness-native representation without becoming a second source of truth.

The Foundation defines:

- machine-readable Adapter manifests with independent Adapter versioning and explicit Protocol compatibility intervals;
- capability declarations for instructions, commands, skills, hooks, agent roles, and generated files;
- deterministic plans generated before mutation;
- `forge_owned`, `user_owned`, and `shared` ownership modes;
- explicit `create`, `update`, `preserve`, `conflict`, and `delete_generated` operation intents;
- repository-native installation records under `.forge/adapters/<id>/installation.yml`;
- digest-based drift detection and stale-state protection;
- explicit Harness enforcement limitations;
- conformance checks preserving canonical Flow, TDD RED, Strict Review, and repository authority;
- safe repository publication with path confinement, update preconditions, rollback, and installation-record-last semantics.

Adapters consume Effective Forge Configuration. They do not execute Forge lifecycle stages, and Protocol v1 defines no separate Adapter activation lifecycle.

No real Harness-specific Adapter ships in this Foundation Change. The first concrete Harness integration is intentionally a separate Change so the abstraction can be tested against real Harness primitives without contaminating Core semantics.

## Change as the fundamental unit

Forge organizes engineering around a `Change`, not only around features. A Change may represent a feature, bugfix, refactor, security correction, performance improvement, migration, documentation, infrastructure, or maintenance.

Every Change has Intent, classification, a Flow, Verification, Review, and Documentation Impact. Behavioral Changes are TDD-first unless an explicit justified exception applies.

## Flows

Forge defines three canonical Flows:

- **FAST** — low-semantic-impact work with minimal ceremony, never reduced quality.
- **STANDARD** — ordinary behavioral Changes and small-to-medium features.
- **FULL** — architecture, security, authorization, integrations, persistence, public contracts, major domain behavior, and other high-impact work.

Flows may escalate `FAST -> STANDARD -> FULL`. Automatic downgrade is forbidden.

## Repository layout

- `protocol/` — canonical Forge Protocol.
- `.forge/` — Forge's own dogfooding workspace.
- `src/forge_cli/` — bootstrap CLI and Harness Adapter Foundation implementation.
- `docs/adr/` — Architecture Decision Records.
- `docs/rfcs/` — Protocol evolution proposals.
- `examples/` — reference Forge Changes.

## Dogfooding

Forge develops Forge using Forge. The `.forge/` directory is active engineering state, not an example.

The first Forge Change is `CHG-0001 — Bootstrap Forge CLI`. The Harness Adapter Foundation is governed as `CHG-0002`.

## License

Apache License 2.0.
