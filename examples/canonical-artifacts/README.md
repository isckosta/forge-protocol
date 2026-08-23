# Canonical Artifact Examples

Two annotated Artifacts demonstrating `protocol/artifact-structure.md`
(CHG-0016), specifically the Result-Before-Evidence recommendation for
Verification and Review — the one concrete regression Discovery found
between `CHG-0001` and `CHG-0015` in this repository's own history.

These are illustrative, not a real Change: they use a fictional
`CHG-EXAMPLE` identifier and describe a small, invented bugfix so the
structure is legible without requiring familiarity with this
repository's actual history. They are not reformatted copies of any real
historical Change (`protocol/artifact-structure.md` §1 and the
originating Discovery both call out mass-reformatting historical Changes
as out of scope).

Annotations are HTML comments (`<!-- ... -->`), invisible when the file
renders as Markdown, each naming the `protocol/artifact-structure.md`
principle or per-type recommendation the section beneath it demonstrates.

`intent.md` is the representative business Change example. It demonstrates
the structured Intent layout, including conditional sections, while
`intent-technical.md` shows that the same layout also works for a technical
reliability Change without inventing business metadata.

- `verification.md` — `## Result` first, per §4 "Verification".
- `review.md` — aggregate `## Verdict` first, existing per-iteration
  convention preserved beneath it, per §4 "Review".
