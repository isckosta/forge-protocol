---
forge:
  artifact: review
  schema: 1
change: CHG-0010
status: passed
iteration: 6
---

# Strict Review — Adapter CLI and Codex Installation UX

## Review method

An independent Reviewer — a fresh agent with no access to the Resolver's
implementation context, honoring C-026/`reviewer_resolver_separation` even
though Protocol 1 does not enforce execution-provenance independence — read
`specification.md`, `architecture.md`, `test-strategy.md`, `traceability.yml`,
`tdd-evidence.yml` (all 42 cycles at the time of review, with line-by-line
sampling of TDD-004G/H/I, TDD-009C, TDD-010), `verification.md`, `manifest.yml`,
and `plan.md` Task 9. It read the full production code for `publisher.py`,
`ownership.py`, `state.py`, `configuration.py`, `targets.py`, `driver.py`,
`service.py`, `adapter_cli.py`, and `projection.py`, plus the merge commit
`c5f0230` diff and the surrounding commit graph from `df0cb420` to `afd2016`.
It ran the full suite and `git diff --check`, and wrote two standalone
reproduction scripts to probe the TOCTOU class TDD-009C claims to have closed
against paths that fix does not touch. The Resolver verified each finding
directly against the cited code before remediating, and used regression-first
TDD for every behavioral fix.

## Iteration 1 — FAIL

**Revision reviewed:** `afd2016`.

One BLOCKER and one MAJOR finding, plus three non-blocking observations.

### BLOCKER — Installation-record path never re-validated before the final write

`publish_adapter_plan` (`src/forge_cli/adapters/publisher.py`) resolves
`installation_path` via `_safe_target` exactly once, before the entire
preflight/validation/mutation sequence runs, then reuses that same `Path`
object to read the prior record, write the new record
(`_write_installation_record_atomically`), and restore/remove it during
rollback. This is the identical TOCTOU class TDD-009C closed for every
generated-artifact operation, left open on the publisher's own bookkeeping
path: a directory component of `.forge/adapters/<id>` swapped for a symlink
after preflight redirects the installation record write outside the
repository root with no error raised. Neither of TDD-009C's two regression
tests exercised this path; both only targeted plan operations. The Reviewer
reproduced this with a standalone script confirming `publish_adapter_plan`
returns silently while writing a full, valid `installation.yml` into an
attacker-controlled directory.

### MAJOR — FR-023 violated: publisher failures misreported as internal errors

None of `AdapterPublicationError`'s subclasses (`AdapterPublicationConflictError`,
`UnsafeAdapterPathError`, `AdapterPublicationRollbackError`) defined a `.code`
class attribute, unlike every `AdapterServiceError` subclass in `service.py`.
`_handle_adapter_error` in `adapter_cli.py` falls through to
`E_FORGE_INTERNAL_ERROR` at exit `70` whenever `getattr(error, "code", None)`
is not a string, so every `publish_adapter_plan`-raised failure — including
the expected, well-understood collision-after-planning case — surfaced to CLI
users as an internal error instead of the stable `E_FORGE_*` code and exit `2`
FR-023 requires for domain/validation failures including "collision." No
existing test exercised a `publish_adapter_plan`-raised failure through the
CLI; the suite's only conflict-exit-code coverage was the plan-time
`plan.conflicts` path, a different code path entirely.

### Observations (non-blocking, acknowledged)

1. `CodexProjectionInput`/`generate_codex_projection_bundle` in `projection.py`
   are reachable only from tests and the wheel-probe helper, not from any
   production driver — the same "test-only reachability" pattern TDD-010 was
   created to eliminate for the Reviewer/Resolver content. Kept as an
   intentional compatibility shim for now; a future Change may prune it once
   nothing outside the test suite needs single-Flow projection.
2. TDD-010's production change (protocol_id threading) was written directly
   inside merge commit `c5f0230` rather than as a discrete post-merge commit,
   so its RED state (driver.py/service.py temporarily reverted in the working
   tree) is not independently recoverable from Git history — only
   `tdd-evidence.yml`'s narrative attests to it. The full-suite result and
   `git diff --check` are consistent with the claim, but this is weaker
   evidence than the discrete RED/GREEN commits used elsewhere. Accepted as a
   known gap in this Change's evidence trail; not remediated retroactively
   because doing so would require rewriting already-integrated merge history.
3. `configuration.py` uses a dir-fd-anchored, `O_NOFOLLOW`-based write path
   that structurally prevents symlink-following at every ancestor.
   `publisher.py` instead relies on repeated `_safe_target` re-validation
   immediately before each syscall, which narrows but does not eliminate the
   TOCTOU window, as the BLOCKER above demonstrated for the one path it had
   forgotten to re-validate at all. Adopting the stronger fd-anchored
   technique in `publisher.py` is a legitimate future hardening, out of scope
   for this remediation pass, which closes the concretely evidenced gap
   rather than replacing the publisher's whole filesystem-safety strategy.

