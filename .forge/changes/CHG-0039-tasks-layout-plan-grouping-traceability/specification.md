---
forge:
  artifact: specification
  schema: 1
change: CHG-0039
status: draft
---

# CHG-0039 · Specification

> **Change Contract**
>
> Esta Specification define o novo layout de `tasks.md` (Flow FULL): uma checklist de execução agrupada pelo item de Plan correspondente, com referências compactas opcionais a Requirements, User Stories e Test Design/Test Strategy, preservando seu papel de checklist operacional.

## Overview

| | |
|---|---|
| **Change** | CHG-0039 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Summary

O scaffold SHALL gerar um `tasks.md` (Flow FULL) com Overview, Tasks agrupadas por item de Plan (`### Plan N · <título>`), IDs `T-xxx` estáveis, referência compacta opcional (`Plan:`/`Requirements:`/`Stories:`/`Test Design:`) e `## Status` — preservando o front matter existente, a checklist como fonte de estado de execução, e sem introduzir enforcement semântico de Markdown.

## Classification

STANDARD. O comportamento é localizado ao renderer do scaffold (`src/forge_cli/change_scaffolding.py`) e à guidance de documentação (`protocol/artifact-structure.md`); não há mudança de Protocol integer, Change Schema, Gate semantics ou execução de Harness Adapter.

## User Stories

Nenhuma se aplica. Esta é uma Change técnica de tooling/scaffolding sem ator de domínio distinto; os Requirements abaixo são autocontidos, conforme Protocol §41 ("Requirements remain the authoritative contract ... without a User Story").

## Functional Requirements

### FR-001 · Grouped execution checklist scaffold layout
Origin: Discovery — achado sobre o template mínimo atual de `tasks`

#### Requirement
O `tasks.md` gerado (Flow FULL) SHALL preservar o `forge:` front matter existente e emitir, em inglês, as headings estruturais `Overview`, `Execution` e `Status`, substituindo o template mínimo atual (`- [ ] T-001 <work item>` seguido diretamente de `## Status`).

#### Expected Behavior
A heading de identidade do artefato SHALL seguir o padrão já adotado por `intent`, `specification` e `test_design` (`# CHG-XXXX · Tasks`), em vez do padrão genérico anterior (`# Tasks — CHG-XXXX Title`).

#### Acceptance
AC-001 — Given um scaffold FULL comportamental, When `tasks.md` é gerado, Then o front matter e as headings estruturais listadas estão presentes.

### FR-002 · Tasks grouped by Plan item
Origin: Discovery — perda de rastreabilidade ao Plan em checklists longas

#### Requirement
Dentro de `Execution`, o exemplo gerado SHALL agrupar Tasks sob uma heading `### Plan N · <título>`, preservando o identificador estável `T-xxx` de cada Task como item de checklist (`- [ ] T-xxx <work>`), não como número de lista Markdown.

#### Boundary
Este Requirement cobre a forma do scaffold gerado — o agrupamento real refletindo os itens verdadeiros do Plan de uma Change concreta é responsabilidade de quem preenche o artefato, não do template.

#### Acceptance
AC-002 — O exemplo gerado contém pelo menos uma heading `### Plan 1 ·` seguida de itens `- [ ] T-xxx`.

### FR-003 · Compact optional traceability metadata
Origin: Discovery — necessidade de rastreabilidade a Requirements/Stories/Test Design sem sobrecarregar cada Task

#### Requirement
Cada Task de exemplo SHALL poder ser seguida de uma linha compacta de metadata inline no formato `` `Plan: N` · `Requirements: FR-xxx` · `Stories: US-xxx` `` (Stories quando aplicável), e a guidance SHALL declarar explicitamente que nem toda referência se aplica a toda Task — uma Task sem User Story ou sem Test Design associado permanece válida sem essas referências.

#### Expected Behavior
A guidance SHALL usar `TDD-xxx` (não `TD-xxx`) como convenção de exemplo para referência a Test Design/Test Strategy, por ser a convenção real que uma Change de Flow FULL produz (`test-strategy.md`, `## TDD-xxx`) — `TD-xxx` é a convenção de Flow FAST/STANDARD (`test-design.md`, CHG-0038), onde `tasks.md` não existe.

#### Boundary
Esta metadata é compacta e opcional; não substitui o conteúdo do Plan, da Specification ou do Test Design/Test Strategy, e não introduz validação semântica de referência (nenhum `forge validate` novo).

#### Acceptance
AC-003 — O exemplo gerado contém pelo menos uma linha de metadata inline com `` `Plan:` `` e `` `Requirements:` ``, e a guidance declara que referências não são obrigatórias em toda Task.

