---
forge:
  artifact: specification_drift
  schema: 1
change: CHG-0012
status: complete
---
# Specification Drift — CHG-0012

This Change went through four distinct approaches before reaching its final,
engineer-approved form. Each is recorded here because each represents a
genuine Requirement-level correction (or, in the fourth case, a genuine
Requirement-level *decision*), not merely an implementation adjustment.

## Attempt 1 — unconditional exemption (Resolution 1)
Exempt `state.current == "complete"` unconditionally from the freeze-drift
check. Independent Strict Review Iteration 1 found **CHG-0012-R001
(BLOCKER)**: this silently disabled detection of the Change's *own* reviewed
files being tampered with, not only unrelated repository activity —
`intent.md`'s original Goal section asserted the tradeoff was safe because
"only unrelated activity" would be exempted; that assertion was false as
implemented.

## Attempt 2 — trust the first seal commit (Resolution 2)
Compare the frozen subject against the first commit where `state.current`
recorded `complete`, instead of exempting unconditionally. Independent
Resolution Verification Iteration 2 found **CHG-0012-R002 (BLOCKER,
resolution regression)**: `state.current` is hand-editable with no
programmatic gate; seal → revert → tamper → re-seal hid the tampering
because only the first seal commit was ever trusted.

## Attempt 3 — walk the entire post-seal history (Resolution 3)
Walk the full history after the first seal and fall back to comparing
against HEAD if `state.current` is ever observed reverted or unparseable.
Independent Resolution Verification Iteration 3 found **CHG-0012-R003
(BLOCKER, resolution regression)**: the history walk used
`git log --diff-filter=AM`, which is structurally blind to commits that
*delete* `manifest.yml` — seal → delete manifest.yml → tamper → recreate
manifest.yml as complete hid the tampering, defeating the walk's own
docstring claim of covering "the entire history."

This was the **second consecutive Resolution Verification producing an
independent, material finding** — the Convergence Limit CHG-0011 defines.
The independent Reviewer correctly stopped rather than attempting a fourth
automatic fix, recording `review.convergence.state: review_convergence_failed`
on `manifest.yml` and returning authority to the engineer, exactly as
CHG-0011's mechanism prescribes (dogfooded here for the first time on a
Change other than CHG-0011 itself).

## Attempt 4 — structural rewrite: scope to the implementation's own touched paths
Given three consecutive attempts to infer *when* it is safe to trust
`state.current`'s mutable history each closing one gap and opening another,
the engineer chose Non-Convergence option B ("return to an earlier
engineering phase") and directed a structural rewrite that stops depending
on `state.current`'s history entirely: compare only the paths the frozen
implementation commit itself touched, checked permanently against current
HEAD, exactly like an active Change.

This closed R001, R002, and R003 simultaneously (confirmed: all three
attack scenarios, replayed against the rewritten code, are caught). But it
reintroduced real, observed CI friction: `src/forge_cli/validation/__init__.py`
is a shared, frequently-touched file, and this Change's own implementation
touches it — so once merged, this Change's own frozen subject would trip
the *next* Change that also touches that file, exactly the original CI
failure pattern, just narrowed to files the two Changes happen to share
rather than the whole repository. This was discovered empirically (CHG-0011's
manifest began failing validation again against this Change's own
uncommitted work) rather than anticipated during the engineering decision,
and is recorded here as the reason Attempt 4 was not adopted despite closing
every previously-found BLOCKER.

## Final decision — accept the Attempt 1 shape, with its risk explicitly documented (Non-Convergence option C)
Presented with the choice between (a) the structurally stronger Attempt 4,
which reintroduces real operational friction on shared files, (b) reverting
CHG-0012 entirely and resolving each future occurrence of the original bug
manually, or (c) the simplest exemption (Attempt 1's shape) with its known
gap explicitly accepted rather than silently reintroduced, the engineer
chose (c).

**The accepted residual risk**: once a Change's `state.current` is
`complete`, its own previously-reviewed files could in principle be edited
without this check detecting it — whether by a hand-edited `state.current`
value that was never genuinely earned through Completion, or otherwise.
**Why this is accepted**: Protocol 2's entire provenance model is
`assurance: recorded` (self-declared, repository-native) throughout, not
`assurance: verified` (observer-backed) — the system does not otherwise
defend against an actor with direct write access deliberately fabricating
review state, and no branch-protection or permission enforcement exists at
this layer of `forge validate` regardless of this specific check. Closing
this one narrow gap while the broader trust model remains self-declared
provides limited additional real protection, at a cost (Attempt 4's
friction) the engineer judged disproportionate. This is an explicit,
documented C-040 trade-off, not a silently reintroduced defect: R001/R002/
R003 are real, were each independently found and reproduced by adversarial
review, and remain technically valid attack descriptions against the final
shipped code — they are consciously not fixed, not undiscovered.

No requirement was weakened to close this Change faster in the sense of
skipping review: four independent Strict Review Iterations were conducted,
three found real BLOCKERs that were genuinely fixed at each step (even
though the final code reverts to Attempt 1's shape, that reversion happened
only after Attempts 2-4 were tried, understood, and found to trade one real
problem for another), and Non-Convergence was reached and handled exactly as
CHG-0011 prescribes: automatic progression stopped, and an explicit,
justified engineering decision was made by the engineer, not fabricated by
the agent.
