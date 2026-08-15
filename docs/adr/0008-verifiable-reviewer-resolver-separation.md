# ADR-0008 — Verifiable Reviewer/Resolver Separation

Status: Accepted for CHG-0008 Resolution; independent re-review pending.

## Decision
Protocol 1 retains conceptual Role separation. Protocol 2 requires independent Review Execution and Context plus repository-native provenance bound to the exact review subject.

A revision has two identities: a logical ID and a concrete immutable reference. `revision.id` supports lifecycle naming; it cannot establish concrete binding alone. `revision.immutable_ref` is provider/VCS-neutral. In Git, `revision.commit` is a compatible shorthand for a `git_commit` immutable ref.

The review subject is frozen after implementation, tests, specification, verification evidence, and documentation are complete. The provenance record is committed after that freeze and points to the frozen revision. Review-control metadata may follow; other post-freeze reviewable changes invalidate the subject and require renewed provenance.

For Git, "post-freeze reviewable change" means the effective reviewable workspace delta relative to the frozen commit, not only committed history. Core evaluates committed `<subject>..HEAD`, staged/index, unstaged working-tree, tracked deletion/rename, and Git-visible untracked paths from the repository root. Git-ignored untracked paths are excluded.

Only the exact repository-root-relative `manifest.yml`, `provenance.yml`, and `review.md` paths of the frozen Change are review-control metadata. The exception is not based on basename, substring, suffix, directory membership, rename destination, or a symlink/non-regular replacement.

Core validates logical/concrete binding, local Git commit existence, effective workspace freeze, Role, assurance, and Execution/Context independence. `forge validate` owns the normative invariant; Doctor may surface additional operational diagnostics but cannot substitute for validation. `recorded` means repository-native self-recorded evidence; only `verified` may represent stronger observer-backed evidence.

## Consequences
The model avoids commit self-reference, removes ambiguity between GREEN and review-subject commits, blocks dirty/staged/untracked review bypasses, remains local-first, preserves Protocol 1 compatibility, and gives Codex/Harnesses an explicit sequence: finish reviewable material → ensure effective workspace cleanliness → freeze → record subject provenance → re-check the freeze → independently review the frozen subject → record Reviewer provenance.
