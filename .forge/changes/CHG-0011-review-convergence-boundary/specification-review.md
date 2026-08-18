# Adversarial Specification Review — CHG-0011

Status: complete

Two edge cases were found and corrected before Architecture.

First, the original FR-006 allowed a `resolution_verification` Iteration to
be `status: passed` simultaneously with `full_review_required: true`. That
state is incoherent: if out-of-scope material mutation was detected, the
Verification cannot itself approve the subject — approval can only come from
the unrestricted Initial Review that follows. FR-006 and FR-012 were
rewritten so an Iteration that detects out-of-scope mutation is always
`status: failed` with `full_review_required: true`; only a subsequent
`initial_review` Iteration can reach `passed` for that subject family.

Second, FR-002 did not address a `resolution_verification` Iteration placed
first in `iterations`, which has no prior reviewed subject to diff against
and would make Resolution Delta computation (FR-004) undefined. FR-002 now
explicitly rejects that case.

No requirement was weakened to reduce iteration count or to let a Resolution
Verification claim unrestricted review authority. FR-007's "no re-audit"
obligation is unchanged, and Reviewer/Resolver independence (INV-004)
remains identical to Protocol 2 as established by CHG-0008 for every
Iteration regardless of `kind`.
