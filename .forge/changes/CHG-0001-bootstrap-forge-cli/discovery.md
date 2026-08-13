---
forge:
  artifact: discovery
  schema: 1
change: CHG-0001
status: approved
---

# Discovery — Bootstrap Forge CLI

## Current state

Forge Foundation provides the Core Protocol, Engineering Contract, canonical Flows, TDD-first Policy, Strict Review Policy, Schemas, Architecture Decisions, and project dogfooding configuration.

No Python package or executable CLI exists.

## Architectural constraints

- The CLI is not the development runtime.
- No LLM provider dependency.
- Filesystem is the source of truth.
- Canonical Protocol and project configuration remain separate.
- All reasonably testable executable behavior developed in this Change follows Forge TDD.
- Forge v1 operates on Git repositories.

## Candidate stack

- Python 3.12+
- Typer for CLI declaration
- Pydantic for internal structured models where useful
- Rich for terminal presentation
- Pytest for executable tests
- `pathlib` for filesystem handling

## Excluded dependencies

AI SDKs, databases, web frameworks, Agent frameworks, and Git libraries unless later evidence justifies them.

## Git interaction

Prefer the installed `git` executable through subprocess argument arrays. Shell interpretation should not be required.

## Protocol resolution

Canonical Flow and Contract definitions remain authoritative within the installed Forge distribution. Project files reference or extend canonical concepts without duplicating authoritative definitions.

## Risks

### CLI scope expansion
The CLI must not accumulate lifecycle commands such as `forge specify`, `forge implement`, or `forge review`.

### Destructive initialization
`forge init` must preserve existing repository state and avoid partial successful-looking initialization.

### Schema drift
CLI compatibility and Protocol compatibility must remain explicit.

### False TDD
Tests generated after Implementation must not be recorded as RED evidence.

### Configuration ambiguity
Canonical Protocol, project configuration, and Harness Adapter representation must have explicit precedence and responsibilities.

## Conclusion

A small deterministic Python CLI is justified. A larger runtime is not.
