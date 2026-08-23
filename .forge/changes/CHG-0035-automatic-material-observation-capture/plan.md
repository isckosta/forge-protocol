---
forge:
  artifact: plan
  schema: 1
change: CHG-0035
status: pending
---

# Plan — CHG-0035 Automatic Material Observation Capture

1. Add `experience/event.py` and `experience/policy.py` with bounded event
   types, normalization, allowlisted Adapter-conformance detectors, and
   `IGNORE`/`CAPTURE` decisions. Test with `tests/unit/` before integration.
2. Add `experience/recorder.py` as the only bridge from policy decisions to
   `ExperienceStorage`; check enablement before all side effects, attach
   optional automatic provenance/fingerprint, suppress equivalent duplicates,
   and return secondary diagnostics on failure.
3. Extend `experience/model.py`, `storage.py`, and `markdown.py` only with
   optional schema-@1-compatible capture metadata and deterministic rendering;
   preserve historical reports and manual recording.
4. Integrate the recorder at the existing Adapter conformance producer while
   preserving its result and ignoring generic project validation failures.
5. Add the TDD cases in `test-strategy.md`, CLI/Adapter/contract regressions,
   privacy checks, and failure-isolation checks.
6. Update `docs/experience-reporting.md`, both packaged Adapter workflow
   resources, and examples with manual versus automatic capture guidance.
7. Run focused RED/GREEN cycles, full verification, `forge validate`, FER
   validation, Markdown rendering, and a bounded dogfooding run.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation. The
Plan/Implementation boundary requires an explicit human Plan Decision recorded
in this artifact and provenance.

<!-- forge:plan-approval-confirmation -->

Generation was not treated as approval. Explicit human authorization was
received from the user as “Autorizo” in the active session on 2026-08-23.
This records the Plan Decision and authorizes crossing the Plan/Implementation
boundary for CHG-0035; it is repository evidence, not cryptographic or
provider-native attestation.

<!-- forge:plan-approval-record -->
