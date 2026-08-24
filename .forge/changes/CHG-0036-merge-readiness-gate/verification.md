---
forge:
  artifact: verification
  schema: 1
change: CHG-0036
status: complete
---

# Verification — CHG-0036 Merge Readiness Gate

## Result

**PASS**

## Summary

The implemented Merge Readiness surface is distinct from `forge validate`,
resolves explicit Git subjects, blocks material diffs without governing
Changes, evaluates lifecycle claims and blocking Review severities, checks
Plan content digests, emits deterministic human/JSON diagnostics, and is
wired into a full-history GitHub Actions workflow.

## Test Evidence

- `.venv/bin/python -m pytest -q`: **645 passed, 2 warnings**.
- `.venv/bin/python -m pytest -q tests/cli/test_merge_check.py`: **6 passed**.
- Covered material provenance missing, incomplete lifecycle, complete Change,
  stale Plan digest, distinct exit code, and manifest-only claims.

## Forge Evidence

- `forge validate`: **PASS**.
- `forge change merge-check --base <HEAD> --head <HEAD> --json`: **ready**.
- `git diff --check`: **PASS**.
- CI workflow uses `fetch-depth: 0` and explicit Pull Request base/head SHAs.

## Compatibility/Limitations

The evaluator remains local and provider-independent. Branch protection is an
external GitHub configuration and release provenance remains independent.
Protocol 1 historical validation is preserved. Independent Strict Review and
final Completion remain outstanding lifecycle gates for this Change.

## Conclusion

Verification passes for the implemented and tested scope; this does not claim
that CHG-0036 is complete or merge-ready before independent Strict Review.
