---
forge:
  artifact: specification_review
  schema: 1
change: CHG-0045
status: complete
---

# Adversarial Specification Review — CHG-0045

**Verdict: PASS (three findings, all resolved in the same authoring
session).**

Per `protocol/flows/full.yml`'s `specification_review` Gate
(`mode: adversarial`), this Review actively searched for self-
authorization loopholes, overpromised automation, fragmented-requirement
gaps, and unverified coverage claims — the failure modes this Gate exists
to catch — rather than re-reading the Specification for style. This
Review ran in the same session/Execution/Context that authored the
Specification; per `protocol/versions/2/specification.md`, Protocol 2's
independent-Execution/Context requirement (C-026) binds Strict Review
only, not Specification Review, so this is conforming, not self-review of
a Gate that requires independence.

## Findings

### SR-001 (MAJOR) — NFR-001 implied automatic derivation that does not exist
**Found:** The original NFR-001 required the shared independence-text
module to "derive its content from... C-026's actual text," but no
mechanism exists anywhere in this codebase to mechanically derive English
operational prose from Contract paragraph text (unlike Flow YAML → gate
names, which is genuinely structured data — Discovery). As written, FR-002
would have been unimplementable as specified, or implemented as a
disguised piece of "hidden automation" F-010 explicitly disfavors.
**Resolution:** NFR-001 rewritten to require a single shared, still
hand-authored rendering, checked by a test asserting agreement on specific
mechanically-checkable claims rather than full derivation. Applied
directly to `specification.md`.

### SR-002 (MAJOR) — FR-001's acceptance criterion did not prevent a "collapsed but orphaned" outcome
**Found:** AC-004 as originally written only asserted the independence
block appears exactly once — a generator could satisfy that literally by
moving the block to an unrelated location no Flow section points to,
technically de-duplicating the string while making the FAST-flow reader
unaware the requirement applies to FAST at all. This would satisfy the
letter of FR-001 while defeating US-003's actual goal (self-review cannot
be recorded as Strict Review under any Flow).
**Resolution:** AC-004 extended to require each applicable per-Flow
section to carry an explicit pointer to the single shared section. Applied
directly to `specification.md`.

### SR-003 (MINOR) — FR-006's Boundary implicitly asserted subagent and non-listed-tool coverage
**Found:** The original Boundary text named only "Codex parity" as
explicitly out of scope, which by omission read as if Bash/Edit/Write
coverage inside a subagent's own tool calls, and coverage of any other
mutation-capable tool (MCP filesystem tools, `NotebookEdit`), were settled
or irrelevant. Neither was verified during Discovery. Representing
untested coverage as covered-by-omission would itself violate the honesty
posture (C-073-adjacent) this Change is trying to strengthen.
**Resolution:** Boundary text extended to name both gaps explicitly and
require the Change to state, not assume, whichever way verification comes
out. Applied directly to `specification.md`.

## Checked and found sound

- Every FR traces to a specific Discovery citation or governing-prompt
  section; none introduces content beyond what Discovery evidenced.
- CON-001–CON-004 do not conflict with any FR (no FR requires a new
  Protocol identifier, a paraphrase of Contract text, harness-specific
  leakage into shared modules, or a premature plugin system).
- The Self-Hosting Boundary section does not attempt to grant this
  Change's own future output authority over this Change's own governance
  — checked specifically for the circular-authority failure mode C-062
  targets, by construction rather than by generic disclaimer.
- Out of Scope explicitly defers the Codex-guard-parity and centralized-
  `forge internal guard-check` questions rather than silently deciding
  them, consistent with the governing prompt's Decision Discipline
  (§41): neither is Contract/Product-class (human-authority) nor
  incidental — they are legitimately deferred to a materially separate
  Change or to Architecture's recorded, agent-reviewable rationale.

## Conclusion

Three defects found and resolved before Architecture. Specification is
internally consistent, each FR has verifiable Acceptance, and no finding
required an Unresolved Decision escalation (all were resolvable by
tightening the Specification's own wording, not by an unresolved question
needing evidence this Review couldn't produce). Proceeds to Architecture.
