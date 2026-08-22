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
conducted in a repository with no prior Git commit, the complete pre-existing
state within the intended repository scope MUST be committed, with no file
excluded, before Implementation begins. The baseline commit represents the
before-state; it is not Implementation. The Change's subsequent commits
MUST therefore be reviewable as the delta from that complete baseline.

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
