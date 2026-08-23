---
forge:
  artifact: discovery
  schema: 1
change: CHG-0037
status: complete
---

# Discovery — CHG-0037 Specification Layout User Story Traceability

## Executive Summary

The repository already separates normative semantics from presentation: Protocol/Contract define Requirements and Acceptance, while `protocol/artifact-structure.md` is explicitly non-binding guidance under C-067. The safe evolution point is therefore the guidance and scaffold, not a Markdown parser or Change Schema extension.

## Investigation

### Repository authorities

- Active project Protocol is 2; Protocol 1 remains frozen for historical instances.
- `.forge/forge.yml` selects STANDARD by default, with canonical FAST/STANDARD/FULL project Flow files.
- `src/forge_cli/change_scaffolding.py` owns Specification generation.
- `forge validate` validates repository-native YAML state, schemas, Flow, Decisions, and provenance; it does not parse Specification Markdown.
- `protocol/schemas/change-v2.schema.json` contains only aggregate Requirement counters, while `traceability.yml` maps Requirements/Acceptance to Plan tasks and remains independent.
- Harness Adapter resources project canonical guidance; no adapter consumes Specification headings as a parser contract.

### Compatibility finding

Historical Specifications use both `Acceptance Criteria` and local layouts. They must not be rewritten. Adding optional User Stories and a new scaffold layout preserves their validity because C-067 makes artifact structure guidance non-binding and no existing validator depends on these headings.

### Flow classification

STANDARD is sufficient: the behavior is localized to scaffold rendering and documentation guidance, with no Protocol semantic, Schema, Gate, or Adapter execution change. TDD applies to the renderer.