### Resolution (regression-first TDD)

- **TDD-011** (BLOCKER): added
  `test_directory_symlink_swap_after_preflight_prevents_escaping_installation_record_write`,
  confirmed RED (`DID NOT RAISE`, installation record written outside root).
  Fix: `_rollback_publication` now takes `installation_relative` (a string)
  instead of a precomputed `Path` and resolves it via `_safe_target`
  immediately before restoring/removing it, inside the same per-target
  try/except that already reports rollback failures; the main function
  re-resolves `installation_path` immediately before
  `_write_installation_record_atomically` instead of reusing the value
  computed at the top of the function. Confirmed GREEN. Focused publisher
  regression: 23 passed.
- **TDD-012** (MAJOR): added
  `test_adapter_install_maps_publication_conflict_to_stable_conflict_exit_code`
  and `test_adapter_install_maps_unsafe_path_to_stable_exit_code`, confirmed
  RED (`70 == 2` assertion failures). Fix: `AdapterPublicationConflictError.code
  = "E_FORGE_ADAPTER_CONFLICT"` (reusing the code already used for
  `plan.conflicts` and `AdapterPlanConflictError`, since both represent the
  same collision concept at different detection points) and
  `UnsafeAdapterPathError.code = "E_FORGE_ADAPTER_UNSAFE_PATH"` (new stable
  code for the invalid-configuration/unsafe-path category). The base
  `AdapterPublicationError` and `AdapterPublicationRollbackError` intentionally
  remain without a `.code` override so should-never-happen internal-invariant
  and incomplete-rollback failures continue to surface loudly as
  `E_FORGE_INTERNAL_ERROR`, matching the proportional scope of what was
  evidenced. Confirmed GREEN.

Full suite after both fixes: `.venv/bin/python -m pytest -q` — 347 passed.
`git diff --check` clean.

## Final finding counts (Iteration 1)

- BLOCKER: 1 (resolved)
- MAJOR: 1 (resolved)
- MINOR: 0
- OBSERVATION: 3 (acknowledged, non-blocking)

Decision: FAIL. Re-review of the resolved revision is required before PASS
(`re_review.required_after_blocking_resolution`).

## Iteration 2 — FAIL

**Revision reviewed:** `1fcac5a`.

A second, independent fresh Reviewer (no access to the Iteration 1 Resolver's
implementation context beyond what is recorded in this file and
`tdd-evidence.yml`) verified both Iteration 1 remediations by hand-tracing the
exact diff and actively probing for a still-open variant, then continued the
full adversarial review across all 18 dimensions rather than only the two
prior findings, per `diff_only_review: false`.

### Verification of Iteration 1 remediations

- **BLOCKER (installation-record TOCTOU): confirmed genuinely closed** for
  the reported gap. The Reviewer hand-traced the fix's control flow against
  the existing regression test and separately probed whether the attack
  could instead land inside `_rollback_publication`'s own
  `_safe_target`-then-`_restore_bytes`/`unlink` gap, or the equivalent gap at
  every other `_safe_target`-then-syscall pair in the module. It confirmed
  such a window still exists, but classified it as a concrete instance of
  Iteration 1's already-accepted Observation #3 (repeated re-validation
  narrows but does not eliminate TOCTOU) rather than a new class of
  exposure — the original BLOCKER's window spanned the entire
  preflight/validation/mutation sequence and needed no timing precision to
  exploit; the residual window is a single Python statement. Not escalated.
- **MAJOR (FR-023 exit codes): fix was directionally correct but
  incomplete** — see new MAJOR below.

### MAJOR — FR-023 still violated for "stale state": most `AdapterPublicationError` raise sites remained uncoded

Iteration 1's fix added `.code` only to `AdapterPublicationConflictError` and
`UnsafeAdapterPathError`, the two exceptions it happened to reproduce. It left
every raise site in `_load_prior_installation_record` and
`_validate_prior_record_authorizes_plan` on the uncoded base
`AdapterPublicationError`, and `tdd-evidence.yml`'s own TDD-012 notes
mischaracterized all of them as "should-never-happen internal-invariant
failures." The Reviewer disproved that characterization for these two
functions specifically: unlike `_validate_record_matches_plan` (which checks
`next_record`, a value `AdapterService` constructs deterministically from the
same plan being published — a genuine internal invariant), `prior_record` is
independently re-read from disk by `_load_prior_installation_record` at
publish time, after `AdapterService._prepare()` already captured its own
snapshot. A plan built against one snapshot and a disk record that changed
before `publish_adapter_plan` re-validates it — via ordinary concurrent
`forge adapter update` usage, or external interference with
`installation.yml` — is exactly FR-023's listed "stale state" category, not
an internal bug. The Reviewer reproduced it directly: a plan whose
`expected_current_digest` no longer matched the on-disk prior record's
recorded digest raised the uncoded base class, mapping through the real
`_handle_adapter_error` to exit `70`/`E_FORGE_INTERNAL_ERROR` instead of exit
`2`. No existing test exercised this path.

