# ADR-0015 — Interaction Language Resolution

Status: Accepted for CHG-0017 Implementation; independent Strict Review pending.

## Decision

Forge gains an optional, additive `interaction.language` field on
`forge/project@1` (`protocol/schemas/project.schema.json`), four new
binding Contract rules (`C-070`–`C-073`,
`protocol/contract/engineering.md` and
`protocol/versions/2/contract/engineering.md`), and a new
`protocol/specification.md` §42 defining a three-level precedence chain
for which human language a Harness should use when interacting with a
developer: explicit project configuration → Harness-observed chat hint →
English fallback.

`ROADMAP.md`'s original sketch proposed a four-level chain, inserting a
"repository/context language" heuristic level between explicit
configuration and the chat hint, and explicitly left open which of its
levels were deterministic configuration versus Harness-only hints. That
question is this ADR's `DEC-001` (`product`/`contract` class,
non-negotiable `human` Authority floor per
`protocol/policies/decision.yml`): resolved by explicit human decision in
favor of the three-level chain (Alternative A). The fourth level is
deferred, not built, because no deterministic, offline mechanism exists
for inferring a repository's interaction language from its content — any
heuristic (reading README/comment/commit-message language) has no single
correct answer, and a wrong silent guess is a worse outcome than falling
through honestly to the next level. Building such a heuristic now would
also be disproportionate to a Change the ROADMAP itself names as the
smallest of the four items remaining before v1.

Interaction language governs prose only. Canonical identifiers — schema
keys, Change and requirement identifiers, Gate names, Contract rule
identifiers — remain invariant regardless of configured interaction
language (C-070), and Gate semantics do not vary by it (C-071).
Deterministic project configuration takes precedence over any
Harness-observed signal (C-072). Neither C-072 nor C-073 (Harness
honesty: an Adapter projecting this guidance MUST NOT claim to guarantee
the Harness's actual output language) is validated by `forge validate` —
Core can project an instruction; it cannot observe or verify a live chat
session, matching C-067's own disclaimer for a different, prior concern.

A Harness Adapter projects the effective instruction directly, reusing
the same generic pipeline `CHG-0016` established for Contract/Flow
content: `AdapterProjectionContext` and `CodexProjectionInput` both gain
`interaction_language: str = ""` as an additive default, so every caller
that predates this Change continues to build the same output it always
did. Unlike `CHG-0016`'s `artifact_structure_content` (a static canonical
document projected as its own `references/*.md` resource), this value is
a small, project-specific scalar — it is rendered as one interpolated
instruction line inside the existing `SKILL.md` body (`DEC-002`,
`architectural` class, resolved autonomously), not as a new resource
file. No RFC accompanies this ADR, matching `CHG-0013`'s and `CHG-0016`'s
own precedent for the same F-008 evaluation: this is additive
configuration and Contract guidance, not a foundational Protocol
redefinition.

## Consequences

A project can express an interaction-language preference through
ordinary, schema-validated configuration, and a Codex session receives an
unambiguous, Contract-traceable instruction reflecting it — without
Forge Core ever claiming to verify what a Harness actually produced in a
live chat (INV-001, this Change's own Specification), and without any
canonical, machine-readable identifier ever becoming translatable. The
repository/context heuristic level named in `ROADMAP.md`'s original
sketch remains genuinely unimplemented — an honest, documented gap rather
than a silently narrowed promise — and is revisitable as its own future
Change if a deterministic mechanism for it is ever demonstrated, not
merely proposed. Every historical manifest in this repository
(`CHG-0001`–`CHG-0016`) continues to validate with zero new findings,
confirmed directly, not assumed.
