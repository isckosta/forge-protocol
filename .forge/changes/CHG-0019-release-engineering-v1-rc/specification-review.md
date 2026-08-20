# Specification Review — Release Engineering & v1 Release Candidate (Infrastructure)

## Verdict

**APPROVED, with 1 MINOR finding resolved in place.** No BLOCKER or MAJOR.
Specification proceeds to Architecture.

## Findings

### SR-001 — MINOR — FR-003's exclusion list missed a fourth real schema-version pair

**Finding**: The first draft of FR-003 named only two explicit
non-candidates (`forge/change@*`, `forge/adapter-installation@*`), but
`protocol/schemas/catalog.yml` lists **four** families with more than one
version, not two — `forge/policy/review@1`/`@2` is also a real pair, and
the first draft simply didn't check for it.

**Checked during this Review**: read both `policy-review.schema.json`
files directly (a real, non-superset content difference — Protocol 2
requires nine new `reviewer_resolver_separation`/`re_review` sub-keys a
`@1` instance lacks) and, more importantly, grepped
`src/forge_cli/` for any reader/validator of `.forge/policies/review.yml`
against either schema — none exists. This repository's own copy of that
file still declares `@1` under a `protocol: 2` project, and nothing
currently notices or cares. This is not a live bug this Change needs to
fix (nothing consumes the file, so nothing is broken by its version
lagging) — it is a genuinely different kind of non-candidate than the
other two (not "needs input," but "no live consumer exists to migrate
for"), and worth stating precisely rather than folding into the same
reasoning as the other exclusions.

**Resolution applied**: FR-003 and `discovery.md` both amended to name
and correctly reason about all three non-candidates, not two.

## Checked and found sound

- FR-002/FR-003's chosen candidate (`execution-provenance@1`→`@2`) is
  re-verified as the only pair that is both a real, live, superset case:
  read the full schema diff directly (role enum, `execution.delegated_by`,
  `baseline`, relaxed `scope.minItems`) and confirmed every non-
  `delegated_task` field is unaffected.
- C-075's wording deliberately generalizes CHG-0007's own real precedent
  (checked directly: `CHG-0007/architecture.md`'s "Historical migration"
  section and `knowledge-capture.md`'s "cannot be reconstructed" language)
  rather than inventing a new principle.
- AC-002's exact count ("six real `@1` provenance files") matches
  `CHG-0008`, `CHG-0011`–`CHG-0015` — confirmed by listing
  `.forge/changes/*/provenance.yml` and grepping each `schema:` line.
- INV-001 (RELEASING.md references, doesn't restate, compatibility.md) is
  checked against the drafted FR-008 wording — no duplicated normative
  text planned.

## Conclusion

One MINOR finding, resolved without reopening Discovery. Specification is
APPROVED and proceeds to Architecture.
