---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0050
status: complete
---
# Knowledge Capture — CHG-0050

## What Changed

Forge Review gained a developer-facing UX layer over CHG-0048's Review
Profile model: three named Review Experience Modes (`recommended`
default, `fast`, `thorough`) selectable per Change and as a persistent
project preference, resolved through a new, structurally
never-below-floor function (`resolve_effective_review_profile`); a
schema-tracked Review phase (`review.current_phase`) making
Discovery/Findings/Resolution/Re-review observable and Core-validated;
and a new read-only `forge change review-status` command.

## Durable Knowledge

**A per-Flow, install-time Adapter projection function cannot read a
specific Change's live manifest fields.** `_gate_instructions` in both
Harness Adapters runs once per canonical Flow at `forge adapter
install` time, before any Change exists. The original Architecture for
this Change (and its Plan) assumed otherwise for `review.mode`/
`current_phase`, discovered wrong only during Implementation (`DEC-004`).
Any future Change adding Adapter-projected text that varies by
per-Change state must design for this from the start: per-Flow static
text can only depend on Flow-level data (like `review.profile` already
does); a specific Change's live state needs a separate, on-demand
channel (here, `forge change review-status`) — not a retrofit into the
install-time projection path.

**`compute_review_profile_floor`/`resolve_effective_review_profile`'s
never-below-floor guarantee is structural, not tested-in.** The
function can only ever return `floor` or one `PROFILE_RANK` step above
it; there is no code path that reads a `mode` value and returns
something lower. This is why Strict Review Iteration 1 could
adversarially probe it with garbage `mode` strings and find nothing —
the guarantee doesn't depend on validating `mode` at all, only on the
function's own shape. Future work extending mode/profile resolution
should preserve this property: make the safety guarantee an emergent
consequence of the function's structure, not a validated invariant
that a missed edge case could silently violate.

**An unvalidated value flowing from a project-configuration read into
an unguarded dict/enum lookup is a real, live crash risk in a
"read-only diagnostic" command specifically.** `forge validate` already
had a name and error code (`E_FORGE_REVIEW_PROFILE_BELOW_FLOOR`) for
the exact malformed input (an invalid `.forge/flows/<flow>.yml`
`review.profile` override) that crashed `forge change review-status`
with a raw `KeyError` (R-001). A command whose entire purpose is safety
(runnable at any time, on any project state, per its own Specification
Boundary) is exactly where this class of gap matters most and is
easiest to miss, because the "happy path" test suite for a new command
rarely constructs a fixture from a *different* subsystem's known bad
input. When adding a new command that reads existing configuration,
check what validation already rejects that input for, and confirm the
new command degrades the same way — don't assume "it validates
upstream" without tracing the actual call path.

**C-026's provenance append-only rule and the manifest/provenance/
review.md metadata exception have a real, sharp edge once Strict
Review has already passed an iteration.** Iteration 2 found two
genuine, low-severity findings (R-005, R-006) whose obvious fixes
(correcting a scope list, renumbering a TDD identifier) turned out to
be mechanically forbidden after the fact: `resolution-001`'s `scope`
field, once committed, cannot be rewritten (it's a "committed Review
Iteration ... binding," not exempt review-control metadata), and
`tdd-evidence.yml` is not one of the three exempt paths, so editing it
after Iteration 2 had already reviewed and passed a commit would
invalidate that passed subject. The practical lesson: get Resolution
Delta scope declarations and cross-file identifier numbering right
*before* freezing, because non-blocking findings discovered by a later
Resolution Verification about the Resolution itself cannot always be
cleanly fixed without another full Review cycle — sometimes the
correct, Contract-compliant outcome is to disclose and accept them
instead, exactly like an ordinary OBSERVATION.

## Consequences for Future Changes

- Any future Change that adds Adapter-projected instruction text should
  check upfront whether the text needs to vary per-Change (requiring a
  new observability channel, as here) or only per-Flow (fitting the
  existing `_gate_instructions` pattern directly) — this distinction
  was the single largest planning gap in this Change.
- A Resolution's declared `scope` list should be double-checked against
  `git diff --stat` of the actual commit before freezing, not written
  from memory of intended changes — `provenance.yml`'s own record of
  itself is an easy path-to-forget case (this Change's own R-005).
- New `TDD-xxx` identifiers added by a Resolution (not planned at Test
  Strategy time) should be checked against every file that uses the
  convention (`tdd-evidence.yml` *and* `test-strategy.md`), not just the
  file being edited, before choosing a number.

## References

- `docs/rfcs/0008-review-experience-modes.md`
- `.forge/changes/CHG-0050-review-experience-modes/architecture.md` (`DEC-004`)
- `.forge/changes/CHG-0050-review-experience-modes/review.md`
