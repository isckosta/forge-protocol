## Forge Workflow Instructions

Repository-native Forge state remains authoritative. Use the effective Flow and
Engineering Contract references in this skill as derived, repository-local
representations; do not redefine their lifecycle here.

- Classify the work and resolve the applicable effective Flow before acting.
- Preserve every applicable Flow gate, including TDD RED-before-behavior and
  Strict Review requirements.
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
stage transitions—such as Discovery, Implementation, Verification, and Review
completion—rather than a status message for every command or tool call. Keep
the detailed record in `.forge/changes/.../` artifacts; narrate intermediate
steps when they need human input, change scope, or surface a blocker. This is
a communication suggestion, not a technical enforcement mechanism.
These instructions represent Forge requirements; they are not technical enforcement.

Skill discovery limitation: after `forge adapter install`, the Harness may not refresh its skill catalog in the current session. This is Harness runtime behavior, not technically controlled by Forge. If the `forge` skill is not
available yet, read this `SKILL.md` directly or retry in a later turn/session.
