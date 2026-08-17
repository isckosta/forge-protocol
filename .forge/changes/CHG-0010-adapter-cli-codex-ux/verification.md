---
forge:
  artifact: verification
  schema: 1
change: CHG-0010
status: passed
---

# Verification — Adapter CLI and Codex Installation UX

## Scope

Verification covers all 33 Requirements (24 FR, 4 NFR, 5 INV) and all 12
acceptance scenarios for the generic Harness Adapter contract, the packaged
Codex driver, the public `forge adapter` command group, and the installed
Codex Adapter Installation UX golden path, at revision `80d924c` on branch
`feat/chg-0010-adapter-cli-codex-ux`.

This revision also folds in two remediations discovered after the original
implementation Tasks closed:

- a publisher path-confinement race (`C-002`, TDD-009C): the mutation loop
  reused a Path resolved once during preflight instead of re-validating
  immediately before each write, letting a directory swapped for a symlink
  after preflight redirect a create/update/delete outside the publication
  root;
- reconciliation with `main`'s independently merged Protocol 2 introduction
  (TDD-010): the Codex projection now threads the project's declared
  protocol id through to `resolve_effective_contract`/`resolve_effective_flow`
  and the rendered `SKILL.md`, instead of always resolving Protocol 1
  canonical resources regardless of the project's actual protocol.

## TDD audit (Step 1)

Every FR/NFR/INV in `traceability.yml` maps to at least one planning Task and
`test-strategy.md` TDD id; every AC maps to at least one Task. No orphaned
requirement or acceptance scenario was found. `tdd-evidence.yml` records 42
cycles (`cycle_count: 42`); every cycle's RED command/result precedes and
differs from its GREEN command/result, and every RED `reason` describes a
behavioral failure rather than a collection error. `TDD-009C` and `TDD-010`
were added as remediation cycles after the original Task 1-8 test-strategy
mapping; they reinforce requirements already traced to their original Tasks
(FR-017/FR-018/NFR-002/NFR-003/INV-001/INV-004 via T-004/T-005; FR-009/FR-010/
NFR-001/INV-001 via T-003/T-008) rather than introducing new ones, so
`traceability.yml` needed no structural change.

## Automated evidence

### Full suite

```text
.venv/bin/python -m pytest -q
344 passed in 22.17s
```

Includes the installed-wheel offline golden path
(`test_installed_wheel_runs_the_codex_adapter_golden_path_offline`), which
builds an isolated wheel, installs it into a fresh venv with no network
access (audit-hook and socket-level guard), runs `forge init` through the
installed `forge` executable, and drives `plan`/`install`/`update` end to end
against the packaged Codex Adapter.

### Repository hygiene

```text
git diff --check
git status --short
```

`git diff --check` reported no whitespace errors. `git status --short` shows
only the pre-existing untracked `.codex/`, `docs/document-2026-08-13T04-46-37-625Z.md`,
`docs/superpowers/`, and `uv.lock`, which are excluded from every commit on
this branch.

### Plan/install parity

Exercised by `test_plan_is_read_only_and_uses_evidence_target` and
`test_install_dry_run_is_read_only_and_returns_the_install_plan`: `plan codex`
and `install codex --dry-run` report identical ordered operations and mutate
no filesystem bytes.

## Acceptance scenarios

- **AC-001 Golden path:** `test_installed_wheel_runs_the_codex_adapter_golden_path_offline`.
- **AC-002 Discovery:** `test_adapter_list_treats_unsupported_project_protocol_as_unknown_compatibility` and the installed-wheel probe's `adapter list` assertion.
- **AC-003 Plan parity:** `test_plan_is_read_only_and_uses_evidence_target`, `test_install_dry_run_is_read_only_and_returns_the_install_plan`.
- **AC-004 Collision:** `test_conflicted_plan_is_refused_before_any_mutation`, `test_user_owned_preserve_operation_never_overwrites_existing_content`.
- **AC-005 Idempotent reinstall:** `test_install_then_reinstall_is_true_noop`, `test_empty_projection_reinstall_is_a_true_noop`.
- **AC-006 Safe update:** `test_update_deletes_an_intact_obsolete_recorded_artifact`, `test_update_refreshes_an_older_record_even_when_all_artifacts_are_unchanged`, and the new `test_directory_symlink_swap_after_preflight_prevents_escaping_update_target` (C-002).
- **AC-007 Drift protection:** `test_doctor_reports_drift_and_action_without_mutating`, `test_update_refuses_drift_without_partial_mutation`.
- **AC-008 Atomic rollback:** `test_failure_after_create_update_and_delete_restores_every_file_and_installation_record`, `test_incomplete_rollback_reports_generic_publication_failure_and_target`.
- **AC-009 Configuration precedence:** `test_target_precedence_reports_explicit_configuration_then_evidence`.
- **AC-010 Limitations remain truthful:** `test_projection_marks_instructions_as_representation_not_enforcement`.
- **AC-011 Invalid or stale state:** `test_update_rejects_wrong_record_identity_without_mutation`, `test_update_rejects_an_unsafe_recorded_path_as_invalid_state_without_mutation`, `test_incompatible_protocol_fails_before_install_mutation`.
- **AC-012 Canonical survival:** `test_deleting_generated_tree_leaves_separate_canonical_forge_tree_byte_identical`, `test_publisher_rejects_recorded_canonical_path_outside_publication_root`.

## Protocol reconciliation evidence

`test_install_projects_protocol1_skill_without_reviewer_resolver_independence`
and `test_install_projects_protocol2_skill_with_reviewer_resolver_independence`
verify a Protocol 1 project's installed `SKILL.md` carries none of the
Protocol 2 Reviewer/Resolver independence content, and a Protocol 2 project's
does, closing the gap where `main`'s Protocol 2 projection content existed
only in test-only call sites unreachable from any driver.

## External review surface

No pull request exists yet for CHG-0010; the branch is local-only. The
blocking external-review-thread condition (C-027) is therefore satisfied
trivially for this Verification, but it must be re-evaluated before
Completion if a pull request is opened.

## Result

All 33 Requirements and all 12 acceptance scenarios are covered. The final
fresh run at `80d924c` passed all 344 tests, including the offline installed-wheel
golden path, with clean repository hygiene.
