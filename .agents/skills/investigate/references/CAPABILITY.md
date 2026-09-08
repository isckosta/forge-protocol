---
capability: investigate
schema: 1
---

# Capability — Investigate

## Identity

**Investigate** is a disciplined, evidence-driven diagnostic competency:
given a bug, a regression, a failing test, or any observed behavior
whose cause is not yet established, it determines what is actually true
before anything is proposed about what to do next. It is a competency
for finding out, not for fixing.

## Purpose

The default failure mode for diagnosing a problem is `symptom ->
plausible guess -> code change`: the first explanation that fits the
symptom gets acted on, evidence that would have contradicted it is never
collected, and the resulting change may correct a coincidence rather
than a cause. Investigate exists to replace that shortcut with:

```
problem
-> establish facts
-> reproduce when possible
-> gather evidence
-> competing hypotheses
-> test hypotheses
-> isolate root cause
-> conclusion
```

Its value is a conclusion whose confidence is proportionate to the
evidence actually gathered — including, when the evidence does not
support one, the explicit conclusion that root cause is not yet
established, rather than a fabricated certainty that only exists to end
the investigation.

## Applicability

Investigate legitimately applies to:

- bugs;
- regressions;
- failing or flaking tests;
- intermittent or non-deterministic behavior;
- differences in behavior between environments;
- integration problems between components or systems;
- any technical cause that is currently unknown;
- any symptom whose origin still needs to be demonstrated, not assumed.

Investigate does **not** apply once root cause is already established by
sufficient evidence and the remaining work is purely implementation —
at that point, invoking Investigate adds ceremony without adding
information, and the work belongs to whatever Flow stage implements the
already-understood fix. Investigate also does not apply to open-ended
exploration with no observed problem to explain (that is design or
research, not diagnosis).

## Inputs

Before Investigate can run, it needs:

- a stated problem: what was observed, and — as precisely as it is
  known — when, where, and under what conditions;
- read access to the relevant code, tests, and configuration;
- read access to runtime evidence where it exists: logs, error output,
  stack traces, monitoring/observability data, CI results;
- read access to Git history for the affected area (commits, blame,
  related past Changes) where causal timing matters;
- read access to any other artifact plausibly relevant to the problem
  (existing Change Artifacts, prior Knowledge Capture, configuration
  files, dependency versions);
- whatever access is required to attempt reproduction, when
  reproduction is applicable (a runnable environment, test harness, or
  equivalent) — Investigate does not require reproduction to be
  possible, only that its possibility be genuinely attempted before
  being ruled out.

A problem statement that is too vague to test any hypothesis against
(no observed behavior, no context) is insufficient input; the first
step of Behavior below is establishing enough fact to make the problem
concrete.

## Behavior

Investigate follows this sequence, and does not skip ahead in it:

1. **Problem** — restate what is actually being investigated, distinct
   from any explanation for it. A problem statement that already
   contains a diagnosis has skipped ahead.
2. **Establish facts** — separate what is directly observed (a fact:
   this input, on this commit, produced this output) from what is
   assumed, reported secondhand, or inferred. Facts and hypotheses are
   never merged into a single undifferentiated narrative; a reader must
   be able to tell which is which at every point in the investigation.
3. **Reproduce when possible** — attempt a deterministic reproduction of
   the observed behavior. A successful reproduction converts the
   problem into something that can be tested directly; a failed or
   infeasible reproduction attempt is itself recorded as evidence (with
   its Reproduction Status made explicit — see Outputs), not silently
   dropped.
4. **Gather evidence** — collect evidence from code, tests, runtime
   behavior, Git history, and other relevant artifacts before forming
   or committing to any explanation of cause. Evidence is gathered to
   inform hypotheses, not selectively gathered to confirm one already
   favored.
5. **Competing hypotheses** — form more than one plausible explanation
   before testing any of them. Fixating on the first plausible
   explanation (the `symptom -> plausible guess -> code change`
   pattern this competency exists to prevent) is a failure of this step,
   not an acceptable shortcut through it.
6. **Test hypotheses** — test each hypothesis against the gathered
   evidence: does the code path it implies actually execute; do the
   tests confirm or contradict it; does runtime evidence match its
   predicted effect; does Git history support or undermine its timing;
   do other relevant artifacts corroborate or conflict with it.
7. **Isolate root cause** — eliminate hypotheses the evidence
   contradicts. A hypothesis survives elimination, not proof by
   plausibility alone; a hypothesis is only treated as root cause once
   the surviving evidence sufficiently supports it and competing
   explanations have been genuinely tested, not merely dismissed.
