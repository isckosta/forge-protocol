---
forge:
  artifact: review
  schema: 1
change: CHG-0046
status: active
---

# CHG-0046 · Review

## Verdict

**REQUEST CHANGES (current, Iteration 4 — `kind: resolution_verification`,
FAILED).** A new BLOCKER (R005) was independently found in
`resolution-002`'s own Resolution Delta — the design that replaced the
`state.current`-keyed mechanism Iterations 1–3 reviewed. Iteration 3's
PASS below applied to the subject *then* current (`ff8fe51`, Resolution
`resolution-001-scope`); that subject was superseded by `resolution-002`
(`6c6cdab`) after an external reviewer (Codex, PR #37) found the design
Iterations 1–3 all passed directly contradicted
`protocol/versions/2/specification.md` §5. Iteration 4 reviews that new
subject and does not pass it. See "## Iteration 4 — Resolution
Verification" below.

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
- **Iteration 3** (`kind: resolution_verification`) — **PASS** (of the
  then-current subject `ff8fe51`, later superseded): R004 resolved by a
  new, additive `resolution-001-scope` provenance record
  (`resolution-001` itself unmodified, append-only per C-026) declaring
  the exact `scope`/`targets` Protocol 2 §11 requires; `forge validate`
  passed against that subject; `resolution-001-scope`'s declared `scope`
  independently confirmed to match the real Resolution Delta exactly; 0
  new material findings. See "## Iteration 3 — Resolution Verification"
  below for full detail. Iterations 1 and 2's verdict text is left
  verbatim below as the historical record.
- **Iteration 4** (`kind: resolution_verification`) — **FAILED**: reviews
  `resolution-002` (`6c6cdab`), the design that replaced the
  `state.current`-keyed mechanism after Specification Drift. 1 new BLOCKER
  (R005 — the renewal record's ancestor check has no lower bound at the
  current `subject_commit`, so a renewal record anchored during an earlier
  freeze cycle silently and permanently tolerates an unrelated,
  unexplained divergence from a later frozen subject — independently
  reproduced end-to-end). See "## Iteration 4 — Resolution Verification"
  below for full detail.

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
| **Iterations** | 4 |
| **Current Subject** | `6c6cdab52cc519bff21b444188b6c059585e36d0` (Resolution `resolution-002`) |
| **Open Blockers** | 1 (R005) |
| **Open Majors** | 0 |
| **Open Minors** | 0 |
| **Open Observations** | 1 (R003) |
| **Final Iteration** | 4 |
| **Result** | FAILED |

Iteration 1 subject (superseded): `60b699bb69c06ed0b078572dd705191e73441c68`.
Iteration 2/3 subject (superseded): `ff8fe51cc3dd237252c579f9775d8122254bf189`.
R001/R002 (Iteration 1, MAJOR) resolved by `resolution-001` and
independently re-verified in Iteration 2 — no longer outstanding. R004
(Iteration 2, MAJOR) resolved by `resolution-001-scope` and independently
re-verified in Iteration 3 — no longer outstanding, against that
(superseded) subject. R005 (Iteration 4, BLOCKER) is open against the
current subject (`resolution-002`) and blocks Completion.

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
| R005 | BLOCKER | Open | 4 |

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
**PASS** (of the subject then current, `ff8fe51`; superseded by Iteration
4 below, which reviews a *new* frozen subject, `resolution-002`, produced
after external review found the design Iteration 1–3 all reviewed itself
violated Protocol §5).

## Iteration 4 — Resolution Verification

### Scope and authority

Independent Resolution Verification of `resolution-002`
(`6c6cdab52cc519bff21b444188b6c059585e36d0`), executed in a freshly
spawned Execution and Execution Context
(`claude-code-review-0046-independent-4` /
`claude-code-review-session-2026-08-25-iter4`, recorded in this Review's
own `provenance.yml` entry `review-004`), distinct from every prior
Execution/Context in this Change's history and from `resolution-002`'s
own (`claude-code-implementation-0046` /
`claude-code-session-2026-08-25`). Per C-047/§11, bounded to
`PR37-CODEX-001` (the sole Finding `resolution-002` targets), defects
within `resolution-002`'s own Resolution Delta, and Out-of-Scope
Mutation. Unlike Iterations 2–3, this Iteration does independently
re-derive the design's conformance to Protocol §5/§8/§11/§14's own text
directly — that is precisely the gap the prior three Iterations left
open (none of them checked the design against the Protocol text itself;
that is exactly how the `state.current` defect survived three internal
Reviews), and the task that opened this Iteration required it.

### Resolution Delta — no Out-of-Scope Mutation, scope matches exactly

```
$ git diff --name-only ff8fe51cc3dd237252c579f9775d8122254bf189 6c6cdab52cc519bff21b444188b6c059585e36d0
CHANGELOG.md
docs/adr/0018-merge-readiness-post-review-artifact-scope.md
.forge/changes/CHG-0046-.../architecture.md
.forge/changes/CHG-0046-.../knowledge-capture.md
.forge/changes/CHG-0046-.../manifest.yml
.forge/changes/CHG-0046-.../provenance.yml
.forge/changes/CHG-0046-.../review.md
.forge/changes/CHG-0046-.../specification-drift.md
.forge/changes/CHG-0046-.../specification.md
.forge/changes/CHG-0046-.../tasks.md
.forge/changes/CHG-0046-.../tdd-evidence.yml
.forge/changes/CHG-0046-.../verification.md
src/forge_cli/merge_readiness/evaluator.py
tests/cli/test_merge_check.py
```

Subtracting the three always-exempt review-control paths
(`manifest.yml`/`provenance.yml`/`review.md`) leaves exactly the 11 paths
`resolution-002`'s own `scope` declares — no more, no less. No file
outside this Change's own directory, `evaluator.py`, its test, and the
Documentation Impact artifacts (`CHANGELOG.md`, the ADR) appears. **No
Out-of-Scope Mutation; no under- or over-declared scope.**

### Independent test/CLI re-run

Not accepted from `verification.md`'s claim:

```
.venv/bin/python -m pytest tests/cli/test_merge_check.py tests/unit/test_merge_readiness_policy.py -v
  -> 26 passed (includes TDD-008..011:
     test_merge_check_tolerates_change_local_artifact_with_anchored_renewal_record,
     test_merge_check_still_flags_change_local_edit_without_renewal_record,
     test_merge_check_ignores_unanchored_renewal_record,
     test_merge_check_scopes_renewal_tolerance_to_the_declared_paths)
.venv/bin/python -m pytest -q
  -> 706 passed, 2 warnings (same two pre-existing, unrelated FER warnings)
```

CHG-0045's real PR #36 commits, reproduced from a disposable
`git worktree` (`git worktree add /tmp/verify-chg0045
8cc69ecf1e3b81ab0d73b14410d8c1845feb7c6c --detach`, confirmed `forge_cli`
loaded is this repository's own currently-checked-out package), not
trusted from `verification.md`'s claim:

```
$ forge change merge-check --base 3aa195539218b8902296ff37f043359dd6e2614c --head 8cc69ecf1e3b81ab0d73b14410d8c1845feb7c6c
FAIL MR-015 [CHG-0045]: REVIEW SUBJECT STALE
MERGE BLOCKED
```

Matches `verification.md`'s disclosed claim exactly — that branch predates
this Resolution's correction and has no renewal record, so MR-015
correctly re-fires. Worktree removed after (`git worktree remove
/tmp/verify-chg0045 --force`).

### Independent Protocol-text conformance check (the check Iterations 1–3 never performed)

Read `protocol/versions/2/specification.md` §5, §8, §11, §14 directly,
not through Architecture's or Specification's own paraphrase of it:

(a) **Unconditional three-file exception.** Confirmed: the corrected
`evaluator.py` allowed-set is still exactly `{manifest.yml, provenance.yml,
review.md}`; `manifest.state` is not read anywhere in the MR-015 block
(`grep state.get\("current"\)` inside the block: zero matches). Conforms.

(b) **§5's "Appending a new provenance record... remains allowed" / §8's
"without renewed provenance."** The renewal mechanism is generally the
right *shape* — an explicit, anchored, additional provenance record, not
a mutable flag. But see R005 below: the specific ancestor test the code
uses to decide whether a renewal record counts as "renewed provenance for
*this* delta" is too permissive, and empirically defeats §8's own
"without renewed provenance" condition for the specific delta under
evaluation once a *second* freeze has occurred.

(c) **§11's `role: resolution`/`targets` model, and CON-004's
`role: implementation` convention for non-Finding-driven renewals.**
Sound and non-conflicting. `resolution-002` itself correctly uses
`role: resolution` with `targets: [PR37-CODEX-001]` (a real external
Finding), consistent with §11. CON-004's guidance that routine
Documentation Impact/Knowledge Capture bookkeeping should use
`role: implementation` instead is a defensible authoring convention, not
itself mechanically enforced beyond FR-001's own check (as CON-004 itself
discloses) — no defect here.

(d) **`_first_committed_record` reuse for renewal-record anchoring.**
Sound for the specific, narrow property it verifies: that a referenced
renewal record's *content* has not been silently rewritten since its
first committed representation (verified directly: `renewal-001`
rewritten-scope fixture in `test_merge_check_ignores_unanchored_renewal_record`
correctly still fires MR-015). But immutability-once-anchored and
"this record is temporally valid evidence for *this* freeze's delta" are
two different properties. Reusing MR-021's function correctly gives
renewal records the first property; nothing in the design gives them the
second — that gap is R005 below.

### R005 — BLOCKER — a renewal record's ancestor check has no lower bound at `subject_commit`, so a renewal record anchored during an *earlier* freeze cycle silently and permanently tolerates an unrelated, unexplained divergence from a *later* frozen subject

**Found:** `evaluator.py`'s renewal loop (the code this Resolution
introduces) accepts any `role: implementation`/`resolution` record whose
`revision.commit` satisfies `git merge-base --is-ancestor renewal_commit
head_revision` — i.e. *any* ancestor of `head_revision`, unbounded in how
far in the past. It never additionally checks that `renewal_commit` is a
descendant of (or equal to) the *current* `subject_commit` — i.e. that
the renewal record actually postdates the freeze it is supposedly
renewing. Architecture's own "Alternatives Considered" rationale for
choosing "ancestor" over "equals `head_revision` exactly" is about
accommodating the two-commit freeze convention (the renewal's commit is
typically the *parent* of `head_revision`) — it never argues for, or
even considers, tolerance reaching arbitrarily far into the past, across
a *prior*, already-superseded freeze cycle.