### FR-004 · Compact, derivable Overview
Origin: Discovery — pedido original de seção `Overview` sem introduzir estado divergente

#### Requirement
O `tasks.md` gerado SHALL incluir uma seção `Overview` com uma tabela contendo apenas campos seguramente derivados ou apresentacionais (`Change`, `Flow`, `Status`), sem introduzir um campo mantido manualmente que possa divergir do estado real da checklist.

#### Boundary
Este Requirement não obriga contagem automática de Tasks concluídas/pendentes no scaffold estático — apenas restringe o Overview do template a campos que já são seguros para o scaffold vazio inicial. Uma Change concreta preenchendo o artefato manualmente é livre para apresentar contagens lidas da própria checklist, desde que não crie uma segunda fonte de verdade.

#### Acceptance
AC-004 — O `tasks.md` gerado contém `## Overview` com uma tabela de duas colunas incluindo `Change` e `Flow`.

### FR-005 · Status remains a simple operational summary
Origin: Discovery — preservar `## Status` sem transformá-lo em diário de desenvolvimento

#### Requirement
`## Status` SHALL permanecer a seção final do artefato, com uma frase curta descrevendo o estado operacional agregado — preservando o comportamento observável do template anterior (`No task has started.`).

#### Boundary
Este Requirement não introduz uma tabela obrigatória de contagens no scaffold vazio inicial; uma Change concreta pode optar por uma tabela `State`/`Completed`/`Remaining`/`Blocked` quando fizer sentido, sem que o scaffold a force.

#### Acceptance
AC-005 — `tasks.md` gerado termina com `## Status` seguido de uma frase declarando que nenhuma Task foi iniciada.

### FR-006 · Compatibility and scope boundary
Origin: Discovery — achado de compatibilidade e ausência de consumidor programático

#### Requirement
`tasks.md` históricos SHALL permanecer válidos sem reescrita; `forge validate` SHALL NOT passar a parsear ou impor a estrutura Markdown de `tasks.md`; nenhum outro template de artefato (`plan`, `test_strategy`, etc.) SHALL ser alterado por esta Change.

#### Acceptance
AC-006 — Os testes de scaffold e de contrato existentes continuam passando; nenhum arquivo sob `protocol/schemas/` muda; os templates `plan` e `test_strategy` em `_markdown()` permanecem byte-idênticos aos anteriores.

## Non-functional Requirements

### NFR-001 · Plain-text readability
O Markdown gerado SHALL permanecer legível sem HTML específico de renderer, badges, emojis ou tooling externo obrigatório — funcional no GitHub, em editores Markdown, em terminal e em Harnesses.

## Constraints

### CON-001 · Scope boundary
Não criar parser de Markdown, novo mecanismo de blocked Tasks, novo comando de lifecycle, nova versão de Protocol, novo Schema, Story Points, estimativas, assignees obrigatórios, Sprint, Epic, backlog, prioridade obrigatória por Task, ou dependency graph entre Tasks. Não redesenhar `plan.md` ou `test-strategy.md`. Não fabricar um exemplo de domínio completo (ex.: ERP) como diretório ou artefato real do repositório.

## Traceability Matrix

Índice apenas; as referências locais em cada Requirement permanecem autoritativas.

| Discovery | Requirement | Acceptance |
|---|---|---|
| Template mínimo atual de `tasks` | FR-001 | AC-001 |
| Perda de rastreabilidade ao Plan em checklists longas | FR-002 | AC-002 |
| Necessidade de rastreabilidade compacta a Requirements/Stories/Test Design | FR-003 | AC-003 |
| Overview sem nova fonte de verdade | FR-004 | AC-004 |
| Status como leitura rápida, não diário | FR-005 | AC-005 |
| Compatibilidade e ausência de consumidor programático | FR-006 | AC-006 |

## Compatibility Statement

O front matter existente, o Change Schema, os inteiros de Protocol, os Flow Gates, os `tasks.md` históricos, os demais templates de artefato e a semântica de Harness Adapter permanecem inalterados. A nova estrutura aplica-se apenas a `tasks.md` recém-gerados (Flow FULL) e à guidance correspondente.

## Specification Gate

Esta Specification está completa quando o comportamento do scaffold, a guidance canônica de `protocol/artifact-structure.md` §4 ("Tasks"), a documentação e os testes focados estiverem atualizados sem introduzir enforcement semântico de Markdown.

## Out of Scope

Mudança de semântica de Protocol, mudança de Schema, parsing de Markdown por validador, novo mecanismo de blocked Tasks, reescrita retroativa de artefatos históricos, e qualquer alteração em `plan.md` ou `test-strategy.md`.
