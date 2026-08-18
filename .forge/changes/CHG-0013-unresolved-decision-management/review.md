---
forge:
  artifact: review
  schema: 1
change: CHG-0013
status: active
---
# Strict Review — Unresolved Decision Management

## Iteration 1 — REQUEST CHANGES

Executed by an independent Agent invocation (general-purpose, spawned
fresh, no shared conversation context with the Implementation session).
Execution/Context: `chg-0013-review-session-1` / `chg-0013-review-context-1`
— distinct from the Implementation's `chg-0013-impl-session-1` /
`chg-0013-impl-context-1`. Subject reviewed: `40dbfb94dfda9909c47ad158c1e5f6b6d2da903e`
(`implementation-001`), with the post-freeze metadata commit `ba5b880`
examined for Protocol 2 §5 compliance.

### Verification performed

`git log`/`git status`/`git diff 28bb6f3..40dbfb9` (full diff read) and
`git diff 40dbfb9..HEAD`; `forge validate` run twice independently;
`git stash push -u -- .codex docs/document-2026-08-13T04-46-37-625Z.md
docs/superpowers uv.lock` followed by `forge validate`, then `git stash
pop`, run twice, with final state re-verified via `git status
--porcelain=v1 --untracked-files=all`, `git diff --stat`, `git stash
list`, `git rev-parse HEAD`; `python -m pytest -q` (full suite) and
`pytest tests/unit/test_unresolved_decisions.py -v` individually; a
standalone scratch script calling `validate_project` directly with
adversarial fixture manifests not present in the existing test suite
(written to the session scratchpad, outside the repository, deleted after
use); the C-047–C-050 backfill compared byte-for-byte against the
canonical text.

### Findings

**CHG-0013-R001 (BLOCKER)** — `verification.md` misattributed the live
`forge validate` `C-026` finding to four pre-existing untracked paths,
"verified... via `git stash`." The Reviewer reproduced that exact stash
sequence independently and found the finding persists with those four
paths removed — the claim is false. Actual root cause, found by tracing
`_review_control_metadata_paths`/`_reviewable_workspace_delta`
(`src/forge_cli/validation/__init__.py`): the Protocol 2 §5 review-control
metadata exception is exactly `{manifest.yml, provenance.yml, review.md}`
— **not `verification.md`**. The post-freeze commit `ba5b880` modified
`verification.md` (adding the very paragraph making the false claim, plus
the TDD-ordering-deviation paragraph), which is not in the exempted set —
a genuine post-freeze mutation of the reviewable subject, exactly what §5
says invalidates the binding. The freeze is genuinely broken and the
recorded diagnosis for it is factually wrong.

**CHG-0013-R002 (MAJOR)** — the product/contract human-authority floor
(C-055, FR-017, `authority_floor` in `protocol/policies/decision.yml`) was
only checked in the narrow combination `authority == human AND
resolved_via == autonomous_decision`. `_validate_unresolved_decisions`
never checked that `class in {product, contract}` implies `authority ==
human`. Empirically confirmed: a manifest with `class: product, authority:
agent, resolved_via: autonomous_decision` validated with zero findings.
`architecture.md` claims "No project-configurable relaxation of
product/contract Authority below human" as an architectural guarantee the
mechanical layer did not actually deliver for a manifest setting
`authority` directly. Not disclosed anywhere as a known limitation.

**CHG-0013-R003 (MINOR)** — `invalidates` referencing an artifact key
entirely absent from `artifacts` (as opposed to present-but-complete)
silently passed, because `artifacts.get(key)` returns `None`, not a value
in `{"complete","approved"}`. Confirmed empirically with a synthetic
manifest.

**CHG-0013-R004 (MAJOR)** — the disclosed TDD-ordering deviation (C-009:
`_validate_unresolved_decisions` was authored before its test file) is
real, not merely stylistic — RED did not chronologically precede
Implementation, full stop — even though the reconstructed-RED mitigation
and its disclosure in `verification.md`/`tdd-evidence.yml`/
`knowledge-capture.md` are thorough and honest, not concealment. Per this
Change's own precedent (CHG-0012's explicit accept/reject residual-risk
decision), a real Contract deviation needs an explicit accept/reject
engineering decision recorded through the appropriate mechanism, not left
as a paragraph for the Reviewer to silently wave through. Judged MAJOR
(real, mitigated by faithful reconstruction and full transparency — not
BLOCKER).

**CHG-0013-R005 (OBSERVATION)** — `supersedes`/`superseded_by` are
schema-declared but never read/validated by `_validate_unresolved_decisions`
(no check that a `superseded` entry's `superseded_by` points at an
existing sibling, or that the two fields are mutually consistent).
Consistent with `architecture.md`'s own enumerated validator scope, which
never claims to check these fields — not a broken promise, a completeness
gap worth tracking.

