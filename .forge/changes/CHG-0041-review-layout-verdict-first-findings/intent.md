---
forge:
  artifact: intent
  schema: 1
change: CHG-0041
status: active
---

# CHG-0041 · Review Layout Verdict First Findings

> **Change Intent**
>
> Redesenha o `review.md` gerado pelo scaffold para elaborar a
> guidance "aggregate Verdict primeiro" já normatizada (C-068,
> `protocol/artifact-structure.md` §4 "Review") com um Review Summary
> derivado, identificação clara do subject atual, um índice de Open
> Findings, e findings estruturados dentro do histórico de iterações
> já preservado — sem alterar reviewer/resolver independence, frozen
> subject semantics, ou o severity model.

## Overview
| | |
|---|---|
| **Change** | CHG-0041 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

O `review.md` gerado pelo scaffold hoje (`change_scaffolding.py:311`) é
um esqueleto de duas linhas: `## Verdict\n\n**PENDING**\n\n## Iteration
1 — PENDING\n\nRecord Strict Review findings.\n`. A guidance normativa
(C-068, `protocol/artifact-structure.md` §4 "Review") já estabelece
"aggregate Verdict no topo, iterações preservadas abaixo" desde
`CHG-0016`, e a própria `CHG-0016/review.md` real já demonstra boa
parte da estrutura elaborada (Verdict com breakdown por iteração,
Summary com tabela de severidade, Review Subject, Review Execution
Independence, findings como `### Rxxx — SEVERITY — <title>` com
Problem/Evidence). Mas o scaffold nunca materializou essa elaboração —
nenhum `review.md` recém-gerado oferece Review Summary, Current
Subject, Open Findings, ou estrutura de finding com campos.

Levantamento do histórico real (`CHG-0008` a `CHG-0040`) mostra
convenção estável de `## Iteration N — <verdict>` (traço-em, heading
`##`) e prefixo de finding `Rxxx` (sem prefixo de Change desde
`CHG-0016`; `CHG-XXXX-Rxxx` era usado antes). Também mostra
inconsistência real de vocabulário de verdict de iteração mais antigo
(`FAIL`, `FAILED`, texto livre como "Adversarial Re-review") que não
deve ser tratado como autoridade atual.

## Goal

1. O `review.md` gerado SHALL apresentar `Verdict` como primeira seção
   substantiva, com um dos estados reconhecidos (`PASS`/`REQUEST
   CHANGES`).
2. O scaffold SHALL oferecer estrutura para Review Summary derivado,
   Current Subject, Open Findings (condicional), e guidance de
   Reviewer Independence — antes do histórico de iterações.
3. A convenção real e estável `## Iteration N — <verdict>` SHALL ser
   preservada exatamente como está — não substituída por um novo
   heading level ou separador.
4. Findings SHALL manter o prefixo `Rxxx` já estabelecido (distinto de
   `SR-xxx` de Specification Review), com estrutura que preserva
   identidade, severidade, evidência e impacto sem prescrever
   implementação.
5. Nenhuma mudança de reviewer/resolver independence semantics,
   frozen subject semantics, severity model, Protocol integer, Change
   Schema, ou Harness Adapter é introduzida.

## Scope

O layout de apresentação do artefato Review: o template do scaffold
(`review` em `change_scaffolding.py`), a guidance correspondente em
`protocol/artifact-structure.md`, e os testes de scaffold cobrindo o
novo layout.

## Out of Scope

Não introduz novo validador Markdown, novo campo de schema, novo
estado de verdict além de `PASS`/`REQUEST CHANGES`, nova versão de
Protocol, nem reescreve `review.md` de Changes históricas. Não altera
`specification-review.md` (namespace `SR-xxx` distinto, fora de
escopo). Não duplica `manifest.yml: review.iterations[]` nem
`provenance.yml` — permanecem a autoridade estruturada; `review.md`
apenas os apresenta.

## Success Criteria

Um leitor de qualquer `review.md` recém-gerado consegue responder "a
Review mais recente passou?" lendo apenas a primeira seção, sem
percorrer iterações antigas com REQUEST CHANGES. O histórico completo
de iterações e findings permanece integralmente preservado e
rastreável. A guidance permanece proporcional: uma Review de uma única
iteração continua podendo ser curta.
