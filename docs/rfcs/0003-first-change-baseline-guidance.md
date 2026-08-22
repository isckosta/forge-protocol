# RFC-0003 — First-Change Baseline Guidance

Status: Accepted for Protocol 1

## Summary

This RFC adds a canonical Engineering Contract invariant for a Change
conducted in a repository with no prior Git commit. Before Implementation
begins, the complete pre-existing repository state must be committed as a
single baseline, with no file in the intended repository scope excluded.

## Motivation

A first Change has no historical commit to represent its before-state. A
separately created baseline is therefore part of the Change's evidence. If
the baseline omits a pre-existing file that Implementation later touches,
the Change diff represents that file as entirely new and obscures what the
Change actually modified. The first external validation of Forge exposed
this failure: the incomplete baseline was detected only by Strict Review.

The existing Contract requires Intent, classification, Specification before
behavior, TDD RED before production behavior, Verification, and Review, but
does not state how the first-commit before-state must be established.

## Decision

Add the following Contract rule:

**C-076 — Complete baseline for a first-commit Change.** When a Change is
conducted in a repository with no prior Git commit, the intended repository
scope MUST be declared, and the complete state that existed before the Change
began MUST be committed as one baseline, with no in-scope file excluded,
before Implementation begins. Change artifacts created after that point are
not pre-existing state. The baseline commit represents the before-state; it
is not Implementation. The Change's subsequent commits MUST therefore be
reviewable as the delta from that complete baseline.

This is a repository-state requirement, not a claim that a Harness can
technically prevent an incomplete commit. An Adapter may project the rule as
workflow guidance, but canonical repository-native state and evidence remain
authoritative.

## Compatibility and consequences

The rule is additive. A repository with existing Git history continues to
use its existing before-state. A first-commit Change gains an explicit
precondition that makes its diff evidence trustworthy. The rule introduces
no schema field, Flow stage, CLI command, Adapter lifecycle state, or
provider-specific dependency. Existing valid Protocol 1 instances are not
invalidated; the rule applies when the first-commit condition is present.

This rule applies only to Changes begun after C-076 adoption; it does not
retroactively invalidate a previously valid Change or require a historical
Change to acquire a baseline it did not have. This preserves the meaning of
existing Protocol 1 and Protocol 2 instances under C-045/C-046.

Because this repository's active project resolves Protocol 2's effective
Contract from `protocol/versions/2/contract/engineering.md`, C-076 is
recorded with identical meaning in both that versioned Contract and the
shared `protocol/contract/engineering.md`. This compatibility-preserving
dual representation follows existing repository precedent and does not
create a new integer Protocol identifier.

The rule does not prescribe a particular commit message, branch name, Git
hosting provider, or automation. It requires completeness within the scope
the Change is actually conducting, which must be stated when the repository
contains intentionally excluded operational or generated material.

## Alternatives rejected

### Adapter guidance only

Rejected as the canonical solution. It would leave the rule advisory and
allow each future Adapter to omit or reinterpret a lifecycle precondition
whose purpose is Harness-independent evidence integrity. The wording will
still be projected by both current Adapters as a usability measure.

### Automatic baseline command

Rejected for this RFC. Automatic Git mutation would create a new CLI and
Harness boundary, require decisions about ignored/untracked/generated files,
and exceed the remediation need. A future Change may evaluate automation
with its own safety and scope analysis.

### Review-only detection

Rejected as the primary rule. Strict Review remains responsible for
adversarial detection, but discovering an incomplete baseline after
Implementation is precisely the late failure this invariant is intended to
prevent.

## Future work

Future Changes may define a deterministic diagnostic or opt-in baseline
helper if real repositories demonstrate that the scope distinction cannot be
made reliably by the agent. Such work must preserve this Contract rule and
must not claim prevention unless the underlying Harness actually enforces it.

## RFC Addendum — final timing and compatibility boundary

The Contract wording is intentionally precise: the intended scope is declared
before the baseline, the baseline is one commit containing the complete state
that existed before the Change began, and Change artifacts created afterward
are not part of that pre-existing state. The rule applies prospectively to
new Changes after adoption. This addendum records those boundaries before
the corresponding Contract correction is accepted.

## RFC Addendum 2 — acceptance wording

The prospective-application boundary is part of C-076's compatibility
meaning: it preserves the meaning of existing instances under C-045/C-046
while requiring the complete baseline for newly begun first-commit Changes.