**CHG-0013-R006 (OBSERVATION)** — every Decision-related finding is
tagged `code: "C-051"` regardless of which of the ~15 distinct checks
failed (shape, duplicate ID, C-055, C-057, INV-003 all report `C-051`,
distinguishable only by free-text `message`). Mirrors the pre-existing
`_finding`/`"C-026"` umbrella-code convention, so not a new anti-pattern,
but a closer mismatch than that precedent since C-051 is narrowly titled.
Low impact (`code` is display-only).

**CHG-0013-R007** — reviewed, no defect found: the four-class taxonomy
rationale (EVIDENCE/DISCOVERY exclusion) is coherent and specific; the
Reviewer looked for an uncovered concept and did not find one.

**CHG-0013-R008** — reviewed, no defect found: the C-047–C-050 backfill is
byte-for-byte identical (modulo line-wrapping) to the canonical text;
`pytest -q` independently confirmed at 389 passed, matching the artifact's
own claim exactly; `test_legacy_manifests_are_unaffected` confirmed
against this repository's own real `CHG-0001`–`CHG-0012` manifests.

### Verdict

**REQUEST CHANGES.** R001 alone blocks Completion (the review subject's
own freeze is invalid and its stated root-cause is wrong). R002 is a
second, independent MAJOR defect in the mechanism's core security
property. R004 requires an explicit human accept/reject decision, not
silent disclosure. R003/R005/R006 lower-severity, tracked.

