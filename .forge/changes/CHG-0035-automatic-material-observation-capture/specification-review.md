---
forge:
  artifact: specification_review
  schema: 1
change: CHG-0035
status: complete
---

# Specification Review — CHG-0035 Automatic Material Observation Capture

## Verdict

**PASS** — the specification preserves FER's opt-in, local, non-normative and
failure-isolated boundaries while limiting automation to facts the current
Forge can actually observe.

## Findings

No blocking finding remains. The specification explicitly rejects exception →
FER, test failure → FER, non-zero exit → FER, generic event logging, and
automatic `forge_problem` attribution.

## Checked and found sound

- The existing manual `forge experience record` surface remains supported.
- Disabled FER has no report or auxiliary-state side effects.
- Automatic entries default to `uncertain` and carry detector provenance.
- Deduplication excludes volatile evidence and does not create state while
  FER is disabled.
- Existing `forge/experience-report@1` reports and Markdown remain compatible.
- FER does not become Protocol, Contract, Flow, Gate, lifecycle, Review, or
  Adapter conformance state.
- Adapter/Harness/Agent semantic responsibility is not falsely represented as
  mechanical enforcement.

## Conclusion

The specification is ready for architecture and test-strategy design. The
remaining material decisions are intentionally deferred to Architecture:
the exact Forge-owned detector set, duplicate coalescing representation, and
secondary diagnostic mechanism.
