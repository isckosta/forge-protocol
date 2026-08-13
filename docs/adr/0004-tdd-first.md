# ADR-0004 — Forge is TDD-First

Status: Accepted

## Context

AI coding agents can generate production Implementations extremely quickly. This creates a risk that tests become post-hoc validation artifacts generated to confirm code that already exists.

That approach provides coverage but loses a primary benefit of TDD: expected behavior exists independently from Implementation.

## Decision

Forge adopts TDD-first development for reasonably testable executable behavioral Changes.

The canonical cycle is RED -> GREEN -> REFACTOR.

### RED

RED requires expected behavior, an appropriate executable test, test execution, failure, and failure for the expected behavioral reason. Infrastructure or test-construction failures do not establish RED.

### GREEN

After RED, Implementation should introduce the minimum relevant production behavior necessary to make the test pass.

### REFACTOR

After GREEN, design may improve while relevant tests remain passing. New behavior requires another TDD cycle.

### Post-hoc tests

Tests created after Implementation remain useful for Verification and regression protection. They are not TDD evidence.

### Exceptions

TDD may be marked not applicable where no reasonably testable executable behavior exists. Exceptions require explicit justification. Verification and Strict Review remain mandatory.

## Consequences

Expected behavior exists independently from Implementation, bugfixes prove defects before fixing them, Agents receive stronger design constraints, and Review can distinguish TDD from post-hoc coverage. Development requires more execution cycles and poorly designed systems may expose testability problems; that pressure is considered beneficial.
