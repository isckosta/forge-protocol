---
forge:
  artifact: discovery
  schema: 1
change: CHG-0046
status: complete
---

# Discovery — CHG-0046 Merge Readiness Post Review Artifact Scope

## Executive Summary

Both MR-015 and MR-017 are confirmed, reproducible defects in
`src/forge_cli/merge_readiness/evaluator.py` and its backing policy — not
in CHG-0045. The strongest, most load-bearing finding: `forge validate`
already contains a *working* implementation of the same "has the reviewed
subject gone stale" invariant (`validation/__init__.py:375`), and it
already encodes the exact carve-out MR-015 is missing — it only checks
staleness `and st.get("current")!="complete"`. The CI merge-readiness gate
and the local validator are, right now, two independent implementations of
one Contract invariant (C-026) that silently disagree, and CI's own two
steps on the exact same commit prove it: "Validate Forge repository"
passes ("Forge project is valid"), "Evaluate Forge Merge Readiness" on the
identical HEAD fails MR-015 on that same invariant. This is not a
hypothetical drift risk; it is presently blocking a real, passed-Review PR
(#36).

A second finding, initially expected to be part of the same bug, turned
out not to be: MR-006 (`Verification evidence is not bound to the
immutable implementation subject`) is **not** downstream of MR-015's
allowed-file-set bug. It is a real, independent gap in CHG-0045's own
`provenance.yml` — no `role: implementation, source.reference:
verification.md` record is bound to `95b521e` (the final passed Review's
actual subject commit); the only such record is bound to `23d763b` (the
*original*, pre-Resolution implementation). CHG-0043's own `provenance.yml`
(`verification-001/-002/-003`, each re-bound to its own Resolution's
subject) is the established, already-working precedent CHG-0045 did not
follow. Widening MR-015's allowed-file set does nothing for this — it is
correctly, if belatedly, caught. Same conclusion for MR-008: a missing
`content_digest` field, not gate logic.

## Investigation

### MR-015: the CI gate and `forge validate` implement the same invariant, and disagree

`_check_change()` in `evaluator.py:132-146` computes the post-freeze
allowed set as a hardcoded literal:

```python
change_root = path.parent.relative_to(root).as_posix()
delta = subprocess.run(
    ["git", "diff", "--name-only", subject_commit, head_revision, "--", change_root],
    ...
)
allowed = {
    f"{change_root}/manifest.yml",
    f"{change_root}/provenance.yml",
    f"{change_root}/review.md",
}
if delta.returncode != 0 or any(item and item not in allowed for item in delta.stdout.splitlines()):
    diagnostics.append(ReadinessDiagnostic("MR-015", "REVIEW SUBJECT STALE", ...))
```

`forge validate`'s C-026 check (`validation/__init__.py:68-85`,
`_reviewable_workspace_delta`) computes essentially the same thing —
committed + staged + unstaged + untracked delta since the frozen subject,
minus the same three-file `_review_control_metadata_paths()` allowlist —
but the finding that consumes it is gated:

```python
elif position==len(bound)-1 and status in{"pending","passed"} and st.get("current")!="complete" and _changed(r,mpath,sim[1]):
    out.append(_finding(r,mpath,"C-026 review subject changed after its immutable revision freeze; create new subject provenance."))
```

(`validation/__init__.py:375`, emphasis on `st.get("current")!="complete"`.)
Once a Change reaches `state.current: complete`, `forge validate` stops
enforcing this invariant — which is exactly the state a Change is in by
the time Documentation/Knowledge Capture/Completion-stage artifacts have
finished landing. `evaluator.py`'s MR-015 has no equivalent condition; it
checks unconditionally, regardless of `state.current`.

**Reproduction**, against CHG-0045's actual PR #36 base/head:

```
$ forge change merge-check --base 3aa195539218b8902296ff37f043359dd6e2614c --head 9f49c13761be6c3779045b3a186c3aeaccaff938
...
FAIL MR-015 [CHG-0045]: REVIEW SUBJECT STALE
FAIL MR-006 [CHG-0045]: Verification evidence is not bound to the immutable implementation subject
FAIL MR-008 [CHG-0045]: PLAN AUTHORIZATION STALE
MERGE BLOCKED
```

