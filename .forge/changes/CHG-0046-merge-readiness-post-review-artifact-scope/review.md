---
forge:
  artifact: review
  schema: 1
change: CHG-0046
status: passed
---

# CHG-0046 · Review

## Verdict

**PASS (final, Iteration 3 — `kind: resolution_verification`).** No
blocking Findings remain outstanding. One non-blocking OBSERVATION (R003)
remains open, unchanged since Iteration 1.

- **Iteration 1** (`kind: initial_review`) — **REQUEST CHANGES**: 0
  BLOCKER, 2 MAJOR (R001, R002), 0 MINOR, 1 OBSERVATION (R003).
- **Iteration 2** (`kind: resolution_verification`) — **REQUEST CHANGES**:
  R001/R002 both independently re-verified resolved against the frozen
  Resolution subject `ff8fe51cc3dd237252c579f9775d8122254bf189`; Resolution
  Delta independently recomputed, no Out-of-Scope Mutation. 1 new MAJOR
  (R004 — `resolution-001`'s own provenance record lacked the `scope`/
  `targets` fields Protocol 2 §11 requires, so `forge validate` could not
  mechanically confirm the absence of Out-of-Scope Mutation even though
  this Iteration had confirmed it by hand).
- **Iteration 3** (`kind: resolution_verification`) — **PASS**: R004
  resolved by a new, additive `resolution-001-scope` provenance record
  (`resolution-001` itself unmodified, append-only per C-026) declaring
  the exact `scope`/`targets` Protocol 2 §11 requires; `forge validate`
  now genuinely passes; `resolution-001-scope`'s declared `scope`
  independently confirmed to match the real Resolution Delta exactly; 0
  new material findings. See "## Iteration 3 — Resolution Verification"
  below for full detail. Iterations 1 and 2's verdict text is left
  verbatim below as the historical record.

**REQUEST CHANGES (Iteration 1, `kind: initial_review`), as originally
recorded.** 0 BLOCKER, 2 MAJOR (R001, R002), 0 MINOR, 1 OBSERVATION (R003).
Per `protocol/policies/review.yml`, `blocking: [blocker, major]` — both
MAJOR findings block Completion.

Both real fixes described in Intent/Specification/Architecture are sound
and independently verified: the MR-015 temporal-boundary logic correctly
mirrors `forge validate`'s existing `state.current != "complete"`
carve-out, is scoped exclusively to `change_root`-prefixed paths, reads
`state.current` fresh from the manifest at `head_revision` (not a stale or
cached value), and leaves pre-Completion behavior byte-for-byte unchanged
— confirmed both by code inspection and by re-running the full test suite
and a direct reproduction against CHG-0045's actual PR #36 commits. The
MR-017 fix genuinely resolves nine of the ten named paths correctly.
What blocks this Iteration are two independently reproduced defects the
Change's own artifacts do not disclose: a new unguarded manifest read that
crashes the CLI on a malformed `state:` field (R001), and a `material_prefixes`
entry broader than what this Change's own Specification (AC-005) and
Architecture ("Design" section) explicitly promise (R002).

## Review Summary

| | |
|---|---|
| **Iterations** | 3 |
| **Current Subject** | `ff8fe51cc3dd237252c579f9775d8122254bf189` (Resolution, via `resolution-001-scope`) |
| **Open Blockers** | 0 |
| **Open Majors** | 0 |
| **Open Minors** | 0 |
| **Open Observations** | 1 (R003) |
| **Final Iteration** | 3 |
| **Result** | PASS |

Iteration 1 subject (superseded): `60b699bb69c06ed0b078572dd705191e73441c68`.
R001/R002 (Iteration 1, MAJOR) resolved by `resolution-001` and
independently re-verified in Iteration 2 — no longer outstanding. R004
(Iteration 2, MAJOR) resolved by `resolution-001-scope` and independently
re-verified in Iteration 3 — no longer outstanding.

## Current Subject

| | |
|---|---|
| **Subject SHA** | `60b699bb69c06ed0b078572dd705191e73441c68` |
| **Frozen** | Yes — `provenance.yml` record `implementation-subject-001`, committed at `0913d92d37b17cb1450ab3d7cea51b1ba6d36bc0` ("chore(chg-0046): freeze Implementation subject at 60b699b (C-026)") |
| **Iteration** | 1 |

Verified directly: `git log --oneline -1 60b699bb69c06ed0b078572dd705191e73441c68` resolves to `feat(chg-0046): state-conditioned MR-015 allowed-set, additive MR-017 policy rules`. `git status --short --untracked-files=all` at the current branch tip (`0913d92`, one commit past the frozen subject, containing only the `provenance.yml` freeze record — review-control metadata) is empty: no committed post-subject delta outside `provenance.yml`, no staged/unstaged/untracked reviewable changes.

## Reviewer Independence

