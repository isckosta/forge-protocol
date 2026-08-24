---
forge:
  artifact: intent
  schema: 1
change: CHG-0043
status: active
---

# CHG-0043 · Knowledge Capture Durable Lessons

> **Change Intent**
>
> Elabora o scaffold e a guidance de `knowledge-capture.md` (produzido
> apenas no Flow FULL) para tornar mais claro o que é conhecimento
> durável — distinto de Decision, Architecture, Specification, Review,
> Specification Drift, e do Forge Experience Report (FER) — preservando
> integralmente a estrutura já estável (`What Changed`, `Durable
> Knowledge`, `Consequences for Future Changes`, `References`) que a
> guidance anterior explicitamente marcava como "no material change
> recommended."

## Overview
| | |
|---|---|
| **Change** | CHG-0043 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

`protocol/artifact-structure.md`'s seção "Knowledge Capture" é hoje um
parágrafo curto. Ao contrário de Specification Drift (sem scaffold),
`knowledge_capture` **tem** um scaffold real
(`change_scaffolding.py:32,345`), usado apenas quando o Flow é FULL
(`protocol/flows/full.yml`, `required: true`, e
`required_knowledge_capture_complete` como gate de Completion). 25
exemplos reais existem, mostrando duas formas legítimas e reais: prosa
curta por seção (`CHG-0033`, `CHG-0035`, `CHG-0036`) para uma única
lição principal, e uma lista de itens independentes com título +
explicação (`CHG-0016`, sete lições distintas) quando há múltiplas
lições. O scaffold atual (`## What Changed\n\n## Durable
Knowledge\n\n## Consequences for Future Changes\n\n## References\n\n`)
não orienta qual usar, nem distingue este artefato de Decision,
Architecture, Specification, Review, Specification Drift, ou do Forge
Experience Report (FER — `docs/experience-reporting.md`, um mecanismo
real e ativo, opt-in, local, distinto por natureza).

## Goal

1. Preservar integralmente a estrutura estável (`What Changed` →
   `Durable Knowledge` → `Consequences for Future Changes` →
   `References`), adicionando apenas identidade de documento
   consistente com os demais artefatos redesenhados e um `Summary`
   opcional.
2. Orientar `Durable Knowledge` para itens independentes (`### K-xxx`)
   *quando* houver múltiplas lições — sem tornar IDs obrigatórios
   (nenhum consumidor real existe hoje para esse namespace).
3. Distinguir explicitamente Knowledge Capture de Decision,
   Architecture, Specification, Review, Specification Drift, e FER.
4. Documentar a relação real com F-008 (ADR/RFC para trabalho
   arquiteturalmente/normativamente material) sem inventar um fluxo
   mecânico de "promoção" que não existe hoje.
5. Confirmar que um Knowledge Capture vazio (nenhuma lição além da
   própria Change) é um resultado válido, não uma falha a disfarçar.

## Scope

`change_scaffolding.py` (template `knowledge_capture`),
`protocol/artifact-structure.md` (seção "Knowledge Capture"), e os
testes de scaffold correspondentes.

## Out of Scope

Não altera Decision mechanics, Architecture, Specification, Review,
Specification Drift, ou FER. Não introduz IDs `K-xxx` obrigatórios,
novo comando CLI, novo schema, ou novo validador. Não reescreve
`knowledge-capture.md` histórico.

## Success Criteria

Um agente escrevendo um `knowledge-capture.md` real consegue
distinguir rapidamente o que pertence ali do que pertence a outro
artefato ou ao FER, e sabe que registrar "nenhuma lição adicional" é
uma resposta honesta e válida quando aplicável.
