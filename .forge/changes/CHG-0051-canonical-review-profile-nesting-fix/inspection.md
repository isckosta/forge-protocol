---
forge:
  artifact: inspection
  schema: 1
change: CHG-0051
status: complete
---

# CHG-0051 · Inspection

## Root Cause

`_canonical_review_profile(effective)` (`src/forge_cli/validation/__init__.py`) does:

```python
canonical=effective.get("canonical")
canonical_flow=canonical.get("flow")
canonical_review=canonical_flow.get("review")   # wrong: review is not under flow
```

`effective["canonical"]` is the raw `yaml.safe_load` of a canonical Flow file (`resolve_effective_flow`, `protocol_resolution/__init__.py`). Every real Flow file's top-level keys are `schema`, `flow` (id/name/description only), `stages`, `gates`, and `review` — all siblings. `canonical_flow.get("review")` therefore always returns `None`, and the function falls through to its `"strict"` default unconditionally for real Flow content.

## Evidence

```
$ python3 -c "
from pathlib import Path
from forge_cli.protocol_resolution import resolve_effective_flow
from forge_cli.protocol_resources import resolve_protocol_root
effective = resolve_effective_flow(resolve_protocol_root(), Path('/tmp/forge-demo'), 'standard', 2)
print(effective['canonical']['flow'].get('review'))   # None
print(effective['canonical'].get('review'))            # {'profile': 'standard', 'blocking': ..., 'convergence_limit': 2}
"
```

Live: `forge change review-status` on a freshly scaffolded STANDARD-Flow Change (no project-flow profile override) reported `Resolved profile: strict` instead of the Flow's real floor, `standard`.

## Impact

- CHG-0050 (`compute_review_profile_floor`, `resolve_effective_review_profile`, `forge change review-status`, both Adapters' new mode-resolution line): every canonical-only floor computation (i.e. no project-flow profile override present — the common case) silently returns `strict` regardless of the Change's actual Flow.
- CHG-0048 (`_validate_review_profile_floor`, `forge validate`'s `E_FORGE_REVIEW_PROFILE_BELOW_FLOOR`): a project-flow override is compared against a phantom `strict` canonical floor instead of the real one, which would incorrectly reject a legitimate override that raises a Flow's profile above its true floor but below `strict` (e.g. FAST → `standard`).

## Fix Boundary

Read `canonical.get("review")` directly (the correct top-level location) instead of `canonical_flow.get("review")`. No other logic changes: the project-override branch was already reading `effective["project"]["review"]` correctly (project-flow override files also declare `review:` at their own top level, and that path was never nested under `flow`).

## Conclusion

One-line nesting-depth fix plus fixture correction. No design change; `_PROFILE_RANK`, `resolve_effective_review_profile`, and every CHG-0050 schema/CLI/Adapter surface built on top of `compute_review_profile_floor` are unaffected in shape, only in the value they now correctly receive.
