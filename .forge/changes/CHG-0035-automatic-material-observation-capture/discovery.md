---
forge:
  artifact: discovery
  schema: 1
change: CHG-0035
status: pending
---

# Discovery — CHG-0035 Automatic Material Observation Capture

## Executive Summary

**Recommendation: FULL Flow, with a hybrid capture strategy and no new FER
schema version.** CHG-0030 through CHG-0033 establish a local, opt-in,
non-normative FER writer with schema `forge/experience-report@1`, canonical
YAML, generated Markdown, bounded text, atomic writes, and isolated failures.
The current Forge can mechanically observe validation and Adapter conformance
facts, but it does not own a runtime lifecycle or approval executor.

## Investigation

### Current FER source of truth

- `configuration.py` treats absent/false `.forge/contributor.yml` as disabled.
- `model.py` preserves `forge_problem`, `project_problem`, and `uncertain`,
  and rejects oversized or sensitive text.
- `storage.py` lazily creates `dogfooding/reports/FER-####.yml`, appends under
  a local lock, writes YAML atomically, and updates Markdown. It has no
  candidate or fingerprint state.
- `experience_cli.py` supports `enable`, `disable`, `status`, `record`,
  `validate`, and `render`; manual recording must remain.
- CHG-0030 hardening rejects unsafe evidence, malformed reports, symlinks,
  unsafe ancestors, and preserves failure isolation.

### Real mechanical boundaries

`forge change new` scaffolds artifacts; normal validation reads repository
artifacts and emits findings; Adapter conformance validates a supplied
representation against required stages, gates, invariants, and limitations.
There is no lifecycle state machine, approval transaction, or review executor.
Approval bypass, lifecycle violation, repeated workaround, and semantic
contradiction therefore remain manual/assisted observations for now.

Adapter conformance findings such as removed Forge stages/gates/invariants,
TDD-red bypass, strict-review bypass, or authority shift are structured facts,
but only explicit Forge-owned checks may produce automatic events. Generic
validation failures, exceptions, test failures, and non-zero exits are not
events by themselves.

### Strategy decision

Fully automatic capture would force premature attribution or broad interception
and make FER an event log. Candidate-plus-confirmation would add persistent
candidate state and new CLI lifecycle semantics. **Hybrid is selected:**
high-confidence Forge-owned invariant events are recorded automatically as
`uncertain`; ambiguous semantic signals continue through `forge experience
record`. This minimizes lost evidence without inventing enforcement.

### Policy, deduplication, and provenance

The policy receives a bounded event with stable type, Change/execution/boundary
when known, expected invariant, observed condition, and purpose-specific
evidence. It returns `IGNORE` or `CAPTURE` before persistence. Automatic
entries default to `classification: uncertain`; the policy never infers a
Forge root cause.

Equivalent events within one report use a fingerprint derived from event type,
Change, execution/boundary, expected invariant, and observed condition after
bounded normalization. Timestamps, stack traces, and volatile output are
excluded. Repeats coalesce; materially different expected/observed conditions
create distinct observations. No fingerprint state is written when disabled.

### Responsibility and compatibility

Forge CLI/Core may emit only facts it establishes mechanically. Adapters supply
structured conformance facts but do not write FER. Harnesses, Agents, and
contributors continue to submit semantic observations manually; guidance is
not enforcement. FER remains outside Protocol, Contract, Flow, Change
validity, Review, Gates, Adapter conformance, and mergeability.

Existing `forge/experience-report@1` reports and Markdown remain authoritative.
Optional automatic provenance/observation extensions are preferred over `@2`;
the next design gate must confirm they are accepted by current readers.

### Open decisions for the next gate

- Which current conformance findings are stable enough to be detector inputs?
- Should coalesced occurrences use an optional count, bounded evidence, or
  simply ignore duplicates after retaining the first observation?
- What secondary diagnostic can expose a FER failure without changing the
  primary command result?
