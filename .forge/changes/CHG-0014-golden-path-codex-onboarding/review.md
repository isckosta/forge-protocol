---
forge:
  artifact: review
  schema: 1
change: CHG-0014
status: failed
---

# Strict Review — Golden Path Baseline and Codex Onboarding Validation

## Iteration 1 — REQUEST CHANGES (`kind: initial_review`)

Reviewed revision: `4b4405c3cc72957e3ed7be9246e912fc76bd8289` (`implementation-001`, per `provenance.yml`).

Reviewer Execution: `review-exec-chg0014-20260818-01`.
Reviewer Execution Context: `review-context-chg0014-20260818-01`.
Assurance: `recorded` (self-recorded repository-native provenance; no cryptographic/external attestation claimed).

This is CHG-0014's own first Strict Review Iteration (`kind: initial_review`), independent in Execution and Execution Context from the Implementation session that produced `implementation-001` (`implementation-exec-chg0014-20260818-01` / `implementation-context-chg0014-20260818-01`). This session has no memory of the Implementation session and independently re-derived every claim below rather than trusting `discovery.md`/`verification.md`/`tdd-evidence.yml`'s narrative on their own say-so.

### Verification performed

- Read `protocol/specification.md` (§21, §22, §24, §25, §39), `protocol/versions/2/specification.md` (all sections), `protocol/contract/engineering.md`, `protocol/versions/2/contract/engineering.md`, `protocol/policies/review.yml`, `protocol/versions/2/policies/review.yml`, `protocol/schemas/change-v2.schema.json`, `protocol/schemas/execution-provenance.schema.json` in full before forming any judgment.
- Read `intent.md`, `discovery.md`, `specification.md`, `test-design.md`, `plan.md`, `tdd-evidence.yml`, `verification.md`, `manifest.yml`, `provenance.yml` in full, then `git diff 6734847..4b4405c --stat` and the complete `git diff 6734847..4b4405c` for the actual reviewable diff (26 files, +2193/-4).
- Confirmed `2d30413` (the commit after the frozen subject) touches only `provenance.yml` (`git show 2d30413 --stat`), the exact review-control-metadata exception permitted by `protocol/versions/2/specification.md` §5 — it does not widen or redefine the frozen `implementation-001` binding.
- `.venv/bin/python -m pytest tests/ -q`: **406 passed**, matching `verification.md`'s claim exactly.
- `.venv/bin/python -m pytest tests/golden_path/ -v`: 2 passed. `.venv/bin/python -m pytest tests/unit/test_codex_projection_gates.py tests/cli/test_adapter_commands.py tests/unit/test_doctor_diagnostics.py tests/cli/test_doctor.py -v`: all passed (11 + 21 + 7 + 3).
- `.venv/bin/forge validate` (pre-edit baseline): exit 0, "Forge project is valid". `.venv/bin/forge doctor` (this repository): all 7 checks PASS, exit 0 — confirms CON-001 (no Adapter installed here, so no `adapter:` checks appear) as claimed.
- Independently validated `manifest.yml`, `provenance.yml`, and `tdd-evidence.yml` directly against `protocol/schemas/change-v2.schema.json`, `protocol/schemas/execution-provenance.schema.json`, and `protocol/schemas/tdd-evidence.schema.json` with `jsonschema.Draft202012Validator` (not the claim in `verification.md` that Layer B's schema check passed — CHG-0014's *own* artifacts, checked directly by this session): **0 schema errors** across all three.
- Read the full diffs of `src/forge_cli/adapters/codex/projection.py`, `src/forge_cli/doctor/__init__.py`, `src/forge_cli/adapter_cli.py`, and their four touched/added test files, line by line, cross-referencing every RED claim in `tdd-evidence.yml` against the actual pre-image code (via `git show 6734847:<path>`) to independently judge RED plausibility rather than trusting the narrative.
- Read `tests/golden_path/test_golden_path_standard.py` (327 lines) in full and adversarially probed whether Layer B's TDD/ordering claims could pass vacuously.
- Ran `git status --porcelain -uall` and investigated every untracked path with `git log --all --diff-filter=A -- <path>`, `git check-ignore -v <path>`, and direct content inspection — see BLOCKER-1.
- Independently reproduced the `forge doctor` Adapter-readiness aggregation's `warning`→`PASS` behavior end to end against a throwaway repository (not reusing any shipped test) — see MAJOR-1.
- Confirmed scope claims directly: `git diff 6734847..4b4405c -- protocol/` is empty (no Protocol/Contract/Schema file touched); root `pyproject.toml` is untouched (only `examples/golden-path-standard/starter/pyproject.toml`, a disposable fixture, changed); no new `@app.command()`/`@adapter_app.command()` was added to `app.py`/`adapter_cli.py`.

