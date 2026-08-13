---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0006
status: complete
---

# Knowledge Capture — CHG-0006

## External review state is process evidence

Repository-native Forge artifacts remain the canonical Change state. When a pull request or equivalent surface is active, its unresolved blocking threads are additional process evidence that must be reconciled before `review_passed` and Completion. The absence of an external review surface satisfies this condition trivially and preserves local-only Changes.

## Canonical Gate and derived Harness instruction

`blocking_review_threads_resolved` in the resolved canonical Flow is the Gate authority. The Codex Adapter conditionally translates that known identifier into a deterministic human-readable instruction and retains the complete canonical Flow in the generated resource. The sentence improves Harness participation but is derived representation, not a second semantic source or proof of enforcement.

## Ownership boundary

The Adapter and CLI do not discover external reviews, classify comments, resolve threads, or authorize Review/Completion transitions. Those actions remain in the Forge-governed engineering process and the active review surface. Adding provider-specific automation would require a separate Change and architecture decision.

## Remediation ownership

CHG-0005 history remains immutable. Its verified RED/GREEN runs are historical context, while CHG-0006 owns the new projection behavior and its complete temporal TDD evidence. Remediation records must not retroactively make an incomplete prior artifact appear complete.
