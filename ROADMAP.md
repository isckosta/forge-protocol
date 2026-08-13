# Forge Roadmap

> From Foundation to a stable, installable engineering protocol.

## Goal

Forge v1 should let a developer install Forge in a real Git repository, configure a supported coding Harness, open the Harness chat, and begin a correctly governed Change without manually reconstructing Forge internals.

The chat remains the runtime. The repository remains durable memory. Forge remains the protocol.

## Current position

Forge already has the core Foundation: FULL, STANDARD, and FAST Flows; TDD-first behavioral development; Verification; adversarial Strict Review; repository-native Change state; bootstrap CLI; generic Harness Adapter Core; and a concrete Codex Adapter.

The remaining work is primarily contract stabilization, productization, external validation, Harness-independence proof, and release engineering.

Directional maturity:

| Area | Approximate maturity |
| --- | ---: |
| Protocol / Foundation | 90% |
| Bootstrap CLI | 70% |
| Harness Adapter Core | 90% |
| Codex Adapter | 80% |
| Developer experience | 30% |
| Productization | 30% |
| Release readiness | 20% |

These percentages are directional only. Release readiness is determined by the gates below.

## Strategic constraints

1. **Chat is the lifecycle runtime.** The CLI installs, configures, validates, diagnoses, migrates, plans, and safely mutates Adapter artifacts. It does not replace chat with lifecycle commands.
2. **Repository is durable memory.** Normal Forge operation must not require a hosted Forge backend, account, or remote database.
3. **Protocol is authoritative.** Harness projections are derived representations, never a competing source of truth.
4. **TDD-first remains a behavioral invariant.** Reasonably testable behavioral Changes establish valid RED before production behavior.
5. **Strict Review remains adversarial.** Completion requires Verification, Review, and reconciliation of blocking external review threads when an external review surface exists.
6. **FAST reduces ceremony, not quality.** Quality invariants remain consistent across Flows.
7. **Harness independence must be demonstrated.** A second real Harness Adapter is required before the Adapter Core is considered proven for v1.

# Roadmap to v1

Roadmap stages do not reserve Change identifiers. Forge assigns the next stable
`CHG-NNNN` identifier when a stage begins as an actual repository-native
Change. This keeps planning labels from colliding with remediation or other
work discovered before a stage starts.

## Protocol v1 Contract Freeze

### Objective

Promote the current draft/Foundation semantics into a stable v1 contract suitable for external adoption.

### Scope

- audit canonical Protocol documents for contradictions, duplication, ambiguous terminology, and undocumented invariants;
- reconcile FULL, STANDARD, and FAST semantics;
- freeze lifecycle terminology and Gate names;
- freeze TDD-first semantics and justified exception rules;
- freeze Verification, Strict Review, and Completion semantics;
- freeze external blocking-review-thread reconciliation semantics;
- freeze ownership modes: `forge_owned`, `user_owned`, and `shared`;
- freeze Adapter capability, limitation, repository-authority, and derived-projection semantics;
- audit Protocol schemas and identifiers;
- define v1 compatibility guarantees;
- define backward-compatible versus breaking Protocol evolution;
- define deprecation policy;
- establish stable Protocol version naming.

### Exit criteria

- canonical Protocol passes consistency review;
- schemas are versioned and validated;
- canonical Flows have no contradictory Gates;
- compatibility and deprecation policies are documented;
- v1 semantics are frozen except for release-blocking corrections;
- Strict Review passes with zero blocker/major findings.

## Adapter CLI & Codex Installation UX

### Objective

Make Forge usable without requiring users to understand Adapter internals or manually copy Harness instructions.

### Target experience

```bash
pipx install forge-protocol
cd my-project
forge init
forge adapter install codex
```

Opening Codex afterward should expose the effective Forge workflow through the supported Harness projection mechanism.

### Required capabilities

The final command names are subject to Specification, but v1 needs equivalents of:

```text
forge adapter list
forge adapter install <adapter>
forge adapter configure <adapter>
forge adapter plan <adapter>
forge adapter validate <adapter>
forge adapter doctor <adapter>
forge adapter update <adapter>
```

### Scope

