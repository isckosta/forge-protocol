---
forge:
  artifact: discovery
  schema: 1
change: CHG-0056
status: pending
---

# Discovery — CHG-0056 Capability Exposure

## Executive Summary

The native extension unit is a skill, not a Forge slash command. Codex officially scans direct child skill directories under `.agents/skills`, exposes them through the skill selector, and supports explicit `$skill` invocation. Slash remains a Harness UX detail.

## Investigation

- The canonical loader had no deterministic catalog view; adapters had no Capability input.
- Codex requires each skill to be a directory with `SKILL.md`, so the publication root must be `.agents/skills` while the existing `forge/SKILL.md` path remains unchanged.
- Claude Code's packaged evidence declares skills and commands supported; its `.claude` root can contain sibling `skills/<capability>/` directories.
- The generated skill envelope will reference the exact canonical `CAPABILITY.md`, avoiding duplicated competency behavior.
