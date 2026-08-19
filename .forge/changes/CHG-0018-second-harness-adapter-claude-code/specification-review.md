# Specification Review — Second Harness Adapter (Claude Code)

## Verdict

**APPROVED, with 1 MINOR finding resolved in place.** No BLOCKER or MAJOR.
Specification proceeds to Architecture.

## Findings

### SR-001 — MINOR — FR-006's hook could plausibly block ordinary `git add`/`git commit` of Forge review-control files

**Finding**: The first draft of FR-006 described the hook as blocking any
Bash command that would "directly mutate" the three named review-control
files, without excluding version-control commands. `git add`/
`git commit .forge/changes/*/manifest.yml` genuinely "mutates" the
repository's tracked state of that file and would match an
under-specified pattern — but is exactly how every real Change in this
repository, including this one, records its own provenance/manifest
updates (see `CHG-0017`'s own commit history). A hook that blocked it
would break the normal workflow it's meant to protect, not enforce
anything useful.

**Resolution applied**: FR-006 amended to name the exact in-place-mutation
command shapes the hook matches (`sed -i`, `perl -i`, `truncate`, shell
redirection) and explicitly exclude read-only/VCS commands
(`cat`/`ls`/`git add`/`git commit`/`git status`/`git diff`/`git show`/
`grep`).

## Checked and found sound

- FR-001–FR-002 (the two Core-leak fixes) map directly to concrete,
  already-confirmed findings in `discovery.md`, not speculative cleanup.
- FR-005's CLAUDE.md path choice (`.claude/CLAUDE.md`, not root
  `CLAUDE.md`) avoids the SHARED-ownership/merge problem entirely, per
  `discovery.md`'s own reasoning — checked against `ownership.py`'s actual
  `classify_artifact` logic (read directly during Discovery, not assumed).
- FR-009's new Contract rule number (`C-074`) is the correct next free
  number: `protocol/contract/engineering.md` currently ends at `C-073`
  (`CHG-0017`).
- AC-002's explicit "no shim, since nothing outside `codex/driver.py`
  imports it" default is checked against Discovery's own grep — no
  unresolved ambiguity carried forward.
- NFR-001's exact wording ("no file under `adapters/*.py`... references
  `codex`... except `packaged.py`'s composition-root imports") matches
  what Discovery's Explore report found is the *only* legitimate,
  intentional cross-reference — not a loophole.

## Conclusion

One MINOR finding, resolved without reopening Discovery. Specification is
APPROVED and proceeds to Architecture.
