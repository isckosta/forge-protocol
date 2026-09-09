---
capability: review
schema: 1
---

# Capability — Review

## Identity

**Review** is a critical, adversarial evaluation competency: it examines a
subject against the obligations, context, and effective review profile
supplied by Forge, then reports supported findings and meaningful gaps.

## Purpose

Review exists to challenge whether a subject is correct, coherent, safe, and
adequately supported before its surrounding Forge process relies on it. It
looks beyond the subject's own narrative so defects, regressions,
inconsistencies, risks, and unsupported claims are surfaced while they can
still be understood and addressed.

## Applicability

Review applies when Forge supplies a subject and an effective review context
for critical evaluation of that subject. The subject may be a change,
artifact, implementation, proposal, decision, or other material claim whose
correctness and support need to be challenged.

Review does not decide when review is mandatory, select a Review Mode or
Review Profile, resolve governance questions, approve a subject, or replace
Verification, Investigate, Fix, or QA. Verification checks declared
acceptance and required evidence; Review challenges the subject and its
supporting claims. Investigate establishes causes of observed problems; Fix
implements corrections; QA explores observable product behavior.

## Inputs

Before Review runs, it needs:

- the immutable or otherwise clearly identified subject under review;
- the applicable requirements, obligations, constraints, claims, and
  expected behavior against which the subject is to be evaluated;
- the surrounding context, including relevant dependencies, prior behavior,
  affected boundaries, and available repository or runtime evidence;
- the effective review profile supplied by Forge, including its scope,
  depth, materiality expectations, and any review-specific evidence
  expectations. Review consumes this profile as given; it does not select,
  resolve, weaken, or modify it.

If an input is missing, ambiguous, or outside the effective profile, Review
records that limitation and does not silently substitute a weaker criterion.

## Behavior

Review establishes the subject and the claims it makes, then maps those
claims and relevant behavior to the applicable obligations and effective
review profile. It actively searches for:

- defects, regressions, and violations of requirements or constraints;
- an inconsistency or other inconsistencies between specification,
  implementation, evidence, and
  observed behavior;
- risks at boundaries, failure paths, security or safety-sensitive areas,
  compatibility surfaces, and likely change interactions;
- an unsupported claim or claims that are only partially supported,
  stale, or stronger
  than their evidence permits.

It uses both confirming and disconfirming evidence. It tests plausible
counterexamples, traces important claims to concrete evidence, checks whether
the evidence actually covers the claimed scope, and distinguishes an observed
fact from an inference or an untested possibility. It prioritizes findings by
materiality and severity when the effective profile or available context
supports that distinction.

Review records cleanly examined areas and relevant limitations as well as
findings. No finding means only that no finding was established within the
performed scope and evidence; it is not a guarantee beyond that scope.

Review does not select or modify the effective profile; it does not modify the
profile or its scope. It does not own Flow,
Gates, approval, Completion, the rules that make Review mandatory, Review Mode
or Profile selection, normative independence requirements, provenance
authority, human authority, lifecycle, executor, registry, or orchestration.
Those responsibilities remain with Forge Core, Flow, the applicable review
rules, and the surrounding authority mechanisms.

## Outputs

Review produces a review result containing:

- the identified subject, review context, effective profile as received, and
  scope actually examined;
- clear findings, each with a stable reference where possible, location or
  affected scope, observed condition, expected or required condition,
  explanation of the discrepancy or risk, impact, and materiality or
  severity when applicable;
- concrete evidence for each conclusion, including commands, tests,
  observations, references, traces, or other reproducible support;
- explicit uncertainty, assumptions, evidence gaps, unreviewed areas, and
  plausible counter-evidence;
- a concise account of examined areas with no established finding and why the
  available evidence was sufficient for that limited conclusion.

The result may propose questions or corrective directions, but it does not
make approval, Completion, lifecycle, authority, or other governance
decisions.

## Evidence Expectations

A Review run should leave repository-native or otherwise durable evidence that
allows another qualified reviewer to understand what subject and effective
profile were used, what scope was examined, which checks were performed, and
how each finding follows from the evidence. Evidence should identify exact
locations or revisions where relevant and make reproduction possible through
the recorded commands, tests, observations, or source references.

Findings must not rely on an unsupported assertion of failure or correctness.
When evidence is unavailable or contradictory, the result records an evidence
gap or uncertainty instead of manufacturing confidence. Severity or
materiality labels must be explained by impact and by the applicable review
context. A clean area must state the examined scope and its limits.

The Capability owns neither storage nor lifecycle for this evidence. The
surrounding Forge process determines the authoritative artifact, provenance,
independence, approval, and retention rules.
