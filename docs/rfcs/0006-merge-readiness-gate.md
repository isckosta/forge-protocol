# RFC-0006 — Merge Readiness Gate

Status: Accepted

## Summary

This RFC proposes a repository-native Merge Readiness Gate for the revision
proposed to enter the protected branch. It composes the existing effective
Flow, Change artifacts, validation rules, immutable Git subjects, and
provenance evidence without turning `forge validate` into a merge checker.

The RFC also resolves the specific authority gap identified by CHG-0036:
human Plan authorization must remain valid only while the approved Plan
content remains the content governed by that authorization.

## Motivation

Forge can currently validate structural and semantic validity, but validity
does not mean that a Change has completed Verification, Review, Resolution,
and Completion. A Pull Request can therefore have ordinary CI checks green
while its governing Change is still pending or stale. Conversely, material
runtime, Protocol, Adapter, test, or CI changes can be proposed without a
governing Change.

## Proposed decision

Add a provider-independent readiness evaluator and a CLI surface equivalent
to `forge change merge-check`. The evaluator receives explicit immutable base
and head revisions, resolves every affected Change from the diff, loads the
effective Flow, and derives a deterministic conjunctive verdict from existing
repository-native evidence. It returns stable diagnostics and uses command-
specific exit codes: 0 ready, 1 blocked, and 2 operational/configuration
failure.

The evaluator must not duplicate Flow definitions, execute lifecycle stages,
or replace Review, Verification, Completion, branch protection, or release
provenance. A required CI check may invoke `forge validate` followed by this
evaluator after fetching complete history. External branch protection remains
an administrative boundary.

## Plan authority binding

The accepted canonical rule is an immutable Plan-content binding. The
repository-native approval record must identify the exact approved Plan
content by a deterministic digest and bind that digest to the recorded human
Decision/provenance. A later Plan whose canonical content digest differs is
stale and cannot authorize the effective revision. The binding must be
represented in the existing provenance/Decision authority model, not in chat
history or Adapter output, and must fail closed when the historical binding
cannot be established.

The final field shape and migration boundary belong to Architecture and must
be accepted before implementation. Existing pre-CHG-0036 Changes remain
historically valid; the new binding applies prospectively according to the
compatibility rule recorded by CHG-0036.

## Alternatives

### A — Content digest binding (recommended)

Record a canonical digest of the approved Plan content in the repository-native
approval evidence and compare it with the effective Plan at merge-check time.
This detects edits even when history is rewritten or approval metadata is
appended later. It requires a small schema/representation extension and a
canonicalization rule.

### B — Immutable approval commit binding

Bind approval to the Git commit that contains the approved Plan and reject
any later Plan content change. This reuses Git identity directly but requires
complete history and careful treatment of metadata-only commits, rebases, and
Plan files changed alongside approval metadata.

### C — Decision-only binding

Treat the existing C-077 Decision and confirmation markers as sufficient.
This preserves compatibility and avoids schema work, but cannot detect the
stale Plan case required by CHG-0036 and is therefore rejected.

## Compatibility and assurance

Protocol 1 remains frozen and historically valid. The evaluator must use an
explicit compatibility policy for current merge authorization and must never
fabricate missing historical evidence. Recorded provenance remains durable
repository evidence, not cryptographic or external attestation. Release PR
provenance remains a separate later-stage check.

## Acceptance boundary

This RFC was accepted by explicit human decision selecting Option A
(`content digest binding`) for CHG-0036. The exact field shape and
canonicalization algorithm remain Architecture responsibilities and must be
recorded before Implementation.
