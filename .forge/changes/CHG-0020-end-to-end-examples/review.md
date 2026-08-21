---
forge:
  artifact: review
  schema: 1
change: CHG-0020
status: passed
---
# Strict Review — CHG-0020

## Verdict

**PASS (Iteration 1, `kind: initial_review`).** No BLOCKER, MAJOR, MINOR, or
OBSERVATION Findings.

This Change's declared central risk (`specification.md` CON-001: "every
commit hash, Finding ID, and quoted excerpt ... checked against real `git
show`/file content before Verification, not reconstructed from memory") is
the one this Review treated as requiring the most scrutiny, precisely
because a curation-only Change's entire value proposition is citation
accuracy, and a plausible-sounding paraphrase is the failure mode hardest to
catch by skimming. Every commit hash cited by both new READMEs, the
Finding data quoted from `CHG-0016`'s real `review.md`, and the claims about
`CHG-0018`'s Core fixes, its dogfooded bug-catch, and its own R001 Finding
were independently re-checked against the actual cited sources, not accepted
from `verification.md`'s own account of having done so. All of it holds.

## Summary

| Severity | Count |
| --- | --- |
| BLOCKER | 0 |
| MAJOR | 0 |
| MINOR | 0 |
| OBSERVATION | 0 |

## Review Subject

Frozen Implementation subject `9f643c313368558afd07e1dd17d3a47eadc4d0c7`
(`provenance.yml`, record `implementation-001`), reviewed against the
Change's own pre-Implementation baseline `d35ecab` (this Change's own
Intent/Discovery/Specification/Plan/Tasks commit). The later commit
`349bec4` (implementation-role provenance recording, and `manifest.yml`'s
`provenance` field flipping to `complete`) is Change-local review-control
metadata, exempt from the freeze per Protocol 2 §5 and this repository's
own established convention (`CHG-0014`/`CHG-0017`/`CHG-0018` precedent), and
was not treated as part of the reviewed diff.

## Review Execution Independence

This Review was executed in an Execution and Execution Context distinct
from the Implementation session that produced `implementation-001`, per
Contract C-026 and Protocol 2 §2 (`protocol/versions/2/specification.md`
§2). It was performed cold, from repository state alone, with no access to
the Implementation conversation and no prior memory of this Change beyond
the committed Artifacts and diff state. Every citation was re-checked
directly against `git log`/`git show`/file content; no claim in
`verification.md`, `knowledge-capture.md`, or any commit message was
accepted without independent reproduction. See `provenance.yml` record
`review-001` for this execution's own self-recorded provenance and honest
assurance statement.

## Iteration 1 — PASS

No Findings raised.

## Checked and found sound (no defect)

Recorded explicitly so a Resolver (or, since there is nothing to resolve, a
future reader) knows what was actually exercised, not merely skimmed.

- **All nine commit hashes cited in `examples/strict-review-remediation/README.md`**
  (`bf69393`, `70478ae`, `e50d3c5`, `f7829d9`, `6d6e2c7`, `848adc9`,
  `67766d3`, `856e6a4`, `85c8ce0`) — each independently confirmed via `git
  log -1 --format="%h %s" <sha>` to exist with exactly the quoted subject
  line, byte for byte.
- **All thirteen commit hashes cited in `examples/full-feature/README.md`**
  (`723efd9`, `35fbb48`, `4f676b9`, `4531b8f`, `9b23c41`, `e5579ec`,
  `6214390`, `b192824`, `3d954dd`, `7385799`, `75e3678`, `511f901`,
  `d489f1b`) — same check, same result: all exist, all subject lines match
  exactly.
