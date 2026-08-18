---
forge:
  artifact: review
  schema: 1
change: CHG-0011
status: passed
iteration: 2
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

## Iteration 2 — PASS

Reviewed revision: `chg-0011-resolution-001`, `e52000fd8f50a12096c043d454822483e2977e31` (subject provenance `resolution-001`, `role: resolution`, `targets: [CHG-0011-R001, CHG-0011-R002, CHG-0011-R003, CHG-0011-R004]`).

Reviewer Execution: `review-exec-chg0011-20260818-4f2a19be`.
Reviewer Execution Context: `review-context-chg0011-20260818-4f2a19be`.
Assurance: `recorded` (self-recorded repository-native provenance; no cryptographic/external attestation claimed).

This is CHG-0011's own second Strict Review Iteration, classified `kind: resolution_verification` — it is a review of `resolution-001`, the Resolution that addressed Strict Review Iteration 1's R001–R004. Its authority is bounded, per this Change's own `specification.md` (Finding taxonomy, FR-007–FR-009), to: (a) whether R001–R004 were actually fixed; (b) resolution regressions (class B) inside the Resolution's own delta; (c) Out-of-Scope Mutation (class C) against the declared `resolution-001` scope; (d) provenance/revision/subject correctness for this Iteration. This section applies that bounded authority to itself, not an unrestricted Initial Review re-audit of the whole CHG-0011 diff.

### Resolution Delta computed independently

`git diff --name-status 3469d66dbb22765b8beb7d712fb6cefb67454616..e52000fd8f50a12096c043d454822483e2977e31` (computed directly, not trusted from any artifact) yields 12 changed paths:

```
M  .forge/changes/CHG-0011-review-convergence-boundary/architecture.md
M  .forge/changes/CHG-0011-review-convergence-boundary/knowledge-capture.md
M  .forge/changes/CHG-0011-review-convergence-boundary/provenance.yml
A  .forge/changes/CHG-0011-review-convergence-boundary/specification-drift.md
M  .forge/changes/CHG-0011-review-convergence-boundary/specification.md
M  .forge/changes/CHG-0011-review-convergence-boundary/tasks.md
M  .forge/changes/CHG-0011-review-convergence-boundary/tdd-evidence.yml
M  .forge/changes/CHG-0011-review-convergence-boundary/traceability.yml
M  protocol/schemas/change-v2.schema.json
M  protocol/versions/2/specification.md
M  src/forge_cli/validation/__init__.py
M  tests/unit/test_resolution_verification.py
```

`provenance.yml` is excluded from the Resolution Delta by this Change's own FR-004 (review-control metadata exception: `manifest.yml`/`provenance.yml`/`review.md`). The remaining 11 paths match `resolution-001`'s declared `scope` list exactly — 11 declared, 11 present, one-to-one. `manifest.yml` and `review.md` were not touched by the Resolution commit (consistent with FR-004). **No Out-of-Scope Mutation (class C) found**; declared scope was accurate, not just broad-enough-to-pass.

### R001 (BLOCKER) — verified fixed, adversarially probed

Read the actual diff of `_validate_resolution_verification` in `src/forge_cli/validation/__init__.py`. The fix moves the decision from a single manifest-wide `review.convergence.decision` field to `iterations[i+1].convergence_decision`, read fresh inside the historical-scan loop (`decision=nxt.get("convergence_decision")`) for **every** index `i` where `streaks[i]>=2`, rather than once from a shared field. The schema (`protocol/schemas/change-v2.schema.json`) was correspondingly changed: `review.convergence.decision` was removed entirely (not left as inert legacy), and `convergence_decision` was added as a per-Iteration property.

