---
forge:
  artifact: intent
  schema: 1
change: CHG-0042
status: active
---

# CHG-0042 · Specification Drift Narrative Chronology

> **Change Intent**
>
> Elabora a guidance de `specification-drift.md` em
> `protocol/artifact-structure.md`, hoje limitada a três seções
> terse (Root Cause, Evidence, Final decision), com uma narrativa
> cronológica mais completa (Context, Trigger, Original Specification,
> Observed Conflict, Root Cause, Evidence, Specification Correction,
> Impact Assessment, Affected Artifacts, Re-verification, Final
> decision) — preservando explicitamente a exceção deliberada a
> Result-Before-Evidence que já existe desde `CHG-0016`.

## Overview
| | |
|---|---|
| **Change** | CHG-0042 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

`protocol/artifact-structure.md`'s seção "Specification Drift" é hoje
apenas um parágrafo curto (Root Cause, Evidence, `## Final decision`
por último). Os quatro exemplos reais existentes
(`CHG-0008`/`0011`/`0012`/`0013`) divergem fortemente em estrutura
entre si — nenhum usa headings estruturais claros, um sequer tem front
matter — porque a guidance nunca detalhou o suficiente. Diferente de
Verification/Review, este artefato não tem scaffold algum
(`specification_drift` não existe em `_STAGE_FILES` nem em nenhum
Flow YAML como stage) — é criado manualmente, sob demanda, quando um
drift real ocorre durante Review/Resolution.

## Goal

1. Elaborar a guidance de "Specification Drift" com a sequência
   narrativa completa, preservando a exceção deliberada (Final decision
   por último, não Result-Before-Evidence).
2. Esclarecer o boundary de materialidade já demonstrado por
   `CHG-0013` (Specification Review ≠ Specification Drift) e a
   distinção com Resolution/Decision.
3. Não introduzir scaffold automático para um artefato que é, por
   natureza, condicional e não determinístico por Change.

## Scope

Apenas `protocol/artifact-structure.md` (seção "Specification Drift")
e `CHANGELOG.md`. Nenhum código-fonte é alterado — não há renderer
para este artefato.

## Out of Scope

Não cria stage de scaffold para `specification_drift`; não reescreve
`specification-drift.md` histórico; não altera Protocol §13, Decision
mechanics, Resolution semantics, ou frozen subject semantics; não
renomeia o artefato.

## Success Criteria

Um agente que precisa criar um `specification-drift.md` real encontra,
em `protocol/artifact-structure.md`, guidance suficiente para produzir
um documento cronológico, proporcional, e auditável — sem precisar
inferir a estrutura a partir de exemplos históricos inconsistentes
entre si.
