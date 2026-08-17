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

The Git freeze is expressed as one abstraction: **reviewable workspace delta since frozen subject**. Core unions committed `<subject>..HEAD`, staged/index, unstaged working-tree, and Git-visible untracked deltas from the repository root. Rename/copy parsing keeps source and destination paths; tracked deletions remain visible; ignored untracked paths remain excluded.

## Immutable authority for the subject
R007 established that filesystem allowlisting alone is insufficient: if the current mutable `provenance.yml` both chooses the baseline and is excluded from that baseline's delta, provenance can move the subject forward and hide a reviewable mutation.

The immutable authority is now **Git history, not the latest provenance value**. For a referenced subject provenance ID, Core reads the exact Change-local `provenance.yml` through committed history from oldest to newest. The first committed representation containing that ID anchors the whole subject record. Later content must preserve its ID, Role, Execution, Execution Context, logical revision, immutable reference/commit, source and assurance exactly. Removal, replacement, semantic mutation, duplicate/shadow IDs, or recreation with different content cannot redefine the subject.

## Historical Review Iteration identity
R008 separates Review lifecycle metadata from historical subject identity. Once a valid committed `manifest.yml` representation establishes an Iteration binding, the Iteration ID, logical revision and subject provenance are historical authority independently of `pending`, `passed`, or `failed` verdict state. A failed Review is still auditable evidence of which subject was reviewed; changing the verdict never authorizes redirecting that evidence.

Core therefore resolves the first valid committed `revision`/`subject_provenance` binding for each current Iteration ID regardless of status, compares the current binding against that authority, and also preserves every previously established bound Iteration ID so an attacker cannot rename/remove an old ID and present the replacement as a new Iteration. A genuinely new Iteration ID with its own binding remains legal.

Lifecycle fields remain independently mutable when the Protocol permits them. A legitimate `pending -> failed` transition, evidence-gap update, finding counter change, or append of a later Review/Resolution record does not mutate subject identity and remains valid. The effective workspace freeze remains lifecycle-aware: a failed subject may be followed by Resolver changes for the next Resolution, while the failed Iteration's historical identity remains immutable.

Historical YAML that cannot be parsed cannot itself establish a valid Review Iteration subject binding. Core may continue through such a snapshot to locate a later valid committed representation for the requested Iteration; if no safe authority can be determined, shallow history, Git failure, duplicate identity, inaccessible state, or otherwise insufficient history still fails closed.

This authority is born after the frozen reviewable commit: a metadata commit adds the Resolution provenance record pointing back to the frozen commit. That first committed record is the repository-native anchor. Subsequent Review provenance may be appended without changing it.

## Review-control metadata boundary
Only the exact repository-root-relative `manifest.yml`, `provenance.yml`, and `review.md` paths for the frozen Change may differ after freeze, and only while they remain regular non-symlink files. The exception permits lifecycle metadata append/update; it does not authorize rewriting an anchored subject record or historical Iteration subject binding. Basename, suffix, substring, directory membership, another Change's metadata, rename targets, and symlink substitutions do not qualify.

## Fail-closed history requirement
Core obtains the Git repository root locally with `git rev-parse --show-toplevel`. Existing anchored subjects require complete committed history so their first committed authority can be determined. Shallow repositories are insufficient and fail closed. CI therefore uses `fetch-depth: 0`. An unborn repository has no historical anchor yet and may establish its first record prospectively.

Git command failure, ambiguous historical identity, inaccessible historical state, or any other inability to determine the required authority fails closed. A malformed historical document cannot establish a valid binding by itself; if no later valid committed representation supplies the required authority, validation fails closed. No GitHub API or hosted Forge backend is required.

## Assurance boundary
This mechanism is repository-native and provider-independent. It makes rewrite attempts mechanically detectable against local Git history, but it is not cryptographic/external attestation and does not prevent an actor with authority to rewrite repository history from rewriting history itself. `recorded` therefore remains the correct assurance for self-observed Resolution/Review provenance; `verified` remains reserved for stronger observer-backed evidence.

Execution and Context separation, concrete revision equality, Protocol 1 compatibility, and FAST/STANDARD/FULL enforcement remain unchanged.