This is also a direct textual conflict this Resolution itself introduces
and never reconciles: **Specification's own FR-001 Requirement and AC-001
both say the renewal record's `revision.commit` must "equal
`head_revision` exactly"** — not "be an ancestor of." Architecture's
Design section and the actual code both implement the strictly broader
"ancestor of (or equal to)" relation instead, with Architecture's
Alternatives Considered section explicitly documenting the deviation from
its *own* first draft — but neither Architecture nor the code was
reconciled back against Specification's still-unedited FR-001/AC-001 text,
which remains normative for this Change (per CON-002/CON-004's own
framing) and was rewritten in this exact commit (`resolution-002`'s
declared `scope` includes `specification.md`). Two artifacts this single
Resolution both touched now disagree with each other on an
acceptance-critical detail, and neither discloses the disagreement.

**Evidence — directly reproduced**, via a disposable fixture repository
(not this repository): froze a Change's Review subject at `S1`
(`state.current: complete`, admissible subject/reviewer/verification
provenance). Added a legitimate, anchored `renewal-001` record (`role:
implementation`, commit between `S1` and a later `S2`, `scope: [...,
protected.md]`) explaining a genuine post-`S1` `knowledge-capture.md`
addition — `protected.md` was *also* named in the same renewal's scope
in this fixture, deliberately, to probe the boundary. A **second**,
independent Strict Review then passed and froze a **new** subject `S2`
(a new `role: resolution` provenance record, a new `review.iterations`
entry pointing `subject_provenance` at it) — `protected.md` unchanged at
`S2`, identical to `S1`. Then, **after `S2`'s freeze, with no new
renewal record of any kind**, `protected.md` was tampered
(`"TAMPERED after S2 freeze, no new renewal record covers this!"`) and
committed as `head`. Ran `forge change merge-check --base <base> --head
<head>` from that fixture repo (confirmed loading this repository's own
currently-checked-out `merge_readiness` package):