Verification performed beyond reading the diff:
- Ran the Resolver's own new regression test, `test_convergence_decision_cannot_be_reused_across_independent_episodes`, which reproduces the exact scenario from Iteration 1's R001 finding (episode 1 resolved with a valid decision + a failing follow-on `initial_review`, then an independent episode 2 two-strike streak, then a final `passed` `initial_review` with no decision of its own) — it now fails validation as required.
- Constructed my own additional adversarial scenario, independent of the shipped test suite, using `test_resolution_verification.py`'s own helper functions against the real `validate_project` (real Git-backed manifests, not mocked): a **plateaued** streak (4 consecutive `resolution_verification` failures with `new_material_findings: 1`, never interrupted by a genuine `initial_review`) followed by a `passed` `initial_review` carrying no decision anywhere. This probes whether the per-index historical scan could be tricked by streak overlap/aliasing (i.e., whether one `i+1` index could be claimed by two different streak positions). Result: correctly rejected, with the redundant-but-safe "further resolution_verification Iteration is not valid" finding firing at every intermediate index and the "requires its own valid convergence_decision" finding firing at the terminal index. No bypass found; the mechanism fails closed, never open, under streak plateau.
- Confirmed each streak index `i` maps to a distinct `i+1` (array positions are unique per `i`), so aliasing/reuse across two different episodes' authorizing Iterations is structurally impossible now that committed Iterations are immutable (Protocol 2/CHG-0008 freeze) and the decision lives on the Iteration itself rather than a shared field.

R001 is genuinely closed. `AC-015` is satisfied.

### R003 (MAJOR) — verified fixed, adversarially probed

`fnmatch` was removed from the import list and from `_uncovered_paths`, which now does plain set membership (`p not in patterns`) with no pattern interpretation at all.

Verification performed beyond reading the diff: ran `_uncovered_paths` directly (not just via `validate_project`) against a battery of path-matching tricks beyond the shipped `scope: ["*"]` regression test — `scope: ["src/*"]`, a leading `./src/x.py`, a doubled slash `src//x.py`, a trailing slash `src/x.py/`, and a case variant `SRC/X.PY` against an actual delta path `src/x.py`. Every one of these was correctly treated as **uncovered** (fails closed — the trick never causes a real out-of-scope path to be mistaken as covered; at worst a legitimately-covered path could be mis-declared and flagged as uncovered, which forces escalation, not a bypass). No path-normalization or case-sensitivity bypass exists in the exact-match implementation. `AC-016` is satisfied.

### R002 (MAJOR) — verified fixed, genuinely consistent

`specification.md` AC-009 was retracted and replaced (not reworded around the contradiction): it now states a decision is unconditionally required on `iterations[i+1]` regardless of that Iteration's `kind`, matching FR-012, `protocol/versions/2/specification.md` §13 (both updated in this Resolution's diff, read directly), and the actual code (`if not valid_decision: out.append(...)` is unconditional — it does not branch on `nxt.get("kind")`). Cross-checked against the shipped test `test_convergence_limit_blocks_further_resolution_verification_without_decision` (asserts rejection of a `resolution_verification` at `i+1` with no decision) and `test_convergence_limit_allows_new_initial_review_after_decision` (asserts acceptance of `initial_review` at `i+1` *with* a decision) — no test exercises "initial_review, no decision" as a positive case, consistent with the corrected AC-009's claim that this case is now rejected, not permitted. No remaining self-contradiction found between AC-009, FR-012, §13, and the implementation.

### R004 (MINOR) — verified fixed

`specification.md` FR-013 now states plainly that Core does not read `finding_classes`/`evidence_gap` content, only requires `new_material_findings` to be present/well-typed — matching the actual code (`finding_classes` and `evidence_gap` do not appear anywhere in `src/forge_cli/validation/__init__.py`, confirmed by direct search). One imprecision noted but not treated as a defect: Iteration 1's finding text quoted `architecture.md`'s validator-changes step 8 as characterizing the check as "consistent (`>0` implies at least one B/C class recorded)" — that exact phrase is not literally present in `architecture.md` at either the pre- or post-Resolution commit (checked directly); step 8's actual text was already accurate (it only ever described the `new_material_findings` well-typedness check, not content cross-checking) and was left unchanged by this Resolution. This does not affect the verdict: FR-013's specification text (the actual overstatement Iteration 1 identified and evidenced with a reproduction) is corrected and now matches code; the `architecture.md` quote imprecision is an artifact of how Iteration 1's finding text was phrased, not a live inconsistency in the current repository.

