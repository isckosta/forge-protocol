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

C-045/C-046 constrain breaking Protocol 1 evolution. The implementation therefore treats completed historical manifests as historical records and applies the new identity requirement prospectively to active FULL review execution. This compatibility boundary requires independent Strict Review.

A pending Strict Review cannot truthfully contain identity for a Reviewer session that has not executed. The schema therefore does not require `reviewer_identity` while `review.status` is `pending`; once FULL Review execution begins, identity is mandatory.
