# RFC-0008 — Behavioral User Story Slices

Status: Proposed for Protocol 2

## Summary

This RFC proposes making User Stories mandatory only for Changes whose
Specification introduces or changes behavior observable by an actor. Each
Story is a stable `US-xxx` first-person outcome slice with local Acceptance
Criteria. Requirements remain the normative units of the Specification and
may relate to zero, one, or many Stories.

## Decision proposed

1. Add the explicit `change.observable_behavior` marker to Protocol 2 Change
   manifests.
2. Require at least one stable Story in a behavioral Specification and allow
   technical Changes to omit Stories.
3. Preserve Story-to-Requirement many-to-many links and add conditional
   Story-to-Task and Story-to-Verification links from Implementation onward.
4. Generate `tasks.md` and `traceability.yml` for behavioral STANDARD
   scaffolds; retain the existing FULL Tasks stage.
5. Validate only repository-native identifiers and evidence boundaries. Do not
   heuristically score Story prose quality.
6. Keep historical manifests without the explicit marker valid.

## Compatibility

The marker is optional for historical manifests. Existing Requirement
traceability remains authoritative and no Story is synthesized for technical
or FAST Changes without a Specification stage.

## Approval

This RFC records the material Protocol decision required by F-008. It is not
approved by an agent; a human authority must record approval before the Change
may cross the Plan/Implementation governance boundary.
