---
forge:
  artifact: test_design
  schema: 1
change: CHG-0051
status: complete
---

# CHG-0051 · Test Design

> Verification Design

## Overview

| | |
|---|---|
| **Change** | CHG-0051 |
| **Flow** | FAST |
| **Status** | Complete |

## Test Strategy

| Layer | Scope | Method |
|---|---|---|
| Layer A | `_canonical_review_profile` and its two consumers | Automated |

## Coverage Map

| Requirement | Scenario | Method |
|---|---|---|
| FR-001 | TD-001 | Automated |
| FR-001 | TD-002 | Automated |

## Layer A · Canonical profile lookup

### TD-001 · Canonical profile is read from the Flow document's top level, not nested under `flow`
Requirements: FR-001
Type: Unit

#### Purpose
Prove the actual defect: given a fixture shaped like a real canonical Flow file (`review:` a sibling of `flow:`, not nested inside it), `_canonical_review_profile`/`compute_review_profile_floor` must return that real profile, not silently fall back to `"strict"`.

#### Scenario
Given an `effective["canonical"]` dict shaped exactly like `protocol/flows/standard.yml` (top-level `flow:` and `review: {profile: standard}` as siblings)
When `compute_review_profile_floor(effective)` is called with no project override
Then it returns `"standard"`, not `"strict"`

#### Evidence
Unit test assertion on the returned value.

#### Failure Condition
Returning `"strict"` for a Flow whose real top-level `review.profile` is something else — the exact false-negative this defect produces silently (no exception, just a wrong value).

### TD-002 · The three real canonical Flow files resolve to their own documented floors
Requirements: FR-001
Type: Integration

#### Purpose
Prove the fix against the actual repository files, not only a hand-built fixture — closes the gap between "the function is correct in isolation" and "the function is correct for what it will really be called with."

#### Scenario
Given each of `protocol/flows/{fast,standard,full}.yml`, loaded via the real `resolve_effective_flow`
When `compute_review_profile_floor` is called for each with no project override
Then it returns `focused`, `standard`, and `strict` respectively

#### Evidence
Unit test assertion, one per Flow, using `resolve_effective_flow` against this repository's real `protocol/` tree.

#### Failure Condition
Any Flow resolving to a profile other than its documented one (`test_canonical_flow_files_declare_the_expected_profile` in `tests/contract/test_review_profile_schemas.py` already fixes what each Flow *declares*; this test proves what the function *reads back*, which is the part that was actually wrong).

## Valid RED

RED is valid when TD-001/TD-002 fail because the function returns `"strict"` instead of the Flow's real profile — not because of an import error, a malformed fixture, or an unrelated failure.

## Requirement Coverage

| Requirement | Automated | Manual | Status |
|---|---|---|---|
| FR-001 | TD-001, TD-002 | — | Covered |

## Coverage Gaps

None.

## Test Design Gate

Both scenarios have a clear Purpose stating the consequence of the defect (a silent wrong value, not a crash), a Failure Condition naming the false-negative risk, and Valid RED is defined. Ready for Implementation.
