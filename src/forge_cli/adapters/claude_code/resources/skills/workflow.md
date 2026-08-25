## Forge Workflow Instructions

Repository-native Forge state remains authoritative. Use the effective Flow and
Engineering Contract references in this skill as derived, repository-local
representations; do not redefine their lifecycle here.

### Bootstrap

- Classify the work and resolve the applicable effective Flow before acting.
- Preserve every applicable Flow gate, including TDD RED-before-behavior and
  Strict Review requirements.
- Before relying on this skill's own `references/*` for a state-changing
  decision, check the Adapter's own recorded drift state (`forge doctor` or
  `forge adapter doctor <adapter-id>`, where `<adapter-id>` is the id shown
  under this repository's own `.forge/adapters/` directory, e.g.
  `claude-code` or `codex`) — these references are generated content that can
  fall behind the canonical Forge state they project. If drift is reported,
  stop advancing on the affected reference and report it to the operator;
  do not run `forge adapter update` to self-heal without the operator's
  explicit go-ahead, since that modifies persistent repository
  configuration. A clean drift state requires no extra step.
- At a human-authority Gate, a blocked state, or a missing-evidence
  condition, report briefly: Current Change, Effective Flow, Current State,
  the Boundary reached, the Required Decision or Evidence, and the
  Next Permitted Action — not a dump of internal protocol detail beyond
  what the decision requires.
- Before modifying repository files, create or use a working branch; do not
  implement directly on `main`.
- After the Change is ready for integration, open a Pull Request against
  `main` and use that PR as the repository-native integration record.
- Before representing a Change as ready for merge, run `forge validate` and
  `forge change merge-check` for the exact Pull Request base/head subject.
  This is guidance; the required CI check is the technical enforcement.
- Unresolved review comments or conversations block merge. The agent must not
  merge or claim the Change complete while unresolved review comments remain;
  resolve applicable feedback, rerun relevant checks, and then merge through
  the Pull Request.
Before crossing the Plan/Implementation boundary on a Change adopted from
CHG-0025 onward, obtain an explicit human-authority Plan Decision and record
the operator-observed confirmation in the Plan and provenance. `status: approved` alone is not
authorization; this guidance does not technically enforce the conversation
boundary, so recorded Change state remains authoritative.
When this is the repository's first commit, commit the complete pre-existing
state in the intended repository scope, with no file excluded, before
starting Implementation. This Adapter projects the requirement but cannot
technically enforce Git behavior.
The baseline commit is the before-state, not Implementation.
Chat-cadence suggestion (non-binding): prefer concise narration at meaningful
stage transitions—such as Discovery, Implementation, Verification, and when
Review is complete—rather than a status message for every command or tool call. Keep
the detailed record in `.forge/changes/.../` artifacts; narrate intermediate
steps when they need human input, change scope, or surface a blocker. This is
a communication suggestion, not a technical enforcement mechanism.
These instructions represent Forge requirements; they are not technical enforcement.

When authoring `intent.md`, make it the structured declaration of why the
Change exists and what must be true when it ends. Start with the Change
identity heading (`# CHG-XXXX · <Change Title>`) and a one- or two-sentence
`Change Intent` callout. Use the core sections `Overview`, `Problem`, `Goal`,
`Scope`, `Out of Scope`, and `Success Criteria`; add `Business Impact`,
`Current Behavior`, `Desired Behavior`, `Expected Outcome`, `Business Rules`,
`Operational Boundary`, or references only when materially applicable.
Keep structural headings in English, write prose in the applicable interaction
language, derive only trustworthy metadata, and omit sections with no content.
Intent must not become a Discovery, Specification, Plan, repository audit, or
test plan. Preserve the YAML front matter and `schema: 1`.

Skill discovery limitation: after `forge adapter install`, the Harness may not refresh its skill catalog in the current session. This is Harness runtime behavior, not technically controlled by Forge. If the `forge` skill is not
available yet, read this `SKILL.md` directly or retry in a later turn/session.
Artifact-publication suggestion (non-binding): when a key stage completes—especially
Specification or Strict Review—and the active Harness supports shareable Artifacts,
offer to publish the relevant full `.forge/changes/.../specification.md` or
`review.md` so the human can read the detail in chat. If no such Harness mechanism
exists, point the human to the repository-native file instead; do not imply that
publishing is automatic or supported by every Harness. This is communication
guidance, not technical enforcement.
Forge Experience Reporting (FER) is optional contributor tooling. When it is
explicitly enabled, record only material observations about Forge behavior
that could help maintainers understand, reproduce, improve, or validate Forge;
do not record normal project implementation activity, every tool call, or
complete prompts/conversations/logs. Do not classify an ordinary project
defect as a Forge problem without evidence; use `uncertain` when causality is
unclear. FER is local-first, non-blocking evidence and does not create a Gate,
Review Finding, Issue, RFC, or Change.
Automatic FER capture is policy-controlled and currently limited to structured
Forge-owned Adapter conformance facts; it is not an execution log. Automatic
capture defaults to `uncertain` classification and does not prove a Forge bug.
Lifecycle, approval, workaround, and root-cause observations still require
manual contributor or Agent recording.