Isolating exactly which change_root-local paths changed between the
frozen subject (`95b521ef5ccec4e1651518b91a9e9ce74f86bb5a`, `resolution-002`)
and HEAD:

```
$ git diff --name-only 95b521e 9f49c13 -- .forge/changes/CHG-0045-.../
knowledge-capture.md
manifest.yml            # already allowed
provenance.yml          # already allowed
review.md               # already allowed
specification-drift.md
tasks.md
```

`knowledge-capture.md` and `specification-drift.md` map directly to
canonical Flow stages (`knowledge_capture`, and drift capture written
during `documentation`) that every Flow places after `strict_review`:

```
$ python3 -c "import yaml; d=yaml.safe_load(open('protocol/flows/full.yml')); print([s['id'] for s in d['stages']])"
['intent', 'discovery', 'specification', 'specification_review', 'architecture',
 'test_strategy', 'plan', 'tasks', 'tdd_implementation', 'verification',
 'strict_review', 'documentation', 'knowledge_capture', 'completion']
```

`fast.yml` and `standard.yml` place `strict_review` before
`documentation`/`documentation_impact` and `completion` too — this is not
a FULL-Flow-only shape, it is universal across all three canonical Flows.
`tasks.md`'s post-freeze edit (T-022 through T-025, confirmed by direct
diff) is the Change recording its own final Review-iteration outcome and
Documentation/Knowledge-Capture/Completion bookkeeping — narrative
completion of work the Flow itself schedules after Review, not a change to
reviewed implementation.

### The false positive was already observed once, and misread as confirmation

CHG-0045's own `tasks.md` (T-023) documents directly hitting this
mechanism, from the inside, one day before this Discovery:

