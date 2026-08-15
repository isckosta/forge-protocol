# Knowledge Capture — CHG-0008

Protocol compatibility is a semantic boundary. Protocol 1 remains unchanged; Protocol 2 adds independent Execution/Context and concrete revision-bound Strict Review.

A logical revision ID is not a concrete review subject. Protocol 2 normalizes an immutable revision reference and compares it across subject and Reviewer provenance. In Git, commit SHA is the concrete reference.

A provenance record cannot truthfully contain the SHA of the same commit that contains the record. Therefore the reviewable Resolution is frozen first; provenance is review-control metadata committed afterwards and points to the frozen subject.

Strict Review Iteration 3 exposed the next boundary: a commit SHA does not describe the **effective workspace**. A checkout may contain staged, unstaged, deleted, renamed, or untracked reviewable material while `HEAD` still equals the frozen subject. Consequently the freeze invariant must compare all reviewable Git state, not only commit history.

The durable abstraction is `reviewable workspace delta since frozen subject`: committed delta + index delta + working-tree delta + Git-visible untracked paths. `.gitignore` keeps irrelevant ignored cache/editor/temp paths out of this invariant. Machine-readable NUL-delimited Git output avoids whitespace/quoting ambiguity and preserves rename source/destination identity.

The metadata exception must be exact. Only the frozen Change's repository-root-relative `manifest.yml`, `provenance.yml`, and `review.md` regular files may differ. Basename matching, a lookalike file, another Change, rename-to-allowlist, a directory named like metadata, or symlink substitution is not review-control metadata.

A second lesson from Iteration 3 is procedural: Review metadata is executable repository state. An unquoted YAML value containing `MAJOR:` broke the canonical artifact contract and CI even though the review decision itself was semantically legitimate. Review-control metadata must remain schema/YAML-valid and should be validated like any other repository artifact.

`recorded` remains self-recorded repository evidence; `verified` is stronger observer-backed evidence. Core verifies consistency, locality, effective workspace freeze, and revision binding, not cryptographic authorship. A Resolver may establish and verify a Resolution subject but cannot certify the independent Strict Review that follows it.
