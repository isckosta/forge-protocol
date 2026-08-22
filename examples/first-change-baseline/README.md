# Example — First-Change Baseline

This is a realistic, illustrative fixture for C-076, not a claim about a
real external Git history. It demonstrates the commit boundary an agent must
use when a repository has no prior commit.

## Pre-existing state

Before the Forge Change begins, the repository's declared intended scope is
the whole project. A complete inventory finds these files:

```text
README.md
src/app.py
tests/test_app.py
config.example.env
```

No in-scope file is excluded. Generated caches and local secrets are outside
the declared scope and are not committed; that scope decision is made before
the baseline, not inferred after the diff looks wrong.

## Baseline before Implementation

The repository has no prior Git commit. The agent records the complete
pre-existing state first:

```bash
git status --short
git add -A
git commit -m "chore: record pre-existing state before first Change"
# baseline commit: 1111111
```

This commit is the before-state. It is not an Implementation commit, and the
four listed files are all present in it.

## Change and reviewable diff

Only after the baseline does the agent create the Change artifacts and begin
Implementation:

```bash
git commit -m "docs(chg-0001): record intent and specification"
git commit -m "feat(chg-0001): implement the requested behavior"
git diff 1111111..HEAD --stat
```

The final diff is measured from `1111111`. A pre-existing file modified by
Implementation appears as modified, not as 100% new. Strict Review still
checks the actual repository state; this example demonstrates the required
baseline evidence and does not claim Adapter-level technical enforcement.
