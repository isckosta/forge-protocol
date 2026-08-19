# Test Strategy — CHG-0016

## Objective

This Change's deliverable is overwhelmingly prose (a new canonical
guidance file, Contract/Specification/Compatibility pointer text, one
`ARCHITECTURE.md` sentence, one ADR, `CHANGELOG.md`) plus one small,
genuinely executable surface (Codex Adapter projection). Per Protocol
§19, TDD is marked `not_applicable` for the prose deliverables — it
cannot reasonably provide value for normative Markdown content, and
Verification/Strict Review remain mandatory for them regardless. TDD
applies fully to the Adapter projection change and to the pre/post
regression baseline.

## Strategy

Three TDD cases, all mechanically checkable, none fabricated to pad
coverage:

## TDD-001 — Codex Adapter projection includes `protocol/artifact-structure.md`

**Covers:** FR-009, AC-009.

**RED:** A test asserting the Codex projection bundle (whatever
`CodexProjectionInput`/`CodexProjectionBundle` construction test already
exercises `flow_content`/`contract_content` for) also carries an
`artifact_structure_content` (or equivalently named) field populated from
`protocol/artifact-structure.md`, with a non-empty SHA-256 digest. This
fails today because the field, the resource load, and the file itself do
not exist.

**GREEN:** Add the resource, wire `_resource()` loading into
`projection.py`'s existing pattern, add the field to the bundle.

**Expected Result:** The generated Codex skill bundle contains the new
content and digest; existing `flow_content`/`contract_content` fields and
their digests are byte-identical to before this Change (no incidental
change to unrelated projection output).

## TDD-002 — Adding the third resource does not change existing Adapter projection behavior

**Covers:** NFR-003, backward compatibility of the projection mechanism
itself.

**RED:** Re-run the existing Codex Adapter projection/publication test
suite as it stands today (before TDD-001's GREEN) to record its current
pass/fail baseline — this "RED" is a baseline capture, not a failing
assertion, matching `CHG-0015/plan.md`'s own stated practice of recording
an explicit `forge validate`/test baseline before Implementation rather
than relying on "it passed before."

**GREEN:** The same suite passes unchanged after TDD-001's GREEN, plus
one new assertion that adding the third resource introduced no new
required Adapter capability (`adapter.yml`'s declared capabilities are
unchanged) and no new ownership/collision classification for existing
generated artifacts.

**Expected Result:** Zero regressions in existing Adapter tests; the new
field is strictly additive.

## TDD-003 — Repository-wide `forge validate` / `forge doctor` baseline is unchanged

**Covers:** AC-013, CON-004, the compatibility claim underlying DEC-002's
"no new Protocol integer" conclusion for Alternative A.

**RED:** Record the exact current output of `forge validate` and `forge
doctor` against this repository (including every historical
`CHG-0001`–`CHG-0015` manifest) as the pre-Implementation baseline.

**GREEN:** After Implementation, `forge validate`/`forge doctor` report
the identical overall status against the same historical Changes, plus a
successful, unchanged result against `CHG-0016` itself once its own
`manifest.yml` is populated. No historical Change transitions from valid
to invalid.

**Expected Result:** Byte-for-byte-equivalent overall validity status;
any difference is treated as a regression requiring investigation before
Verification proceeds, not as an expected side effect.

**Baseline recorded now, before Implementation** (HEAD `7985080`, working
tree otherwise clean except this Change's own new, untracked planning
directory): `forge validate` reports **"Forge project is valid"** (exit
0) — confirming, mechanically, that `DEC-001` being `open` is correctly
*not* asserted as any Gate having passed anywhere in this Change's own
`manifest.yml` (Core's `C-051` check ran clean only after
`specification_review`/`architecture`/`test_strategy`/`plan`/`tasks` were
set to `drafted` rather than `complete`/`approved`/`ready` — the first
draft of this manifest legitimately failed this exact check, which is
the mechanism working as intended, not a defect). `forge doctor` reports
all 7 checks `PASS`. `pytest -q tests/contract` reports **35 passed**.
Any regression against these exact figures during Implementation is
investigated before Verification proceeds.

## Non-mechanical Validation

Reviewed by Strict Review, not by an automated test, because the subject
is normative prose rather than executable behavior:

- `protocol/artifact-structure.md`'s content against FR-001 (all six
  principles present), FR-002 (all fourteen real Artifact types covered,
  under real names), and INV-001 (no restated Contract/Flow/Policy
  normative text — reference by identifier only).
- New Contract rule wording (`C-067`+) against FR-006 and against
  DEC-001's eventual resolution (rule strength matches what the human
  actually decided, not what this Test Strategy assumed).
- `protocol/specification.md` §41 and `protocol/compatibility.md`
  addendum against FR-007/FR-008 and the CHG-0011/CHG-0013/CHG-0015
  addendum style precedent.
- `docs/adr/0014-*.md` against Contract F-008 and this repository's own
  ADR style (`docs/adr/0012-unresolved-decision-management.md` as the
  closest structural precedent, per Discovery).
- Canonical examples under `examples/canonical-artifacts/` against
  FR-010 and against Result-Before-Evidence as actually defined in the
  new guidance file (self-consistency check: the examples must conform
  to the guidance they demonstrate).
- `ARCHITECTURE.md` §5's one added sentence against FR-011, matching the
  minimal-edit precedent CHG-0015 itself set for its own `ARCHITECTURE.md`
  touch.

## Completion Criteria

All of AC-001 through AC-013 satisfied (AC-003 as amended if DEC-001
resolves as Alternative B); TDD-001 through TDD-003 GREEN; Non-mechanical
Validation items reviewed and accepted at Strict Review; `tdd-evidence.yml`
and `traceability.yml` produced during Implementation from what actually
happened (not authored in advance, per the same reasoning
`CHG-0015/plan.md` step 7 already recorded for itself — reconstructed
evidence is forbidden by C-016/C-021).

## Traceability (informal — `traceability.yml` itself is Plan/Tasks-stage-onward work)

FR-001/FR-002 → AC-001/AC-002 → Non-mechanical Validation (content
review). FR-003 → AC-003 → contingent on DEC-001. FR-004 → AC-004 →
content review + canonical examples. FR-005 → AC-005 → content review.
FR-006/FR-007/FR-008 → AC-006/AC-007/AC-008 → content review. FR-009 →
AC-009 → TDD-001/TDD-002 (the only FR with full mechanical TDD
coverage). FR-010 → AC-010 → canonical examples + content review.
FR-011 → AC-011 → Documentation Impact review. CON-002/CON-004 →
AC-012/AC-013 → TDD-003.
