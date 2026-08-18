---
forge:
  artifact: intent
  schema: 1
change: CHG-0012
status: complete
---
# Intent — Freeze check exempts completed Changes

## Problem

`forge validate`'s CI step (`.github/workflows/`) started failing on `main`
(GitHub Actions run `32091880352`) immediately after merging CHG-0010 and
CHG-0011, with:

```
C-026 [.forge/changes/CHG-0008-reviewer-resolver-separation/manifest.yml] C-026 review subject changed after its immutable revision freeze; create new subject provenance.
C-026 [.forge/changes/CHG-0011-review-convergence-boundary/manifest.yml] C-026 review subject changed after its immutable revision freeze; create new subject provenance.
```

`_validate_protocol2_review_provenance` (`src/forge_cli/validation/__init__.py`)
re-checks a passed Review Iteration's frozen subject against the *current*
HEAD unconditionally whenever that Iteration's `status` is `pending` or
`passed` (line 348), with no exception for a Change whose `state.current` is
already `complete`. Once any subsequent commit touches a file outside that
Change's own three review-control-metadata paths — which is inevitable and
expected once other Changes continue development on `main` — the check
fires, even though the Change it is nominally protecting has already
finished and been accepted.

The same file already has precedent for exempting `complete` Changes: line
296 skips the `forge/change@1`-must-upgrade finding when
`state.current == "complete"`. The freeze-drift check lacked the equivalent
exemption.

## Goal

A passed Review Iteration's frozen-subject-drift check MUST NOT fire once
the Change's own `state.current` is `complete`. The freeze exists to protect
review integrity *while a decision can still be influenced* — before
Completion. After Completion, the Change is closed history; unrelated,
expected activity elsewhere in the repository must not resurrect it as a
validation failure.

## Non-goals

- No change to freeze semantics for an *active* (non-complete) Change —
  every existing CHG-0008/CHG-0011 regression covering that case must
  remain green.
- No change to any other C-026 invariant (provenance authority, Execution/
  Context independence, Iteration identity history).
- No retroactive migration of CHG-0008/CHG-0011's `state.current` value —
  both already declare `complete`.

## Flow

FAST. This is a single, localized, semantically narrow correction to an
existing condition in one function; it introduces no new concept, schema
field, or Contract rule, and directly parallels an existing precedent in the
same function.
