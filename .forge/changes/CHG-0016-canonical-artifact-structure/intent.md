# Intent — Canonical Artifact Structure for Human-Readable Change Documentation

## Summary

Forge Change Artifacts (Intent, Discovery, Specification, Architecture,
Test Strategy, Plan, Tasks, Verification, Review, Resolution, Knowledge
Capture) have well-defined *semantics* — the Protocol says what each stage
must establish — but no equivalent normative guidance for how each
Artifact should organize what it presents to a human reader. Structure is
currently pure agent behavior: consistent when one session's habits carry
across a Change, divergent whenever a different agent, Harness, or session
produces the next one.

This Change introduces a **Canonical Artifact Structure**: non-binding,
canonical guidance — living beside Contract, Flow, and Policy in
`protocol/` — that gives each human Markdown Artifact type a recommended
information architecture (what belongs in it, and in what order), without
turning `forge validate` into a Markdown linter or making any existing
Change non-conforming.

## Problem

`protocol/specification.md` and `ARCHITECTURE.md` normatively define
*what* each Artifact must establish (Contract C-001–C-066, Flow minimum
lifecycles) but say nothing about *how* that content should be organized
for a human reader. `ARCHITECTURE.md:36` already lists "Artifact
semantics" as part of what canonically lives in `protocol/` — but no file
under `protocol/` currently defines it; the label is reserved, not filled.

The absence is not hypothetical. Comparing this repository's own
completed Changes shows measurable drift:

- `CHG-0001/verification.md` opens with `## Result` immediately after the
  title. `CHG-0015/verification.md` (the most recent Change) has **no
  `## Result` heading at all** — PASS/FAIL exists only in `manifest.yml`,
  not in the artifact a human reads. The outcome-first convention existed
  and was lost, not merely unformalized.
- Total Markdown lines across a Change's Artifacts grew from 896
  (CHG-0001) to 2404 (CHG-0015) — a ~2.7x increase — without a
  proportional increase in declared semantic complexity (both are `kind:
  feature`).
- The Plan → Implementation boundary is currently reinforced by
  hand-written prose repeated nearly verbatim across sessions (see
  `CHG-0015/plan.md` and `CHG-0013/plan.md`, both containing a
  hand-authored "Explicit boundary" section making the same argument) —
  evidence that the boundary is a real, recurring need currently met by
  reinvention rather than by structure.
- `Review.md` already puts each iteration's verdict in its own heading
  (`## Iteration N — PASS`), but a Change with several iterations (e.g.
  `CHG-0008`, six iterations) gives a top-to-bottom reader five negative
  verdicts before the final one, with no aggregate summary at the top.

## Desired Outcome

A reader opening any Forge Artifact should be able to determine, without
reading the whole document: what they are reading, which Change it
belongs to, its current state, its primary conclusion, and where the
supporting evidence lives — while a reader who needs the reasoning or the
evidence can still find it, in a predictable place, without it crowding
out the outcome.

## Scope

- New canonical guidance document(s) under `protocol/` defining
  Progressive Disclosure, Artifact Responsibility, Result-Before-Evidence,
  Scanability, Proportionality, and Extensibility as design principles,
  and a recommended structural core / conditional / optional section
  breakdown per human Artifact type actually produced by this repository.
- Minimal, additive Contract guidance referencing that document.
- Adapter projection support so the Codex Adapter (and any future Adapter)
  can surface the guidance without redefining or duplicating it.
- Canonical examples demonstrating the structure, without mass-reformatting
  historical Changes.

## Out of Scope

- Markdown AST validation, heading-presence linting, HTML/PDF rendering,
  or any new `forge validate` enforcement beyond what Discovery
  demonstrates is materially necessary.
- Redesigning `manifest.yml`, `provenance.yml`, `tdd-evidence.yml`,
  `traceability.yml`, or any machine-readable Schema.
- Reformatting CHG-0001 through CHG-0015.
- Any new Flow, lifecycle stage, Finding severity, Review convergence
  rule, or Unresolved Decision Management semantic change.

## Success Criteria

See Specification (`specification.md`) for concrete, verifiable Acceptance
Criteria. At Intent stage, success means: a single canonical source of
truth for Artifact structure exists in `protocol/`; STANDARD and FULL's
most outcome-critical Artifacts (Verification, Review) can be scanned for
their result without reading supporting evidence first; FAST inherits no
new ceremony; and every existing completed Change remains valid.
