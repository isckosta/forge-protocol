---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0016
status: complete
---
# Knowledge Capture — CHG-0016

- **A global find/replace on a short identifier substring will silently
  corrupt any longer identifier that contains it as a substring — verify
  the match is anchored, not just present, before running it.**
  Correcting `specification-review.md`'s Finding IDs from an incorrectly
  reused `R-00N` (Strict Review's real prefix) to the correct `SR-00N`
  (Specification Review's real prefix, confirmed against `CHG-0007`'s own
  history) used `sed 's/R-001/SR-001/g'` across the file. That pattern
  also matched inside `FR-001` and `NFR-001`, silently producing
  `FSR-001`/`NFSR-001`. Caught immediately by re-reading the file's own
  diff, not by a separate check — but the fix should have used a stricter
  pattern (a leading non-word-character anchor, or targeted `Edit` calls)
  from the start. General lesson: any bulk textual substitution inside a
  document with its own dense identifier vocabulary (`FR-`, `NFR-`,
  `CON-`, `INV-`, `DEC-`, `AC-`) needs the same scrutiny a code refactor
  would get, not less, because there is no compiler to catch the
  collision.

- **An originating brief's suggested structure is not evidence that the
  structure has precedent — check the real artifacts before adopting an
  invented convention as if it were already standard.** The prompt that
  started this Change suggested `### P-001` heading-per-work-item Plan
  structure and `### ADR-001` headings inside per-Change `architecture.md`
  files. Neither has any precedent: real Plans (`CHG-0007`, `CHG-0013`,
  `CHG-0015`) use a flat numbered list with no heading-per-item, and
  `CHG-0015/architecture.md` already uses `## DEC-002`, never `## ADR-002`
  — `docs/adr/` is a separate, project-durable namespace. Discovery caught
  both before Specification was written, by directly reading real Plan
  and Architecture files rather than trusting the brief's examples. The
  Canonical Artifact Structure this Change produced recognizes the real
  conventions and explicitly rejects the invented ones, with the
  rejection reasoning kept visible (`protocol/artifact-structure.md` §4)
  rather than silently doing the right thing without saying why the
  obvious-looking alternative was wrong.

- **`forge validate`'s C-051 check is not just documentation of the
  Unresolved Decision Management rule — it mechanically blocks a Gate the
  moment a manifest's `artifacts` vocabulary implies the Gate passed,
  regardless of intent.** The first draft of this Change's own
  `manifest.yml` set `specification_review: complete` while `DEC-001` was
  still `open`. `forge validate` failed immediately with a C-051 finding
  naming the exact conflict — not a bug, the mechanism working exactly as
  `protocol/policies/decision.yml` specifies. The fix was not to weaken
  the check but to use a manifest vocabulary (`drafted`, distinct from
  `complete`/`approved`/`ready`) that accurately represents "the document
  is written, the Gate is not asserted" — a real state this repository's
  existing artifact-status vocabulary had no established word for before
  this Change needed one.

- **Wiring a new resolved-content field through an existing projection
  mechanism touches every layer that mechanism has, not just the
  Harness-specific one — Plan's estimate of "one file" undercounted by
  three.** `Plan` step 4 named only
  `src/forge_cli/adapters/codex/projection.py`. Implementing FR-009
  correctly (reusing the exact pattern `contract_content` already
  establishes, per NFR-003) required also extending the generic
  `AdapterProjectionContext` (`adapters/driver.py`, shared by every
  Harness Adapter, not just Codex), both of `service.py`'s
  `AdapterProjectionContext` construction sites, and a new resolver
  function in `protocol_resolution/__init__.py`. This was recorded here
  and in `verification.md`, not by quietly editing the already-approved
  Plan to make it look like it had said this all along (`protocol/
  artifact-structure.md`'s own FR-005/C-069 recommendation, demonstrated
  against this Change's own Implementation).

- **An exact-snapshot integration test (`adapter_cli_wheel_probe.py`'s
  hardcoded `expected` reference-links list) is a feature, not friction —
  it caught the one real, user-visible behavior change this Change makes
  to the installed Codex skill's content, in the one test that actually
  builds and runs an installed wheel offline.** The fix was to update the
  hardcoded expectation to include the new, intentionally added
  `references/artifact-structure.md` link — confirming the change was
  deliberate and complete, not to loosen the assertion to stop it from
  needing maintenance.

- **A specified falsification test that is never actually run is worse than
  no test at all — it creates a false record of having checked.**
  `specification-review.md`'s own "Checked and found sound" section named
  the exact grep (`grep -ni "codex\|claude\|..." protocol/artifact-structure.md`)
  that would have caught NFR-002's violation before Implementation. It was
  specified, never run, and `traceability.yml` went on to record
  `NFR-002: evidence: artifact_structure_md_contains_no_harness_specific_content`
  — an affirmatively false claim, not merely an unverified one. Found only
  by an independent Strict Review actually executing the named grep
  (`R001`). General lesson: a Non-mechanical Validation item written down in
  Test Strategy or Specification Review is a promise, not documentation of
  something already done — it must be executed, not merely designed,
  before its result is recorded as evidence.
- **A Change whose entire subject is "recognize real convention instead of
  inventing new structure" is exactly the kind of Change most likely to
  silently drop a real convention it didn't think to enumerate.** Every
  Artifact type section in `protocol/artifact-structure.md` documented a
  structural core — and none mentioned the `forge:` frontmatter block that
  opens every real Artifact in this repository from `CHG-0006` onward,
  including this Change's own `plan.md`/`tasks.md`. Its own new
  `verification.md` and both canonical examples then shipped without it —
  reproducing, in the guidance's own deliverables, the exact
  regression-by-omission (`CHG-0001` had `## Result`; `CHG-0015` didn't)
  that motivated the whole Change (`R002`). The convention was omitted not
  by disagreement but because enumerating "what every Artifact already has
  in common" is a different exercise from "what makes each Artifact type
  distinct," and only the second one got done. General lesson: when a
  Change's method is "audit real examples for convention," the audit needs
  an explicit pass for cross-cutting conventions common to *all* examples,
  not only per-type ones — the common ones are exactly the ones easiest to
  stop seeing once you're looking for what varies.
- **A Decision's `resolved_via` classifies its weakest sub-question, not
  its strongest — and a Decision record's own Confidence paragraph can
  miscount its own Question without anyone noticing until it's checked
  against the Question itself.** `DEC-002` posed three sub-questions;
  two were resolved by genuine citation of existing normative text
  (`evidence`), the third by design reasoning about which existing file
  category fit (`autonomous_decision`). The record's Confidence paragraph
  said "both sub-answers were reached by direct citation," silently
  dropping the third from its own accounting, and `manifest.yml` recorded
  the whole Decision as `resolved_via: evidence` — exactly the shape
  `decision.yml`'s `agent_inference_is_not_evidence: true` exists to
  prevent, on a Decision this Change's own Specification Review passed
  without catching (`R008`). `CHG-0015`'s own structurally comparable
  architectural Decision correctly used `autonomous_decision`; this one
  should have matched it from the start.
- F-008 ("Material Architecture Changes require ADR") is again satisfied
  by an ADR alone, following the same established practice `docs/adr/
  0012`/`docs/adr/0013` already recorded for `CHG-0013`/`CHG-0015`: no
  `docs/rfcs/` entry accompanies a Contract/Specification-level addition
  below the scale of a new integer Protocol identifier.
