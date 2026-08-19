# Forge Examples

This directory contains reference Forge Changes.

- `golden-path-standard/` — the canonical STANDARD-Flow, Codex-Harness
  Golden Path: install Forge, initialize a repository, install the Codex
  Adapter, confirm readiness, and carry one small behavioral Change through
  TDD, Verification, and (pending independent execution) Strict Review.
  Includes a disposable starter fixture, deterministic Layer A/B automated
  tests (`tests/golden_path/`), and a behaviorally-specified manual
  acceptance procedure for the parts a live Codex session must prove.

Future examples should also demonstrate:

- a FAST bugfix using regression-first TDD;
- a FAST tiny Feature;
- a STANDARD behavioral Feature;
- a FULL architectural Change;
- RED -> GREEN -> REFACTOR evidence;
- Flow escalation;
- a justified TDD exception;
- Strict Review Findings;
- Reviewer/Resolver cycles;
- Documentation Impact evaluation.

Examples must reflect canonical Protocol semantics.
