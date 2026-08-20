---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0019
status: complete
---
# Knowledge Capture — CHG-0019

- **Capturing genuine RED for a packaging-configuration fix required
  temporarily reverting the fix itself, not just reasoning about what
  the old behavior "must have been."** `pyproject.toml`'s dynamic-
  version-sourcing fix (TDD-001) was already implemented before it
  occurred to formally capture RED against the *old* file. Rather than
  assert "the old file obviously wouldn't track `CLI_VERSION`," the
  actual sequence was: `git stash` the fix, change `CLI_VERSION`, build a
  real wheel, observe the stale filename (genuine RED), `git stash pop`
  to restore the fix, rebuild, observe the correct filename (genuine
  GREEN), then revert the temporary `CLI_VERSION` change before
  committing anything. Confirmed afterward, not merely assumed, that no
  commit in this Change's history ever recorded the temporary test value
  (`git log --all -p | grep` returned zero hits). General lesson: when a
  fix is already written before RED is captured, the honest path is to
  temporarily undo it and re-observe, not to narrate what RED "would have
  looked like."

- **A schema-family exclusion list needs to be checked against the
  actual catalog, not against however many pairs happen to be already in
  mind.** The first Specification draft named two non-candidates
  (`forge/change@1`, `forge/adapter-installation@1`) because those were
  the two pairs already discussed in planning research — a third,
  real pair (`forge/policy/review@1`/`@2`) existed in
  `protocol/schemas/catalog.yml` the whole time and was simply not
  re-checked against the full list before drafting FR-003. Found at
  Specification Review by re-deriving the count from the catalog itself
  rather than trusting the running mental list, and turned out to need a
  *third*, structurally different exclusion reason (no live consumer at
  all, confirmed by grep) — not a variant of the other two. General
  lesson: an exhaustiveness claim ("these are the N cases") should be
  checked against the authoritative enumeration (the catalog file) at
  the moment it's written, not against whatever the investigation so far
  happened to surface.

- **Exact string replacement, not YAML re-serialization, is what makes
  "no other byte changes" actually true, not just intended.** The
  migration engine's first design instinct would be to `yaml.safe_load`
  a provenance file, mutate the `schema` key, and `yaml.safe_dump` it
  back — but `safe_dump` does not promise to preserve key order,
  quoting style, or comment placement, so a round-trip through it could
  silently reformat a file whose entire point is to remain untouched
  except one field. Implemented instead as a plain `str.replace` of the
  exact schema string, verified directly against this repository's own
  six real historical files with a line-by-line diff, not just a re-
  validated-schema check. General lesson: "verified schema-valid after
  the change" is a weaker claim than "verified byte-identical except the
  one intended line" — the second is what this Change's own Contract
  rule (C-075) and Specification (FR-003) actually require, and only the
  second was actually tested for.

- **The C-026 per-Iteration freeze-drift signal on `state.current !=
  complete` has now been independently rediscovered a third time**
  (`CHG-0017`'s own knowledge-capture; `CHG-0018`'s Resolution
  Verification R002; this Change's Resolution Verification O002) — each
  time by a genuinely independent Reviewer with no access to the prior
  occurrences, each time correctly diagnosed as the same known,
  intended, self-resolving-at-Completion mechanism rather than a new
  Core defect. Confirmed again here: `state.current: complete` clears it.
  General lesson, now with three independent data points: a `forge
  validate`/`forge doctor` message that named the exemption condition
  explicitly (e.g. "...; this clears once state.current reaches
  complete") would likely stop costing every future Reviewer the same
  investigation — worth a small, low-risk future Change on its own
  (message wording only, no semantic change), not undertaken here since
  it is unrelated to this Change's own declared scope.