```
MERGE READY
```

**MR-015 did not fire.** The stale `renewal-001` record — anchored,
still an ancestor of `head_revision` (trivially, forever, once
committed), scope still literally containing `protected.md` — silently
granted tolerance for a divergence from the *current* frozen subject
(`S2`) that record was never written to explain and has no relationship
to. The correct result is `MERGE BLOCKED`/`FAIL MR-015` for
`protected.md`, since no provenance record explains the `S2`→`head`
delta to that file at all.

**Impact:** This is not a cosmetic gap. It means a renewal record, once
committed and anchored, grants **permanent, cumulative, non-expiring**
tolerance for every path in its `scope` across *every* subsequent freeze
cycle a Change ever goes through — not narrowly scoped "auditable per
commit" tolerance for the one delta it was written to explain, which is
exactly what CON-002 and Architecture's own Architectural Goals both
promise ("auditable per-commit, not a single mutable flag covering every
future commit once flipped once" / "a renewal record covering
`knowledge-capture.md` does not blanket-cover... unrelated
`specification.md`"). The unbounded-ancestor check makes that promise
false across freeze *cycles*, even though it is honored within a single
cycle (AC-007's own scenario, correctly tested). Directly relevant to
this repository's *own* history: `resolution-001-scope`
(`ff8fe51cc3dd237252c579f9775d8122254bf189`, already committed, anchored,
non-empty `scope` naming `evaluator.py`, `verification.md`, `tasks.md`,
`tdd-evidence.yml`, and the two test files) will — per this same defect —
continue to silently tolerate any *future*, unrelated, unexplained
divergence of those exact paths from whatever subject is frozen *next*,
for the rest of this Change's lifetime, unless a stricter lower bound is
added. This is precisely the class of freeze bypass §5/§8 exist to
prevent, and precisely the class of defect this whole Resolution was
written to fix for the `state.current` case — reintroduced, in a
narrower but still live form, by the fix itself.

**Required Resolution (not performed by this Iteration, per its own
bounded authority and the instruction not to fix findings inline):** The
renewal-commit ancestor check must additionally require `renewal_commit`
to be a descendant of (or equal to) the *current* `subject_commit` —
i.e. `git merge-base --is-ancestor subject_commit renewal_commit` in
addition to (or instead of) the existing `--is-ancestor renewal_commit
head_revision` check — so a renewal record can only supply tolerance for
divergence from the freeze it actually postdates, not from every
subsequent freeze indefinitely. Separately, Specification's FR-001/AC-001
"equals `head_revision` exactly" text and Architecture's/the code's
"ancestor of head_revision" must be reconciled — either Specification is
corrected to state the actual (once properly bounded) relation, or the
implementation is tightened to match Specification's literal text — they
cannot continue to silently disagree.

### New Findings introduced by this Resolution

One new Finding: **R005 (BLOCKER)** — a defect in the renewal-tolerance
mechanism this Resolution's own Resolution Delta introduces (entirely new
code in `evaluator.py`, not present before `resolution-002`), independently
reproduced end-to-end against a disposable fixture, not a hypothetical.
Not an Out-of-Scope Mutation (it is inside `evaluator.py`, squarely within
`resolution-002`'s own declared `scope`) — it is a correctness defect
within the Resolution Delta, within this Iteration's bounded authority
(C-047, point 2) to discover and report.

### Convergence accounting

`new_material_findings: 1` (R005). `full_review_required: false` — R005
is a scoped defect within `evaluator.py`, the file `resolution-002`'s own
`scope` already names; it is not Out-of-Scope Mutation (§11's specific
trigger for mandatory `full_review_required: true`), so a further,
narrowly-bounded Resolution + Resolution Verification remains the correct
next step, not escalation to a fresh, unrestricted Initial Review.
`consecutive_unconverged_verifications`: the trailing run of
`resolution_verification` Iterations with `status: failed` and
`new_material_findings > 0` was broken at Iteration 3 (`status: passed`,
`new_material_findings: 0`); this Iteration (4) starts a **new** trailing
run of length 1 — below the Convergence Limit of 2. No Convergence Limit
concern; no `convergence_decision` is required on the next Iteration.

### Checked and found sound (Iteration 4)

- Resolution Delta matches `resolution-002`'s declared `scope` exactly —
  no Out-of-Scope Mutation, no over- or under-broad declaration.
- Full pytest suite independently re-run: 706 passed, consistent with
  `verification.md`'s claim.
- `forge validate`/`forge doctor` independently re-run against current
  repository state at the time of this check (pre-freeze of this
  Iteration's own subject binding): clean except the same two
  pre-existing, disclosed `WARN`s.
- CHG-0045's real PR #36 reproduction independently re-verified via
  disposable `git worktree`: `MR-015` correctly re-fires, matching
  `verification.md`'s disclosed claim.
- AC-007's own scenario (a renewal record's tolerance does not blanket-cover
  an unrelated path changed in the *same* commit) is correctly implemented
  and tested (`test_merge_check_scopes_renewal_tolerance_to_the_declared_paths`)
  — R005 is a distinct defect, about tolerance surviving *across* freeze
  cycles, not about scope leaking *within* one.
- `_first_committed_record` reuse for renewal-record content-immutability
  is sound and correctly tested
  (`test_merge_check_ignores_unanchored_renewal_record`).

### Conclusion

`resolution-002` correctly fixes `PR37-CODEX-001` for the *specific*
scenario Codex found and for the scenario this Change's own AC-001/
AC-003/AC-006/AC-007 test: a `state.current`-keyed blanket exception is
gone, `manifest.state` is never read, and single-freeze-cycle renewal
tolerance is properly anchored and path-scoped. But the replacement
mechanism itself does not fully conform to Protocol §5/§8's freeze
invariant once a Change goes through more than one freeze cycle — which
this Change's own history (four Review Iterations, two Resolutions, two
distinct frozen subjects so far) demonstrates is the normal case, not an
edge case — because the renewal record's ancestor check has no lower
bound at the current `subject_commit`. This is independently reproduced,
not hypothetical, and is a defect within `resolution-002`'s own
Resolution Delta. Per the instructions governing this Iteration: **do not
mark this passed under pressure to finally get this done.** This Review
Iteration is **FAILED**.
