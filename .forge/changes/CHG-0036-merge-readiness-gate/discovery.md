---
forge:
  artifact: discovery
  schema: 1
change: CHG-0036
status: complete
---

# Discovery — CHG-0036 Merge Readiness Gate

## Executive Summary

The repository already contains authoritative lifecycle and evidence
mechanisms. The missing capability is an evaluation boundary, not a second
lifecycle. The implementation should therefore compose the effective Flow,
existing validation rules, Git revision evidence, and canonical Change
artifacts into a separate read-only readiness engine. Because this changes
merge authorization and CI behavior, the Change is FULL and requires an RFC
before changing Contract or Gate semantics.

## Investigation

### CLI and validation boundary

The CLI currently exposes `forge validate`, `forge doctor`, migration,
scaffolding, and Adapter infrastructure. `forge validate` returns a project
validity result and must remain distinct from a readiness verdict. Its
validation module already contains reusable checks for Protocol 2 provenance,
review-subject freeze, Resolution Verification, delegated effects, unresolved
Decisions, and C-077 Plan authorization. There is no `merge-check` command or
readiness result model.

### Canonical Flow and lifecycle

`protocol/flows/fast.yml`, `standard.yml`, and `full.yml` are the canonical
Flow definitions resolved through `protocol_resolution`. Their completion
Gates require Verification, Review, documentation, TDD compliance, and
blocking review-thread resolution, with additional requirements in FULL.
The readiness evaluator must load these definitions and interpret their Gate
identifiers; it must not reproduce a second FAST/STANDARD/FULL matrix.

This Change is disqualified from FAST by `authorization_model_change`,
`architectural_change`, and `major_public_contract_change`. STANDARD is also
insufficient because this is a new authorization boundary affecting Protocol,
CLI, CI, and compatibility. The effective classification is FULL.

### Plan authority and stale approval

RFC-0004 and C-077 already require a human-authority technical Decision,
explicit Plan confirmation, and recorded provenance for active Changes from
CHG-0025 onward. The current validator proves presence and authority, but it
does not establish that the approved Plan content is still the content used
by the current implementation. A readiness check must add a canonical,
revision- or content-bound comparison for Plan authority rather than treating
`status: approved` as permission.

### Verification, Review, Resolution, and revision binding

Protocol 2 already defines concrete immutable Git subjects, independent
Reviewer Execution and Context, append-only historical subject bindings,
effective-workspace freeze, Resolution Delta, Resolution Verification, and
non-convergence. Existing tests cover stale subjects, malformed provenance,
renames, deletions, symlinks, and review-control metadata exceptions.

The evaluator should reuse those mechanisms and require the effective merge
subject to equal the admissible final Review/Resolution subject. A passed
manifest field without a corresponding admissible iteration and provenance
chain is not sufficient. Protocol 1 remains historically valid and must not
be retroactively strengthened; current merge authorization still needs an
explicit compatibility policy.

### Change resolution and provenance

No current command determines governing Changes from a revision range. The
safe source is the Git diff between explicit immutable `BASE` and `HEAD`.
Affected Change directories must be resolved from changed paths and their
manifest identities, including both sides of renames and deletions. Missing
history, malformed Change directories, contradictory manifest IDs, and
ambiguous ownership must fail closed. A material diff with zero affected
Changes must produce a stable provenance-missing failure.

The materiality policy must be centralized and testable. Repository truth
shows that Protocol resources, schemas, runtime `src/`, Adapter projections,
tests, and `.github/workflows/` can alter Forge behavior, runtime behavior,
evidence, or enforcement. Non-normative explanatory documentation may be
permitted without a Change; Protocol, Contract, policy, schema, and workflow
documentation cannot be silently treated as non-material. The policy must be
reviewed against actual repository ownership rather than copied from a fixed
prompt path list.

### CI and external enforcement

The existing `tests` and `verification` workflows already fetch complete Git
history. A new required check can run `forge validate` followed by the
provider-independent evaluator with explicit base/head SHAs supplied by the
Pull Request workflow. Branch protection, required-check configuration, and
the no-bypass setting remain GitHub administration boundaries and must be
documented as such. The release workflow's merged-PR provenance check solves
a later release question and must remain independent.

### Security and assurance boundary

Repository-native `recorded` provenance is durable evidence, not cryptographic
or external attestation. The checker can detect manifest tampering,
subject drift, stale approvals, deleted artifacts, path confusion, shallow
history, and ambiguous ownership when the required Git evidence is present.
It cannot prove that a recorded self-observation was truthful outside the
repository, nor can it enforce external branch protection. Those limitations
must be explicit in the Specification and diagnostics.

## Recommendation

Proceed with a separate reusable evaluator and a `forge change merge-check`
CLI surface, backed by a centralized materiality/provenance policy and the
existing effective Flow and validation authorities. Before implementation,
record and accept an RFC for the new merge authorization semantics, then
complete Architecture, Test Strategy, Plan, and the required human Plan
Decision. No implementation should begin before that boundary.

## Open Questions

1. Should the Plan authority binding use an additive field in the existing
   provenance schema or an existing immutable artifact/content reference?
2. What exact compatibility rule allows current Protocol 1 Changes to be
   evaluated without invalidating their historical validity?
3. Which repository materiality policy categories and exclusions should be
   accepted as normative authority in the RFC?
