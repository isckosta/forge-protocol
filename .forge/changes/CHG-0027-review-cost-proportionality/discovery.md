---
forge:
  artifact: discovery
  schema: 1
change: CHG-0027
status: complete
---
# Discovery — Review Cost Proportionality

## Evidence inspected

The current canonical rules establish three different controls:

- `protocol/flows/fast.yml` makes FAST a minimal-ceremony Flow, but keeps
  TDD, Verification, Strict Review, and Documentation Impact. Its
  disqualifiers include architectural, security, authorization, new
  invariant, integration, significant cross-module, and major public
  contract changes.
- `protocol/flows/standard.yml` is the default ordinary behavioral Flow;
  `protocol/flows/full.yml` adds Specification Review, Architecture, Test
  Strategy, explicit Tasks, and Knowledge Capture for high-impact work.
- `protocol/policies/review.yml` requires strict adversarial Review,
  reviewer/resolver separation, re-review after blocking resolution, and
  explicitly rejects both diff-only Review and passing tests as sufficient.

`protocol/contract/engineering.md` C-003 makes semantic impact, not line
count, authoritative for classification. C-022 and C-023 require
adversarial Review; C-039 requires proportional process; C-040 requires
explicit tradeoffs; and C-047/C-048 bound resolution verification to the
resolved subject and delta. `protocol/artifact-structure.md` §2.5 likewise
requires proportionality without allowing a material change to masquerade
as a small one.

## Historical measurements

The following table uses a reproducible repository-history proxy: the
committed range from the first Change artifact commit through the final
review-control commit on each historical Change branch. It counts all
Change artifacts as well as implementation files, so it is a Change
footprint, not a claim about production-code size. Recorded wall-clock
spans come from each Change's `provenance.yml`; token usage and human
attention time were not recorded and cannot be reconstructed.

| Change | Flow | footprint | requirements | TDD cycles | Review iterations | recorded span |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| CHG-0021 | FULL | 28 files, +2,683/-5 | 5 | 8 | 2 | 03:40–10:15 (6h35) |
| CHG-0020 | STANDARD | 17 files, +1,069/-19 | 5 | not applicable | 1 | 20:59–21:40 (41m) |
| CHG-0024 | FAST | 11 files, +377/-4 | 2 | 1 | 1 | 00:00–00:30 (30m) |

The ranges were measured with `git diff --shortstat` over respectively
`27e4fc0^1..27e4fc0`, `d35ecabe^..0eec94a`, and `2d0f1ef^..c63107b`.
The requirements, cycles, iterations, and timestamps are taken directly
from the committed manifests and provenance records. CHG-0021 is also
direct evidence that review cost is not only a function of initial diff
size: its cold Specification Review found four MINOR findings, its cold
Strict Review found a real BLOCKER (the claimed 535/0 baseline was actually
534/1 because its own traceability was schema-invalid), and a distinct
Resolution Verification had to reproduce the fix. This is three independent
Review executions with materially different findings and outcomes.

The sample is small and selection-biased. CHG-0024 is a small FAST Change;
CHG-0020 is a documentation-only STANDARD Change; and CHG-0021 is a large
FULL Change with generated Adapter and validation work. The data
demonstrates useful observability, not a validated pricing model. It also
does not establish that line count causes review time.

## Alternatives considered

### A — Keep only the current Flow choice

This preserves semantic classification and has no new mechanism cost. It
does not answer the remediation: within a Flow there is no durable
calibration vocabulary, so review effort remains largely ad hoc.

### B — Automatically choose Review depth from lines or files

Rejected. C-003 makes semantic impact authoritative, and a line threshold
can classify a generated-file change as risky or a compact authorization
change as harmless. An automatic downgrade would also conflict with the
canonical Flow escalation and strict-review guarantees.

### C — Proposed Review Calibration Profile (recommended)

Add a small, repository-native declaration to the Change's planning/review
evidence in a future implementation Change. The profile records observable
signals: semantic impact, blast radius, changed-file/module count,
additive versus substitutive behavior, external/public boundary, and test
surface. It selects a review emphasis and evidence budget inside the
already-classified Flow; it never removes the Flow's required stages,
Strict Review, reviewer independence, TDD, Verification, or documentation.

The first version should be descriptive and auditable, not a numerical
score. During a bounded pilot, each Change records the declared profile,
actual review iterations, findings by severity, and optionally observed
wall-clock duration. After 5–10 Changes, maintainers can calibrate whether
thresholds are useful. No token or attention-time claim is made until the
repository records it directly.

## Decision

Recommend Option C with **Confidence: Medium (0.72)**. The evidence is
strong enough to justify a concrete vocabulary and pilot, but too sparse
to justify mandatory thresholds or automated reduction of review work.
The mechanism must be accepted through a separate RFC decision and then
implemented by a future Change; this Change proposes it only.

## RFC gate

`CONTRIBUTING.md` requires an RFC before material changes to Review
semantics. This Change therefore proposes
`docs/rfcs/0005-review-cost-proportionality.md`, using the repository's
real Proposed/Accepted lifecycle. The concrete precedent is
`docs/rfcs/0002-harness-adapter-foundation.md`: its proposal commit is
`f8c8449` and its later acceptance commit is `bb332ff`. RFC-0003 also
records the same separation in its Change history. The RFC must not be
marked Accepted by this Change.
