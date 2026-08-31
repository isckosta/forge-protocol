---
forge:
  artifact: intent
  schema: 1
change: CHG-0050
status: active
---

# CHG-0050 · Review Experience Modes

> **Change Intent**
>
> Expose Review to the developer through three UX-level modes
> (Recommended/Fast/Thorough) that map onto Forge's existing internal
> review-profile resolution, and make Review progress
> (Discovery/Findings/Resolution/Re-review) observable in the Harness,
> without letting UI choice silently reduce Flow/Contract-required
> assurance.

## Overview
| | |
|---|---|
| **Change** | CHG-0050 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

Today's Review experience can leave a developer stuck in
`review -> resolution -> review` cycles without a clear answer to why
the process continues, how much remains, or whether another full
review pass is coming. Separately, Review's internal vocabulary
(`focused`/`standard`/`strict` profiles, Flow identifiers) is exposed
as if it were something the developer must understand and choose
correctly to operate Forge, when it is actually Core's classification
concern (RFC-0007, C-022/C-023). There is no UX-level control that
lets a developer express "go fast" or "be thorough" without naming
Flow or profile directly, and no standing way to see, mid-Review,
which phase is active, what is left, and what happens next.

## Goal

1. Offer three developer-facing Review modes: `Recommended` (default;
   Forge determines the appropriate rigor for the Change), `Fast`
   (prioritizes speed and relevant findings), and `Thorough`
   (adversarial, in-depth analysis for higher-assurance situations).
2. Keep these modes strictly a UX/preference layer: Forge continues to
   resolve the effective review profile internally per Flow, the
   Engineering Contract, and any other applicable rule (RFC-0007);
   mode selection never overrides a Flow/Contract-required floor.
3. Make Review progress observable in the Harness as distinct,
   nameable phases (Discovery, Findings, Resolution, Re-review), so a
   developer can tell what is currently happening and what is left.
4. After Resolution, default to a re-review targeted at the resolved
   findings and the produced delta, instead of automatically
   restarting a full Discovery pass.
5. Let a developer stop further processing at a point where doing so
   does not produce a false claim of success, and ensure any
   unresolved-findings end state is recorded plainly with its
   evidence.
6. Preserve every existing blocking/assurance guarantee (Reviewer/
   Resolver independence, Convergence Limit, blocking Finding
   semantics, human-authority requirements) regardless of the selected
   mode.

## Scope

- The developer-facing vocabulary and control surface for choosing a
  Review mode per Change, and optionally as a persistent preference.
- How the chosen mode and the resolved effective review profile are
  surfaced for diagnosis/transparency in the Harness.
- Observability of Review lifecycle phases (Discovery, Findings,
  Resolution, Re-review) during an active Review.
- The default re-review scoping behavior after Resolution (targeted
  vs. full Discovery restart).
- The developer's ability to end further processing explicitly,
  and how an unresolved-findings end state is represented.
- This is a Protocol/CLI/Harness-Adapter-level capability: it must
  work in any Forge-enabled repository, not depend on
  `forge-protocol`'s own internal structure or artifacts.

## Out of Scope

- Redefining the internal review-profile model itself
  (`focused`/`standard`/`strict`, RFC-0007) — this Change consumes
  that model, it does not replace it.
- Changing Reviewer/Resolver independence mechanics, evidence
  requirements, Finding severities, or the Convergence Limit
  (C-026, C-047-C-050) — these remain unconditioned on UX mode.
- Building a numeric review score or any heuristic that substitutes
  for Flow's semantic classification (C-003).
- Any change to how Flow itself is classified or escalated.

## Success Criteria

- A typical Change run under `Recommended` converges without
  unnecessary full-review cycles.
- Review progress is clearly observable in the Harness at all times:
  active mode, effective profile (when useful for diagnosis), current
  phase, and what remains.
- Re-review after Resolution is targeted at the delta/findings by
  default, not a full Discovery restart.
- `Thorough` measurably increases rigor/adversariality, not merely the
  number of review rounds, and still respects the Convergence Limit.
- A developer can stop additional processing without Forge
  representing an invalid or fabricated success/approval state, and
  any unresolved findings remain visible with their evidence.
- The capability works in any Forge-enabled repository.
