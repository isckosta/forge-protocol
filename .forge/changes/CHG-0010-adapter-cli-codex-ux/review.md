---
forge:
  artifact: review
  schema: 1
change: CHG-0010
status: pending
iteration: 1
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