- Adapter discovery from packaged resources;
- Protocol compatibility checks before installation/update;
- deterministic plan-before-mutation;
- explicit publication-target resolution;
- installation records;
- ownership-aware mutation;
- collision and stale-state protection;
- drift diagnostics;
- dry-run/plan visibility;
- safe updates;
- Codex installation through the generic Adapter Core;
- actionable enforcement-limitation diagnostics;
- idempotent installation;
- offline operation after package installation where vendor discovery is unnecessary.

### Product constraint

Lifecycle commands such as `forge specify`, `forge implement`, `forge verify`, and `forge review` remain intentionally outside the CLI. Lifecycle execution stays in chat.

### Exit criteria

- a clean repository goes from `forge init` to usable Codex projection through documented CLI commands;
- installation is deterministic, safe, and idempotent;
- user-owned files cannot be silently overwritten;
- drift is detectable;
- behavior works from an installed wheel;
- onboarding requires no manual prompt copying.

## Interaction Language Resolution

### Objective

Separate Forge's canonical implementation language from the language used to interact with the developer.

Protocol, source, schemas, IDs, and canonical Forge repository documentation remain English-first. User-facing generated prose and Harness interaction may use project/developer language.

### Proposed configuration

```yaml
interaction:
  language: auto
```

### Intended precedence

```text
explicit project language
    -> repository/context language
    -> active user/chat language
    -> English fallback
```

The Specification must determine which signals are deterministic configuration and which are only Harness hints.

### Invariants

- schema keys remain stable;
- requirement and Change IDs remain stable;
- machine-readable state remains language-independent;
- translation cannot change Gate semantics;
- deterministic project configuration overrides heuristic detection.

### Exit criteria

- non-English interaction requires no manual prompt rewriting;
- canonical machine-readable semantics remain interoperable;
- language behavior has conformance coverage.

## End-to-End Examples & External Project Validation

### Objective

Prove Forge outside its own repository and create a practical onboarding path.

### Required examples

```text
examples/
  fast-bugfix/
  standard-feature/
  full-feature/
  strict-review-remediation/
  codex-adapter-project/
```

Each example should contain real repository-native Change evidence rather than explanatory prose alone.

### External validation matrix

Exercise Forge against at least:

- Laravel/PHP;
- Node.js/TypeScript;
- Python;
- a monorepo;
- an existing/legacy repository.

Validation should cover FAST bugfix, STANDARD feature, FULL feature, Strict Review remediation, Adapter drift, and user-owned collision behavior where applicable.

### Golden path

Create `docs/getting-started.md` with a first successful Change as the primary onboarding path:

```text
1. Install Forge
2. Initialize repository
3. Install/configure Codex Adapter
4. Open Codex
5. Request a small Change
6. Observe Flow classification
7. Observe TDD, Verification, and Review evidence
```

### Exit criteria

- examples contain complete relevant Change artifacts;
- external validation has no unresolved blocker/major findings;
- multiple programming ecosystems are demonstrated;
- at least one legacy repository is validated;
- a developer unfamiliar with Forge can complete the golden path without studying internal architecture first.

## Second Harness Adapter

### Objective

Demonstrate that the Harness Adapter Core is genuinely generic using a second materially different coding Harness.

Claude Code is a strong candidate, but Harness selection must use current documented capabilities when the Change begins.

### Scope

- dated capability evidence;
- independent Adapter version and Protocol compatibility interval;
- `enforced`, `represented`, and `unsupported` invariant assessment;
- deterministic projection;
- evidence-backed or explicit publication target only;
- reuse of generic planning, ownership, state, drift, limitations, and publication;
- isolated distribution validation;
- explicit review of any pressure to change the generic Core.

### Architecture test

The key question is not merely whether the second Adapter works. It is whether it can be implemented without introducing vendor-specific concepts into the generic Adapter Core.

### Exit criteria

- second Adapter works end-to-end;
- no vendor SDK is introduced without Specification justification;
- Core changes, if any, are demonstrably Harness-independent;
- both Adapters pass shared conformance tests;
- Adapter architecture is sufficiently proven for v1 freeze.

## Release Engineering & v1 Release Candidate

### Objective

Turn the mature repository into a reproducible, upgradeable, externally consumable release.

### Versioning

Define and enforce independent versioning rules for:

- Forge CLI/package;
- Forge Protocol;
- Harness Adapters;
- schemas and repository-native installation state.

### Distribution

Establish:

