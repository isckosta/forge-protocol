---
forge:
  artifact: plan
  schema: 1
change: CHG-0013
status: approved
---
# Plan — CHG-0013

1. Schemas: add optional `decisions` array (shape in `architecture.md`) to
   both `change.schema.json` and `change-v2.schema.json`,
   `additionalProperties: false` preserved. New
   `protocol/schemas/policy-decision.schema.json`. Add
   `forge/policy/decision@1` to `protocol/schemas/catalog.yml`.
2. Protocol docs: `protocol/contract/engineering.md` (C-051–C-059);
   `protocol/versions/2/contract/engineering.md` (backfill C-047–C-050,
   then add C-051–C-059 — see `discovery.md` finding); new
   `protocol/specification.md` §39; new `protocol/policies/decision.yml`;
   `protocol/compatibility.md` (new subsection).
3. Repository docs: one added sentence to `ARCHITECTURE.md` §17 naming
   Decision Gate blocking; no other section touched (§26 Protocol-2
   staleness explicitly left to a separate Change, per `architecture.md`).
4. Core validator: `_validate_unresolved_decisions` in
   `src/forge_cli/validation/__init__.py`, wired into `validate_project` for
   every protocol id (not gated behind `pid == 2`, unlike the Protocol-2-only
   C-026 machinery).
5. Tests: TDD-001 through TDD-012 per Test Strategy, using `tmp_path`
   fixture manifests plus the twelve real historical manifests
   (`CHG-0001`–`CHG-0012`) for the compatibility regression baseline.
6. Verification: `pytest -q`, `forge validate` (baseline today: "Forge
   project is valid," zero findings — confirmed before this Plan was
   written), `forge doctor`.
7. Documentation/Knowledge Capture: `docs/adr/0012-unresolved-decision-
   management.md` (triggered by `architecture.yml`
   `adr.required_when: architectural_pattern_change` /
   `long_lived_cross_cutting_decision` — this Change introduces both);
   `knowledge-capture.md`; `traceability.yml`; `tdd-evidence.yml`. An RFC
   under `docs/rfcs/` is evaluated at Documentation time against
   `CONTRIBUTING.md`'s "Material Protocol Changes require RFC" rule
   (`.forge/contract/engineering.md` F-008) — not authored during planning,
   since RFC authorship is itself Documentation-stage work this Change's own
   boundary defers.
8. Freeze subject, record `implementation`-role provenance (this Change's
   first Iteration — `initial_review`, not `resolution_verification`,
   exactly as CHG-0011's own Plan reasoned for itself).
9. Independent Strict Review (separate Execution/Context from
   Implementation, per Protocol 2 — executed by a fresh agent instance, not
   this session).

## Explicit boundary

This Plan and the following Tasks are the last planning artifacts produced
in this session. Per this Change's own governing instructions, Implementation
(steps 4–6 above as actual code, not the design already recorded in
`architecture.md`) requires explicit human approval in a later message.
Nothing above authorizes starting it.
