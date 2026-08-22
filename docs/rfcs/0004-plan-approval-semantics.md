# RFC-0004 — Plan Approval Semantics

Status: Accepted for Protocol 1 and Protocol 2

## Summary

This RFC defines the authority boundary for crossing from a complete Plan to
Implementation. A Plan's `status: approved` is not, by itself, evidence that
a human authorized Implementation. A Change that declares an approved Plan
before Implementation must record a human-authority technical Decision owned
by the Plan and resolved through an explicit human act recorded in the Plan
and provenance.

## Motivation

The Standard and Full Flows require `plan_complete`, but neither the Flow nor
the Change Schema identifies the authority that asserted it. Existing Plans
use `status: approved`, allowing an agent-authored string to look equivalent
to a human approval. Contract C-055 already rejects the corresponding
self-resolution pattern for human-authority Decisions; the Plan boundary
needs the same protection.

## Decision

Add the following Contract rule:

**C-077 — Plan Implementation requires recorded human authorization.** A
Change MUST NOT cross its Plan/Implementation boundary while its Plan is
declared `approved` unless its manifest records a material technical
Decision owned by `plan` with `authority: human`, `status: resolved`, and
`resolved_via: human_decision`. The Plan MUST record the explicit human
confirmation and the Change's provenance MUST preserve its statement and
context. An agent MUST NOT silently infer or claim that confirmation.
`forge validate` MUST report a finding when the required Decision is absent
or unresolved, while preserving the distinction between recorded evidence
and cryptographic or external attestation. Transient conversation text alone
is not repository state; the recorded Plan and provenance are the durable
evidence.

The rule applies prospectively from CHG-0025 onward to Changes that are not
yet complete when the rule is adopted. Existing Changes with lower allocated
identifiers, including still-active historical Changes, remain valid under
the compatibility boundary in C-045/C-046; they are not silently rewritten
to manufacture an approval event that never occurred. `specification_gate_passed` remains a
technical lifecycle Gate: it is not renamed to imply human approval and does
not acquire this requirement unless a future Change establishes a separate
human-authority decision for Specification.

The existing `status: approved` vocabulary is retained for compatibility and
because it describes the Plan's approved content. Its authority is now
explicitly represented by the Decision record rather than inferred from the
status string.

## Compatibility and consequences

This is an additive Contract clarification for Protocol 1 and Protocol 2. It does not change the
meaning of completed historical Changes, add a new CLI command, require a
provider-native attestation, or make transient chat state canonical. New or
active Changes must carry the Decision before crossing the boundary. The
existing `decisions[]` vocabulary is reused; no new Schema shape or CLI
command is required. This follows CHG-0014's established explicit approval
boundary and provenance convention.

The validation rule detects missing and invalid authority evidence. Harnesses
may project a prompt for a human act, but a projection is not itself proof;
the manifest and its recorded Decision remain authoritative.

## Alternatives rejected

### Rename `approved` to `ready`

Rejected as the primary solution. A rename removes a misleading word but
does not identify the authority that may cross `plan_complete` and does not
fail closed when that authority is absent.

### Adapter-only guidance

Rejected as the canonical solution. Both current Adapters can remind an
agent to obtain a human act, but guidance cannot make the Gate semantically
checkable or prevent an agent-authored status from being treated as proof.

### New CLI approval command

Rejected for this RFC. The CLI is not required for normal lifecycle
execution, and introducing a command would expand the change into a new
Harness/CLI boundary. A future Change may add an ergonomic recording helper
while preserving this repository-native Decision requirement.

## Future work

Future Changes may define a provider-independent UX for recording the human
Decision, extend the same authority treatment to another Gate after evidence
of a human-authority requirement, or add stronger cryptographic attestation.
