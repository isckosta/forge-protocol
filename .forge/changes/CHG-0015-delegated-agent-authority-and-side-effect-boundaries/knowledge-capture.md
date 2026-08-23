---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0015
status: complete
---
# Knowledge Capture — CHG-0015

- **An exclusion designed to fix one gap can silently reopen a different
  one at the exact same call site — verify the fix against the mechanism's
  own bootstrapping behavior, not only against the vulnerability that
  motivated it.** The first correction (commit `d1ec5e8`) removed the
  review-control-metadata exclusion from the delegate Observed Effect
  computation, correctly fixing a self-authorization blind spot. Writing
  the fixture-repo Test Strategy immediately afterward surfaced that the
  fix was itself broken: the delegating Execution's own act of recording
  the delegate's provenance necessarily mutates `provenance.yml`, and that
  write always happens after the delegate's baseline is captured — so a
  no-exclusion path-diff flagged *every* legitimate delegation as an
  Out-of-Scope Mutation, universally, not just attacks. The eventual fix
  (`c7ffb47`) required recognizing that Out-of-Scope Mutation (a path-diff
  question) and self-authorization (a "did this record's own declared
  Authority change from its history" question) are answerable by two
  different, independent mechanisms — conflating them into one path-diff
  check made *a* correct answer for one property impossible to reconcile
  with a correct answer for the other.
- **A function's name and one-line docstring are not the same as its
  actual precondition set — read the callee before writing "reuses X
  verbatim" in a design document.** Architecture named
  `_first_committed_provenance_record` as directly reusable for the C-062
  self-authorization check. It is not: that function's acceptance check
  calls `_record_fields`, which hardcodes the Protocol-2 Reviewer/Resolver
  role enum (`implementation`/`resolution`/`review`) — correct for C-026's
  own purpose, and silently wrong for any other role, including
  `delegated_task`, by returning `_HISTORY_ERROR` (a fail-closed result
  that looked like a plausible, if pessimistic, answer, not an obvious
  crash) rather than a clear signal that the function did not apply.
  Caught only by actually running the test against real Git history, not
  by re-reading the design. General lesson: "fails closed" and "fails
  informatively" are different properties, and a reused function that
  fails closed for the wrong reason is a harder defect to notice than one
  that crashes.
- **A relaxed schema constraint (`minItems: 1` to `0`) that looks purely
  additive can still break a downstream function that assumed the old
  constraint held.** `_uncovered_paths` (CHG-0011) treats an empty `scope`
  as malformed input (`if not scope: return None`), which was correct
  under `@1`'s `minItems: 1` guarantee but wrong once `@2` legitimately
  allows `scope: []` for zero-write-authority delegation — reusing
  `_uncovered_paths` unmodified for the new check would have silently
  treated every read-only delegate's Out-of-Scope Mutation as
  "undeterminable" instead of "everything is out of scope," a fail-*open*
  direction for exactly the incident's own shape. Caught during
  Architecture, before any code existed, by tracing the callee's actual
  guard clause rather than assuming an existing helper generalizes.
  Resolved with a new, narrower helper (`_deleg_uncovered`) rather than
  changing `_uncovered_paths`'s existing, still-correct-for-Resolution
  behavior.
- **A conservative default described in prose ("the Change's own
  governed Artifact and source paths... plus whatever `src`/`tests` paths
  the Change's own `intent.md` names") is not automatically implementable
  just because it sounds concrete.** Free-form Markdown is not
  deterministically parseable for "which paths are in scope" without an
  unreliable heuristic — exactly the kind of non-determinism C-065's
  fail-closed discipline exists to avoid. Caught while writing GREEN, not
  earlier, because Architecture's own review pass evaluated the *shape* of
  the design (a conservative default exists, is fail-closed-leaning) without
  asking whether the specific default was mechanically computable. Narrowed
  to a single deterministic rule (the Change's own `.forge/changes/<id>/`
  directory) with an explicit escape hatch (a primary Execution that needs
  broader first-hop delegation must declare `scope` itself); the narrower
  rule then required fixing four already-written fixture-repo tests (TDD-004,
  005, 009, 010) whose primary records had not declared a `scope`, which
  is itself a useful confirmation that the tests were exercising real
  behavior, not asserting whatever the code happened to do.
- **Running the actual validator against a self-authored manifest is not
  optional scaffolding — it is where a real Contract-ownership defect was
  found in this Change's own artifacts, not by re-reading them.** The first
  draft of `specification.md`/`manifest.yml` resolved `DEC-002`
  (`architectural` class) during Specification, reasoning that
  `agent_with_review` Authority was satisfied by the Adversarial
  Specification Review that immediately followed. Running `forge validate`
  surfaced a C-051 finding: `decision.yml`'s `owning_artifact_by_class`
  fixes `architectural` questions to **Architecture** as owning Artifact,
  not Specification, and holding sufficient Authority in the abstract does
  not license an Artifact to resolve a Decision it does not own (C-052).
  Architecture did not exist yet in the Change at that point; nothing had
  standing to resolve `DEC-002`. This is the same general lesson as the
  self-authorization findings above, applied to this Change's own process
  rather than to its subject matter: a self-declared resolution is not the
  same as a verified one, which is this Change's entire thesis, demonstrated
  against itself before any Architecture or Implementation existed.
- **Delegation Ceiling and self-declared "unbounded" scope interact badly
  by default — an absent value must not be read as "no limit."**
  Specification's first draft of the Delegation Ceiling (FR-007) required a
  delegate's Scope to stay within its delegator's own Scope but never
  stated what happens when the delegator's own Scope was never declared —
  true of every primary Execution under this Change's own rollout decision
  (`DEC-001`). Found during this Change's own Adversarial Specification
  Review (`specification-review.md` R002), before any code existed: an
  undeclared delegator Scope read as unbounded would have made the ceiling
  trivially satisfiable by any grant at all, defeating it exactly in the
  incident's own shape (a primary Execution, with no declared Scope,
  delegating to a subagent).
- F-008 ("Material Protocol Changes require RFC") is again satisfied by an
  ADR alone, following the same established practice `docs/adr/0012`
  already recorded for `CHG-0013` (itself following `CHG-0008`/`CHG-0011`):
  no `docs/rfcs/` entry accompanies a Contract/Specification-level addition
  below the scale of a new integer Protocol identifier. Recorded here
  explicitly, again, rather than re-deriving the interpretation from F-008's
  literal text each time a Change reaches this evaluation.
