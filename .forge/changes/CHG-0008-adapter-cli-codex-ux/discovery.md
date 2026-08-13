---
forge:
  artifact: discovery
  schema: 1
change: CHG-0008
status: complete
---

# Discovery — Adapter CLI and Codex Installation UX

## Repository baseline

The Change began from commit `df0cb42020604d54ea1673106d746bc855bafb5e`
on branch `feat/chg-0008-adapter-cli-codex-ux` in an isolated worktree. The
baseline suite passed all 162 tests after the local test environments received
the `pip` module required by the existing isolated-wheel test.

## Existing CLI and Core

`src/forge_cli/app.py` currently exposes only `version`, `init`, `validate`,
and `doctor`. Typer already provides the command framework and the CLI uses
stable domain/environment exit-code conventions.

The generic Adapter Core already provides:

- immutable, deterministically ordered plans;
- Protocol compatibility checks;
- ownership classification for Forge-owned, user-owned, and shared files;
- installation records and generated-artifact digests;
- drift detection;
- path traversal and symlink protection;
- publication preconditions, atomic replacement, and rollback;
- conformance and explicit limitation reporting.

The missing product layer is packaged discovery plus orchestration from an
initialized project into those primitives. Core also lacks an explicit no-op
intent and implemented safe publication for obsolete generated artifacts.

## Existing Codex Adapter

The Codex Adapter descriptor, capability evidence, projection renderer,
invariant assessment, target resolver, and generic Core integration are
packaged under `src/forge_cli/adapters/codex/`. Its current projection is an
in-memory pair of Markdown resources. Target resolution deliberately returns
no target unless an explicit or evidence-backed path is supplied.

CHG-0004 made that conservative choice because it had no documented Codex
repository target. It remains the correct fallback rule: no target may be
invented when neither evidence nor explicit configuration exists.

## Current Codex publication evidence

Official OpenAI documentation observed on 2026-08-13 states that Codex scans
`.agents/skills` from the current working directory through the repository root
and identifies `$REPO_ROOT/.agents/skills` as the location for skills available
throughout a repository. It also defines a skill as a directory containing a
required `SKILL.md` plus optional references, scripts, assets, and metadata.

Source: https://developers.openai.com/codex/skills

This is sufficient evidence for the Codex Adapter release to package
`.agents/skills/forge` as its repository-scoped default. It does not justify a
`.codex/` destination or a user-global mutation.

## Configuration boundary

Project configuration currently allows only a string list of Harness names.
Embedding Adapter-specific settings in `.forge/forge.yml` would either require
a public project-schema expansion or lossy YAML rewriting. A dedicated
user-owned `.forge/adapters/<adapter-id>/config.yml` keeps Adapter configuration
independent from Forge-owned derived installation state at
`.forge/adapters/<adapter-id>/installation.yml`.

## Product decomposition decision

The Roadmap stage is implemented as one FULL Change rather than a partial CLI.
Adapter Core and the concrete Codex Adapter already exist, so independent TDD
cycles can deliver the seven commands without exposing a temporary interface
or repeating integration and Strict Review across two incomplete Changes.

## Safety gaps to resolve

- Identical desired and recorded content is currently classified as `UPDATE`,
  causing unnecessary writes rather than a no-op.
- `DELETE_GENERATED` exists in the plan vocabulary but the publisher rejects
  it.
- Installation records do not yet model obsolete generated paths during an
  update.
- A service boundary is needed to build consistent snapshots and prevent CLI
  handlers from duplicating planning rules.
- Read-only validation and diagnostic results need stable domain findings and
  command output.
