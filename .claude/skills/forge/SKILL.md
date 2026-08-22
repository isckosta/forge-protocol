---
name: forge
description: Use for Forge-governed engineering Changes in this repository.
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "${CLAUDE_PROJECT_DIR}/.claude/skills/forge/hooks/check-manifest-edit.sh"
---

## Forge Workflow Instructions

Repository-native Forge state remains authoritative. Use the effective Flow and
Engineering Contract references in this skill as derived, repository-local
representations; do not redefine their lifecycle here.

- Classify the work and resolve the applicable effective Flow before acting.
- Preserve every applicable Flow gate, including TDD RED-before-behavior and
  Strict Review requirements.
These instructions represent Forge requirements; they are not technical enforcement.

## Effective Forge references

- [Engineering Contract](references/engineering-contract.md)
- [Artifact Structure](references/artifact-structure.md)
- [Decision Rules](references/decision-rules.md)
- [Flow `fast`](references/flows/fast.yml)
- [Flow `full`](references/flows/full.yml)
- [Flow `standard`](references/flows/standard.yml)

Interaction language: auto -- use the active chat's observed language if there is one, otherwise English (C-070-C-073).

## Illustrative enforcement hook

This skill registers a `PreToolUse` hook (active once this skill has been invoked in a session, not from session start) that denies a `Bash` command matching an in-place-mutation shape (`sed -i`/`perl -i`/`truncate`/output redirection) targeting `.forge/changes/*/manifest.yml`, `provenance.yml`, or `review.md`. It does not match read-only or version-control commands (`cat`/`ls`/`git add`/`git commit`/`git status`/`git diff`/`git show`/`grep`) against the same paths. This is Core's honest boundary (C-073): the hook enforces this one narrow, mechanically-checkable pattern; it is not a general security boundary and is not represented as one.

### Flow `fast` gate obligations

- RED must be executed.
- RED must fail for the expected reason.
- Completion requires Verification to pass.
- Completion requires Strict Review to pass.
- Completion requires all blocking review threads on any active external review surface to be resolved.
- Completion requires Documentation Impact to be evaluated.
- Completion requires TDD compliance or an explicit, recorded exception.

### Reviewer/Resolver independence

- Under Protocol 2, Strict Review must run in an Execution and Execution Context independent from the implementation or resolution that produced the revision under review.
- Merely changing Role inside the same conversation, thread, session, or reasoning context is self-review and cannot satisfy Strict Review.
- Finish the Implementation/Resolution and all reviewable evidence before freezing the review subject.
- Before freezing, ensure the effective reviewable Git workspace is clean: no committed post-subject delta, staged reviewable changes, unstaged reviewable changes, or Git-visible untracked reviewable files.
- Identify the concrete immutable subject revision. In Git, use the subject commit SHA; `revision.id` alone is not sufficient.
- Record the frozen subject in `provenance.yml`; the Review Iteration references it through `subject_provenance`.
- Only the exact Change-local `manifest.yml`, `provenance.yml`, and `review.md` paths are review-control metadata that may differ after the freeze; do not generalize that exception to the Change directory, matching basenames, symlinks, or rename targets.
- Git-ignored cache/editor/temp files do not count as reviewable workspace mutations for the freeze invariant.
- Re-check committed, staged, unstaged, and untracked reviewable deltas after recording review-control metadata.
- Start Strict Review against the frozen subject, not an ambiguous later HEAD or dirty checkout.
- Record the independent Reviewer execution through `reviewer_provenance`; it must bind to the exact same logical revision and immutable reference.
- Reviewer Execution and Context must both differ from the subject. Distinct invented IDs are not evidence.
- `claimed` is insufficient; `recorded` is repository-native self-recorded evidence and `verified` is stronger observer-backed evidence.
- After blocking findings are resolved, freeze the new Resolution revision and re-review that concrete revision independently.

### Flow `full` gate obligations

- For Changes allocated from CHG-0025 onward, `plan_complete` also requires
  a human-authority Plan Decision recorded in the Plan and provenance;
  `status: approved` alone is not authorization.
- Implementation MUST NOT begin until: architecture_complete, architecture_gate_passed, test_strategy_complete, plan_complete, tasks_ready.
- RED must be executed.
- RED must fail for the expected reason.
- Completion requires Verification to pass.
- Completion requires Strict Review to pass.
- Completion requires all blocking review threads on any active external review surface to be resolved.
- Completion requires Documentation Impact to be evaluated.
- Completion requires required documentation to be updated.
- Completion requires TDD compliance or an explicit, recorded exception.

