---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0001
status: complete
---

# Knowledge Capture — Bootstrap Forge CLI

## Durable decisions confirmed by implementation

### The CLI distribution carries canonical Protocol resources

The installed Forge CLI must be able to validate and diagnose a project without access to the Forge source repository and without downloading Protocol files.

The wheel therefore bundles the canonical `protocol/` tree under `forge_cli/resources/protocol`.

Runtime resolution prefers bundled resources. Source-tree `protocol/` is only a development fallback for editable repository execution.

### Protocol identity and maturity label are distinct

Protocol compatibility is represented by the stable identifier `1` in project configuration.

`1-draft` is the current human-readable maturity/display label for that Protocol identifier.

These values are centralized in `forge_cli.version`.

### Initialization publishes only complete workspaces

Forge builds a workspace in a temporary staging directory and publishes it as `.forge/` only after all planned files are written.

Workspace plan paths are canonical POSIX-relative paths. Backslash ambiguity, absolute paths, traversal components, NUL bytes, and file/parent collisions are rejected before materialization.

### Forge initialization is serialized across cooperating processes

Initialization uses an exclusive `.forge.init.lock` file. A process only removes a lock it successfully acquired.

This prevents two Forge initialization processes from entering workspace publication concurrently.

Hard crashes may leave a stale lock or staging directory. CHG-0001 intentionally does not auto-delete such artifacts because lock liveness cannot be determined safely in all environments. A future Doctor capability should diagnose stale initialization artifacts.

### Exit codes are part of the CLI contract

- `0`: success;
- `2`: invalid or conflicting Forge project state;
- `3`: required environment capability unavailable or current path outside a required Git repository;
- `70`: unexpected internal failure.

### The public CLI remains infrastructure-only

The bootstrap command surface is:

- `forge version`;
- `forge init`;
- `forge validate`;
- `forge doctor`.

Specification, implementation, Verification, Review, and Resolution remain chat-executed Protocol activities and are intentionally absent from the CLI.