### MINOR — `manifest.yml` `tdd.cycles` stale relative to `tdd-evidence.yml` (C-029)

Commit `1fcac5a` bumped `tdd-evidence.yml`'s `cycle_count` from 42 to 44 when
adding TDD-011/TDD-012 but left `manifest.yml`'s `tdd.cycles` at 42.

### Resolution (regression-first TDD)

- **TDD-013** (MAJOR): added
  `test_stale_prior_record_authorization_mismatch_uses_stable_stale_record_code`
  (publisher-level) and
  `test_adapter_update_maps_stale_record_to_stable_exit_code` (CLI-level).
  Confirmed RED for the publisher-level test (`AttributeError`: no such
  exception class yet). Fix: new
  `AdapterPublicationStaleRecordError(AdapterPublicationError)`,
  `code = "E_FORGE_ADAPTER_STALE_RECORD"`, replacing the base-class raise at
  every site in `_load_prior_installation_record` and
  `_validate_prior_record_authorizes_plan`. `_validate_record_matches_plan`
  deliberately remains uncoded — it is a true internal invariant, not
  on-disk staleness, per the analysis above. Confirmed GREEN.
- **MINOR**: `manifest.yml` `tdd.cycles` corrected to `45` (matching
  `tdd-evidence.yml`'s `cycle_count` after TDD-013).

Full suite after remediation: `.venv/bin/python -m pytest -q` — 349 passed.
`git diff --check` clean.

## Final finding counts (Iteration 2)

- BLOCKER: 0
- MAJOR: 1 (resolved)
- MINOR: 1 (resolved)
- OBSERVATION: 0 new (Iteration 1's three stand; the residual rollback-window
  instance noted above does not escalate Observation #3)

Decision: FAIL. Re-review of the resolved revision is required before PASS.

## Iteration 3 — FAIL

**Revision reviewed:** `fdf06a5`.

A third, independent fresh Reviewer verified Iteration 2's remediation and
continued the full adversarial review.

### Verification of Iteration 2 remediations

- **TDD-013 (MAJOR fix): confirmed complete.** The Reviewer re-read the full
  current `publisher.py` and found no remaining uncoded base-class raise
  inside `_load_prior_installation_record` or
  `_validate_prior_record_authorizes_plan`.
- **The `_validate_record_matches_plan` uncoded distinction: confirmed
  logically sound.** The Reviewer traced `installation_record`'s only
  construction site (`AdapterService._installation_record()`, called in the
  same statement as `prepared.result.plan` in both `install()` and
  `update()`, with zero disk I/O between plan and record construction) and
  could not construct a counterexample where a mismatch there reflects
  genuine external staleness rather than an internal bug in
  `_installation_record()` itself.
- **MINOR (manifest.yml): confirmed fixed** — `tdd.cycles` matched
  `tdd-evidence.yml`'s `cycle_count` (45) at the reviewed revision.

### MAJOR — no-op short-circuit performed a second, unsafe, uncoded raw read three lines after TDD-013's fix stops

`publish_adapter_plan`'s PRESERVE/UNCHANGED-only no-op short-circuit
(`src/forge_cli/adapters/publisher.py`, then line 469) called the raw
`state.load_installation_record` directly instead of reusing `prior_record`
— already loaded and validated three lines earlier by the very function
TDD-013 had just hardened. The raw call performs no symlink check and, on
parse/schema failure, raises the uncoded `InvalidAdapterInstallationRecordError`,
falling through to `E_FORGE_INTERNAL_ERROR`/exit `70` — exactly the FR-023
violation TDD-013 closed, one call away. Unlike the earlier findings, this is
not only a race edge case: `AdapterService.update()` reaches this exact
branch on every ordinary "version bump, content unchanged" reinstall, a
routine path.

### MINOR — `AdapterService._effective_flows` raised the uncoded base `AdapterServiceError` for duplicate enabled canonical Flow configuration

Same FR-023 uncoded-exception pattern found twice already in
`publisher.py` (`src/forge_cli/adapters/service.py`, `_effective_flows`),
this time reachable only through a hand-edited/misconfigured project with two
enabled `.forge/flows/*.yml` files resolving to the same canonical Flow id —
narrower reachability than the MAJOR findings, so classified MINOR rather
than MAJOR/BLOCKER.

No BLOCKER-class finding: no write escapes the repository root in either new
finding; the bypassed symlink check was on a read, and the comparison result
is discarded on mismatch.

### Resolution (regression-first TDD)

- **TDD-014** (MAJOR): added
  `test_no_op_short_circuit_reuses_the_already_loaded_prior_record_instead_of_a_second_raw_read`,
  confirmed RED (`InvalidAdapterInstallationRecordError` from re-parsing a
  corrupted on-disk record the first safe read had already seen before
  corruption). Fix: the no-op check now compares `prior_record ==
  installation_record` instead of re-reading
  `load_installation_record(installation_path)` — a one-line change that
  removes the redundant I/O, the redundant TOCTOU window, and the coding gap
  together. Confirmed GREEN.
- **TDD-015** (MINOR): added
  `test_plan_rejects_duplicate_enabled_canonical_flow_with_stable_code`,
  confirmed RED (`ImportError`, no such exception class yet). Fix: new
  `AdapterFlowConfigurationError(AdapterServiceError)`,
  `code = "E_FORGE_ADAPTER_FLOW_CONFIGURATION"`, replacing the base-class
  raise in `_effective_flows`. Confirmed GREEN.

Full suite after remediation: `.venv/bin/python -m pytest -q` — 351 passed.
`git diff --check` clean.

## Final finding counts (Iteration 3)

- BLOCKER: 0
- MAJOR: 1 (resolved)
- MINOR: 1 (resolved)
- OBSERVATION: 0 new

Decision: FAIL. Re-review of the resolved revision is required before PASS.

## Iteration 4 — FAIL

**Revision reviewed:** `23559dc`.

A fourth independent Reviewer verified Iteration 3's remediation, then, given
three consecutive iterations finding progressively subtler instances of the
same general defect class in `publisher.py`, read the entirety of
`publish_adapter_plan` and every helper it calls line by line before
continuing the broader adversarial review.

### Verification of Iteration 3 remediations

- **TDD-014 (MAJOR fix): correct as far as it went, but exposed a deeper
  problem.** The one-line change (`prior_record == installation_record`) does
  eliminate the redundant raw read reported in Iteration 3. The Reviewer
  confirmed `prior_record`'s possible `None` value compares safely and
  falls through to the full mutation path, not a bug. But tracing where
  `prior_record` itself comes from — `_load_prior_installation_record(installation_path)`
  — surfaced that `installation_path` was still the single Path object
  resolved once at the top of the function, before the entire preflight loop
  and `_validate_record_matches_plan`, exactly the BLOCKER class Iteration 1
  described, on the one remaining use TDD-011 never touched (TDD-011 only
  re-resolved the write and rollback paths, not this read).
- **TDD-015 (MINOR fix): confirmed correct** —
  `AdapterFlowConfigurationError`/`E_FORGE_ADAPTER_FLOW_CONFIGURATION` maps
  to exit 2 as expected.

### BLOCKER — Prior-record read authorizing publication used a Path resolved before the entire preflight/validation window, letting a forged record overwrite a real repository file

`_load_prior_installation_record` only checks whether the `installation.yml`
leaf itself is a symlink; it does not walk ancestor components the way
`_safe_target` does. Reusing the once-resolved `installation_path` for this
read meant a directory swapped for a symlink during preflight/validation
(before the read) let an attacker-forged `installation.yml` be read as the
prior record, which `_validate_prior_record_authorizes_plan` then trusted to
authorize a plan operation against a real repository file. Because the
per-operation mutation targets are resolved fresh and safely (TDD-009C) and
the final install-record write/rollback are also already re-resolved
(TDD-011), a two-phase attack — swap before the read, restore the real
directory before the final write — let `publish_adapter_plan` complete
without raising anything at all, permanently overwriting a real file with
attacker-controlled content and recording the mutation as legitimate. The
Reviewer reproduced this directly: a real `generated.md` containing
"old-user-content", no genuine prior installation record, and a forged
`installation.yml` reachable only during the swap window resulted in
`generated.md` containing "attacker-new-content" with `publish_adapter_plan`
returning normally. None of the three existing symlink-swap regression tests
(TDD-009C, TDD-011) planted a forged record at the swap destination or
restored the real directory before the final write, so none exercised this
path.

### Resolution (regression-first TDD)

- **TDD-016** (BLOCKER): added
  `test_installation_state_directory_symlink_swap_before_first_read_cannot_forge_authorization`,
  confirmed RED (`DID NOT RAISE`, real file overwritten with attacker
  content). Fix: moved `installation_path = _safe_target(root,
  installation_relative)` from before the preflight loop to immediately
  before `_load_prior_installation_record`, its first actual use — closing
  the preflight-loop-sized window down to the same single-statement residual
  window already accepted as Observation #3. All four uses of the
  installation-record path (authorization read, write, rollback, and the
  no-op comparison that reuses the same read) are now fed by a resolution
  that happens immediately before or adjacent to their point of use.
  Confirmed GREEN.

Full suite after remediation: `.venv/bin/python -m pytest -q` — 352 passed.
`git diff --check` clean.

## Final finding counts (Iteration 4)

- BLOCKER: 1 (resolved)
- MAJOR: 0
- MINOR: 0
- OBSERVATION: 0 new

Decision: FAIL. Re-review of the resolved revision is required before PASS
(`re_review.required_after_blocking_resolution`).

## Iteration 5 — FAIL

**Revision reviewed:** `9ff7a76`.

A fifth independent Reviewer verified TDD-016 and actively tried to break it
with variants, then re-read the entirety of `publish_adapter_plan` and every
helper it calls line by line, given four consecutive iterations finding
progressively subtler instances of the same defect class in the same
function.

### Verification of Iteration 4 remediation

**Not fully closed.** The specific authorization-read vector TDD-016 targeted
resists variants (the Reviewer actively tried swapping in the residual
single-statement window and confirmed the fresh `_safe_target` call still
catches it). But TDD-016's own completeness claim — "all four uses... now fed
by a resolution immediately before or adjacent to their point of use" — was
inaccurate: it missed a fifth use (the rollback backup capture,
`prior_installation`/`installation_existed`), which still reused the Path
from the fix's own resolution across a window spanning the entire
authorization check, not a single statement.

### BLOCKER-1 — Rollback backup capture reused the authorization-read's Path across the whole authorization-check window, letting a forged record be written to the real installation.yml during rollback

`prior_installation = installation_path.read_bytes()...` and
`installation_existed = installation_path.exists()` (immediately after
`_validate_prior_record_authorizes_plan`) reused the same `installation_path`
TDD-016 resolved for the authorization read, without re-resolving. A
directory swapped for a symlink to a directory containing a forged
`installation.yml` *after* the (legitimate) authorization check passed but
*before* this capture poisoned `prior_installation`/`installation_existed`
with forged content. If the attacker then restores the real directory before
a later failure triggers rollback, `_rollback_publication`'s own (already
correctly re-resolving) restore step writes that forged backup to the real
path — with no error. The Reviewer reproduced this directly: a fresh
install with no genuine prior record ended up, after a triggered rollback,
with a forged `installation.yml` at the real `.forge/adapters/<id>/`
location.

### BLOCKER-2 — `_rollback_publication` never re-resolved the `Path` objects captured in `applied` at mutation time, unlike every other installation-path use in the same function

For a multi-operation plan, the first-processed operation's target `Path`
(captured in `applied` at mutation time) was reused unmodified at rollback
time, however much later that occurs relative to a subsequent operation's
failure. A directory swapped for a symlink between the first operation's
mutation and the second operation's failure let `_restore_bytes` write the
first operation's original (potentially sensitive) content into an
attacker-controlled directory — exfiltrating it — while the real,
already-mutated file was left un-rolled-back, with no rollback failure
reported at all: a silent, false appearance of a clean rollback. The Reviewer
reproduced this directly with a two-operation plan and a swap timed between
the first operation's successful mutation and the second's precondition
failure.

No new MINOR or OBSERVATION findings this iteration; the Reviewer's sampling
of CLI error mapping, dependency direction, and untracked-content checks
found nothing new.

### Resolution (regression-first TDD)

- **TDD-017** (BLOCKER-1): added
  `test_rollback_backup_capture_cannot_be_poisoned_by_a_directory_swap_after_authorization`,
  confirmed RED (forged `installation.yml` present at the real path after a
  triggered rollback). Fix: `_load_prior_installation_record` now returns
  `(record, raw_bytes)`, reading the file's raw bytes as part of the same
  safe read used to parse and validate it, instead of the caller separately
  re-reading `installation_path.read_bytes()`/`.exists()` later.
  `installation_existed` is now derived as `prior_record is not None`,
  exactly equivalent to the removed separate existence check. Confirmed
  GREEN.
- **TDD-018** (BLOCKER-2): added
  `test_rollback_of_an_already_applied_operation_reuses_a_stale_target_path`,
  confirmed RED (secret original content written to the attacker-controlled
  directory; the real file left with its new, un-rolled-back content; no
  rollback failure reported — `AdapterPublicationConflictError` instead of
  the expected `AdapterPublicationRollbackError`). Fix: `applied` now stores
  `(operation.path, original_bytes)` tuples instead of `(Path,
  original_bytes)`; `_rollback_publication` re-resolves each via
  `_safe_target(root, relative_path)` immediately before `_restore_bytes`.
  A still-swapped ancestor at rollback time now correctly raises
  `UnsafeAdapterPathError`, recorded as an `AdapterRollbackFailure`,
  surfacing as `AdapterPublicationRollbackError` — a loud, honest failure
  instead of silent exfiltration with a false appearance of success.
  Confirmed GREEN.

Full suite after remediation: `.venv/bin/python -m pytest -q` — 354 passed.
`git diff --check` clean.

## Final finding counts (Iteration 5)

- BLOCKER: 2 (resolved)
- MAJOR: 0
- MINOR: 0
- OBSERVATION: 0 new

Decision: FAIL. Re-review of the resolved revision is required before PASS
(`re_review.required_after_blocking_resolution`).

## Pre-Iteration 6 note — Resolution scope (TDD-019)

Before requesting Iteration 6, self-review found two remaining call sites of
the same defect class Iterations 1–5 progressively closed (a decision-
authorizing read and a later rollback-backup read of the same on-disk
content performed as two separate physical reads, letting a concurrent
writer desynchronize the two): `_load_prior_installation_record`'s own
prior-record parse, and the update/delete mutation-loop precondition
recheck. TDD-019 (`tdd-evidence.yml`) closes both with a single-read-derives-
both pattern, per CHG-0011's Resolution Scope discipline — applied here by
convention, not mechanism, since CHG-0010 is `forge/change@1` and predates
Protocol 2's provenance ledger:

- **Declared scope:** `src/forge_cli/adapters/state.py` (`parse_
  installation_record`/`load_installation_record` split),
  `src/forge_cli/adapters/publisher.py` (`_current_digest_and_bytes` plus
  the two call sites replacing `_current_digest`+`read_bytes()`),
  `tests/integration/test_adapter_publisher.py` (two new regression tests).
- **Declared targets:** the two remaining double-read call sites named
  above — not a re-opening of any other part of the module.
- **Note to the Iteration 6 Reviewer:** this is the sixth consecutive
  iteration finding an instance of the same underlying defect class in this
  file. Iteration 1's Observation #3 already named the structural
  alternative (`configuration.py`'s fd-anchored, `O_NOFOLLOW`-based write
  path, which prevents this whole class by construction rather than by
  re-validating before each use) as legitimate future hardening explicitly
  deferred as out of scope for each individual remediation pass. The
  engineer was presented this choice again after TDD-019 and chose to
  proceed with a scoped Iteration 6 rather than pause for the structural
  rewrite; if Iteration 6 finds yet another instance of this same class,
  that recommendation should be escalated explicitly rather than absorbed
  into a seventh scoped pass.

## Iteration 6 — PASS

**Revision reviewed:** `2b25ae0`.

A sixth independent Reviewer — fresh, no access to the Resolver's
self-review context beyond this file and `tdd-evidence.yml` — applied the
Resolution Verification discipline named in the Pre-Iteration 6 note *by
convention* (CHG-0010 is `forge/change@1` and predates CHG-0011's mechanical
enforcement): scope bounded to (a) whether TDD-019 actually closes its two
named call sites, (b) whether TDD-019's own delta introduces a new defect,
(c) whether its Git delta stayed within the declared scope, and (d) whether
the fix is genuinely complete for the six-iteration defect class or a
seventh instance can be found. Method: read `review.md` Iterations 1-5 and
the Pre-Iteration 6 note in full; read `git show 2b25ae0` in full (the
complete diff, all six files); read the TDD-019 entry in
`tdd-evidence.yml` including its RED reason and notes; re-read the entirety
of the current `src/forge_cli/adapters/publisher.py` and
`src/forge_cli/adapters/state.py` line by line, specifically hunting for any
other place that reads or checks a path's content more than once for
related decision/backup purposes; cross-checked `src/forge_cli/adapters/repository.py`
and `configuration.py`'s read sites to confirm none of them pair a
decision-read with a later same-content backup-read outside publisher.py's
own module boundary; ran `.venv/bin/python -m pytest -q` and
`.venv/bin/forge validate` directly.

### (a) Verification: TDD-019 closes both declared call sites

- **`_load_prior_installation_record`:** confirmed. It now performs exactly
  one `path.read_bytes()`, decodes it once, and passes the decoded text to
  the new pure-parsing `parse_installation_record(text)` -- which does no
  I/O of its own. The prior two-physical-read shape (`path.read_bytes()`
  followed by `load_installation_record(path)`'s own separate
  `path.read_text()`) is gone; there is no window between the record used
  for `_validate_prior_record_authorizes_plan` and the `raw` bytes used as
  the rollback backup for them to diverge.
- **Update/delete mutation-loop precondition recheck:** confirmed. Both
  branches (`publisher.py` lines ~517-533 for UPDATE, ~541-558 for DELETE)
  moved the digest comparison out of the short-circuiting `or` chain and
  into a single `current_digest, original = _current_digest_and_bytes(target)`
  call, checking the digest against `original` derived from the same
  `path.read_bytes()`. The prior shape (`_current_digest(target)` -- its own
  `path.read_text()` -- inside the `or` chain, then a separate
  `target.read_bytes()` two lines later) is gone for both branches.

### (b) New defect inside TDD-019's own delta

None found. Specifically checked, per the task's own prompt:

- **Error/encoding parity between `_current_digest` and
  `_current_digest_and_bytes`:** identical. Both catch
  `(OSError, UnicodeError)` and raise the same
  `AdapterPublicationConflictError` with the same message shape; the new
  function's `raw.decode("utf-8")` raises `UnicodeDecodeError`, a subclass
  of `UnicodeError`, caught the same way `_current_digest`'s
  `path.read_text(encoding="utf-8")` was.
- **`state.py`'s split (`parse_installation_record` / `load_installation_record`):**
  behaviorally equivalent to the pre-TDD-019 single function. The new
  `load_installation_record` catches `OSError` from its own
  `path.read_text()` and re-raises `InvalidAdapterInstallationRecordError`;
  `parse_installation_record` catches `(TypeError, KeyError, ValidationError,
  yaml.YAMLError)` from parsing -- together the same exception surface the
  old single function exposed, just split across the read boundary. Its one
  remaining caller (`repository.py`'s `_load_optional_record`, a single-read
  snapshot site, not a decision+backup pair) is unaffected.
- **`_current_digest_and_bytes` and the mutation loop's `or`-chain
  restructuring:** confirmed the digest check still runs *after* the
  existence/symlink guard (so a missing or symlinked target still raises
  before any read is attempted) and *before* `applied.append(...)` and the
  actual mutation, preserving the original ordering guarantees.
- **Test-file diff:** the modified
  `test_rollback_of_an_already_applied_operation_reuses_a_stale_target_path`
  correctly re-targets `_current_digest_and_bytes` (the new call site) and
  its updated comment accurately describes that only the mutation-loop
  recheck calls it now, not the preflight loop (which still calls the
  digest-only `_current_digest`). Confirmed correct by re-reading
  `_preflight_operation`.

### (c) Scope discipline

`git show 2b25ae0 --stat` touches six files:
`src/forge_cli/adapters/publisher.py`, `src/forge_cli/adapters/state.py`,
`tests/integration/test_adapter_publisher.py` -- the three declared in the
Pre-Iteration 6 note -- plus `.forge/changes/CHG-0010-adapter-cli-codex-ux/manifest.yml`,
`review.md`, and `tdd-evidence.yml`. The latter three are not a scope
violation: `manifest.yml`'s only change is `tdd.cycles: 50 -> 51` (the same
bookkeeping convention Iteration 2's MINOR established), `tdd-evidence.yml`
is the TDD-019 log entry itself, and `review.md`'s change is the
Pre-Iteration 6 note this Iteration was asked to read -- all three are
required companions to declaring and logging the resolution, not
independent production changes. No file outside the declared set was
touched.

### (d) Hunt for a seventh instance

Actively re-read `publish_adapter_plan` and every helper it calls,
specifically for any remaining place that reads a path's content more than
once for related decision/backup purposes. Found none:

- `_preflight_operation`'s three `_current_digest(target)` calls (UNCHANGED,
  DELETE_GENERATED, UPDATE) are advisory fail-fast checks only -- no backup
  is captured at preflight time, and per TDD-014/016/017's established
  pattern, the mutation loop always freshly and authoritatively re-resolves
  and re-reads immediately before mutating, never trusting the preflight
  result. This is not the same defect class: there is no "authorize once,
  reuse later" relationship between the preflight read and anything
  downstream.
