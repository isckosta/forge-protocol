---
forge:
  artifact: discovery
  schema: 1
change: CHG-0011
status: complete
---

# Discovery — CHG-0011

## Repository truth audit

Established directly from `protocol/` and `src/forge_cli/` (not from prior
session memory):

- Protocol version in use by this project: `2` (`.forge/forge.yml`).
- Active Change schema: `forge/change@2`
  (`protocol/schemas/change-v2.schema.json`). It declares `review.iterations[]`
  with `id`, `revision`, `subject_provenance`, `reviewer_provenance`,
  `status`, `evidence_gap` — **no field distinguishes why an iteration
  exists**. There is no `kind`, no scope, no convergence counter.
- Execution provenance ledger: `forge/execution-provenance@1`
  (`protocol/schemas/execution-provenance.schema.json`). Records have `role`
  (`implementation|resolution|review`), `execution{id,context_id}`,
  `revision{id, immutable_ref|commit}`, `source{assurance,observed_by}`. No
  field lets a `resolution` record declare what it changed or which findings
  it targeted.
- Mechanical enforcement lives entirely in
  `src/forge_cli/validation/__init__.py::_validate_protocol2_review_provenance`
  and `validate_project`. It enforces, today: subject/Reviewer role
  correctness, revision binding (logical + concrete immutable), Execution/
  Context independence, the effective reviewable workspace freeze (via
  `_reviewable_workspace_delta`, unioning committed/staged/unstaged/untracked
  deltas from the frozen subject commit, excluding only the exact
  Change-local `manifest.yml`/`provenance.yml`/`review.md` paths), and
  Git-history-anchored immutability of subject/Iteration provenance records
  (`_first_committed_provenance_record`, `_first_committed_review_iteration`,
  `_committed_review_iteration_ids`). This machinery is exactly what CHG-0011
  needs to reuse for Resolution Scope/Delta — it already computes
  "everything that changed since a frozen commit, excluding review-control
  metadata." Extending it to diff **two** frozen commits (prior reviewed
  subject → new Resolution subject) reuses `_diff_paths`/`_untracked_paths`
  without a parallel subsystem.
- Review policy is **not** parsed by the CLI at all.
  `protocol/policies/review.yml`, `protocol/versions/2/policies/review.yml`,
  and their schemas (`policy-review@1`, `policy-review@2`) are normative
  documents the agent reads and follows; `validate_project` never loads them.
  The mechanical/declarative split already exists: Python enforces structural
  invariants; YAML policy documents describe the same invariants for humans
  and agents (e.g. `reviewer_resolver_separation` in
  `protocol/versions/2/policies/review.yml` mirrors, in prose/YAML, exactly
  what `_validate_protocol2_review_provenance` enforces in code). CHG-0011
  follows the same split: new Python enforcement + a matching new YAML block.
- Contract resolution (`src/forge_cli/protocol_resolution/__init__.py`):
  `protocol/versions/<n>/contract/engineering.md` overrides the canonical
  `protocol/contract/engineering.md` only if it exists; it does not exist for
  Protocol 2, so **the Contract file is shared** between Protocol 1 and
  Protocol 2 resolution. CHG-0008 already added Protocol-2-motivated rules
  (C-045, C-046) directly to this shared file, because they describe
  Protocol-evolution process obligations rather than new mandatory Gates for
  existing instances. CHG-0011 follows the same precedent for its new C-XXX
  rules: they define what a *classified* Resolution Verification must and
  must not do; a Change that never sets `kind` makes no such claim and is
  therefore unaffected.
- `protocol/versions/2/specification.md` (55 lines, §1–§9) is the existing,
  intentionally separate elaboration surface for Protocol-2-only semantics
  (distinct from the shared canonical `protocol/specification.md`). This is
  the correct place to add Resolution Verification/Scope/Convergence
  sections — extending an existing primitive rather than creating a parallel
  document, per C-032/C-033.
- Empirical precedent for legitimate iteration: `CHG-0008`'s own 6 Strict
  Review iterations (`.forge/changes/CHG-0008-.../review.md`) were each a
  *directly caused* regression/gap in the prior Resolution's own delta
  (R004→R005 commit-binding gap, R005→R006 workspace-freeze gap, R006→R007
  provenance-authority gap, R007→R008 status-coupling gap) — a legitimate
  hardening chain, not scope amplification into unrelated territory. This
  confirms the convergence signal must be "material finding independent of
  the current cycle's originating findings," not merely "any new finding" —
  otherwise CHG-0008's own real, valid iteration chain would have been
  wrongly flagged non-convergent.
- Empirical precedent for the actual failure mode: `CHG-0010` is currently at
  Strict Review iteration 5 (`forge/change@1`, no provenance ledger, no
  scope). It is the concrete case motivating this Change, and it is Protocol
  1, so CHG-0011's mechanical enforcement (which depends on the Protocol 2
  provenance ledger) structurally cannot and must not retroactively apply to
  it — confirming the compatibility boundary below.
- No `review_kind`, `resolution_scope`, `convergence`, "Decision Gate", or
  similar vocabulary exists anywhere in `protocol/`, `ROADMAP.md`, or
  `docs/adr/`. This is new vocabulary, not a rename of an existing concept.

## Compatibility finding

Adding new **optional** fields to `forge/change@2` and
`forge/execution-provenance@1`, plus new **derived** (Core-recomputed, not
self-declared) convergence state, does not remove/weaken an existing
invariant, does not change the meaning of an existing required field, and
does not invalidate a previously valid conforming instance (`CHG-0008`,
`CHG-0010`, or any other Protocol 1/2 manifest that predates this Change and
never sets `kind`/`scope`/`targets`). Per `protocol/compatibility.md` this
does **not** require a new integer Protocol identifier and does **not**
require a new `forge/change@N` schema suffix — it is exactly the "optional
artifacts whose absence preserves existing meaning" category the document
already recognizes as compatible Protocol 2 evolution. This is recorded
formally as ADR-equivalent reasoning in `architecture.md` and as the
compatibility statement in `specification.md` §Compatibility, and
`protocol/compatibility.md` itself is updated with a short explicit
subsection (Contract F-009 requires evaluating backward compatibility for
Schema/Protocol changes).

## Adversarial self-check risk noted for Architecture

A convergence counter that is *read* from the manifest as authoritative
(rather than *recomputed* by Core from the `iterations` array on every
validation) is resettable/manipulable by simply rewriting the counter field.
Architecture must make the counter and `review_convergence_failed` state
Core-derived and cross-checked against self-declared values, not
self-declared truth — this is carried into Specification INV and
Architecture directly.