- PyPI publication;
- GitHub Releases;
- immutable version tags;
- wheel/sdist verification;
- package-content verification;
- clean-environment installation tests;
- promised offline-runtime checks;
- release notes.

### Migration strategy

Define migration architecture before stable formats become accidental permanent contracts.

Expected direction, subject to Specification:

```text
forge doctor
forge migrate --check
forge migrate
```

Migration architecture must account for future transitions such as project schema versions, Protocol compatibility changes, Adapter installation schemas, Adapter upgrades, and deprecated canonical fields.

### Release progression

```text
0.1.0-alpha.1
    -> external real-world validation
0.1.0-beta.1
    -> stabilization and fixes
1.0.0-rc.1
    -> contract freeze; blocker/major fixes only
1.0.0
```

Additional prereleases are evidence-driven, not deadline-driven.

### Exit criteria

- package installs from the public distribution channel in a clean supported environment;
- GitHub Release and package release map to the same source revision;
- migration policy exists and current-state/no-op migration is testable;
- release documentation is complete;
- all v1 blocker/major findings are closed;
- final Verification and Strict Review pass;
- Protocol compatibility contract is frozen.

# Release gates

## Gate A — Protocol stability

Protocol v1 is frozen, schemas validate, Flow semantics are reconciled, compatibility/deprecation policy exists, and no blocker/major Protocol finding remains.

## Gate B — Installation usability

A developer can reach a usable Forge-enabled repository without manually copying prompts or editing internal Adapter resources.

## Gate C — Real-world validation

Forge has been exercised outside its own repository across multiple ecosystems and at least one legacy codebase.

## Gate D — Harness independence

At least two concrete Harness Adapters demonstrate the generic Core boundary.

## Gate E — Distribution

Public artifacts install and run from clean environments with package resources, schemas, Adapter resources, and offline guarantees verified.

## Gate F — Upgrade safety

A documented migration and compatibility model exists before stable repository schemas are promised indefinitely.

## Gate G — Review integrity

All release-blocking findings and blocking external review threads are reconciled. Verification and Strict Review pass on the release-candidate revision.

# Explicitly deferred beyond v1

The following are not required for v1 and should not distract from the roadmap without new evidence:

- Forge Cloud;
- hosted workflow orchestration;
- centralized Forge database;
- mandatory user accounts;
- web dashboard;
- graphical lifecycle editor;
- organization control plane;
- remote Change execution service;
- large Adapter marketplace;
- dozens of Harness integrations;
- lifecycle CLI commands that move specification/implementation/review out of chat;
- telemetry required for normal local operation.

These may be proposed later through explicit RFCs/Changes.

# Recommended execution order

```text
Protocol v1 Contract Freeze
    |
    v
Adapter CLI & Codex Installation UX
    |
    v
Interaction Language Resolution
    |
    v
End-to-End Examples & External Validation
    |
    v
Second Harness Adapter
    |
    v
Release Engineering & v1 RC
```

Discovery for Protocol v1 Contract Freeze and Adapter CLI & Codex Installation UX may overlap: usability evidence found while designing Adapter installation should feed the Protocol freeze rather than being ignored until after freeze.

# Definition of Forge v1

Forge v1 is ready when a developer who did not design Forge can:

1. install Forge from a public package;
2. initialize an existing or new Git repository;
3. install a supported Harness Adapter without manually copying prompts;
4. open the supported coding Harness and receive Forge semantics automatically;
5. execute FAST, STANDARD, and FULL Changes through chat;
6. obtain repository-native specification/TDD/Verification/Review evidence appropriate to the Flow;
7. rely on user-owned files being protected from silent Adapter mutation;
8. diagnose Adapter drift and compatibility problems;
9. work in a configured interaction language without changing canonical machine-readable semantics;
10. upgrade Forge through a documented compatibility/migration path;
11. reproduce the golden path in more than one programming ecosystem;
12. rely on Adapter architecture validated against at least two real Harnesses.

At that point Forge is no longer merely a Foundation or protocol experiment. It is a stable, installable engineering protocol with a proven operating model.

# Primary success metric

The primary v1 metric is not the number of Protocol pages, CLI commands, Adapters, or generated artifacts.

> A developer can install Forge in a real repository and begin a correctly governed Change in roughly five minutes, without needing to understand Forge's internal architecture first.

Every roadmap item should be evaluated against that outcome.
