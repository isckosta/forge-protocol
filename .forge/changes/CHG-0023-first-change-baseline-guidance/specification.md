---
forge:
  artifact: specification
  schema: 1
change: CHG-0023
status: active
---

# Specification — First-Change Baseline Guidance

## Summary

Adopt RFC-0003's first-commit baseline invariant as C-076 in the Engineering
Contract, and add concise projection guidance to both current Adapter
workflow templates. Demonstrate the invariant in a clearly labeled
realistic `examples/` fixture.

## Classification

**FULL.** This Change materially updates the canonical Engineering Contract,
requires RFC-0003, changes two Adapter projections, and adds a durable
example of a lifecycle precondition. `protocol/flows/full.yml` requires the
adversarial Specification Review, Architecture, Test Strategy, Plan, Tasks,
Verification, Strict Review, Documentation, and Knowledge Capture stages for
this high-impact process change. FAST is not appropriate for a canonical
Contract change; STANDARD lacks the required `specification_review` stage.

## Functional Requirements

### FR-001

Both `protocol/contract/engineering.md` and the effective Protocol 2 Contract
at `protocol/versions/2/contract/engineering.md` MUST contain identical C-076
semantics: when a Change is conducted in a repository with no prior Git
commit, the complete pre-existing state within the declared intended
repository scope MUST be committed as one baseline commit, with no file
excluded, before Implementation begins. The baseline is the before-state,
not Implementation, and subsequent Change commits MUST be reviewable as the
delta from that baseline. If operational or generated material is
intentionally outside the scope, that scope MUST be declared before the
baseline is committed.

### FR-002

Both `src/forge_cli/adapters/codex/resources/skills/workflow.md` and
`src/forge_cli/adapters/claude_code/resources/skills/workflow.md` MUST
project explicit, concrete guidance for the first-commit baseline rule. The
guidance MUST identify the complete-state/no-exclusion requirement and MUST
not claim that the Adapter technically enforces Git behavior.

### FR-003

`examples/` MUST contain a clearly labeled realistic demonstration showing a
pre-existing repository state, a complete baseline commit before
Implementation, and a later Implementation commit whose diff is measured
from that baseline. The demonstration MUST state that it is illustrative if
it is not a curated real Git history and MUST follow the conventions in
`examples/README.md`.

### FR-004

The Change MUST preserve existing Flow, TDD, Review, Adapter, and repository
authority semantics. It MUST NOT alter `protocol/schemas/*.json`, the CLI
surface, or the concurrent `change-scaffolding-cli` work.

## Non-functional Requirements

### NFR-001

C-076 MUST remain provider-independent and Harness-agnostic. The rule
specifies required repository state/evidence; projection is guidance and
cannot be described as technical prevention.

### NFR-002

The two Adapter workflow templates MUST remain semantically identical for
this guidance so Codex and Claude Code receive the same rule.

## Security Requirements

None. The Change improves evidence integrity and adds no authentication,
authorization, credential, network, or filesystem enforcement surface.

## Constraints / Invariants

### CON-001

No file under `protocol/schemas/` changes.

### CON-002

`src/forge_cli/app.py`, `src/forge_cli/adapter_cli.py`, and any new
`forge change` command remain untouched.

### CON-003

The RFC MUST precede the Contract implementation. RFC-0003 is the recorded
normative decision and this Specification MUST NOT silently replace it.

## Acceptance Criteria

- **AC-001** (FR-001): Contract validation and a focused repository test
  confirm both effective Contract files contain C-076 with one complete
  baseline, declared scope, no-exclusion, before-Implementation, and
  baseline-to-delta requirements.
- **AC-002** (FR-002, NFR-001): both workflow-resource tests observe the
  explicit guidance in the packaged templates and confirm it does not claim
  technical enforcement.
- **AC-003** (FR-003): the example contains an explicit pre-existing file
  inventory, a complete baseline commit step before Implementation, and a
  baseline-to-Implementation diff explanation; its illustrative status is
  visible to readers.
- **AC-004** (FR-004, CON-001, CON-002): the diff contains no schema, CLI,
  scaffolding-command, or unrelated remediation-item changes.
- **AC-005** (NFR-002): the Codex and Claude Code workflow templates carry
  byte-identical baseline guidance.
- **AC-006** (Documentation Impact): `examples/README.md` indexes the new
  example, `ROADMAP-REMEDIATION.md` marks item #3 done with the real Change
  link, and Knowledge Capture records the durable lesson.
- **AC-007**: full `pytest`, `forge validate`, and `forge doctor` results
  remain green, with any pre-existing warnings called out rather than
  silently treated as failures.

## Out of Scope

See `intent.md` for the full exclusion list. In particular, this Change does
not implement baseline automation, modify schemas, or touch CHG-0022's CLI
files and command work.
