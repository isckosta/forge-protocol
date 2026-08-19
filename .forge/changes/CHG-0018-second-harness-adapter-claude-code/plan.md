---
forge:
  artifact: plan
  schema: 1
change: CHG-0018
status: approved
---
# Plan — CHG-0018

**Written for DEC-001/002/003 all resolved (architectural, autonomous,
per `architecture.md`).**

1. Core fixes: relocate `assess_invariant`/`to_generic_limitation` to new
   `adapters/assessment.py`; strip `.codex` from `adapters/configuration.py`
   and `adapter-configuration.schema.json`; update the one affected
   generic test (`test_adapter_configuration.py`) and add the Codex-owned
   equivalent test if not already covered.
2. New `src/forge_cli/adapters/claude_code/` package: `resources/
   {adapter.yml,capabilities.yml,publication.yml}` + a skill template,
   `descriptor.py`, `evidence.py`, `targets.py`, `projection.py`,
   `driver.py` — per `architecture.md`'s Content Shape.
3. Registration: `adapters/packaged.py`.
4. Protocol docs: `C-074` in both Contract files.
5. Tests: TDD-001 (Core-fix relocation, RED/GREEN), TDD-002 (Claude Code
   driver produces all three mechanisms' artifacts correctly, RED/GREEN),
   TDD-003 (shared conformance suite passes both drivers), TDD-004
   (repository-wide baseline unchanged).
6. ADR: `docs/adr/0016-*.md` (number re-verified immediately before
   writing).
7. Dogfooded Golden Path: install the Claude Code Adapter into a scratch
   repository, then — as the live Harness — carry a real, small Change
   through Intent → ... → Strict Review, recording genuine evidence under
   `examples/golden-path-claude-code/`.
8. Documentation: `CHANGELOG.md`, `ROADMAP.md` status flip,
   `knowledge-capture.md`, `traceability.yml`, `tdd-evidence.yml` (from
   real Implementation evidence, not drafted ahead of it).
9. Strict Review: adversarial, evaluating in particular NFR-001 (no
   vendor-specific concept actually leaked into the Core, not just
   specified), whether the hook's pattern-matching claim stays honest
   (FR-006), and whether the dogfooded Golden Path evidence is genuine
   (a live session's real artifacts) rather than narrated/simulated.

## Validation Strategy

`pytest -q` (existing suite plus TDD-001–004), `forge validate`, `forge
doctor` — against the pre-Implementation baseline, before Implementation
begins. Plus a real `forge adapter install claude-code` against a fresh
scratch repository (mirroring `CHG-0017`'s own end-to-end verification
practice).

## Compatibility Impact

None: Core changes are relocation/generalization only (CON-002 — the
schema change only widens acceptance). No new Protocol integer. No
historical Change invalidated.

## Implementation Boundary

Reaching `tasks_ready` is not, by itself, authorization to begin
Implementation. For this Change, that explicit go-ahead was already given
via this session's plan-mode approval (covering Discovery through
Completion, dogfooded as a real Change), distinct from the architectural
Decisions above, which required no human authority floor (none is
`product`/`contract` class). `tasks.md` below has every task unchecked;
none has been started as of this Plan's own approval.
