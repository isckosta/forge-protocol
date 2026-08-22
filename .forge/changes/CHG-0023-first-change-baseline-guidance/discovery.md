---
forge:
  artifact: discovery
  schema: 1
change: CHG-0023
status: active
---

# Discovery — First-Change Baseline Guidance

## Executive Summary / Recommendation

**Recommendation: Option A — the Engineering Contract. Confidence: High.**
The rule governs the validity of a Change's before/after evidence and is
therefore a provider-independent lifecycle invariant, not merely a helpful
Adapter phrasing. It belongs beside C-001 (Intent), C-002 (classification),
C-007 (Specification before behavior), and C-009/C-010 (test before and
observed RED). The Contract change requires an RFC before Specification,
as mandated by `CONTRIBUTING.md`; both Adapter workflows should then project
the canonical wording by reference.

## The observed gap

The external first-commit Change described by
`ROADMAP-REMEDIATION.md` had no prior Git commit to serve as a baseline. Its
ad hoc baseline omitted files that the Change later modified, so the review
diff falsely represented those pre-existing files as entirely new. The
repository's current Contract has no rule naming the first-commit case, and
the two packaged workflow resources only say that repository-native state is
authoritative and that Flow gates must be preserved:

- `src/forge_cli/adapters/codex/resources/skills/workflow.md` contains the
  effective-Flow/Contract framing and TDD/Strict Review reminders, but no
  baseline procedure.
- `src/forge_cli/adapters/claude_code/resources/skills/workflow.md` has the
  same content byte-for-byte and the same omission.

## Option A — Engineering Contract

Existing Contract rules establish process invariants rather than Harness
mechanics. C-001 and C-002 require Intent and classification before work;
C-007 forbids behavioral Implementation before Specification; C-009 and
C-010 require an executable test and observed RED before production
behavior; C-020, C-022, and C-028 require Verification, Review, and
Documentation Impact. These rules remain meaningful regardless of the
Harness, Git provider, or CLI. A complete first-commit baseline has the same
shape: it is a precondition for trustworthy Change evidence, not a command
that one Harness may interpret differently.

The Contract is the right normative home, but it must not pretend to enforce
filesystem or Git behavior. As with Adapter limitations elsewhere, the rule
can require the repository state and evidence; the Harness can only project
the instruction. The proposed RFC will define the exact boundary: before
Implementation in a repository with no prior commit, commit the complete
pre-existing state, including every file present in the intended repository
scope, with no exclusions. The baseline commit itself is not Change
Implementation.

`CONTRIBUTING.md` explicitly requires an RFC before materially changing the
Engineering Contract. `docs/rfcs/0001-forge-core-protocol.md` and
`docs/rfcs/0002-harness-adapter-foundation.md` establish the real RFC shape:
Summary, Motivation, Decision, relevant protocol consequences, Alternatives
rejected, and Future work.

## Option B — Adapter-projected guidance only

This option would add the rule only to each Adapter's packaged
`resources/skills/workflow.md`, where it would reach `SKILL.md`/the Codex
skill projection. It needs no RFC and is operationally easy, but it would be
non-binding guidance: a future Adapter, or a consumer that reads only the
canonical Contract, could omit it without violating the stated Contract.
The duplicate template also creates two maintenance points for a rule whose
meaning should be Harness-independent. The current resources are appropriate
for stable framing and reminders, not for defining a new lifecycle
precondition.

## Decision boundary and compatibility

Option A is recommended despite its additional RFC gate because the failure
mode is semantic evidence corruption, not merely user friction. The change
is additive: existing repositories with prior commits retain their current
baseline workflow, and first-commit Changes gain an explicit prerequisite.
No schema field, Flow identifier, CLI behavior, or Adapter activation state
is needed. The Contract's existing provider-independence and Adapter
projection boundaries remain intact. If RFC review rejects canonical
placement, the Specification must return to Option B rather than silently
mutating the requirement.

## Flow Classification Finding

**FULL.** Option A materially changes the canonical Engineering Contract.
`protocol/flows/full.yml` is the appropriate high-rigor path for a
high-impact public contract/process invariant, while
`protocol/flows/standard.yml` lacks the required adversarial
`specification_review` stage. FAST is disqualified by the semantic impact,
even though the final line count may be small: the work changes a canonical
Contract, adds an RFC, and changes guidance consumed by both Adapters. This
is not a new security, persistence, or schema feature, but it is a
cross-implementation lifecycle rule whose correctness depends on precise
scope and compatibility analysis.

## Documentation Impact Signal

Required updates are `docs/rfcs/NNNN-*.md`,
`protocol/contract/engineering.md`, both Adapter workflow resources,
`examples/` (with a README mapping entry if the demonstration is a new
category), and the item #3 status/link in `ROADMAP-REMEDIATION.md`. No
schema or CLI update is expected. Knowledge Capture should preserve the
distinction between a complete baseline and an Implementation commit for
future first-commit Changes.

## Baseline

The current branch is `chg-0023-first-change-baseline-guidance`, created from
the repository's active CHG-0022 worktree. Existing CHG-0022 files and
untracked files remain untouched and are not part of this Change's scope.
