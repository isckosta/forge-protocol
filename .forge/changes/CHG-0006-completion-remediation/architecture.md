# Architecture — CHG-0006

## Decision

Retain the existing Codex projection boundary. `_instructions(flow_content: str) -> str` parses canonical Flow YAML and emits stable human-readable statements for known Gate identifiers. CHG-0006 adds one conditional mapping for `blocking_review_threads_resolved`; it introduces no new module, service, external dependency, or lifecycle state.

## Data flow

1. Effective canonical Flow provides `before_completion.require`.
2. The renderer recognizes the blocking-thread token.
3. The generated skill communicates the corresponding Completion invariant.
4. The full canonical Flow remains appended and authoritative.
5. Repository artifacts and any active external review surface supply actual process evidence.

## Enforcement boundary

The sentence represents the invariant. It does not prove or perform enforcement. The Adapter and CLI do not discover pull requests, classify findings, resolve threads, or authorize Completion. No Architecture Decision Record is required because the established Adapter projection boundary remains unchanged.
