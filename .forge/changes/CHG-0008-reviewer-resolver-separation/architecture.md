---
forge:
  artifact: architecture
  schema: 1
change: CHG-0008
status: complete
---
# Architecture — Protocol 2 Review Provenance

Protocol 2 separates logical revision identity (`revision.id`) from concrete immutable revision identity. `revision.immutable_ref` is the generic Core representation; Git `revision.commit` remains a compatible shorthand and must agree when both are present.

## Review-subject freeze
A Resolver completes implementation, tests, normative docs, verification evidence, and other reviewable material, then creates a concrete subject commit. Subject provenance is written afterwards and points back to that frozen commit. This avoids impossible self-reference: a commit cannot contain a truthful reference to its own not-yet-known SHA.

Only Change-local review-control metadata (`manifest.yml`, `provenance.yml`, `review.md`) may change after the freeze without creating a new subject. Any other committed change invalidates the binding and requires a new subject provenance record.

For Git immutable refs, Core validates local commit existence and detects post-freeze subject mutation using local `git diff`; no GitHub API or hosted Forge backend is required. Subject and Reviewer provenance must normalize to the same immutable reference in addition to the same logical revision ID.

`recorded` remains repository-native self-recorded evidence, not external proof. `verified` remains reserved for observer-backed evidence. Execution and Context separation remain independently enforced across FAST, STANDARD, and FULL.