> "A first attempt committed both [`.claude/CLAUDE.md`,
> `.playwright-mcp/`] directly on this branch — this immediately
> re-triggered a *new*, correct C-026 finding ('review subject changed
> after its immutable revision freeze') ... confirming this repository's
> own mechanical protection was working exactly as designed even though
> the commit's content was a no-op."

That conclusion is correct for `.claude/CLAUDE.md` and `.playwright-mcp/`
— both are genuinely outside the Change's own directory, and represent
exactly the kind of post-freeze implementation-adjacent mutation C-026
exists to catch. But the same freeze diff, at the same moment, was also
flagging `knowledge-capture.md`/`specification-drift.md`/`tasks.md` — all
*inside* the Change directory, all Flow-scheduled post-Review artifacts —
and that half of the same signal was not distinguished from the first.
This is strong first-party evidence that the false positive is not
theoretical: an attentive team, actively working around one real instance
of this exact mechanism, still did not catch the neighboring false one,
because the check does not distinguish "implementation changed" from
"Change directory's own later-stage bookkeeping advanced," and nothing in
its output says which case fired.

### MR-017: ten Adapter-generated paths have no classification rule

`classify_path()` (`policy.py:29-43`) resolves a path against, in order:
`change_prefix` (`.forge/changes/`) → `material_paths` (exact matches) →
`permitted_paths` (exact matches) → `ambiguous_prefixes` → `material_prefixes`
→ `permitted_prefixes` → falls through to `"ambiguous"`.
`protocol/policies/merge-readiness.yml`'s actual prefixes:

```yaml
material_prefixes:
  - .github/workflows/
  - protocol/
  - src/
  - tests/
  - adapters/
permitted_paths: [README.md, CONTRIBUTING.md, CHANGELOG.md]
permitted_prefixes: [docs/, examples/]
```

None of `.claude/`, `.agents/`, or `.forge/adapters/` appear anywhere.
The ten paths CI actually flagged on PR #36 — `.claude/CLAUDE.md`,
`.claude/skills/forge/SKILL.md`, `.claude/skills/forge/hooks/check-manifest-edit.sh`,
`.claude/skills/forge/references/{artifact-structure,engineering-contract}.md`,
`.agents/skills/forge/SKILL.md`, `.agents/skills/forge/references/{artifact-structure,engineering-contract}.md`,
`.forge/adapters/{claude-code,codex}/installation.yml` — are exactly the
Agent Adapter–generated surface CHG-0045 itself is about: real,
digest-tracked, `forge doctor`-verified generated output
(`.forge/adapters/*/installation.yml` is the digest ledger CHG-0045's own
Intent describes), not ambiguous or arbitrary paths. `adapters/` *is*
already a `material_prefix` — but that refers to
`src/forge_cli/adapters/` on-disk paths do not start with `adapters/`,
they start with `.claude/`, `.agents/`, or `.forge/`, none of which the
policy's prefix list anticipates. Any PR touching generated Adapter output
— which is the entire mechanism CHG-0045 built — trips MR-017
unconditionally.

### A more severe, orthogonal, pre-existing gap found while probing MR-015's actual scope

Verifying what protection AC-002 (Specification, drafted after this
paragraph) could rely on surfaced that MR-015's `-- change_root` pathspec
(`evaluator.py:134`) means it **never inspects any path outside the
Change's own directory, regardless of `state.current`.** Empirically
reproduced against a disposable fixture repository (not this repository):
freeze a Change's subject as `complete` with a passing Review/Verification
exactly as `test_merge_check_accepts_complete_change_without_material_runtime_diff`
does, then commit a further change to `src/runtime.py` on top, attributed
to the same already-complete Change (no new Change directory) —
`forge change merge-check` reports **`MERGE READY`**. `forge validate`
also does not catch it: `_reviewable_workspace_delta`'s C-026 check is
whole-repo-scoped (unlike MR-015) and *would* see the `src/` change, but
it is gated by the same `st.get("current")!="complete"` condition
(`validation/__init__.py:375`) this Discovery already cited as the
carve-out MR-015 is missing — so once a Change is `complete`, neither
mechanism verifies that the actually-merged implementation still matches
what Strict Review reviewed.

This is real and already live on `main`, independent of CHG-0045 and of
anything MR-015/MR-017's fixes touch — MR-015 was, per CHG-0036's own
history, deliberately scoped to `change_root` to fix cross-Change
contamination (memory: [[project-merge-readiness-scoping-bug]] finding 1),
not to detect a Change's own implementation drift; nothing else in
`evaluator.py` fills that gap for the completed-Change case. Adopting the
temporal `state.current == "complete"` boundary this Discovery otherwise
recommends for `change_root` paths does not make this worse — MR-015 already
provided zero protection for non-`change_root` paths regardless of state —
but it also does not make it better, and a reader could otherwise mistake
"MR-015 still protects `change_root`-external paths" for a true statement.
It is not. Closing this gap requires resolving the same tension CHG-0036
already fought once (repo-wide staleness detection vs. cross-Change false
positives) for the *completed* state specifically, which is a materially
larger design problem than either MR-015 or MR-017's fix here — recorded
as an explicit Out-of-Scope finding for a future Change, not silently
absorbed into this one.

### MR-006 and MR-008: real, but not this gate's defect

`bound_verification_records` (`evaluator.py:155-161`) requires a
`role: implementation, source.reference: verification.md` record whose
`revision.commit` equals `subject_commit` exactly. CHG-0045's
`provenance.yml` has exactly one such record, `implementation-subject-001`,
bound to `23d763b5b076bd1fd3df75743e9df90fcc4b0423` — the commit *before*
Resolutions 1 and 2 (`b43cb76`, `95b521e`) changed the implementation to
resolve R001-R007. The final passed Review iteration (`review-003`)
reviewed `95b521e`, not `23d763b`; no verification record is bound to
`95b521e`. CHG-0043's `provenance.yml` shows the pattern this repository
already uses correctly — a fresh `verification-NNN` record, each bound to
its own Resolution's subject commit, recorded every time the subject
changed. CHG-0045 recorded Review re-iterations after each Resolution but
never a matching re-verification record. This is a real absence of
evidence the gate is correctly refusing to accept — fixing MR-015 does not
touch it. Likewise, MR-008 fires because `plan-approval-001`'s `source`
never carries a `content_digest` block at all (confirmed by direct
inspection of `provenance.yml:4-26`) — `digest` stays `None`, and
`evaluator.py:289`'s `if not isinstance(digest, str)` fires. Both are
one-record provenance gaps, correctable directly on CHG-0045's branch
(`provenance.yml` is already exempt from the freeze), independent of
anything this Change touches.