- **`CHG-0016`'s real `review.md`, read in full and checked against the
  README's paraphrase.** The Summary table (`BLOCKER 1 / MAJOR 2 / MINOR 6 /
  OBSERVATION 3` raised in Iteration 1) matches `review.md`'s own table
  exactly. The R012 (BLOCKER — `src/forge_cli/validation/__init__.py:320`
  accepting only `forge/execution-provenance@1`), R001 (MAJOR —
  `traceability.yml` asserting NFR-002 held when the shipped file violated
  it), and R002 (MAJOR — the new guidance omitting the `forge:` frontmatter
  convention) descriptions in the README are accurate on every substantive
  point — file, line, defect, severity — not merely plausible-sounding.
  The README's own disclosure that it surfaces only 3 of 12 Findings, and
  points at `review.md` for the rest, is honest; it does not imply
  completeness it does not have.
- **`CHG-0018`'s real `verification.md` and `review.md`, read in full and
  checked against `examples/full-feature/README.md`'s claims.** The two
  Core-leak fixes (`.codex` hardcoding in the generic `adapters/*.py`
  surface; misfiled generic invariant-assessment logic), the new Claude
  Code Adapter, and the FULL classification rationale (Core + Contract +
  schema + executable surface, matching `CHG-0013`/`0015`/`0016`/`0017`
  precedent) all check out against `review.md`'s "Checked and found sound"
  section. Independently confirmed the schema claim specifically:
  `git diff 723efd9^..d489f1b --stat -- protocol/schemas/adapter-configuration.schema.json`
  shows the file genuinely changed (1 insertion, 1 deletion) within
  `CHG-0018`'s range, matching the README's "a Protocol schema
  (`adapter-configuration.schema.json`)" claim.
- **The `greet(None)` regression, checked against `verification.md`'s Layer
  C section.** `verification.md` records the scratch session's own spawned
  subagent finding "a real **MAJOR** finding (R001): `if not name.strip():`
  regressed `greet(None)` from `ValueError` to `AttributeError`" — matching
  the README's paraphrase exactly, including severity (MAJOR) and the
  specific exception-type regression.
- **The hook-pattern MINOR, checked against `CHG-0018`'s own real
  `review.md` `### R001` section.** `review.md` records: "R001 — MINOR —
  The `PreToolUse` hook's substring matching denies plausible, legitimate
  compound Git commands" — resolved in `7385799`, confirmed by Iteration 2
  (`511f901`). The README's characterization ("a hook pattern-matching
  false positive on compound Git commands," resolved in `7385799`,
  confirmed by `511f901`) matches exactly.
- **No conflation between the two distinct "R001" labels.** `CHG-0018`'s
  own `review.md` R001 (hook pattern-matching MINOR, against `CHG-0018`'s
  own Implementation subject) and the *scratch session's own* `review.md`
  R001 (the `greet(None)` regression MAJOR, recorded inside that scratch
  repository's own `.forge/changes/CHG-0001-.../review.md`, a different
  Change's own Finding numbering entirely) are two independently-numbered
  Findings in two different provenance trees that happen to share a label.
  `examples/full-feature/README.md`'s own text never uses the label "R001"
  for the `greet(None)` bug — it names the bug by its behavior
  (`ValueError` → `AttributeError`) and separately, later, uses "R001"
  only for `CHG-0018`'s own hook finding — so the two are kept distinct in
  the deliverable text itself. `knowledge-capture.md`'s own account of
  this exact risk is accurate, not merely asserted.
- **`examples/README.md`'s mapping table.** All five ROADMAP-named
  categories (`fast-bugfix`, `standard-feature`, `full-feature`,
  `strict-review-remediation`, `codex-adapter-project`) are present, each
  pointing at a directory that exists
  (`ls examples/`: `canonical-artifacts`, `full-feature`,
  `golden-path-claude-code`, `golden-path-standard`,
  `strict-review-remediation`, plus `README.md`) and actually contains what
  is claimed (spot-checked each target README's content against the
  table's one-line description).
- **The two golden-path README addenda, diffed against their
  pre-Implementation state (`d35ecab`).** `git diff d35ecab --
  examples/golden-path-claude-code/README.md` and the same for
  `golden-path-standard/README.md` each show exactly one new paragraph
  inserted (5 and 6 added lines respectively), with every surrounding line
  unchanged. No other content in either file was touched.
- **`ROADMAP.md`'s new status line.** Names what is satisfied (the five
  `examples/` categories, via `CHG-0020`, citing `CHG-0016`/`CHG-0018`) and
  explicitly states "the External validation matrix below remains entirely
  open: no real target repository exists in any ecosystem other than this
  one" — not silently dropped.
- **No historical Change's own artifacts were modified.** `git log
  --oneline -- .forge/changes/CHG-0016-canonical-artifact-structure/` and
  the same for `CHG-0018-second-harness-adapter-claude-code/` show no
  commit after each Change's own Completion (`85c8ce0`, `d489f1b`
  respectively) touching those directories — `CHG-0020`'s own commits do
  not appear in either list.
- **Test suite, reproduced independently.** `python -m pytest -q` →
  **524 passed**, matching the claimed figure exactly. `forge validate` →
  "Forge project is valid", exit 0. `forge doctor` → all checks PASS
  except the pre-existing, unrelated `migration_available` WARN (6 real
  `forge/execution-provenance@1` migration candidates, a `CHG-0019`
  finding this Change does not touch or change) — matching
  `verification.md`'s own account exactly.
- **`git diff --stat d35ecab..9f643c3`** touches exactly the five Markdown
  deliverables plus this Change's own `.forge/changes/CHG-0020-.../`
  artifacts — no code, Contract, or schema file. Matches the STANDARD
  classification and CON-003's historical-validity constraint.

## Conclusion

No BLOCKER, MAJOR, MINOR, or OBSERVATION Finding. Every commit hash, Finding
excerpt, and factual claim this Review spot-checked in
`examples/strict-review-remediation/README.md` and
`examples/full-feature/README.md` matches its cited real source exactly —
not a paraphrase that drifts from it, not a plausible-sounding
reconstruction. The two golden-path addenda are genuinely additive. The
mapping table and `ROADMAP.md` status line are both accurate and complete.
No historical Change's own artifacts were touched, and the full test
suite, `forge validate`, and `forge doctor` are unchanged. This Change is
**PASS** and may proceed toward Completion.

**PASS.**
