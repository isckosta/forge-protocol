---
capability: qa
schema: 1
---

# Capability — Quality Assurance

## Identity

**Quality Assurance (QA)** is a Harness-independent, behavior-oriented
competency for exercising executable software as a product and discovering
problems that are not limited to already-known Requirements.

## Purpose

QA provides structured exploratory evaluation of observable behavior. Its
value is to turn meaningful interaction with a runnable product into findings
that another person can reproduce, understand, prioritize, and route for
appropriate follow-up.

## Applicability

QA applies when software can be exercised through a runnable product surface,
such as a UI, API, CLI, service, job, integration, or other executable
boundary, and the goal is to discover behavioral risks beyond a fixed claim
set. It applies to new or changed software, existing journeys, integrations,
and targeted exploratory sessions.

QA does not replace deterministic Verification of known claims or Requirements,
Review of a Change and its risks, Investigate of the root cause of a known
problem, or Fix of an established defect. Those competencies may be useful
after QA produces a finding, but QA does not invoke their authority or perform
their work. QA also does not require a particular test framework, environment,
or harness.

## Inputs

QA needs:

- a runnable build, product surface, or executable boundary to exercise;
- enough context to identify the supported user journeys, important states,
  interfaces, constraints, and meaningful risks;
- available setup data, credentials, fixtures, dependencies, and environment
  information needed for safe execution;
- a stated scope or risk focus when one exists, while retaining permission to
  explore adjacent behavior that is materially connected; and
- a way to capture outputs, errors, state transitions, and other evidence.

If expected behavior is not documented, QA records the basis for its expected
behavior separately from what it observed and marks uncertainty rather than
presenting an assumption as a fact.

## Behavior

QA exercises the software as a product and explores a risk-informed set of
scenarios. It starts with representative happy paths, then varies inputs,
ordering, timing, permissions, data volume, repetition, and state. The
exploration includes, as applicable:

1. **Happy paths** — confirm that ordinary end-to-end journeys produce the
   visible result a user would reasonably expect.
2. **Edge cases** — exercise boundaries of values, sizes, timing, repetition,
   empty and unusually large data, and transitions near limits.
3. **Invalid states and errors** — submit malformed, incomplete, unauthorized,
   conflicting, stale, or otherwise invalid inputs and observe validation,
   recovery, isolation, and error communication.
4. **Combinations** — combine relevant features, roles, data shapes, options,
   retries, and state transitions where their interaction could change the
   result.
5. **Boundary conditions** — exercise interactions between components, services,
   persistence, configuration, external dependencies, and user-visible
   interfaces when those boundaries are in scope. QA keeps any assumption
   about the product distinct from an observation and labels it before using
   it to interpret a result.

For each meaningful scenario, QA records the starting state, exact actions or
requests, relevant data, environment and build identity, and the observable
result. It compares that result with an explicitly stated expected behavior.
An unexpected result is explored enough to establish whether it is stable,
intermittent, environment-dependent, or not reproducible. QA may narrow a
finding's conditions through additional experiments, but it does not turn
inference into fact, claim a root cause without evidence, or silently correct
the behavior under test. QA must not fix the software.

QA distinguishes these outcomes:

- **Observed behavior** is what the executable actually did.
- **Expected behavior** is the supported expectation used for comparison,
  including its source or confidence when it is not a formal Requirement.
- **Finding** is an observable mismatch, failure, risk, or notable behavioral
  result that merits follow-up; it is not automatically a defect diagnosis.
- **Root cause** remains unknown unless separate evidence establishes it; QA
  may recommend Investigate when causal diagnosis is needed.

QA is not Verification: it may check known behavior while exploring, but its
purpose is broader discovery rather than proving a preselected claim. It is
not Review: it evaluates the running product, not the quality or risk of a
Change. It is not Investigate: it characterizes what happens, not why a known
problem happens. It is not Fix: it reports and routes findings, without
implementing a correction.

This competency does not define a new Gate, Flow, lifecycle, mandatory
artifact, executor, registry, or enforcement mechanism. It does not select a
Flow, approve a Change, authorize a decision, or redefine the Protocol or
Engineering Contract.

## Outputs

QA produces a session summary that states the exercised scope, scenarios
covered, relevant environment/build identity, and areas not exercised. It
produces one finding per distinct behavioral problem or risk, using this
shape:

```
Finding
Observed behavior
Expected behavior
Conditions of reproduction
Evidence
Impact
Reproduction status
Uncertainty and suspected cause (only when clearly labelled)
Recommended next competency or action
```

Each finding distinguishes observed from expected behavior and includes
reproduction conditions precise enough for another person to retry. Evidence
may include captured output, screenshots, responses, logs, traces, state
snapshots, recordings, or a minimal reproduction sequence, as appropriate to
the product surface. Impact explains who or what is affected and the practical
consequence, without inflating severity beyond the evidence. A finding may
state `NOT REPRODUCED` when repeated attempts did not reproduce it; that is a
result with its conditions and evidence, not a silently omitted failure.

QA may recommend Verification, Review, Investigate, Fix, or further QA as the
next competency, but the recommendation is not an approval, assignment, or
implementation decision.

## Evidence Expectations

Evidence is expected to be reproducible, attributable, and sufficient to
separate observation from interpretation. A QA run should preserve, where
available:

- the exact build, revision, configuration, platform, and relevant dependency
  versions;
- setup state, account or role context, data or fixtures, and preconditions;
- ordered actions, requests, inputs, timing or concurrency details, and reset
  steps;
- the complete relevant observable output, including error details and the
  state after failure; and
- the expected-behavior source, impact rationale, reproduction attempts, and
  any uncertainty or suspected cause explicitly labelled as such.

Evidence can be retained in the surrounding repository-native context, such
as existing test or Change documentation, a report, or a message. QA does not
own a new mandatory artifact type or persistence mechanism. Durable evidence
must remain available through the repository or other context that governs
the run; transient recollection alone is insufficient for a reproducible
finding.
