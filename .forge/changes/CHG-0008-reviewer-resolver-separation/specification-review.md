# Adversarial Specification Review — CHG-0008

Status: complete

The pre-implementation review challenged two edge cases. First, requiring reviewer identity
while Strict Review is still pending would force fabricated evidence for a Change that has
opted into the new requirement; the eventual resolution avoids this by letting a Change defer
opting in (via schema suffix) until it can truthfully supply that evidence, rather than by
exempting `pending` review status from an already-adopted requirement. Second, applying the
new required field retroactively would invalidate completed `forge/change@1` history and
conflict with the explicit non-goal; this is resolved by keeping `forge/change@1` unchanged and
introducing the requirement only under a new `forge/change@2` suffix, so completed historical
records are preserved without needing a status-based carve-out.

No requirement was weakened to permit FULL same-session Review. `agent_same_session` remains prohibited for FULL both by policy and semantic CLI validation.
