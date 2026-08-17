---
forge:
  artifact: intent
  schema: 1
change: CHG-0010
status: approved
---

# Intent — Adapter CLI and Codex Installation UX

## Problem

Forge ships a generic Adapter Core and a Codex Adapter, but adopters must call
Python APIs, choose an undocumented publication target, and manually bridge
generated resources into Codex. The public CLI exposes no Adapter commands.

Consequently, the Roadmap's four-command onboarding path is not usable and the
existing safety, ownership, drift, and installation-record semantics are not
available as a coherent product experience.

## Desired outcome

Deliver a complete `forge adapter` command group that discovers packaged
Adapters and safely configures, plans, installs, validates, diagnoses, and
updates a repository-scoped Codex skill. A clean Git repository must progress
from `forge init` to a discoverable Forge workflow in Codex without manual
prompt copying.

## Success criteria

- `.agents/skills/forge/SKILL.md` is the evidence-backed default Codex target.
- Planning is deterministic, visible, and precedes every mutation.
- Installation and update preserve ownership and stop on collision or drift.
- Repeated installation with identical inputs is a true no-op.
- Validation and doctor output are actionable and stable.
- The full experience works offline from an installed wheel.
- No lifecycle execution commands are introduced.

## Classification

FULL is required because this Change creates a public multi-command interface,
extends Adapter Core state transitions and deletion behavior, changes the
Codex publication contract, and defines safety-sensitive mutation semantics.

## Constraints

- Repository-native Forge state remains authoritative.
- Codex-specific behavior remains outside the generic Adapter Core.
- No command writes to `.codex/` or a user-global directory by default.
- User-authored files are never silently adopted or overwritten.
- Runtime behavior does not depend on vendor network access.
- Local `.codex/`, `docs/superpowers/`, `uv.lock`, and session documents are
  excluded from the Change.

## Out of scope

- lifecycle commands such as `forge specify`, `forge implement`, or
  `forge review`;
- interaction-language resolution;
- a second Harness Adapter;
- hosted Adapter discovery or a Forge backend;
- global Codex installation;
- publishing the final Forge v1 release.
