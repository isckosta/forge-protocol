---
forge:
  artifact: review
  schema: 1
change: CHG-0045
status: passed
---
# Strict Review — CHG-0045

## Verdict

**PASS (final, Iteration 4 — `kind: resolution_verification`).** No
blocking Findings remain outstanding. Two non-blocking OBSERVATIONs remain
open: R008 (an unrelated, pre-existing Core `forge validate` gap, Out of
Scope for this Change — its Iteration-3-disclosed untracked-file trigger
is no longer present in the working tree as of Iteration 4) and R009 (a
pre-existing `CHANGELOG.md` prose mention of the bare `forge adapter
doctor` command, not itself inaccurate, recorded per C-050, not targeted
by `resolution-003`). See Iteration 4, below, for PR36-CODEX-001's
verification.

- **Iteration 1** (`kind: initial_review`) — **REQUEST CHANGES**: 1
  BLOCKER (R001), 3 MAJOR (R002/R003/R004), 1 MINOR (R005), 0 OBSERVATION.
- **Iteration 2** (`kind: resolution_verification`) — **REQUEST CHANGES**:
  0 BLOCKER, 1 new MAJOR (R007 — `resolution-001`'s own record fails
  mechanical scope verification), 0 new MINOR, 2 new OBSERVATION (R006, a
  premature-tense wording issue; R008, an unrelated, pre-existing Core
  `forge validate` latent bug). R001-R005 all independently re-verified
  resolved against actual repository state at the frozen Resolution
  subject `b43cb761d08433ae8a0b7dbc3be82d1e57f09221`, not accepted from
  `resolution-001`'s own claim; the Resolution Delta (`git diff
  23d763b..b43cb76`) contains exactly the six files `resolution-001`
  declares, all inside this Change's own directory — no Out-of-Scope
  Mutation.
- **Iteration 3** (`kind: resolution_verification`) — **PASS**: R006
  (wording) and R007 (`resolution-001-scope`'s new provenance record,
  additive not a rewrite) both independently re-verified resolved; `forge
  validate` genuinely passes at the current repository state; the
  single-commit Resolution Delta for `95b521e` (computed the way Core's
  own `_resolution_delta` computes it — `to_commit^..to_commit`, not the
  cumulative range) is exactly the three files `resolution-002` declares
  — no Out-of-Scope Mutation; 0 new material findings (R008 recurs in a
  now-empirically-confirmed way but is not new substance — see below);
  Convergence Limit (2 consecutive `resolution_verification` Iterations
  with `new_material_findings > 0`) is **not** reached, since Iteration 3
  itself has `new_material_findings: 0`.
- **Iteration 4** (`kind: resolution_verification`) — **PASS**: verifies
  the fix of `PR36-CODEX-001`, an external, independent Codex review-bot
  finding on this repository's own open PR #36 (not a Finding raised by
  this Review): `workflow.md`'s Bootstrap guidance now correctly shows
  `forge adapter doctor <adapter-id>` (the real, required positional
  argument, confirmed by direct read of `adapter_cli.py::doctor`), both
  `workflow.md` sources remain byte-identical, both installed `SKILL.md`
  files carry the identical fix (confirmed by direct read and independent
  digest verification), and a genuine regression test was added. Resolution
  Delta (`resolution-003`'s frozen commit's own first-parent diff,
  `b626080^..b626080`, computed the way Core's own `_resolution_delta()`
  computes it to avoid contamination from the intervening CHG-0046 merge)
  is exactly the seven files `resolution-003` declares — no Out-of-Scope
  Mutation. 0 new material findings; one new non-blocking OBSERVATION
  (R009) recorded per C-050, not targeted by this Resolution.

Everything below this Verdict down to the end of the original `##
Conclusion` is Iteration 1's verbatim historical record, except the
Summary table immediately below, which is restated in Raised/Outstanding
form to account for R001-R007's resolution and R008/R009's disposition.
Iterations 2, 3, and 4 are appended at the end of this file in order.

`protocol/policies/review.yml` sets `blocking: [blocker, major]`; every
BLOCKER and MAJOR ever raised (R001, R002, R003, R004, R007) is now
resolved and independently re-verified. R005/R006 (non-blocking, also
resolved) and R008/R009 (non-blocking, open, Out of Scope) are the only
Findings with any remaining trace, and none of them block. This Change
may proceed toward Completion — subject to the R008 operational caveat in
Iteration 3, below, which is about repository hygiene, not about this
Review's own verdict (and, as of Iteration 4, no longer empirically
triggered — the working tree is clean of untracked files).

**REQUEST CHANGES (Iteration 1, `kind: initial_review`), as originally
recorded.** 1 BLOCKER, 3 MAJOR, 1 MINOR, 0 OBSERVATION — blocking per
`protocol/policies/review.yml` (`blocking: [blocker, major]`).

The generator-level de-duplication this Change sets out to make (FR-001
through FR-006) is real and independently verified end to end: the
Reviewer/Resolver-independence block renders exactly once in the actual
installed `SKILL.md`, every per-Flow section carries a working pointer to
it, the Codex Adapter imports the identical shared module rather than
defining its own copy, the hook frontmatter and script genuinely deny
`Edit`/`Write` mutation of the three protected paths (and genuinely allow
everything else, including deep-nested-path and trailing-suffix
false-positive cases I constructed myself), and both Adapters' installed
digests match their actual on-disk content byte-for-byte. That part of the
Implementation is sound.

What is not sound is the Change's own claimed evidence trail. Running
`pytest -q` against the frozen subject — independently, twice, once with a
scratch venv and once with this repository's own committed `.venv` —
produces **700 passed, 1 failed**, not the "701 passed, 0 failed"
`verification.md` and `provenance.yml`'s `implementation-subject-001`
record both assert. The failure is real, reproducible, and directly caused
by this Change's own `traceability.yml` (R001, below) — not a flake, not
an environment difference. Separately, `tasks.md`'s own checklist claims
work (`knowledge-capture.md`, "Documentation Impact evaluated") that does
not exist on disk and that `manifest.yml` itself correctly records as
still pending (R003), and a material, human-authority Decision
(`DEC-006`) is recorded in `manifest.yml` with no narrative anywhere
explaining what it is (R002). A Change whose own Specification requires
("FR-007") that "a Change, phase, or Review MUST NOT be declared complete
from narrative assertion alone" should not itself ship a false test-count
assertion and false task-completion checkmarks in its own frozen subject.

## Summary

Counting semantics, stated explicitly since the Protocol does not fix
them: **Raised** is cumulative — every Finding ever recorded in this
Review, in the Iteration that recorded it. **Outstanding** is the state
*after* the final Iteration, and is what `manifest.yml`'s
`review.blockers`/`majors`/`minors`/`observations` carry.

| Severity | Raised (It. 1) | Raised (It. 2) | Raised (It. 3) | Raised (It. 4) | Raised total | Outstanding | Blocking |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BLOCKER | 1 | 0 | 0 | 0 | 1 | 0 | yes |
| MAJOR | 3 | 1 | 0 | 0 | 4 | 0 | yes |
| MINOR | 1 | 0 | 0 | 0 | 1 | 0 | no |
| OBSERVATION | 0 | 2 | 0 | 1 | 3 | 2 | no |

R001 (BLOCKER, Iteration 1) and R002/R003/R004 (MAJOR, Iteration 1) are
resolved by `resolution-001` and verified in Iteration 2 — no longer
outstanding. R005 (MINOR, Iteration 1) is likewise resolved and verified.
R007 (MAJOR, Iteration 2) was resolved by `resolution-001-scope` and
verified in Iteration 3 — no longer outstanding. R006 (OBSERVATION,
Iteration 2, a wording issue) was resolved by `resolution-002` and
verified in Iteration 3 — no longer outstanding. R008 (OBSERVATION,
Iteration 2, an unrelated pre-existing Core `forge validate` latent bug,
recorded per C-050) remains open and outstanding — non-blocking to this
Review's own verdict, Out of Scope for this Change to fix, but see
Iteration 3's operational caveat about its concrete, empirically-confirmed
consequence for this Change's own path to a `forge validate`-clean
repository state (as of Iteration 4, the working tree is clean of
untracked files and this consequence is not currently triggered). R009
(OBSERVATION, Iteration 4, a pre-existing `CHANGELOG.md` prose mention of
the bare `forge adapter doctor` command, not itself inaccurate, recorded
per C-050) is likewise open and outstanding — non-blocking, not targeted
by `resolution-003`, proportionate for a human maintainer to address
alongside R008, not required by this Review.

## Review Subject

Frozen Implementation subject `23d763b5b076bd1fd3df75743e9df90fcc4b0423`
(`provenance.yml`, record `implementation-subject-001`), reviewed against
the Change's own baseline `3aa1955` (pre-Change `main` tip). The later
commit `1bb818b` (Implementation-subject-freeze provenance recording,
touching only `provenance.yml`) is Change-local review-control metadata,
exempt from the freeze per Protocol 2, and was confirmed — not assumed —
to touch nothing else: `git diff --stat 23d763b..1bb818b` shows exactly
one file, `provenance.yml`, 28 insertions, 0 deletions. `git status
--porcelain=v1 --untracked-files=all` at review time shows only three
untracked files predating and unrelated to this Change
(`.claude/CLAUDE.md`, `.playwright-mcp/`, `RELATORIO-SESSAO-2026-08-22.md`
— all disclosed as such in `provenance.yml`'s own
`implementation-subject-001` statement); the effective reviewable
workspace was clean.

## Review Execution Independence

This Review was executed in an Execution and Execution Context distinct
from the Implementation session that produced `implementation-subject-001`
(`claude-code-implementation-0045` / `claude-code-session-2026-08-24`),
per Contract C-026 and Protocol 2 §2: `claude-code-review-0045-independent`
/ `claude-code-review-session-2026-08-24` (see `provenance.yml`, record
`review-001`). It was performed cold, from repository state and the
governing prompt alone, with no access to the Implementation conversation
and no prior memory of this Change. Every material claim in
`verification.md`, `tdd-evidence.yml`, `traceability.yml`, and
`tasks.md` was independently reproduced against the actual repository
state — a real `pytest -q` run (twice, two separate interpreters), a real
`forge validate`/`forge doctor`/`forge adapter plan` run against this
repository's own real installation, real `sha256sum` digest spot-checks
against `installation.yml`'s recorded values, and real JSON payloads piped
directly into the actual generated hook script via `sh` — not accepted
from any artifact's own prose.

## Iteration 1 — REQUEST CHANGES

### R001 — BLOCKER — `verification.md` and `provenance.yml` both assert a passing full test suite that does not actually pass

**Problem:** `verification.md`'s Test Evidence section states: "`pytest -q`
(full suite): pre-Implementation baseline 692 passed; post-Implementation
701 passed, 0 failed". `provenance.yml`'s `implementation-subject-001`
record repeats the identical, specific claim: "full pytest suite 701
passed". Both are false. Running `pytest -q` against the frozen subject
produces:

```
FAILED tests/contract/test_protocol_contract.py::test_canonical_yaml_instances_satisfy_their_declared_schemas
1 failed, 700 passed, 2 warnings in ~85-90s
```

reproduced identically twice — once via a fresh scratch venv
(`pip install -e ".[test]"`), once via this repository's own committed,
pinned `.venv/bin/pytest` — with the working tree in the exact state
described in Review Subject above (clean except the three disclosed,
unrelated untracked files).

**Root cause, traced to the exact line:** the failing assertion is
`test_canonical_yaml_instances_satisfy_their_declared_schemas`
(`tests/contract/test_protocol_contract.py:147`), which validates every
canonical YAML instance in the repository — including this Change's own
`traceability.yml` — against its declared JSON Schema
(`protocol/schemas/traceability.schema.json`). That schema requires
`requirements.<key>.tasks` to be a non-empty array (`"minItems": 1`) for
every requirement key. This Change's own `traceability.yml` violates it
for three keys:

```
requirements.CON-001.tasks: []
requirements.CON-002.tasks: []
requirements.CON-004.tasks: []
```

(confirmed by direct `Read` of `traceability.yml` lines 14, 15, 17). This
is not a pre-existing, repository-wide condition this Change merely
inherited: I checked every `traceability.yml` under `.forge/changes/`
programmatically for a `CON-*` key with an empty `tasks` array, and
CHG-0045's is the only one in this repository's entire history with this
shape. CON-001/CON-002/CON-004 are genuinely task-less by their own
substance (no Plan item exists to "not add a new Protocol identifier," for
example) — but the schema does not carve out an exception for that, and
this Change's own `traceability.yml` does not supply one (e.g. a
placeholder task, or an `evidence`-only justification the schema would
accept), so the honest thing this Change needed to do was either satisfy
the schema or fix/except it — neither happened before freeze.

**Impact:** This is the exact scenario the reviewing brief for this
Session explicitly names as a BLOCKER by construction: a quantified,
specific evidence claim ("701 passed, 0 failed") recorded in both
`verification.md` and `provenance.yml`, asserted as directly-observed
fact ("Every new test... was run individually and as part of the full
suite; both confirmed green" — `verification.md`), that does not hold
against the actual frozen repository state. It is not a matter of
interpretation or environment drift: the failure is deterministic (a pure
JSON Schema validation over static YAML, no network, no time-dependence)
and was reproduced identically across two independent Python
environments.

**Suggested Resolution (non-blocking on this Review to specify, per
C-025):** Either add at least one task to each of CON-001/CON-002/CON-004
in `traceability.yml` (e.g. pointing at the Plan/Architecture item that
established the constraint, even if no dedicated Task executes it), or
correct `verification.md`/`provenance.yml`'s test-count claims to the
actual, reproduced figure before re-freezing, and re-run the full suite
one more time after the fix to confirm 0 failures before the next freeze.

### R002 — MAJOR — `DEC-006` is recorded in `manifest.yml` as a material, human-authority Decision with no narrative anywhere explaining what it is

**Problem:** `manifest.yml`'s `decisions[]` array includes:

```yaml
- id: DEC-006
  class: technical
  materiality: material
  status: resolved
  authority: human
  owning_artifact: tasks
  discovered_in: tasks
  resolved_via: human_decision
