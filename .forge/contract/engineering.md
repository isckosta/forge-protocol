# Forge Project Engineering Contract

The Forge project is governed by `protocol/contract/engineering.md` plus the rules below.

## F-001 — Forge dogfoods Forge
Every material Forge Change MUST use Forge.

## F-002 — Protocol-first development
Behavior that changes Forge semantics MUST be specified in the Protocol before or together with Implementation.

## F-003 — TDD-first development
Forge executable behavior MUST be developed through TDD when reasonably testable.

## F-004 — Harness independence
Canonical Forge behavior MUST NOT exist exclusively inside a Harness Adapter.

## F-005 — CLI boundary
The Forge CLI MUST remain focused on installation, initialization, configuration, validation, migration, diagnostics, version reporting, and Adapter management.

## F-006 — No Forge Cloud dependency
Core Forge operation MUST remain possible without a Forge-hosted backend.

## F-007 — No LLM SDK in Protocol Core
Canonical Protocol behavior MUST NOT depend directly on an LLM SDK.

## F-008 — Public architectural decisions
Material Protocol Changes require RFC. Material Architecture Changes require ADR.

## F-009 — Compatibility awareness
Changes to Schemas, Protocol semantics, or Adapter contracts MUST evaluate backward compatibility.

## F-010 — Foundation simplicity
Forge MUST prefer explicit structures over premature plugin systems, services, or hidden automation.

## F-011 — Deterministic validation
Machine-readable Protocol Artifacts SHOULD become deterministically validatable.
