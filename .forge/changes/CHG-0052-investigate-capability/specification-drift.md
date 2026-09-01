---
forge:
  artifact: specification_drift
  schema: 1
change: CHG-0052
status: complete
---

# Specification Drift — CHG-0052

## Root Cause

`specification.md`'s FR-006 and `CON-001` prohibited any change to
`capabilities/README.md` or `capabilities/capability.md` for this
Change. That prohibition was derived from the original request's
"Architecture" boundary list (`CapabilityRegistry`, `CapabilityExecutor`,
discovery, a new lifecycle/Gate/Protocol version, `/investigate`, a
Harness-specific `SKILL.md`, Harness adapters) plus its own instruction
not to "redesign the foundation... salvo se a implementação revelar uma
incompatibilidade objetiva." The Specification over-read that guidance:
it treated "do not redesign the foundation" as "do not touch any byte of
the foundation's documentation," which the original request never
actually said, and which is a different, stronger claim than the one the
request's boundary list supports.

`capabilities/README.md:3-6` states, as of the frozen Iteration 3
subject: "No concrete Capability exists yet — this document defines the
abstraction so that the first real Capability (`investigate`, in a later
Change) has a place to live." Once `capabilities/investigate/
CAPABILITY.md` exists — which is this Change's entire purpose — that
sentence is not a design choice under discussion; it is a factually false
status claim about the present state of the repository, sitting three
lines into the exact document a reader would open first to understand
Forge's Capability layer.

## Evidence

Codex's review comment (PR #47, thread on `CHANGELOG.md:16`, anchored to
`capabilities/README.md:3-5`, P2): "Introducing the first concrete
capability makes the repository's main capability overview immediately
inaccurate: `capabilities/README.md:3-5` still says that no concrete
Capability exists and that `investigate` will arrive in a later Change.
Consumers following the newly announced path are therefore given
contradictory current-state documentation; update that status paragraph
even if the architectural contract otherwise remains unchanged."

Independently re-read against the actual file: confirmed literally true
— `capabilities/README.md` lines 3–6 (at the Iteration 3 subject,
`deee80048ec3e71072229c1d83e1acdfb45d88f4`) read exactly as quoted above,
and `capabilities/investigate/CAPABILITY.md` exists in the same
revision. No other paragraph of `capabilities/README.md` makes a
present-tense factual claim contradicted by this Change — the rest of
the document (What a Capability is/is not, Responsibilities,
Architectural boundaries, the relation diagram, "Adding a future
Capability" and its worked `investigate/` example) describes the
abstraction itself, not the current inventory of concrete Capabilities,
and remains accurate unchanged.

This repository has one directly on-point precedent for exactly this
shape of defect and its resolution:
`CHG-0046/specification-drift.md` — a normative correction found by the
same class of source (an external, independent GitHub Codex review bot,
on a PR, after this repository's own internal Strict Review had already
passed) that the internal Review process had not caught.

## Final decision

FR-006 and `CON-001` are corrected (superseded, not deleted) to narrow
their scope: this Change MUST NOT introduce any of the mechanisms listed
in FR-006 (`CapabilityRegistry`, `CapabilityExecutor`, discovery, a
dependency graph, a composition runtime, Capability-owned state, a new
lifecycle, a new Gate, a new Protocol version, `/investigate`, a
Harness-specific `SKILL.md`, a Harness adapter), and MUST NOT alter the
architectural contract of `capabilities/README.md` or
`capabilities/capability.md` (their "What a Forge Capability is/is not,"
Responsibilities, and Architectural boundaries sections, and
`capability.md` in its entirety) — but MAY, and in this specific case
MUST, correct a status statement in `capabilities/README.md` that this
Change's own delivery makes factually false, limited to the minimum text
needed to restore accuracy (the introductory status paragraph naming
`investigate` as future work). `capabilities/capability.md` remains
untouched by this correction — it defines the timeless contract, not a
present-tense inventory, and this Change's own Discovery/Verification
already confirmed nothing about it changes.

This required reopening Strict Review for this narrowly-scoped delta:
tracked as finding **R-003** (this document's Evidence, above) in
`review.md`, resolved via `resolution-003`, and re-verified by a fourth
independent Reviewer execution (Iteration 4), per C-026 — `capabilities/
README.md` is genuine reviewable content, not Change-local bookkeeping,
so it does not qualify for the lighter self-attested-provenance-only
renewal `CHG-0046` used for its own (Change-local, non-reviewable-code)
correction.
