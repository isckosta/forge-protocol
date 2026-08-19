# ADR-0013 — Delegated Execution Authority Boundaries

Status: Accepted for CHG-0015 Implementation; independent Strict Review pending.

## Decision

Forge gains a normative distinction between Capability (what an Execution
can technically do) and Authority (what a specific delegation permits it to
do), and a mechanism to make Authority a checkable property rather than a
natural-language instruction. This was motivated by a real incident: during
`CHG-0014`'s Discovery, a research subagent explicitly delegated read-only
work overwrote that Change's `intent.md` directly. The mutation was caught
only because a human-equivalent Execution happened to notice — no Forge
mechanism was capable of detecting it, since Protocol 2's only prior
mutation-detection machinery (`_reviewable_workspace_delta`) only activates
after a Review-subject freeze, long after the incident's own lifecycle
point.

A delegated Execution (`forge/execution-provenance@2`, `role:
delegated_task`) declares an Authorized Scope — exact repository-relative
paths it may mutate, possibly empty for read-only delegation, reusing and
generalizing `scope`, already present but role-restricted in `@1`. An
Execution Boundary (a baseline captured at delegation-open — a commit SHA
plus a content-identity map of every already-dirty path, so a delegating
Execution's own concurrent work-in-progress is never misattributed) lets
Core compute the delegate's Observed Effect independent of Change lifecycle
stage, including before any Review-subject freeze — the exact point the
motivating incident occurred at. Any Observed Effect outside the declared
Scope is Out-of-Scope Mutation (C-061), generalizing Protocol 2 §11's
existing Resolution-specific concept. A delegate rewriting its own
already-committed Scope to claim broader Authority is self-authorization
(C-062), detected separately — by comparing a record's current declared
Scope against its first committed representation (the same "immutable once
committed" rule C-026 already established), not by the Observed-Effect
path-diff, which necessarily excludes `manifest.yml`/`provenance.yml`/
`review.md` for an unrelated, structural reason (a delegating Execution's
own bookkeeping write of the delegate's provenance record is unavoidable
noise at the path-diff level, indistinguishable from an attack there).
A delegating Execution cannot grant Authority exceeding its own — the
Delegation Ceiling (C-063), checked transitively through nested delegation,
with a deterministic conservative default (the Change's own `.forge/
changes/<id>/` directory) when a first-hop delegator declares no Scope of
its own.

Detection (C-064) — verifying an Observed Effect against a declared Scope
using only local Git-native state — is the mandatory floor; harness-
enforced Prevention remains optional and is not claimed anywhere in this
repository today (no installed Adapter offers it). Indeterminate
authorization (unavailable Git history, malformed records) fails closed
(C-065), never defaulting to "authorized." No enforcement claim overstates
Detection as Prevention (C-066).

New Contract rules (C-060–C-066, `protocol/contract/engineering.md`,
mirrored into `protocol/versions/2/contract/engineering.md` per the
CHG-0011/CHG-0013 dual-file precedent) bind a Change only once it records a
`role: delegated_task` provenance entry — the same prospective-only binding
pattern C-047–C-059 already established. No RFC accompanies this ADR:
matching CHG-0008, CHG-0011, and CHG-0013's own established practice
(recorded in `docs/adr/0012`'s own Decision section), `docs/rfcs/` is
reserved for foundational Protocol RFCs; a Contract/Specification-level
addition below the scale of a new integer Protocol identifier gets an ADR
only, which this Change follows rather than reinterpreting.

## Consequences

Forge can now distinguish, mechanically, "this delegated Execution had
filesystem write access" from "this delegated Execution was authorized to
use it here" — the property the motivating incident showed did not
previously exist as anything other than a sentence in a prompt. The
mechanism was corrected twice during its own Architecture and
Implementation, both times by actually trying to build and test it rather
than by review of the design alone: an early draft would have made
self-authorization mechanically undetectable for exactly the three files
that matter most (fixed by separating the self-authorization check from
the path-diff entirely, `c7ffb47`); a later draft reused an existing
"first committed representation" helper that turns out to hard-reject any
non-Reviewer/Resolver role by construction (fixed with a narrower sibling
function, `0b788de`). Both are recorded in `knowledge-capture.md` as
general lessons, not only as fixed bugs. This mechanism does not attempt
network/external-service coverage, does not build an automatic-rollback
engine, does not fully solve concurrent-delegation attribution beyond
fail-closed on ambiguity, and does not add any new Adapter capability —
each deliberately deferred, recorded in `architecture.md`'s own "What this
Change deliberately does not build."
