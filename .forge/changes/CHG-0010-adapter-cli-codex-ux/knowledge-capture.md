---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0010
status: complete
---
# Knowledge Capture — CHG-0010

## The TOCTOU pattern that took six iterations to close

`src/forge_cli/adapters/publisher.py` repeatedly resolved a filesystem path
once, then reused that resolved `Path` (or its already-read content) across
multiple later operations — a preflight check, an authorization read, a
mutation, a rollback-backup capture, a rollback restore — each of which
should have re-validated or re-read fresh, since an attacker (or, more
realistically, a concurrent legitimate process) could redirect the path via
directory-to-symlink swap or change the underlying content in the window
between the first resolution/read and each later use. Six independent Strict
Review Iterations (`review.md`) each found one more call site still doing
this, in decreasing order of exploitation window size: the original
BLOCKER spanned the entire preflight/validation/mutation sequence; the final
instances (TDD-018, TDD-019) were single-statement-sized windows between two
adjacent reads of the same file.

**General lesson for this codebase:** "re-validate immediately before each
use" is a real, working mitigation — the Reviewer confirmed it closes every
concretely demonstrated instance — but it is inherently enumerative: its
completeness depends on someone finding every use site, and finding one more
site never proves no more exist. `src/forge_cli/adapters/configuration.py`
already uses a structurally different technique (a dir-fd-anchored,
`O_NOFOLLOW`-based write path) that prevents this entire defect *class* by
construction rather than by re-validating before each use — named as
available since Iteration 1's Observation #3, still not adopted in
`publisher.py` after six iterations of the enumerative approach finding one
more instance each time.

**Follow-up recorded, not implemented in this Change:** adopt
`configuration.py`'s fd-anchored technique in `publisher.py`, replacing the
current re-validate-before-each-use pattern for the whole module rather than
its next individual call site. The Iteration 6 Reviewer's independent
assessment: *"the defect class is closed for all currently-existing call
sites as far as exhaustive re-reading can determine, but six consecutive
iterations finding one more instance by the same manual-enumeration method
is evidence the method is fragile, not that the class is exhausted."* The
engineer was offered this rewrite before Iteration 6 and chose to proceed
with a scoped resolution instead, a legitimate call under this Change's own
scope discipline — but the recommendation should not be lost after
Completion. Suggested as a dedicated future Change (`refactor` or `security`
kind), not absorbed silently into CHG-0010's already-large TDD evidence
trail.

## Applying CHG-0011's Resolution Verification discipline to a Protocol 1 Change

This Change is `forge/change@1` and predates CHG-0011's mechanically-enforced
Resolution Scope/Convergence machinery, which only activates for
`forge/change@2` manifests that declare `kind`. Iteration 6's Resolution
(TDD-019) nonetheless declared its scope and targets in `review.md`'s
"Pre-Iteration 6 note" by convention, and the independent Reviewer confirmed
the actual Git delta matched that declared scope with no scope creep. This
is evidence the discipline CHG-0011 formalizes mechanically is also usable,
by convention, on Protocol 1 Changes that predate it — supporting
`protocol/compatibility.md`'s framing that the discipline is a process
obligation, not solely a Protocol-2-gated mechanism.
