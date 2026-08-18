---
forge:
  artifact: plan
  schema: 1
change: CHG-0011
status: approved
---
# Plan — CHG-0011

1. Schemas: extend `change-v2.schema.json` (iteration `kind`,
   `full_review_required`, `new_material_findings`, `finding_classes`; new
   top-level `review.convergence`) and `execution-provenance.schema.json`
   (`scope`, `targets`) — additive, `additionalProperties: false` preserved.
2. Protocol docs: `protocol/contract/engineering.md` (C-047–C-050),
   `protocol/versions/2/specification.md` (§10–§13),
   `protocol/versions/2/policies/review.yml` (`resolution_verification`
   block), `protocol/compatibility.md` (explicit compatibility subsection).
3. Project config: `.forge/forge.yml`
   (`review.convergence.allow_residual_risk_acceptance`, default absent).
4. Configuration loader: extend `load_project_configuration` (or confirm it
   already passes through unknown nested keys safely) so the new optional
   field round-trips without breaking existing project config validation.
5. Core validator: `_resolution_delta`, `_validate_resolution_verification`,
   wired into `_validate_protocol2_review_provenance`, in
   `src/forge_cli/validation/__init__.py`.
6. Tests: TDD-012 through TDD-020 per Test Strategy, using real
   `tmp_path` Git repos (matching existing `tests/cli/
   test_review_iteration_history.py` style) plus fixture manifests derived
   from `CHG-0008`/`CHG-0010` for the regression baseline.
7. Verification: `pytest -q`, `forge validate`, `forge doctor` from the
   worktree.
8. Documentation/Knowledge Capture: `docs/adr/0011-review-convergence-
   boundary.md` (mirrors `docs/adr/0008-...`), `knowledge-capture.md`.
9. Freeze subject, record `resolution`-role provenance (this Change's own
   Implementation, since there is no prior blocking finding to resolve —
   this is the *first* Iteration, so it is `implementation` role /
   `initial_review`, not itself a `resolution_verification` — the new
   mechanism only activates starting from *its own* second Iteration
   onward, if any).
10. Independent Strict Review (separate Execution/Context from
    Implementation, per Protocol 2 — executed by a fresh agent instance, not
    this session).
