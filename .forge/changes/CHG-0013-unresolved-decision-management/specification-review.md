# Adversarial Specification Review — CHG-0013

Status: complete

One material defect was found and corrected before Architecture.

The original FR-013/INV-001 blocked Gates on any `decisions[]` entry whose
`status` was not `resolved`. This silently included `superseded`: once a
Decision is superseded by a later one, its own record is historical — the
live obligation to have an answer is carried by whichever Decision
superseded it, not by the stale entry. Under the original wording, a
superseded Decision would block Gates forever with no path to `resolved`,
since a superseded record is not expected to reach `resolved` itself (its
successor is). This would have made Decision-superseding unusable the first
time it was actually exercised. FR-013 and INV-001 (and the Terminology
section, which now names the exact blocking set as "Open-blocking states":
`open`, `analyzing`, `awaiting_decision`) were corrected so only those three
states block; `resolved` and `superseded` both do not.

FR-014 was also tightened: the original text said the owning Artifact "MUST
be revisited (its own stage/Gate re-entered)" without stating explicitly
that a Gate the owning Artifact had already passed (in particular
`specification_review_passed`) must be re-satisfied by a new Review
Iteration rather than treated as still valid once the Decision resolves.
Left implicit, this would have allowed exactly the silent-propagation
failure mode this Change exists to prevent: a backward-invalidating
Decision resolving without the upstream Gate ever being re-checked. FR-014
now states this explicitly.

No requirement was weakened to reduce the number of blocking states or to
let a downstream Artifact skip re-triggering an upstream Gate. The
Materiality test (FR-003), the Evidence-before-escalation requirement
(FR-004/INV-002), and the human-authority non-negotiability (FR-009/C-055)
are unchanged from the first draft.
