# Discovery — CHG-0006

## Repository evidence

CHG-0005 introduced the canonical `blocking_review_threads_resolved` token in FULL, STANDARD, and FAST and added normative Core Protocol wording. Its behavioral regression was valid: Tests run `31723140301` failed at commit `929b6c4f1bfe88ca5ef3ab25e797b66e12a1433b` with `1 failed, 135 passed`; Tests run `31723428304` passed at commit `a1898f3b39ee4121610491eff947aa5ef1d57839`; the refactor remained green in run `31723460470` at `f96cfead579b2a3f031f8bc828e4815091c318b8`.

The completed CHG-0005 TDD artifact records only a cycle identifier and title. It omits its requirement, behavior, RED commit/run/reason, and GREEN commit/run. CHG-0006 preserves that historical record and cites the verified evidence as context rather than relabeling it as a new TDD cycle.

## Projection gap

The Codex workflow renderer recognizes `verification_passed` and `review_passed` as human-readable Completion instructions. The new token currently survives only inside the raw canonical Flow YAML appended to the generated resource. The Harness-facing instruction section does not explicitly tell Codex to reconcile blocking threads before Completion.

## Boundaries

- Repository-native Forge state remains canonical.
- An active external review surface is process evidence, not duplicated Change state.
- The Adapter represents the Gate but does not enforce, query, classify, or resolve review threads.
- The CLI remains outside Specification, TDD Implementation, Verification, Review, Resolution, and Completion execution.
