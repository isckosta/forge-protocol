# Forge Protocol

This directory contains the canonical Forge Protocol. The Protocol defines Forge semantics independently from the official CLI and individual coding Harnesses.

## Canonical areas

- `contract/` — non-negotiable engineering invariants.
- `flows/` — canonical Change lifecycle definitions.
- `policies/` — baseline engineering policies.
- `schemas/` — machine-readable artifact schemas.
- `specification.md` — normative Core Protocol specification.

## Protocol versus workspace

`protocol/` defines Forge. `.forge/` configures Forge for a repository. Project configuration may specialize behavior only where the Protocol allows and may not weaken canonical Contract invariants.

## Normative language

`MUST` and `MUST NOT` are requirements. `SHOULD` and `SHOULD NOT` are strong recommendations requiring explicit reasoning when ignored. `MAY` represents optional behavior.
