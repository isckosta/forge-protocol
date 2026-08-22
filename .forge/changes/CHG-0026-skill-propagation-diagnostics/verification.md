---
forge:
  artifact: verification
  schema: 1
change: CHG-0026
status: passed
---

# Verification — Skill Propagation Diagnostics

## Result

**PASS**

## Summary

| Check | Result |
| --- | --- |
| Install output regression | PASS |
| Codex workflow disclosure | PASS |
| Claude Code projected skill disclosure | PASS |
| Adapter command/projection matrix | PASS — 42 passed |
| Full suite | PASS with 580 passed and 2 environment-only failures |
| `forge validate` | PASS |
| Documentation Impact | PASS — roadmap item #6 updated |

## Test Evidence

- RED: the three new expectations failed against the unmodified code with 3
  assertion failures for the missing diagnostic/disclosures.
- Focused RED/GREEN selection: **3 passed** for the initial cycle and **2 passed**
  for the Claude path resolution cycle.
- Adapter command and projection matrix: **42 passed**.
- Full suite: **580 passed, 2 failed**. Both failures are the pre-existing
  distribution tests that build a wheel and cannot download isolated
  `hatchling` build dependencies because this environment cannot resolve
  PyPI; no tested behavior in this Change is involved.

## Forge Evidence

- `/home/isckosta/forge-protocol/.venv/bin/forge validate` → `Forge project is valid`.
- `git diff --check` → clean.
- The generated paths named by the install diagnostic match the published
  skill resources: `.agents/skills/forge/SKILL.md` and, for the explicit
  Claude Code target, `<target>/SKILL.md` under its publication root.

## Scope and Compatibility

The CLI still performs the same publication and installation-record writes;
only its post-install diagnostic output changed. Both Adapter templates now
disclose a possible Harness catalog delay without claiming Forge controls it.
No catalog-refresh mechanism, Contract, Schema, Doctor, scaffolding command,
or example file changed. Codex behavior remains honestly unverified in a live
Codex session.

## Conclusion

The onboarding path now explains the observed same-session discovery limitation
and provides a direct-file fallback while preserving existing Adapter behavior.
The Change is ready for independent Strict Review.
