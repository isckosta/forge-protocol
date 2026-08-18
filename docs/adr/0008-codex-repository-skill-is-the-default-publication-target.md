# ADR-0008 — Codex repository skill is the default publication target

Status: Accepted

## Context

ADR-0007 separates logical Codex projection resources from filesystem
publication and permits publication only to an explicit or evidence-backed
destination. At the time of CHG-0004, Forge had no documented repository path
and correctly shipped no default.

Official Codex documentation observed on 2026-08-13 now defines
`$REPO_ROOT/.agents/skills` as a repository scope for skills shared throughout
the repository. The Forge Roadmap also requires `forge adapter install codex`
to produce a usable projection without manual prompt copying.

## Decision

The packaged Codex Adapter uses `.agents/skills/forge` as its evidence-backed
repository publication target. It emits a valid `SKILL.md` and derived
references beneath that root.

An explicit command target overrides project Adapter configuration, which
overrides the packaged default. Every target remains repository-relative and
passes generic path-safety and ownership checks.

Forge does not write to `.codex/`, a home directory, or another global target
by default. Repository-native Forge state remains authoritative.

Source: https://developers.openai.com/codex/skills

## Consequences

The four-command onboarding path can install a Codex-discoverable Forge skill
without an invented vendor convention or manual copying. Installation remains
deterministic and offline because the evidence and default ship with the
Adapter release.

ADR-0007 remains in force: another Harness or a future Codex surface still
requires packaged evidence or explicit configuration before publication.
