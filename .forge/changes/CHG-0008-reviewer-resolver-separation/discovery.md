# Discovery — CHG-0008

## Existing behavior

- `change.schema.json` had no `reviewer_identity` field.
- `review.yml` represented separation as `required: true` only.
- `policy-review.schema.json` encoded that same bare-boolean shape.
- C-026 stated only that Reviewer and Resolver were distinct conceptual Roles.
- Specification §25 repeated the conceptual distinction.
- `validate_project` validated project configuration/flow/contract availability but did not inspect Change review identity.
- Codex projection generation represented stages and Gates but did not instruct isolated Strict Review execution.

## Constraints found

Completed FULL Changes CHG-0001, CHG-0002, CHG-0004, CHG-0006, and CHG-0007 legitimately lack the new evidence because it did not exist when they completed. The explicit non-goal forbids rewriting them.

C-045/C-046 constrain breaking Protocol 1 evolution. The implementation resolves this via
`protocol/compatibility.md`'s schema-versioning mechanism: `forge/change@1` stays unchanged
and backward compatible, and the new structural requirement lives only under a new suffix,
`forge/change@2`. Historical manifests, and CHG-0008's own manifest while its Review remains
pending, stay on `forge/change@1` and are unaffected.

Correction to an earlier draft of this note: the requirement is not conditioned on
`review.status`. Under `forge/change@2`, `reviewer_identity` is required for every FULL
manifest regardless of review status, including `pending` — this matches AC-004 as literally
specified and is enforced by
`test_full_pending_review_without_reviewer_identity_is_structurally_invalid`. What determines
whether the requirement applies is the schema suffix a manifest declares (`@1` vs. `@2`), not
its review status. A Change only migrates to `@2` once it is prepared to truthfully carry
reviewer identity evidence.
