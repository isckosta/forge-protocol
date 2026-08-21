---
forge:
  artifact: discovery
  schema: 1
change: CHG-0021
status: complete
---

# Discovery — Adapter Reference Schema Projection

## Executive Summary

The two `forge validate` rejections reported by CHG-0001's external
validation report are both real, both correctly enforced, and both
invisible to an agent that only has a Harness Adapter installed. The
strongest finding: one of the two rules the report blames on "no
projected Schema" (`resolved_via`) is **already** present in
`protocol/schemas/change-v2.schema.json` — the gap is that this JSON
Schema file itself is never projected or referenced by either Adapter,
not that the rule is undocumented anywhere. The other rule
(`class` → `owning_artifact`, and `class` → authority floor) genuinely
exists **only** in Python — `protocol/schemas/change-v2.schema.json`
does not encode it at all. This split changes the shape of the fix: a
single Markdown reference generated from the Python constants (which are
the authoritative source for both rules already, whether or not the JSON
Schema also happens to encode one of them) closes both gaps uniformly,
without requiring a second, structurally different fix for each.
Recommendation: build that reference and project it into both Adapters,
rather than projecting the raw JSON Schema files.

## Where each rule actually lives

### `resolved_via`

`protocol/schemas/change-v2.schema.json:93` already declares
`"resolved_via": {"enum": ["evidence", "autonomous_decision",
"human_decision", null]}`. `src/forge_cli/validation/__init__.py:369`
independently declares the same three-value set (excluding `null`, which
the Python check treats separately via `is not None`) as
`_DEC_RESOLVED_VIA`. Both already agree; the enum is not undocumented,
it is unprojected. The CHG-0001 report's own text is consistent with
this ("o enum real ... só existe no `.py` do pacote instalado ... e no
JSON Schema ... nenhum dos dois presente nos `references/`").

### `class` → `owning_artifact`, and `class` → authority floor

`src/forge_cli/validation/__init__.py:370` (`_DEC_OWNING_BY_CLASS`) and
`:371` (`_DEC_AUTHORITY_FLOOR`) have no JSON Schema counterpart at all:
`change-v2.schema.json`'s `owning_artifact` property (line 91) is typed
as a free, unconstrained string, and `authority` (line 90) is a flat
three-value enum with no per-`class` conditional. `grep -n
"owning_artifact_by_class\|authority_floor"
protocol/policies/decision.yml` shows the same mapping stated a third
time, in prose-adjacent YAML form, as policy — a third representation of
one rule, none of which the Adapter projects.

## Two candidate fixes, and why the narrower one wins

**Candidate A** — promote `_DEC_OWNING_BY_CLASS` and
`_DEC_AUTHORITY_FLOOR` into `change-v2.schema.json` via an `allOf`/`if`/
`then` conditional per `class`, mirroring the existing `status` →
`resolved_via` conditional already at schema line ~99. This would make
the JSON Schema itself the single normative source for every Decision
structural rule, and "project the schema" would then be a complete fix
for all of them uniformly.

**Candidate B** — leave `validation/__init__.py`'s constants exactly as
they are (already tested, already the actual enforcement path
regardless of what the JSON Schema says), and generate a derived
Markdown reference from those constants for projection.

Candidate A is rejected for this Change: it changes
`protocol/schemas/change-v2.schema.json`, a Protocol schema file, which
`CONTRIBUTING.md`'s RFC requirement ("Protocol interoperability")
treats conservatively and separately from an ordinary behavioral fix; it
also does not, by itself, solve the projection gap — a promoted schema
rule would still need to reach `references/` through some Adapter
mechanism, the same mechanism Candidate B needs regardless. Candidate A
remains a legitimate future direction and is recorded as such in
Knowledge Capture, not discarded.

## Existing precedent to reuse, not reinvent

`CHG-0016` (`canonical-artifact-structure`) already solved the identical
shape of problem for a different reference
(`protocol/artifact-structure.md`): both Adapters thread an optional
`*_content: str = ""` parameter through
`AdapterProjectionContext` → each Adapter's `driver.py` → each Adapter's
`generate_*_projection_bundle`, with additive-only inclusion (`has_*`
gates both the resource and its reference link). `grep -rn
artifact_structure src/forge_cli` confirms the exact call chain:
`protocol_resolution/__init__.py:141`
(`resolve_effective_artifact_structure`) →
`adapters/service.py:445,612` → `adapters/driver.py:20`
(`AdapterProjectionContext.artifact_structure_content`) →
`adapters/{codex,claude_code}/driver.py:46` →
`adapters/{codex,claude_code}/projection.py`. This Change's own resource
should follow the same chain shape for the same reason CHG-0016 did:
consistency, and a caller that does not opt in sees unchanged output.

One difference matters: `resolve_effective_artifact_structure` resolves
*file content* from `protocol/` (with a versioned-root fallback,
because `protocol/artifact-structure.md` is itself a maintained prose
document). This Change's content has no such file — it is *rendered*
from Python data that already lives in `validation/__init__.py`, always
available in the installed package, with no versioned-root concept to
fall back through. The new function is a renderer, not a file resolver,
and does not need `resolve_effective_artifact_structure`'s fallback
logic.

## A real constraint: import direction

`src/forge_cli/validation/__init__.py:10` already imports from
`forge_cli.protocol_resolution` (`resolve_effective_contract`,
`resolve_effective_flow`, etc.). `src/forge_cli/protocol_resolution/__init__.py`
imports nothing from `forge_cli.validation`. Placing the new renderer
inside `protocol_resolution` (the module whose existing naming
convention, `resolve_effective_*`, would otherwise fit best) and having
it import the constants from `validation` would invert that edge and
create an import cycle: `validation → protocol_resolution → validation`.
This is a real constraint discovered here, not a stylistic preference,
and is carried into Architecture as the basis for DEC-001.

## Flow Classification Finding

FULL, on direct precedent: `CHG-0016` is the closest real analog in this
repository's own history — adding one new derived reference, projected
into both Adapters' `references/`, with the accompanying skill-link and
resource-inclusion changes — and it also classified FULL (its own
Classification section reasons in prose, "FAST is inapplicable
(multi-file, cross-module, normative-guidance change)", without naming a
specific `fast.yml` disqualifier by id). This Change's own, independent
reasoning names the disqualifier explicitly: `protocol/flows/fast.yml`
lists `significant_cross_module_change`, and this Change touches
`validation`, both Adapters' `projection.py`, both Adapters' `driver.py`,
and `adapters/driver.py`/`adapters/service.py` — five modules, matching
that disqualifier on its own terms independent of what CHG-0016's prose
said. The projected `references/` surface is also consumer-facing across
every project that installs either Adapter, and `protocol/flows/standard.yml`
has no `specification_review` stage at all, so FULL is the only canonical
Flow under which this Review is even a required Gate. See
`specification.md` for the full classification statement.

## Compatibility Finding

Additive only. No existing field, resource name, or projection bundle
member changes shape; a caller that does not pass the new content
parameter is unaffected, matching `CHG-0016`'s own compatibility
contract for `artifact_structure_content` (`tests/unit/
test_claude_code_projection_bundle.py`'s and `tests/unit/
test_codex_projection_bundle.py`'s existing "omits when not provided"
tests already establish and protect this shape for the sibling
resource; this Change's tests follow the identical pattern for the new
one).

## Documentation Impact Signal

`CHANGELOG.md` (new entry), `ROADMAP.md` (no stage exists yet for this
work — it originates from the post-CHG-0001 external-validation
remediation plan, outside the current roadmap stage list; no existing
roadmap section needs a status flip). No ADR: this is an additive
Adapter-Core mechanism reusing an already-adopted pattern
(`CHG-0016`), not a new long-lived Architecture Decision in the sense
`CONTRIBUTING.md`'s ADR requirement targets.

## Baseline (pre-Implementation)

Recorded at `HEAD d102d664b452e17b4cf6b747bf012731655aa737` (tip of
`main`, `CHG-0020` complete): `pytest -q` → 524 passed, 0 failed;
`forge validate` → "Forge project is valid", exit 0; `forge doctor` →
7/7 checks PASS (one non-blocking `migration_available` WARN,
pre-existing and unrelated to this Change).
