---
forge:
  artifact: intent
  schema: 1
change: CHG-0027
status: complete
---
# Intent — Review Cost Proportionality

## Problem

Forge currently expresses most review-cost proportionality through the
binary FAST/STANDARD/FULL Flow choice. That is useful for semantic scope,
but it does not give a Reviewer a durable, comparable way to calibrate the
amount of review evidence within a Flow. A small Change can therefore carry
the same review preparation burden as a much larger Change, while a large
Change can be described only by its semantic Flow classification.

The remediation item is RFC-level. This Change must investigate whether
diff size, blast radius, touched modules, additive versus substitutive
behavior, and other observable dimensions can support proportional review
cost without weakening adversarial Review, TDD, Verification, or Contract
requirements.

## Desired outcome

Deliver a human-decision-ready RFC that:

1. reports real historical Change-size and Review-cost proxies;
2. distinguishes useful signals from unsafe automatic shortcuts;
3. proposes a concrete, bounded calibration mechanism if the evidence
   supports one; and
4. remains `Status: Proposed`, because acceptance is a separate human
   decision and a future implementation Change.

## Scope

In scope: Intent, evidence-based Discovery, a proposed RFC, the RFC's
Specification Review and Strict Review, and durable verification of this
documentation-only Change.

Out of scope: implementation of a new Flow, Gate, Review policy, CLI
command, scoring algorithm, schema change, or modifications for roadmap
items #2–#6 and #8–#10.

## Success criteria

- The RFC cites the canonical Flow and Review rules it would affect.
- Historical measurements are reproducible from repository history and
  clearly label Change-artifact overhead separately from production diff.
- The recommendation has an explicit Confidence rating and limitations.
- The proposal preserves strict adversarial Review and does not treat
  passing tests or diff-only inspection as sufficient.
