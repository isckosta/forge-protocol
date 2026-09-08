---
capability: fix
schema: 1
---

# Capability — Fix

## Identity

**Fix** is a disciplined implementation competency: given a sufficiently
understood defect, it restores the violated behavior with the smallest
correct change and leaves reproducible evidence that the repair works.

## Purpose

Fix exists to keep implementation distinct from diagnosis without making
diagnosis a mandatory ceremony. It turns a supported root cause understanding
into a minimal, safe, verifiable repair, avoiding broad changes that merely
hide a symptom or silently expand the repair boundary.

## Applicability

Fix applies to bugs, regressions, failing tests, findings, issues, stack
traces, results of an investigation, and precise defect descriptions when
the observed behavior, expected behavior, supported cause, and affected
boundary are sufficiently understood. It may be used directly when that
understanding is already established; an investigation is not a mandatory
precondition.

Fix does not apply when a material part of the observed behavior, expected
behavior, cause, or affected boundary remains unknown. In that case, the
work must be directed to investigate rather than treating inference as
   an established cause. It also does not turn an architecture redesign or architectural change,
breaking change, requirement redefinition, or unrelated cleanup into a
local repair.

## Inputs

Fix accepts a concrete defect input such as a bug report, failing test,
finding, issue, stack trace, investigation result, or precise description.
Before implementation it needs the evidence available for the affected
code, tests, configuration, and runtime or CI behavior, together with:

- the observed behavior and conditions that produce it;
- the expected behavior or property that must be restored;
- the supported cause, with uncertainty called out rather than implied;
- the repair boundary: affected component, interfaces, and behavior that
  must remain unchanged; and
- a reproducible regression or equivalent verification target when one can
  reasonably be automated.

## Behavior

Fix follows this decision and implementation sequence:

1. **Check understanding** — compare observed behavior, expected behavior,
   cause, and boundary. If any material element is not sufficiently
   supported, stop implementation and direct the work to investigation.
2. **Preserve the repair boundary** — state what is in scope and what must
   not change. Check whether the proposed correction would become an
   architectural change, breaking change, requirement redefinition, or
   other material scope expansion. Escalate that expansion instead of
   silently accepting it.
3. **Define the smallest repair** — choose the narrowest change that
   addresses the supported cause and restores the expected property. Do
   not correct only the visible symptom when the evidence identifies a
   deeper cause, and do not add unrelated refactoring or speculative
   hardening to the repair.
4. **Drive a regression when feasible** — establish a test or other
   repeatable check that demonstrates the original failure before the
   implementation, then make the minimal correction.
5. **Verify the claim** — rerun the original regression and relevant
   affected behavior, and add proportional checks for adjacent behavior
   within the boundary. Evidence must show both that the expected behavior
   was restored and that the repair did not regress the protected boundary.
6. **Escalate uncertainty** — if the cause, expected behavior, boundary,
   or verification evidence becomes insufficient during the work, stop and
   recommend investigation or a human decision; never present an inference
   as a confirmed cause.

Fix is implementation guidance, not a replacement for Forge governance. It
does not select or redefine Flow, create or redefine a Gate, change approval
semantics, decide Merge Readiness, control lifecycle, or authorize a merge.
It does not redefine Protocol or Engineering Contract requirements. A
material scope expansion remains a governance and decision concern even
when the repair appears technically convenient.

## Outputs

A Fix run produces an observable repair result containing, where applicable:

```
Problem and expected behavior
Supported cause and evidence
Repair boundary
Minimal change made
Regression and verification results
Scope expansion or uncertainty
Recommended escalation, if needed
```

When the preconditions are satisfied, the result identifies the cause-led
minimal correction and evidence that the expected behavior was restored. If
they are not satisfied, the result explicitly stops short of claiming a
fix and directs the problem to investigation or the appropriate human
decision. It does not create a mandatory capability-owned artifact, and it
does not make an approval, Flow, Gate, lifecycle, or Merge Readiness
decision.

## Evidence Expectations

The repair should preserve evidence sufficient to reproduce the original
failure and to reproduce the restored behavior. At minimum, evidence
should identify the input or condition, the observed failure before the
change when reasonably automatable, the expected result, the exact
verification command or procedure, and its result after the change.

Evidence is proportional to the claim: a unit-level defect needs a
deterministic regression at that level; an integration or boundary defect
needs the corresponding affected behavior checked; and a claim that the
repair is minimal needs an explicit repair boundary and a review of scope.
Passing tests alone do not establish that the expected behavior was tested
or that the supported cause was corrected.

Repository-native code, tests, Change Artifacts, and verification records
are the durable evidence when the result must survive the execution. Any
remaining uncertainty, unverified condition, or material scope expansion
must be named explicitly rather than hidden behind a successful test run.
