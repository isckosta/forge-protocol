# Intent — Interaction Language Resolution

## Summary

Forge's canonical implementation language is English: Protocol, source,
schemas, identifiers, and canonical Forge repository documentation are all
English-first, and this Change does not touch that. What is currently
undefined is the language used to *interact* with a developer through a
Harness chat — the prose Forge-generated Artifacts, and the prose a
developer reads back from the Harness, have no configured or resolvable
language at all today; whatever a Harness session happens to produce is
the only "answer."

This Change introduces **Interaction Language Resolution**: an optional,
additive project configuration field (`interaction.language`) and a
Contract-governed precedence rule for how a Harness should resolve which
human language to use, while keeping every canonical, machine-readable
identifier (schema keys, Change/requirement IDs, Gate names, Contract rule
IDs) invariant regardless of that choice.

## Problem

`ROADMAP.md` ("Interaction Language Resolution") names this as the next
unstarted item in the v1 execution order, and states the objective
directly: "Separate Forge's canonical implementation language from the
language used to interact with the developer." It proposes a
configuration shape (`interaction: {language: auto}`) and a four-level
precedence sketch (explicit project language → repository/context
language → active user/chat language → English fallback), then explicitly
defers the hard part: "The Specification must determine which signals are
deterministic configuration and which are only Harness hints."

That deferred question is real, not rhetorical. Forge Core is a local,
offline CLI plus a repository-native Protocol (`protocol/specification.md`
§2, §33) — it has no access to the live chat session at the time a
project is configured, and no reliable, deterministic, offline way to
infer a "repository/context language" from arbitrary project content
(READMEs, comments, and commit messages are not a language signal with a
single correct answer, and guessing wrong silently would be worse than not
guessing).

Without this Change, `interaction.language` does not exist as a concept
anywhere in the Protocol, schemas, or Adapter projection — a project has no
way to state a language preference at all, and nothing prevents a future
Adapter or Contract change from inventing an ad hoc, incompatible
mechanism for the same need.

## Desired Outcome

A project can declare `interaction.language` in `.forge/forge.yml`. A
Codex session opened against that project receives an explicit,
Contract-backed instruction describing which language to interact in and
why — deterministically, if the project configured one; otherwise falling
back to whatever language signal the Harness itself can observe, with
English as the final fallback if neither is available. No canonical
identifier, schema key, Gate name, or Contract rule ID ever changes
because of this. No developer needs to manually restate a language
preference in every chat.

## Scope

- An optional, additive `interaction.language` field on `forge/project@1`
  (`protocol/schemas/project.schema.json`).
- New Contract rules governing what interaction language *may* and *may
  not* affect (canonical identifiers, Gate semantics, precedence over
  heuristic signals, honest limits on what Core can verify).
- A new `protocol/specification.md` section defining the concept and its
  precedence chain.
- Codex Adapter projection support so a configured (or default `auto`)
  interaction language is surfaced to a Codex session without any new
  Codex-specific concept being introduced into the generic Adapter Core.

## Out of Scope

- Any heuristic, repository-content-based language detection performed by
  Forge Core itself (the ROADMAP's "repository/context language" level).
  Deferred; see the accompanying ADR (`docs/adr/0015-interaction-language-resolution.md`)
  for the Decision record.
- Translating any canonical Protocol document, schema, or this
  repository's own English-language Artifacts.
- Any new Flow, lifecycle stage, Finding severity, Review convergence
  rule, or Unresolved Decision Management semantic change.
- A second Harness Adapter (a separate, later ROADMAP item).

## Success Criteria

See `specification.md` for concrete, verifiable Acceptance Criteria. At
Intent stage, success means: a project can express an interaction-language
preference through ordinary, schema-validated configuration; a generated
Codex projection carries an unambiguous, Contract-traceable instruction
reflecting that preference (or its `auto` default); and no existing
project, schema, or historical Change is invalidated by the addition.
