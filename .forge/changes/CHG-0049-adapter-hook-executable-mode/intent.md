---
forge:
  artifact: intent
  schema: 1
change: CHG-0049
status: active
---

# CHG-0049 · Adapter Hook Executable Mode

> **Change Intent**
>
> The Claude Code Adapter materializes `check-manifest-edit.sh` without an
> executable bit, so the `PreToolUse` hook it declares fails with
> `Permission denied` and a Forge-declared protection silently does not run.
> Make Adapter-generated hook scripts materialize executable on POSIX,
> detect a non-executable hook through Forge diagnostics, and let
> `adapter update` repair an already-broken installation.

## Overview
| | |
|---|---|
| **Change** | CHG-0049 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

The Claude Code Adapter projects an illustrative enforcement hook,
`.claude/skills/forge/hooks/check-manifest-edit.sh`, and `SKILL.md`
registers it as a `PreToolUse` hook of `type: command` whose `command` is
the script path itself. Claude Code executes that path directly through a
shell.

The Adapter materialization pipeline models a generated artifact as
`(path, content, digest)` only. Nothing in the projection, planner, or
publisher carries or applies a file mode, so the publisher's
atomic-write path (`_replace_file`) lands every file — the hook
included — at the process umask default (`0644`). The script is also
committed into this repository as git mode `100644`.

Result: the shell cannot `execve` the hook (`exit 126`,
`Permission denied`), Claude Code treats the hook as failed, and the
`PreToolUse` guard that Forge declares as active does not operate. A
declared protection becomes an inoperative one, with no diagnostic
surfacing the gap.

Observed (this repository, 2026-08-26):

```
$ printf '%s' '{"tool_name":"Bash","tool_input":{"command":"echo x > .forge/changes/CHG-0001/manifest.yml"}}' \
    | "${PWD}/.claude/skills/forge/hooks/check-manifest-edit.sh"
permission denied: .../.claude/skills/forge/hooks/check-manifest-edit.sh
exit=126
```

With the executable bit set, the same invocation returns the expected
`permissionDecision: deny` JSON and `exit 0`.

## Goal

1. Adapter-generated artifacts that must be executable are materialized
   with the executable bit set on POSIX platforms, on both `install` and
   `update`.
2. The hook script is versioned in this repository as an executable file.
3. Forge diagnostics (`forge doctor` and/or `forge adapter doctor`)
   detect an installed hook that should be executable but is not.
4. `forge adapter update` repairs an existing installation whose hook was
   materialized non-executable, idempotently.
5. The fix is a property of the Adapter materialization pipeline, not of
   this repository's layout — a fresh external Forge project gets an
   executable hook with no reference to `forge-protocol` internals.

## Scope

- The Claude Code Adapter projection, the Harness-agnostic Adapter
  planning/publication pipeline, and Adapter diagnostics.
- The repository-tracked mode of `check-manifest-edit.sh`.
- Automated coverage reproducing the non-executable failure and proving
  the corrected behaviour after materialization.

## Out of Scope

- The Codex Adapter (it ships no hook script).
- Changing `SKILL.md` to invoke the script via `sh` to sidestep the
  missing permission.
- Broadening the hook mechanism itself (new matchers, new hook types, new
  enforcement surface).
- A general file-permission model for arbitrary user-owned or shared
  artifacts — only Forge-owned generated artifacts declared executable by
  their Adapter projection are in scope.
- Windows / non-POSIX permission-bit emulation beyond gracefully doing
  nothing where executable bits are not meaningful.

## Success Criteria

1. A newly installed Claude Code Adapter on a POSIX system produces
   `check-manifest-edit.sh` with an executable bit set.
2. Claude Code can run the `PreToolUse` hook without `Permission denied`.
3. A project whose hook is not executable is reported by Forge
   diagnostics.
4. Running `forge adapter update` on such a project makes the hook
   executable.
5. Tests reproduce the prior failure and demonstrate the correction.
6. No behaviour depends on the internal structure of `forge-protocol`.