### Findings

- **CHG-0014-R001 — BLOCKER (dimension: domain_invariants / C-026, Protocol 2 §5) — the effective reviewable workspace is not clean: four Git-visible, non-ignored, untracked files exist that are no part of the frozen `implementation-001` subject and no part of this Change's review-control-metadata exception, and this mechanically prevents any bound `pending`/`passed` Review Iteration for this Change from validating today.**

  `git status --porcelain -uall` shows four untracked paths: `.codex/config.toml`, `docs/document-2026-08-13T04-46-37-625Z.md`, `docs/superpowers/specs/2026-08-13-chg-0006-completion-remediation-design.md`, `uv.lock`. None is excluded by `.gitignore` (`git check-ignore -v` on all four: no match, exit 1). None was ever added in any commit on any branch (`git log --all --diff-filter=A -- <path>`: empty for all four). Their content confirms they are unrelated to CHG-0014's subject matter: `.codex/config.toml` is a PyCharm MCP-server URL, not a Forge Codex Adapter artifact (this repository has no `.forge/adapters/` directory at all — no Adapter is actually installed here, consistent with `verification.md`'s own CON-001 claim); `docs/document-2026-08-13T04-46-37-625Z.md` is an unrelated full product-specification document; `docs/superpowers/specs/2026-08-13-chg-0006-completion-remediation-design.md` is an unrelated design note for a different, already-closed Change (CHG-0006), apparently left by a local "superpowers" skill; `uv.lock` has no corresponding root `pyproject.toml` change in this diff. All four share an mtime of `2026-08-18 20:33:52`, before the Implementation commit's timestamp (`23:02:57`), consistent with pre-existing session/tooling residue rather than anything CHG-0014 produced.

  `protocol/versions/2/specification.md` §5 is explicit that "Core MUST account for reviewable deltas introduced by ... Git-visible untracked files," with no carve-out for files judged "unrelated" to the Change under review — the only permitted exception is the Change's own exact `manifest.yml`/`provenance.yml`/`review.md` paths. This repository's own mechanical enforcement agrees: `src/forge_cli/validation/__init__.py:60-63` (`_untracked_paths`, `git ls-files --others --exclude-standard`) feeds directly into `_reviewable_workspace_delta`/`_changed` (lines 68-85), which does not scope untracked files to the Change directory or to files the Implementation commit touched. I reproduced this directly against the real `validate_project` machinery (not mocked):

  ```
  >>> _changed(repo_root, CHG-0014-manifest-path, "4b4405c3cc72957e3ed7be9246e912fc76bd8289")
  True
  >>> _reviewable_workspace_delta(...)
  {'docs/document-2026-08-13T04-46-37-625Z.md', '.codex/config.toml',
   'docs/superpowers/specs/2026-08-13-chg-0006-completion-remediation-design.md',
   'uv.lock'}
  ```

  Concretely: had I bound my own Review Iteration with `status: pending` or `status: passed` referencing `implementation-001` (`src/forge_cli/validation/__init__.py:349`, `elif status in{"pending","passed"}and st.get("current")!="complete"and _changed(...)`), `forge validate` would emit `C-026 review subject changed after its immutable revision freeze; create new subject provenance.` and exit 2 — a real, reproducible failure of this repository's own freeze invariant, not a hypothetical. This is why my own Iteration below is recorded with `status: failed` rather than any bound `pending`/`passed` state: it is the only status value that does not trip this specific check, and it is also the accurate verdict.

  This finding does **not** indict CHG-0014's own diff — the diff itself is exactly what `git diff 6734847..4b4405c` shows, and no reviewed file has drifted. It is a currently-blocking **precondition** that Protocol 2 ties directly to `review_passed` eligibility for *any* Change while this workspace state persists, discovered by actively trying to reject the Implementation rather than assuming "pre-existing, so harmless." Per C-059, I record this rather than resolve it myself. Remediation is outside a Reviewer's role (C-026 Reviewer/Resolver separation) but is straightforward: remove, gitignore, or commit the four files (none of which appear to belong in this repository's history at all) before the next Review Iteration is attempted.

- **CHG-0014-R002 — MAJOR (dimensions: correctness, test_quality, documentation) — `forge doctor`'s new Adapter-readiness aggregation silently relabels a genuine `warning`-status Adapter diagnostic as `PASS`, producing self-contradictory output, and is untested for that path.**

  `src/forge_cli/doctor/__init__.py::_adapter_readiness_checks` (new in this diff): `status_map = {"passed": "passed", "failed": "failed", "warning": "passed"}`. `AdapterService.doctor` legitimately returns `warning`-status checks (`src/forge_cli/adapters/service.py:135-136`, `_warning_check`) — for example `compatibility` when project configuration cannot yet be validated (`service.py:278-285`, message: *"Protocol compatibility cannot be checked until project configuration is valid."*) — while an Adapter is still installed. I reproduced this directly, end to end, against a throwaway repository (not reusing any shipped test): `forge init` → `forge adapter install codex` → corrupt `.forge/forge.yml` to invalid YAML → `forge doctor`:

  ```
  FAIL project_configuration: mapping values are not allowed here ...
  FAIL adapter:codex:configuration: mapping values are not allowed here ...
  PASS adapter:codex:compatibility: Protocol compatibility cannot be checked until project configuration is valid.
  PASS adapter:codex:conformance: Adapter conformance cannot be checked until project configuration and target are valid.
  PASS adapter:codex:limitations: Adapter capability limitations cannot be inspected until representation is available.
  ```

  Three lines are labeled `PASS` while their own message text says the opposite — the check could not be performed, which is precisely what `warning` exists to communicate and precisely what the pre-existing `forge adapter doctor codex` command still renders correctly as `WARN` for the identical underlying `AdapterCheck` (`src/forge_cli/adapters/formatting.py:27-30`). The fidelity loss is specific to this Change's new top-level aggregation path, not a pre-existing limitation being inherited. Root cause: `app.py`'s top-level `doctor()` command's `labels` dict (`src/forge_cli/app.py:130-134`) has no `"warning"` key; passing a `warning` status through unmapped would raise `KeyError` and crash the command. The chosen fix avoids the crash by discarding the `warning` semantic rather than adding it — `labels["warning"] = "WARN"` would have fixed the crash risk without misinforming the user, and would not have changed exit-code behavior at all (`DoctorResult.passed` already only checks `status != "failed"`, `doctor/__init__.py:36-37`).

  This is exactly the class of defect the task brief asked this dimension of Review to probe ("verifique que ... mapeia corretamente status 'warning' para não travar o exit code indevidamente") — the exit code is not wrongly blocked (verified: `warning`-mapped-to-`passed` cannot cause a spurious non-zero exit, since `!= "failed"` already treated `warning` as non-blocking before this Change), but the *label* is wrong, silently, in the exact command this Change's own stated purpose is to make trustworthy ("`forge doctor` never surfaced installed-Adapter health" — CHANGELOG.md). No test in `tests/unit/test_doctor_diagnostics.py`, `tests/cli/test_doctor.py`, or `tests/golden_path/` exercises any scenario in which an aggregated Adapter check carries `status: warning` — the two adapter-readiness tests shipped (`test_doctor_reports_installed_adapter_readiness`, `test_doctor_reports_drifted_adapter_as_failed`) only cover the `passed`/`failed` paths, leaving this defect's exact trigger condition entirely outside the Change's own regression net.

- **CHG-0014-R003 — MINOR (dimension: test_quality) — Layer B's commit-ordering assertions (`git merge-base --is-ancestor`) in `tests/golden_path/test_golden_path_standard.py` are self-referential and cannot independently falsify a reordering, because the test script itself is the sole author of the linear commit sequence it then asserts is linear.**

  `test_golden_path_produces_a_valid_standard_change` commits `planning_commit`, then `red_commit`, then `implementation_commit` strictly in that order within the same script, then asserts `merge-base --is-ancestor planning_commit red_commit` and `red_commit implementation_commit` (lines 282-295). Given single-branch, strictly sequential `_commit_all` calls, these ancestor relationships hold by construction for any content whatsoever — the assertions can only fail if the *test script itself* is later edited to reorder its own `_commit_all` calls, not if some independent actor (e.g., a differently-behaving Codex session in Layer C, which this test does not exercise) tried to commit Implementation before RED. The genuinely non-vacuous part of Layer B — real subprocess RED (`returncode != 0`, `"DID NOT RAISE"` in `red_run.stdout`) before any production-code edit, then real subprocess GREEN (`"3 passed"`) after — is independently reproduced by this Reviewer and is **not** vacuous; only the ordering-assertion framing overstates what those specific two `assert` lines, in isolation, prove about "genuine chronological TDD" beyond the RED/GREEN content itself, which the docstring (lines 6-10) partially conflates. The one assertion that does add independent value here is `production_diff_before_green` (line 301-304, confirming `src/accounts/users.py` is absent from the `planning_commit..red_commit` diff) — that one is not self-referential in the same way and genuinely rules out production code preceding RED within the constructed history. Non-blocking: this does not misrepresent the actual RED/GREEN evidence, only slightly overstates what the ordering assertions specifically contribute.

### Positive observations (not findings, recorded for completeness)

- The subagent-overwrite incident disclosed in `discovery.md` ("Note on this Discovery's own process") was handled correctly: the unauthorized write was caught, the subagent was stopped (`TaskStop`), the affected file (`intent.md`) was discarded and rewritten from scratch, and the two claims at risk were independently re-derived from source rather than kept on the subagent's authority. No residual reliability concern in the final artifacts follows from this incident.
- The decision to leave FULL's `before_architecture` gate unrepresented in generated Codex instructions is reasonable and consistently disclosed in three independent places (`discovery.md`, `intent.md` Non-goals, `verification.md` Product findings #2) rather than silently dropped — it does not sit on the Plan→Implementation boundary this Change targets, and FULL Golden Paths are explicitly out of scope.
- `README.md`, `ROADMAP.md`, `CHANGELOG.md`, and `examples/README.md` edits are accurate against the verified diff and do not overclaim; `CHANGELOG.md`'s "Known limitations" section and `docs/getting-started.md`'s "Known limitation" note both honestly disclose the absence of a mechanically-enforced Plan→Implementation human-approval Gate rather than implying one exists.
- `tdd-evidence.yml`'s four cycles (TDD-001A, TDD-001B, TDD-002, TDD-003) and the disclosed TDD-002-companion-without-its-own-RED were independently cross-checked against the pre-image code and the actual test diffs; every RED claim is plausible given what the pre-image `_gate_instructions`/`adapter_cli.py::install`/`doctor/__init__.py::diagnose` code could and could not do, and every cited failure signature (`AssertionError` on a missing branch, an empty `adapter_checks` dict, `DID NOT RAISE`) is a legitimate RED reason under C-011, not a syntax/fixture/environment failure.
- Requirement/Non-goal boundaries (no `protocol/` change, no new lifecycle CLI command, no new root dependency) are all independently confirmed true, not merely asserted.

### Verdict

**REQUEST CHANGES**

Finding counts (this Iteration):

- BLOCKER: 1 (CHG-0014-R001)
- MAJOR: 1 (CHG-0014-R002)
- MINOR: 1 (CHG-0014-R003)
- OBSERVATION: 0 (four positive observations recorded above are not Findings)

Per C-027/C-035, Completion MUST NOT proceed with an unresolved BLOCKER Finding present, and per `blocking: [blocker, major]` the MAJOR must also be resolved. CHG-0014-R001 blocks even attempting a `passed` Review Iteration today, independent of the Implementation's own quality — it is a workspace-hygiene precondition, not a defect in the reviewed diff, but Protocol 2's freeze invariant does not distinguish the two and this repository's own validator confirms that mechanically. CHG-0014-R002 is a genuine, reproducible defect inside the reviewed diff itself and must be fixed (or the aggregation's status mapping otherwise corrected to preserve `warning` fidelity) with regression coverage added for the `warning` path before the next Review Iteration. CHG-0014-R003 does not block Completion by itself but should be addressed alongside the others.

This Iteration is recorded with `status: failed` and no `reviewer_provenance`-gated pass condition is asserted; `review.status` remains `failed` (not `passed`) in `manifest.yml`, and `state.current` remains `strict_review` — Completion has not been evaluated and is not claimed by this Review.