### Reviewer/Resolver independence

- Under Protocol 2, Strict Review must run in an Execution and Execution Context independent from the implementation or resolution that produced the revision under review.
- Merely changing Role inside the same conversation, thread, session, or reasoning context is self-review and cannot satisfy Strict Review.
- Finish the Implementation/Resolution and all reviewable evidence before freezing the review subject.
- Before freezing, ensure the effective reviewable Git workspace is clean: no committed post-subject delta, staged reviewable changes, unstaged reviewable changes, or Git-visible untracked reviewable files.
- Identify the concrete immutable subject revision. In Git, use the subject commit SHA; `revision.id` alone is not sufficient.
- Record the frozen subject in `provenance.yml`; the Review Iteration references it through `subject_provenance`.
- Only the exact Change-local `manifest.yml`, `provenance.yml`, and `review.md` paths are review-control metadata that may differ after the freeze; do not generalize that exception to the Change directory, matching basenames, symlinks, or rename targets.
- Git-ignored cache/editor/temp files do not count as reviewable workspace mutations for the freeze invariant.
- Re-check committed, staged, unstaged, and untracked reviewable deltas after recording review-control metadata.
- Start Strict Review against the frozen subject, not an ambiguous later HEAD or dirty checkout.
- Record the independent Reviewer execution through `reviewer_provenance`; it must bind to the exact same logical revision and immutable reference.
- Reviewer Execution and Context must both differ from the subject. Distinct invented IDs are not evidence.
- `claimed` is insufficient; `recorded` is repository-native self-recorded evidence and `verified` is stronger observer-backed evidence.
- After blocking findings are resolved, freeze the new Resolution revision and re-review that concrete revision independently.

### Flow `standard` gate obligations

- For Changes allocated from CHG-0025 onward, `plan_complete` also requires
  a human-authority Plan Decision recorded in the Plan and provenance;
  `status: approved` alone is not authorization.
- Implementation MUST NOT begin until: intent_present, discovery_complete, specification_complete, specification_gate_passed, plan_complete.
- RED must be executed.
- RED must fail for the expected reason.
- Completion requires Verification to pass.
- Completion requires Strict Review to pass.
- Completion requires all blocking review threads on any active external review surface to be resolved.
- Completion requires Documentation Impact to be evaluated.
- Completion requires required documentation to be updated.
- Completion requires TDD compliance or an explicit, recorded exception.

### Reviewer/Resolver independence

- Under Protocol 2, Strict Review must run in an Execution and Execution Context independent from the implementation or resolution that produced the revision under review.
- Merely changing Role inside the same conversation, thread, session, or reasoning context is self-review and cannot satisfy Strict Review.
- Finish the Implementation/Resolution and all reviewable evidence before freezing the review subject.
- Before freezing, ensure the effective reviewable Git workspace is clean: no committed post-subject delta, staged reviewable changes, unstaged reviewable changes, or Git-visible untracked reviewable files.
- Identify the concrete immutable subject revision. In Git, use the subject commit SHA; `revision.id` alone is not sufficient.
- Record the frozen subject in `provenance.yml`; the Review Iteration references it through `subject_provenance`.
- Only the exact Change-local `manifest.yml`, `provenance.yml`, and `review.md` paths are review-control metadata that may differ after the freeze; do not generalize that exception to the Change directory, matching basenames, symlinks, or rename targets.
- Git-ignored cache/editor/temp files do not count as reviewable workspace mutations for the freeze invariant.
- Re-check committed, staged, unstaged, and untracked reviewable deltas after recording review-control metadata.
- Start Strict Review against the frozen subject, not an ambiguous later HEAD or dirty checkout.
- Record the independent Reviewer execution through `reviewer_provenance`; it must bind to the exact same logical revision and immutable reference.
- Reviewer Execution and Context must both differ from the subject. Distinct invented IDs are not evidence.
- `claimed` is insufficient; `recorded` is repository-native self-recorded evidence and `verified` is stronger observer-backed evidence.
- After blocking findings are resolved, freeze the new Resolution revision and re-review that concrete revision independently.
