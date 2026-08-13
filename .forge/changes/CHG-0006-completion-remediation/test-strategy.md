# Test Strategy — CHG-0006

Status: approved.

## Behavioral TDD

TDD-001 covers FR-001, FR-002, AC-001, and AC-002.

- Positive case: a Flow containing `blocking_review_threads_resolved` produces the explicit Harness instruction.
- Negative case: a Flow omitting the token does not receive the instruction.
- Mutation check: removing the new production branch must fail the positive case while the negative case remains green.

Valid RED requires the positive assertion to fail because the renderer lacks the mapping. Fixture, syntax, dependency, or environment failures are invalid.

## Verification

- focused Codex projection Gate suite;
- complete automated suite;
- deterministic repeat coverage retained by the existing projection suite;
- isolated wheel and offline Distribution Verification;
- YAML parsing and diff hygiene;
- traceability across all four requirements;
- active PR check and blocking-thread reconciliation before Completion.