No file was modified by this Review. The one working-tree mutation
performed (`git stash push -u` on the four untracked paths, to reproduce
the artifact's claim) was reverted immediately after each of two test
runs; final state verified unchanged (`git status`, `git diff --stat`,
`git stash list`, `git rev-parse HEAD` all confirmed). The scratch probe
script was written only outside the repository and deleted after use.

## Resolution 1

Performed by the original Implementation session (role: `resolution`,
distinct Role from Reviewer per C-026; a *different* independent
Execution/Context is required again for the Resolution Verification that
follows, not for this Resolution itself — matching how CHG-0011 handled
its own first Resolution).

- **R001**: root cause corrected in `verification.md` (the false stash-based
  diagnosis replaced with the actual §5 exemption-set explanation).
  `implementation-001` superseded by `implementation-002`, a fresh freeze
  commit that includes the corrected `verification.md` and the R002/R003
  code fixes as part of the frozen subject itself (not a post-freeze
  mutation of it). `review-001` updated to reference `implementation-002`.
- **R002**: fixed with TDD (RED confirmed first — see `tdd-evidence.yml`
  cycle TDD-010). `_DEC_AUTHORITY_FLOOR = {"product": "human", "contract":
  "human"}` added; `_validate_unresolved_decisions` now checks it
  independently of the `resolved_via` combination. Three new tests.
- **R003**: fixed with TDD (RED confirmed first — TDD-011). The C-057
  `invalidates` check now distinguishes "key absent from `artifacts`" from
  "key present and complete/approved"; both are findings. One new test.
- **R004**: not self-resolved. Presented to the human user as an explicit
  Decision, structured as Question/Alternatives/Trade-offs/Recommendation/
  Confidence/Authority, per the Reviewer's own instruction — Authority:
  human, by direct analogy to `review.convergence_decision`'s
  `accept_residual_risk` option (Protocol 2, CHG-0011), which this Change's
  own Resolver is not entitled to select on its own behalf either.

  **Decision recorded:** `option: accept_residual_risk` (informal, this is
  not a `review.convergence` Non-Convergence episode so the formal
  `convergence_decision` schema field does not apply — recorded here in
  prose instead). **Reason (human-provided):** accepted the Resolver's
  Recommendation (Confidence: MEDIUM) as-is: the historical TDD-ordering
  deviation on commit `40dbfb9` remains in Git history unaltered (no
  rebase/rewrite); the harm C-009 exists to prevent (tests shaped to
  confirm an already-written implementation rather than define correct
  behavior) did not materialize, evidenced by the reconstructed RED finding
  8 genuine gaps, and by TDD-010/TDD-011 (the R002/R003 fixes) independently
  demonstrating genuine RED-first discipline going forward. No further
  corrective action beyond what Resolution 1 already performed.
- **R005, R006**: accepted as documented follow-up, not fixed in this
  Resolution (matches the Reviewer's own severity assessment and rationale;
  recorded in `knowledge-capture.md`).

Resolution Scope (files touched by this Resolution, for the Resolution
Verification that follows):
`.forge/changes/CHG-0013-unresolved-decision-management/verification.md`,
`.forge/changes/CHG-0013-unresolved-decision-management/manifest.yml`,
`.forge/changes/CHG-0013-unresolved-decision-management/provenance.yml`,
`.forge/changes/CHG-0013-unresolved-decision-management/architecture.md`,
`.forge/changes/CHG-0013-unresolved-decision-management/knowledge-capture.md`,
`.forge/changes/CHG-0013-unresolved-decision-management/traceability.yml`,
`.forge/changes/CHG-0013-unresolved-decision-management/tdd-evidence.yml`,
`src/forge_cli/validation/__init__.py`,
`tests/unit/test_unresolved_decisions.py`.
Resolution Targets: `CHG-0013-R001`, `CHG-0013-R002`, `CHG-0013-R003`.

## Iteration 2 — PASS (`kind: resolution_verification`)

Executed by a second, independent Agent invocation (general-purpose,
spawned fresh, no shared context with Implementation, Resolution, or
Iteration 1's Reviewer). Execution/Context: `chg-0013-verify-session-1` /
`chg-0013-verify-context-1`. Subject: `resolution-001`, commit
`695fab81489f7bad6938dc944dbbdecdf912860f`.

### Verification performed

`git diff 40dbfb9..695fab81` (full, filtered per declared-scope file) and
`git diff 695fab81..3320913` (the post-freeze bookkeeping commit, checked
specifically for a repeat of R001's exact bug pattern — found clean, only
`manifest.yml`/`provenance.yml` touched); `forge validate`; independent
re-reproduction of the `git stash push -u -- .codex
docs/document-2026-08-13T04-46-37-625Z.md docs/superpowers uv.lock` +
`forge validate` + `git stash pop` sequence against the *corrected*
subject; `pytest tests/unit/test_unresolved_decisions.py -v` (18 tests);
`pytest -q` (full suite, 393); two inline adversarial Python probes calling
`_validate_unresolved_decisions` directly with hand-crafted manifests
targeting the R002/R003 checks; comparison against CHG-0011's own
`resolution-001`/`review-002` precedent for how `manifest.yml`/
`provenance.yml` appearing in the Resolution Delta outside declared
`scope` should be treated.

### Resolution Delta vs. declared scope

**No Out-of-Scope Mutation.** The Delta touched the 8 declared `scope`
files plus `manifest.yml`/`provenance.yml` (review-control bookkeeping
only — recording that Iteration 1 happened — no reviewable engineering
claim altered through them), consistent with the Protocol 2 §5
review-control exemption set and directly precedented by CHG-0011's own
`resolution-001` leaving `provenance.yml` out of its declared `scope`
while its diff still touched it (that Change's own `review-002`,
PASS, ruled the same way).

### R001, R002, R003 — verified genuinely fixed, independently re-reproduced

R001: `verification.md`'s diagnosis now correctly attributes the freeze
break to `verification.md`'s own post-freeze mutation, matching Iteration
1's finding exactly; re-running the stash sequence against the *current*
subject confirms the untracked-paths diagnosis is genuinely correct this
time (`forge validate` clean with them stashed, the `C-026` finding
present with them restored). R002: `_DEC_AUTHORITY_FLOOR` checked
unconditionally; seven hand-crafted adversarial manifests found no escape
from the floor. R003: the `invalidates` check now distinguishes absent
from present-and-complete/approved; adversarial probing confirmed.

### New finding

**CHG-0013-R009 (OBSERVATION)** — an `artifacts` value of `None`/`null`
(as opposed to absent, R003's actual target, or `"complete"`/`"approved"`)
still bypasses the C-057 `invalidates` check. No code path in this
repository ever writes a `null` artifact value; accepted as documented
follow-up (`knowledge-capture.md`), not blocking, same treatment as
R005/R006.

### R004 assessment

Found plausible, structurally conformant (Question/Alternatives/
Trade-offs/Recommendation/Confidence/Authority all present), and
internally consistent across `review.md`, `tdd-evidence.yml`, and
`knowledge-capture.md`. Cannot be verified from outside this session with
absolute certainty to be a genuine human act rather than the Resolver's
own invention, but the content is not self-serving (accepts a real
historical deviation as residual risk rather than erasing it) and matches
the format this mechanism itself requires.

### Verdict

**PASS.** `full_review_required: false`. No Out-of-Scope Mutation; R001,
R002, R003 genuinely fixed and independently re-verified; R004 plausibly
recorded; one new OBSERVATION (R009) carried forward as follow-up, not
blocking; full suite passes at the claimed count (393).

No file was modified by this Review. Working tree state confirmed
unchanged before/after (`git status`, `git diff --stat`); the one
temporary mutation (`git stash push -u` on the four untracked paths) was
reverted immediately and verified restored. All adversarial probing was
inline Python, no files written to the repository.
