---
forge:
  artifact: intent
  schema: 1
change: CHG-0043
status: active
---

# CHG-0043 · HTTP Integration Timeout And Retry Policy

> **Change Intent**
>
> Make transient HTTP failures recoverable without allowing retries to prolong requests beyond the integration's operational limit.

## Overview

| | |
|---|---|
| **Change** | CHG-0043 |
| **Flow** | STANDARD |
| **Status** | Active |
| **Affected Capability** | HTTP Integration Reliability |

## Problem

The integration can wait too long for an upstream response and does not apply
a consistent retry policy to transient failures. Callers experience delayed
responses, while operators cannot predict when a request will stop retrying.

## Business Impact

The behavior increases request latency, makes failures harder to diagnose, and
can amplify load on an already unhealthy upstream service.

## Goal

Establish bounded timeouts and retries for transient HTTP failures while
preserving a clear failure result for non-retryable responses.

## Scope

This Change covers the integration's request timeout, retry classification,
retry limit, and observable failure reporting.

## Out of Scope

This Change does not redesign the upstream API, introduce a queue, or change
the integration's business payloads.

## Operational Boundary

A retry is a new attempt to obtain the same integration result; it is not
permission to duplicate a non-idempotent business operation.

## Success Criteria

Transient failures receive bounded retries, non-retryable failures stop
immediately, and every request completes within the declared operational
timeout budget.
