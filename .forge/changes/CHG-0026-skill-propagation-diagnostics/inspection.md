---
forge:
  artifact: inspection
  schema: 1
change: CHG-0026
status: complete
---

# Inspection — Skill Propagation Diagnostics

## Finding

`src/forge_cli/adapter_cli.py:219-227` prints the successful installation
message. It currently says:

```text
{adapter_id} Adapter installed at {target}.
Open {harness} in this repository to begin a Forge-governed Change;
no further Forge-side step is required.
```

That wording gives no fallback when the Harness catalog has not refreshed.
The generated skill path is deterministic: `.claude/skills/forge/SKILL.md`
for Claude Code and `.agents/skills/forge/SKILL.md` for Codex.

The Claude Code report is direct external evidence for a same-session
discovery delay. Local code shows that both Adapters publish a skill and both
use a packaged workflow template, but this repository has no live Harness
session in which to verify Codex catalog timing. The Change therefore uses a
Harness-runtime disclosure that is explicit about uncertainty rather than
claiming a Codex-specific reproduction.

## Flow Classification

This is FAST. `protocol/flows/fast.yml` includes localized copy correction,
low-risk maintenance, and localized behavior correction, and requires only
Intent, Inspection, Test Design when behavioral, TDD Implementation,
Verification, Strict Review, Documentation Impact, and Completion. None of
FAST's disqualifiers applies: there is no architecture, security or
authorization model, domain invariant, integration, cross-module semantic
change, or public Contract/Schema change. The install output and projected
skill text are executable/generated behavior, so TDD remains applicable.

The scope touches the shared Adapter CLI output and both projected templates,
but only to disclose a Harness-runtime limitation; it does not alter the
publication or catalog mechanism. That shared surface increases the need for
focused parity tests but does not raise the semantic impact to STANDARD.

## Decision

Use a generic, explicitly non-guaranteed propagation warning in the install
output and in both projected skills. Name each generated skill path in the
install output from the Adapter's target rather than asserting that Codex and
Claude Code have identical refresh behavior. The warning must say that a
later turn/session may be required and that direct file reading is the
fallback.

## Documentation Impact

`ROADMAP-REMEDIATION.md` will mark item #6 Done and link CHG-0026 after the
independent Strict Review passes. No Contract, Schema, RFC, or mechanism-level
documentation change is required.
