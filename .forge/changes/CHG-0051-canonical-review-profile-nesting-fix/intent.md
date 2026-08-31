---
forge:
  artifact: intent
  schema: 1
change: CHG-0051
status: active
---

# CHG-0051 · Canonical Review Profile Nesting Fix

> **Change Intent**
>
> `_canonical_review_profile` (introduced by CHG-0050, extracted verbatim from CHG-0048's pre-existing `_validate_review_profile_floor`) reads a canonical Flow's `review.profile` from the wrong nesting level, silently defaulting every Flow's floor to `strict` unless a project-flow override explicitly sets `review.profile`. Fix the nesting and the test fixtures that masked it.

## Overview
| | |
|---|---|
| **Change** | CHG-0051 |
| **Flow** | FAST |
| **Status** | Active |

## Problem

Real canonical Flow files (`protocol/flows/{fast,standard,full}.yml`) declare `review:` as a **top-level sibling** of `flow:`, not nested inside it (confirmed: `protocol/flows/standard.yml`'s `review:` key is at line 62, `flow:` at line 3, both top-level). `_canonical_review_profile` (`src/forge_cli/validation/__init__.py`) instead reads `effective["canonical"]["flow"]["review"]` — one level too deep — so `canonical_flow.get("review")` is always `None` for real Flow data, and the function falls through to its `"strict"` default every time. This function backs both `_validate_review_profile_floor` (shipped in CHG-0048) and CHG-0050's new `compute_review_profile_floor`/`resolve_effective_review_profile`/`forge change review-status`.

Discovered live: `forge change review-status` on a freshly scaffolded Change under the STANDARD Flow (real floor `standard`) reported `Resolved profile: strict` for `review.mode: recommended`, which RFC-0008 guarantees must equal the Flow's actual floor.

Concrete consequences of the bug:
- CHG-0050's `recommended`/`fast` modes silently over-report the effective profile as `strict` for every Flow, defeating the entire point of a `standard`/`focused` floor being visible or actionable — the resolved value shown is simply wrong whenever no project-flow override sets a profile.
- CHG-0048's `_validate_review_profile_floor` (`forge validate`'s `E_FORGE_REVIEW_PROFILE_BELOW_FLOOR` check) compares a project override against a phantom `strict` floor instead of the Flow's real one, so it would incorrectly reject a legitimate override (e.g. FAST's project-flow file raising its profile to `standard`, still below the wrongly-assumed `strict` floor) as "weaker than floor."

Existing unit tests (`tests/unit/test_validation_review_profile.py`, `tests/unit/test_protocol_resolution_review_mode.py`) did not catch this because their fixtures construct `effective["canonical"]` with `review` already (incorrectly) nested inside `flow`, matching the bug instead of the real file shape.

## Goal

1. `_canonical_review_profile` reads a canonical Flow's `review.profile` from the correct top-level location.
2. Test fixtures for this function and its consumers use the real Flow-file shape (top-level `review:`), not the bug-shaped nesting.
3. A regression test proves the defect against realistic Flow content before the fix (C-018).

## Scope

- `_canonical_review_profile` and its two existing consumers (`compute_review_profile_floor`, `_validate_review_profile_floor`).
- Test fixtures in `tests/unit/test_validation_review_profile.py` and `tests/unit/test_protocol_resolution_review_mode.py` that assumed the wrong nesting.

## Out of Scope

- Any change to `_PROFILE_RANK`, `resolve_effective_review_profile`'s own resolution logic, or any CHG-0050 schema/CLI/Adapter surface — the bug is isolated to one canonical-profile lookup.
- Re-litigating CHG-0050's already-closed Strict Review.

## Success Criteria

- `forge change review-status` on a real, unmodified STANDARD-Flow Change reports `Resolved profile: standard`, not `strict`.
- `forge validate`'s `E_FORGE_REVIEW_PROFILE_BELOW_FLOOR` check compares a project override against each Flow's actual canonical profile.
- Full suite and `forge validate` pass on this repository's own `.forge/`.