8. **Conclusion** — state the outcome as either `ROOT CAUSE CONFIRMED`,
   with the evidence that sustains it, or `ROOT CAUSE NOT ESTABLISHED`,
   naming what remains unresolved and what evidence would be needed to
   resolve it. Both are valid, complete outcomes of an investigation;
   neither is a failure of the process.

Investigate MAY use temporary instrumentation or experiments (adding a
log line, running a script, exercising a code path in isolation) when
they are necessary to gather evidence or test a hypothesis, provided
they are clearly identified as investigative and are not carried forward
as, or confused with, the final solution. Investigate MUST NOT correct
the problem it is investigating, and MUST NOT alter production behavior
merely to validate a hypothesis — an experiment that changes observable
behavior for anyone other than the investigation itself is out of
bounds. Investigate does not decide that an implementation is warranted;
it recommends a next action (see Outputs) and leaves that decision, and
any Flow, Gate, or approval it would require, to whatever process
governs the repository it runs in.

Investigate is diagnostic, not implementation, and stays within that
boundary explicitly: it does not fix the problem it investigates; it
does not alter production behavior beyond what a clearly-identified,
temporary experiment requires; it does not approve Changes; it does not
select or redefine Flow; it does not create Gates; it does not control
lifecycle; it does not substitute for a human decision; it does not
turn an inference into a fact; and it does not redefine Protocol or
Engineering Contract. A conclusion Investigate reaches is an input to a
decision, never the decision itself.

## Outputs

An investigation produces an observable result covering, where
applicable:

```
Problem
Observations
Reproduction Status
Evidence
Hypotheses Evaluated
Root Cause
Uncertainty
Recommended Next Action
```

- **Observations** and **Evidence** are kept distinct from
  **Hypotheses Evaluated**: what was seen and what was gathered are not
  the same thing as what was inferred from them.
- **Reproduction Status** states plainly whether the problem was
  reproduced deterministically, reproduced only intermittently, or could
  not be reproduced, and why.
- **Hypotheses Evaluated** lists every competing explanation that was
  seriously considered, not only the one that survived — including why
  each eliminated hypothesis was eliminated.
- **Root Cause** states one of two literal outcomes: `ROOT CAUSE
  CONFIRMED`, with the evidence that sustains it, or `ROOT CAUSE NOT
  ESTABLISHED`, with what is still unknown and, where identifiable, what
  would resolve it.
- **Uncertainty** states explicitly what is not yet known even when root
  cause is confirmed (residual risk, untested conditions, scope not yet
  investigated) — a confirmed root cause is not the same claim as a
  fully characterized problem.
- **Recommended Next Action** proposes what should happen next —
  implement a fix, investigate further, gather more evidence, or decide
  the issue is not worth pursuing — without assuming that implementation
  is automatically the right next step, and without approving,
  authorizing, or scheduling that action itself; that remains a decision
  for whatever human or process holds that authority.

This competency does not require or impose a new mandatory artifact
type of its own — a run of Investigate produces this output shape in
whatever form the surrounding context already uses (a report, a
Discovery-stage document, a comment, a message), not a new file kind
invented to hold it.

## Evidence Expectations

Every causal conclusion Investigate reaches is expected to point to the
evidence that supports it, and to preserve, without blurring, the
distinction between:

- **CONFIRMED** — directly observed or reproduced; the evidence itself
  demonstrates the claim (a reproduced failure, a test that fails for
  the stated reason, a log line that shows the stated state).
- **INFERRED** — supported by evidence but not directly observed; a
  reasonable conclusion given what was gathered, stated as inference,
  not fact.
- **UNKNOWN** — not established either way; explicitly named as a gap
  rather than silently omitted or papered over with an inference dressed
  as a fact.

An investigation that reaches `ROOT CAUSE CONFIRMED` is expected to
attach CONFIRMED- or sufficiently-corroborated INFERRED-level evidence
to that specific claim; a conclusion resting only on UNKNOWN-level
material is, by definition, `ROOT CAUSE NOT ESTABLISHED`, however
plausible it reads.

When an investigation's result needs to survive past the execution that
produced it, repository-native evidence (committed code, tests, commit
history, and, in a Forge-governed repository, Change Artifacts) is the
durable source of truth — Investigate does not own storage of its own,
and a conclusion that exists only in a transient conversation or an
un-committed note has not, in that sense, survived its own execution.
