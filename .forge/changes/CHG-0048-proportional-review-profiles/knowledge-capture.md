---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0048
status: complete
---
# Knowledge Capture — CHG-0048

## What Changed

Forge's Review model split from a single, Flow-invariant "Strict Review
adversarial" obligation into three canonical Review Profiles bound to
Flow (`focused`/FAST, `standard`/STANDARD, `strict`/FULL — behaviorally
unchanged). C-022/C-023 were revised, C-031 clarified, four Schemas
gained a `profile` field (three additively, `flow.schema.json`
narrowing `strict`/`adversarial` from `const: true` to plain booleans),
`validation/__init__.py` gained a profile-floor check reusing the
existing `resolve_effective_flow` call site, and both Harness Adapters'
`_gate_instructions()` render a profile-specific completion instruction,
gated on `protocol_id >= 2` — Protocol 1 always sees the fixed
strict-only text, since Protocol 1's Contract has no Review Profile
concept. Authorized by RFC-0007, which formally supersedes RFC-0005 (an
earlier, narrower proposal on the same topic that was never accepted).

## Durable Knowledge

- **Any new per-Flow Adapter-projected text must be gated on
  `protocol_id` the same way the existing Reviewer/Resolver independence
  block already is — this is not obvious from reading the Specification
  or Architecture alone.** Independent Strict Review Iteration 1's R-001
  (BLOCKER) found that the new profile-instruction substitution in both
  `claude_code/projection.py` and `codex/projection.py` was added right
  next to the already-`protocol_id`-gated independence block, but
  without copying that gate — because Protocol 1 and Protocol 2 read the
  *same* canonical Flow files (there is no `protocol/versions/1/flows/`
  directory), any new Flow-content-derived text a future Change adds to
  `_gate_instructions()` will silently apply to Protocol 1 projects too
  unless explicitly gated. **Consequence for future Changes:** when
  adding new per-Flow instruction text to either Adapter's
  `_gate_instructions()`, check whether the new text encodes a
  Protocol-2-only concept (independence, Review Profiles, or anything
  else introduced after Protocol 1 was frozen) and gate it on
  `protocol_id >= 2` explicitly — do not assume "it's right next to a
  gated block" means it inherited the gate.

- **A claimed diff file-count is exactly the kind of self-reported
  number that should be computed, not hand-counted, and this Change
  demonstrates the failure mode twice in the same file.** `verification.md`
  originally claimed 33 files (Iteration 1's OBSERVATION 2: actually 35,
  with a category breakdown that itself summed to 34). The correction
  applied in Resolution claimed 35 (Iteration 2's R-003: actually 36 —
  `discovery.md` was omitted from the Artifacts sub-count). Both errors
  were arithmetic slips in a manually-composed category breakdown, not
  disagreement about which files were in scope — every file in both
  versions of the diff was legitimate. **Consequence for future
  Changes:** when a Verification or Review artifact states a file count
  or category breakdown, generate it from the actual `git diff --stat`
  output (or a script that sums it) rather than composing it by hand and
  asserting it sums correctly — two independent adversarial reviewers
  each caught a hand-arithmetic error in this exact sentence, in two
  consecutive revisions.

- **Superseding a prior RFC that was never accepted is a lighter-weight
  act than amending an accepted one, but still needs an explicit,
  reasoned rebuttal of the superseded RFC's own stated rationale, not
  just a claim that its mechanism was narrower.** RFC-0007's first draft
  distinguished its own (broader) mechanism from RFC-0005's (narrower,
  descriptive-only) one, but never engaged RFC-0005's *epistemic*
  objection — that a calibration pilot was needed before anything
  binding, specifically to avoid an under-calibrated numeric threshold.
  Specification Review's SR-001 caught this gap before Architecture
  began. **Consequence for future Changes:** when a Change's own RFC
  supersedes an earlier one, explicitly address *why* the earlier RFC's
  stated safeguards/objections no longer apply (or still apply and are
  satisfied another way) — distinguishing mechanisms is not the same as
  rebutting the reasoning that produced them.

- **`resolve_effective_flow`'s previously-discarded return value in
  `validate_project` was the correct, already-wired integration point
  for a new per-Flow validation check — no new mechanism was needed.**
  This confirms a general pattern worth remembering for future
  Flow-scoped validation additions in this codebase: `validate_project`
  already resolves the effective (canonical + project-override) Flow for
  every `.forge/flows/*.yml` file it finds, purely to check it *resolves*
  without error; a future Change adding Flow-scoped validation should
  check first whether it can hook into this existing call rather than
  adding a second Flow-resolution pass.

## Consequences for Future Changes

- A future Change introducing a fourth (or configurable) Review Profile,
  or changing what `focused`/`standard` require, should reuse
  `REVIEW_PROFILE_INSTRUCTION` in `review_independence.py` and the
  `protocol_id >= 2` gating pattern established here — do not
  reintroduce per-Adapter duplication.
- `flow.schema.json`, `project-flow.schema.json`, `policy-review-v2.schema.json`,
  and `change-v2.schema.json` are not loaded by any `src/forge_cli`
  runtime code today (confirmed during this Change's Strict Review,
  OBSERVATION 1) — a pre-existing repository pattern, not something this
  Change introduced or is responsible for fixing. A future Change that
  wants Schema-level enforcement of Flow/profile consistency will need
  to actually wire JSON Schema validation into the CLI first; it does
  not exist today despite the Schema files' apparent authority.
- `docs/rfcs/0005-review-cost-proportionality.md` remains in the
  repository, marked `Status: Superseded by RFC-0007`, as historical
  record — its Calibration Pilot idea (observational review-cost data
  collection across 5–10 Changes before any binding threshold) remains a
  legitimate, unclaimed idea for a future, separate RFC that wants to
  add *numeric* calibration on top of the three fixed profiles this
  Change introduces.

## References

- `docs/rfcs/0007-proportional-review-profiles.md` (accepted RFC, includes the resolved Open Normative Question)
- `docs/rfcs/0005-review-cost-proportionality.md` (superseded)
- `protocol/compatibility.md` (`### CHG-0048` entry)
- `.forge/changes/CHG-0048-proportional-review-profiles/review.md` (both Strict Review Iterations)