This Review runs in a freshly spawned Execution and Execution Context
(`claude-code-review-0046-independent` / `claude-code-review-session-2026-08-24`,
recorded in this Review's own `provenance.yml` entry, `role: review`)
independent from `implementation-subject-001`'s Execution/Context
(`claude-code-implementation-0046` / `claude-code-session-2026-08-25`).
Both `execution.id` and `execution.context_id` differ, satisfying Protocol
2's independence requirement (C-026). This Review had no visibility into
any prior conversation that produced the Implementation; all findings
below were derived directly from repository state, the diff, and
independent test/CLI execution performed in this session.

## Open Findings

| Finding | Severity | Status | Iteration |
|---|---|---|---|
| R001 | MAJOR | Resolved (Iteration 2) | 1 |
| R002 | MAJOR | Resolved (Iteration 2) | 1 |
| R003 | OBSERVATION | Open | 1 |
| R004 | MAJOR | Resolved (Iteration 3) | 2 |

## Iteration 1 — REQUEST CHANGES

### R001 — MAJOR — the new `is_complete` read in `_check_change()` lacks the isinstance guard every other manifest-section read in the same function uses, and crashes the CLI on a malformed `state:` field

**Found:** `evaluator.py:145` (the new line this Change introduces):

```python
is_complete = manifest.get("state", {}).get("current") == "complete"
```

Every other place `_check_change()` reads a manifest sub-section defends
against that section not being a mapping, e.g. (unchanged by this diff):

```python
flow = manifest.get("flow", {}).get("current") if isinstance(manifest.get("flow"), dict) else None
...
review = manifest.get("review", {}) if isinstance(manifest.get("review"), dict) else {}
...
state = manifest.get("state", {}) if isinstance(manifest.get("state"), dict) else {}
```

The last of these — the *existing*, already-guarded `state` read used later
in the same function for MR-005/MR-016/MR-013 — is functionally what
`is_complete` needs, but the new line does not reuse it or its guard; it
re-derives `state.current` inline, unguarded. If a Change's `manifest.yml`
has a malformed `state:` field (e.g. `state: complete` — a bare string
instead of `state: {current: complete}`, a plausible hand-edit or
scaffold-generation mistake, not a hypothetical), `manifest.get("state",
{})` returns that string as-is (the `{}` default only applies when the key
is *absent*, not when its value is not a mapping), and `.get("current")`
raises `AttributeError: 'str' object has no attribute 'get'`.

**Evidence — directly reproduced**, in a disposable fixture repository
(not this repository), against the actual `60b699bb`/current-branch
`evaluator.py`: a Change frozen with `review.status: passed`, one passed
Review iteration, admissible subject/reviewer provenance, and
`state: complete` (string, not mapping) in `manifest.yml`, evaluated via
`forge change merge-check --base <base> --head <head>` from that fixture
repo (module resolution confirmed to load this repository's own
currently-checked-out `merge_readiness` package, per `forge_cli.__file__`
resolving to `/home/isckosta/forge-protocol/src/forge_cli/__init__.py`):

```
AttributeError: 'str' object has no attribute 'get'
  .../evaluator.py:145 in _check_change
    is_complete = manifest.get("state", {}).get("current") == "complete"
```

The exception is **not** caught by `evaluate_merge_readiness`'s own except
clause (`MergeReadinessOperationalError, MaterialityPolicyError,
yaml.YAMLError, TypeError`) — `AttributeError` is not a subclass of any of
those — so it propagates out of the CLI command entirely: a raw traceback,
not a `MR-9xx` operational diagnostic, not `MERGE BLOCKED`. This is a
strictly worse failure mode than what the codebase's own `MR-900`
diagnostic path exists to provide for exactly this class of "cannot
reliably determine" input, and inconsistent with C-078's fail-closed
principle in spirit — a crash is not a controlled, diagnosable failure.

Confirmed this is newly introduced by this diff, not pre-existing: before
this Change, `_check_change()`'s MR-015 block never read `manifest["state"]`
at all (only the three-literal-file allowlist); the first and only place
`state` was read was the already-guarded line later in the function. The
same malformed-`state` fixture, evaluated against `_check_change()` as it
existed before `60b699bb`'s diff, would not reach any unguarded `.get()`
call in this code path.

**Required Resolution:** `is_complete` must be computed defensively,
consistent with the file's own established convention for reading
manifest sub-sections — e.g. reuse the already-guarded `state` variable
(hoisted above this block, or the existing later computation reordered
ahead of it) rather than a second, unguarded inline read of the same
field. A malformed `state:` field must produce a diagnostic (or otherwise
degrade gracefully), not an unhandled exception.

### R002 — MAJOR — the `.forge/adapters/` `material_prefixes` entry is broader than this Change's own Specification (AC-005) and Architecture ("Design") both promise, and is untested at the boundary that matters

**Found:** Architecture's Design section states the MR-017 resolution for
this path family explicitly as `` .forge/adapters/*/installation.yml ``
(scoped to the `installation.yml` file specifically, one level of adapter-id
wildcarding) — distinct, by Architecture's own text, from the `**`
(fully recursive) scoping it explicitly chose for
`.claude/skills/forge/**` and `.agents/skills/forge/**`. `classify_path()`
(`policy.py:29-43`) only supports literal string-prefix matching, not glob
patterns — there is no way to express "any adapter id, but only
`installation.yml`" as a `material_prefixes` entry. Plan item 6 and the
implemented `protocol/policies/merge-readiness.yml` both add
`.forge/adapters/` (a bare directory prefix) to `material_prefixes`
instead — silently widening Architecture's own stated design to cover
every file under every adapter's directory, not just `installation.yml`.

Specification's FR-002 Boundary is explicit that this Change "resolves
only the ten specific paths Discovery identified... does not require
auditing or reclassifying any path the policy already resolves to
material, permitted, or change" (and AC-005 requires any path "not in the
ten identified paths and not already matched by an existing policy rule"
to keep resolving to `ambiguous`). `.forge/adapters/<id>/config.yml` — the
user-owned Adapter configuration file this repository's own history
documents (CHG-0010 Discovery: "user-owned `.forge/adapters/<adapter-id>/config.yml`
keeps Adapter configuration") — is such a path: it is not one of the ten
Discovery named, and before this Change it fell through to `ambiguous`
like `installation.yml` did. After this Change it resolves to `material`
instead, contradicting AC-005 as written.

**Evidence — directly reproduced** against the actual policy file at
`60b699bb`:

```
>>> classify_path(".forge/adapters/claude-code/config.yml", policy)
'material'      # not one of the ten paths; AC-005 requires 'ambiguous'
>>> classify_path(".forge/adapters/claude-code/installation.yml", policy)
'material'      # correct, one of the ten
>>> classify_path(".forge/adapters/claude-code/some-future-file.txt", policy)
'material'      # any future file under an adapter's directory, swept in too
```

No test in `tests/unit/test_merge_readiness_policy.py` or
`tests/cli/test_merge_check.py` exercises this boundary. TDD-005
(`test_unrelated_unclassified_path_still_falls_back_to_ambiguous`) and the
pre-existing `test_ambiguous_unclassified_diff_is_blocked` both use an
unrelated top-level path (`unclassified.data`) as their AC-005 evidence —
neither tests a sibling path adjacent to one of the ten actually-added
rules, which is exactly the case this over-broad prefix gets wrong. The
practical consequence today is limited (this repository currently has no
`.forge/adapters/` directory at all, so nothing trips MR-001 yet), but the
defect is real, already merged into the policy file, and will silently
misclassify the first `config.yml` (or any other adapter-directory file)
any future Adapter installation introduces.

**Required Resolution:** Resolve `.forge/adapters/*/installation.yml`
precisely as Architecture specifies — e.g. as exact `material_paths`
entries for the two currently-known adapter ids (`.forge/adapters/claude-code/installation.yml`,
`.forge/adapters/codex/installation.yml`), consistent with how
`.claude/CLAUDE.md` was correctly added as an exact `material_paths` entry
for the same "single file, not a prefix" reason Plan item 6 itself states
— not a `.forge/adapters/` directory prefix. Add a test asserting a
sibling path under an adapter's directory that is not `installation.yml`
(e.g. `.forge/adapters/claude-code/config.yml`) still resolves to
`ambiguous`, to actually cover AC-005's boundary.

### R003 — OBSERVATION — FR-001's tolerance, once `state.current: complete`, extends to every Change-local path including `verification.md`/`review.md` themselves, not only the doc-stage artifacts named as examples

**Found:** FR-001's Requirement text says "any Change-local path," and
AC-001's example list (`knowledge-capture.md`, `specification-drift.md`,
`tasks.md`, "in addition to the already-allowed
`manifest.yml`/`provenance.yml`/`review.md`") is explicitly non-exhaustive.
The implementation matches that literal breadth exactly: once
`state.current == "complete"`, editing `verification.md` or `review.md`'s
own textual content after the freeze — previously always flagged
`MR-015`-stale, since neither file was in the original three-file allowed
set — no longer trips `MR-015` either. `MR-006`/`MR-007` still require
`"**PASS**"` to be present in that content at `head_revision`, so the
specific self-attestation those checks corroborate cannot be silently
inverted, but surrounding narrative/evidence text in either file becomes
freely editable post-Completion with no staleness signal at all. This is
not a defect — it is exactly what the Specification's own literal text and
`forge validate`'s existing (even broader, whole-repo) precedent already
authorize, and Architecture's Risks section names the adjacent "premature
completion" risk generally — but neither Specification, Architecture, nor
Verification calls out this specific consequence (that the previously-protected
`verification.md`/`review.md` texts themselves lose that protection once
complete) by name anywhere. Recording it explicitly so a future reader does
not need to re-derive it from the diff.

**Required Resolution:** None required to pass Review — this is
intentional, Specification-authorized behavior. Consider naming this
consequence explicitly in Architecture's Risks or Specification's FR-001
Expected Behavior, so it is not left only implicit in "any Change-local
path."

## Checked and found sound

- **MR-015 scoping correctness.** The `-- change_root` pathspec on the
  `git diff` inside `_check_change()` already restricts every item in
  `delta.stdout.splitlines()` to paths under `change_root`; the added
  `item.startswith(f"{change_root}/")` guard is redundant with that
  pathspec (harmless, not a defect) rather than a separate scoping
  mechanism. AC-002's claim — this Change's tolerance cannot leak to paths
  outside `change_root` — is structurally true because this check never
  sees such paths at all, independent of `is_complete`.
- **`is_complete` freshness.** `manifest` is loaded once, at function
  entry, via `_manifest(root, change_id, head_revision)`, which reads
  `manifest.yml` at `head_revision` (`tree_file(root, head_revision,
  ...)`) — not at `subject_commit` or any cached value. `is_complete`
  therefore reflects the Change's actual state at the commit under
  evaluation, and the same `manifest` variable is reused for MR-005's own
  `state.current` check later in the function — no risk of the two
  disagreeing on which manifest they read.
- **No regression for incomplete Changes (AC-003).** Confirmed by direct
  trace: when `is_complete` is `False`, the generator condition `not
  (False and ...)` is always `True`, so every item in `delta.stdout`
  participates in the `any(...)` exactly as it did before this diff —
  byte-identical pre-Completion behavior. `test_merge_check_still_flags_change_local_edit_before_completion`
  (TDD-002) independently confirms this by direct execution.
- **Reproduction against the real CHG-0045/PR #36 commits.** Independently
  reproduced in this Review (not trusted from `verification.md`'s claim):
  checked out a disposable `git worktree` at PR #36's actual head
  (`9f49c13761be6c3779045b3a186c3aeaccaff938`) against its actual base
  (`3aa195539218b8902296ff37f043359dd6e2614c`), ran `forge change
  merge-check` from that worktree (confirmed the `merge_readiness` package
  loaded is this repository's own editable-installed, currently-checked-out
  copy, not the worktree's). Result: `FAIL MR-006`, `FAIL MR-008`,
  `MERGE BLOCKED` — `MR-015` and `MR-017` no longer appear, exactly as
  `verification.md` claims.
- **Test suite, independently re-run, not trusted from `verification.md`.**
  `.venv/bin/python -m pytest tests/cli/test_merge_check.py
  tests/unit/test_merge_readiness_policy.py -v` → 22 passed. Full suite,
  `.venv/bin/python -m pytest -q` → 702 passed, 2 pre-existing unrelated
  warnings (`tests/unit/test_experience_capture.py`, FER capture-failure
  logging, untouched by this diff). `forge validate` → "Forge project is
  valid"; `forge doctor` → all PASS except the same two pre-existing,
  unrelated WARNs `verification.md` reports (`adapter:installation_missing`,
  `migration_available`) — independently re-run, not trusted from
  `verification.md`'s claim.
- **MR-006/MR-008 genuinely untouched.** The full diff (`git diff
  3aa1955..60b699bb -- src/forge_cli/merge_readiness/evaluator.py`)
  contains exactly one hunk in `evaluator.py`, entirely inside the MR-015
  block; the MR-006 (`bound_verification_records`) and MR-008 (Plan digest)
  logic elsewhere in `_check_change()` is byte-identical to the pre-Change
  version. The real PR #36 reproduction above independently confirms both
  still fire.
- **The claimed pre-existing `change_root`-external gap is real and
  honestly disclosed, not silently absorbed.** Confirmed by direct code
  trace: the `git diff --name-only subject_commit head_revision -- change_root`
  pathspec means this check never inspects any path outside
  `change_root`, independent of `state.current` and independent of this
  Change — TDD-003
  (`test_merge_check_does_not_detect_external_drift_after_completion`)
  passes unmodified before and after this diff, correctly characterizing
  (not fixing) it. Discovery, Specification's Out of Scope, and
  Architecture's Risks section all name this explicitly and consistently,
  rather than letting AC-002's original (Specification Review-corrected)
  wording imply a protection that does not exist.
- **Provenance/manifest internal consistency.** `provenance.yml`'s
  `plan-approval-001.source.content_digest.value` (sha256, 64 hex chars)
  was independently recomputed from `plan.md`'s actual current content
  (excluding the two `<!-- forge:plan-approval-* -->` marker lines, per
  `evaluator.py`'s own canonicalization) and matches exactly. Both commit
  SHAs `afdc4e36ff43dfb9cf487b853f996e981a23ffb4` (`plan-approval-001`) and
  `60b699bb69c06ed0b078572dd705191e73441c68` (`implementation-subject-001`
  / `verification-001`) resolve via `git cat-file -e` and `git log`.
  `manifest.yml`'s `DEC-002` (`class: technical`, `materiality: material`,
  `authority: human`, `owning_artifact: plan`, `resolved_via:
  human_decision`) matches `plan.md`'s own recorded approval narrative and
  `provenance.yml`'s `plan-approval-001` (`observed_by: operator`,
  satisfying C-077's requirement that the confirming record identify the
  operator, not `self`, as observer). `DEC-001` (architectural, resolved
  via `autonomous_decision`, owned by `architecture`) matches Architecture's
  own DEC-001 narrative.
- **Test honesty (TDD-002/TDD-003/TDD-005).** These are recorded as guard
  or characterization tests with `red: {observed: false, ...}` and an
  explicit reason, not misrepresented as RED-GREEN cycles — consistent
  with C-011/C-016. `tdd-evidence.yml`'s cycle count (5) matches
  `manifest.yml`'s `tdd.cycles: 5`.
- **MR-017's other nine paths.** Independently re-verified via
  `classify_path()`: all nine remaining paths from Discovery's list of ten
  (everything except the `.forge/adapters/` family, R002 above) resolve
  exactly to `material` as intended, with no unintended widening —
  `.claude/skills/forge/**` and `.agents/skills/forge/**` are deliberately
  recursive per Architecture's own stated design, unlike the
  `.forge/adapters/` case.

## Conclusion

Two MAJOR findings (R001, R002) block Completion under
`protocol/policies/review.yml`'s `blocking: [blocker, major]`. Neither
undermines the core correctness of the two fixes this Change sets out to
make — the MR-015 temporal-boundary design is sound and the MR-017 fix
correctly resolves nine of ten paths — but both are real, independently
reproduced defects: a new crash surface (R001) and a scope-boundary
violation of this Change's own AC-005 (R002), neither disclosed in
Verification or caught by the existing test suite. This Change is not
ready for Completion. A Resolution addressing R001 and R002, followed by
an independent Resolution Verification against the new frozen subject, is
required before this Review can pass.

## Iteration 2 — REQUEST CHANGES (`kind: resolution_verification`)

### Iteration 2 scope and authority

This Iteration is a Resolution Verification, not a second Initial Review.
Per `protocol/versions/2/specification.md` §10-§11, its authority is
bounded to exactly three things: (1) R001 and R002, the two Findings
`resolution-001` targets; (2) defects within `resolution-001`'s own
Resolution Delta; (3) Out-of-Scope Mutation. It is deliberately not a
re-audit of `implementation-subject-001`. Nothing in Iteration 1's
"Checked and found sound" section — MR-015 scoping correctness,
`is_complete` freshness, no regression for incomplete Changes, the
CHG-0045/PR #36 reproduction, provenance/manifest internal consistency,
test honesty, or MR-017's other nine paths — was re-litigated here.

### Iteration 2 execution independence

Executed in a freshly spawned Execution and Execution Context
(`claude-code-review-0046-independent-2` /
`claude-code-review-session-2026-08-24-iter2`, recorded in this Review's
own `provenance.yml` entry `review-002`), distinct from `resolution-001`'s
`claude-code-implementation-0046` / `claude-code-session-2026-08-25` and
from `review-001`'s own identity. No claim in `resolution-001`'s
`provenance.yml` statement, `tasks.md` T-014/T-015/T-016,
`tdd-evidence.yml`'s TDD-006/TDD-007, or `verification.md`'s addendum was
accepted without independent reproduction against actual repository
state. Subject: `resolution-001`, frozen at
`ff8fe51cc3dd237252c579f9775d8122254bf189` (revision
`chg-0046-resolution-001`).

### Resolution Delta, computed independently — no Out-of-Scope Mutation

Computed per §11 as the committed diff between the immutable revision of
the Iteration immediately preceding this one (`review-001`'s subject,
`60b699bb69c06ed0b078572dd705191e73441c68`) and this Iteration's own
subject (`ff8fe51cc3dd237252c579f9775d8122254bf189`):

```
$ git diff --name-only 60b699bb69c06ed0b078572dd705191e73441c68 ff8fe51cc3dd237252c579f9775d8122254bf189
.forge/changes/CHG-0046-.../discovery.md
.forge/changes/CHG-0046-.../manifest.yml
.forge/changes/CHG-0046-.../provenance.yml
.forge/changes/CHG-0046-.../review.md
.forge/changes/CHG-0046-.../tasks.md
.forge/changes/CHG-0046-.../tdd-evidence.yml
.forge/changes/CHG-0046-.../verification.md
protocol/policies/merge-readiness.yml
src/forge_cli/merge_readiness/evaluator.py
tests/cli/test_merge_check.py
tests/unit/test_merge_readiness_policy.py
```

Subtracting the three Change-local review-control paths
(`manifest.yml`/`provenance.yml`/`review.md`) leaves: `discovery.md`
(addendum), `tasks.md`, `tdd-evidence.yml`, `verification.md` — all
Change-local bookkeeping, always in scope for this Change's own directory
— plus `protocol/policies/merge-readiness.yml` and
`src/forge_cli/merge_readiness/evaluator.py`, the exact two files
Specification's FR-001/FR-002 and this Change's Scope name, plus their
two test files (`tests/cli/test_merge_check.py`,
`tests/unit/test_merge_readiness_policy.py`). No `src/`, `tests/`, or
`protocol/` path outside these appears anywhere in the diff; no other
Change's directory appears. This matches `resolution-001`'s own narrated
scope exactly. **Out-of-Scope Mutation: none.**

### R001, re-checked against actual repository state — resolved

Not accepted from `resolution-001`'s claim. Read `evaluator.py` directly:
`state = manifest.get("state", {}) if isinstance(manifest.get("state"), dict) else {}`
is now hoisted to the top of `_check_change()` (line 70), and the
`is_complete` line now reads `is_complete = state.get("current") == "complete"`
(line 146) — reusing the single guarded variable; the previously-duplicated
guarded computation later in the function was removed, not left as dead
code. Independently reproduced the exact crash scenario in a disposable
fixture repository (not this repository, and deliberately without
`.forge/forge.yml` present, per this Change's own
`test_merge_check_degrades_gracefully_on_malformed_state_field` docstring,
which explains why: with `forge.yml` present, `validate_project()`'s own
unrelated pre-existing unguarded read at `validation/__init__.py:321/375`
fires first and would mask whether *this* code path is fixed):

- Checked out `evaluator.py` at `60b699bb` (the Iteration-1-reviewed
  version) into the working tree, called `_check_change()` directly
  against a fixture Change with `state: complete` (bare string) and a
  populated `review.iterations` list (so the vulnerable branch is
  actually reached — an empty `iterations` list short-circuits before the
  vulnerable line, which a first attempt at this reproduction initially
  missed): **`AttributeError: 'str' object has no attribute 'get'`**,
  reproducing R001 exactly.
- Restored `evaluator.py` to its current (`ff8fe51`) content and re-ran
  the identical fixture: **no exception**, `_check_change()` returns
  `ReadinessDiagnostic("MR-005", "COMPLETION NOT READY", ...)` — a
  controlled diagnostic, not a crash. Working tree confirmed clean
  (`git status --short`) after restoring.

R001 is resolved.

### R002, re-checked against actual repository state — resolved

Not accepted from `resolution-001`'s claim. Read
`protocol/policies/merge-readiness.yml` directly: the bare `.forge/adapters/`
`material_prefixes` entry is gone; `material_paths` now carries exactly
`.forge/adapters/claude-code/installation.yml` and
`.forge/adapters/codex/installation.yml`. Independently called
`classify_path()` against the live policy:

```
classify_path(".forge/adapters/claude-code/config.yml", policy)        -> ambiguous
classify_path(".forge/adapters/claude-code/installation.yml", policy)  -> material
classify_path(".forge/adapters/codex/installation.yml", policy)        -> material
classify_path(".forge/adapters/claude-code/some-future-file.txt", ...) -> ambiguous
```

Matches Architecture's `.forge/adapters/*/installation.yml` design and
Specification's AC-005 exactly — the sibling `config.yml` R002 identified
now correctly falls back to `ambiguous`. R002 is resolved.

### R004 — MAJOR — `resolution-001`'s own provenance record omits `scope`/`targets`, so `forge validate` cannot mechanically verify the Resolution Delta — genuinely reproduced, blocking

**Not R001 or R002** (it is a defect in the Resolution's own provenance
record, not in `evaluator.py` or the materiality policy), but squarely
**inside the Resolution Delta** — `provenance.yml`'s `resolution-001`
record was itself added within the diff this Iteration verifies — so this
is within this Iteration's own bounded authority (point 2: defects within
the Resolution Delta) to discover and record, not an unrestricted
re-audit.

**Problem:** Per `protocol/versions/2/specification.md` §11, "A
`role: resolution` provenance record referenced by a
`resolution_verification` Iteration MUST declare `scope`... and
`targets`." Read `provenance.yml`'s `resolution-001` record directly: it
has a `source.statement` prose field narrating the Resolution Delta
("Resolution Delta (git diff 60b699b..ff8fe51, excluding
manifest.yml/provenance.yml/review.md): discovery.md (addendum),
tasks.md, ...") but no structured `scope:` or `targets:` field at all —
the same gap this repository's own CHG-0045 Iteration 2 independently
found and recorded as R007 for an identical reason.

**Evidence — directly reproduced**, against this Iteration's own recorded
state (with `review-002` bound as `kind: resolution_verification`,
`subject_provenance: resolution-001`):

```
$ forge validate
C-026 [.../manifest.yml] The Resolution referenced by a resolution_verification
Iteration must declare non-empty scope and targets before it can be
mechanically verified as scoped.
```

Reproduced deterministically (pure structural read of `provenance.yml`,
no network, no time-dependence) — confirmed by adding the iteration entry
to a scratch copy of `manifest.yml`, running `forge validate`, observing
the failure, then restoring the file to its pre-edit state (`git status
--short` confirmed clean immediately after).

**Impact:** This does not indicate an actual Out-of-Scope Mutation — this
Iteration independently confirmed, via direct `git diff --name-only`
computation above (not via this mechanical check), that the Resolution
Delta contains none — but `forge validate` cannot confirm that itself
without the missing fields, which defeats the purpose of the mechanical
gate. Blocking per `protocol/policies/review.yml` (MAJOR).

**Suggested Resolution (non-blocking on this Review to specify, per
C-025):** Add `scope: [protocol/policies/merge-readiness.yml,
src/forge_cli/merge_readiness/evaluator.py, tests/cli/test_merge_check.py,
tests/unit/test_merge_readiness_policy.py]` and `targets: [R001, R002]` to
`resolution-001`'s existing `provenance.yml` record (or a new,
identically-scoped supplementary record, following CHG-0045's own
`resolution-001-scope` precedent). Since `provenance.yml` is one of the
three review-control-metadata paths exempt from the freeze, this does not
require a new frozen Resolution revision — only a further, narrowly-bounded
Resolution Verification (Iteration 3) confirming `forge validate` is then
clean.

## Checked and found sound (Iteration 2)

- **The `validation/__init__.py:321` disclosure is honest and accurate.**
  `discovery.md`'s addendum, `tasks.md` T-016, `tdd-evidence.yml`
  TDD-006's notes, and `verification.md`'s addendum all describe a second,
  unrelated, pre-existing unguarded `state` read in
  `src/forge_cli/validation/__init__.py:321` (crashing at line 375),
  discovered incidentally while isolating R001's fixture. Confirmed
  directly: `validation/__init__.py` does not appear anywhere in the
  Resolution Delta (see above) — genuinely untouched by this Change,
  genuinely out of Scope, and correctly disclosed rather than silently
  fixed or silently dropped. Not re-litigated further here (C-047/C-050:
  recorded, not pursued, since it predates and is unrelated to this
  Resolution).
- **Full pytest suite, independently re-run, not trusted from
  `verification.md`.** `.venv/bin/python -m pytest -q` → `704 passed, 2
  warnings` (same two pre-existing, unrelated warnings as Iteration 1).
  `.venv/bin/python -m pytest tests/cli/test_merge_check.py
  tests/unit/test_merge_readiness_policy.py -v` → `24 passed` (12 + 12,
  including the two new Resolution tests
  `test_merge_check_degrades_gracefully_on_malformed_state_field` and
  `test_sibling_adapter_directory_file_stays_ambiguous`).
- **`forge doctor`** → all `PASS` except the same two pre-existing,
  disclosed `WARN`s (`adapter:installation_missing`,
  `migration_available`), unchanged by this Resolution.
- **Change-local bookkeeping (`discovery.md`, `tasks.md`,
  `tdd-evidence.yml`, `verification.md`) is internally consistent.**
  `tasks.md` T-001 through T-016 correctly marked `[x]`; T-017/T-018/T-019
  correctly left `[ ]` (Resolution Verification, Documentation Impact,
  Knowledge Capture are legitimately still pending). `tdd-evidence.yml`'s
  `cycle_count: 7` matches its own 7 listed cycles and `manifest.yml`'s
  `tdd.cycles: 7`. No overclaim of a stage that has not actually
  occurred.

### New Findings introduced by the Resolution

One new Finding: **R004 (MAJOR, blocking)** — `resolution-001`'s own
provenance record fails mechanical scope verification, a real defect
inside the Resolution Delta itself, not an Out-of-Scope Mutation and not
a regression in R001/R002's own fixes, but material enough to keep this
Iteration from `status: passed`. `full_review_required: false`: R004 is
not an Out-of-Scope Mutation (§11's specific trigger for mandatory
`full_review_required: true`); it is a scoped, narrow
metadata-completeness defect in `resolution-001`'s own record, correctable
without reopening R001/R002 or expanding beyond this Iteration's own
bounded authority.

### Convergence accounting

`new_material_findings: 1` (R004 — the only new Finding, and it is a
material defect within the Resolution Delta). `full_review_required:
false` per above. `consecutive_unconverged_verifications` is `1` after
this Iteration (the first `resolution_verification` Iteration to end
without a clean `passed` status) — below the Convergence Limit of 2, since
this is the first such non-convergence, not a repeated cycle on the same
Finding.

### Verdict

**REQUEST CHANGES.**

R001 and R002 are both genuinely resolved in repository state,
re-verified directly against the actual frozen Resolution subject rather
than accepted from `resolution-001`'s own claim — including an
independent, from-scratch reproduction of R001's crash scenario against
`evaluator.py` at both the pre-fix (`60b699b`) and post-fix (`ff8fe51`)
commits. The Resolution Delta contains no Out-of-Scope Mutation — exactly
the files `resolution-001` names, all inside this Change's own directory
or the two files/tests Scope names. But `resolution-001`'s own provenance
record omits the `scope`/`targets` fields §11 requires, so `forge
validate` cannot mechanically confirm what this Iteration has confirmed
by hand (R004, MAJOR, blocking) — a real, reproduced `forge validate`
failure, not a hypothetical one. This Change is **REQUEST CHANGES**; it
may proceed to a further, narrowly-bounded Resolution (completing
`resolution-001`'s own `scope`/`targets` fields — review-control metadata,
not a new code change) and a further Resolution Verification (Iteration
3) once R004 is fixed.

## Iteration 3 — Resolution Verification

### Scope and authority

Independent Resolution Verification, executed in a freshly spawned
Execution and Execution Context (`claude-code-review-0046-independent-3`
/ `claude-code-review-session-2026-08-25-iter3`, recorded in this Review's
own `provenance.yml` entry `review-003`), distinct from every prior
Execution/Context in this Change's history. Per C-047, bounded to R004
(the only Finding Iteration 2 left open and the only thing this metadata
Resolution targets), defects within its own Resolution Delta, and
Out-of-Scope Mutation. No code, test, or behavioral change occurred
between Iteration 2 and this Iteration — the subject commit
(`ff8fe51cc3dd237252c579f9775d8122254bf189`) is unchanged; only a new,
additive `provenance.yml` record (`resolution-001-scope`) and
`manifest.yml`'s `review-002.subject_provenance` repoint were added.
R001/R002's substance was not re-litigated (already independently
re-verified twice: Iteration 1's own reproduction and Iteration 2's
from-scratch re-reproduction).

### R004 — re-checked against actual repository state — resolved

`forge validate` run directly against current repository state:

```
$ forge validate
Forge project is valid
```

Clean. `provenance.yml` now carries a new `resolution-001-scope` record
(`role: resolution`, `revision.commit: ff8fe51...`, identical to
`resolution-001`'s own commit — no new frozen subject) declaring `scope`
(8 exact repository-relative paths) and `targets: [R001, R002, R003]`.
`manifest.yml`'s `review-002` iteration entry's `subject_provenance` now
reads `resolution-001-scope` instead of `resolution-001`.

`resolution-001-scope`'s declared `scope` was independently checked
against the real Resolution Delta:

```
$ git diff --name-only 60b699bb69c06ed0b078572dd705191e73441c68 ff8fe51cc3dd237252c579f9775d8122254bf189 \
    -- . ':!.../manifest.yml' ':!.../provenance.yml' ':!.../review.md'
.forge/changes/CHG-0046-.../discovery.md
.forge/changes/CHG-0046-.../tasks.md
.forge/changes/CHG-0046-.../tdd-evidence.yml
.forge/changes/CHG-0046-.../verification.md
protocol/policies/merge-readiness.yml
src/forge_cli/merge_readiness/evaluator.py
tests/cli/test_merge_check.py
tests/unit/test_merge_readiness_policy.py
```

This is an exact match, path-for-path, with `resolution-001-scope`'s
declared `scope` list — neither broader (no hidden Out-of-Scope Mutation
concealed by an over-broad declaration) nor narrower (no in-scope work
falsely excluded). R004 is resolved.

### Provenance integrity checks

- **`resolution-001` unmodified (C-026 append-only).** Extracted
  `resolution-001`'s record as committed at `2f09140` (`chore(chg-0046):
  freeze Resolution revision at ff8fe51`) and diffed it (parsed YAML, not
  raw text) against the current record: byte-for-byte identical.
  `resolution-001-scope` is a genuinely new, separate record (distinct
  `id`, added at `9ef29aa`), not a disguised rewrite of `resolution-001`.
- **Both records agree on the commit they describe.** `resolution-001`
  and `resolution-001-scope` both bind `revision.commit:
  ff8fe51cc3dd237252c579f9775d8122254bf189` — identical.
- **`manifest.yml` internal consistency.** `review-002`'s
  `subject_provenance: resolution-001-scope` correctly resolves to an
  existing `role: resolution` record bound to the same commit
  `review-002`'s own `revision: chg-0046-resolution-001` already
  described; no orphaned or dangling reference.
- **`git log --follow` on `provenance.yml`** shows exactly the expected
  four commits (`c934594` Plan approval, `0913d92` Implementation freeze,
  `2f09140` Resolution freeze, `9ef29aa` R004 fix) — no history rewrite,
  no force-push artifact, no missing intermediate state.

### Independent spot-check re-run

Not accepted from Iteration 2's stated verdict alone — re-run directly in
this Iteration's own Execution:

```
.venv/bin/python -m pytest tests/cli/test_merge_check.py tests/unit/test_merge_readiness_policy.py -v
  -> 24 passed
.venv/bin/python -m pytest -q
  -> 704 passed, 2 warnings (same two pre-existing, unrelated FER warnings
     as Iterations 1-2)
```

### New Findings introduced by this Resolution

None. `new_material_findings: 0`.

### Convergence accounting

Iteration 2 ended with `new_material_findings: 1` (R004); this Iteration
(3) ends with `new_material_findings: 0` — the trailing run of
`resolution_verification` Iterations with `new_material_findings > 0` is
broken at length 1, well below the Convergence Limit of 2. No Convergence
Limit concern.

### Checked and found sound (Iteration 3)

- `resolution-001-scope`'s `scope` list matches the real Resolution Delta
  exactly (see above) — no Out-of-Scope Mutation, no over/under-broad
  scope declaration.
- `resolution-001` remains intact and unmodified since its original
  freeze commit.
- `forge validate` passes cleanly against current repository state.
- Full pytest suite: 704 passed, consistent with Iterations 1-2.

### Conclusion

R004 is genuinely resolved: `resolution-001-scope` supplies exactly the
`scope`/`targets` metadata Protocol 2 §11 requires, referencing the same,
unchanged, already-twice-reviewed commit; `forge validate` now passes;
the declared scope independently verified accurate against the real
diff; `resolution-001` itself remains untouched, satisfying C-026's
append-only invariant. No new material finding. R003 (OBSERVATION)
remains open, non-blocking, unchanged since Iteration 1. This Review is
**PASS**.
