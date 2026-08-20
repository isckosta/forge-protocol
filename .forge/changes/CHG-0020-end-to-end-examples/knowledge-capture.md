---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0020
status: complete
---
# Knowledge Capture — CHG-0020

- **Curating real evidence is cheaper than fabricating a scenario, but
  its own failure mode is different: a citation that quietly doesn't say
  what it claims.** Every commit hash and quoted Finding excerpt in
  `strict-review-remediation/README.md` and `full-feature/README.md` was
  checked against real `git log`/`git show`/file content (T-006) before
  committing, not reconstructed from this conversation's own memory of
  earlier Changes. One concrete case worth naming: both `CHG-0018`'s own
  Strict Review (hook-pattern MINOR) and the *inner*, dogfooded scratch
  session's own Strict Review of its toy `greet()` fix (regression MAJOR)
  are independently labeled "R001" in their respective `review.md`
  files — same label, two unrelated Findings in two different Changes'
  own numbering. Easy to conflate if citing from memory; the direct
  `grep`/`git show` check caught that these are genuinely distinct before
  either README's text was finalized.

- **A curation-only Change's Verification step is the citation check
  itself, not a test run.** No code was touched, so `pytest -q`/
  `forge validate`/`forge doctor` staying unchanged (524 passed; clean;
  clean) confirms only that nothing broke — it says nothing about
  whether the new prose is accurate. The actual verification burden for
  this kind of Change is entirely in re-reading the historical artifacts
  being cited, which is a different (and easy to skip) kind of diligence
  than the tests-pass check most Changes lean on.

- **STANDARD flow's lighter ceremony (no Architecture, no
  Specification-Review, no `tdd-evidence.yml`) is legitimate here, not a
  shortcut.** This Change touches no Contract, schema, or executable
  code — `discovery.md`'s Flow Classification Finding correctly applied
  `protocol/contract/engineering.md` C-003 (semantic impact, not size) to
  land on STANDARD despite this being the fifth Change discussed in one
  long session; the ceremony matches the actual blast radius (five
  Markdown files), not the length of the surrounding conversation.
