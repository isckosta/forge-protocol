---
forge:
  artifact: plan
  schema: 1
change: CHG-0057
status: complete
---

# Plan — CHG-0057 Release 0 1 0b4

1. Set `CLI_VERSION` to `0.1.0b4`.
2. Cut the dated changelog section for the merged capability exposure change.
3. Validate, push the release PR, merge it normally, tag the merged `main`
   commit, and create the GitHub Release to trigger the official publisher.

## Implementation Boundary

The release procedure and protected-branch policy provide the required human
authority for the release actions.
