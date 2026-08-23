---
forge:
  artifact: inspection
  schema: 1
change: CHG-0029
status: complete
---
# Inspection — CHG-0029 Artifact Publication Suggestion

## Evidence

- `src/forge_cli/adapters/claude_code/resources/skills/workflow.md` and
  `src/forge_cli/adapters/codex/resources/skills/workflow.md` were identical
  at the start of the Change and contained no suggestion to publish
  `review.md` or `specification.md` as a shareable Artifact.
- Claude Code has a real Harness-native Artifact capability: Anthropic's
  documentation describes publishing Claude Code session output as a
  shareable page, with permission and visibility constraints. This confirms
  that the Harness can expose a shareable session output, but does not prove
  that every Markdown file is automatically publishable as an Artifact.
- The Codex Adapter has a `publication.yml` and publication-target resolution
  for publishing its generated local resources. That is Adapter resource
  publication, not evidence of a Codex Harness mechanism for publishing a
  shareable session Artifact. No such shareable-Artifact mechanism is
  established by the current Codex Adapter resources or repository evidence;
  the guidance must therefore not promise one.

## Flow Classification

**FAST.** This is localized prose-only guidance in two parallel templates. It
does not touch architecture, security, authorization, domain invariants,
integration, public contracts, runtime behavior, Flow/Gate semantics, or
validation. Those are the FAST disqualifiers in `protocol/flows/fast.yml`;
none applies. FAST still requires Verification, Strict Review, Documentation
Impact, and an honest TDD exception.

## Recommendation

Use one Harness-neutral conditional sentence in both templates: when the
active Harness supports shareable session Artifacts, offer to publish the
relevant complete `review.md` or `specification.md` at the relevant stage;
otherwise point the human to the repository-native file. Confidence:
**High** for the non-binding, conditional guidance; **High** that the Codex
Adapter's local publication target must not be presented as a shareable
session Artifact mechanism.

## TDD Applicability

Not applicable. The Change adds Markdown guidance only and introduces no
executable behavior or enforced Protocol rule.
