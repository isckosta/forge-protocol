# The Capability Contract

Status: Foundation (introduced by `CHG-0047`). This document defines the
minimal contract a `CAPABILITY.md` definition must satisfy. It is a
human-readable contract, not a JSON Schema — see [`README.md`](README.md)
for what a Capability is and is not, and for the architectural boundaries
this contract does not relax.

A `CAPABILITY.md` is not a `SKILL.md`. It is the canonical, Harness-
independent definition of a competency; a `SKILL.md` (or any other
Harness-specific representation) is an adaptation a Harness Adapter
derives from it, not a substitute for it.

## Minimal frontmatter

Every `CAPABILITY.md` starts with a small identity frontmatter block:

```markdown
---
capability: investigate
schema: 1
---
```

- `capability` — the Capability's stable identifier (lowercase,
  hyphen-free by convention, matching its directory name under
  `capabilities/`).
- `schema` — an integer versioning this contract's shape, so a future,
  incompatible revision of the contract can be introduced without
  silently reinterpreting an existing definition.

No other frontmatter field is part of this contract. A concrete
definition MAY carry additional prose elsewhere in the file, but nothing
beyond `capability` and `schema` is required or parsed by the loader.

## Required sections

After the frontmatter, a `CAPABILITY.md` MUST contain each of the
following sections as a `##` heading, in any order, each with non-empty
content:

### `## Identity`
A short, unambiguous statement of what this competency is called and
what it is, in one or two sentences. Not a restatement of the frontmatter
`capability` id — the human-readable name and framing.

### `## Purpose`
Why this competency exists and what problem it addresses. States the
value it provides, not the steps it takes (that belongs to Behavior).

### `## Applicability`
When this competency legitimately applies, and — as important — when it
does not. A Capability that does not state its own boundaries invites
misuse by whatever invokes it.

### `## Inputs`
What this competency needs to operate: what it reads, what context it
requires, what must already exist before it can run. Not a formal
parameter schema — a plain description sufficient for a reader (human or
agent) to know what to gather first.

### `## Behavior`
What this competency actually does, described at a level a reader can
follow and a reviewer can check against — without redefining Flow,
lifecycle, or Gate semantics, which remain Core/Flow's authority
regardless of what a Capability's Behavior section says.

### `## Outputs`
What this competency produces: artifacts, findings, decisions proposed
(not decisions made — see the Architectural boundaries in `README.md`),
or other observable results.

### `## Evidence Expectations`
What a run of this competency is expected to leave behind so its result
is checkable later — consistent with Forge's repository-native evidence
principle (`README.md`). This section states an expectation, not an
enforcement mechanism; enforcing it, where warranted, is a CLI, CI, or
hook concern outside the Capability itself.

## What this contract deliberately does not require

- A formal input/output schema (JSON Schema or otherwise) — prose is
  sufficient until a concrete need demonstrates otherwise.
- An execution protocol, a composition mechanism, or a dependency
  declaration between Capabilities.
- A Harness-specific field of any kind (nothing naming Claude, Codex, or
  Cursor). A Capability that needs Harness-specific behavior belongs to a
  Harness Adapter's derived representation, not to the canonical
  definition.
- A lifecycle status, an authority field, or a Gate reference. A
  Capability does not carry Change lifecycle state — it is not a Change
  Artifact.

## Example skeleton

```markdown
---
capability: example
schema: 1
---

# Capability — Example

## Identity
One or two sentences naming and framing this competency.

## Purpose
Why this competency exists.

## Applicability
When it applies, and when it explicitly does not.

## Inputs
What it needs before it can run.

## Behavior
What it does.

## Outputs
What it produces.

## Evidence Expectations
What a run of it should leave behind.
```

This skeleton is illustrative only — it defines no real Capability and is
not consumed by any code.
