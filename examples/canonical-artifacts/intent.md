---
forge:
  artifact: intent
  schema: 1
change: CHG-0042
status: active
---

# CHG-0042 · Stock Reservation On Sales Order Confirmation

> **Change Intent**
>
> Ensure that confirming a sales order commits available stock consistently, so concurrent confirmations cannot promise the same units twice.

## Overview

| | |
|---|---|
| **Change** | CHG-0042 |
| **Flow** | STANDARD |
| **Status** | Active |
| **Domain** | Sales / Inventory |
| **Affected Capability** | Stock Reservation |

## Problem

Concurrent sales-order confirmations can use the same available stock. A
customer may receive a confirmation for an order that the operation cannot
fulfil, and the resulting discrepancy is discovered only later in the flow.

## Business Impact

The current behavior can produce:

- confirmed orders that cannot be fulfilled;
- divergence between physical and committed stock;
- incomplete fulfilment operations;
- cancellations after a customer-facing confirmation.

## Current Behavior

```text
Create Order
    ↓
Check Available Stock
    ↓
Confirm Order
    ↓
Continue Sales Flow
```

## Desired Behavior

Confirmation must turn availability into a consistent stock commitment before
the order proceeds in the sales flow.

## Goal

Introduce a stock reservation tied to sales-order confirmation. At the end of
this Change:

1. a confirmed order has a traceable reservation;
2. the same availability cannot be reserved twice;
3. confirmation fails when stock is insufficient;
4. a failed attempt leaves no partial new reservation.

## Expected Outcome

| Order | Requested | Result | Reserved | Remaining |
|---|---:|---|---:|---:|
| #1048 | 8 | Confirmed | 8 | 2 |
| #1049 | 6 | Rejected | 0 | 2 |

## Business Rules

### Reservation Ownership

A reservation belongs to one sales order and remains traceable to it.

### Atomicity

If one line cannot be reserved, no new reservation from that confirmation
attempt remains active.

## Scope

| Area | Responsibility |
|---|---|
| Sales Orders | Request and control confirmation |
| Inventory | Calculate availability and create reservations |
| Cancellation | Release eligible reservations |

## Out of Scope

This Change does not redesign the full inventory domain. It excludes future
stock forecasting, warehouse transfers, picking and packing, and automatic
backorders.

## Operational Boundary

A reservation represents committed stock; it does not represent stock that
has already been physically moved or consumed.

## Success Criteria

Concurrent confirmations never succeed by consuming the same available stock,
and an eligible cancellation restores that stock for later use.

> **Product question:** When the ERP confirms a sale, does it actually have enough stock to fulfil what it just promised?