```

I searched every file in this Change's directory for the literal string
`DEC-006`. It appears exactly once, in `manifest.yml` itself. Nothing in
`tasks.md` (`DEC-006`'s own `owning_artifact`), `verification.md`,
`plan.md`, `architecture.md`, or any other Change artifact names,
describes, or cross-references it. Given its shape — `technical`,
`material`, `authority: human`, `discovered_in: tasks`,
`resolved_via: human_decision` — this most plausibly corresponds to the
operator's explicit, in-session authorization to bypass
`AdapterService`'s own `_reject_drift`/`_reject_conflicts` guards
(`tasks.md` T-016, `verification.md`'s "Adapter Republish" section), which
is exactly the shape of a material, human-authority technical Decision.
But no artifact ever makes that link explicit — a Reviewer (or any future
reader) can only guess.

**Impact:** This is a genuine traceability gap in exactly the discipline
this Change's own FR-007 exists to strengthen ("a Change... MUST NOT be
declared complete from narrative assertion alone; completion requires
resolving the actual Gate evidence"). `decisions[]` is structured
repository-native evidence; an entry with no corresponding rationale
anywhere is functionally a silent Decision, the pattern
`artifact-structure.md`'s Plan guidance explicitly warns against
("Implementation-time discoveries belong in ... a Decision record ... not
in a silent edit").

**Suggested Resolution:** Add a short, explicit `DEC-006` narrative to
`tasks.md` (or wherever it substantively belongs) naming exactly what was
decided, by whom, and linking it to the T-016 authorization narrative
already written — even a few sentences would close this gap, since the
underlying event is already honestly described elsewhere; it is only the
manifest cross-reference that is missing.

### R003 — MAJOR — `tasks.md` T-017/T-018 claim work as complete that does not exist on disk, contradicting `manifest.yml`'s own accurate state

**Problem:** `tasks.md` records, both checked `[x]`:

```
- [x] T-017 Documentation Impact evaluated — see `verification.md` /
      `knowledge-capture.md` (Plan item 14).
- [x] T-018 Wrote `verification.md`, `knowledge-capture.md`,
      `traceability.yml` from real Implementation evidence (Plan item 15).
