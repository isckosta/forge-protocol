---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0007
status: complete
---

# Knowledge Capture — Protocol v1 Contract Freeze

## Version axes are independent

Protocol `1` is an integer compatibility contract. Schema suffixes version
individual artifact shapes; CLI and Adapter releases retain independent SemVer.
Changing a human display label does not change compatibility, while weakening
an invariant or invalidating a conforming instance requires a new integer
Protocol identifier.

## A schema catalog needs semantic rejection tests

Catalog/file closure and meta-schema validity prove only that schemas are
present and syntactically valid. A stable protocol also needs negative tests
that attempt to weaken stages, Gates, Policies, evidence, and compatibility
bounds. Happy-path canonical instances alone cannot prove contract strength.

## Distribution is a separate boundary

Source-tree catalog validation does not prove installed availability. The wheel
test must load the packaged catalog away from source imports and resolve every
entry. This is distribution Verification, even when packaging behavior already
exists and therefore has no valid feature RED.

## Historical truth outranks cosmetic compliance

Structural migrations may remove obsolete fields or wrap unchanged mappings.
Missing TDD evidence cannot be reconstructed. When a completed historical
Change lacks durable RED/GREEN details, an explicit exception is more accurate
than retaining a false compliance claim.

## RED/GREEN must be independently auditable

Interactive observation is insufficient when test and implementation first
appear in the same commit. Durable TDD evidence should reference a test-only
RED revision/run and a later GREEN revision/run with exact commands and results.

## Change IDs and branches

Roadmap stages do not reserve Change identifiers. Forge allocates the next ID
when the repository-native Change begins. Dedicated branches should include
that ID using `<type>/chg-NNNN-<slug>` for traceability, but Git branch names
remain references rather than lifecycle authority.
