# ADR-0019 — Capability Architecture Foundation

Status: Accepted for CHG-0047, independent Strict Review passed.

## Decision

Forge gains a new, explicit architectural layer — the **Forge
Capability** — sitting between Core/Flow (which decides *when* a
competency is needed) and Harness Adapters (which translate a Capability
into a concrete environment, e.g. a Claude Skill). A Capability is a
specialized, reusable agentic competency (investigate, review, verify
provenance, challenge a claim) defined canonically, once, in a
Harness-independent `CAPABILITY.md`, distinct from any `SKILL.md` a
Harness Adapter later derives from it.

This Change ships the foundation only: `capabilities/README.md` (the
concept, its boundaries, and how to add a future Capability) and
`capabilities/capability.md` (the minimal human contract — Identity,
Purpose, Applicability, Inputs, Behavior, Outputs, Evidence
Expectations — no JSON Schema), plus a small, generic package
(`src/forge_cli/capabilities/`: a frozen `Capability` dataclass and a
deterministic `load_capability(path)` loader: locate → read → parse →
normalize → return). No concrete Capability (`investigate` or any
other) is implemented, and no registry, executor, plugin system, or new
Gate exists — F-010 ("Forge MUST prefer explicit structures over
premature plugin systems, services, or hidden automation") is the
explicit design constraint this ADR records, not an afterthought: the
task itself named the classes to avoid (`CapabilityRegistry`,
`CapabilityExecutor`, `CapabilityPipeline`, `CapabilityGraph`,
`CapabilityProvider`), and none were introduced.

A Capability MUST NOT own or redefine Protocol lifecycle, Flow
selection, Change lifecycle, mandatory Gates, approval semantics, human
authority, or Protocol compatibility — those remain Core/Flow's
authority unconditionally. A pre-existing, unrelated module,
`src/forge_cli/adapters/capabilities.py` ("Harness capability
requirements" — whether a Harness declares support for a feature like
subagents), is untouched; `capabilities/README.md` explicitly
disambiguates the two concepts, since they share an English word but
answer unrelated questions.

The loader deliberately does **not** mirror
`protocol_resources.resolve_protocol_root`'s packaged-resource/
source-tree fallback: a Capability definition is repository-native
content of whichever Forge-enabled repository uses it (like
`.forge/changes/`), not a resource shipped inside the `forge-cli`
Python package (like `protocol/`). `pyproject.toml` is therefore
unchanged.

## Consequences

A future Change can introduce `investigate` as
`capabilities/investigate/CAPABILITY.md` and load it with the existing,
unmodified loader — no redesign of this foundation is required. A
future Harness Adapter can derive a Skill/representation from a
Capability without that representation ever becoming the canonical
source. Both extension points existed only as directions this ADR
records, not as code, at the time of this Change.

**This design withstood unusually deep adversarial pressure before
closing.** Independent Strict Review found and required correction of
defects across five Review Iterations — not in the architecture itself
(which passed unchanged from Iteration 1 onward), but in the loader's
Markdown section-parsing correctness: a schema-violating YAML key in
`tdd-evidence.yml` (twice, R-001/R-003 — the second instance introduced
by the fix for the first); a section parser that silently truncated
content at a heading-shaped line inside a fenced code block, in
successively narrower failure modes as each fix closed one case and a
fresh adversarial pass found the next — no fence-indentation tracking
(R-002), no delimiter-type tracking (R-004), no delimiter-length
tracking (R-006). Two consecutive Resolution Verifications with
material findings reached Protocol 2's Convergence Limit; the human
maintainer, presented with the four available options, selected
`new_full_review` over accepting the residual risk or reworking the
Plan — the root cause was judged narrow and well understood, not
architectural. A fresh, unrestricted Initial Review (Iteration 4) then
passed cleanly, finding only one non-blocking documentation gap in this
Change's own `plan.md` (R-008), whose fix itself required one further
scoped Resolution Verification (Iteration 5) under C-026's freeze
invariant. The practical lesson, worth recording because it will recur:
a small, focused parser is exactly the kind of code where "looks correct
after one adversarial pass" is not the same claim as "is correct" —
CommonMark's fence-closing semantics (delimiter type *and* length, not
just presence) took three independent, adversarial rounds to fully
match, each round finding a real, previously-undetected input that
silently corrupted data rather than failing loudly.
