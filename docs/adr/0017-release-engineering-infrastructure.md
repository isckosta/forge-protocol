# ADR-0017 — Release Engineering & v1 Release Candidate (Infrastructure)

Status: Accepted for CHG-0019 Implementation; independent Strict Review pending.

## Decision

Forge gains the infrastructure `ROADMAP.md`'s "Release Engineering & v1
Release Candidate" milestone requires, without cutting a real release.
`pyproject.toml`'s own `version` field and `version.py`'s `CLI_VERSION`
were two independently hardcoded strings with zero enforcement (confirmed
structurally: the commits that centralized `CLI_VERSION` never touched
`pyproject.toml`) — fixed by `[tool.hatch.version]` reading `CLI_VERSION`
dynamically, verified with a real RED/GREEN build (a changed
`CLI_VERSION` produced a stale-versioned wheel before the fix, and a
correctly-versioned one after).

A new `forge migrate`/`forge migrate --check` mechanism recognizes
exactly one schema family: `forge/execution-provenance@1` → `@2`, the
one case found to be both a real, live-instance case (six historical
Changes — `CHG-0008`, `CHG-0011`–`0015` — still declare `@1`) and a
byte-identical superset for any record whose `role` isn't
`delegated_task` (`protocol/compatibility.md`'s own CHG-0015 text). Two
other schema-version pairs were found and deliberately excluded, each for
a different reason: `forge/change@1` is explicitly forbidden from
migration by `compatibility.md`'s own normative text; `forge/
adapter-installation@1` needs a `publication_root` with no derivable
default. A fourth pair, `forge/policy/review@1`/`@2`, was found during
Specification Review and excluded for a third reason again — it is a
canonical, Protocol-version-selected resource with no live per-project
consumer in this codebase at all, not user data to migrate. Building a
general-purpose migration framework for hypothetical future cases was
explicitly rejected — this Change builds exactly the one case it has
real evidence for, mirroring the same discipline this repository already
applies elsewhere (e.g. `CHG-0018`'s DEC-003).

New Contract rule `C-075` generalizes `CHG-0007`'s own one-off,
truth-preserving migration discipline (never fabricate missing historical
data) into a durable rule, now that `forge migrate` is a reusable
mechanism rather than a single manual fix.

A new `publish.yml` GitHub Actions workflow builds wheel and sdist,
smoke-tests both offline, and publishes via PyPI OIDC trusted publishing
(no stored token) — but triggers only on a published GitHub Release,
which does not exist and which this Change does not create.
`verification.yml` is cleaned up (two stale branch triggers referencing
deleted branches removed; sdist coverage added alongside the pre-existing
wheel-only check, verified locally before trusting it to CI).
`RELEASING.md` records the actual manual checklist a human will follow
later, including the PEP 440 version scheme (`ROADMAP.md`'s own
`0.1.0-alpha.1`-style sketch was not valid PEP 440 and is corrected here
as a factual fix, not a judgment call) and the one genuinely external
prerequisite this repository cannot perform itself: registering a PyPI
trusted publisher.

## Consequences

A human can now bump one version string, run `forge migrate`/`--check`
against any project needing it, and follow `RELEASING.md` to cut Forge's
first real prerelease — all already built and tested. Nothing about this
Change's own landing publishes anything, tags anything, or creates a
GitHub Release; that remains a distinct, later, explicitly-authorized
action. The migration mechanism is deliberately narrow — a future second
real migration case (e.g. `adapter-installation@1`→`@2` once a real
installed-Adapter case exists to drive its design) is a new Change, not
an extension implied by this one. `forge doctor`'s new advisory is
non-blocking by construction (`status="warning"`, `DoctorResult.passed`
already ignores anything but `"failed"`) — it changes no existing
project's `forge doctor` exit code.
