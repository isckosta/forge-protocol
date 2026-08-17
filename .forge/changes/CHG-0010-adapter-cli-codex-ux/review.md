---
forge:
  artifact: review
  schema: 1
change: CHG-0010
status: pending
iteration: 4
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
