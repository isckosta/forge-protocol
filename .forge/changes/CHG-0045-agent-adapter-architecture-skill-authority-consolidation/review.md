---
forge:
  artifact: review
  schema: 1
change: CHG-0045
status: failed
---
# Strict Review — CHG-0045

## Verdict

**REQUEST CHANGES (Iteration 1, `kind: initial_review`).** 1 BLOCKER, 3
MAJOR, 1 MINOR, 0 OBSERVATION. `protocol/policies/review.yml` sets
`blocking: [blocker, major]`; this Change may not proceed to Completion
until the BLOCKER and all three MAJOR findings are resolved and
re-reviewed.

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

| Severity | Count | Blocking |
| --- | --- | --- |
| BLOCKER | 1 | yes |
| MAJOR | 3 | yes |
| MINOR | 1 | no |
| OBSERVATION | 0 | no |

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
