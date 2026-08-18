---
forge:
  artifact: review
  schema: 1
change: CHG-0011
status: failed
iteration: 1
---

# Strict Review — Review Convergence Boundary

## Iteration 1 — REQUEST CHANGES

Reviewed revision: `3469d66dbb22765b8beb7d712fb6cefb67454616` (implementation-002, superseding implementation-001 per `provenance.yml`).

Reviewer Execution: `review-exec-chg0011-20260817-932c60cd`.
Reviewer Execution Context: `review-context-chg0011-20260817-932c60cd`.
Assurance: `recorded` (self-recorded repository-native provenance; no cryptographic/external attestation claimed).

This is CHG-0011's own first Strict Review Iteration (`kind: initial_review`), independent in Execution and Execution Context from the Implementation session that produced `implementation-001`/`implementation-002`.

### Verification performed

- `pytest -q` from `/home/isckosta/forge-protocol/.worktrees/chg-0011` (`.venv`): **242 passed**, matching `verification.md`'s claim.
- `forge validate` from the same worktree: exit 2, exactly one finding — `C-026 [.forge/changes/CHG-0008-reviewer-resolver-separation/manifest.yml] C-026 review subject changed after its immutable revision freeze; create new subject provenance.` Independently reproduced on a scratch `git worktree` of `main` at `02cd6899c6b704f0f3a301cc2fd6be54b0b0211c` (pre-CHG-0011): identical single finding, confirming it is pre-existing and not introduced by this Change. `forge doctor`: exit 0, all PASS. The compatibility claim (`AC-012`, `verification.md`) is confirmed.
- `CHG-0008` and `CHG-0010`'s real manifests were re-read directly and confirmed to declare no `kind`/`scope`/`targets`/`convergence` fields; `test_legacy_manifests_are_unaffected` was read and confirmed to assert this against the live repository, not a synthetic fixture.
- The diff `02cd6899..3469d66` was read in full (schemas, Contract, Protocol 2 Specification, review policy, `compatibility.md`, `.forge/forge.yml`, `src/forge_cli/validation/__init__.py`, `tests/unit/test_resolution_verification.py`, `docs/adr/0011-review-convergence-boundary.md`).
- Both TDD-evidence-reported defect fixes (resettable trailing-only convergence counter; Full Review Escalation not blocking on first occurrence) were verified by reading the actual code paths (`_validate_resolution_verification`'s unconditional `full_review_required`-based next-iteration check, and the separate full-history `streaks` scan) rather than trusting the narrative — both are genuinely present and structurally sound in isolation.
- The mechanism was adversarially probed beyond the shipped test suite using three hand-built, real-Git-backed manifests (constructed with the test file's own helper functions, executed against the actual `validate_project`, not mocked). Two of the three probes found genuine defects, detailed below.

### Findings

- **CHG-0011-R001 — BLOCKER — Convergence decision has no binding to the episode it is meant to authorize; a single stale decision can be reused to silently bypass the engineer-decision requirement for later, independent Non-Convergence episodes.**

  `review.convergence.decision` (schema: `change-v2.schema.json`, `{option, reason, recorded_at?}`) and its enforcement in `_validate_resolution_verification` (`src/forge_cli/validation/__init__.py`) carry no episode identifier and no check that `decision.recorded_at` (or any other signal) postdates the specific qualifying iterations of the Non-Convergence episode it is supposed to authorize. The historical-scan loop:

  ```python
  for i,streak_i in enumerate(streaks):
      if streak_i<2 or i+1>=len(its):continue
      nxt=its[i+1]
      if not valid_decision:
          out.append(_finding(...))
      if isinstance(nxt,dict)and nxt.get("kind")=="resolution_verification":
          out.append(_finding(...))
  ```

  checks the *same* manifest-wide `valid_decision` boolean (derived once from whatever `review.convergence.decision` currently holds) against **every** historical index where the Convergence Limit was reached — including ones that occurred *before* that decision was ever written, or ones that occur *later*, after a fresh Resolution → Resolution Verification cycle has independently accumulated its own two-strike streak.

  Reproduced directly against `validate_project` (real Git repository, real commits, using the test module's own fixture helpers, not mocked): a manifest with (1) a first Non-Convergence episode legitimately resolved with a valid `new_full_review` decision and a following `initial_review` Iteration that itself fails with a fresh, unrelated finding, then (2) a **second**, fully independent Resolution → two consecutive `resolution_verification` failures with `new_material_findings: 1` each (a second genuine two-strike streak), then (3) a final `initial_review` Iteration marked `passed`, with `review.convergence.decision` left completely unchanged from episode 1 (same `reason` text describing episode 1, same stale `recorded_at`) — validates with `result.passed == True` and **zero findings**. The second Non-Convergence episode is never flagged as requiring its own decision at all.

  This directly defeats FR-014 ("non-convergence returns authority to the engineer"), the Convergence Policy in Protocol 2 Specification §13, and Contract C-049 ("reaching the applicable Convergence Limit MUST... require an explicit engineering decision before the cycle may continue") for every episode after the first: an engineer (or an agent under pressure to reach `review.status: passed`) can write one decision early in a Change's life and then coast through arbitrarily many subsequent genuine Non-Convergence episodes without ever making a new one. None of the 14 new tests in `tests/unit/test_resolution_verification.py` construct more than one Non-Convergence episode per manifest, so this bypass is entirely unexercised by the shipped test suite.

  This is precisely the class of resettable/bypassable-boundary risk `discovery.md`'s own "Adversarial self-check risk noted for Architecture" section identified for the *counter* (and which was correctly fixed there) — the same risk simply re-appears one field over, in the *decision* record, which received no equivalent anti-reuse binding.

- **CHG-0011-R002 — MAJOR — Specification self-contradiction: AC-009 is false as implemented; the contradiction is untested.**

  `specification.md` AC-009 states: "appending a new `initial_review` Iteration (with or without a decision record) is legal" after Non-Convergence. But FR-012 ("Any Iteration appended after the second such failed Iteration is valid only if both hold: a valid `review.convergence.decision`... is present, and the new Iteration is `kind: initial_review`"), `protocol/versions/2/specification.md` §13 ("A new `initial_review` Iteration remains valid only when `review.convergence.decision` is present..."), and the actual code (the `if not valid_decision:` check in `_validate_resolution_verification`, which does not condition on `nxt.get("kind")`) all agree with each other and disagree with AC-009: a decision is unconditionally required, regardless of the next Iteration's kind.

  Reproduced directly: a real Git-backed manifest appending a fresh `initial_review` Iteration after a legitimate two-strike Non-Convergence episode, with **no** `review.convergence.decision` block at all, is rejected by `validate_project` with finding `"An Iteration exists after the Convergence Limit was reached without a valid review.convergence.decision (option and reason)."` — directly contradicting AC-009's literal text.

  `test_convergence_limit_allows_new_initial_review_after_decision` (the test whose name most closely matches this AC) only exercises the *with-decision* case; no test exercises "initial_review, no decision" at all, so this contradiction passed both `specification-review.md`'s adversarial self-check and the full test suite undetected. Whichever side is correct (AC-009 should be dropped, or FR-012/§13/the implementation should be relaxed to match AC-009), the artifact currently asserts something about its own behavior that is not true.

- **CHG-0011-R003 — MAJOR — Resolution Scope containment can be trivially defeated by an unbounded glob; entirely untested.**

  `_uncovered_paths` matches declared `scope` entries via `fnmatch.fnmatch`, which does not treat `/` as special. Confirmed directly: `fnmatch.fnmatch("protocol/contract/engineering.md", "*") == True`. A Resolution can declare `scope: ["*"]` (or any similarly broad pattern) and thereby have *every* repository path treated as covered, fully defeating Out-of-Scope Mutation detection (FR-005/FR-006, Contract C-048) for that Resolution — a Resolution could rewrite arbitrary, unrelated parts of the repository and still be mechanically "in scope."

  Neither FR-003 nor the schema addition (`execution-provenance.schema.json`'s `scope`: `{"type":"array","minItems":1,"items":{"type":"string","minLength":1}}`) impose any minimum-specificity constraint on declared scope entries, and none of the 14 new tests exercise glob-based scope at all — every test in `tests/unit/test_resolution_verification.py` uses exact literal paths (e.g. `["src/x.py"]`, `["src/feature.py"]`). FR-003 explicitly permits "`fnmatch`-style path globs," so this is a documented capability of the mechanism, shipped with zero test coverage of the one case (a broad/degenerate glob) that would demonstrate whether it can be gamed. This is exactly the scenario this review was directed to check ("Can Resolution Scope be declared so broadly it defeats the purpose?"), and the answer is yes, mechanically, today.

- **CHG-0011-R004 — MINOR — FR-013's evidentiary requirement is asserted but not mechanically enforced.**

  `specification.md` FR-013 states that when `new_material_findings > 0`, "the Iteration's `evidence_gap` (or `review.md`) MUST identify at least that many class B/C Findings with IDs," and `architecture.md`'s validator-changes step 8 characterizes the check as "consistent (`>0` implies at least one B/C class recorded)." The actual implementation only checks that `new_material_findings` is a non-negative integer; `finding_classes` and `evidence_gap` content are never read by `_validate_resolution_verification` (confirmed: neither identifier appears anywhere in `src/forge_cli/validation/__init__.py`). A manifest can declare `new_material_findings: 3` with `finding_classes` absent or set to `unrelated_latent_finding` and no matching evidence, and no finding results. This mirrors the pre-existing, already-accepted trust boundary for self-declared blocker/major/minor counts elsewhere in Protocol 2 (so it is not a novel weakening this Change introduces), but the Specification's own text overstates what is actually mechanically checked.

- **CHG-0011-R005 — OBSERVATION — A recurring, never-fixed class-A finding is not bounded by this mechanism at all, by explicit design.**

  Per FR-011 and `test_recurring_unresolved_finding_does_not_increment_convergence` (TDD-014), a Resolution that repeatedly fails to fix its own target Finding (the *same* Finding recurring, class A) never increments the derived convergence counter, so such a cycle can repeat indefinitely without ever reaching `review_convergence_failed`. This is honestly disclosed as an intentional scope narrowing in `test-strategy.md` (TDD-014) and `specification.md` (FR-011's rationale), not a hidden defect, but it is worth naming explicitly against `intent.md`'s framing of the problem ("no repository-native boundary preventing a 6th, 7th, or Nth... re-audit") — the boundary shipped here does not, in fact, bound that specific recurrence pattern.

### Assessment against the Change's own declared terms

- The mechanism's happy path (FR-001–FR-010, out-of-scope detection with literal paths, Full-Review-Escalation-on-first-occurrence, the counter's derived-not-declared property for the *first* episode) is correctly implemented and its two self-reported TDD defect fixes are real, verified by reading the code directly.
- Reviewer/Resolver independence, freeze, and provenance-authority invariants (Protocol 2 §2–§8 / CHG-0008) are unaffected: `_validate_resolution_verification` is appended after, never in place of, the existing checks, confirmed by direct reading of the diff.
- Scope discipline is otherwise respected: no `forge/decision@1` schema, no general Decision Gate, no CLI subcommand, no delegation semantics were introduced; the diff matches `architecture.md`'s "what this Change deliberately does not build."
- However, the Change's headline claim — that Non-Convergence "MUST" require "an explicit engineering decision" before the cycle may continue (Intent Required Outcome 4, FR-014, C-049) — is not true in general; it is true only for a manifest's *first* Non-Convergence episode. This is a correctness defect in the mechanism the Change exists to build, not a documentation nit, and it is compounded by an internal specification contradiction (R002) and an untested containment bypass (R003) in the same review surface the review brief specifically asked to probe.

### Verdict

**REQUEST CHANGES**

Finding counts:

- BLOCKER: 1 (CHG-0011-R001)
- MAJOR: 2 (CHG-0011-R002, CHG-0011-R003)
- MINOR: 1 (CHG-0011-R004)
- OBSERVATION: 1 (CHG-0011-R005)

Per C-027, Completion MUST NOT proceed with an unresolved BLOCKER or MAJOR finding present. A Resolution addressing R001–R003 (R004/R005 at the Resolver's discretion, though R004 should be corrected or at minimum acknowledged) is required before the next Strict Review Iteration.
