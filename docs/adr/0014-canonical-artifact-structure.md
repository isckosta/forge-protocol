# ADR-0014 — Canonical Artifact Structure

Status: Accepted for CHG-0016 Implementation; independent Strict Review pending.

## Decision

Forge gains a new canonical file, `protocol/artifact-structure.md`,
providing non-binding guidance for the information architecture of human
Forge Artifacts — Progressive Disclosure, Artifact Responsibility,
Result-Before-Evidence, Scanability, Proportionality, and Extensibility —
plus recommended structural core/conditional/optional sections per
Artifact type. It lives beside `protocol/specification.md`,
`protocol/compatibility.md`, and `protocol/contract/engineering.md` — same
authority tier, same prose style — rather than as a new Policy YAML
schema: it governs a human/agent reader's document, not machine-validated
governance data, so it does not fit the shape `protocol/policies/*.yml`
files share.

The motivation is measured, not speculative: comparing `CHG-0001` against
`CHG-0015`, this repository's own Verification `## Result` heading —
present at the start of `CHG-0001/verification.md` — is absent from
`CHG-0015/verification.md`, whose PASS/FAIL outcome exists only inside a
prose evidence paragraph and in `manifest.yml`. The convention existed and
regressed, rather than never having existed. Total Artifact Markdown
volume across a Change also grew roughly 2.7x over the same span without
a proportional increase in declared semantic complexity.

Conformance to `protocol/artifact-structure.md` MUST NOT be treated as a
Gate condition (`protocol/contract/engineering.md` C-067) — this was the
one genuinely material, `contract`-class Unresolved Decision this Change
recorded (`DEC-001`, Specification), resolved by explicit human decision
in favor of guidance over enforcement: no new integer Protocol, no new
`forge validate` check, no historical Change (`CHG-0001`–`CHG-0015`)
becomes non-conforming. Two further additive Contract rules recommend,
without mandating, outcome-first Verification/Review presentation
(C-068) and that an approved Plan not silently absorb Implementation-time
discoveries (C-069) — the latter naming, as a canonical, always-last
`## Implementation Boundary` section, a paragraph two prior Changes
(`CHG-0013`, `CHG-0015`) had each independently hand-written under an
ad-hoc "Explicit boundary" heading.

A Harness Adapter projects the guidance by reference, the same mechanism
already used for Flow and Contract content: the Codex Adapter's
`generate_codex_skill_bundle` gained one additional optional resource,
`references/artifact-structure.md`, included only when the canonical file
resolves — `AdapterProjectionContext` and `CodexProjectionInput` both
carry the new field as an additive default, so every caller that predates
this Change continues to build the same resource set it always did. No
RFC accompanies this ADR, matching `CHG-0013`'s own precedent
(`docs/adr/0012`) for the same F-008 evaluation: this is additive
guidance, not a foundational Protocol redefinition.

## Consequences

Forge Artifacts gain a single, canonical, non-binding reference for how
they should organize what they present to a human reader — without
becoming a Markdown linter (`forge validate` performs no new check),
without forcing FAST to inherit ceremony (`inspection.md` stays
proportional by design, §4), and without inventing structure this
repository's own real history does not already support: the guidance
recognizes existing, stable conventions (`FR/NFR/SEC/INV/CON-xxx`,
`DEC-xxx`, `## Iteration N — <verdict>`, flat numbered Plan work lists)
rather than replacing them with untested ideals. Whether agents actually
follow non-binding guidance without a Gate behind it is an open bet, not
a guarantee this ADR makes — `DEC-001`'s Specification record names this
explicitly as the accepted risk, revisitable as its own future Change if
guidance alone proves insufficient. Every historical manifest in this
repository (`CHG-0001`–`CHG-0015`) continues to validate with zero new
findings, confirmed directly (`verification.md`), not assumed.