```

`ls .forge/changes/CHG-0045-agent-adapter-architecture-skill-authority-consolidation/`
shows no `knowledge-capture.md` file exists anywhere in the Change
directory. `manifest.yml` itself, correctly, records
`documentation: pending`, `knowledge_capture: pending`, and
`documentation: {impact_evaluated: false}` — directly contradicting
T-017's "Documentation Impact evaluated" and T-018's "Wrote ...
knowledge-capture.md" claims. `grep -in "documentation\|changelog"` over
`verification.md` finds no Documentation Impact evaluation content either
(no CHANGELOG.md entry references CHG-0045; no `docs/adr/` entry exists
for it).

**Note on what is *not* wrong here:** `protocol/flows/full.yml` places
the `documentation` and `knowledge_capture` stages *after*
`strict_review`, and the `before_completion` gate (not any earlier gate)
requires `documentation_impact_evaluated`/`required_knowledge_capture_
complete`. So it is entirely legitimate for these to still be `pending`
at this stage — `manifest.yml`'s `state.current: strict_review` is
correct, and nothing about this finding blocks the Flow's own stage
ordering. Plan item 14 explicitly anticipated recording this "as a
Documentation Impact finding during Verification, not pre-decided here,"
which is the right instinct.

**Impact:** The problem is narrower but still real: `tasks.md` checks two
items off as `[x]` complete and describes them in the past tense ("Wrote
... knowledge-capture.md") when the referenced artifact was never
created and the manifest's own bookkeeping says the opposite. This is a
self-inconsistency inside the frozen Implementation subject's own
evidence — exactly the "no false Completion" (C-035) and "not... narrative
assertion alone" (this Change's own FR-007) discipline this Change asks
every future agent to honor.

**Suggested Resolution:** Correct T-017/T-018 in `tasks.md` to accurately
describe what was actually done at Verification time (e.g., "Documentation
Impact scoping recorded for the post-Review `documentation`/
`knowledge_capture` stages; CHANGELOG.md entry and knowledge-capture.md
deferred, per Plan item 14, to those stages") rather than checked-off,
past-tense claims of artifacts that do not exist.

### R004 — MAJOR — the Adapter Republish (T-016) exposed a real, unaddressed remediation gap in the exact drift-detection mechanism this Change tells every future agent to "trust and check," and neither Architecture's Risks nor the Specification's Compatibility Statement account for it

**Problem:** `verification.md`'s own "Adapter Republish — how it was
actually done" section honestly discloses that `forge adapter
update`/`forge adapter install` refused to run for *both* Adapters via
`AdapterService`'s own `_reject_drift`/`_reject_conflicts` guards, that
`publish_adapter_plan`'s own record-writer also declined, and that the
actual remediation required writing generated content directly via the
production `driver.project()` call and hand-rebuilding
`installation.yml` from real on-disk digests, under explicit, one-time
human authorization to bypass the guard (I independently confirmed
`src/forge_cli/adapters/service.py`, `ownership.py`, and `planner.py` were
*not* modified by this Change — the guard logic itself is intact for
future runs, which is good — but no *supported*, safe recovery command
exists for the situation this Change's own DEC-004 established is latent
in every Forge-governed repository with this Adapter already installed:
an `installation.yml` that predates real canonical `protocol/` drift,
which the normal `update`/`install` path refuses outright rather than
offering any resolution path short of this kind of manual bypass).

Architecture's own Risks section anticipated only that "`forge adapter
update` will surface real `UPDATE`s beyond this Change's own diff" — a
milder failure mode than "refuses to run at all, for both Adapters, via
two independent internal guards, requiring a hand-authorized bypass of
production code." The Specification's Compatibility Statement asserts,
unqualified: "a `forge adapter update` after this Change's Implementation
will show `UPDATE` (not `CONFLICT`) for the affected generated paths,
resolving Discovery's live drift as an ordinary consequence of
republishing, not a special-cased patch." This Change's own dogfooded
experience directly contradicts "ordinary consequence" — it required an
extraordinary, one-time, human-authorized deviation from the ordinary
`forge adapter update` path — and no artifact revises that framing after
the fact.

**Impact:** Every other Forge-governed repository with this Adapter
already installed is, by DEC-004's own admission, in the same
"`installation.yml` never committed, real canonical drift accumulated
underneath it" position this repository was in. Per this finding, those
repositories' operators will hit the identical `forge adapter update`
refusal this Change's own Implementer hit, with no supported CLI path
out short of the same kind of hand-authorized guard bypass this Change
required — a materially more disruptive adoption story than "run `forge
adapter update`" implies, and currently undocumented anywhere a future
adopter would find it before hitting the wall themselves.

**Suggested Resolution (non-blocking on this Review to specify, per
C-025):** At minimum, revise the Specification's Compatibility Statement
and/or add a Documentation Impact item recording this remediation path
honestly for future adopters (a `forge adapter update --acknowledge-
stale-baseline`-shaped command, or a documented manual procedure); at
maximum, treat it as a Material Unresolved Decision for a follow-up
Change, since it affects every existing adopter of this Adapter, not only
this repository.

## R005 — MINOR — `traceability.yml`'s `acceptance` table has two related mapping errors

**Problem:** `traceability.yml`'s `acceptance` section maps:

```yaml
AC-001: [test_projection_renders_reviewer_resolver_independence_exactly_once_across_flows]
AC-002: []
```

AC-001 is FR-005's own acceptance criterion ("a reader can locate...
without searching multiple Flow-specific sections"). The test actually
listed under it is the FR-001/AC-004 test (independence-block-appears-
once), already separately and correctly listed under `AC-004`. FR-005
itself is recorded with `tests: []` in the `requirements` section
(consistent with Test Strategy's own declared Non-mechanical Validation
approach for "locatable sections" — TDD-008, verified by human reading,
not a mechanical test) — so AC-001 should likewise be empty, not
populated with an unrelated FR-001 test. Meanwhile AC-002 is FR-007's own
acceptance criterion (boundary-reporting format) and is left empty even
though a real, correctly-written test exists and is already linked under
`requirements.FR-007.tests`:
`test_workflow_template_instructs_boundary_reporting_format`.

**Impact:** Non-blocking — the underlying behavior for both FR-005 and
FR-007 is genuinely tested or genuinely (and legitimately) non-mechanical;
this is a bookkeeping-accuracy defect in the `acceptance` cross-reference
table specifically, not a missing-coverage defect. But `traceability.yml`
is this Change's own declared "authoritative FR↔Task↔Test↔Evidence
mapping" (Specification, Traceability Matrix section), so an incorrect
entry undermines exactly the auditability this Change's FR-002/NFR-001
machinery is designed to protect elsewhere.

**Suggested Resolution:** Move the independence test reference from
`AC-001` to (it already correctly lives under) `AC-004` only; populate
`AC-002` with `test_workflow_template_instructs_boundary_reporting_format`.

## Checked and found sound (no defect)

- **FR-001, reproduced against the actual installed `SKILL.md`, not
  synthetic fixtures.** `grep -c "### Reviewer/Resolver independence"
  .claude/skills/forge/SKILL.md` → exactly `1`. All three Flow sections
  (`fast`, `full`, `standard`) each carry the line `Strict Review for this
  Flow is subject to the single "Reviewer/Resolver independence" section
  below; it is not restated per Flow.` — confirmed by direct read of
  `SKILL.md` lines 123-176, not accepted from `tdd-evidence.yml`'s claim.
- **FR-002, reproduced by reading the actual source, not trusting the
  import statement's existence alone.**
  `src/forge_cli/adapters/review_independence.py` genuinely exists, is
  genuinely harness-agnostic (no Claude-Code/Codex-specific logic), and
  both `src/forge_cli/adapters/claude_code/projection.py` and
  `src/forge_cli/adapters/codex/projection.py` genuinely
  `from forge_cli.adapters.review_independence import
  REVIEWER_RESOLVER_INDEPENDENCE_LINES, REVIEWER_RESOLVER_INDEPENDENCE_
  POINTER` — confirmed by direct `grep -n` on both files; neither
  redefines its own local copy of the constant (the pre-Change generator
  did, confirmed via `git diff 3aa1955..23d763b`).
- **FR-006, reproduced with real subprocess payloads, not read from
  source and assumed to work.** Piped nine hand-constructed JSON
  `PreToolUse` payloads directly into the actual generated
  `.claude/skills/forge/hooks/check-manifest-edit.sh` via `sh`: `Edit`
  and `Write` against each of `manifest.yml`/`provenance.yml`/
  `review.md` (including an absolute-path-prefixed variant and a
  multi-level relative-path-prefixed variant) all correctly `deny`; an
  `Edit` against an unrelated source file and a `Write` against
  `intent.md` both correctly allow (no output); a `manifest.yml.bak`
  suffix and a `not-a-manifest.yml` substring case both correctly allow,
  confirming the match is exact-path, not naive substring; a
  `NotebookEdit` targeting `manifest.yml` correctly allows too — which is
  not a defect, since `SKILL.md`'s own disclosure explicitly and
  accurately names `NotebookEdit` as unguarded. The pre-existing `Bash`
  `sed -i`/`git add` cases (CHG-0018's own regression suite) still behave
  identically, confirmed by the same method.
- **Both Adapters' digests genuinely match what's on disk, not merely
  what `installation.yml` claims.** `sha256sum
  .claude/skills/forge/SKILL.md`,
  `.claude/skills/forge/hooks/check-manifest-edit.sh`, and
  `.agents/skills/forge/SKILL.md` all match their recorded digests in
  `.forge/adapters/claude-code/installation.yml` and
  `.forge/adapters/codex/installation.yml` exactly, byte for byte.
- **`forge validate`, `forge doctor`, `forge adapter plan claude-code`,
  `forge adapter plan codex`, all reproduced independently, all matching
  `verification.md`'s specific claims:** `forge validate` → "Forge
  project is valid"; `forge doctor` → all `PASS` except the two disclosed
  `WARN`s (`limitations`, `migration_available`) already present before
  this Change; `forge adapter plan` for both Adapters → all `UNCHANGED`,
  no `CONFLICT`, no error.
- **Provenance commits are real and contain what they claim.**
  `381dfc621196c65c44b0636a8e2e9ff83b3ffb0d` (Plan approval) and
  `23d763b5b076bd1fd3df75743e9df90fcc4b0423` (Implementation subject) both
  resolve via `git cat-file -t` to real commits on this branch; `git log
  --format='%H %ad %s' 381dfc6..23d763b --reverse` confirms the Plan-
  approval commit genuinely precedes every code-touching commit (`68dd5fa`,
  `c206237`), so the Plan/Implementation boundary (C-077) was not crossed
  before the recorded human approval.
- **Self-Hosting Boundary genuinely honored, not merely asserted.** No
  evidence this Change's own Plan Decision, Gate evaluation, or Review
  requirement was evaluated against a `SKILL.md` shape this Change itself
  produced — the Plan-approval commit predates every code change, and
  this Review itself was conducted using the repository's real, current
  `forge` skill instructions (which already state the reused self-hosting
  sentence verbatim), not a hypothetical post-Change one.
- **FR-006's disclosure text is honest and matches actual coverage,
  including its stated gaps.** `SKILL.md`'s "Illustrative enforcement
  hook" section explicitly names what it does cover (`Bash`, `Edit`,
  `Write`, three exact paths) and what it does not (MCP filesystem tools,
  `NotebookEdit`, unverified subagent coverage) — verified against actual
  probe behavior above; no overclaim found.
- **NFR-003 (`SKILL.md` does not grow), reproduced exactly.** `wc -l
  .claude/skills/forge/SKILL.md` → `175`, matching `verification.md`'s
  claimed 175 exactly — smaller than the claimed 180-line pre-Change
  baseline.
- **Documentation Impact deferral to post-Review stages is legitimate,
  not a silent skip.** `protocol/flows/full.yml` places `documentation`
  and `knowledge_capture` stages after `strict_review`, and only the
  `before_completion` gate requires them — `manifest.yml`'s
  `state.current: strict_review` with `documentation: pending`/
  `knowledge_capture: pending` is the Flow working as designed, not an
  omission (see R003 for the narrower, real defect this uncovered instead
  — `tasks.md`'s own overclaiming about this same deferred work).
- **No scope creep.** `git diff --stat 3aa1955..23d763b -- src/forge_cli/
  adapters/` touches exactly the five files Architecture/Plan named in
  advance (`claude_code/projection.py`, `claude_code/resources/skills/
  workflow.md`, `codex/projection.py`, `codex/resources/skills/
  workflow.md`, the new `review_independence.py`); no shared,
  harness-agnostic module outside `adapters/` was touched, and no
  Contract/Flow/Decision-Rules canonical source file
  (`protocol/contract/engineering.md`, `protocol/flows/*.yml`,
  `src/forge_cli/validation/__init__.py`) was touched, matching CON-001/
  CON-002's compatibility claims.

## Conclusion

The generator-level work this Change sets out to do is real, correctly
scoped, and independently verified against the actual repository state,
not merely against this Change's own narrative — FR-001, FR-002, and
FR-006 in particular hold up under direct, adversarial, hands-on probing
that went beyond the cases `tdd-evidence.yml` itself names. But the
Change's own evidence trail contains a specific, quantified, false claim
("701 passed, 0 failed") in both `verification.md` and `provenance.yml`,
caused by a genuine, reproducible schema violation in this Change's own
`traceability.yml` — a BLOCKER by construction, since Strict Review cannot
accept a Change's self-reported test evidence that does not match the
frozen subject's actual, reproducible behavior. Three further MAJOR
findings — an undocumented human-authority Decision (R002), false
task-completion claims about a document that was never written (R003),
and an unaddressed remediation gap in the Adapter drift-detection
mechanism this Change asks every future agent to trust (R004) — compound
the evidence-integrity concern rather than standing alone. This Change is
**REQUEST CHANGES**; it may proceed to a Resolution and re-Review once
R001-R004 are addressed and R005 is, at the Resolver's discretion, cleaned
up alongside them.

## Iteration 2 — REQUEST CHANGES (`kind: resolution_verification`)

### Iteration 2 scope and authority

This Iteration is a **Resolution Verification**, not a second Initial
Review. Per `protocol/contract/engineering.md` C-047 and
`protocol/versions/2/specification.md` §10, its authority is bounded to
exactly three things:

1. R001-R005, the five Findings `resolution-001` targets;
2. defects within `resolution-001`'s own Resolution Delta;
3. Out-of-Scope Mutation.

It is deliberately **not** a re-audit of `implementation-subject-001`.
Nothing in Iteration 1's "Checked and found sound" section — FR-001,
FR-002, FR-006's hook behavior, both Adapters' digests, `forge validate`/
`doctor`/`adapter plan`, the provenance commit chain, the Self-Hosting
Boundary, and everything else Iteration 1 already examined and found
sound — was re-litigated here. Re-opening any of that is precisely what
C-047 forbids.

### Iteration 2 execution independence

Executed in `claude-code-review-0045-independent` /
`claude-code-review-session-2026-08-24` (this Review's own established
identity, distinct from `resolution-001`'s
`claude-code-implementation-0045` / `claude-code-session-2026-08-24`), a
continuation of the same independent Reviewer identity that produced
`review-001` — not a new, unrelated identity, but still an Execution and
Execution Context distinct from the Implementation/Resolution session
that produced `resolution-001`, satisfying C-026's actual requirement
(independence from the *subject*, not a fresh identity per Iteration). No
claim in `resolution-001`'s own `provenance.yml` statement, `tasks.md`
T-016/T-020, `specification-drift.md`, or `verification.md`'s addendum was
accepted without independent reproduction against the actual repository
state at the new frozen subject. See `provenance.yml` record `review-002`
for this execution's own self-recorded provenance.

Subject: `resolution-001`, frozen at
`b43cb761d08433ae8a0b7dbc3be82d1e57f09221` (revision
`chg-0045-resolution-001`). `HEAD` at the time of this Iteration is
`4fa5635` (this Review's own Iteration 1 `manifest.yml`/`provenance.yml`/
`review.md` commit), whose only difference from the subject is exactly
those three Change-local review-control paths — confirmed directly via
`git diff --stat b43cb76..HEAD`, which shows only `manifest.yml`,
`provenance.yml`, `review.md`. `git status --porcelain=v1
--untracked-files=all` shows only the same three pre-existing, disclosed,
unrelated untracked files noted in Iteration 1 (`.claude/CLAUDE.md`,
`.playwright-mcp/`, `RELATORIO-SESSAO-2026-08-22.md`); otherwise clean.

### Resolution Delta, computed independently — no Out-of-Scope Mutation

Computed per §11 as the committed diff between the immutable revision of
the Iteration immediately preceding this one (`review-001`'s subject,
`23d763b5b076bd1fd3df75743e9df90fcc4b0423`) and this Iteration's own
subject (`b43cb761d08433ae8a0b7dbc3be82d1e57f09221`) — both already-frozen
historical commits, not the current workspace:

```
$ git diff --name-only 23d763b..b43cb76
.forge/changes/CHG-0045-.../provenance.yml
.forge/changes/CHG-0045-.../specification-drift.md
.forge/changes/CHG-0045-.../specification.md
.forge/changes/CHG-0045-.../tasks.md
.forge/changes/CHG-0045-.../traceability.yml
.forge/changes/CHG-0045-.../verification.md
```

`git log 1bb818b..b43cb76 --oneline` confirms this is a single commit
(`b43cb76`), not a squashed range hiding other changes. Subtracting the
one Change-local review-control path (`provenance.yml`) leaves exactly
five: `specification-drift.md` (new), `specification.md`, `tasks.md`,
`traceability.yml`, `verification.md` — every one of them inside this
Change's own `.forge/changes/CHG-0045-.../` directory; no `src/`, `tests/`,
`protocol/`, or other Change's directory appears anywhere in the diff.
This matches `resolution-001`'s own narrated scope exactly, in both
directions. **Out-of-Scope Mutation: none.** `full_review_required` is
`false` and this Iteration is eligible to be `status: passed`.

### R001, re-checked against actual repository state — resolved

Not accepted from `resolution-001`'s own claimed "701 passed, 0 failed."
Ran the full suite myself, twice — once via a fresh scratch venv
(`pip install -e ".[test]"`) and once via this repository's own committed,
pinned `.venv/bin/pytest` — against the working tree at this Iteration's
subject:

```
$ .venv/bin/pytest -q
701 passed, 2 warnings in 81.39s
```

Both runs agree: **701 passed, 0 failed**, matching `resolution-001`'s
claim exactly and, critically, no longer reproducing Iteration 1's
`test_canonical_yaml_instances_satisfy_their_declared_schemas` failure.
Confirmed the root-cause fix directly by reading `traceability.yml`
itself, not trusting the commit message: `requirements.CON-001.tasks`,
`CON-002.tasks`, and `CON-004.tasks` now each read `[T-002]` — non-empty,
satisfying `protocol/schemas/traceability.schema.json`'s `minItems: 1` —
rather than the `[]` Iteration 1 found. `verification.md` gained an
**Addendum** (not a silent rewrite of the original false claim) that
names the actual pre-fix state (700 passed, 1 failed at freeze time,
matching Iteration 1's own finding exactly), the root cause (suite not
re-run after `traceability.yml`'s last edit before freezing), and the fix
— the original "701 passed, 0 failed" sentence is left untouched above the
Addendum, which is the honest way to correct a record (compare to R003's
same pattern in `tasks.md`, below). R001 is resolved.

### R002, re-checked against actual repository state — resolved

Not accepted from `resolution-001`'s claim that "an explicit DEC-006
narrative" was added. Read `tasks.md` T-016 directly: it now contains a
dedicated paragraph, explicitly labeled **DEC-006**, that names the exact
event it refers to ("the explicit, in-session human authorization
described above — to bypass `AdapterService`'s own
`_reject_drift`/`_reject_conflicts` guards for this one-time republish...
is that Decision") and explicitly attributes the addition to this
Review's own R002 finding. A future reader no longer has to guess what
`manifest.yml`'s `DEC-006` entry refers to. R002 is resolved.

### R003, re-checked against actual repository state — resolved

Not accepted from `resolution-001`'s claim. Read `tasks.md` T-017/T-018
directly, side by side with `manifest.yml`'s `documentation`/
`knowledge_capture` fields (still, correctly, `pending`). T-017 now reads
"Documentation Impact scoping recorded for the post-Review
`documentation`/`knowledge_capture` stages... CHANGELOG.md entry and
`knowledge-capture.md` are deferred to those stages" — past-tense
completion language replaced with an accurate description of scoping, not
completion — and explicitly says so ("this task previously, incorrectly,
said Documentation Impact 'was evaluated' in the past tense; corrected").
T-018 now reads "`knowledge-capture.md` was **not** written at this
stage... Knowledge Capture is a post-Review stage... and is written after
Review" — again explicitly flagging its own prior overclaim as corrected
by R003. Neither task now contradicts `manifest.yml`'s own state. R003 is
resolved.

### R004, re-checked against actual repository state — resolved

Not accepted from `resolution-001`'s claim that `specification-drift.md`
is a "genuine Root Cause / Evidence / Final decision narrative." Read the
full file directly: it has all three sections, each with real, specific
content — Root Cause traces the original Compatibility Statement's
unqualified "ordinary consequence" claim to an untested assumption made
before Implementation attempted the republish; Evidence cites the actual
guard-refusal mechanism (`_reject_drift`/`_reject_conflicts`) and
attributes the finding to this Review's own Iteration 1; Final decision
explicitly declines to build a supported recovery command as an
undisclosed scope-creep fix, instead deferring it as named follow-up work.
This is not a stub — confirmed `specification-drift.md` is itself an
established artifact type in this repository (four prior precedents exist
under `.forge/changes/`: CHG-0008, CHG-0011, CHG-0012, CHG-0013), not
invented ad hoc for this Resolution.

Read `specification.md`'s Compatibility Statement directly: the original
"ordinary consequence" paragraph is left intact (not silently rewritten)
and followed by a clearly labeled **"Corrected by Specification Drift
after Strict Review Iteration 1 (R004)"** paragraph that states plainly
the republish "required a one-time, human-authorized bypass of that
production code," names the mechanism, and discloses that the same
refusal is latent in every other Forge-governed repository with this
Adapter installed under similarly stale conditions — matching, not
softening, R004's original finding. R004 is resolved.

### R005, re-checked against actual repository state — resolved

Not accepted from `resolution-001`'s claim. Read `traceability.yml`'s
`acceptance` table directly: `AC-001: []` (correctly empty now, matching
FR-005's own `tests: []` — the independence-block test that was
previously, incorrectly, listed here is no longer present) and
`AC-002: [test_workflow_template_instructs_boundary_reporting_format]`
(correctly populated, matching the same test already linked under
`requirements.FR-007.tests`). R005 is resolved.

### R007 — MAJOR — `resolution-001`'s own provenance record omits `scope`/`targets`, so `forge validate` cannot mechanically verify the Resolution Delta — genuinely reproduced, blocking

**Not one of R001-R005** (it is a defect in the Resolution's own
provenance record, not in any of the five files R001-R005 targeted), but
squarely **inside the Resolution Delta** — `provenance.yml`'s
`resolution-001` record was itself added by commit `b43cb76` (confirmed:
`provenance.yml` appears in `git diff --stat 23d763b..b43cb76`, 28
insertions) — so this is within this Iteration's own bounded C-047
authority (point 2: defects within the Resolution Delta) to discover and
record, not an unrestricted re-audit.

**Problem:** Once this Review's own `review-002` entry (`kind:
resolution_verification`) is added to `manifest.yml`'s bound Review
Iterations — which this Iteration is required to do — `forge validate`'s
`_validate_resolution_verification` check activates for the first time
for this Change (it only runs when a bound Iteration has
`kind: resolution_verification`) and requires the Resolution it verifies
(`resolution-001`) to declare non-empty `scope` and `targets` lists so the
tool can independently compute the Resolution Delta and check it for
Out-of-Scope Mutation itself, mechanically. Read `provenance.yml`'s
`resolution-001` record directly: it has a `statement` prose field
narrating scope ("Resolution Delta (git diff 23d763b..b43cb76): exactly
specification.md, specification-drift.md (new), tasks.md,
traceability.yml, verification.md") but no structured `scope:` or
`targets:` field at all. This repository's own established convention for
exactly this situation — `CHG-0018/provenance.yml`'s `resolution-001`
record — has both: `scope: [src/forge_cli/adapters/claude_code/
projection.py, tests/unit/test_claude_code_projection_bundle.py]` and
`targets: [R001]`. This Change's `resolution-001` record does not follow
that precedent.

**Evidence:** Ran `forge validate` against the actual working tree at this
Iteration's own state (with `review-002` recorded):

```
$ .venv/bin/forge validate
C-026 [.../manifest.yml] The Resolution referenced by a resolution_verification
Iteration must declare non-empty scope and targets before it can be
mechanically verified as scoped.
```

Reproduced deterministically, not a flake — the check is a pure structural
read of `provenance.yml`, no network, no time-dependence.

**Impact:** This is a real, mechanical `forge validate` failure at the
frozen Resolution subject, for a Change whose `before_completion` gate
requires exactly this kind of mechanical evidence, not narrative
assertion. It does not indicate an actual Out-of-Scope Mutation — I
independently confirmed, via direct `git diff --name-only 23d763b..b43cb76`
computation (not via this mechanical check), that the Resolution Delta
contains no Out-of-Scope Mutation — but `forge validate` cannot confirm
that itself without the missing fields, which defeats the purpose of
having a mechanical check at all. Blocking per `protocol/policies/
review.yml` (MAJOR).

**Suggested Resolution (non-blocking on this Review to specify, per
C-025):** Add `scope: [specification.md, specification-drift.md,
tasks.md, traceability.yml, verification.md]` and
`targets: [R001, R002, R003, R004, R005]` to `resolution-001`'s existing
`provenance.yml` record. Since `provenance.yml` is one of the three
review-control-metadata paths this repository's own C-026 freeze
exemption already covers, completing this record does not require a new
frozen Resolution revision or a new commit touching `b43cb76`'s own
content — only `provenance.yml` needs to gain the two fields, followed by
a further, narrowly-bounded Resolution Verification (Iteration 3)
confirming `forge validate` is then clean.

### R008 — OBSERVATION — unrelated, pre-existing Core `forge validate` latent bug: any untracked file anywhere in the repository trips the C-026 freeze check for a Change's last `pending`/`passed` bound Review Iteration, recorded per C-050

**Not targeted by `resolution-001`, not inside the Resolution Delta**
(this is a Core validation-logic gap in `src/forge_cli/validation/
__init__.py`, unrelated to any file `resolution-001` touched), **and not
counted toward this Iteration's own `new_material_findings`** (C-047
scopes this Iteration's authority to R001-R005, the Resolution Delta, and
Out-of-Scope Mutation; C-050 requires an unrelated Finding discovered
incidentally be recorded, not discarded, and not treated as license to
re-audit further — the same posture `CHG-0018/review.md`'s own R002 took
for a structurally similar Core gap). Recorded here because it is real,
demonstrated, and would otherwise go unrecorded.

**Problem:** `_reviewable_workspace_delta()`
(`src/forge_cli/validation/__init__.py:82-93`) computes "has anything
changed since this Review Iteration's frozen subject" as the union of
committed diff, staged diff, unstaged diff, **and every untracked file in
the repository** (`_untracked_paths()`, `git ls-files --others
--exclude-standard`), minus only this specific Change's own three
review-control-metadata paths. It does not scope untracked files to
anything relevant to the Change being validated — a completely unrelated
stray file anywhere in the repository (a scratch note, a tool-generated
artifact, an editor swap file not covered by `.gitignore`) makes this
check see "the workspace changed," even though nothing reviewable for
*this* Change actually did.

**Evidence, reproduced independently, not inferred:** Isolated the
variable by temporarily moving this repository's three pre-existing,
disclosed, unrelated untracked files (`.claude/CLAUDE.md`,
`.playwright-mcp/`, `RELATORIO-SESSAO-2026-08-22.md`) out of the working
tree (to a scratchpad location, restored immediately afterward — confirmed
via `git status --porcelain` before and after) and re-ran `forge validate`:
with the untracked files present, `forge validate` reported **two**
errors, including "C-026 review subject changed after its immutable
revision freeze; create new subject provenance."; with them moved aside,
that specific error **disappeared** (only R007's `scope`/`targets` error
remained) — isolating the cause to the untracked files themselves, not to
anything this Resolution actually did.

**Impact:** Non-blocking to this Iteration and not a defect in this
Change's own Resolution. But it means `forge validate` can spuriously fail
for *any* Forge-governed Change, in *any* repository, whenever a `passed`
or `pending` last-bound Review Iteration exists alongside any untracked
file anywhere in the working tree — a materially broader blast radius than
"this Change's own reviewable material changed." Given R007 currently
keeps this Iteration's own last bound entry at `status: failed` (not in
`{"pending","passed"}`), this specific check does not currently fire for
CHG-0045's own manifest — but it will resurface the moment a future
Iteration legitimately reaches `passed` while these (or any other)
untracked files remain present.

**Suggested Resolution (non-blocking on this Review to specify, per
C-025; Core-level, not this Change's own scope to fix):** Scope
`_untracked_paths()`'s contribution to `_reviewable_workspace_delta()` to
paths that are plausibly reviewable for the Change in question (e.g.
under `src/`, `tests/`, `protocol/`, or the Change's own directory) rather
than the entire repository's untracked-file surface, or exempt genuinely
Change-unrelated untracked paths the same way `.gitignore`d paths are
already exempted per this repository's own stated Reviewer/Resolver
independence guidance ("Git-ignored cache/editor/temp files do not count
as reviewable workspace mutations for the freeze invariant" — this
untracked-but-not-ignored case is the same problem one step removed).

### R006 — OBSERVATION — new, non-blocking wording finding discovered inside the Resolution Delta itself, recorded per C-050

**Not targeted by `resolution-001`** (it postdates and is a byproduct of
the R001/R004 fixes), **but inside the Resolution Delta** (`verification.md`
and `specification-drift.md`, both Delta files), so within this
Iteration's own bounded authority to record, per C-047's second scope
item.

**Problem:** `verification.md`'s new R001 Addendum states "Durable lesson
recorded in `knowledge-capture.md`: re-run the full suite after the
*last* content edit before freezing..." in the present/past tense, as if
`knowledge-capture.md` already exists and already contains this lesson.
`specification-drift.md`'s Final decision section similarly states the
recovery-command follow-up work "is recorded as follow-up work in
`knowledge-capture.md`." I checked: `.forge/changes/CHG-0045-.../` contains
no `knowledge-capture.md` file — confirmed by directory listing, not
inferred. This is not wrong in substance (`knowledge-capture.md` is a
legitimate post-Review Flow stage per `protocol/flows/full.yml`, and
`manifest.yml`'s own `knowledge_capture: pending` is accurate and
consistent with T-017/T-018's now-corrected framing elsewhere in the same
Resolution), but the specific phrasing in these two sentences reads as
though the durable lesson and the follow-up-work record already exist,
when they are, accurately, still intended future work.

**Impact:** Non-blocking, and narrower than R003 (which this same
Resolution correctly fixed for the *task-checklist* claims about
`knowledge-capture.md`) — this is two sentences of forward-referencing
prose in files this Iteration is otherwise satisfied with, not a
checklist item falsely marked complete. Recorded so it is not silently
dropped, per C-050.

**Suggested Resolution (non-blocking on this Review to specify, per
C-025):** When `knowledge-capture.md` is actually authored in the
post-Review Documentation/Knowledge Capture stage, ensure it substantively
contains the "re-run after the last content edit" lesson and the
recovery-command follow-up item these two sentences promise; no change to
`verification.md`/`specification-drift.md` is required before Completion,
since both sentences are accurate statements of *intent*, not false
claims of present fact in the way R003's original checklist items were.

### New Findings introduced by the Resolution

Three new Findings: **R007 (MAJOR, blocking)** — `resolution-001`'s own
provenance record fails mechanical scope verification, a real defect
inside the Resolution Delta itself, not an Out-of-Scope Mutation and not
a regression in R001-R005's own fixes, but material enough to keep this
Iteration from `status: passed`. **R006 (OBSERVATION, non-blocking)** — a
wording precision issue inside the Resolution Delta. **R008 (OBSERVATION,
non-blocking)** — an unrelated, pre-existing Core `forge validate` latent
bug, recorded per C-050, not counted toward this Iteration's own
determination. `full_review_required: false` for all three: none is an
Out-of-Scope Mutation (C-047's specific trigger for mandatory
`full_review_required: true`), so a further narrowly-bounded Resolution
Verification (Iteration 3), not a new unrestricted Initial Review, is the
correct next step once R007 is fixed.

### Independent mechanical verification

Every figure below was produced by this execution, not read from
`resolution-001`'s own statement or any commit message.

- `.venv/bin/pytest -q` → **701 passed, 0 failed**, reproduced against the
  actual working tree at the Resolution subject (see R001 above).
- `forge validate`, run against this Iteration's own recorded state
  (`review-002` bound, `kind: resolution_verification`) → **fails** with
  the single error R007 documents (`resolution-001` lacks `scope`/
  `targets`) — reproduced deterministically; see R007 for the isolation
  experiment separating this from R008's unrelated untracked-file cause.
- `forge doctor` → every check `PASS` except the same two pre-existing,
  disclosed `WARN`s already present in Iteration 1 (`limitations`,
  `migration_available`) — unchanged by this Resolution, as expected,
  since it touches no Adapter-generation code.
- `git diff --name-only 23d763b..b43cb76` → exactly six paths, all inside
  this Change's own directory (see Resolution Delta above).
- `git status --porcelain=v1 --untracked-files=all` → clean except the
  same three pre-existing, disclosed, unrelated untracked files noted in
  Iteration 1 (see R008 for their specific, isolated role in a *different*,
  now-dormant `forge validate` error).

### Scope discipline (C-047 / C-050)

No unrelated latent Finding beyond R008 was discovered in this Iteration.
For the record of what was deliberately **not** re-examined: FR-001,
FR-002, FR-006's hook behavior (both digests, both Adapters), the
provenance commit chain, the Self-Hosting Boundary, and every other item
in Iteration 1's "Checked and found sound" section were left alone —
Iteration 1 examined them and found them sound; re-examining them here
would be the unrestricted re-audit C-047 forbids.

### Convergence accounting

`new_material_findings: 1` (R007 — the only new Finding that is a real,
material defect within the Resolution Delta; R006/R008 are non-blocking
OBSERVATIONs, not material in the sense this field tracks).
`full_review_required: false` — R007 is not an Out-of-Scope Mutation
(C-047's specific trigger for mandatory `full_review_required: true`); it
is a scoped, narrow metadata-completeness defect in `resolution-001`'s
own record, correctable without reopening R001-R005 or expanding beyond
this Iteration's own bounded authority.
`consecutive_unconverged_verifications` is `1` after this Iteration (the
first `resolution_verification` Iteration to end without a clean `passed`
status) — below any Convergence Limit concern, since this is the first
such non-convergence, not a repeated cycle on the same Finding.

### Verdict

**REQUEST CHANGES.**

R001 through R005 are all genuinely resolved in repository state,
re-verified directly against the actual frozen Resolution subject rather
than accepted from `resolution-001`'s own claim. The Resolution Delta
contains no Out-of-Scope Mutation — exactly the five declared files, all
inside this Change's own directory. The full test suite is independently
reproduced at 701 passed, 0 failed, closing the specific, quantified false
claim R001 identified. But `resolution-001`'s own provenance record omits
the `scope`/`targets` fields required for `forge validate` to mechanically
confirm what I have independently confirmed by hand (R007, MAJOR,
blocking) — a real, reproduced `forge validate` failure at this frozen
subject, not a hypothetical one. Two further, non-blocking OBSERVATIONs
were discovered inside or adjacent to the Resolution Delta and recorded
per C-050 rather than pursued further here (R006, a wording precision
issue; R008, an unrelated, pre-existing Core latent bug). This Change is
**REQUEST CHANGES**; it may proceed to a further, narrowly-bounded
Resolution (completing `resolution-001`'s own `scope`/`targets` fields —
review-control metadata, not a new code change) and a further Resolution
Verification (Iteration 3) once R007 is fixed.

## Iteration 3 — PASS (`kind: resolution_verification`)

### Iteration 3 scope and authority

Bounded per C-047 to R006 and R007 (the two Findings `resolution-001-scope`
and `resolution-002` target), defects within the Resolution Delta, and
Out-of-Scope Mutation — not a re-audit of `implementation-subject-001` or
of anything Iteration 1/2 already found sound. R008 is explicitly *not*
re-litigated as a defect (it was already recorded and dispositioned in
Iteration 2); this Iteration only verifies its previously-predicted
behavior empirically, which is evidence, not a new audit.

### Iteration 3 execution independence

Same independent Reviewer identity as Iterations 1 and 2
(`claude-code-review-0045-independent` / `claude-code-review-session-
2026-08-24`), distinct from the Resolution's `claude-code-implementation-
0045` / `claude-code-session-2026-08-24`. See `provenance.yml` record
`review-003`.

Subject: `resolution-002`, frozen at
`95b521ef5ccec4e1651518b91a9e9ce74f86bb5a`. `HEAD` at the time of this
Iteration is `a8ff30f` (this Review's own Iteration 2 `manifest.yml`/
`provenance.yml`/`review.md` commit), whose only difference from the
subject is exactly those three Change-local review-control paths —
confirmed via `git diff --stat 95b521e..a8ff30f`. `git status
--porcelain=v1 --untracked-files=all` shows the same three pre-existing,
disclosed, unrelated untracked files noted in Iterations 1-2; otherwise
clean.

### R007, re-checked against actual repository state — resolved, and legitimately, not as a disguised rewrite

Not accepted from the coordinator's own claim that `resolution-001` was
left untouched. Independently diffed `resolution-001`'s own record
between the commit that originally froze it (`96658cb`) and the current
working tree:

```
$ python3 -c "... compare resolution-001 record at 96658cb vs now ..."
resolution-001 unchanged: True
```

Confirmed structurally byte-for-byte identical (parsed-YAML equality, not
just textual — immune to inconsequential re-serialization). Separately
confirmed a genuinely new, additional record, `resolution-001-scope`,
exists (`provenance.yml`, distinct `id`), referencing the *same* logical
revision and commit R007 already reviewed
(`revision.id: chg-0045-resolution-001`,
`immutable_ref.value: b43cb761d08433ae8a0b7dbc3be82d1e57f09221` — identical
to what Iteration 2 reviewed), now carrying `scope:` (the same five files
Iteration 2 already independently confirmed as the Resolution Delta) and
`targets: [R001, R002, R003, R004, R005]`. `manifest.yml`'s `review-002`
Iteration's `subject_provenance` now reads `resolution-001-scope` instead
of `resolution-001` — read directly, confirmed, not inferred.

Independently confirmed the coordinator's claim that an in-place edit was
attempted first and correctly rejected: this is exactly the failure mode
C-026's "frozen subject authority cannot be rewritten" check exists to
catch (`src/forge_cli/validation/__init__.py` line 366: `if sa is not None
and sa!=sub: ... "C-026 immutable subject provenance differs from its
first committed record"`), and `tasks.md` T-021 independently corroborates
the same account. This is the legitimate, append-only pattern this
repository's own C-026 freeze discipline requires — not a disguised
rewrite. R007 is resolved.

Ran `forge validate` against the actual current repository state myself:

```
$ .venv/bin/forge validate
Forge project is valid
```

Confirmed independently, not accepted from the coordinator's claim.

### R006, re-checked against actual repository state — resolved

Not accepted from the coordinator's claim. Read `verification.md` and
`specification-drift.md` directly, diffed against their Iteration-2-time
content (`95b521e^..95b521e`, the single fix commit):
`verification.md`'s Addendum now reads "Durable lesson, **to be recorded
in the still-pending** `knowledge-capture.md` **at its own post-Review
Flow stage**" (was: "recorded in `knowledge-capture.md`", present tense);
`specification-drift.md`'s Final decision now reads "It **will be**
recorded as follow-up work in `knowledge-capture.md` **at that Artifact's
own post-Review Flow stage (not yet written as of this Specification
Drift)**" (was: "is recorded"). Both corrections are genuine — future
tense, explicit "not yet written"/"still-pending" framing — and neither
overclaims or underclaims: `knowledge-capture.md` still does not exist
(confirmed by directory listing, same check as Iteration 2), and both
sentences now say so accurately. R006 is resolved.

### Resolution Delta, computed independently — no Out-of-Scope Mutation

Computed the way Core's own `_resolution_delta()` actually computes it
(`src/forge_cli/validation/__init__.py`: the resolution commit's own
first-parent diff, `to_commit^..to_commit` — **not** the cumulative range
from the prior subject, per that function's own documented rationale:
"Using the full range from the prior subject would incorrectly include
unrelated Changes merged into the branch between the two frozen
subjects"):

```
$ git diff --stat 95b521ef5ccec4e1651518b91a9e9ce74f86bb5a^..95b521ef5ccec4e1651518b91a9e9ce74f86bb5a
 specification-drift.md | 10 +++--
 tasks.md                | 44 +++++++++++++++++-----
 verification.md         |  3 +-
```

Exactly the three files `resolution-002`'s own `scope:` declares. Read
`tasks.md`'s own diff in full (44 lines is more than R006's two-sentence
wording fix alone would suggest): confirmed it is legitimate T-020/T-021/
T-022 bookkeeping — recording Iteration 2's actual REQUEST CHANGES
verdict, the R007 metadata-fix method (including the coordinator's own
disclosed C-026 rejection on their first attempt), R006's fix, and the
Convergence Limit math for a possible future Iteration — not scope creep,
not silently smoothing over the REQUEST CHANGES history, and consistent
word-for-word with the coordinator's own account. **Out-of-Scope
Mutation: none.** `full_review_required` remains `false`.

### R008 — operational caveat, empirically confirmed, not a new Finding

R008 (the unrelated, pre-existing Core `forge validate` latent bug
recorded in Iteration 2) is not re-opened as a new material Finding here —
its cause and disposition (Core-level, unrelated to this Change's
content, Out of Scope to fix within CHG-0045) are unchanged from
Iteration 2. But its Iteration-2-predicted consequence — "it will
resurface the moment a future Iteration legitimately reaches `passed`...
while these (or any other) untracked files remain present" — is worth
confirming empirically rather than leaving as a prediction, since this
Iteration is exactly that moment. Tested directly, in a disposable sandbox
copy of `manifest.yml`/`provenance.yml` (restored immediately afterward,
confirmed via `git diff --stat` showing no residual change): appending a
`review-003` bound Iteration with `status: passed` to `manifest.yml`
(with the untracked files still present, unmodified) makes `forge
validate` fail again, reproducing the identical C-026 freeze-check error
Iteration 2 first found:

```
C-026 [.../manifest.yml] C-026 review subject changed after its immutable
revision freeze; create new subject provenance.
```

This confirms R008's predicted blast radius precisely: recording this
Iteration's own genuine PASS verdict as `status: passed` in `manifest.yml`
will make `forge validate` non-clean again, purely because of the three
pre-existing, disclosed, CHG-0045-unrelated untracked files
(`.claude/CLAUDE.md`, `.playwright-mcp/`, `RELATORIO-SESSAO-2026-08-22.md`)
still present in the working tree — not because of any defect in this
Resolution or this Change. This repository has an established precedent
for exactly this situation: `CHG-0018/review.md`'s own Iteration 2 (R002)
disclosed an unrelated, still-open `forge validate` failure and still
recorded a final **PASS** verdict, and that Change went on to reach
`state.current: complete` (confirmed by direct read of
`CHG-0018/manifest.yml`) without R002 ever being fixed. Following that
precedent: this does not change this Iteration's own PASS verdict, since
the defect is not in this Resolution — but it is a genuine, actionable
precondition for a mechanically clean `forge validate` at or before this
Change's own Completion, and the human maintainer should decide how to
handle it (remove/relocate/`.gitignore` the three untracked files, since
none of them are this Change's own scope to touch; or fix R008's
underlying Core gap; or accept the disclosed gap through Completion the
same way `CHG-0018` did) rather than have it silently rediscovered at
Completion time.

### New Findings introduced by the Resolution

None. R008's resurgence, confirmed above, is evidence about an
already-recorded Finding's already-predicted behavior, not a new defect
in `resolution-002` itself. `new_material_findings: 0`.

### Independent mechanical verification

Every figure below was produced by this execution, not read from the
coordinator's own account or any commit message.

- `.venv/bin/pytest -q` → **701 passed, 0 failed**, reproduced against the
  actual working tree at the `resolution-002` subject.
- `forge validate`, run against the actual current repository state
  (`review-002` still bound at `status: failed`, `review-003` not yet
  recorded) → **`Forge project is valid`**. Confirmed independently.
- `forge doctor` → every check `PASS` except the same two pre-existing,
  disclosed `WARN`s already present in Iterations 1-2 (`limitations`,
  `migration_available`).
- `git diff 95b521e^..95b521e --stat` → exactly the three declared
  `resolution-002` scope files (see Resolution Delta above).
- `resolution-001`'s own record confirmed byte-for-byte unchanged since
  its original freeze at `96658cb` (parsed-YAML equality check, not
  merely textual).
- Sandboxed reproduction of R008's predicted `passed`-status resurgence
  (see above), restored immediately, confirmed via `git diff --stat`
  showing zero residual change afterward.

### Scope discipline (C-047 / C-050)

No unrelated latent Finding beyond the already-recorded R008 was
discovered in this Iteration. FR-001/FR-002/FR-006's hook behavior, both
Adapters' digests, the Self-Hosting Boundary, R001-R005's own substance,
and everything else Iterations 1-2 already examined and found sound (or
already found and disposed of, for R006/R007) were left alone —
re-examining them here would be the unrestricted re-audit C-047 forbids.

### Convergence accounting

`new_material_findings: 0` for this Iteration. Iteration 2 had
`new_material_findings: 1` (R007); Iteration 3 has `0` — so the
Convergence Limit condition (`protocol/versions/2/specification.md`
§12-13: 2 *consecutive* `resolution_verification` Iterations with
`new_material_findings > 0`) is **not met**: only one Iteration in this
Review's history had a nonzero count, not two consecutive ones. No
`convergence_decision` is required. `consecutive_unconverged_verifications`
resets to `0` at this Iteration.

### Verdict

**PASS.**

R006 and R007 are both genuinely resolved, independently re-verified
against actual repository state rather than accepted from the
coordinator's own account: `resolution-001` is confirmed byte-for-byte
unchanged since its original freeze; `resolution-001-scope` is confirmed
to be a genuinely new, additional record referencing the identical
already-reviewed revision, not a disguised rewrite (and the coordinator's
account of a first, correctly-rejected in-place-edit attempt is
independently corroborated, not merely trusted); `forge validate` is
confirmed clean at the current repository state; the wording fix in
`verification.md`/`specification-drift.md` is confirmed genuine and
accurate. The single-commit Resolution Delta for `95b521e` contains no
Out-of-Scope Mutation. Zero new material findings; the Convergence Limit
is not reached. R008 remains open as a disclosed, non-blocking, Out-of-
Scope OBSERVATION, with its predicted consequence now empirically
confirmed rather than left theoretical — matching this repository's own
`CHG-0018` precedent for reaching a final PASS and Completion alongside a
disclosed, unrelated, still-open Core gap. This Change is **PASS** and may
proceed toward Completion (Documentation Impact, `knowledge-capture.md`,
and Completion itself remain the Flow's own next stages, per
`protocol/flows/full.yml`; the R008 operational caveat above is the human
maintainer's to resolve at or before that point, not a re-opening of this
Review's own verdict).

## Iteration 4 — Resolution Verification

### Iteration 4 scope and authority

Bounded per C-047 to `PR36-CODEX-001` (the single Finding `resolution-003`
targets — an external, independent GitHub Codex review-bot finding on this
repository's own PR #36, not a Finding raised by this Review), defects
within the Resolution Delta, and Out-of-Scope Mutation. Not a re-audit of
`implementation-subject-001` or of anything Iterations 1-3 already
examined and found sound. Performed cold, from repository state and the
governing prompt alone, with no access to any prior Implementation or
Resolution conversation.

### Iteration 4 execution independence

Distinct Execution/Execution Context from every prior record in
`provenance.yml`: `claude-code-review-0045-resolution-verification-004` /
`claude-code-review-session-2026-08-25b`, independent of `resolution-003`'s
`claude-code-implementation-0045` / `claude-code-session-2026-08-25`. See
`provenance.yml` record `review-004`.

Subject: `resolution-003`, frozen at
`b626080ef976f83c34e085d177cf1cfdd356faf0`. `HEAD` at the time of this
Iteration is `0b72e582b4f941d3a36433821e01458d70cc244f` (this Change's own
`resolution-003` provenance-recording commit), whose only difference from
the subject is exactly `provenance.yml` (Change-local review-control
metadata, exempt) — confirmed via `git diff --stat
b626080..0b72e58` showing exactly one file, 44 insertions, 0 deletions.
`git status --porcelain=v1 --untracked-files=all` at review time shows a
clean working tree, no untracked files at all (R008's Iteration 2/3
disclosed pre-existing untracked files are no longer present).

### PR36-CODEX-001, re-checked against actual repository state — real finding, genuinely and completely fixed

Read `src/forge_cli/adapter_cli.py`'s `doctor` command directly:

```
def doctor(adapter_id: Annotated[str, typer.Argument(metavar="ADAPTER")]) -> None:
```

`adapter_id` has no default and is declared `typer.Argument`, so `ADAPTER`
is genuinely a required positional argument — confirmed, not accepted from
the coordinator's own claim. The finding is real: an agent that read the
prior wording ("`forge adapter doctor`" named as a bare alternative to
`forge doctor`) and ran it literally would get Typer's missing-argument
error, not a diagnosis.

Read both `workflow.md` sources directly. Both now read (identical text,
line 13-14 in each):

```
decision, check the Adapter's own recorded drift state (`forge doctor` or
`forge adapter doctor <adapter-id>`, where `<adapter-id>` is the id shown
under this repository's own `.forge/adapters/` directory, e.g.
`claude-code` or `codex`) ...
```

This is a genuine, complete fix: it shows the required argument, and adds
an explanatory clause telling an agent where to find a concrete value
(`.forge/adapters/`), not just the bare placeholder syntax. `diff
src/forge_cli/adapters/claude_code/resources/skills/workflow.md
src/forge_cli/adapters/codex/resources/skills/workflow.md` → no output —
still byte-identical, preserving the invariant
`test_workflow_templates_project_identical_baseline_guidance` enforces.

Read both installed `SKILL.md` files directly
(`.claude/skills/forge/SKILL.md`, `.agents/skills/forge/SKILL.md`): both
carry the identical corrected line (`` `forge adapter doctor
<adapter-id>` ``) — not stale. Ran `forge adapter plan claude-code` and
`forge adapter plan codex` against the actual current repository state
myself: both report `UNCHANGED forge_owned .../SKILL.md` (and every other
generated path `UNCHANGED`) — the installed projections match their
recorded `installation.yml` digests exactly, confirmed independently by
`sha256sum` against each `installation.yml`'s own recorded `digest:`
value for `SKILL.md`
(`.claude/skills/forge/SKILL.md` → `010a9a57...93aac`, matches;
`.agents/skills/forge/SKILL.md` → `f3274a4e...057ce0`, matches). The
regeneration via `forge adapter update` was genuine, not merely claimed.

PR36-CODEX-001 is resolved.

### Resolution Delta, computed independently — exact match to declared scope, no Out-of-Scope Mutation

A naive `git diff 95b521e..b626080` would be wrong here: this branch was
merged with `main` (picking up CHG-0046's entire unrelated diff) between
Iteration 3's frozen subject and this Resolution. Computed the Resolution
Delta the way Core's own `_resolution_delta()` actually computes it
(`src/forge_cli/validation/__init__.py`, read directly — its own
docstring: "Using the full range from the prior subject would incorrectly
include unrelated Changes merged into the branch between the two frozen
subjects"): the frozen resolution commit's own first-parent diff,
`b626080^..b626080` (`b626080`'s only parent is `0416da1`, a linear commit,
not a merge, so first-parent diff and full diff coincide here):

```
$ git diff --stat b626080ef976f83c34e085d177cf1cfdd356faf0^ b626080ef976f83c34e085d177cf1cfdd356faf0
 .agents/skills/forge/SKILL.md                                       | 4 +++-
 .claude/skills/forge/SKILL.md                                       | 4 +++-
 .forge/adapters/claude-code/installation.yml                        | 2 +-
 .forge/adapters/codex/installation.yml                              | 2 +-
 src/forge_cli/adapters/claude_code/resources/skills/workflow.md     | 4 +++-
 src/forge_cli/adapters/codex/resources/skills/workflow.md           | 4 +++-
 tests/unit/test_claude_code_workflow_resource_authority.py          | 15 +++++++++++++++
 7 files changed, 29 insertions(+), 6 deletions(-)
```

Exactly the seven paths `resolution-003`'s own `scope:` declares — no more,
no fewer. **Out-of-Scope Mutation: none.** `full_review_required` remains
`false`.

### New Findings introduced by the Resolution

None discovered within the Resolution Delta or its immediate consequences.
`new_material_findings: 0`.

One non-blocking, C-050 latent observation outside the Resolution Delta,
recorded rather than discarded, per the task's own instruction to check for
it: `CHANGELOG.md` line 29 (pre-existing, part of this Change's original
Unreleased entry, not touched by `resolution-003`) reads "...a
digest-based drift record (`forge doctor`/`forge adapter doctor`) before
trusting..." — naming the bare command without the now-required argument.
This is prose describing a feature that was added, not literal
copy-paste command guidance an agent would execute (unlike `workflow.md`,
which is read and acted on directly by an operating agent) — read in
context it is not inaccurate, since it never claims the bare command is
runnable. `docs/adr/0018-agent-adapter-skill-authority-consolidation.md`
contains no reference to `forge adapter doctor`/`forge doctor` at all —
nothing stale there. `tasks.md`/`knowledge-capture.md` contain no entry
documenting `resolution-003`/PR36-CODEX-001 (`tasks.md` stops at T-025,
recorded before this fix); proportionate to record but not required to
block on, since `tasks.md`'s own checklist is Change-local bookkeeping
outside PR36-CODEX-001's targeted scope, not `workflow.md`'s own
technical accuracy. Recorded as **R009 — OBSERVATION** (non-blocking,
C-050, not targeted by this Resolution, not re-litigated further here).

### Independent mechanical verification

Every figure below was produced by this execution, not read from the
coordinator's own account or any commit message.

- `.venv/bin/pytest tests/unit/test_claude_code_workflow_resource_authority.py
  tests/unit/test_first_change_baseline_guidance.py -v` → **10 passed**,
  including the new
  `test_workflow_template_shows_the_required_adapter_id_argument_for_adapter_doctor`,
  which asserts `"forge adapter doctor <adapter-id>"` is present in the
  loaded template — a genuine, targeted regression test, not tautological.
- `.venv/bin/python -m pytest -q` → **721 passed** (up from Iteration 3's
  701, the difference explained by the intervening CHG-0046 merge
  bringing in its own additional tests, not by `resolution-003` itself —
  `resolution-003`'s own first-parent diff adds exactly one new test,
  `test_workflow_template_shows_the_required_adapter_id_argument_for_
  adapter_doctor`), reproduced against the actual working tree at the
  `resolution-003` subject.
- `.venv/bin/forge validate`, run against the actual current repository
  state → **`Forge project is valid`**. Confirmed independently.
- `.venv/bin/forge doctor` → every check `PASS` except the same two
  pre-existing, disclosed `WARN`s already present in Iterations 1-3
  (`limitations` for both Adapters) plus the pre-existing, unrelated
  `migration_available` `WARN` — no new `WARN`/`FAIL`.
- `.venv/bin/forge adapter plan claude-code` / `codex` → all paths
  `UNCHANGED`, confirmed independently against actual `sha256sum` digests.
- `diff` of both `workflow.md` sources → empty (byte-identical).
- `git diff b626080^..b626080` → exactly the seven declared scope paths
  (see Resolution Delta above).

### Scope discipline (C-047 / C-050)

No unrelated latent Finding beyond R009 (recorded, non-blocking, not
re-litigated as license for a broader re-audit per C-050) was discovered.
Everything Iterations 1-3 already examined and found sound, and everything
outside `resolution-003`'s own declared scope and PR36-CODEX-001's own
subject matter, was left alone — re-examining it here would be the
unrestricted re-audit C-047 forbids.

### Convergence accounting

`new_material_findings: 0` for this Iteration. No prior Iteration in this
Review's history immediately precedes this one with `new_material_findings
> 0` (Iteration 3 itself had `0`), so the Convergence Limit condition (2
*consecutive* `resolution_verification` Iterations with
`new_material_findings > 0`) is not met and was never at risk. No
`convergence_decision` is required.

### Verdict

**PASS.**

PR36-CODEX-001 is a real, external, independently-sourced finding (GitHub
Codex review bot, PR #36, P2) and is now genuinely and completely fixed:
`adapter_cli.py::doctor`'s `ADAPTER` argument is confirmed required by
direct source read; both `workflow.md` sources correctly show the required
argument with an explanatory clause and remain byte-identical to each
other; both installed `SKILL.md` files carry the identical fix, confirmed
both by direct content read and by independent `sha256sum`/`forge adapter
plan` digest verification against `installation.yml`; a genuine, targeted
regression test was added and passes. The Resolution Delta, computed the
way Core's own `_resolution_delta()` computes it (first-parent diff of the
frozen resolution commit, to avoid contaminating the delta with the
intervening CHG-0046 merge), is exactly the seven files `resolution-003`
declares — no more, no fewer, no Out-of-Scope Mutation. Full suite: 721
passed. `forge validate`/`forge doctor` clean, no new `WARN`/`FAIL`. One
non-blocking C-050 observation recorded (R009: a pre-existing `CHANGELOG.md`
mention of the bare command, prose rather than operational guidance, not
independently inaccurate) — not targeted by this Resolution, not blocking.
Zero new material findings; the Convergence Limit is not at risk. This
Change's Resolution Verification for PR36-CODEX-001 is **PASS** and may
proceed toward Completion of this specific Resolution cycle.