### Class D (unrelated latent) note

While reading `_validate_resolution_verification` for this verification, no new pre-existing-but-unrelated defect was noticed beyond what Iteration 1 already recorded (R005, OBSERVATION, accepted by design and correctly left unresolved by this Resolution — `specification-drift.md` records it as "not resolved by design," which is itself the correct disposition for an accepted-scope-narrowing OBSERVATION, not a lapse). No class D finding is raised in this Iteration.

### Verification performed

- `pytest -q` from `/home/isckosta/forge-protocol/.worktrees/chg-0011` (`.venv`): **244 passed**, matching `verification.md`/`resolution-001`'s claim, independently reproduced.
- `forge validate` from the same worktree: exit 2, exactly one finding — the same pre-existing `C-026` CHG-0008 freeze finding Iteration 1 already independently confirmed as pre-existing and unrelated to CHG-0011. No new finding introduced by this Resolution's changes. `AC-014` is satisfied for the Resolution subject.
- Full `git diff --name-status` Resolution Delta computed directly (above) and cross-checked against `resolution-001`'s declared `scope`, not trusted blindly (per this Iteration's own required task (c)).

### Was the Resolution-Verification framing meaningfully constrained relative to an unrestricted re-audit?

Yes, materially. Concretely, this Iteration did **not**: re-read or re-adjudicate the happy-path FR-001–FR-010 mechanics already assessed in Iteration 1 (only the R001/R003 code paths that actually changed were re-read line-by-line); re-run the full adversarial probing Iteration 1 did against the pre-Resolution code (out-of-scope containment happy path, Full Review Escalation, etc.) since none of that was touched by this delta; or treat R005 (OBSERVATION, explicitly left unresolved by design) as blocking, which an unrestricted re-audit applying Intent's framing fresh might have been tempted to revisit. The scope boundary in practice meant: read the 11-path delta in full (all of it — none of the 11 files is large), verify each of R001–R004's fixes against the specific lines Iteration 1 cited, and adversarially re-probe only the two mechanisms (`convergence_decision` binding, `_uncovered_paths` matching) Iteration 1 found breakable — rather than re-deriving new adversarial scenarios against parts of the mechanism Iteration 1 already cleared. This is narrower, faster, and more targeted than Iteration 1's audit, while still catching a genuine regression or out-of-scope mutation had either existed — the taxonomy (class A/B/C mandatory, D recorded-not-dropped) did its job as a bounding device, not a suppression device.

### Assessment against the Change's own declared terms

- All four targeted findings (R001 BLOCKER, R002/R003 MAJOR, R004 MINOR) are genuinely resolved: verified by reading the actual code/spec diff, not by trusting `resolution-001`'s or `specification-drift.md`'s narrative, and by independently reproducing both the shipped regression tests and my own additional adversarial probes against real `validate_project`.
- R005 (OBSERVATION) remains correctly unresolved by design, consistent with its own disposition in Iteration 1 and `specification-drift.md`.
- No class B (resolution regression), class C (out-of-scope mutation), or class D (unrelated latent, independently BLOCKER/MAJOR) finding was found. `new_material_findings` for this Iteration is `0`.
- `pytest -q` (244 passed) and `forge validate` (single pre-existing CHG-0008 finding) both independently reproduced, matching the Resolution's claims.

### Verdict

**PASS**

Finding counts (this Iteration):

- BLOCKER: 0
- MAJOR: 0
- MINOR: 0
- OBSERVATION: 0 (R005 carries forward from Iteration 1 as an accepted-by-design, unresolved OBSERVATION — not re-raised here since it is not a finding of this Iteration)

`new_material_findings: 0`. CHG-0011 may proceed to Completion per this Change's own convergence mechanism, which this Iteration has now used, and passed, on itself.
