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

The Git freeze is expressed as one abstraction: **reviewable workspace delta since frozen subject**. Core unions four local sources relative to the repository root:

1. committed delta from `<subject>..HEAD`;
2. staged/index delta;
3. unstaged working-tree delta;
4. Git-visible untracked paths.

Machine-readable NUL-delimited Git output is used. Rename/copy status contributes both source and destination paths so moving reviewable content onto an allowlisted path cannot erase the mutation. Deletions remain visible. `git ls-files --others --exclude-standard -z` supplies untracked paths while respecting `.gitignore`.

## Review-control metadata boundary
The exception is exact and Change-local. Only the repository-root-relative paths for that frozen Change's `manifest.yml`, `provenance.yml`, and `review.md` may differ after freeze. Basename, suffix, substring, directory membership, another Change's metadata, or a rename target do not qualify. An allowlisted path must remain a regular non-symlink file; deletion or symlink substitution is reviewable mutation.

All other implementation, test, specification, evidence, documentation, Change, and normative Protocol material remains part of the review subject. Any such delta requires renewed subject provenance.

## Locality and validation boundary
Core obtains the Git repository root locally with `git rev-parse --show-toplevel`; nested CLI execution therefore resolves the same repository-relative paths. No GitHub API or hosted Forge backend is required. `forge validate` owns the normative C-026 failure because dirty subject state can invalidate `review_passed`/Completion. `forge doctor` may add operational diagnostics but cannot substitute for validation.

`recorded` remains repository-native self-recorded evidence, not external proof. `verified` remains reserved for observer-backed evidence. Execution and Context separation remain independently enforced across FAST, STANDARD, and FULL.
