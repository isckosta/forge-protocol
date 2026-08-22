# Forge

> Build with agents. Engineer with discipline.

Forge is an open-source engineering protocol for AI-assisted software development.

AI can generate code quickly. The difficult part is establishing what should be built, proving expected behavior before implementation, verifying the resulting system, and reviewing the Change rigorously enough to discover why it might still be wrong.

Forge governs that process through Spec-Driven Development, Test-Driven Development, explicit engineering policies, proportional development Flows, Verification, adversarial Strict Review, and repository-native engineering knowledge.

**Your chat is the runtime. Your repository is the durable memory. Forge is the protocol.**

## Status

Forge Protocol `2` is the stable engineering contract in effect (Protocol `1`
remains supported for existing Changes). The CLI is published pre-release
software on PyPI as `forge-protocol`, currently `0.1.0a1`
([PEP 440](https://peps.python.org/pep-0440/); see `RELEASING.md`). Two
concrete Harness Adapters exist — Codex and Claude Code — each with their
own independent Adapter version.

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

Forge exposes infrastructure commands and Change scaffolding:

```text
forge version
forge init
forge validate
forge doctor
forge change new <slug>
forge change new <slug> --non-behavioral
```

`forge init` requires Git and initializes `.forge/` at the Git repository root, even when invoked from a nested directory. `forge validate` validates project state against the bundled canonical Protocol. `forge doctor` performs read-only diagnostics.

`forge change new <slug>` scans the repository's existing Changes for the next
`CHG-NNNN`, resolves the enabled active Flow, prints its complete publication
plan, and then creates the required artifact placeholders. It is offline-safe
and works from an installed wheel; `--non-behavioral` omits TDD-only artifacts.

The CLI also exposes an Adapter command group for installing and managing Harness Adapters:

```text
forge adapter list
forge adapter configure <adapter>
forge adapter plan <adapter>
forge adapter install <adapter>
forge adapter validate <adapter>
forge adapter doctor <adapter>
forge adapter update <adapter>
```

For example, from an initialized project:

```bash
forge adapter install codex
```

plans, then safely publishes, the Codex Harness projection described below.

The CLI deliberately does **not** expose development-lifecycle commands such as `specify`, `implement`, `verify`, or `review`. Those activities execute in the chat runtime under the Protocol.

New to Forge? `docs/getting-started.md` is the fastest path from nothing installed to a Codex session ready to receive a Change, and `examples/README.md` maps five worked scenarios (a FAST bugfix, a STANDARD feature, a FULL feature, a Strict Review remediation cycle, and a Codex Adapter project) to real, repository-native evidence.

### Installation

Forge targets Python 3.12+ and is published pre-release software:

```bash
pip install forge-protocol
forge version
```

The published wheel bundles the canonical Protocol resources required by the CLI, including Harness Adapter Schemas, so normal runtime operation does not depend on a network connection.

### Development installation

To work on Forge itself, install from a clone of this repository instead:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
forge version
```

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

### Codex Adapter

The first concrete Harness integration targets Codex while preserving the generic Adapter Core boundary.

- packaged `adapter.yml` and `capabilities.yml` resources are the runtime authority for Adapter identity and capability evidence;
- `skills` and deterministic generated files are supported, while hooks, commands, agent roles, and persistent instructions remain unsupported until evidence proves otherwise;
- deterministic `forge-flow.md` and `forge-contract.md` resources are generated from canonical Forge input;
- stable workflow framing comes from the packaged Adapter resource, while stage order and Gate content remain derived from canonical Flow state;
- projection generation does not invent a Codex publication path; publication requires an explicit or evidence-backed target;
- planning, ownership, collision handling, installation state, and drift detection reuse the generic Adapter Core;
- normal descriptor loading, projection, and planning require neither live vendor access nor a Codex/OpenAI SDK.

Codex workflow instructions represent Forge requirements but do not claim technical enforcement. Canonical repository-native Forge state remains authoritative, and no separate Adapter activation lifecycle is introduced.

### Claude Code Adapter

The second concrete Harness integration, proving the generic Adapter Core needed no vendor-specific concept to support it (two pre-existing Codex-only leaks in the generic Core were found and fixed as part of that proof).

- three real projection mechanisms, all `forge_owned` under one shared publication root (`.claude`): a Skill (`.claude/skills/forge/`), a `CLAUDE.md` pointer, and an illustrative `PreToolUse` enforcement hook that denies in-place mutation of frozen Change review-control files without blocking ordinary Git commands over the same paths;
- a materially richer, dated capability profile than Codex's: `persistent_instructions`, `commands`, `skills`, `hooks`, `agent_roles`, and `generated_files` are all `supported`, versus Codex's `skills`/`generated_files` only;
- both Adapters share one conformance test suite and the same generic planning, ownership, drift-detection, and publication mechanics — no Adapter-specific fork of Core behavior.

```bash
forge adapter install claude-code
```

installs it the same way `forge adapter install codex` does. See `examples/golden-path-claude-code/` for a fully executed (not merely described) end-to-end run.

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

The first Forge Change is `CHG-0001 — Bootstrap Forge CLI`. The Harness Adapter Foundation is governed as `CHG-0002`, the first concrete Codex integration as `CHG-0004`, and the second concrete Harness Adapter — Claude Code — as `CHG-0018`.

## License

Apache License 2.0.