- `repository.py`'s `_snapshot_artifact` (plan-build-time digest) and
  `_load_optional_record` are a different, already-reviewed boundary -- the
  plan/execute split every prior iteration examined, gated by the
  `expected_current_digest` conflict check publisher.py re-validates
  independently at publish time via its own fresh read. Not a same-content
  decision+backup pair.
- `_rollback_publication` re-resolves every path via `_safe_target`
  immediately before restoring (TDD-018) and uses only bytes already
  captured earlier (`applied`, `prior_installation`) -- no new read of
  current on-disk content occurs during rollback itself.
- `_validate_record_matches_plan`'s comparison inputs
  (`installation_record`) are constructed in-memory by the caller with zero
  disk I/O, confirmed sound in Iteration 3 and unchanged here.

No seventh instance of the defect class found.

### Test quality: TDD-019's two new regression tests

Both exercise genuine desynchronization, not trivial assertions:

- **`test_prior_record_read_is_not_desynchronized_by_a_concurrent_content_change`**
  monkeypatches `parse_installation_record` to rewrite the on-disk file with
  a forged record *and then* delegate to the real parser. Because the
  production code now derives the text passed to the parser from bytes
  already captured before this call, the returned `record` and `raw`
  reflect the pre-race legitimate content, not the forged rewrite -- the
  test asserts exactly that (`raw == legit_bytes`, record shows
  `legit.md`). Against the pre-TDD-019 two-read shape, the equivalent
  attack (rewrite between the caller's `read_bytes()` and
  `load_installation_record`'s own internal `read_text()`) would have
  desynchronized the two.
- **`test_update_precondition_digest_and_rollback_backup_come_from_the_same_read`**
  monkeypatches `_current_digest_and_bytes` to rewrite the target with
  attacker content immediately before delegating to the real combined read,
  then asserts `publish_adapter_plan` raises `AdapterPublicationConflictError`
  and the target is left with the attacker's rewritten content untouched
  (no partial mutation). This proves the digest comparison and the would-be
  rollback-backup bytes are always drawn from the identical physical read --
  a race can only ever produce a *consistent* (matching) or *safely
  rejected* (mismatched, aborted) outcome, never a decision authorized
  against one version of the content with a backup silently captured from
  another.

Both tests are confirmed RED before the fix (`tdd-evidence.yml`'s TDD-019
`red.reason`) and GREEN after.

### Observations (non-blocking, new this iteration)

1. **DELETE precondition recheck has no dedicated race regression test
   symmetric to UPDATE's.** `test_update_precondition_digest_and_rollback_backup_come_from_the_same_read`
   only exercises the UPDATE branch. The DELETE branch (`publisher.py` lines
   ~541-558) applies the structurally identical `_current_digest_and_bytes`
   fix and was verified correct by direct code reading, so this is a
   coverage-symmetry gap rather than an unverified defect -- not escalated.
2. **Pre-existing, out-of-scope encoding gap, unrelated to the TOCTOU
   class:** neither the old `load_installation_record` nor the new
   `_load_prior_installation_record`/`state.load_installation_record`
   catches a raw `UnicodeDecodeError` arising from invalid-UTF-8 bytes in
   `installation.yml` outside the `(OSError, TypeError, KeyError,
   ValidationError, yaml.YAMLError)` handler -- a mis-encoded on-disk record
   would surface as an uncaught internal error (the same FR-023
   "uncoded exception" pattern found and fixed for other raise sites in
   Iterations 1-3) rather than a stable `E_FORGE_*` exit. Confirmed this
   predates TDD-019 -- the identical gap existed in the pre-TDD-019
   `load_installation_record` -- so it is not a regression introduced by
   this commit and is not the TOCTOU defect class this Iteration is scoped
   to. Recorded for a future pass, not escalated here.

### Full suite and `forge validate`

`.venv/bin/python -m pytest -q` -- 356 passed, matching `tdd-evidence.yml`'s
claim. `.venv/bin/forge validate` reported exactly the two pre-existing,
out-of-scope findings already flagged for this Iteration (the CHG-0008
freeze/C-026 issue and CHG-0010's own `forge/change@1` vs. Protocol 2 schema
mismatch, also C-026) -- no new `forge validate` finding.

### Answer to the required question: is the sixth-iteration pattern actually closed?

**Closed for the currently-existing call sites, as far as this Reviewer's
exhaustive re-read of `publish_adapter_plan` and every helper it calls can
determine -- but I recommend the structural fd-anchored rewrite regardless,
not because I found a seventh instance, but because of what six iterations
of this exact search pattern demonstrates about the strategy itself.** Every
one of Iterations 1 through 6 found its instance by the same method: a
fresh Reviewer (or, this time, the Resolver in self-review) manually
enumerating every read/check site in one file and reasoning about pairwise
ordering. That method has a perfect record of finding one more instance
each time it has been tried, which is not evidence the class is now
exhausted -- it is evidence that manual enumeration in a file that repeats
the same "safe-target then syscall" shape at every mutation point is
inherently susceptible to missing one. `configuration.py`'s dir-fd-anchored,
`O_NOFOLLOW` write path (Iteration 1's Observation #3, still standing after
six iterations) eliminates this whole class *by construction* -- a swapped
ancestor cannot redirect an fd-relative operation regardless of timing --
so no future Reviewer needs to re-derive the same enumeration to check
whether this pass's fix was complete. This does not change the PASS verdict
below: TDD-019 correctly closes what it claims to close, introduces nothing
new, and stayed in scope. But given this is now the sixth consecutive
iteration of the identical class, I recommend the engineer treat the
structural rewrite as due, not merely available, before this file sees a
seventh.

## Final finding counts (Iteration 6)

- BLOCKER: 0
- MAJOR: 0
- MINOR: 0
- OBSERVATION: 2 new (non-blocking; Iteration 1's three stand unchanged,
  bringing the running total to 5)

Decision: **PASS.**
